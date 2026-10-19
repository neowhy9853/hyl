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
coverage_root="$result_dir/phase4_execution/coverage"
mkdir -p "$coverage_root/before" "$coverage_root/after"

run_one() {
	local label=$1
	local headers=$2
	local coverage_dir="$coverage_root/$label"
	local binary="$coverage_dir/ctl_maxname_probe"

	cc -std=c11 -Wall -Wextra -Werror -O0 -g --coverage \
		-I"$headers/include" \
		"$entry_dir/ctl_maxname_probe.c" -o "$binary"
	"$binary" --describe >"$coverage_dir/probe.stdout"

	set +e
	(
		cd "$coverage_dir"
		gcov -b -c -o "$coverage_dir" "$entry_dir/ctl_maxname_probe.c"
	) >"$coverage_dir/probe.gcov.stdout" \
	  2>"$coverage_dir/probe.gcov.stderr"
	probe_gcov_rc=$?
	(
		cd "$coverage_dir"
		gcov -b -c -o "$coverage_dir" "$headers/include/linux/sysctl.h"
	) >"$coverage_dir/sysctl-header.gcov.stdout" \
	  2>"$coverage_dir/sysctl-header.gcov.stderr"
	header_gcov_rc=$?
	set -e

	printf '%s\n' "$probe_gcov_rc" >"$coverage_dir/probe.gcov.rc"
	printf '%s\n' "$header_gcov_rc" >"$coverage_dir/sysctl-header.gcov.rc"
	printf '%s probe_gcov_rc=%s header_gcov_rc=%s\n' \
		"$label" "$probe_gcov_rc" "$header_gcov_rc"
}

run_one before "$before_headers"
run_one after "$after_headers"
echo "coverage_control=runtime probe has counters; CTL_MAXNAME macro declaration has none"
