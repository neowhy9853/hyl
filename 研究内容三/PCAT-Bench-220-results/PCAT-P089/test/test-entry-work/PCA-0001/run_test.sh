#!/bin/bash
# PCA-TE-0001: SIDE_EFFECT_CHANGE in asyncio Process.wait()
# Test: wait() returns on process exit, not on pipe EOF
set -euo pipefail

RESULT_DIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P029/compatibility-testing"
AFTER_DIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P029/_worktrees/patched"
AFTER_LOG="${RESULT_DIR}/test-entry-work/PCA-0001/runs/after_test.log"
BEFORE_DIR="${RESULT_DIR}/test-entry-work/PCA-0001/runs/before_worktree"
BEFORE_LOG="${RESULT_DIR}/test-entry-work/PCA-0001/runs/before_test.log"
RESULTS_JSON="${RESULT_DIR}/phase4_execution/results.json"

mkdir -p "${RESULT_DIR}/phase4_execution"
mkdir -p "$(dirname "${AFTER_LOG}")"

echo "=== PCA-TE-0001: Running patched test ==="
echo "Test: test_wait_even_if_pipe_is_open"
echo "After dir: ${AFTER_DIR}"
echo ""

cd "${AFTER_DIR}"

# Run the exact test added by the patch
echo ">>> Running: python -m unittest Lib.test.test_asyncio.test_subprocess.SubprocessThreadedLoopTests.test_wait_even_if_pipe_is_open -v"
python -m unittest Lib.test.test_asyncio.test_subprocess.SubprocessThreadedLoopTests.test_wait_even_if_pipe_is_open -v 2>&1 | tee "${AFTER_LOG}"
AFTER_EXIT=$?

echo ""
echo ">>> After test exit code: ${AFTER_EXIT}"

# Run related existing tests to check for regressions
echo ""
echo "=== Running regression tests ==="
REGRESSION_TESTS=(
    "Lib.test.test_asyncio.test_subprocess.SubprocessThreadedLoopTests.test_empty_input"
    "Lib.test.test_asyncio.test_subprocess.SubprocessThreadedLoopTests.test_stdin_stdout"
    "Lib.test.test_asyncio.test_subprocess.SubprocessThreadedLoopTests.test_communicate"
)
REGRESSION_FAILED=0
for t in "${REGRESSION_TESTS[@]}"; do
    echo ">>> Running: python -m unittest ${t} -v"
    if ! python -m unittest "${t}" -v 2>&1; then
        REGRESSION_FAILED=1
        echo "REGRESSION: ${t} FAILED"
    fi
done

echo ""
echo "=== Summary ==="
echo "Patch test exit code: ${AFTER_EXIT}"
echo "Regression test failures: ${REGRESSION_FAILED}"

# Write results JSON
cat > "${RESULTS_JSON}" << EOFJSON
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "finding_id": "PCA-0001",
    "entry_id": "PCA-TE-0001",
    "patch_test_passed": $([ "${AFTER_EXIT}" -eq 0 ] && echo "true" || echo "false"),
    "patch_test_exit_code": ${AFTER_EXIT},
    "regression_test_failures": ${REGRESSION_FAILED},
    "artifacts": {
        "after_test_log": "${AFTER_LOG}"
    }
}
EOFJSON

echo "Results written to ${RESULTS_JSON}"

if [ "${AFTER_EXIT}" -eq 0 ] && [ "${REGRESSION_FAILED}" -eq 0 ]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "SOME TESTS FAILED"
    exit 1
fi
