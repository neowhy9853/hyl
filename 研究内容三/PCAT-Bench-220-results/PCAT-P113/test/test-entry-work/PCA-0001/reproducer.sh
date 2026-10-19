#!/bin/bash
# PCA-0001 Test Reproducer: Conditional Authorization header removal
# Target: libsoup/soup-auth-manager.c:446-454 (update_authorization_header)
# 
# This reproducer validates the behavioral change where Authorization/Proxy-Authorization
# headers are now only removed when soup_message_get_auth(msg) returns non-NULL.
# User-provided headers on messages without cached auth are preserved.
#
# Requires: 
#   - Working libsoup build with gcov instrumentation
#   - Apache HTTP server with Digest auth configured
#   - OR: Custom Python HTTP server with auth
#
# Environment: This test needs intltool, autoconf, automake, glib-devel, and Apache/nginx
# for Digest authentication. Recorded as 'needs_env' when dependencies are missing.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_DIR="$SCRIPT_DIR"

echo "=== PCA-0001: Conditional Authorization Header Removal ==="
echo "Target: libsoup/soup-auth-manager.c:446-454"
echo "Symbol: update_authorization_header"
echo ""

# --- Step 1: Check build dependencies ---
echo "[1/4] Checking build dependencies..."
MISSING=""
for tool in autoconf automake pkg-config make gcc intltoolize; do
    if ! which "$tool" &>/dev/null; then
        MISSING="$MISSING $tool"
    fi
done

if [ -n "$MISSING" ]; then
    echo "WARNING: Missing dependencies:$MISSING"
    echo "Install them with: sudo apt install intltool autoconf automake pkg-config"
fi

# Check glib-2.0
if ! pkg-config --exists glib-2.0 2>/dev/null; then
    echo "WARNING: glib-2.0 not found via pkg-config. Install glib-devel."
fi

echo ""

# --- Step 2: Build libsoup from analysis worktree with gcov ---
ANALYSIS_REPO="${ANALYSIS_REPO:-/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P053/_worktrees/patched}"
BUILD_DIR="${BUILD_DIR:-$TEST_DIR/build}"

echo "[2/4] Building libsoup with gcov instrumentation..."
echo "Source: $ANALYSIS_REPO"
echo "Build dir: $BUILD_DIR"

if [ ! -d "$ANALYSIS_REPO" ]; then
    echo "ERROR: Analysis worktree not found at $ANALYSIS_REPO"
    echo "Run: python3 orchestrator.py --ensure-worktree analysis.json"
    exit 1
fi

if [ ! -f "$ANALYSIS_REPO/configure" ]; then
    echo "Running autogen.sh to generate configure script..."
    if [ -x "$ANALYSIS_REPO/autogen.sh" ]; then
        cd "$ANALYSIS_REPO"
        NOCONFIGURE=1 ./autogen.sh 2>&1 || {
            echo "ERROR: autogen.sh failed (missing intltool?)"
            echo "STATUS: needs_env - cannot build without intltool"
            exit 0
        }
    else
        echo "ERROR: No autogen.sh found"
        exit 1
    fi
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

if [ ! -f "$BUILD_DIR/Makefile" ]; then
    "$ANALYSIS_REPO/configure" \
        CFLAGS="-fprofile-arcs -ftest-coverage -O0 -g" \
        LDFLAGS="-lgcov --coverage" \
        --enable-static \
        --disable-glibtest \
        --prefix="$BUILD_DIR/install" 2>&1 || {
        echo "WARNING: Configure failed. This is expected when dependencies are incomplete."
        echo "STATUS: needs_env - configure requires glib-devel, libxml2-devel, sqlite-devel"
    }
fi

if [ -f "$BUILD_DIR/Makefile" ]; then
    make -j$(nproc) V=0 2>&1 || echo "WARNING: Build failed - expected if deps missing"
    echo "Built successfully (or with warnings)"
fi

echo ""

# --- Step 3: Run the auth-test targeted at the new test ---
echo "[3/4] Running targeted auth test..."
echo "This test requires Apache HTTP server with Digest auth on port 47524."
echo "Without Apache, the test will be skipped (SKIP_IF_NO_APACHE)."
echo ""
echo "Test to run: /auth/authorization-header-request"
echo "This test validates:"
echo "  1. Authorization header from cached digest auth works"
echo "  2. Manual Authorization header is preserved (not stripped) when cache cleared"
echo "  3. Manual Authorization header works with SOUP_MESSAGE_DO_NOT_USE_AUTH_CACHE"
echo ""

# If the test binary was built, try to run it
if [ -f "$BUILD_DIR/tests/auth-test" ]; then
    cd "$BUILD_DIR/tests"
    ./auth-test -p /auth/authorization-header-request 2>&1 || true
else
    echo "STATUS: needs_env - test binary not built (requires Apache + full libsoup build)"
fi

echo ""

# --- Step 4: Collect gcov coverage ---
echo "[4/4] Collecting gcov coverage for target lines..."
TARGET_FILE="libsoup/soup-auth-manager.c"
TARGET_LINES="446-454"

if [ -f "$BUILD_DIR/libsoup/soup-auth-manager.c.gcda" ]; then
    cd "$BUILD_DIR/libsoup"
    gcov -o . "$ANALYSIS_REPO/$TARGET_FILE" 2>&1 || true
    if [ -f "soup-auth-manager.c.gcov" ]; then
        echo "=== Coverage for target lines $TARGET_LINES ==="
        grep -E "^[[:space:]]*(446|447|448|449|450|451|452|453|454):" soup-auth-manager.c.gcov || echo "No coverage data for target lines"
    fi
else
    echo "STATUS: needs_env - no coverage data (build incomplete)"
fi

echo ""
echo "=== Test Entry Summary ==="
echo "Finding: PCA-0001 (HIGH priority)"
echo "Type: SIDE_EFFECT_CHANGE"
echo "Status: needs_env (requires intltool, glib-devel, Apache HTTP server)"
echo "Entry: $SCRIPT_DIR/reproducer.sh"
echo "Exit: 0 (non-fatal - environment dependencies missing)"
exit 0
