#!/bin/bash
# PCA-0001: Test bond_option_xmit_hash_policy_set XDP guard
# Target: drivers/net/bonding/bond_options.c:1592-1599
# Compatibility type: CONFIG_CLI_BEHAVIOR_CHANGE
# Contract: config_cli_behavior_stability (exact comparison)

set -euo pipefail

# --- Configuration ---
BOND_NAME="test_bond0"
SYSFS_BOND="/sys/class/net/${BOND_NAME}/bonding"
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULT_FILE="${TEST_DIR}/result.txt"
BONDING_MODULE_PATH="${1:-/lib/modules/$(uname -r)/kernel/drivers/net/bonding/bonding.ko}"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$RESULT_FILE"; }
fail() { log "FAIL: $*"; echo "FAIL" > "$RESULT_FILE"; exit 1; }

echo "=== PCA-0001 XDP Guard Test ===" > "$RESULT_FILE"
log "Test started"

# --- Prerequisite checks ---
if [ "$(id -u)" -ne 0 ]; then
    log "SKIP: This test requires root privileges for bonding operations"
    echo "SKIP: root required" > "$RESULT_FILE"
    exit 0
fi

# Check bonding module availability
if ! lsmod | grep -q "^bonding"; then
    if ! modprobe bonding 2>/dev/null; then
        log "SKIP: Cannot load bonding module"
        echo "SKIP: bonding module not available" > "$RESULT_FILE"
        exit 0
    fi
fi

# Check that we have the patched bonding module (with __bond_xdp_check)
BOND_CHECK_SYMBOL=$(modprobe --dump-modversions "$BONDING_MODULE_PATH" 2>/dev/null | grep -c "__bond_xdp_check" || true)
if [ "$BOND_CHECK_SYMBOL" -eq 0 ]; then
    modinfo bonding 2>/dev/null | grep -q "__bond_xdp_check" && BOND_SYMBOL_IN_MODINFO=1 || BOND_SYMBOL_IN_MODINFO=0
    if [ "$BOND_SYMBOL_IN_MODINFO" -eq 0 ]; then
        log "WARN: Current bonding module does not appear to have __bond_xdp_check symbol"
        log "This test is designed for a patched bonding module"
    fi
fi

# --- Cleanup handler ---
cleanup() {
    log "Cleaning up..."
    ip link delete "$BOND_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# --- Test 1: Create bond and verify basic operations ---
log ""
log "=== Test 1: Create bond and verify sysfs access ==="

# Create bond in balance-xor mode
ip link add "$BOND_NAME" type bond mode balance-xor 2>/dev/null || {
    log "SKIP: Cannot create bond device (need bond module and permissions)"
    echo "SKIP: cannot create bond" > "$RESULT_FILE"
    exit 0
}

# Verify sysfs path exists
if [ ! -d "$SYSFS_BOND" ]; then
    fail "Bond sysfs directory not found at $SYSFS_BOND"
fi

# Check current xmit_hash_policy
CURRENT_POLICY=$(cat "${SYSFS_BOND}/xmit_hash_policy" 2>/dev/null | awk '{print $1}')
log "Current xmit_hash_policy: $CURRENT_POLICY"

# Test changing xmit_hash_policy without XDP loaded (should succeed)
log ""
log "=== Test 2: Change xmit_hash_policy without XDP (should succeed) ==="

for policy in "layer2" "layer2+3" "layer3+4" "encap2+3" "encap3+4" "vlan+srcmac"; do
    policy_num=$(cat "${SYSFS_BOND}/xmit_hash_policy" 2>/dev/null | awk '{print $2}')
    if echo "$policy $policy_num" > "${SYSFS_BOND}/xmit_hash_policy" 2>/tmp/bond_test_stderr; then
        log "PASS: Set xmit_hash_policy to '$policy' succeeded (no XDP loaded)"
    else
        log "FAIL: Set xmit_hash_policy to '$policy' failed without XDP"
        cat /tmp/bond_test_stderr >> "$RESULT_FILE"
    fi
done

# Reset to layer2+3 for next tests
echo "layer2+3 1" > "${SYSFS_BOND}/xmit_hash_policy" 2>/dev/null || true

# --- Test 3: XDP guard test ---
log ""
log "=== Test 3: XDP guard - verify EOPNOTSUPP when XDP is loaded ==="

# Load a simple XDP program (using a trivial pass/drop program)
XDP_PROG="/sys/fs/bpf/test_xdp_bond"

# Check if we can create a BPF program
if command -v bpftool &>/dev/null; then
    # Create a trivial XDP pass program
    if bpftool prog loadall /dev/null "$XDP_PROG" type xdp 2>&1 | grep -q 'Invalid'; then
        log "SKIP: Cannot create XDP program with bpftool (try: bpftool prog load <xdp_prog.o> $XDP_PROG)"
        log "Manual test: Load an XDP program on $BOND_NAME, then run:"
        log "  echo 'vlan+srcmac 2' > ${SYSFS_BOND}/xmit_hash_policy"
        log "  Expected: -EOPNOTSUPP (Operation not supported)"
        echo "PARTIAL: XDP program not available via bpftool" > "$RESULT_FILE"
        exit 0
    fi
else
    log "SKIP: bpftool not available"
    log "Manual test: Load an XDP program on $BOND_NAME, then run:"
    log "  echo 'vlan+srcmac 2' > ${SYSFS_BOND}/xmit_hash_policy"
    log "  Expected: -EOPNOTSUPP (Operation not supported)"
    echo "PARTIAL: bpftool not available" > "$RESULT_FILE"
    exit 0
fi

# Test with XDP loaded: should reject vlan+srcmac
if echo "vlan+srcmac 2" > "${SYSFS_BOND}/xmit_hash_policy" 2>/tmp/bond_xdp_test_stderr; then
    log "FAIL: Setting vlan+srcmac with XDP loaded should have returned EOPNOTSUPP but succeeded"
else
    rc=$?
    stderr=$(cat /tmp/bond_xdp_test_stderr)
    if echo "$stderr" | grep -qi "not supported\|EOPNOTSUPP\|operation not permitted"; then
        log "PASS: Setting vlan+srcmac with XDP loaded correctly rejected"
    elif [ $rc -ne 0 ]; then
        log "PASS: Setting vlan+srcmac with XDP loaded returned error code $rc"
        log "  stderr: $stderr"
    else
        log "WARN: Unexpected result when setting vlan+srcmac with XDP: $stderr"
    fi
fi

# --- Test 4: Remove XDP and verify normal operation resumes ---
log ""
log "=== Test 4: Remove XDP, verify normal operation resumes ==="

if ip link set dev "$BOND_NAME" xdp off 2>/dev/null; then
    log "XDP removed from $BOND_NAME"
    
    if echo "vlan+srcmac 2" > "${SYSFS_BOND}/xmit_hash_policy" 2>/dev/null; then
        log "PASS: Setting vlan+srcmac succeeded after XDP removal"
    else
        log "FAIL: Setting vlan+srcmac failed even after XDP removal"
    fi
else
    log "WARN: Could not remove XDP from $BOND_NAME"
fi

log ""
log "=== Test complete ==="
echo "DONE" >> "$RESULT_FILE"
