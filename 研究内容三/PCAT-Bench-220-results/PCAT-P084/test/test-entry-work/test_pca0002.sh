#!/bin/bash
# PCA-TE-0002: PYTHON_BASIC_REPL with -E and -I flags in asyncio REPL
set -euo pipefail

BEFORE_PYTHON="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/compatibility-testing/before_build/source/python"
AFTER_PYTHON="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/_worktrees/patched/python"

echo "=== PCA-TE-0002: PYTHON_BASIC_REPL in asyncio REPL ==="

# Detection method: pyrepl emits colored prompts with ANSI SGR sequences.
# Basic REPL emits plain prompts or minimal ANSI.
# Key difference: pyrepl prompt includes color escape like \033[36m (cyan) or similar.
# We check for ANSI SGR codes (CSI ... m) in the prompt area.

run_async_test() {
    local label="$1"
    local python="$2"
    local extra_args="$3"
    local expect_pyrepl="$4"

    local output
    output=$(PYTHON_BASIC_REPL=1 TERM=xterm-256color timeout 15 "$python" $extra_args -m asyncio 2>&1 <<< "exit()") || true

    # pyrepl uses \033[...m color codes in prompts; basic REPL doesn't
    if echo "$output" | grep -qP '\033\[3[0-9]m.*>>>' || echo "$output" | grep -qP '\033\[9[0-9]m.*>>>'; then
        local pyrepl_state="enabled"
    elif echo "$output" | grep -q ">>>" && echo "$output" | grep -qP '\033'; then
        # Has some ANSI but might be basic REPL (which can also have ANSI sequences)
        # Check for the characteristic colored prompt of pyrepl
        if echo "$output" | grep -qP '\033\[.*m.*>>>' ; then
            local pyrepl_state="enabled"
        else
            local pyrepl_state="disabled"
        fi
    else
        local pyrepl_state="disabled"
    fi

    local passed=false
    if [ "$expect_pyrepl" = "$pyrepl_state" ]; then
        passed=true
    fi

    echo "  [$label] pyrepl=$pyrepl_state expected=$expect_pyrepl -> $(if $passed; then echo "PASS"; else echo "FAIL"; fi)"

    if $passed; then return 0; else return 1; fi
}

echo "--- BEFORE (base_commit: 2df69de5) ---"
run_async_test "I1-before-noflag" "$BEFORE_PYTHON" "" "disabled" || true
run_async_test "I2-before-E" "$BEFORE_PYTHON" "-E" "disabled" || true
run_async_test "I3-before-I" "$BEFORE_PYTHON" "-I" "disabled" || true

echo "--- AFTER (patched: 7f8fc07) ---"
run_async_test "I1-after-noflag" "$AFTER_PYTHON" "" "disabled" || true
run_async_test "I2-after-E" "$AFTER_PYTHON" "-E" "enabled" || true
run_async_test "I3-after-I" "$AFTER_PYTHON" "-I" "enabled" || true

echo "=== PCA-TE-0002 DONE ==="
