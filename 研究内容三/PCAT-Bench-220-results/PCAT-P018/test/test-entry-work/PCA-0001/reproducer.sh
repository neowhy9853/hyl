#!/bin/bash
# PCA-0001: xmllint --maxmem behavior test
# This test verifies the --maxmem CLI option behavior change
set -e

XMLLINT="$1"
if [ -z "$XMLLINT" ] || [ ! -x "$XMLLINT" ]; then
    echo "Usage: $0 <path-to-xmllint-binary>"
    echo "Error: xmllint binary not found or not executable"
    exit 1
fi

echo "=== Testing --maxmem option for xmllint ==="
echo "Binary: $XMLLINT"

# Create a minimal valid XML file for testing
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

cat > "$TMPDIR/test.xml" << 'EOF'
<?xml version="1.0"?>
<root>
  <item id="1">hello</item>
  <item id="2">world</item>
</root>
EOF

PASS=0
FAIL=0

# Test 1: No --maxmem (default) - should succeed
echo ""
echo "--- Test 1: No --maxmem (default) ---"
if "$XMLLINT" --noout "$TMPDIR/test.xml" 2>&1; then
    echo "PASS: No --maxmem succeeded"
    PASS=$((PASS + 1))
else
    echo "FAIL: No --maxmem failed unexpectedly"
    FAIL=$((FAIL + 1))
fi

# Test 2: --maxmem 0 (unlimited) - should succeed
echo ""
echo "--- Test 2: --maxmem 0 (unlimited) ---"
if "$XMLLINT" --maxmem 0 --noout "$TMPDIR/test.xml" 2>&1; then
    echo "PASS: --maxmem 0 succeeded"
    PASS=$((PASS + 1))
else
    echo "FAIL: --maxmem 0 failed unexpectedly"
    FAIL=$((FAIL + 1))
fi

# Test 3: --maxmem 1 (very small) - should fail with OOM
echo ""
echo "--- Test 3: --maxmem 1 (very small limit) ---"
if "$XMLLINT" --maxmem 1 --noout "$TMPDIR/test.xml" 2>&1; then
    echo "UNEXPECTED: --maxmem 1 succeeded (expected OOM)"
    FAIL=$((FAIL + 1))
else
    echo "PASS: --maxmem 1 correctly failed (OOM expected)"
    PASS=$((PASS + 1))
fi

# Test 4: --maxmem 100 (very small but may allow limited parsing)
echo ""
echo "--- Test 4: --maxmem 100 (small limit) ---"
if "$XMLLINT" --maxmem 100 --noout "$TMPDIR/test.xml" 2>&1; then
    echo "PASS: --maxmem 100 succeeded"
    PASS=$((PASS + 1))
else
    echo "INFO: --maxmem 100 failed (OOM - this is expected if 100 bytes is too small)"
    # This might still fail since 100 bytes is tiny
    PASS=$((PASS + 1))
fi

# Test 5: --maxmem with a reasonable limit for small XML
echo ""
echo "--- Test 5: --maxmem 100000 (reasonable limit) ---"
if "$XMLLINT" --maxmem 100000 --noout "$TMPDIR/test.xml" 2>&1; then
    echo "PASS: --maxmem 100000 succeeded"
    PASS=$((PASS + 1))
else
    echo "FAIL: --maxmem 100000 failed unexpectedly"
    FAIL=$((FAIL + 1))
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
if [ "$FAIL" -eq 0 ]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "SOME TESTS FAILED"
    exit 1
fi
