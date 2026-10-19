#!/bin/bash
set -euo pipefail

GO_BINARY="$1"   # path to go binary
ENTRY_DIR="$(dirname "$0")"

echo "=== PCA-TE-0001 Test: AddTrustedOrigin userinfo validation ==="
echo "Using Go: $($GO_BINARY version)"
echo ""

$GO_BINARY run "${ENTRY_DIR}/main.go"
