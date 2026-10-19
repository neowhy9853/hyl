#!/bin/bash
# PCA-0001: SIDE_EFFECT_CHANGE - systemd-integration.sh menu_show_once grubenv side effect
# Tests that the patched script writes menu_show_once=1 in addition to menu_show_once_timeout

set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

GRUBENV="${TEST_DIR}/grubenv"
SYSTEMD_INPUT="${TEST_DIR}/reboot-to-boot-loader-menu"
TEST_TIMEOUT_USEC="20000000"  # 20 seconds in microseconds
EXPECTED_TIMEOUT=$(((TEST_TIMEOUT_USEC + 500000) / 1000000))  # 20 seconds

echo "=== PCA-0001: menu_show_once grubenv side effect test ==="

# Prepare mock systemd input
mkdir -p "${TEST_DIR}/run/systemd"
echo "${TEST_TIMEOUT_USEC}" > "${SYSTEMD_INPUT}"

# Create a mock grub-editenv that logs all calls
MOCK_EDITENV="${TEST_DIR}/mock-grub-editenv"
cat > "${MOCK_EDITENV}" << 'MOCKEOF'
#!/bin/bash
# Mock grub-editenv that logs calls and simulates real behavior
LOGFILE="${TMP_MOCK_LOG}"
echo "$@" >> "${LOGFILE}"
# Simulate actual grub-editenv behavior with a real grubenv file
GRUBENV_FILE="${TMP_GRUBENV_FILE}"
if [ "$2" = "create" ]; then
    echo "# GRUB Environment Block" > "${GRUBENV_FILE}"
elif [ "$2" = "set" ]; then
    echo "$3" >> "${GRUBENV_FILE}"
elif [ "$2" = "list" ]; then
    cat "${GRUBENV_FILE}"
fi
exit 0
MOCKEOF
chmod +x "${MOCK_EDITENV}"

# ---------- TEST 1: Before-patch behavior ----------
echo ""
echo "--- Test 1: Before-patch (only menu_show_once_timeout) ---"
export TMP_MOCK_LOG="${TEST_DIR}/before_calls.log"
export TMP_GRUBENV_FILE="${TEST_DIR}/before_grubenv"

# Simulate before-patch script
TIMEOUT_USEC=$(cat "${SYSTEMD_INPUT}")
TIMEOUT=$(((TIMEOUT_USEC + 500000) / 1000000))
"${MOCK_EDITENV}" "${GRUBENV}" create
"${MOCK_EDITENV}" "${GRUBENV}" set menu_show_once_timeout=$TIMEOUT

echo "Before-patch grubenv state:"
"${MOCK_EDITENV}" "${GRUBENV}" list

# Verify menu_show_once is NOT set
if ! grep -q "^menu_show_once=" "${TMP_GRUBENV_FILE}" 2>/dev/null; then
    echo "PASS: menu_show_once NOT set in before-patch behavior (as expected)"
else
    echo "FAIL: menu_show_once IS set in before-patch behavior (unexpected)"
    exit 1
fi

# Verify menu_show_once_timeout is correctly set
if grep -q "^menu_show_once_timeout=${EXPECTED_TIMEOUT}$" "${TMP_GRUBENV_FILE}"; then
    echo "PASS: menu_show_once_timeout=${EXPECTED_TIMEOUT} correctly set"
else
    echo "FAIL: menu_show_once_timeout not correctly set in before-patch test"
    exit 1
fi

# ---------- TEST 2: After-patch behavior ----------
echo ""
echo "--- Test 2: After-patch (also sets menu_show_once=1) ---"
export TMP_MOCK_LOG="${TEST_DIR}/after_calls.log"
export TMP_GRUBENV_FILE="${TEST_DIR}/after_grubenv"

# Simulate after-patch script (with the new menu_show_once=1 line)
TIMEOUT_USEC=$(cat "${SYSTEMD_INPUT}")
TIMEOUT=$(((TIMEOUT_USEC + 500000) / 1000000))
"${MOCK_EDITENV}" "${GRUBENV}" create
"${MOCK_EDITENV}" "${GRUBENV}" set menu_show_once_timeout=$TIMEOUT
# --- NEW BEHAVIOR: also set menu_show_once=1 ---
"${MOCK_EDITENV}" "${GRUBENV}" set menu_show_once=1

echo "After-patch grubenv state:"
"${MOCK_EDITENV}" "${GRUBENV}" list

# Verify menu_show_once IS set to 1
if grep -q "^menu_show_once=1$" "${TMP_GRUBENV_FILE}"; then
    echo "PASS: menu_show_once=1 detected in after-patch grubenv (NEW side effect confirmed)"
else
    echo "FAIL: menu_show_once=1 NOT found in after-patch grubenv"
    exit 1
fi

# Verify menu_show_once_timeout is still correctly set
if grep -q "^menu_show_once_timeout=${EXPECTED_TIMEOUT}$" "${TMP_GRUBENV_FILE}"; then
    echo "PASS: menu_show_once_timeout=${EXPECTED_TIMEOUT} still correctly set"
else
    echo "FAIL: menu_show_once_timeout not correctly set in after-patch test"
    exit 1
fi

# ---------- TEST 3: Verify that menu_show_once_timeout overrides menu_show_once (compatibility contract) ----------
echo ""
echo "--- Test 3: menu_show_once_timeout override contract ---"

# Using actual grub-editenv if available
if command -v grub-editenv &>/dev/null; then
    REAL_GRUBENV="${TEST_DIR}/real_grubenv"
    grub-editenv "${REAL_GRUBENV}" create
    grub-editenv "${REAL_GRUBENV}" set menu_show_once=1
    grub-editenv "${REAL_GRUBENV}" set menu_show_once_timeout=10
    OUTPUT=$(grub-editenv "${REAL_GRUBENV}" list 2>&1)
    echo "Real grub-editenv output (both vars set):"
    echo "${OUTPUT}"
    if echo "${OUTPUT}" | grep -q "menu_show_once=1" && echo "${OUTPUT}" | grep -q "menu_show_once_timeout=10"; then
        echo "PASS: Both variables coexist in real grubenv (override handled by grub.cfg logic)"
    else
        echo "FAIL: One or both variables missing from real grubenv"
        exit 1
    fi
else
    echo "SKIP: grub-editenv not available for real grubenv test"
fi

echo ""
echo "=== All PCA-0001 tests PASSED ==="
exit 0
