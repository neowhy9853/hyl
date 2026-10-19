#!/bin/bash
# PCA-TE-0001: PYTHONSTARTUP behavior with -E and -I flags in asyncio REPL
set -euo pipefail

BEFORE_PYTHON="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/compatibility-testing/before_build/source/python"
AFTER_PYTHON="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/_worktrees/patched/python"
RESULT_DIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/compatibility-testing"

echo "=== PCA-TE-0001: PYTHONSTARTUP in asyncio REPL ==="

STARTUP_FILE=$(mktemp /tmp/test_startup_XXXX.py)
cat > "$STARTUP_FILE" << 'PYEOF'
import sys
sys.stderr.write("PYTHONSTARTUP_EXECUTED_MARKER\n")
PYEOF

run_async_test() {
    local label="$1"
    local python="$2"
    local extra_args="$3"
    local expect_startup="$4"

    local output
    output=$(PYTHONSTARTUP="$STARTUP_FILE" TERM=dumb timeout 10 "$python" $extra_args -m asyncio 2>&1 <<< "exit()") || true

    if echo "$output" | grep -q "PYTHONSTARTUP_EXECUTED_MARKER"; then
        local started=1
    else
        local started=0
    fi

    local passed=false
    if [ "$expect_startup" = "yes" ] && [ "$started" = "1" ]; then
        passed=true
    elif [ "$expect_startup" = "no" ] && [ "$started" = "0" ]; then
        passed=true
    fi

    echo "  [$label] startup_executed=$started expected=$expect_startup -> $(if $passed; then echo "PASS"; else echo "FAIL"; fi)"

    if $passed; then return 0; else return 1; fi
}

echo "--- BEFORE (base_commit: 2df69de5) ---"
run_async_test "I1-before-noflag" "$BEFORE_PYTHON" "" "yes" || true
run_async_test "I2-before-E" "$BEFORE_PYTHON" "-E" "yes" || true
run_async_test "I3-before-I" "$BEFORE_PYTHON" "-I" "no" || true

echo "--- AFTER (patched: 7f8fc07) ---"
run_async_test "I1-after-noflag" "$AFTER_PYTHON" "" "yes" || true
run_async_test "I2-after-E" "$AFTER_PYTHON" "-E" "no" || true
run_async_test "I3-after-I" "$AFTER_PYTHON" "-I" "no" || true

rm -f "$STARTUP_FILE"
echo "=== PCA-TE-0001 DONE ==="
