#!/usr/bin/env python3
"""Test HAProxy CLI del acl/del map error message behavior before and after patch."""

import subprocess
import os
import sys
import socket
import time
import signal
import tempfile
import shutil

TEST_RESULT_DIR = "/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing"
BEFORE_BIN = os.path.join(TEST_RESULT_DIR, "binary/haproxy.before")
AFTER_BIN = os.path.join(TEST_RESULT_DIR, "binary/haproxy.after")
SOCKET_PATH = "/tmp/pca-test-haproxy.sock"
CONFIG_PATH = os.path.join(TEST_RESULT_DIR, "run/haproxy.cfg")
PID_FILE = os.path.join(TEST_RESULT_DIR, "run/haproxy.pid")
RESULTS_FILE = os.path.join(TEST_RESULT_DIR, "phase4_execution/results.json")

os.makedirs(os.path.join(TEST_RESULT_DIR, "run"), exist_ok=True)

# Create minimal HAProxy config
config = """global
    daemon
    stats socket {sock} mode 600 level admin
    stats timeout 5s

defaults
    log global
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend test-frontend
    bind 127.0.0.1:18080
    default_backend test-backend

backend test-backend
    server test 127.0.0.1:18081
""".format(sock=SOCKET_PATH)

with open(CONFIG_PATH, 'w') as f:
    f.write(config)

def send_cli_command(sock_path, command):
    """Send a CLI command to HAProxy via Unix socket and return response."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(sock_path)
        s.sendall((command + "\n").encode())
        time.sleep(0.5)
        response = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        s.close()
        return response.decode().strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_test(binary_path, label):
    """Run tests with a given haproxy binary."""
    print(f"\n{'='*60}")
    print(f"Testing {label}: {binary_path}")
    print(f"{'='*60}")
    
    # Clean up socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    if os.path.exists(PID_FILE):
        os.unlink(PID_FILE)
    
    # Start haproxy
    proc = subprocess.Popen(
        [binary_path, "-f", CONFIG_PATH, "-p", PID_FILE],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(2)
    
    # Check if started
    if not os.path.exists(SOCKET_PATH):
        stdout, stderr = proc.communicate(timeout=5)
        print(f"FAILED to start {label}")
        print(f"stdout: {stdout.decode()}")
        print(f"stderr: {stderr.decode()}")
        return {"status": "blocked", "error": "failed_to_start"}
    
    results = {}
    
    # The cli_parse_del_map command expects 4 args: del, map|acl, <ref>, <key>
    # Test 1: del acl with nonexistent ref name (should hit the changed code path)
    print("\n  Command: del acl nonexistent_ref some_key")
    r1 = send_cli_command(SOCKET_PATH, "del acl nonexistent_ref some_key")
    print(f"  Response: {r1}")
    results["del_acl_invalid"] = r1
    
    # Test 2: del map with nonexistent ref name
    print("\n  Command: del map nonexistent_ref some_key")
    r2 = send_cli_command(SOCKET_PATH, "del map nonexistent_ref some_key")
    print(f"  Response: {r2}")
    results["del_map_invalid"] = r2
    
    # Test 3: show map (to verify socket works)
    print("\n  Command: show map")
    r3 = send_cli_command(SOCKET_PATH, "show map")
    print(f"  Response: (truncated) {r3[:200] if len(r3) > 200 else r3}")
    results["show_map"] = r3
    
    # Clean up
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        try:
            os.waitpid(pid, 0)
        except:
            pass
    time.sleep(1)
    
    return results

results = {}

# Run before test
before_results = run_test(BEFORE_BIN, "BEFORE (base)")
if "del_acl_invalid" in before_results:
    results["before"] = before_results
else:
    print("Before test blocked, trying after anyway")
    results["before"] = {"status": "blocked"}

# Run after test
after_results = run_test(AFTER_BIN, "AFTER (patched)")
if "del_acl_invalid" in after_results:
    results["after"] = after_results
else:
    print("After test blocked")
    results["after"] = {"status": "blocked"}

# Compare results
print(f"\n{'='*60}")
print("COMPARISON")
print(f"{'='*60}")

if "del_acl_invalid" in results.get("before", {}) and "del_acl_invalid" in results.get("after", {}):
    bef = results["before"]["del_acl_invalid"]
    aft = results["after"]["del_acl_invalid"]
    print(f"\n  del acl nonexistent_ref:")
    print(f"    BEFORE: {bef}")
    print(f"    AFTER:  {aft}")
    if bef != aft:
        print(f"    ✓ DIFFERENCE DETECTED (expected: error message changed)")
    else:
        print(f"    ⚠ SAME (unexpected)")
        print(f"    NOTE: Only SAME if both contain 'Unknown map identifier'.")

if "del_map_invalid" in results.get("before", {}) and "del_map_invalid" in results.get("after", {}):
    bef = results["before"]["del_map_invalid"]
    aft = results["after"]["del_map_invalid"]
    print(f"\n  del map nonexistent_ref:")
    print(f"    BEFORE: {bef}")
    print(f"    AFTER:  {aft}") 
    if bef == aft:
        print(f"    ✓ SAME (expected: map error message unchanged)")
    else:
        print(f"    ⚠ DIFFERENCE DETECTED (unexpected)")

# Check the actual content for compatibility confirmation
if "del_acl_invalid" in results.get("after", {}):
    acl_resp = results["after"]["del_acl_invalid"]
    if "ACL identifier" in acl_resp:
        print(f"✓ CONFIRMED: Error says 'Unknown ACL identifier' as expected in patched version")
    elif "map identifier" in acl_resp:
        print(f"✗ CONFIRMED: Error still says 'Unknown map identifier' (patch NOT effective)")

if "del_map_invalid" in results.get("after", {}):
    map_resp = results["after"]["del_map_invalid"]
    if "map identifier" in map_resp:
        print(f"✓ CONFIRMED: Error says 'Unknown map identifier' as expected")
    elif "ACL identifier" in map_resp:
        print(f"✗ CONFIRMED: Error says 'ACL' for map operation (unexpected)")

# Save results as JSON
import json
with open(RESULTS_FILE, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {RESULTS_FILE}")

# Determine test status
has_before = isinstance(results.get("before"), dict) and "del_acl_invalid" in results.get("before", {})
has_after = isinstance(results.get("after"), dict) and "del_acl_invalid" in results.get("after", {})

if has_before and has_after:
    bef_acl = results["before"]["del_acl_invalid"]
    aft_acl = results["after"]["del_acl_invalid"]
    bef_map = results["before"]["del_map_invalid"]
    aft_map = results["after"]["del_map_invalid"]
    
    # Expected: ACL error changed from "Unknown map identifier" to "Unknown ACL identifier"
    # Map error should stay "Unknown map identifier"
    bef_acl_is_map = "map identifier" in bef_acl
    aft_acl_is_acl = "ACL identifier" in aft_acl
    map_stays_map = "map identifier" in aft_map
    
    if bef_acl_is_map and aft_acl_is_acl and map_stays_map:
        print(f"\n✓ TEST PASSED: BEFORE said 'map' for ACL (bug), AFTER says 'ACL' (fixed)")
        sys.exit(0)
    elif not bef_acl_is_map:
        print(f"\n⚠ BEFORE already had correct 'ACL' message (unexpected - patch may already be applied)")
        sys.exit(2)
    else:
        print(f"\n✗ TEST FAILED: ACL error message did not change as expected")
        sys.exit(1)
else:
    print(f"\n✗ TEST BLOCKED: Could not run test")
    sys.exit(2)
