#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RESULT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
ANALYSIS_DIR=$(CDPATH= cd -- "$RESULT_DIR/.." && pwd)
BASELINE="$RESULT_DIR/environment/baseline"
PATCHED="$ANALYSIS_DIR/_worktrees/patched"
OUT="$RESULT_DIR/phase4_execution/abi_probe"
CC=${CC:-cc}

mkdir -p "$OUT"
BASE_INPUT_H="$BASELINE/include/uapi/linux/input.h"
PATCHED_INPUT_H="$PATCHED/include/uapi/linux/input.h"

"$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -include "$BASE_INPUT_H" "$SCRIPT_DIR/abi_probe.c" \
    -o "$OUT/abi_probe.before"
"$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -include "$PATCHED_INPUT_H" "$SCRIPT_DIR/abi_probe.c" \
    -o "$OUT/abi_probe.after"

"$OUT/abi_probe.before" >"$OUT/default.before.txt"
"$OUT/abi_probe.after" >"$OUT/default.after.txt"

read before_size before_align before_type before_code before_value before_stride \
    <"$OUT/default.before.txt"
read after_size after_align after_type after_code after_value after_stride \
    <"$OUT/default.after.txt"

if [ "$before_size" -eq "$after_size" ]; then
    echo "ERROR: sizeof(struct input_event) did not change" >&2
    exit 1
fi
if [ "$before_stride" -eq "$after_stride" ]; then
    echo "ERROR: input_event array stride did not change" >&2
    exit 1
fi
if [ "$before_type:$before_code:$before_value" != \
     "$after_type:$after_code:$after_value" ]; then
    echo "ERROR: pre-existing field offsets unexpectedly changed" >&2
    exit 1
fi

if "$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -include "$BASE_INPUT_H" "$SCRIPT_DIR/field_probe.c" \
    -o "$OUT/field_probe.before" 2>"$OUT/field_probe.before.stderr"; then
    echo "ERROR: baseline unexpectedly contains compat_reserved" >&2
    exit 1
fi

"$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -include "$PATCHED_INPUT_H" "$SCRIPT_DIR/field_probe.c" \
    -o "$OUT/field_probe.after"
"$OUT/field_probe.after" >"$OUT/field.after.txt"

"$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -D_TIME_BITS=64 -D_FILE_OFFSET_BITS=64 \
    -include "$BASE_INPUT_H" "$SCRIPT_DIR/abi_probe.c" \
    -o "$OUT/abi_probe.time64.before"
"$CC" -std=c11 -Wall -Wextra -Werror -O0 -g -D__user= \
    -D_TIME_BITS=64 -D_FILE_OFFSET_BITS=64 \
    -include "$PATCHED_INPUT_H" "$SCRIPT_DIR/abi_probe.c" \
    -o "$OUT/abi_probe.time64.after"
"$OUT/abi_probe.time64.before" >"$OUT/time64.before.txt"
"$OUT/abi_probe.time64.after" >"$OUT/time64.after.txt"

if cmp -s "$OUT/time64.before.txt" "$OUT/time64.after.txt"; then
    echo "ERROR: time64 build did not expose an ABI layout change" >&2
    exit 1
fi

printf 'ABI_CHANGE_DETECTED before_size=%s after_size=%s before_stride=%s after_stride=%s\n' \
    "$before_size" "$after_size" "$before_stride" "$after_stride"
printf 'BEFORE '
cat "$OUT/default.before.txt"
printf 'AFTER '
cat "$OUT/default.after.txt"
cat "$OUT/field.after.txt"
