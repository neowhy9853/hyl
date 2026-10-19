#!/bin/bash
# Clean sideband output compatibility test
set -e

BEFORE_GIT="/tmp/pca-git-before/git"
AFTER_GIT="/tmp/pca-git-after/git"
RESULTS_DIR="/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/compatibility-testing/test-entry-work/PCA-0001/runs"

# Clean up any previous state
rm -rf /tmp/pca-test-server /tmp/pca-test-client /tmp/pcatest

# Create bare server repo
mkdir -p /tmp/pca-test-server
cd /tmp/pca-test-server
"$BEFORE_GIT" init --bare > /dev/null 2>&1

# Create client repo with a commit
mkdir -p /tmp/pca-test-client
cd /tmp/pca-test-client
"$BEFORE_GIT" init > /dev/null 2>&1
"$BEFORE_GIT" config user.email "test@test.com" > /dev/null 2>&1
"$BEFORE_GIT" config user.name "Test" > /dev/null 2>&1
echo "hello" > file.txt
"$BEFORE_GIT" add file.txt > /dev/null 2>&1
"$BEFORE_GIT" commit -m "init" > /dev/null 2>&1
"$BEFORE_GIT" remote add origin /tmp/pca-test-server > /dev/null 2>&1
"$BEFORE_GIT" push origin master > /dev/null 2>&1

echo "=== Test PCA-0001: Sideband Output Format ==="
echo "Before binary: $BEFORE_GIT"
echo "After binary: $AFTER_GIT"
echo ""

# ============== TEST 1: Pipe mode (dumb terminal) ==============
echo "--- Test 1: Pipe mode (stderr redirected) ---"

# Add second commit for fetch
"$BEFORE_GIT" commit --allow-empty -m "second" > /dev/null 2>&1
"$BEFORE_GIT" push origin master > /dev/null 2>&1

# Before fetch (pipe)
BEFORE_PIPE=$(mktemp)
"$BEFORE_GIT" -C /tmp/pca-test-client fetch origin 2>"$BEFORE_PIPE" || true

# After fetch (pipe)
AFTER_PIPE=$(mktemp)
"$AFTER_GIT" -C /tmp/pca-test-client fetch origin 2>"$AFTER_PIPE" || true

echo "Before pipe stderr:"
od -c "$BEFORE_PIPE" 2>/dev/null || cat -v "$BEFORE_PIPE"
echo ""
echo "After pipe stderr:"
od -c "$AFTER_PIPE" 2>/dev/null || cat -v "$AFTER_PIPE"
echo ""

if diff -q "$BEFORE_PIPE" "$AFTER_PIPE" > /dev/null 2>&1; then
    echo "RESULT: PIPE MODE - PASS (identical output)"
else
    echo "RESULT: PIPE MODE - DIFF"
    echo "Diff:"
    diff "$BEFORE_PIPE" "$AFTER_PIPE" 2>&1 | head -20 || true
fi
echo ""

# ============== TEST 2: TTY mode via script ==============
echo "--- Test 2: TTY mode (script PTY simulation) ---"

if command -v script > /dev/null 2>&1 && script --help 2>&1 | grep -q "quiet"; then
    # Newer script with -q flag
    TTY_BEFORE=$(mktemp)
    TTY_AFTER=$(mktemp)
    
    # Add another commit
    "$BEFORE_GIT" commit --allow-empty -m "third" > /dev/null 2>&1
    "$BEFORE_GIT" push origin master > /dev/null 2>&1
    
    # Before fetch in TTY
    script -q -c "$BEFORE_GIT -C /tmp/pca-test-client fetch origin 2>&1; true" "$TTY_BEFORE" > /dev/null 2>&1 || true
    
    # After fetch in TTY
    script -q -c "$AFTER_GIT -C /tmp/pca-test-client fetch origin 2>&1; true" "$TTY_AFTER" > /dev/null 2>&1 || true
    
    echo "Before TTY stderr (first 80 bytes):"
    xxd "$TTY_BEFORE" 2>/dev/null | head -10 || echo "(cannot xxd)"
    echo ""
    echo "After TTY stderr (first 80 bytes):"
    xxd "$TTY_AFTER" 2>/dev/null | head -10 || echo "(cannot xxd)"
    echo ""
    
    # Check for ANSI escape sequences
    BEFORE_ESC=$(od -c "$TTY_BEFORE" 2>/dev/null | grep -c "033" || echo 0)
    AFTER_ESC=$(od -c "$TTY_AFTER" 2>/dev/null | grep -c "033" || echo 0)
    echo "ESC sequence occurrences - Before: $BEFORE_ESC, After: $AFTER_ESC"
elif command -v script > /dev/null 2>&1; then
    # Older script
    TTY_BEFORE=$(mktemp)
    TTY_AFTER=$(mktemp)
    
    script "$TTY_BEFORE" -c "$BEFORE_GIT -C /tmp/pca-test-client fetch origin 2>&1; true" > /dev/null 2>&1 || true
    script "$TTY_AFTER" -c "$AFTER_GIT -C /tmp/pca-test-client fetch origin 2>&1; true" > /dev/null 2>&1 || true
    
    echo "TTY output files size - Before: $(wc -c < "$TTY_BEFORE"), After: $(wc -c < "$TTY_AFTER")"
    echo "Before TTY hex (first lines):"
    xxd "$TTY_BEFORE" 2>/dev/null | head -10 || echo "(cannot xxd)"
    echo ""
else
    echo "script command not available - skipping TTY test"
fi
echo ""

# ============== TEST 3: Verify ANSI suffix removed, prefix added ==============
echo "--- Test 3: Verify ANSI sequence moved from suffix to prefix ---"

# Check the patched source for the change
cd /tmp/pca-git-after
echo "Patched source - ANSI_PREFIX line:"
grep -n 'ANSI_PREFIX\|ANSI_SUFFIX' sideband.c 2>/dev/null || echo "sideband.c not found"
echo ""

cd /tmp/pca-git-before
echo "Baseline source - ANSI_SUFFIX line:"
grep -n 'ANSI_PREFIX\|ANSI_SUFFIX' sideband.c 2>/dev/null || echo "sideband.c not found"
echo ""

# ============== Cleanup ==============
rm -rf /tmp/pca-test-server /tmp/pca-test-client "$BEFORE_PIPE" "$AFTER_PIPE" "$TTY_BEFORE" "$TTY_AFTER" 2>/dev/null || true
echo "=== Done ==="
