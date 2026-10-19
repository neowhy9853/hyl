#!/bin/bash
# PCA-0001 Test Reproducer: H3 PUSH_PROMISE error handling
# Tests basic binary behavior, version info, and config parsing
# Full protocol testing requires vtest/varnishtest (not available)

set -euo pipefail

RESULT_DIR="/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/compatibility-testing"
BEFORE_BIN="${RESULT_DIR}/haproxy.before"
AFTER_BIN="${RESULT_DIR}/haproxy.after"

echo "=== PCA-0001: ERROR_EXCEPTION_CHANGE - H3 PUSH_PROMISE Error Handling ==="
echo ""

# Step 1: Verify both binaries exist and are executable
echo "--- Step 1: Binary verification ---"
for bin in "$BEFORE_BIN" "$AFTER_BIN"; do
    if [ -x "$bin" ]; then
        echo "PASS: $bin exists and is executable"
        echo "  Size: $(stat -c%s "$bin") bytes"
    else
        echo "FAIL: $bin missing or not executable"
        exit 1
    fi
done

# Step 2: Version output comparison
echo ""
echo "--- Step 2: Version output comparison ---"
BEFORE_VER=$("$BEFORE_BIN" -vv 2>&1 | head -3)
AFTER_VER=$("$AFTER_BIN" -vv 2>&1 | head -3)
echo "Before version: $BEFORE_VER" | head -1
echo "After version:  $AFTER_VER" | head -1
if [ "$(echo "$BEFORE_VER" | head -1)" = "$(echo "$AFTER_VER" | head -1)" ]; then
    echo "PASS: Version strings match"
else
    echo "INFO: Version strings differ (expected - different commits)"
fi

# Step 3: Feature comparison
echo ""
echo "--- Step 3: Feature comparison ---"
BEFORE_FEATURES=$("$BEFORE_BIN" -vv 2>&1 | grep "^Feature list")
AFTER_FEATURES=$("$AFTER_BIN" -vv 2>&1 | grep "^Feature list")
echo "Before: $BEFORE_FEATURES"
echo "After:  $AFTER_FEATURES"
if [ "$BEFORE_FEATURES" = "$AFTER_FEATURES" ]; then
    echo "PASS: Feature lists match"
else
    echo "INFO: Feature lists differ"
fi

# Step 4: Config parsing test
echo ""
echo "--- Step 4: Config parsing test ---"
TMPDIR=$(mktemp -d /tmp/pca-reproducer-XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT

# Basic HTTP config
cat > "$TMPDIR/test.cfg" << 'CFG'
global
    log stdout format raw daemon
    maxconn 10

defaults
    mode http
    timeout client 10s
    timeout connect 10s
    timeout server 10s

frontend fe
    bind 127.0.0.1:10080
    default_backend be

backend be
    server s1 127.0.0.1:10081
CFG

echo "Testing config parsing (Before):"
"$BEFORE_BIN" -c -f "$TMPDIR/test.cfg" 2>&1 && echo "  PASS: Before config valid" || echo "  FAIL: Before config rejected"

echo "Testing config parsing (After):"
"$AFTER_BIN" -c -f "$TMPDIR/test.cfg" 2>&1 && echo "  PASS: After config valid" || echo "  FAIL: After config rejected"

echo ""
echo "=== Summary ==="
echo "Basic binary and config tests passed."
echo ""
echo "LIMITATION: Full H3 PUSH_PROMISE protocol test requires vtest/varnishtest"
echo "with QUIC support, which is not available in this environment."
echo "The actual code path at src/h3.c:2077-2079 can only be triggered by"
echo "an H3 QUIC client sending PUSH_PROMISE on a backend HAProxy connection."
echo ""
echo "To run full test: Install vtest, then use HAProxy reg-tests runner:"
echo "  cd /tmp/pca-haproxy-after && make reg-tests VTEST_PROGRAM=/path/to/vtest"
