#!/bin/bash
# Phase 1.5: Before/After Behavior Comparison
# 
# Builds pre-patch and post-patch versions of the affected binary and
# compares their runtime behavior across multiple dimensions.
#
# Usage:
#   ./compare_behavior.sh <patch.diff> <build_command> <test_commands.txt>
#
# Inputs:
#   patch.diff         - the patch file to analyze
#   build_command       - how to build the project (e.g., "make -j4")
#   test_commands.txt   - file with test commands, one per line
#
# Outputs:
#   behavior_diff.json  - structured diff report
#
# Safety: this legacy helper reverses and reapplies the patch in its current
# checkout. Run it only in a disposable worktree and opt in explicitly with
# PCA_DISPOSABLE_WORKTREE=1. The merged skill normally prefers input_matrix.sh
# with separately prepared before/after directories.

set -euo pipefail

if [ "${PCA_DISPOSABLE_WORKTREE:-0}" != "1" ]; then
    echo "Refusing in-place patch reversal outside an explicitly disposable worktree." >&2
    echo "Use input_matrix.sh with --before-dir/--after-dir, or set PCA_DISPOSABLE_WORKTREE=1 in an isolated worktree." >&2
    exit 2
fi

REVERTED=0

restore_patch() {
    if [ "$REVERTED" = "1" ] && [ -n "${PATCH_FILE:-}" ]; then
        git apply "$PATCH_FILE" 2>/dev/null || true
        REVERTED=0
    fi
}

trap restore_patch EXIT

PATCH_FILE="${1:?Usage: $0 <patch.diff> <build_command> <test_commands.txt>}"
BUILD_CMD="${2:?}"
TEST_CMDS="${3:?}"
WORKDIR="${4:-./behavior_compare}"
REPORT="${WORKDIR}/behavior_diff.json"

mkdir -p "$WORKDIR"/{before,after,results}

echo "=== Phase 1.5: Before/After Behavior Comparison ==="
echo "Patch: $PATCH_FILE"
echo "Build: $BUILD_CMD"
echo "Tests: $TEST_CMDS"

# ---- Step 1: Build BEFORE version (revert patch) ----
echo ""
echo "[1/5] Building BEFORE version..."
cp "$PATCH_FILE" "$WORKDIR/patch.diff"

# Try to apply patch in reverse to get "before" state
if git apply -R "$PATCH_FILE" 2>/dev/null; then
    echo "  Reversed patch applied (git apply -R)"
    REVERTED=1
elif [ -f "Makefile" ] || [ -f "makefile" ]; then
    # If there's no git history, try building from current state as "after"
    # and use patched state logic (see step 2)
    echo "  Cannot revert (no git history), using current as 'after' only"
    REVERTED=0
else
    echo "  WARNING: Cannot determine build system, skipping build"
    REVERTED=0
fi

# Build before
if [ "$REVERTED" = "1" ]; then
    if eval "$BUILD_CMD" 2>"$WORKDIR/before_build.log"; then
        echo "  BEFORE build succeeded"
        # Save built binaries
        find . -type f -executable -name "*.o" -prune -o -type f -executable -print | \
          head -20 | while read bin; do
            cp "$bin" "$WORKDIR/before/" 2>/dev/null || true
          done
    else
        echo "  BEFORE build FAILED (see $WORKDIR/before_build.log)"
    fi
fi

# Restore patch (re-apply since we reverted)
if [ "$REVERTED" = "1" ]; then
    if git apply "$PATCH_FILE" 2>/dev/null; then
        REVERTED=0
    else
        echo "  Warning: could not re-apply patch; exit trap will retry"
    fi
fi

# ---- Step 2: Build AFTER version (patched) ----
echo "[2/5] Building AFTER version..."
# Clean first to ensure full rebuild
if [ -f "Makefile" ] && grep -q "clean" Makefile; then
    make clean 2>/dev/null || true
fi

if eval "$BUILD_CMD" 2>"$WORKDIR/after_build.log"; then
    echo "  AFTER build succeeded"
    find . -type f -executable -name "*.o" -prune -o -type f -executable -print | \
      head -20 | while read bin; do
        cp "$bin" "$WORKDIR/after/" 2>/dev/null || true
      done
else
    echo "  AFTER build FAILED (see $WORKDIR/after_build.log)"
    echo "  Cannot proceed with behavior comparison."
    echo '{"status":"build_failed","error":"after build failed"}' > "$REPORT"
    exit 1
fi

# ---- Step 3: Determine which binaries to compare ----
echo "[3/5] Identifying comparable binaries..."
> "$WORKDIR/comparison_pairs.txt"

# Match binaries that exist in both before/ and after/
for after_bin in "$WORKDIR/after/"*; do
    bin_name=$(basename "$after_bin")
    before_bin="$WORKDIR/before/$bin_name"
    if [ -f "$before_bin" ] && [ -x "$before_bin" ] && [ -x "$after_bin" ]; then
        echo "  Found comparable: $bin_name"
        echo "$bin_name|$before_bin|$after_bin" >> "$WORKDIR/comparison_pairs.txt"
    fi
done

# ---- Step 4: Execute test commands and compare outputs ----
echo "[4/5] Running behavior comparisons..."
RESULTS_FILE="$WORKDIR/results.jsonl"
> "$RESULTS_FILE"

if [ ! -s "$WORKDIR/comparison_pairs.txt" ] && [ ! -f "$TEST_CMDS" ]; then
    echo "  No binaries to compare and no test commands provided."
fi

# 4a: Run provided test commands against each binary pair
while IFS='|' read -r bin_name before_bin after_bin; do
    echo "  Testing binary: $bin_name"
    if [ -f "$TEST_CMDS" ]; then
        while IFS= read -r cmd; do
            [ -z "$cmd" ] && continue
            # Replace placeholder BINARY with actual path
            before_cmd=$(echo "$cmd" | sed "s|BINARY|$before_bin|g")
            after_cmd=$(echo "$cmd" | sed "s|BINARY|$after_bin|g")
            
            # Run before
            before_out=$(eval "$before_cmd" 2>&1 || true)
            before_rc=$?
            
            # Run after
            after_out=$(eval "$after_cmd" 2>&1 || true)
            after_rc=$?
            
            # Compare
            if [ "$before_out" != "$after_out" ] || [ "$before_rc" != "$after_rc" ]; then
                diff_output=$(diff <(echo "$before_out") <(echo "$after_out") 2>/dev/null || echo "<different>")
                echo "  ⚠  DIFF FOUND: $cmd"
                echo "    RC: $before_rc → $after_rc"
                echo "    Diff: $(echo "$diff_output" | head -5 | tr '\n' ' ')"
                
                # Classify the diff
                diff_type="OUTPUT_FORMAT_CHANGE"
                if [ "$before_rc" != "$after_rc" ]; then
                    diff_type="RETURN_CONTRACT_CHANGE"
                fi
                if echo "$after_out" | grep -qi "error\|failed\|invalid\|unknown"; then
                    if ! echo "$before_out" | grep -qi "error\|failed\|invalid\|unknown"; then
                        diff_type="INPUT_CONTRACT_CHANGE"
                    fi
                fi
                
                json_entry=$(cat <<JSON
{"binary":"$bin_name","command":"$cmd","diff_type":"$diff_type","before_rc":$before_rc,"after_rc":$after_rc,"before_out_first_line":"$(echo "$before_out" | head -1)","after_out_first_line":"$(echo "$after_out" | head -1)","diff_found":true}
JSON
)
                echo "$json_entry" >> "$RESULTS_FILE"
            else
                echo "    ✓ No difference"
            fi
        done < "$TEST_CMDS"
    fi
done < "$WORKDIR/comparison_pairs.txt"

# 4b: Empty/error input tests (if binary exists)
for after_bin in "$WORKDIR/after/"*; do
    bin_name=$(basename "$after_bin")
    before_bin="$WORKDIR/before/$bin_name"
    [ ! -f "$before_bin" ] && continue
    
    echo "  Testing edge inputs: $bin_name"
    for edge_input in "" "--help" "--version" "--nonexistent-flag"; do
        before_out=$(eval "$before_bin $edge_input" 2>&1 || true)
        after_out=$(eval "$after_bin $edge_input" 2>&1 || true)
        if [ "$before_out" != "$after_out" ]; then
            json_entry=$(cat <<JSON
{"binary":"$bin_name","command":"$bin_name $edge_input","diff_type":"EDGE_INPUT_CHANGE","diff_found":true}
JSON
)
            echo "$json_entry" >> "$RESULTS_FILE"
        fi
    done
done

# ---- Step 5: Generate structured report ----
echo "[5/5] Generating report..."
DIFF_COUNT=$(wc -l < "$RESULTS_FILE" 2>/dev/null || echo 0)
DIFF_COUNT=$((DIFF_COUNT > 0 ? DIFF_COUNT : 0))

cat > "$REPORT" <<REPORT
{
  "phase": "1.5",
  "tool": "compare_behavior.sh",
  "patch": "$PATCH_FILE",
  "build_status": "completed",
  "diff_count": $DIFF_COUNT,
  "diffs": [
$(if [ -s "$RESULTS_FILE" ]; then
  paste -sd, "$RESULTS_FILE" 2>/dev/null || echo ""
fi)
  ],
  "recommendation": $(if [ "$DIFF_COUNT" -gt 0 ]; then echo '"RUN_COMPATIBILITY_ANALYSIS"'; else echo '"NO_BEHAVIOR_DIFF_DETECTED"'; fi)
}
REPORT

echo ""
echo "=== Phase 1.5 Complete ==="
echo "Diffs found: $DIFF_COUNT"
echo "Report: $REPORT"
