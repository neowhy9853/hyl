#!/bin/bash
# Run probe against both before and after CPython builds
set -e

RESULT_DIR="/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/compatibility-testing"
BEFORE_BUILD="/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/compatibility-testing/builds/before"
AFTER_BUILD="/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/compatibility-testing/builds/after/source"
PROBE="${RESULT_DIR}/test-entry-work/PCA-0001/probe_parse_config_h.py"
OUT_DIR="${RESULT_DIR}/phase4_execution"

mkdir -p "${OUT_DIR}"

echo "=============================================="
echo "BEFORE (baseline, no patch)"
echo "=============================================="
cd "${BEFORE_BUILD}"
./python "${PROBE}" 2>&1; echo "EXIT_CODE=$?" | tee "${OUT_DIR}/before_probe_output.txt"

echo ""
echo "=============================================="
echo "AFTER (patched)"
echo "=============================================="
cd "${AFTER_BUILD}"
./python "${PROBE}" 2>&1; echo "EXIT_CODE=$?" | tee "${OUT_DIR}/after_probe_output.txt"

echo ""
echo "=============================================="
echo "BEFORE - Native test test_PY_BUILTIN_HASHLIB_HASHES_in_vars"
echo "=============================================="
cd "${BEFORE_BUILD}"
./python -m test test_sysconfig -v test_PY_BUILTIN_HASHLIB_HASHES_in_vars 2>&1 | tail -20; echo "EXIT_CODE=$?" | tee "${OUT_DIR}/before_native_test_output.txt"

echo ""
echo "=============================================="
echo "AFTER - Native test test_PY_BUILTIN_HASHLIB_HASHES_in_vars"
echo "=============================================="
cd "${AFTER_BUILD}"
./python -m test test_sysconfig -v test_PY_BUILTIN_HASHLIB_HASHES_in_vars 2>&1 | tail -20; echo "EXIT_CODE=$?" | tee "${OUT_DIR}/after_native_test_output.txt"
