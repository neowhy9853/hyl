#!/bin/bash
set -euo pipefail

TEST_RESULT_DIR="/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing"
TMPDIR="${TEST_RESULT_DIR}/run"
mkdir -p "${TMPDIR}"

cleanup() {
    if [ -n "${HAPROXY_PID:-}" ]; then
        kill "${HAPROXY_PID}" 2>/dev/null || true
        wait "${HAPROXY_PID}" 2>/dev/null || true
    fi
    rm -f "${TMPDIR}/haproxy.cfg" "${TMPDIR}/haproxy.sock"
}
trap cleanup EXIT

# Create minimal HAProxy config with stats socket
cat > "${TMPDIR}/haproxy.cfg" <<'CFG'
global
    daemon
    stats socket /tmp/pca-test-haproxy.sock mode 600 level admin
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
CFG

BEFORE_BIN="${TEST_RESULT_DIR}/binary/haproxy.before"
AFTER_BIN="${TEST_RESULT_DIR}/binary/haproxy.after"
SOCAT="socat"

if ! command -v socat &>/dev/null; then
    echo "socat not found, using nc"
    SOCAT="nc -U"
fi

echo "=== Testing BEFORE binary ==="
# Start before binary
"${BEFORE_BIN}" -f "${TMPDIR}/haproxy.cfg" -p "${TMPDIR}/haproxy.pid" 2>&1 || true
sleep 1

if [ -f "${TMPDIR}/haproxy.pid" ]; then
    HAPROXY_PID=$(cat "${TMPDIR}/haproxy.pid")
    echo "HAProxy before started with PID ${HAPROXY_PID}"
    
    # Test 1: del acl with invalid ref
    echo -e "\n--- Test: del acl #0x1234 ---"
    echo "del acl #0x1234" | socat - UNIX-CONNECT:/tmp/pca-test-haproxy.sock 2>&1 || true
    
    # Test 2: del map with invalid ref  
    echo -e "\n--- Test: del map #0x1234 ---"
    echo "del map #0x1234" | socat - UNIX-CONNECT:/tmp/pca-test-haproxy.sock 2>&1 || true
    
    # Kill before
    kill "${HAPROXY_PID}" 2>/dev/null || true
    wait "${HAPROXY_PID}" 2>/dev/null || true
    sleep 1
    HAPROXY_PID=""
fi

echo ""
echo "=== Testing AFTER binary ==="
# Start after binary
"${AFTER_BIN}" -f "${TMPDIR}/haproxy.cfg" -p "${TMPDIR}/haproxy.pid" 2>&1 || true
sleep 1

if [ -f "${TMPDIR}/haproxy.pid" ]; then
    HAPROXY_PID=$(cat "${TMPDIR}/haproxy.pid")
    echo "HAProxy after started with PID ${HAPROXY_PID}"
    
    # Test 1: del acl with invalid ref
    echo -e "\n--- Test: del acl #0x1234 ---"
    echo "del acl #0x1234" | socat - UNIX-CONNECT:/tmp/pca-test-haproxy.sock 2>&1 || true
    
    # Test 2: del map with invalid ref
    echo -e "\n--- Test: del map #0x1234 ---"
    echo "del map #0x1234" | socat - UNIX-CONNECT:/tmp/pca-test-haproxy.sock 2>&1 || true
    
    # Kill after
    kill "${HAPROXY_PID}" 2>/dev/null || true
    wait "${HAPROXY_PID}" 2>/dev/null || true
fi
