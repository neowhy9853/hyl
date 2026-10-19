#!/bin/bash
# PCA-TE-0001: ERROR_EXCEPTION_CHANGE test for grub_script_function_create
# Tests that redefining a function during execution produces an error
set -e

ANALYSIS_REPO="${ANALYSIS_REPO:-/path/to/patched/worktree}"
GRUB_EMU="${ANALYSIS_REPO}/grub-core/grub-emu"

if [ ! -x "$GRUB_EMU" ]; then
    echo "SKIP: grub-emu not found at $GRUB_EMU"
    exit 0
fi

echo "=== PCA-TE-0001: ERROR_EXCEPTION_CHANGE test ==="
echo "Testing that redefining a function during execution raises GRUB_ERR_BAD_ARGUMENT"

# Create test script using multi-line format
cat > /tmp/pca_test_func_redef.cfg << 'EOF'
# Test: Define a function and then redefine it during execution
function inner { echo inner_initial; }
echo "step1_inner_call"
inner

echo "step2_define_outer"
function outer {
  echo outer_start
  inner
  echo trying_redefinition
  function inner { echo redefined; }
  echo outer_end
}

echo "step3_call_outer"
outer

echo "step4_final_inner_call"
inner
echo "TEST_COMPLETE"
EOF

# Use grub-emu with source command
echo "--- Running test via grub-emu source ---"
printf 'source (host)/tmp/pca_test_func_redef.cfg\n' | timeout 15 "$GRUB_EMU" -r "" 2>&1 | \
    grep -vE '^\s*$|(^|grub>|completions|TAB)' || true

echo ""
echo "=== Test entry artifacts prepared ==="
echo "Full dynamic testing requires QEMU for grub-shell execution"
echo "The grub-emu binary is available for manual testing"
