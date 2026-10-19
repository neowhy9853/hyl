#!/bin/bash
# PCA-0001: SIDE_EFFECT_CHANGE - proxyauthz enabled by default
# Config parsing test for lloadd feature handling
set -euo pipefail

RESULT_DIR="/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/compatibility-testing"
BEFORE_BIN="/tmp/pca-openldap-before/servers/lloadd/lloadd"
AFTER_BIN="/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/_worktrees/patched/servers/lloadd/lloadd"
TEST_WORK="${RESULT_DIR}/test-entry-work/PCA-0001"
RESULTS="${RESULT_DIR}/phase4_execution"

mkdir -p "${TEST_WORK}/configs" "${RESULTS}"

# Clean any stale coverage data
find /tmp/pca-openldap-before/servers/lloadd -name '*.gcda' -delete 2>/dev/null || true
find /home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/_worktrees/patched/servers/lloadd -name '*.gcda' -delete 2>/dev/null || true

# Config 1: Minimal - NO feature keyword (test default behavior)
cat > "${TEST_WORK}/configs/config_default.conf" << 'CONF1'
# Minimal lloadd config - no feature keyword
sockbuf_max_incoming_client 4194303
sockbuf_max_incoming_upstream 4194303
threads 1
bindconf
    bindmethod=simple
    rootdn "cn=admin,dc=example,dc=com"
    credentials secret
CONF1

# Config 2: Explicit enable (same as new default)
cat > "${TEST_WORK}/configs/config_enable.conf" << 'CONF2'
# Explicit enable proxyauthz
sockbuf_max_incoming_client 4194303
sockbuf_max_incoming_upstream 4194303
threads 1
enable proxyauthz
bindconf
    bindmethod=simple
    rootdn "cn=admin,dc=example,dc=com"
    credentials secret
CONF2

# Config 3: Explicit disable
cat > "${TEST_WORK}/configs/config_disable.conf" << 'CONF3'
# Explicit disable proxyauthz
sockbuf_max_incoming_client 4194303
sockbuf_max_incoming_upstream 4194303
threads 1
disable proxyauthz
bindconf
    bindmethod=simple
    rootdn "cn=admin,dc=example,dc=com"
    credentials secret
CONF3

# Config 4: Legacy 'feature' keyword (old-style)
cat > "${TEST_WORK}/configs/config_feature.conf" << 'CONF4'
# Legacy feature keyword
sockbuf_max_incoming_client 4194303
sockbuf_max_incoming_upstream 4194303
threads 1
feature proxyauthz
bindconf
    bindmethod=simple
    rootdn "cn=admin,dc=example,dc=com"
    credentials secret
CONF4

run_test() {
    local label="$1"
    local bin="$2"
    local config="$3"
    local outfile="$4"
    local extra_args="${5:-}"

    echo "=== ${label}: ${config} ===" >> "${outfile}"
    # Use timeout to prevent hanging; ignore non-zero exit (socket bind EPERM expected)
    timeout 10 "${bin}" -d 1 -f "${TEST_WORK}/configs/${config}.conf" ${extra_args} >> "${outfile}" 2>&1 || true
    echo "--- END ${label} ---" >> "${outfile}"
    echo "" >> "${outfile}"
}

echo "==========================================" > "${RESULTS}/config_test_results.txt"
echo "PCA-0001: Config Parsing Test Results" >> "${RESULTS}/config_test_results.txt"
echo "Before: $(file ${BEFORE_BIN} | cut -d, -f1)" >> "${RESULTS}/config_test_results.txt"
echo "After: $(file ${AFTER_BIN} | cut -d, -f1)" >> "${RESULTS}/config_test_results.txt"
echo "==========================================" >> "${RESULTS}/config_test_results.txt"
echo "" >> "${RESULTS}/config_test_results.txt"

# Test all 4 configs on BEFORE binary
for cfg in config_default config_enable config_disable config_feature; do
    run_test "BEFORE" "${BEFORE_BIN}" "${cfg}" "${RESULTS}/config_test_results.txt"
done

# Clear before coverage (it was separately accumulated)
find /tmp/pca-openldap-before -name '*.gcda' -delete 2>/dev/null || true

# Test all 4 configs on AFTER binary
for cfg in config_default config_enable config_disable config_feature; do
    run_test "AFTER" "${AFTER_BIN}" "${cfg}" "${RESULTS}/config_test_results.txt"
done

echo "=== CONFIG TEST COMPLETE ===" >> "${RESULTS}/config_test_results.txt"
echo "Output written to ${RESULTS}/config_test_results.txt"
