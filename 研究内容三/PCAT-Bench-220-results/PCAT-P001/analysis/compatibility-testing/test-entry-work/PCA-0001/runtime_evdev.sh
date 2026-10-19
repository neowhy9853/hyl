#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
RUNTIME="$ROOT/runtime-evdev"

for label in before after; do
    test -s "$RUNTIME/build/$label/arch/x86/boot/bzImage"
    bash "$RUNTIME/run_vm.sh" "$label"
done
