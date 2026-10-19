#!/bin/bash
# PCA-0001: Bluetooth MGMT INPUT_CONTRACT_CHANGE directed test
#
# This script builds and runs a reproducer that tests the
# MGMT_OP_ADD_EXT_ADV_DATA input length validation change.
#
# Prerequisites:
#   1. Kernel with CONFIG_BT=y, CONFIG_BT_MGMT=y
#   2. Bluetooth HCI device available (real or hci_vhci)
#   3. CAP_NET_ADMIN (run as root)
#   4. gcc and standard libc headers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPRODUCER_BIN="${SCRIPT_DIR}/mgmt_reproducer"
REPRODUCER_SRC="${SCRIPT_DIR}/mgmt_reproducer.c"
OUTPUT_FILE="${SCRIPT_DIR}/reproducer_output.txt"
TIMEOUT_SEC=30

echo "=== PCA-0001 directed test ==="
echo "Target: MGMT_OP_ADD_EXT_ADV_DATA input length validation"
echo "Patch: != -> > length check in add_ext_adv_data()"
echo ""

# Check for root
if [ "$(id -u)" -ne 0 ]; then
    echo "SKIP: This test requires root privileges (CAP_NET_ADMIN) to open HCI_CHANNEL_CONTROL."
    echo "Run: sudo bash $0"
    echo ""
    echo "Alternatively, verify the logic manually:"
    echo "  - This patch changes 'expected_len != data_len' to 'expected_len > data_len'"
    echo "  - Before: extra trailing bytes => MGMT_STATUS_INVALID_PARAMS rejection"
    echo "  - After:  extra trailing bytes => silently ignored, command accepted"
    echo "  - This restores backward compat with bluetoothd versions that send extra bytes"
    exit 77  # SKIP
fi

# Check for Bluetooth MGMT capability
if [ ! -d /sys/class/bluetooth ]; then
    echo "WARN: /sys/class/bluetooth not found. Bluetooth subsystem may not be loaded."
    echo "Try: modprobe bluetooth && modprobe btusb (or hci_vhci for virtual testing)"
fi

# Build reproducer
echo "Building reproducer..."
gcc -O0 -g -Wall -o "${REPRODUCER_BIN}" "${REPRODUCER_SRC}" || {
    echo "FAIL: Build failed. Missing gcc or headers?"
    exit 1
}
echo "Build OK"

# Run reproducer with timeout
echo ""
echo "Running reproducer (timeout ${TIMEOUT_SEC}s)..."
timeout "${TIMEOUT_SEC}" "${REPRODUCER_BIN}" 2>&1 | tee "${OUTPUT_FILE}"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "---"
case ${EXIT_CODE} in
    0)
        echo "PASS: All test cases passed."
        ;;
    77)
        echo "SKIP: Test environment not available."
        ;;
    124)
        echo "TIMEOUT: Reproductor hung."
        ;;
    *)
        echo "RESULT: ${EXIT_CODE} - See output above for details."
        ;;
esac

# Coverage reachability signal
echo ""
echo "Coverage signal: gcov should show net/bluetooth/mgmt.c lines 9147-9149 executed"
echo "Verify with: gcov -o net/bluetooth/ net/bluetooth/mgmt.c  (on instrumented kernel)"
echo "Expected: line 9149 (if expected_len > data_len) should be hit"

exit ${EXIT_CODE}
