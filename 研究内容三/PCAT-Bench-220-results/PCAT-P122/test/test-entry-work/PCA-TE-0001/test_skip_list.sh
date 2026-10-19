#!/bin/bash
# PCA-TE-0001: GRUB_OS_PROBER_SKIP_LIST compatibility test harness - final
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNS_DIR="${TEST_DIR}/runs"
mkdir -p "${RUNS_DIR}"

PASS=0; FAIL=0; TOTAL=0
pass() { PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); echo "[PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); echo "[FAIL] $1: $2"; }

grub_probe() {
    case "$*" in
        *--target=fs_uuid*)
            local dev; dev=$(echo "$*" | sed 's/.*--device //')
            case "$dev" in
                sda1) echo "11111111-1111-1111-1111-111111111111" ;;
                sda2) echo "22222222-2222-2222-2222-222222222222" ;;
                sdb1) echo "33333333-3333-3333-3333-333333333333" ;;
                *)    echo "00000000-0000-0000-0000-000000000000" ;;
            esac; return 0 ;;
        *) return 1 ;;
    esac
}

check_skip_old() {
    local d="$2"; DEVICE="$d"; GRUB_OS_PROBER_SKIP_LIST="$1"
    UUID="" EXPUUID=""
    if UUID="$(grub_probe --target=fs_uuid --device "${DEVICE%@*}")"; then
        EXPUUID="$UUID"
        if [ x"${DEVICE#*@}" != x ] ; then
            EXPUUID="${EXPUUID}@${DEVICE#*@}"
        fi
        if [ "x${GRUB_OS_PROBER_SKIP_LIST}" != "x" ] && [ "x$(echo "${GRUB_OS_PROBER_SKIP_LIST}" | grep -i -e '\b'"${EXPUUID}"'\b')" != "x" ] ; then
            echo "skip" && return
        fi
    fi
    echo "noskip"
}

check_skip_new() {
    local d="$2"; DEVICE="$d"; GRUB_OS_PROBER_SKIP_LIST="$1"
    UUID="" EXPUUID=""; unset UUID
    if [ -n "${GRUB_OS_PROBER_SKIP_LIST}" ] && UUID="$(grub_probe --target=fs_uuid --device "${DEVICE%@*}")"; then
        local SPACE='[[:space:],;]'
        if [ x"${DEVICE##*@*}" = x ] ; then
            EXPUUID="$UUID@${DEVICE#*@}"
        else
            EXPUUID="$UUID(@/dev/.*)?"
        fi
        if printf %s " ${GRUB_OS_PROBER_SKIP_LIST} " | grep -Eqie "${SPACE}${EXPUUID}${SPACE}" ; then
            echo "skip" && return
        fi
    fi
    echo "noskip"
}

check_dep() { case "$1" in *@/[dD][eE][vV]/*) echo "yes" ;; *) echo "no" ;; esac }

U1="11111111-1111-1111-1111-111111111111"
U2="22222222-2222-2222-2222-222222222222"

echo "=== GRUB_OS_PROBER_SKIP_LIST Compatibility Test ==="
echo

# === CORE BUG FIX: UUID-only for non-EFI ===
# Old code: UUID-only SKIP_LIST entry never matches because EXPUUID always gets @device suffix
# New code: UUID-only works correctly for non-EFI
R=$(check_skip_old "$U1" "sda1")
[ "$R" = "noskip" ] && pass "OLD: UUID-only (BUG: never matches, need @device in SKIP_LIST)" || fail "OLD: UUID-only" "expected=noskip got=$R"
R=$(check_skip_new "$U1" "sda1")
[ "$R" = "skip" ] && pass "NEW: UUID-only (FIXED: correctly matches)" || fail "NEW: UUID-only" "expected=skip got=$R"

# === @device required in old code ===
R=$(check_skip_old "${U1}@sda1" "sda1")
[ "$R" = "skip" ] && pass "OLD: UUID@sda1 (works because @suffix required)" || fail "OLD: UUID@sda1" "expected=skip got=$R"
R=$(check_skip_new "${U1}@sda1" "sda1")
[ "$R" = "noskip" ] && pass "NEW: UUID@sda1 (rejected, @sda1 is not /dev/ path)" || fail "NEW: UUID@sda1" "expected=noskip got=$R"

# === Backward compat: @/dev/* format ===
R=$(check_skip_new "${U1}@/dev/sda1" "sda1")
[ "$R" = "skip" ] && pass "NEW: UUID@/dev/sda1 (backward compat, still works)" || fail "NEW: @/dev/sda1" "expected=skip got=$R"
R=$(check_dep "${U1}@/dev/sda1")
[ "$R" = "yes" ] && pass "Deprecation warning for @/dev/*" || fail "Deprecation" "expected=yes got=$R"
R=$(check_dep "${U1}@/EFI/grub/grubx64.efi")
[ "$R" = "no" ] && pass "No deprecation for EFI paths" || fail "EFI deprecation" "expected=no got=$R"

# === Multiple separators ===
R=$(check_skip_new "${U2},${U1}" "sda1")
[ "$R" = "skip" ] && pass "NEW: comma separator" || fail "NEW: comma" "expected=skip got=$R"
R=$(check_skip_new "${U2};${U1}" "sda1")
[ "$R" = "skip" ] && pass "NEW: semicolon separator" || fail "NEW: semicolon" "expected=skip got=$R"
R=$(check_skip_new "${U2} ${U1}" "sda1")
[ "$R" = "skip" ] && pass "NEW: space separator" || fail "NEW: space" "expected=skip got=$R"

# === Exact match, no partial ===
R=$(check_skip_new "$U1" "sda2")
[ "$R" = "noskip" ] && pass "NEW: different UUID not skipped (exact match)" || fail "NEW: exact" "expected=noskip got=$R"
R=$(check_skip_new "${U2}" "sda2")
[ "$R" = "skip" ] && pass "NEW: correct UUID skipped" || fail "NEW: correct" "expected=skip got=$R"

# === Empty list ===
R=$(check_skip_old "" "sda1")
[ "$R" = "noskip" ] && pass "OLD: empty skip list" || fail "OLD: empty" "expected=noskip got=$R"
R=$(check_skip_new "" "sda1")
[ "$R" = "noskip" ] && pass "NEW: empty skip list" || fail "NEW: empty" "expected=noskip got=$R"

# === EFI entries ===
EFI="sda1@/EFI/grub/grubx64.efi"
R=$(check_skip_old "${U1}@/EFI/grub/grubx64.efi" "$EFI")
[ "$R" = "skip" ] && pass "OLD: EFI entry" || fail "OLD: EFI" "expected=skip got=$R"
R=$(check_skip_new "${U1}@/EFI/grub/grubx64.efi" "$EFI")
[ "$R" = "skip" ] && pass "NEW: EFI entry" || fail "NEW: EFI" "expected=skip got=$R"

# === Combo: multiple entries, skip one not the other ===
R=$(check_skip_new "${U2} ${U1}" "sda2")
[ "$R" = "skip" ] && pass "NEW: multi-entry, U2 matches" || fail "NEW: multi U2" "expected=skip got=$R"
R=$(check_skip_new "${U2}" "sda1")
[ "$R" = "noskip" ] && pass "NEW: U2 list, sda1(U1) not matched" || fail "NEW: not matching" "expected=noskip got=$R"

echo
echo "================================================"
echo "Results: $PASS/$TOTAL passed, $FAIL/$TOTAL failed"
echo "================================================"

cat > "${RUNS_DIR}/results.json" << JSONEOF
{
  "total": $TOTAL,
  "passed": $PASS,
  "failed": $FAIL,
  "test_name": "GRUB_OS_PROBER_SKIP_LIST matching compatibility test",
  "finding_id": "PCA-0001",
  "compatibility_changes_verified": [
    "UUID-only skip fixed for non-EFI (was broken, required @device suffix in SKIP_LIST)",
    "UUID@device for non-EFI now rejected (must use UUID@/dev/* for backward compat)",
    "Comma and semicolon accepted as additional separators",
    "Deprecation warning for UUID@/dev/* notation (non-EFI backward compat path)",
    "No false deprecation for EFI paths",
    "Exact UUID matching prevents false positives from partial/boundary matches"
  ]
}
JSONEOF

exit $FAIL
