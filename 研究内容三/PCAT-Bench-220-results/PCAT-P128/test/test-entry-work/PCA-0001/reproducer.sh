#!/bin/bash
# PCA-0001: RewriteRule QSA + trailing ? compatibility test
# Builds and runs the synthetic harness with coverage instrumentation

set -e
WORKDIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P068/compatibility-testing/test-entry-work/PCA-0001"
cd "$WORKDIR"

# Clean previous coverage data
rm -f *.gcda *.gcno *.gcov

echo "=== Building synthetic harness with coverage ==="
gcc -fprofile-arcs -ftest-coverage -O0 -g -o rewrite_qsa_test rewrite_qsa_test.c

echo ""
echo "=== Running test ==="
./rewrite_qsa_test
EXIT_CODE=$?

echo ""
echo "=== Collecting coverage ==="
gcov -b rewrite_qsa_test.c

echo ""
echo "=== Coverage of target functions ==="
# The target lines in the synthetic test correspond to:
# apply_trailing_qmark_AFTER (the new logic) and apply_trailing_qmark_BEFORE (the old logic)
echo "--- Coverage of apply_trailing_qmark_BEFORE (simulates OLD logic) ---"
grep -E "^[ ]*[0-9#]|^function" rewrite_qsa_test.c.gcov 2>/dev/null | head -40

echo ""
echo "=== Exit code: $EXIT_CODE ==="
exit $EXIT_CODE
