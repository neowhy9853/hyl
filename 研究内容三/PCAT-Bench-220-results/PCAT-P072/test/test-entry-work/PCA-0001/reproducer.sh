#!/bin/bash
# PCA-0001 Reproducer: Config integer parsing INPUT_CONTRACT_CHANGE
# Tests that strtoll endptr checks properly reject non-numeric
# and trailing-character integer config values.
set -euo pipefail

RESULT_DIR="/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/compatibility-testing"
SOURCE_REPO="/home/soong/pca_benchmark/_repos/lvm2"
PATCH_ID="591a1c9310506124685cacc75aa338e31a148a06"
BASE_COMMIT="d804677c7565bff40c87ed830473674119f23f6a"

BUILD_DIR="${RESULT_DIR}/phase2_build"
BEFORE_DIR="${BUILD_DIR}/before"
AFTER_DIR="${BUILD_DIR}/after"
CONFIG_DIR="${RESULT_DIR}/phase3_inputs/configs"
OUTPUT_DIR="${RESULT_DIR}/phase4_execution"

mkdir -p "${BEFORE_DIR}" "${AFTER_DIR}" "${CONFIG_DIR}" "${OUTPUT_DIR}"

echo "=== PCA-0001 Reproducer: Config Integer Parsing ==="

# ---- Step 1: Build Before (baseline) and After (patched) ----
echo "--- Step 1: Setting up build worktrees ---"

# Before: checkout base_commit
if [ ! -f "${BEFORE_DIR}/tools/lvm" ]; then
    echo "Building BEFORE (baseline, base_commit=${BASE_COMMIT})..."
    if [ ! -d "${BEFORE_DIR}/src" ]; then
        git -C "${SOURCE_REPO}" worktree add --detach "${BEFORE_DIR}/src" "${BASE_COMMIT}" 2>/dev/null || true
    fi
    cd "${BEFORE_DIR}/src"
    ./configure CFLAGS='-O0 -g --coverage' LDFLAGS='--coverage' \
        --disable-udev_sync --disable-udev_rules --disable-selinux \
        --disable-readline --without-blkid \
        --with-thin=none --with-cache=none --with-vdo=none \
        --with-writecache=none --disable-lvmimportvdo 2>&1 | tail -5
    make -j"$(nproc)" 2>&1 | tail -10
    echo "BEFORE build complete"
else
    echo "BEFORE build already exists"
fi

# After: use pre-built worktree from analysis
if [ ! -f "${AFTER_DIR}/tools/lvm" ]; then
    ANALYSIS_REPO="/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/_worktrees/patched"
    if [ -d "${ANALYSIS_REPO}" ]; then
        echo "Building AFTER (patched) from analysis_repo..."
        # Use analysis_repo directly but copy to after dir for isolated build
        rsync -a "${ANALYSIS_REPO}/" "${AFTER_DIR}/src/" --exclude='_worktrees' --exclude='pca-results' 2>/dev/null || \
        git -C "${SOURCE_REPO}" worktree add --detach "${AFTER_DIR}/src" "${BASE_COMMIT}" 2>/dev/null || true
        cd "${AFTER_DIR}/src"
        # Apply the patch
        git am < /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/patch.diff 2>/dev/null || \
        git apply /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/patch.diff 2>/dev/null || true
        ./configure CFLAGS='-O0 -g --coverage' LDFLAGS='--coverage' \
            --disable-udev_sync --disable-udev_rules --disable-selinux \
            --disable-readline --without-blkid \
            --with-thin=none --with-cache=none --with-vdo=none \
            --with-writecache=none --disable-lvmimportvdo 2>&1 | tail -5
        make -j"$(nproc)" 2>&1 | tail -10
        echo "AFTER build complete"
    else
        echo "ERROR: analysis_repo not found at ${ANALYSIS_REPO}"
        exit 1
    fi
else
    echo "AFTER build already exists"
fi

# ---- Step 2: Create test config files ----
echo "--- Step 2: Creating test config files ---"

# Test 1: Valid integer (should work in both)
cat > "${CONFIG_DIR}/config_valid.conf" << 'CONFIG'
global {
    umask = 777
    activation = 1
}
CONFIG

# Test 2: Non-numeric integer (should work in BEFORE, fail in AFTER)
cat > "${CONFIG_DIR}/config_non_numeric.conf" << 'CONFIG'
global {
    umask = abc
}
CONFIG

# Test 3: Trailing characters (should work in BEFORE, fail in AFTER)
cat > "${CONFIG_DIR}/config_trailing.conf" << 'CONFIG'
global {
    umask = 777abc
}
CONFIG

# Test 4: Empty value (should fail in both or behave consistently)
cat > "${CONFIG_DIR}/config_empty.conf" << 'CONFIG'
global {
    umask = 
}
CONFIG

# Test 5: Very large integer (ERANGE)
cat > "${CONFIG_DIR}/config_erange.conf" << 'CONFIG'
global {
    umask = 999999999999999999999999999
}
CONFIG

echo "Test configs created in ${CONFIG_DIR}"

# ---- Step 3: Run tests ----
echo "--- Step 3: Running tests ---"

run_test() {
    local test_name="$1"
    local config_file="$2"
    local binary_dir="$3"
    local label="$4"
    
    local libpath="${binary_dir}/src/libdm/ioctl"
    if [ ! -d "${libpath}" ]; then
        libpath="${binary_dir}/libdm/ioctl"
    fi
    if [ ! -d "${libpath}" ]; then
        libpath=$(find "${binary_dir}" -path "*/libdm/ioctl" -type d 2>/dev/null | head -1)
    fi
    
    local binary="${binary_dir}/tools/lvm"
    if [ ! -f "${binary}" ]; then
        binary="${binary_dir}/src/tools/lvm"
    fi
    
    local config_dir_tmp=$(mktemp -d)
    cp "${config_file}" "${config_dir_tmp}/lvm.conf"
    
    set +e
    result=$(LD_LIBRARY_PATH="${libpath}" LVM_SYSTEM_DIR="${config_dir_tmp}" timeout 10 "${binary}" dumpconfig 2>&1)
    exit_code=$?
    set -e
    
    rm -rf "${config_dir_tmp}"
    
    echo "${label} | ${test_name} | exit=${exit_code} | ${result}" >> "${OUTPUT_DIR}/results.txt"
    echo "${label}: ${test_name} -> exit=${exit_code}"
    echo "${result}" | head -3
    echo "---"
}

echo "Test run: $(date)" > "${OUTPUT_DIR}/results.txt"

echo "--- BEFORE (baseline) tests ---"
for cfg in valid non_numeric trailing empty erange; do
    if [ -f "${BEFORE_DIR}/tools/lvm" ] || [ -f "${BEFORE_DIR}/src/tools/lvm" ]; then
        run_test "${cfg}" "${CONFIG_DIR}/config_${cfg}.conf" "${BEFORE_DIR}" "BEFORE"
    fi
done

echo "--- AFTER (patched) tests ---"
for cfg in valid non_numeric trailing empty erange; do
    if [ -f "${AFTER_DIR}/tools/lvm" ] || [ -f "${AFTER_DIR}/src/tools/lvm" ]; then
        run_test "${cfg}" "${CONFIG_DIR}/config_${cfg}.conf" "${AFTER_DIR}" "AFTER"
    fi
done

# ---- Step 4: Collect gcov coverage ----
echo "--- Step 4: Collecting coverage ---"
if [ -f "${AFTER_DIR}/src/libdm/.libs/libdm-config.gcda" ]; then
    echo "Collecting gcov for libdm-config.c..."
    gcov -o "${AFTER_DIR}/src/libdm/.libs" "${AFTER_DIR}/src/libdm/libdm-config.c" 2>/dev/null || \
    gcov -o "${AFTER_DIR}/src/libdm" "${AFTER_DIR}/src/libdm/libdm-config.c" 2>/dev/null || true
    cat libdm-config.c.gcov 2>/dev/null | head -50 > "${OUTPUT_DIR}/gcov_output.txt" || true
    echo "gcov output saved"
elif [ -f "${AFTER_DIR}/libdm/.libs/libdm-config.gcda" ]; then
    gcov -o "${AFTER_DIR}/libdm/.libs" "${AFTER_DIR}/libdm/libdm-config.c" 2>/dev/null || true
    cat libdm-config.c.gcov 2>/dev/null | head -50 > "${OUTPUT_DIR}/gcov_output.txt" || true
fi

echo "=== Reproducer complete ==="
echo "Results: ${OUTPUT_DIR}/results.txt"
