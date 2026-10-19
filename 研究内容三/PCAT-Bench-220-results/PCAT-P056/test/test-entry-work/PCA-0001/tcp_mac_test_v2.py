#!/usr/bin/env python3
"""
PCA-0001 Test v2: Verify EDNS0 MAC option in TCP forwarded queries.

Sends a TCP DNS query through dnsmasq configured with --add-mac,
captures the forwarded upstream query, and checks for EDNS0 MAC option (0x0008).
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
BASE_CAPTURE_PORT = 25000
BASE_DNSMASQ_PORT = 24000


def make_dns_query(domain):
    tid = random.randint(0, 0xFFFF)
    header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 1)
    question = b""
    for label in domain.split(b"."):
        question += struct.pack("!B", len(label)) + label
    question += b"\x00"
    question += struct.pack("!HH", 1, 1)
    # EDNS0 OPT
    opt = struct.pack("!BBHHHH", 0, 41, 4096, 0, 0, 0) + struct.pack("!H", 0)
    return header + question + opt


def parse_dns_message(data):
    result = {"has_edns0": False, "edns0_options": [], "qr": False}
    if len(data) < 12:
        return result
    tid, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", data[:12])
    result["qr"] = (flags >> 15) & 1
    offset = 12
    for _ in range(qdcount):
        while offset < len(data):
            ll = data[offset]
            if ll == 0:
                offset += 1; break
            if ll & 0xC0 == 0xC0:
                offset += 2; break
            offset += ll + 1
        offset += 4
    for _ in range(ancount + nscount):
        if offset >= len(data): return result
        if data[offset] & 0xC0 == 0xC0: offset += 2
        else:
            while offset < len(data):
                ll = data[offset]
                if ll == 0: offset += 1; break
                if ll & 0xC0 == 0xC0: offset += 2; break
                offset += ll + 1
        offset += 10
        rdlength = struct.unpack("!H", data[offset-2:offset])[0]
        offset += rdlength
    for _ in range(arcount):
        if offset >= len(data): return result
        if data[offset] == 0: offset += 1
        elif data[offset] & 0xC0 == 0xC0: offset += 2
        else:
            while offset < len(data):
                ll = data[offset]
                if ll == 0: offset += 1; break
                if ll & 0xC0 == 0xC0: offset += 2; break
                offset += ll + 1
        if offset + 10 > len(data): return result
        rtype, _, _, _, _, rdlength = struct.unpack("!HHHHHH", data[offset:offset+10])
        offset += 10
        if rtype == 41:
            result["has_edns0"] = True
            opt_end = offset + rdlength
            while offset + 4 <= opt_end and offset < len(data):
                opt_code, opt_len = struct.unpack("!HH", data[offset:offset+4])
                offset += 4
                opt_data = data[offset:offset+opt_len] if offset+opt_len <= len(data) else b""
                result["edns0_options"].append({"code": opt_code, "len": opt_len})
                offset += opt_len
    return result


class UpstreamCapture:
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(8)
        self.sock.bind(("127.0.0.1", port))
        self.captured = []
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                parsed = parse_dns_message(data)
                if not parsed.get("qr"):
                    self.captured.append(parsed)
                # Respond so dnsmasq gets an answer
                resp = bytearray(data)
                resp[2] |= 0x80  # QR
                resp[3] = (resp[3] & 0xF0) | 0x80  # RA
                self.sock.sendto(bytes(resp), addr)
            except socket.timeout:
                continue
            except: pass

    def stop(self):
        self.running = False
        try: self.sock.close()
        except: pass


def run_one(label, binary_path, capture_port, dnsmasq_port):
    print(f"\n{'='*70}")
    print(f"TESTING: {label.upper()}")
    print(f"{'='*70}")
    
    result = {}
    tmpdir = f"/tmp/pca_{label}_{os.getpid()}"
    os.makedirs(tmpdir, exist_ok=True)
    
    conf_file = os.path.join(tmpdir, "dnsmasq.conf")
    with open(conf_file, "w") as f:
        f.write(
            f"port={dnsmasq_port}\n"
            "bind-interfaces\n"
            "interface=lo\n"
            "no-daemon\n"
            "log-queries\n"
            "log-facility=-\n"
            "add-mac\n"
            "no-resolv\n"
            "no-hosts\n"
            f"server=127.0.0.1#{capture_port}\n"
        )

    capture = UpstreamCapture(capture_port)
    capture.start()
    time.sleep(0.3)

    try:
        proc = subprocess.Popen(
            [binary_path, "-C", conf_file],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        time.sleep(1.5)

        if proc.poll() is not None:
            out, _ = proc.communicate(timeout=2)
            result["error"] = f"dnsmasq exited: {out.decode(errors='replace')[:300]}"
            print(f"FAILED: {result['error']}")
            capture.stop()
            return result

        print(f"dnsmasq started (PID {proc.pid})")

        # Send TCP DNS query
        domain = b"tcp-mac-test-%06x.example.com" % random.randint(0, 0xFFFFFF)
        query = make_dns_query(domain)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        try:
            sock.connect(("127.0.0.1", dnsmasq_port))
            sock.sendall(struct.pack("!H", len(query)) + query)
            rlen = sock.recv(2)
            if rlen:
                rlen = struct.unpack("!H", rlen)[0]
                sock.recv(rlen)
            sock.close()
        except Exception as e:
            print(f"TCP error: {e}")
            result["error"] = str(e)
        finally:
            try: sock.close()
            except: pass

        time.sleep(1.5)
        proc.terminate()
        proc.wait(timeout=5)

        capture.stop()
        
        mac_found = any(
            EDNS0_OPTION_MAC in [o["code"] for o in q.get("edns0_options", [])]
            for q in capture.captured
        )
        print(f"Captured {len(capture.captured)} upstream queries, MAC found: {mac_found}")
        for i, q in enumerate(capture.captured):
            codes = [o["code"] for o in q.get("edns0_options", [])]
            print(f"  Query {i}: EDNS0={q['has_edns0']}, opt_codes={codes}")

        result["mac_found"] = mac_found
        result["queries_captured"] = len(capture.captured)
        result["query_details"] = [
            {"has_edns0": q["has_edns0"], "codes": [o["code"] for o in q["edns0_options"]]}
            for q in capture.captured
        ]

    except Exception as e:
        result["error"] = str(e)
        print(f"ERROR: {e}")
        capture.stop()
    finally:
        subprocess.run(["rm", "-rf", tmpdir], capture_output=True, timeout=5)
    
    return result


def main():
    result_dir = os.environ.get(
        "PCA_RESULT_DIR",
        "/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056",
    )
    after_bin = os.path.join(result_dir, "_worktrees", "patched", "src", "dnsmasq")
    before_bin = os.path.join(result_dir, "compatibility-testing", "_worktrees", "baseline", "src", "dnsmasq")

    results = {}
    results["after"] = run_one("after", after_bin, BASE_CAPTURE_PORT, BASE_DNSMASQ_PORT)
    time.sleep(1)
    results["before"] = run_one("before", before_bin, BASE_CAPTURE_PORT + 1, BASE_DNSMASQ_PORT + 1)

    print(f"\n{'='*70}")
    print("FINAL COMPARISON")
    print(f"{'='*70}")
    for label in ["before", "after"]:
        r = results.get(label, {})
        if "error" in r:
            print(f"{label}: ERROR - {r['error']}")
        else:
            print(f"{label}: MAC EDNS0 found = {r.get('mac_found', 'N/A')} "
                  f"(queries: {r.get('queries_captured', 0)})")

    print(f"\nResult: {json.dumps(results, indent=2, default=str)}")
    return results


if __name__ == "__main__":
    results = main()
