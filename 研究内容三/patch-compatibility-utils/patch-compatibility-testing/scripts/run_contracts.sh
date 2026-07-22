#!/bin/bash
# Backward-compatible launcher for the type-aware Python contract runner.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/run_contracts.py" "$@"
