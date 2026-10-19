#!/usr/bin/env python3
"""Run HAProxy in foreground mode for proper gcov flush, test CLI, collect coverage."""
import subprocess
import os
import sys
import socket
import time
import signal
import json

TEST_RESULT_DIR = "/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing"
PATACHED_WORKTREE = "/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/_worktrees/patched"
AFTER_BIN = os.path.join(TEST_RESULT_DIR, "binary/haproxy.after")
SOCKET_PATH = "/tmp/pca-test-haproxy.sock"
CONFIG_PATH = os.path.join(TEST_RESULT_DIR, "run/haproxy.cfg")

# Remove stale coverage data
subprocess.run(["find", PATACHED_WORKTREE, "-name", "*.gcda", "-delete"], check=False)

def send_cli_command(sock_path, command, timeout=3):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((command + "\n").encode())
        time.sleep(0.3)
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

# Clean up socket
for p in [SOCKET_PATH]:
    if os.path.exists(p):
        os.unlink(p)

# Start haproxy in foreground mode (-db) so gcov flushes on SIGTERM
print("Starting HAProxy (foreground mode)...")
proc = subprocess.Popen(
    [AFTER_BIN, "-f", CONFIG_PATH, "-db"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=PATACHED_WORKTREE  # Run from build dir so .gcda lands correctly
)

# Wait for socket
for i in range(10):
    time.sleep(1)
    if os.path.exists(SOCKET_PATH):
        break

if not os.path.exists(SOCKET_PATH):
    print("ERROR: Socket not created. Killing process.")
    proc.kill()
    stdout, stderr = proc.communicate(timeout=5)
    print(f"stdout: {stdout.decode()[:500]}")
    print(f"stderr: {stderr.decode()[:500]}")
    sys.exit(1)

print("HAProxy started, socket ready.")

# Run tests
results = {}
tests = [
    ("del_acl", "del acl nonexistent_ref some_key"),
    ("del_map", "del map nonexistent_ref some_key"),
]

for name, cmd in tests:
    resp = send_cli_command(SOCKET_PATH, cmd)
    print(f"  {cmd} -> {resp}")
    results[name] = resp

# Properly terminate - SIGTERM should flush gcov
print("Sending SIGTERM for gcov flush...")
proc.send_signal(signal.SIGTERM)
try:
    stdout, stderr = proc.communicate(timeout=10)
    print("Process exited.")
except subprocess.TimeoutExpired:
    print("Killing process...")
    proc.kill()
    stdout, stderr = proc.communicate(timeout=5)

# Save results
with open(os.path.join(TEST_RESULT_DIR, "phase4_execution/coverage_run_results.json"), 'w') as f:
    json.dump(results, f, indent=2)

# Now run gcov
print("\nRunning gcov...")
result = subprocess.run(
    ["gcov", "-o", "src/", "src/map.c"],
    capture_output=True, text=True, cwd=PATACHED_WORKTREE
)
print(result.stdout)
print(result.stderr[:500] if result.stderr else "")

# Read the relevant lines
gcov_file = os.path.join(PATACHED_WORKTREE, "map.c.gcov")
if os.path.exists(gcov_file):
    print(f"\nCoverage for changed lines (998-1009):")
    with open(gcov_file) as f:
        for line in f:
            parts = line.strip().split(":", 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                line_no = int(parts[0].strip())
                if 998 <= line_no <= 1009:
                    print(f"  {line.strip()}")
else:
    print(f"gcov file not found at {gcov_file}")
    # Try other locations
    for p in [".", "src/"]:
        f = os.path.join(PATACHED_WORKTREE, p, "map.c.gcov")
        if os.path.exists(f):
            print(f"Found at {f}")
