#!/bin/bash
# PCA-0001 Reproducer: Verify ReadHeaderTimeout applies to unencrypted HTTP/2 preface detection
#
# This script builds and runs the native Go test TestServerUnencryptedHTTP2HeaderTimeout
# that was added by commit 5bbd22ff78daf010c5bd19c466a0c45ac78503d4.
#
# PREREQUISITES:
#   - GOROOT_BOOTSTRAP pointing to Go 1.24.6+ (required to build Go 1.26+ from source)
#   - PATH includes the Go binary from the built GOROOT
#
# BUILD (run once before testing):
#   cd /path/to/patched/worktree/src
#   GOROOT_BOOTSTRAP=/path/to/go1.24 ./make.bash
#
# When built Go is ready at PATCHED_GOROOT, this script runs the test.

set -euo pipefail

PATCHED_GOROOT="${PATCHED_GOROOT:-/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/_worktrees/patched}"
RESULT_DIR="${RESULT_DIR:-/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/compatibility-testing/test-entry-work/PCA-0001}"

echo "=== PCA-0001: ReadHeaderTimeout applied to unencrypted HTTP/2 preface detection ==="
echo ""

# Check if patched Go is built
if [ ! -x "${PATCHED_GOROOT}/bin/go" ]; then
    echo "ERROR: Patched Go not built at ${PATCHED_GOROOT}/bin/go"
    echo "Build it first:"
    echo "  cd ${PATCHED_GOROOT}/src"
    echo "  GOROOT_BOOTSTRAP=/path/to/go1.24.6 ./make.bash"
    exit 1
fi

# Run the native regression test
echo "Running TestServerUnencryptedHTTP2HeaderTimeout..."
GOROOT="${PATCHED_GOROOT}" \
"${PATCHED_GOROOT}/bin/go" test -v -run 'TestServerUnencryptedHTTP2HeaderTimeout' -count=1 -timeout=120s net/http 2>&1 | tee "${RESULT_DIR}/test_output.log"

exit_code=$?
echo ""
echo "Exit code: ${exit_code}"
if [ ${exit_code} -eq 0 ]; then
    echo "PASS: TestServerUnencryptedHTTP2HeaderTimeout passed"
    echo "This confirms the ReadHeaderTimeout is applied to unencrypted HTTP/2 preface detection."
else
    echo "FAIL: Test did not pass"
fi

exit ${exit_code}
