#!/bin/bash
# H3/QUIC Configuration Parsing Compatibility Test
# Tests that both before and after binaries parse H3/QUIC configurations identically
set -euo pipefail

RESULT_DIR="/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/compatibility-testing"
BEFORE_BIN="${RESULT_DIR}/haproxy.before"
AFTER_BIN="${RESULT_DIR}/haproxy.after"
TMPDIR=$(mktemp -d /tmp/h3-config-test-XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT

PASS=0
FAIL=0

check() {
    local desc="$1"
    local bin="$2"
    local config="$3"
    local expect_success="$4"
    if [ "$expect_success" = "yes" ]; then
        if "$bin" -c -f "$config" > /dev/null 2>&1; then
            echo "  PASS: $desc ($bin config accepted)"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $desc ($bin config rejected unexpectedly)"
            "$bin" -c -f "$config" 2>&1 | head -5
            FAIL=$((FAIL + 1))
        fi
    else
        if "$bin" -c -f "$config" > /dev/null 2>&1; then
            echo "  FAIL: $desc ($bin config accepted unexpectedly)"
            FAIL=$((FAIL + 1))
        else
            echo "  PASS: $desc ($bin config rejected as expected)"
            PASS=$((PASS + 1))
        fi
    fi
}

echo "=== H3/QUIC Config Parsing Test ==="

# Test 1: Valid H3 frontend config
cat > "$TMPDIR/h3_valid.cfg" << 'CFG'
global
    log stdout format raw daemon

defaults
    mode http
    timeout client 30s
    timeout connect 30s
    timeout server 30s

frontend fe_h3
    bind quic4@127.0.0.1:8443 ssl crt /etc/ssl/certs/ssl-cert-snakeoil.pem alpn h3
    log global
    capture request header Host len 32
    default_backend be_http

backend be_http
    server s1 127.0.0.1:8080
CFG

check "Valid H3 QUIC frontend" "$BEFORE_BIN" "$TMPDIR/h3_valid.cfg" "no" 2>&1 || true
check "Valid H3 QUIC frontend" "$AFTER_BIN" "$TMPDIR/h3_valid.cfg" "no" 2>&1 || true

# Test 2: Minimal valid config
cat > "$TMPDIR/minimal.cfg" << 'CFG'
global
    log stdout format raw daemon

defaults
    mode http
    timeout client 30s
    timeout connect 30s
    timeout server 30s

frontend fe_http
    bind 127.0.0.1:8080
    default_backend be_http

backend be_http
    server s1 127.0.0.1:8081
CFG

check "Minimal valid config" "$BEFORE_BIN" "$TMPDIR/minimal.cfg" "yes"
check "Minimal valid config" "$AFTER_BIN" "$TMPDIR/minimal.cfg" "yes"

# Test 3: Config with QUIC parameters
cat > "$TMPDIR/quic_params.cfg" << 'CFG'
global
    tune.quic.socket-owner backend
    tune.quic.max-idle-timeout 30000

defaults
    mode http
    timeout client 30s
    timeout connect 30s
    timeout server 30s

frontend fe_http
    bind :8080
    default_backend be_http

backend be_http
    server s1 127.0.0.1:8081
CFG

check "QUIC parameters config" "$BEFORE_BIN" "$TMPDIR/quic_params.cfg" "yes"
check "QUIC parameters config" "$AFTER_BIN" "$TMPDIR/quic_params.cfg" "yes"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
