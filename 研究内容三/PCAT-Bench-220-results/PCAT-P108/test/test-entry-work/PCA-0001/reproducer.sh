#!/usr/bin/env bash
# PCA-0001: SoupKnownStatusCode → SoupStatus enum rename ABI verification
# Tests that old type name no longer works with SOUP_STATUS_* values
# and new type name works correctly.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ANALYSIS_REPO="${1:-/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P048/_worktrees/patched}"
SOURCE_REPO="${2:-/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup}"
BASE_COMMIT="${3:-11811349f8a10ce419d980c01a518c774fe8a5e5}"
TMPDIR="${SCRIPT_DIR}/tmp"
mkdir -p "$TMPDIR"

echo "=== PCA-0001: SoupKnownStatusCode → SoupStatus enum rename ABI test ==="
echo "Analysis repo: $ANALYSIS_REPO"
echo "Source repo: $SOURCE_REPO"
echo "Base commit: $BASE_COMMIT"
echo ""

# --- Test 1: New type name SoupStatus compiles with patched headers ---
echo "--- Test 1: SoupStatus (new type) compiles with patched headers ---"
cat > "$TMPDIR/test_new_type.c" << 'CEOF'
#include <libsoup/soup-status.h>
#include <stdio.h>

int main(void) {
    SoupStatus status = SOUP_STATUS_OK;
    printf("SoupStatus OK = %d\n", (int)status);
    printf("SOUP_STATUS_NOT_FOUND = %d\n", (int)SOUP_STATUS_NOT_FOUND);
    printf("SOUP_STATUS_INTERNAL_SERVER_ERROR = %d\n", (int)SOUP_STATUS_INTERNAL_SERVER_ERROR);
    return 0;
}
CEOF

if gcc -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" \
    $($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "") \
    -o "$TMPDIR/test_new_type" "$TMPDIR/test_new_type.c" 2>&1; then
    echo "PASS: SoupStatus type compiles successfully"
    "$TMPDIR/test_new_type"
else
    echo "FAIL: SoupStatus type compilation failed"
fi
echo ""

# --- Test 2: Old type name SoupKnownStatusCode with SOUP_STATUS_* values ---
echo "--- Test 2a: C compilation - SoupKnownStatusCode with SOUP_STATUS_OK ---"
cat > "$TMPDIR/test_old_type.c" << 'CEOF'
#include <libsoup/soup-status.h>
#include <stdio.h>

int main(void) {
    SoupKnownStatusCode status = SOUP_STATUS_OK;
    printf("status = %d\n", (int)status);
    return 0;
}
CEOF

GLIB_CFLAGS=$($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "")
if gcc -Wall -Werror -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" $GLIB_CFLAGS \
    -o "$TMPDIR/test_old_type" "$TMPDIR/test_old_type.c" 2>&1; then
    echo "C: Old type compiles with SOUP_STATUS_OK (C allows cross-enum assignment)"
else
    echo "C: Old type FAILS to compile (strict mode)"
fi

echo "--- Test 2b: C++ compilation - SoupKnownStatusCode with SOUP_STATUS_OK (should FAIL) ---"
cat > "$TMPDIR/test_old_type.cpp" << 'CEOF'
#include <libsoup/soup-status.h>
#include <cstdio>

int main(void) {
    SoupKnownStatusCode status = SOUP_STATUS_OK;
    printf("status = %d\n", (int)status);
    return 0;
}
CEOF

if g++ -Wall -Werror -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" $GLIB_CFLAGS \
    -o "$TMPDIR/test_old_type_cpp" "$TMPDIR/test_old_type.cpp" 2>&1; then
    echo "C++: Old type compiles (unexpected)"
else
    echo "C++: Old type FAILS to compile (ABI break confirmed for C++ consumers)"
fi

echo "--- Test 2c: C compilation with strict -Wenum-conversion ---"
if gcc -Wall -Wextra -Wenum-conversion -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" $GLIB_CFLAGS \
    -c "$TMPDIR/test_old_type.c" -o /dev/null 2>&1; then
    echo "C strict: No warnings (C is permissive with enums)"
else
    echo "C strict: Warnings generated for cross-enum assignment"
fi
echo ""

# --- Test 3: Deprecated SoupKnownStatusCode enum ---
echo "--- Test 3: Deprecated SoupKnownStatusCode enum with SOUP_KNOWN_STATUS_CODE_* values ---"
cat > "$TMPDIR/test_deprecated.c" << 'CEOF'
#include <libsoup/soup-status.h>
#include <stdio.h>

int main(void) {
    SoupKnownStatusCode status = SOUP_KNOWN_STATUS_CODE_OK;
    printf("Deprecated SoupKnownStatusCode OK = %d\n", (int)status);
    return 0;
}
CEOF

if gcc -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" \
    $($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "") \
    -o "$TMPDIR/test_deprecated" "$TMPDIR/test_deprecated.c" 2>&1; then
    echo "PASS: Deprecated SoupKnownStatusCode compiles with new value names"
    "$TMPDIR/test_deprecated"
else
    echo "FAIL: Deprecated enum compilation failed"
fi
echo ""

# --- Test 4: Compare enum values are identical ---
echo "--- Test 4: Verify enum values are numerically identical ---"
cat > "$TMPDIR/test_values.c" << 'CEOF'
#include <libsoup/soup-status.h>
#include <stdio.h>
#include <assert.h>

int main(void) {
    assert(SOUP_STATUS_OK == SOUP_KNOWN_STATUS_CODE_OK);
    assert(SOUP_STATUS_NOT_FOUND == SOUP_KNOWN_STATUS_CODE_NOT_FOUND);
    assert(SOUP_STATUS_CANCELLED == SOUP_KNOWN_STATUS_CODE_CANCELLED);
    assert(SOUP_STATUS_INTERNAL_SERVER_ERROR == SOUP_KNOWN_STATUS_CODE_INTERNAL_SERVER_ERROR);
    printf("All enum values match between SoupStatus and SoupKnownStatusCode\n");
    return 0;
}
CEOF

if gcc -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" \
    $($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "") \
    -o "$TMPDIR/test_values" "$TMPDIR/test_values.c" 2>&1; then
    echo "PASS: Enum values are numerically identical"
    "$TMPDIR/test_values"
else
    echo "FAIL: Value comparison compilation failed"
fi
echo ""

# --- Test 5: Global defines still work ---
echo "--- Test 5: Status class macros still work ---"
cat > "$TMPDIR/test_macros.c" << 'CEOF'
#include <libsoup/soup-status.h>
#include <stdio.h>
#include <assert.h>

int main(void) {
    assert(SOUP_STATUS_IS_SUCCESSFUL(200));
    assert(SOUP_STATUS_IS_REDIRECTION(301));
    assert(SOUP_STATUS_IS_CLIENT_ERROR(404));
    assert(SOUP_STATUS_IS_SERVER_ERROR(500));
    assert(SOUP_STATUS_IS_TRANSPORT_ERROR(1));
    printf("All status class macros work correctly\n");
    return 0;
}
CEOF

if gcc -I"$ANALYSIS_REPO" -I"$ANALYSIS_REPO/libsoup" \
    $($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "") \
    -o "$TMPDIR/test_macros" "$TMPDIR/test_macros.c" 2>&1; then
    echo "PASS: Status class macros work"
    "$TMPDIR/test_macros"
else
    echo "FAIL: Macro test compilation failed"
fi
echo ""

# --- Test 6: Before/After comparison with base commit header ---
echo "--- Test 6: Before-patch (base commit) header compatibility ---"
git -C "$SOURCE_REPO" show "$BASE_COMMIT:libsoup/soup-status.h" > "$TMPDIR/soup-status-old.h" 2>&1 || {
    echo "WARN: Could not extract old header from git"
}

if [ -f "$TMPDIR/soup-status-old.h" ] && [ -s "$TMPDIR/soup-status-old.h" ]; then
    cat > "$TMPDIR/test_before.c" << 'CEOF'
#include "soup-status-old.h"
#include <stdio.h>

int main(void) {
    SoupKnownStatusCode status = SOUP_STATUS_OK;
    printf("Before patch: SoupKnownStatusCode OK = %d\n", (int)status);
    return 0;
}
CEOF

    if gcc -I"$TMPDIR" -I"$ANALYSIS_REPO/libsoup" \
        $($(which pkg-config) --cflags glib-2.0 2>/dev/null || echo "") \
        -o "$TMPDIR/test_before" "$TMPDIR/test_before.c" 2>&1; then
        echo "PASS: Old type SoupKnownStatusCode compiles with old header (SOUP_STATUS_OK)"
        "$TMPDIR/test_before"
    else
        echo "FAIL: Old header compilation failed"
    fi
fi
echo ""

echo "=== PCA-0001 ABI test complete ==="
echo "Summary: Verify that SoupStatus (new) compiles, SoupKnownStatusCode with SOUP_STATUS_* does not"
