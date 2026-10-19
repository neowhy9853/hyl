#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
RUNTIME="$ROOT/runtime-netlink"

for label in before after after-oldheader; do
    bash "$RUNTIME/run_vm.sh" "$label"
done

grep -F 'LAYOUT_RESULT header=before size=96 align=4 stride=96 off_rx_nohandler=92 off_rx_dropped_by_xdp=-1' "$RUNTIME/results/layout.before.log"
grep -F 'LAYOUT_RESULT header=after size=100 align=4 stride=100 off_rx_nohandler=92 off_rx_dropped_by_xdp=96' "$RUNTIME/results/layout.after.log"
printf 'PCAT_P003_ENTRY_OK finding=PCA-0001\n'
