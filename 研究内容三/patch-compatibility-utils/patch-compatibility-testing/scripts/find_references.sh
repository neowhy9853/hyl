#!/bin/bash
# =============================================================================
# find_references.sh — Find all references to a changed symbol in the codebase
#
# Usage:
#   find_references.sh <symbol_name> <repo_path> [function|struct|macro|variable] [--deep]
# =============================================================================
set -euo pipefail

SYMBOL="${1:-}"
REPO="${2:-.}"
KIND="${3:-function}"
DEEP=false

# Parse remaining args
for arg in "$@"; do
    case "$arg" in
        --deep) DEEP=true ;;
    esac
done

if [ -z "$SYMBOL" ]; then
    echo "Usage: find_references.sh <symbol_name> <repo_path> [function|struct|macro|variable] [--deep]"
    exit 1
fi

cd "$REPO"

echo "=== Symbol: $SYMBOL ==="
echo "=== Kind: $KIND ==="
echo ""

# Source file extensions to search
EXTS="*.c *.h *.cpp *.hpp *.cc *.cxx *.py *.rs *.go"

case "$KIND" in
    function)
        echo "--- Direct function calls ---"
        grep -rn "\b${SYMBOL}\s*(" $EXTS 2>/dev/null | grep -v "^Binary" || echo "(none)"
        echo ""
        echo "--- Function pointer assignments ---"
        grep -rn "&\?${SYMBOL}\b" $EXTS 2>/dev/null | grep -v "^Binary" | grep -v "\b${SYMBOL}\s*(" || echo "(none)"
        ;;
    struct)
        echo "--- Struct declarations/usage ---"
        grep -rn "\bstruct\s\+${SYMBOL}\b" $EXTS 2>/dev/null | grep -v "^Binary" || echo "(none)"
        echo ""
        echo "--- Struct member access ---"
        grep -rn "\.${SYMBOL}\b\|\->${SYMBOL}\b" $EXTS 2>/dev/null | grep -v "^Binary" || echo "(none)"
        ;;
    macro)
        echo "--- Macro usage ---"
        grep -rn "\b${SYMBOL}\b" $EXTS 2>/dev/null | grep -v "^Binary" | grep -v "#define" || echo "(none)"
        ;;
    variable)
        echo "--- Variable references ---"
        grep -rn "\b${SYMBOL}\b" $EXTS 2>/dev/null | grep -v "^Binary" || echo "(none)"
        ;;
esac

if [ "$DEEP" = "true" ]; then
    echo ""
    echo "--- Files that include headers declaring this symbol ---"
    # Find which header declares the symbol, then find all files including it
    HEADER=$(grep -rl "\b${SYMBOL}\b" *.h 2>/dev/null | head -1)
    if [ -n "$HEADER" ]; then
        echo "Declared in: $HEADER"
        echo "Included by:"
        grep -rn "#include.*${HEADER}" $EXTS 2>/dev/null | grep -v "^Binary" || echo "(none)"
    fi
fi
