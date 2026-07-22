#!/bin/bash
# =============================================================================
# rebuild_with_gcov.sh — Rebuild C/C++ project with gcov instrumentation
#
# Usage:
#   User-space: rebuild_with_gcov.sh <project_dir> [make_target] [extra_flags...]
#   Kernel:     rebuild_with_gcov.sh <kernel_source> "" M=fs/f2fs KCFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"
#
# IMPORTANT: Uses -O0 for accurate line-by-line coverage mapping.
# Without -O0, gcov line numbers may not match source due to inlining/code-motion.
# If -O0 fails to build (common in kernel code), fall back to -Og.
#
# Examples:
#   rebuild_with_gcov.sh /tmp/git-worktree-1 all NO_GETTEXT=1 NO_TCLTK=1
#   rebuild_with_gcov.sh /tmp/dnsmasq/src "" COPTS="-DHAVE_DNSSEC"
#   rebuild_with_gcov.sh /tmp/linux "" M=fs/f2fs O=/tmp/kbuild
# =============================================================================
set -euo pipefail

PROJECT_DIR="${1:?Usage: rebuild_with_gcov.sh <project_dir> [make_target] [extra_flags...]}"
TARGET="${2:-all}"
shift 2 2>/dev/null || true

# Detect optimization level from args — default to -O0 for accurate coverage
OPT_LEVEL="-O0"
if echo "$*" | grep -q '\-O[0-9gs]'; then
    OPT_LEVEL=$(echo "$*" | grep -o '\-O[0-9gs]' | head -1)
    echo "Using user-specified optimization: $OPT_LEVEL"
else
    echo "Using -O0 for accurate line coverage mapping"
    echo "(if the build fails, retry with: rebuild_with_gcov.sh <dir> <target> O=<level>)"
fi

cd "$PROJECT_DIR"

echo "=== Cleaning previous build and coverage data ==="
make clean 2>/dev/null || true
find . -name "*.gcda" -delete 2>/dev/null || true
find . -name "*.gcno" -delete 2>/dev/null || true
find . -name "*.gcov" -delete 2>/dev/null || true

echo "=== Building with gcov instrumentation ==="
echo "Project:    $PROJECT_DIR"
echo "Target:     $TARGET"
echo "Optimize:   $OPT_LEVEL"
echo "Extra args: $@"

make -j"$(nproc)" "$TARGET" \
    KCFLAGS="-fprofile-arcs -ftest-coverage $OPT_LEVEL -g" \
    CFLAGS="-fprofile-arcs -ftest-coverage $OPT_LEVEL -g" \
    LDFLAGS="-lgcov --coverage" \
    "$@"

RESULT=$?
echo ""
if [ $RESULT -eq 0 ]; then
    echo "=== Build successful with $OPT_LEVEL ==="
    echo "Coverage files created (*.gcno): $(find . -name '*.gcno' -type f 2>/dev/null | wc -l)"
    echo ""
    echo "To collect coverage after testing:"
    echo "  User-space: cd $PROJECT_DIR && gcov -o <obj_dir> <source_file>"
    echo "  Kernel:     scp vm:/sys/kernel/debug/gcov/<path>/*.gcda → $PROJECT_DIR/<path>/"
else
    echo "=== Build FAILED with $OPT_LEVEL ==="
    echo "Try with -Og: rebuild_with_gcov.sh $PROJECT_DIR $TARGET O=Og $@"
    echo "Or for kernel: make $TARGET KCFLAGS='-fprofile-arcs -ftest-coverage -Og -g' $@"
    echo "(Document the optimization level used in the coverage report)"
fi
