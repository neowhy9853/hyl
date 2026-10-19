#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BUILD="$ROOT/build"
LOGS="$ROOT/logs"
cd "$ROOT"
mkdir -p "$BUILD/before" "$BUILD/after" "$BUILD/config-n" "$LOGS"

COMMON="-std=c11 -Wall -Wextra -Werror -O0 -g -fprofile-arcs -ftest-coverage"
gcc $COMMON -DPATCHED=0 -DCONFIG_USER_MEM=1 \
	-o "$BUILD/before/mock_before" "$ROOT/mock_rereg.c"
gcc $COMMON -DPATCHED=1 -DCONFIG_USER_MEM=1 \
	-o "$BUILD/after/mock_after" "$ROOT/mock_rereg.c"
gcc $COMMON -DPATCHED=1 -DCONFIG_USER_MEM=0 \
	-o "$BUILD/config-n/mock_after_config_n" "$ROOT/mock_rereg.c"

find "$BUILD" -name '*.gcda' -delete
"$BUILD/before/mock_before" >"$LOGS/before.jsonl" 2>"$LOGS/before.stderr"
"$BUILD/after/mock_after" >"$LOGS/after.jsonl" 2>"$LOGS/after.stderr"
"$BUILD/config-n/mock_after_config_n" --helper \
	>"$LOGS/config-n.jsonl" 2>"$LOGS/config-n.stderr"

gcov -b -c -o "$BUILD/before" \
	"$BUILD/before/mock_before-mock_rereg.gcno" \
	>"$LOGS/gcov-before.log" 2>&1
mv "$ROOT/mock_rereg.c.gcov" "$LOGS/mock_rereg.before.gcov"
gcov -b -c -o "$BUILD/after" \
	"$BUILD/after/mock_after-mock_rereg.gcno" \
	>"$LOGS/gcov-after.log" 2>&1
mv "$ROOT/mock_rereg.c.gcov" "$LOGS/mock_rereg.after.gcov"
gcov -b -c -o "$BUILD/config-n" \
	"$BUILD/config-n/mock_after_config_n-mock_rereg.gcno" \
	>"$LOGS/gcov-config-n.log" 2>&1
mv "$ROOT/mock_rereg.c.gcov" "$LOGS/mock_rereg.config-n.gcov"

diff -u "$LOGS/before.jsonl" "$LOGS/after.jsonl" >"$LOGS/before-after.diff" || true
grep 'PCAT_P099_MOCK_DONE failures=0' "$LOGS/before.jsonl"
grep 'PCAT_P099_MOCK_DONE failures=0' "$LOGS/after.jsonl"
grep 'PCAT_P099_MOCK_DONE failures=0' "$LOGS/config-n.jsonl"
echo PCAT_P099_MOCK_SUITE_PASS
