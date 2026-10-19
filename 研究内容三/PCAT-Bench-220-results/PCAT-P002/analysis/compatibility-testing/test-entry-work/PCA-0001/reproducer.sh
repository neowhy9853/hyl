#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
	echo "usage: $0 BEFORE_KERNEL_SOURCE AFTER_KERNEL_SOURCE" >&2
	exit 2
fi

before_source=$1
after_source=$2
result_dir=$(cd "$(dirname "$0")/../.." && pwd)
entry_dir="$result_dir/test-entry-work/PCA-0001"
raw_dir="$result_dir/phase4_execution/raw"
mkdir -p "$raw_dir"

compile_probe() {
	local source_root=$1
	local output=$2
	cc -std=c11 -Wall -Wextra -Werror -O0 -g -D__EXPORTED_HEADERS__ \
		-include "$source_root/include/uapi/linux/uinput.h" \
		"$entry_dir/version_probe.c" -o "$output"
}

compile_legacy() {
	local source_root=$1
	local output=$2
	cc -std=c11 -Wall -Wextra -Werror -O0 -g -D__EXPORTED_HEADERS__ \
		-include "$source_root/include/uapi/linux/uinput.h" \
		"$entry_dir/legacy_consumer.c" -o "$output"
}

compile_probe "$before_source" "$raw_dir/version.before"
compile_probe "$after_source" "$raw_dir/version.after"

"$raw_dir/version.before" >"$raw_dir/version.before.stdout"
"$raw_dir/version.after" >"$raw_dir/version.after.stdout"
before_version=$(tr -d '\r\n' <"$raw_dir/version.before.stdout")
after_version=$(tr -d '\r\n' <"$raw_dir/version.after.stdout")

set +e
compile_legacy "$before_source" "$raw_dir/legacy.before" \
	>"$raw_dir/legacy.before.stdout" 2>"$raw_dir/legacy.before.stderr"
legacy_before_rc=$?
compile_legacy "$after_source" "$raw_dir/legacy.after" \
	>"$raw_dir/legacy.after.stdout" 2>"$raw_dir/legacy.after.stderr"
legacy_after_rc=$?
set -e

printf 'before_version=%s\n' "$before_version"
printf 'after_version=%s\n' "$after_version"
printf 'legacy_before_compile_rc=%s\n' "$legacy_before_rc"
printf 'legacy_after_compile_rc=%s\n' "$legacy_after_rc"

if [[ "$before_version" != 5 || "$after_version" != 6 ]]; then
	echo "unexpected macro values" >&2
	exit 1
fi

if [[ $legacy_before_rc -ne 0 || $legacy_after_rc -eq 0 ]]; then
	echo "unexpected legacy-consumer compilation result" >&2
	exit 1
fi

echo "contract_breach=UINPUT_VERSION changed from 5 to 6"
echo "reachability=compiler expanded include/uapi/linux/uinput.h:46 in both source trees"
