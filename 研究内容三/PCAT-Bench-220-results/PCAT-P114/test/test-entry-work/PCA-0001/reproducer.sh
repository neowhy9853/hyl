#!/bin/bash
set -euo pipefail

# PCA Age Header Test Reproducer
# Tests that soup_cache_send_response no longer adds Age header to cache responses
# Target: libsoup/soup-cache.c:670-708, symbol: soup_cache_send_response

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P054/_worktrees/patched"
BINARY="$SCRIPT_DIR/test_age_header"

echo "=== Building test_age_header ==="

cd "$BUILD_DIR/tests"

gcc -g -O0 \
    -I"$BUILD_DIR" \
    -I"$BUILD_DIR/libsoup" \
    $(pkg-config --cflags glib-2.0 gobject-2.0 gio-2.0 libxml-2.0) \
    -o "$BINARY" \
    "$SCRIPT_DIR/test_age_header.c" \
    "$BUILD_DIR/tests/.libs/test-utils.o" \
    "$BUILD_DIR/libsoup/.libs/libsoup-2.4.so" \
    $(pkg-config --libs glib-2.0 gobject-2.0 gio-2.0 libxml-2.0 sqlite3) \
    -L"$BUILD_DIR/libsoup/.libs" \
    -Wl,-rpath,"$BUILD_DIR/libsoup/.libs"

echo "=== Running test ==="

export LD_LIBRARY_PATH="$BUILD_DIR/libsoup/.libs:$LD_LIBRARY_PATH"
timeout 30 "$BINARY"

EXIT_CODE=$?
echo "Exit code: $EXIT_CODE"
exit $EXIT_CODE
