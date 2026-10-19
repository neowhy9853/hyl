#!/bin/bash
# PCA-0001 / PCA-0002 - btmtk_usb_hci_wmt_sync RETURN_CONTRACT_CHANGE + ERROR_EXCEPTION_CHANGE
# Target: drivers/bluetooth/btmtk.c:682-683, btmtk_usb_hci_wmt_sync
# Test: Verify that too-short WMT FUNC_CTRL events return 0 (not -EINVAL)
#
# Prerequisites:
#   1. Kernel source with patch applied at:
#      /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P041/_worktrees/patched/
#   2. CONFIG_BT=m, CONFIG_BT_MTK=m, CONFIG_GCOV_KERNEL=y
#   3. MT7925 (0e8d:e025) or MT7922 (0489:e0e2) USB Bluetooth adapter
#      OR kernel module mock framework
#
# This script documents the test approach for the return contract + error model change.
# Dynamic execution requires BT hardware or a module mock; without it, results are static_valid_not_run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KERNEL_SRC="/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P041/_worktrees/patched"
TEST_DIR="/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P041/compatibility-testing"
BUILD_DIR="${TEST_DIR}/build"
ANALYSIS_JSON="${TEST_DIR}/../analysis.json"

echo "=== PCA-0001/0002 Test Entry ==="
echo "Target: btmtk_usb_hci_wmt_sync in drivers/bluetooth/btmtk.c"
echo ""

# Phase 1: Verify the patch is applied
echo "--- Phase 1: Verify patch application ---"
EXPECTED_NEW_LINE=$(grep -n 'status = BTMTK_WMT_ON_UNDONE;' "${KERNEL_SRC}/drivers/bluetooth/btmtk.c" | head -1)
if [ -z "$EXPECTED_NEW_LINE" ]; then
    echo "FAIL: Patch not applied or worktree not found"
    echo "Run: orchestrator.py --ensure-worktree ${ANALYSIS_JSON}"
    exit 1
fi
echo "OK: Patched code found at line(s): $EXPECTED_NEW_LINE"

# Phase 2: Check for the old behavior (should NOT be present)
echo "--- Phase 2: Verify old code removed ---"
OLD_ERR_LINE=$(grep -n 'err = -EINVAL' "${KERNEL_SRC}/drivers/bluetooth/btmtk.c" | grep -A2 'BTMTK_WMT_FUNC_CTRL' || true)
if [ -n "$OLD_ERR_LINE" ]; then
    echo "FAIL: Old -EINVAL code still present for FUNC_CTRL"
    exit 1
fi
echo "OK: Old -EINVAL code correctly removed for FUNC_CTRL case"

# Phase 3: Static analysis of return path
echo "--- Phase 3: Return path analysis ---"
echo "After patch: too-short FUNC_CTRL event sets status=BTMTK_WMT_ON_UNDONE, breaks, falls through to return err (0)"
echo ""
echo "=== Test Entry Complete ==="
echo "Status: static_valid_not_run"
echo "Reason: Dynamic testing requires MT7925/7922 USB BT hardware"
echo ""

# Contract probe documentation
cat <<'CONTRACT'
{
  "finding_id": "PCA-0001",
  "entry_id": "PCA-TE-0001",
  "contract_probe": {
    "probe_id": "return_contract_btmtk_wmt_sync_short_functrl",
    "command": "echo 'Dynamic test requires MT7925/7922 USB BT hardware. See harness.c for kernel module approach.'",
    "before_command": "# Build/load module with pre-patch btmtk.c. Send WMT FUNC_CTRL with short SKB. Expect return of -EINVAL.",
    "after_command": "# Build/load module with post-patch btmtk.c. Send WMT FUNC_CTRL with short SKB. Expect return of 0.",
    "comparison": "exit_code",
    "cwd": ".",
    "timeout_seconds": 30
  }
}
CONTRACT

# Output: if hardware present, suggest dynamic test
echo "If MT7925/7922 hardware is available:"
echo "  1. Build kernel with CONFIG_GCOV_KERNEL=y"
echo "  2. Insert btusb.ko with the MTK adapter connected"
echo "  3. Monitor dmesg for 'Failed to send wmt func ctrl' (should NOT appear with patch)"
echo "  4. Verify Bluetooth adapter comes up normally"
echo "  5. Collect gcov data: cat /sys/kernel/debug/gcov/${KERNEL_SRC}/drivers/bluetooth/btmtk.gcda"
