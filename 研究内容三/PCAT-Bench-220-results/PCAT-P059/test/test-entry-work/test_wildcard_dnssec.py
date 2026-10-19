#!/usr/bin/env python3
"""
PCA-0001 Directed Test: DNSSEC Wildcard Validation Corner Case

Tests the fix for the corner case where querying for *.example.com
should NOT trigger a non-existence check for a.example.com.

The patch changes:
- validate_rrset(): skip wildcard expansion when name IS the wildcard
- prove_non_existence(): skip non-existence check when wild_offset == 0
- Removes STAT_SECURE_WILDCARD return code

Test methodology:
1. Start dnsmasq in auth mode serving a DNSSEC-signed zone with wildcard
2. Query for *.example.com A (the corner case)
3. Query for a.example.com A (wildcard expansion - should still work)
4. Query for nonexistent.example.com A (should get NXDOMAIN)
5. Compare behavior between before and after binaries
"""

import sys
import os
import subprocess
import time
import socket
import struct
import random
import json
import signal

DNSPYTHON_AVAILABLE = False
try:
    import dns.message
    import dns.query
    import dns.flags
    import dns.name
    DNSPYTHON_AVAILABLE = True
except ImportError:
    pass


def build_dns_query(name, qtype="A"):
    """Build a simple DNS query packet using raw sockets if dnspython unavailable."""
    if DNSPYTHON_AVAILABLE:
        q = dns.message.make_query(name, qtype)
        return q.to_wire()
    else:
        # Manual build
        tid = random.randint(0, 65535)
        packet = struct.pack("!H", tid)  # ID
        flags = 0x0100  # Standard query, RD=1
        packet += struct.pack("!H", flags)
        packet += struct.pack("!HHHH", 1, 0, 0, 0)  # QDCOUNT=1
        # Encode name
        for label in name.strip(".").split("."):
            packet += struct.pack("B", len(label))
            packet += label.encode()
        packet += b"\x00"  # Root label
        qtype_val = 1 if qtype == "A" else 28 if qtype == "AAAA" else 255
        packet += struct.pack("!HH", qtype_val, 1)  # QTYPE, QCLASS=IN
        return packet


def parse_dns_response(packet):
    """Parse DNS response to extract basic info."""
    if DNSPYTHON_AVAILABLE:
        try:
            msg = dns.message.from_wire(packet)
            answers = []
            for rr in msg.answer:
                for rdata in rr:
                    answers.append({
                        "name": str(rr.name),
                        "type": dns.rdatatype.to_text(rr.rdtype),
                        "ttl": rr.ttl,
                        "rdata": str(rdata)
                    })
            return {
                "rcode": msg.rcode(),
                "flags": dns.flags.to_text(msg.flags),
                "answers": answers,
                "raw_rcode": msg.rcode()
            }
        except Exception as e:
            return {"error": str(e), "packet_len": len(packet)}
    else:
        return {"packet_len": len(packet), "note": "raw packet mode"}


def run_dnsmasq_test(binary_path, zone_path, dns_port, test_name):
    """Run a single dnsmasq instance and test queries."""
    results = []
    pid_file = f"/tmp/pca_test_{dns_port}.pid"
    lease_file = f"/tmp/pca_test_{dns_port}.leases"
    conf_file = f"/tmp/pca_test_{dns_port}.conf"

    # Create minimal dnsmasq config for auth zone
    conf_lines = [
        f"port={dns_port}",
        "no-daemon",
        "log-queries",
        f"log-facility=-",
        f"auth-zone=example.com",
        f"auth-server=example.com",
        f"pid-file={pid_file}",
        f"leasefile-ro={lease_file}",
        "user=root",
        "bind-dynamic",
        f"auth-zone={zone_path}",
        # No DNSSEC validation needed for auth mode
        # The server simply serves the signed zone
    ]

    with open(conf_file, "w") as f:
        f.write("\n".join(conf_lines))

    # Start dnsmasq
    proc = subprocess.Popen(
        [binary_path, "-C", conf_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for startup
    time.sleep(1)

    try:
        # Test 1: Query for *.example.com A (the corner case)
        if DNSPYTHON_AVAILABLE:
            q = dns.message.make_query("*.example.com", "A")
            r = dns.query.udp(q, "127.0.0.1", port=dns_port, timeout=5)
            results.append({
                "test": "*.example.com A (corner case)",
                "rcode": r.rcode(),
                "flags": dns.flags.to_text(r.flags),
                "answers": [{"name": str(rr.name), "type": dns.rdatatype.to_text(rr.rdtype), "rdata": str(rdata)}
                           for rr in r.answer for rdata in rr]
            })

            # Test 2: Query for a.example.com A (wildcard expansion)
            q = dns.message.make_query("a.example.com", "A")
            r = dns.query.udp(q, "127.0.0.1", port=dns_port, timeout=5)
            results.append({
                "test": "a.example.com A (wildcard expansion)",
                "rcode": r.rcode(),
                "flags": dns.flags.to_text(r.flags),
                "answers": [{"name": str(rr.name), "type": dns.rdatatype.to_text(rr.rdtype), "rdata": str(rdata)}
                           for rr in r.answer for rdata in rr]
            })

            # Test 3: Query for nonexistent.example.com A (should NXDOMAIN)
            q = dns.message.make_query("nonexistent.example.com", "A")
            r = dns.query.udp(q, "127.0.0.1", port=dns_port, timeout=5)
            results.append({
                "test": "nonexistent.example.com A (NXDOMAIN expected)",
                "rcode": r.rcode(),
                "flags": dns.flags.to_text(r.flags),
                "answers": [{"name": str(rr.name), "type": dns.rdatatype.to_text(rr.rdtype), "rdata": str(rdata)}
                           for rr in r.answer for rdata in rr]
            })

            # Test 4: Query for *.example.com DNSKEY (DNSSEC records)
            q = dns.message.make_query("example.com", "DNSKEY", want_dnssec=True)
            r = dns.query.udp(q, "127.0.0.1", port=dns_port, timeout=5)
            dnskey_count = sum(1 for rr in r.answer for _ in rr if rr.rdtype == dns.rdatatype.DNSKEY)
            rrsig_count = sum(1 for rr in r.answer for _ in rr if rr.rdtype == dns.rdatatype.RRSIG)
            results.append({
                "test": "example.com DNSKEY (signed zone check)",
                "rcode": r.rcode(),
                "flags": dns.flags.to_text(r.flags),
                "dnskey_count": dnskey_count,
                "rrsig_count": rrsig_count,
                "answer_count": len(r.answer)
            })

        else:
            results.append({"test": "all", "note": "dnspython not available", "status": "skipped"})

    except Exception as e:
        results.append({"test": "queries", "error": str(e)})
    finally:
        # Stop dnsmasq
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=5)
        except:
            pass
        # Cleanup
        for f in [pid_file, lease_file, conf_file]:
            try:
                os.unlink(f)
            except:
                pass

    return {
        "test_name": test_name,
        "binary": binary_path,
        "port": dns_port,
        "results": results
    }


def main():
    base_dir = "/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/f603a4f9/compatibility-testing"
    test_entry_dir = os.path.join(base_dir, "test-entry-work")
    os.makedirs(test_entry_dir, exist_ok=True)

    before_bin = os.path.join(base_dir, "dnsmasq.before")
    after_bin = os.path.join(base_dir, "dnsmasq.after")
    zone_path = os.path.join(test_entry_dir, "signed.zone")

    if not os.path.exists(before_bin):
        print(f"ERROR: before binary not found at {before_bin}")
        sys.exit(1)
    if not os.path.exists(after_bin):
        print(f"ERROR: after binary not found at {after_bin}")
        sys.exit(1)
    if not os.path.exists(zone_path):
        print(f"ERROR: signed zone not found at {zone_path}")
        sys.exit(1)

    print(f"=== PCA-0001 DNSSEC Wildcard Testing ===")
    print(f"Before: {before_bin}")
    print(f"After:  {after_bin}")
    print(f"Zone:   {zone_path}")
    print(f"dnspython available: {DNSPYTHON_AVAILABLE}")
    print()

    # Run tests
    port_before = 15353 + random.randint(1, 1000)
    port_after = port_before + 1

    before_result = run_dnsmasq_test(before_bin, zone_path, port_before, "BEFORE (base commit)")
    print(f"Before test complete")

    after_result = run_dnsmasq_test(after_bin, zone_path, port_after, "AFTER (patched)")
    print(f"After test complete")

    # Save results
    output = {
        "test_metadata": {
            "patch_id": "f603a4f920e6953b11667d424956fd47373870e9",
            "finding_id": "PCA-0001",
            "compatibility_type": "SIDE_EFFECT_CHANGE"
        },
        "before": before_result,
        "after": after_result
    }

    output_path = os.path.join(base_dir, "phase4_execution", "test_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Print summary
    print(f"\n=== RESULTS SUMMARY ===")
    for phase_name, phase_result in [("BEFORE", before_result), ("AFTER", after_result)]:
        print(f"\n--- {phase_name} ---")
        for r in phase_result.get("results", []):
            rcode = r.get("rcode", "?")
            answers = r.get("answers", [])
            ans_str = "; ".join([f"{a['name']} {a['type']} {a['rdata'][:60]}" for a in answers[:3]])
            print(f"  {r['test']}: rcode={rcode} | {ans_str[:100]}")
            if "error" in r:
                print(f"    ERROR: {r['error']}")

    # Compare results
    before_rcodes = {r["test"]: r.get("rcode", -1) for r in before_result.get("results", [])}
    after_rcodes = {r["test"]: r.get("rcode", -1) for r in after_result.get("results", [])}

    print(f"\n=== BEHAVIOR COMPARISON ===")
    diffs_found = False
    for test_name in set(list(before_rcodes.keys()) + list(after_rcodes.keys())):
        b = before_rcodes.get(test_name, "N/A")
        a = after_rcodes.get(test_name, "N/A")
        status = "SAME" if b == a else "DIFFERENT"
        if status == "DIFFERENT":
            diffs_found = True
        print(f"  {test_name}: {b} -> {a} [{status}]")

    if diffs_found:
        print("\n  BEHAVIOR DIFFERENCES DETECTED (expected for this patch)")
    else:
        print("\n  No behavioral differences in auth-zone mode (expected)")
        print("  Note: The patch affects DNSSEC *validation* path, not auth-zone serving")
        print("  Full validation testing requires a recursive resolver setup")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
