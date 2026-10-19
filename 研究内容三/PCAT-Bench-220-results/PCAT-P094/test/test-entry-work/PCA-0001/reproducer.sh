#!/bin/bash
# PCA-0001: SIDE_EFFECT_CHANGE - HTTP server Expect: 100-continue body drain fix
# Tests that after the patch, the server no longer hangs when responding
# to Expect: 100-continue requests with a final status code.

set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${TEST_DIR}/runs/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${OUTPUT_DIR}"

PATCED_GO=${PATCED_GO:-/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P034/_worktrees/patched/bin/go}
BEFORE_GO=${BEFORE_GO:-/data7/wanghy/tmp/opencode/go/bin/go}

HARNESS="${TEST_DIR}/reproducer.go"
BEFORE_BIN="${OUTPUT_DIR}/reproducer_before"
AFTER_BIN="${OUTPUT_DIR}/reproducer_after"

echo "=== PCA-0001 SIDE_EFFECT_CHANGE Contract Test ==="

# Build before binary
echo "[1/4] Building before binary (unpatched)..."
$BEFORE_GO build -o "$BEFORE_BIN" "$HARNESS" 2>&1
echo "  Before build: OK ($BEFORE_GO version)"

# Build after binary (patched)
echo "[2/4] Building after binary (patched)..."
$PATCED_GO build -o "$AFTER_BIN" "$HARNESS" 2>&1
echo "  After build: OK ($PATCED_GO version)"

# Run before test
echo "[3/4] Running BEFORE test (expects hang)..."
set +e
timeout 8 "$BEFORE_BIN" > "${OUTPUT_DIR}/before.stdout" 2> "${OUTPUT_DIR}/before.stderr"
BEFORE_EXIT=$?
set -e

# Run after test
echo "[4/4] Running AFTER test (expects success)..."
set +e
timeout 8 "$AFTER_BIN" > "${OUTPUT_DIR}/after.stdout" 2> "${OUTPUT_DIR}/after.stderr"
AFTER_EXIT=$?
set -e

echo ""
echo "=== Results ==="
echo "Before exit code: $BEFORE_EXIT (2=hang, 0=ok, 1=error)"
echo "After exit code:  $AFTER_EXIT (2=hang, 0=ok, 1=error)"
echo "Before stdout:"
cat "${OUTPUT_DIR}/before.stdout" 2>/dev/null || echo "(empty)"
echo "After stdout:"
cat "${OUTPUT_DIR}/after.stdout" 2>/dev/null || echo "(empty)"
echo ""

if [ $AFTER_EXIT -eq 0 ]; then
    echo "BREACH: After behavior is DIFFERENT from before - no hang."
    echo "CONTRACT: side_effect_manifest_stability - BREACH (intended fix for issue #75933)"
else
    echo "PASS: After behavior matches before behavior."
fi

echo "Artifacts: ${OUTPUT_DIR}"
