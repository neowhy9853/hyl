#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 BEFORE_CONFIGURED_SOURCE AFTER_CONFIGURED_SOURCE" >&2
    exit 2
fi
before_dir=$1
after_dir=$2
probe_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT

cc -I"$before_dir" -I"$before_dir/runtime" "$probe_dir/tcp_layout_probe.c" -o "$work_dir/before-probe"
cc -I"$after_dir" -I"$after_dir/runtime" "$probe_dir/tcp_layout_probe.c" -o "$work_dir/after-probe"
"$work_dir/before-probe" > "$work_dir/before.txt"
"$work_dir/after-probe" > "$work_dir/after.txt"
diff -u "$work_dir/before.txt" "$work_dir/after.txt"
