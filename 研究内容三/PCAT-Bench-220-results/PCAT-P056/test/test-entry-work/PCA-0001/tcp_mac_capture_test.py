#!/usr/bin/env python3
"""
PCA-0001 Test: Verify EDNS0 MAC option in TCP mode forwarded queries.

Strategy:
1. Start a local UDP DNS listener (netcat-like) to capture upstream queries
2. Configure dnsmasq to forward to this local listener
3. Send a DNS query to dnsmasq via TCP
4. Check whether the forwarded upstream query contains the EDNS0 MAC option (0x0008)

Before patch: TCP forwarded query does NOT contain EDNS0 MAC option
After patch:  TCP forwarded query DOES contain EDNS0 MAC option
"""

import socket
import struct
import random
import sys
import os
import subprocess
import time
import json
import threading

EDNS0_OPTION_MAC = 0x0008
CAPTURE_PORT = 15354
DNSMASQ_PORT = 15353


def parse_dns_message(data):
    """Parse a DNS message and extract EDNS0 options."""
    result = {"has_edns0": False, "edns0_options": []}
    if len(data) < 12:
        return result

    tid, flags, qdcount, ancount, nscount, arcount = struct.unpack(
        "!HHHHHH", data[:12]
    )
    result["tid"] = tid
    result["qr"] = (flags >> 15) & 1
    result["opcode"] = (flags >> 14) & 1
    result["rcode"] = flags & 0x0F
    result["ancount"] = ancount
    result["arcount"] = arcount

    offset = 12
    # Skip question
    for _ in range(qdcount):
        while offset < len(data):
            label_len = data[offset]
            if label_len == 0:
                offset += 1
                break
            if label_len & 0xC0 == 0xC0:
                offset += 2
                break
            offset += label_len + 1
        offset += 4

    # Skip answer, authority
    for _ in range(ancount + nscount):
        if offset >= len(data):
            return result
        if data[offset] & 0xC0 == 0xC0:
            offset += 2
        else:
            while offset < len(data):
                label_len = data[offset]
                if label_len == 0:
                    offset += 1
                    break
                if label_len & 0xC0 == 0xC0:
                    offset += 2
                    break
                offset += label_len + 1
        if offset + 10 > len(data):
            return result
        rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[offset:offset+10])
        offset += 10 + rdlength

    # Parse additional
    for _ in range(arcount):
        if offset >= len(data):
            return result
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
                if label_len & 0xC0 == 0xC0:
                    offset += 2
                    break
                offset += label_len + 1
        
        if offset + 10 > len(data):
            return result
        rtype, udp_payload, ext_rcode, version, z, rdlength = struct.unpack(
            "!HHHHHH", data[offset:offset+10]
        )
        offset += 10
        
        if rtype == 41:  # OPT
            result["has_edns0"] = True
            result["udp_payload"] = udp_payload
            result["version"] = version
            opt_end = offset + rdlength
            while offset + 4 <= opt_end and offset < len(data):
                opt_code, opt_len = struct.unpack("!HH", data[offset:offset+4])
                offset += 4
                opt_data = data[offset:offset+opt_len] if offset+opt_len <= len(data) else b""
                result["edns0_options"].append({
                    "code": opt_code, "len": opt_len,
                    "hex": opt_data.hex(),
                })
                offset += opt_len

    return result


class UpstreamCapture:
    """UDP listener that captures upstream DNS queries."""
    
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10)
        self.sock.bind(("127.0.0.1", port))
        self.captured_queries = []
        self.running = True
        self.thread = threading.Thread(target=self._listen)
        self.thread.daemon = True
        
    def start(self):
        self.thread.start()
        
    def _listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                parsed = parse_dns_message(data)
                if not parsed.get("qr"):  # It's a query (QR=0)
                    self.captured_queries.append(parsed)
                # Send a synthetic response to avoid dnsmasq retries
                # Copy the query and set QR=1
                response = bytearray(data)
                response[2] |= 0x80  # Set QR bit
                # Add NOERROR + empty answer
                response[3] &= 0xF0  # Clear RCODE
                # Set RA (recursion available)
                response[3] |= 0x80
                self.sock.sendto(bytes(response), addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Capture error: {e}")
                    
    def stop(self):
        self.running = False
        self.sock.close()
        self.thread.join(timeout=3)


def make_dns_query(domain):
    """Create a standard DNS query (TCP mode sends length-prefixed)."""
    tid = random.randint(0, 0xFFFF)
    header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 1)
    
    question = b""
    for label in domain.split(b"."):
        question += struct.pack("!B", len(label)) + label
    question += b"\x00"
    question += struct.pack("!HH", 1, 1)  # A, IN

    # EDNS0 OPT
    opt = struct.pack("!BBHHHH", 0, 41, 4096, 0, 0, 0)
    opt += struct.pack("!H", 0)
    
    return header + question + opt


def run_test():
    """Run the TCP MAC capture test."""
    result_dir = os.environ.get(
        "PCA_RESULT_DIR",
        "/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056",
    )
    after_binary = os.path.join(result_dir, "_worktrees", "patched", "src", "dnsmasq")
    before_binary = os.path.join(result_dir, "compatibility-testing", "_worktrees", "baseline", "src", "dnsmasq")
    
    tests = [("after", after_binary), ("before", before_binary)]
    results = {}
    
    for label, binary_path in tests:
        if not os.path.exists(binary_path):
            results[label] = {"error": f"Binary not found: {binary_path}"}
            continue

        print(f"\n{'='*70}")
        print(f"TESTING: {label.upper()} binary")
        print(f"{'='*70}")

        tmpdir = f"/tmp/pca_cap_{label}_{int(time.time())}"
        os.makedirs(tmpdir, exist_ok=True)
        pid_file = os.path.join(tmpdir, "dnsmasq.pid")
        conf_file = os.path.join(tmpdir, "dnsmasq.conf")

        conf = (
            f"port={DNSMASQ_PORT}\n"
            "bind-interfaces\n"
            "interface=lo\n"
            "no-daemon\n"
            "log-queries\n"
            "log-facility=-\n"
            "add-mac\n"
            "no-resolv\n"
            "no-hosts\n"
            f"server=127.0.0.1#{CAPTURE_PORT}\n"
            f"except-interface=lo\n"
        )
        with open(conf_file, "w") as f:
            f.write(conf)

        capture = UpstreamCapture(CAPTURE_PORT)
        capture.start()
        time.sleep(0.2)

        try:
            proc = subprocess.Popen(
                [binary_path, "-C", conf_file, "-x", pid_file],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            time.sleep(1)

            ret = proc.poll()
            if ret is not None:
                stdout, _ = proc.communicate(timeout=2)
                capture.stop()
                results[label] = {"error": f"dnsmasq exited with code {ret}"}
                print(f"dnsmasq failed: {stdout.decode(errors='replace')[:300]}")
                continue

            print(f"dnsmasq {label} started (PID {proc.pid})")

            # Send TCP DNS query to dnsmasq
            domain = b"tcp-test-%06x.example.com" % random.randint(0, 0xFFFFFF)
            query = make_dns_query(domain)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            try:
                sock.connect(("127.0.0.1", DNSMASQ_PORT))
                tcp_data = struct.pack("!H", len(query)) + query
                sock.sendall(tcp_data)
                
                # Read response
                resp_len_data = sock.recv(2)
                if resp_len_data:
                    resp_len = struct.unpack("!H", resp_len_data)[0]
                    resp_data = b""
                    while len(resp_data) < resp_len:
                        chunk = sock.recv(resp_len - len(resp_data))
                        if not chunk:
                            break
                        resp_data += chunk
                sock.close()
            except Exception as e:
                print(f"TCP error: {e}")
            finally:
                sock.close()

            time.sleep(1)  # Allow capture to receive forwarded query

            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            
            capture.stop()

            # Analyze captured queries
            print(f"Captured {len(capture.captured_queries)} upstream queries")
            mac_found = False
            for i, q in enumerate(capture.captured_queries):
                opts = q.get("edns0_options", [])
                opt_codes = [o["code"] for o in opts]
                has_mac = EDNS0_OPTION_MAC in opt_codes
                if has_mac:
                    mac_found = True
                print(f"  Query {i}: EDNS0={q.get('has_edns0')}, "
                      f"opts={opt_codes}, MAC={has_mac}")

            results[label] = {
                "upstream_queries_captured": len(capture.captured_queries),
                "mac_edns0_found": mac_found,
                "queries": [
                    {
                        "has_edns0": q.get("has_edns0"),
                        "edns0_option_codes": [o["code"] for o in q.get("edns0_options", [])],
                    }
                    for q in capture.captured_queries
                ],
            }

        except Exception as e:
            results[label] = {"error": str(e)}
            print(f"ERROR: {e}")
        finally:
            subprocess.run(["rm", "-rf", tmpdir], capture_output=True, timeout=5)

    # Comparison
    print(f"\n{'='*70}")
    print("COMPARISON")
    print(f"{'='*70}")
    for label in ["before", "after"]:
        r = results.get(label, {})
        if "error" in r:
            print(f"{label}: ERROR - {r['error']}")
        else:
            print(f"{label}: MAC EDNS0 in upstream query = {r.get('mac_edns0_found', 'N/A')}")

    return results


if __name__ == "__main__":
    results = run_test()
    print(f"\nResult: {json.dumps(results, indent=2, default=str)}")
