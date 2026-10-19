#!/usr/bin/env bash
# PCA-0001: Verify functools.reduce docstring/signature output format change
# Builds patched CPython, runs verification script

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
ANALYSIS_REPO="/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P021/_worktrees/patched"
SOURCE_REPO="/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython"
BASE_COMMIT="b45319e13273ee17e84e6b8c459f03b141518289"
PATCH_DIFF="/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P021/patch.diff"

BUILD_DIR="$BASE_DIR/builds/after"
BEFORE_BUILD_DIR="$BASE_DIR/builds/before"
PYTHON_AFTER="$BUILD_DIR/python"
PYTHON_BEFORE="$BEFORE_BUILD_DIR/python"
VERIFY_SCRIPT="$BASE_DIR/verify_output.py"

echo "=== PCA-0001: OUTPUT_FORMAT_CHANGE verification ==="
echo "Target: functools.reduce docstring/signature"
echo ""

# Build after (patched) version
if [ ! -f "$PYTHON_AFTER" ]; then
    echo "[BUILD] Building patched CPython..."
    mkdir -p "$BUILD_DIR"
    cd "$ANALYSIS_REPO"
    if [ ! -f Makefile ]; then
        ./configure --with-pydebug --prefix="$BUILD_DIR" --quiet 2>&1 | tail -3
    fi
    make -j$(nproc) 2>&1 | tail -5
    cp python "$PYTHON_AFTER"
    echo "[BUILD] Patched CPython built at $PYTHON_AFTER"
else
    echo "[BUILD] Using cached patched build at $PYTHON_AFTER"
fi

# Build before (parent commit) version by reverting patch in temp worktree
if [ ! -f "$PYTHON_BEFORE" ]; then
    echo "[BUILD] Building baseline CPython (before patch)..."
    mkdir -p "$BEFORE_BUILD_DIR"
    BEFORE_WORKTREE="$BASE_DIR/builds/before_wt"
    if [ ! -d "$BEFORE_WORKTREE" ]; then
        git -C "$SOURCE_REPO" worktree add "$BEFORE_WORKTREE" "$BASE_COMMIT" --detach 2>&1 | tail -1
    fi
    cd "$BEFORE_WORKTREE"
    if [ ! -f Makefile ]; then
        ./configure --with-pydebug --prefix="$BEFORE_BUILD_DIR" --quiet 2>&1 | tail -3
    fi
    make -j$(nproc) 2>&1 | tail -5
    cp python "$PYTHON_BEFORE"
    echo "[BUILD] Baseline CPython built at $PYTHON_BEFORE"
else
    echo "[BUILD] Using cached baseline build at $PYTHON_BEFORE"
fi

echo ""
echo "=== Running verification script ==="
echo ""

# Run verification
"$PYTHON_BEFORE" "$VERIFY_SCRIPT" --version before 2>&1 || true
echo "---"
"$PYTHON_AFTER" "$VERIFY_SCRIPT" --version after 2>&1 || true

echo ""
echo "=== Contract comparison ==="
echo ""

# Compare help output
echo "--- help(functools.reduce) BEFORE ---"
"$PYTHON_BEFORE" -c "
import functools, io, sys
buf = io.StringIO()
sys.stdout = buf
help(functools.reduce)
sys.stdout = sys.__stdout__
out = buf.getvalue()
print(out)
" 2>&1 | grep -A5 "reduce(" || true

echo ""
echo "--- help(functools.reduce) AFTER ---"
"$PYTHON_AFTER" -c "
import functools, io, sys
buf = io.StringIO()
sys.stdout = buf
help(functools.reduce)
sys.stdout = sys.__stdout__
out = buf.getvalue()
print(out)
" 2>&1 | grep -A5 "reduce(" || true

echo ""
echo "=== inspect.signature comparison ==="
echo ""

echo "--- BEFORE ---"
"$PYTHON_BEFORE" -c "
import functools, inspect
try:
    sig = inspect.signature(functools.reduce)
    print(f'Signature: {sig}')
    for name, param in sig.parameters.items():
        print(f'  {name}: default={param.default!r}')
except Exception as e:
    print(f'Error: {e}')
" 2>&1 || true

echo ""
echo "--- AFTER ---"
"$PYTHON_AFTER" -c "
import functools, inspect
try:
    sig = inspect.signature(functools.reduce)
    print(f'Signature: {sig}')
    for name, param in sig.parameters.items():
        print(f'  {name}: default={param.default!r}')
except Exception as e:
    print(f'Error: {e}')
" 2>&1 || true

echo ""
echo "=== DONE ==="
