#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
	echo "usage: $0 BEFORE_HEADERS AFTER_HEADERS" >&2
	exit 2
fi

before_headers=$1
after_headers=$2
result_dir=$(cd "$(dirname "$0")/../.." && pwd)
entry_dir="$result_dir/test-entry-work/PCA-0001"
probe_root="$result_dir/phase2_environment/probes"
raw_dir="$result_dir/phase4_execution/raw"
mkdir -p "$probe_root/before" "$probe_root/after" "$raw_dir"

compile_probe() {
	local headers=$1
	local output=$2
	cc -std=c11 -Wall -Wextra -Werror -O0 -g \
		-I"$headers/include" \
		"$entry_dir/ctl_maxname_probe.c" -o "$output"
}

compile_legacy() {
	local headers=$1
	local output=$2
	cc -std=c11 -Wall -Wextra -Werror -O0 -g \
		-I"$headers/include" \
		"$entry_dir/legacy_consumer.c" -o "$output"
}

compile_probe "$before_headers" "$probe_root/before/ctl_maxname_probe"
compile_probe "$after_headers" "$probe_root/after/ctl_maxname_probe"

"$probe_root/before/ctl_maxname_probe" --describe >"$raw_dir/describe.before.stdout"
"$probe_root/after/ctl_maxname_probe" --describe >"$raw_dir/describe.after.stdout"

for nlen in -1 0 8 9 10 11; do
	set +e
	"$probe_root/before/ctl_maxname_probe" --nlen "$nlen" \
		>"$raw_dir/nlen-${nlen}.before.stdout" \
		2>"$raw_dir/nlen-${nlen}.before.stderr"
	before_rc=$?
	"$probe_root/after/ctl_maxname_probe" --nlen "$nlen" \
		>"$raw_dir/nlen-${nlen}.after.stdout" \
		2>"$raw_dir/nlen-${nlen}.after.stderr"
	after_rc=$?
	set -e
	printf '%s\n' "$before_rc" >"$raw_dir/nlen-${nlen}.before.rc"
	printf '%s\n' "$after_rc" >"$raw_dir/nlen-${nlen}.after.rc"
	done

set +e
compile_legacy "$before_headers" "$probe_root/before/legacy_consumer" \
	>"$raw_dir/legacy.before.stdout" 2>"$raw_dir/legacy.before.stderr"
legacy_before_rc=$?
compile_legacy "$after_headers" "$probe_root/after/legacy_consumer" \
	>"$raw_dir/legacy.after.stdout" 2>"$raw_dir/legacy.after.stderr"
legacy_after_rc=$?
set -e
printf '%s\n' "$legacy_before_rc" >"$raw_dir/legacy.before.rc"
printf '%s\n' "$legacy_after_rc" >"$raw_dir/legacy.after.rc"

before_value=$(sed -n '1p' "$raw_dir/describe.before.stdout")
after_value=$(sed -n '1p' "$raw_dir/describe.after.stdout")
before_9=$(sed -n '1p' "$raw_dir/nlen-9.before.rc")
after_9=$(sed -n '1p' "$raw_dir/nlen-9.after.rc")
before_10=$(sed -n '1p' "$raw_dir/nlen-10.before.rc")
after_10=$(sed -n '1p' "$raw_dir/nlen-10.after.rc")

printf 'before=%s\n' "$before_value"
printf 'after=%s\n' "$after_value"
printf 'nlen9_before_rc=%s nlen9_after_rc=%s\n' "$before_9" "$after_9"
printf 'nlen10_before_rc=%s nlen10_after_rc=%s\n' "$before_10" "$after_10"
printf 'legacy_before_compile_rc=%s legacy_after_compile_rc=%s\n' \
	"$legacy_before_rc" "$legacy_after_rc"

if [[ "$before_value" != "CTL_MAXNAME=10 array_count=10 array_bytes=40" ]]; then
	echo "unexpected before header observation" >&2
	exit 1
fi
if [[ "$after_value" != "CTL_MAXNAME=8 array_count=8 array_bytes=32" ]]; then
	echo "unexpected after header observation" >&2
	exit 1
fi
if [[ "$before_9" -ne 0 || "$after_9" -ne 1 ||
	  "$before_10" -ne 0 || "$after_10" -ne 1 ]]; then
	echo "old-valid boundary did not tighten as expected" >&2
	exit 1
fi
if [[ "$legacy_before_rc" -ne 0 || "$legacy_after_rc" -eq 0 ]]; then
	echo "legacy consumer compilation result was not discriminating" >&2
	exit 1
fi

echo "contract_breach=CTL_MAXNAME input boundary tightened from 10 to 8"
echo "reachability=headers_install output expanded include/uapi/linux/sysctl.h:30"
