#!/bin/sh
set -eu

VERSION=${1:?usage: probe_contract.sh before|after input|error|side_effect}
MODE=${2:?usage: probe_contract.sh before|after input|error|side_effect}
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$VERSION" in
	before) BINARY="$ROOT/build/before/mock_before" ;;
	after) BINARY="$ROOT/build/after/mock_after" ;;
	*) echo "invalid version: $VERSION" >&2; exit 2 ;;
esac

OUTPUT=$($BINARY --drivers)

case "$MODE" in
	input)
		LINE=$(printf '%s\n' "$OUTPUT" |
			grep '"driver":"hns","case":"ro_to_local_write"')
		printf '%s\n' "$LINE" |
			sed -E 's/.*"ret":(-?[0-9]+),"errno":([0-9]+).*/ret=\1 errno=\2/'
		printf '%s\n' "$LINE" | grep -q '"ret":0'
		;;
	error)
		printf '%s\n' "$OUTPUT" |
			grep '"driver":"mlx4","case":"ro_to_local_write"' |
			sed -E 's/.*"ret":(-?[0-9]+),"errno":([0-9]+).*/ret=\1 errno=\2/'
		;;
	side_effect)
		printf '%s\n' "$OUTPUT" |
			grep '"case":"ro_to_local_write"' |
			sed -E 's/^\{"version":"[^"]+",//'
		;;
	*) echo "invalid mode: $MODE" >&2; exit 2 ;;
esac
