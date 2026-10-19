#!/usr/bin/env python3
"""
PCA-0001 Test: Verify EDNS0 MAC option presence in TCP mode DNS responses.

This test starts dnsmasq with --add-mac, sends a DNS query over TCP,
and checks whether the EDNS0 MAC option (code 0x0008) appears in the response.

Before patch: TCP child process lacks netlink socket, find_mac() fails silently,
              EDNS0 MAC option is NOT present in response.
After patch:  Parent pre-populates ARP cache before fork, child inherits it,
              EDNS0 MAC option IS present in response (or attempt is made).
"""

import socket
import struct
import random
import sys
import os
import subprocess
import time
import json

# EDNS0 option codes
EDNS0_OPTION_MAC = 0x0008

# DNS query parameters
PORT = 5354
DOMAIN = b"test-eda0a1b2.example.com"
TIMEOUT = 10


def make_dns_query(domain, dnssec_ok=False):
    """Create a DNS query with EDNS0 OPT record."""
    tid = random.randint(0, 0xFFFF)

    # Header: ID, flags=0x0100 (standard query, RD=1), qdcount=1, ancount=0,
    # nscount=0, arcount=1 (EDNS0)
    header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 1)

    # Question: encode domain as labels
    question = b""
    for label in domain.split(b"."):
        question += struct.pack("!B", len(label)) + label
    question += b"\x00"  # end of domain name
    question += struct.pack("!HH", 1, 1)  # QTYPE=A, QCLASS=IN

    # EDNS0 OPT pseudo-record (RFC 6891)
    # Name: root (0x00), Type: OPT (41), UDP payload size: 4096
    # Extended RCODE: 0, Version: 0, DO bit (if DNSSEC OK)
    ext_rcode = 0
    version = 0
    do_bit = 0x8000 if dnssec_ok else 0
    z = do_bit  # Upper 16 bits of Z field (DO bit)
    data_length = 0
    opt = struct.pack("!BBHHHH", 0, 41, 4096, ext_rcode, version, z)
    opt += struct.pack("!H", data_length)

    packet = header + question + opt
    return packet


def parse_dns_response(data):
    """Parse DNS response and extract EDNS0 options."""
    result = {"has_edns0": False, "edns0_options": [], "rcode": None}

    if len(data) < 12:
        return result

    # Parse header
    tid, flags, qdcount, ancount, nscount, arcount = struct.unpack(
        "!HHHHHH", data[:12]
    )
    result["tid"] = tid
    result["flags"] = flags
    result["rcode"] = flags & 0x0F
    result["qr"] = (flags >> 15) & 1
    result["ancount"] = ancount
    result["arcount"] = arcount

    offset = 12

    # Skip question section
    for _ in range(qdcount):
        while offset < len(data):
            label_len = data[offset]
            if label_len == 0:
                offset += 1
                break
            offset += label_len + 1
        offset += 4  # QTYPE + QCLASS

    # Skip answer, authority sections
    for _ in range(ancount + nscount):
        if offset >= len(data):
            return result
        # RR name (compression possible)
        if data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            while offset < len(data):
                label_len = data[offset]
                if label_len == 0:
                    offset += 1
                    break
                offset += label_len + 1
        if offset + 10 > len(data):
            return result
        rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[offset : offset + 10])
        offset += 10 + rdlength

    # Parse additional section (EDNS0 OPT records)
    for _ in range(arcount):
        if offset >= len(data):
            return result

        # OPT pseudo-record name is always root (0x00) or compressed
        if data[offset] == 0:
            offset += 1
        elif data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            while offset < len(data):
                label_len = data[offset]
                if label_len == 0:
                    offset += 1
                    break
                offset += label_len + 1

        if offset + 10 > len(data):
            return result

        rtype, udp_payload, ext_rcode, version, z, rdlength = struct.unpack(
            "!HHHHHH", data[offset : offset + 10]
        )
        offset += 10

        if rtype == 41:  # OPT
            result["has_edns0"] = True
            result["udp_payload"] = udp_payload
            result["version"] = version
            result["do_bit"] = (z & 0x8000) != 0

            # Parse EDNS0 options
            opt_end = offset + rdlength
            while offset + 4 <= opt_end and offset < len(data):
                opt_code, opt_len = struct.unpack("!HH", data[offset : offset + 4])
                offset += 4
                if offset + opt_len <= len(data):
                    opt_data = data[offset : offset + opt_len]
                    result["edns0_options"].append(
                        {"code": opt_code, "len": opt_len, "hex": opt_data.hex()}
                    )
                offset += opt_len

    return result


def run_test():
    """Run the TCP MAC test."""
    result_dir = os.environ.get(
        "PCA_RESULT_DIR",
        "/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056",
    )
    after_binary = os.path.join(
        result_dir, "_worktrees", "patched", "src", "dnsmasq"
    )
    before_binary = os.path.join(
        result_dir,
        "compatibility-testing",
        "_worktrees",
        "baseline",
        "src",
        "dnsmasq",
    )

    results = {}

    for label, binary_path in [("after", after_binary), ("before", before_binary)]:
        if not os.path.exists(binary_path):
            results[label] = {"error": f"Binary not found: {binary_path}"}
            continue

        print(f"\n{'='*60}")
        print(f"Testing {label} binary: {binary_path}")
        print(f"{'='*60}")

        # Create a temp directory for this run
        tmpdir = f"/tmp/pca_test_{label}_{int(time.time())}"
        os.makedirs(tmpdir, exist_ok=True)
        pid_file = os.path.join(tmpdir, "dnsmasq.pid")
        conf_file = os.path.join(tmpdir, "dnsmasq.conf")

        conf = (
            "port=5354\n"
            "bind-interfaces\n"
            "interface=lo\n"
            "no-daemon\n"
            "log-queries\n"
            "log-facility=-\n"
            "add-mac\n"
            "no-resolv\n"
            "no-hosts\n"
            "server=8.8.8.8\n"
        )
        with open(conf_file, "w") as f:
            f.write(conf)

        try:
            # Start dnsmasq
            proc = subprocess.Popen(
                [binary_path, "-C", conf_file, "-x", pid_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            time.sleep(1)

            # Check if it's running
            ret = proc.poll()
            if ret is not None:
                stdout, _ = proc.communicate(timeout=2)
                results[label] = {
                    "error": f"dnsmasq exited with code {ret}",
                    "output": stdout.decode(errors="replace"),
                }
                print(f"dnsmasq failed to start (exit code {ret})")
                print(stdout.decode(errors="replace")[:500])
                continue

            print(f"dnsmasq {label} started (PID {proc.pid})")

            # Send TCP DNS query
            query = make_dns_query(DOMAIN)

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(TIMEOUT)
                sock.connect(("127.0.0.1", PORT))

                # TCP DNS: 2-byte length prefix + DNS message
                tcp_data = struct.pack("!H", len(query)) + query
                sock.sendall(tcp_data)

                # Receive response
                resp_data = b""
                resp_len_data = sock.recv(2)
                if len(resp_len_data) >= 2:
                    resp_len = struct.unpack("!H", resp_len_data)[0]
                    while len(resp_data) < resp_len:
                        chunk = sock.recv(resp_len - len(resp_data))
                        if not chunk:
                            break
                        resp_data += chunk

                sock.close()

                # Parse response
                parsed = parse_dns_response(resp_data)
                results[label] = {
                    "has_edns0": parsed.get("has_edns0", False),
                    "edns0_options": parsed.get("edns0_options", []),
                    "rcode": parsed.get("rcode"),
                    "ancount": parsed.get("ancount"),
                    "response_hex": resp_data.hex()[:200],
                }

                print(f"Response received: {len(resp_data)} bytes")
                print(f"  EDNS0 present: {parsed.get('has_edns0')}")
                print(f"  EDNS0 options: {parsed.get('edns0_options')}")
                print(f"  RCODE: {parsed.get('rcode')}")
                print(f"  Answer count: {parsed.get('ancount')}")

            except socket.timeout:
                results[label] = {"error": "TCP connection timeout"}
                print("ERROR: TCP connection timeout")
            except ConnectionRefusedError:
                results[label] = {"error": "Connection refused"}
                print("ERROR: Connection refused - dnsmasq not listening")
            except Exception as e:
                results[label] = {"error": str(e)}
                print(f"ERROR: {e}")
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

        except Exception as e:
            results[label] = {"error": str(e)}
            print(f"ERROR: {e}")
        finally:
            # Cleanup
            try:
                subprocess.run(
                    ["rm", "-rf", tmpdir], capture_output=True, timeout=5
                )
            except Exception:
                pass

    # Compare results
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    after = results.get("after", {})
    before = results.get("before", {})

    if "error" in after:
        print(f"After: ERROR - {after['error']}")
    else:
        after_opts = [o["code"] for o in after.get("edns0_options", [])]
        after_has_mac = EDNS0_OPTION_MAC in after_opts
        print(f"After:  EDNS0 options codes: {after_opts}, MAC present: {after_has_mac}")

    if "error" in before:
        print(f"Before: ERROR - {before['error']}")
    else:
        before_opts = [o["code"] for o in before.get("edns0_options", [])]
        before_has_mac = EDNS0_OPTION_MAC in before_opts
        print(f"Before: EDNS0 options codes: {before_opts}, MAC present: {before_has_mac}")

    return results


if __name__ == "__main__":
    results = run_test()
    print(f"\n{'='*60}")
    print(f"Result: {json.dumps(results, indent=2, default=str)}")
