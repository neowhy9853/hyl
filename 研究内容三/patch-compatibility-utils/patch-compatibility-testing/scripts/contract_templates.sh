#!/bin/bash
# Legacy low-level contract primitives for Compatibility Verification (Phase 3.5)
#
# The authoritative 13-type registry and runner are compatibility_types.py and
# run_contracts.py. These functions remain for callers that source the old
# library directly. Returns 0 if a primitive holds, 1+ if breached.
#
# Source this file: source contract_templates.sh
# Then call individual contract functions.

set -euo pipefail

# ---- Utility ----
write_result() {
    local results_dir="$1" contract_id="$2" status="$3" detail="$4"
    mkdir -p "$results_dir"
    python3 - "$contract_id" "$status" "$detail" >> "$results_dir/contracts.jsonl" <<'PY'
import datetime
import json
import sys

print(json.dumps({
    "contract_id": sys.argv[1],
    "status": sys.argv[2],
    "detail": sys.argv[3],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}, ensure_ascii=False))
PY
    if [ "$status" = "PASS" ]; then
        echo "  ✓ $contract_id"
    else
        echo "  ✗ $contract_id: $detail"
    fi
}

# ---- Contract: OUTPUT_FORMAT_CHANGE ----
# Assert that before and after binaries produce identical output for the same args
assert_output_stable() {
    local before_bin="$1"
    local after_bin="$2"
    local args="$3"
    local results_dir="$4"
    local contract_id="CT-OUTPUT-$(basename "$before_bin")-$(echo "$args" | md5sum | cut -c1-8)"
    
    local before_out before_rc after_out after_rc
    set +e
    before_out=$("$before_bin" $args </dev/null 2>&1)
    before_rc=$?
    after_out=$("$after_bin" $args </dev/null 2>&1)
    after_rc=$?
    set -e
    
    if [ "$before_out" = "$after_out" ] && [ "$before_rc" = "$after_rc" ]; then
        write_result "$results_dir" "$contract_id" "PASS" "Output and exit code identical"
        return 0
    else
        local diff_text
        diff_text=$(diff <(echo "$before_out") <(echo "$after_out") 2>/dev/null || true)
        write_result "$results_dir" "$contract_id" "BREACH" "Output changed. RC: $before_rc→$after_rc. Diff: $diff_text"
        return 1
    fi
}

# ---- Contract: INPUT_CONTRACT_CHANGE ----
# Assert that previously accepted inputs are still accepted
assert_input_backward_compat() {
    local before_bin="$1"
    local after_bin="$2"
    local args="$3"
    local results_dir="$4"
    local contract_id="CT-INPUT-$(basename "$before_bin")-$(echo "$args" | md5sum | cut -c1-8)"
    
    # First verify before accepts it
    local before_rc=0
    "$before_bin" $args </dev/null >/dev/null 2>&1 || before_rc=$?
    
    if [ "$before_rc" -ne 0 ]; then
        write_result "$results_dir" "$contract_id" "SKIP" "Before also rejects this input (rc=$before_rc), no regression"
        return 0
    fi
    
    # Now check after
    local after_rc=0
    "$after_bin" $args </dev/null >/dev/null 2>&1 || after_rc=$?
    
    if [ "$after_rc" -eq 0 ]; then
        write_result "$results_dir" "$contract_id" "PASS" "Input accepted by both versions"
        return 0
    else
        write_result "$results_dir" "$contract_id" "BREACH" "Previously accepted input now rejected. RC: 0→$after_rc"
        return 1
    fi
}

# ---- Contract: RETURN_CONTRACT_CHANGE ----
# Assert return values are stable for the same inputs
assert_return_code_stable() {
    local before_bin="$1"
    local after_bin="$2"
    local args="$3"
    local results_dir="$4"
    local contract_id="CT-RETURN-$(basename "$before_bin")-$(echo "$args" | md5sum | cut -c1-8)"
    
    local before_rc after_rc
    "$before_bin" $args </dev/null >/dev/null 2>&1 && before_rc=$? || before_rc=$?
    "$after_bin" $args </dev/null >/dev/null 2>&1 && after_rc=$? || after_rc=$?
    
    if [ "$before_rc" = "$after_rc" ]; then
        write_result "$results_dir" "$contract_id" "PASS" "Exit code stable: $before_rc"
        return 0
    else
        write_result "$results_dir" "$contract_id" "BREACH" "Exit code changed: $before_rc→$after_rc"
        return 1
    fi
}

# ---- Contract: SIDE_EFFECT_CHANGE ----
# Compare strace output to detect new system calls
assert_strace_no_new_syscalls() {
    local before_bin="$1"
    local after_bin="$2"
    local args="$3"
    local results_dir="$4"
    local contract_id="CT-SYSCALL-$(basename "$before_bin")-$(echo "$args" | md5sum | cut -c1-8)"
    
    # Only run if strace is available
    if ! command -v strace &>/dev/null; then
        write_result "$results_dir" "$contract_id" "SKIP" "strace not available"
        return 0
    fi
    
    local trace_before="$results_dir/${contract_id}_before.strace"
    local trace_after="$results_dir/${contract_id}_after.strace"
    
    strace -q -o "$trace_before" "$before_bin" $args 2>/dev/null || true
    strace -q -o "$trace_after"  "$after_bin"  $args 2>/dev/null || true
    
    # Extract unique syscall names
    local before_syscalls after_syscalls new_syscalls
    before_syscalls=$(awk '{print $1}' "$trace_before" | sed 's/(.*//' | sort -u)
    after_syscalls=$(awk '{print $1}' "$trace_after" | sed 's/(.*//' | sort -u)
    new_syscalls=$(comm -13 <(echo "$before_syscalls") <(echo "$after_syscalls"))
    
    if [ -z "$new_syscalls" ]; then
        write_result "$results_dir" "$contract_id" "PASS" "No new system calls"
        return 0
    else
        write_result "$results_dir" "$contract_id" "BREACH" "New syscalls: $(echo "$new_syscalls" | tr '\n' ' ')"
        return 1
    fi
}

# ---- Contract: API_SIGNATURE_CHANGE / HEADER_CHANGE ----
# Compile a test file to verify header backward compatibility
assert_compile_test() {
    local test_file="$1"
    local compiler="$2"
    local flags="$3"
    local results_dir="$4"
    local contract_id="CT-COMPILE-$(basename "$test_file" .cpp)"
    
    if $compiler $flags -c "$test_file" -o /dev/null 2>/dev/null; then
        write_result "$results_dir" "$contract_id" "PASS" "Compilation succeeds"
        return 0
    else
        local err_msg
        err_msg=$($compiler $flags -c "$test_file" -o /dev/null 2>&1 | head -5 | tr '\n' ' ')
        write_result "$results_dir" "$contract_id" "BREACH" "Compilation failed: $err_msg"
        return 1
    fi
}

# ---- Contract: ERROR_EXCEPTION_CHANGE ----
# Assert that error messages are stable for error inputs
assert_error_message_stable() {
    local before_bin="$1"
    local after_bin="$2"
    local error_args="$3"
    local results_dir="$4"
    local contract_id="CT-ERROR-$(basename "$before_bin")-$(echo "$error_args" | md5sum | cut -c1-8)"
    
    local before_err after_err
    before_err=$("$before_bin" $error_args </dev/null 2>&1 || true)
    after_err=$("$after_bin" $error_args </dev/null 2>&1 || true)
    
    # Extract just the error message (first line)
    local before_msg after_msg
    before_msg=$(echo "$before_err" | head -1)
    after_msg=$(echo "$after_err" | head -1)
    
    if [ "$before_msg" = "$after_msg" ]; then
        write_result "$results_dir" "$contract_id" "PASS" "Error message stable"
        return 0
    else
        write_result "$results_dir" "$contract_id" "BREACH" "Error message changed: \"$before_msg\" → \"$after_msg\""
        return 1
    fi
}

# ---- Contract Summary ----
contract_summary() {
    local results_dir="$1"
    local results_file="$results_dir/contracts.jsonl"
    
    if [ ! -f "$results_file" ]; then
        echo "No contract results found in $results_dir"
        return 1
    fi
    
    local total passed breached skipped
    total=$(wc -l < "$results_file")
    passed=$(grep -c '"PASS"' "$results_file" 2>/dev/null || true)
    breached=$(grep -c '"BREACH"' "$results_file" 2>/dev/null || true)
    skipped=$(grep -c '"SKIP"' "$results_file" 2>/dev/null || true)
    
    cat <<SUMMARY
=== Contract Verification Summary ===
Total:  $total
Passed: $passed
Breached: $breached
Skipped: $skipped
Status: $(if [ "$breached" -gt 0 ]; then echo "CONTRACT_BREACH_DETECTED"; else echo "ALL_CONTRACTS_PASS"; fi)
=====================================
SUMMARY
    
    # Write machine-readable summary
    cat > "$results_dir/contract_summary.json" <<JSON
{
  "total": $total,
  "passed": $passed,
  "breached": $breached,
  "skipped": $skipped,
  "status": "$(if [ "$breached" -gt 0 ]; then echo "CONTRACT_BREACH_DETECTED"; else echo "ALL_CONTRACTS_PASS"; fi)"
}
JSON
}

# If executed directly (not sourced), show usage
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    echo "Legacy Contract Primitive Library"
    echo "Use run_contracts.sh for type-aware execution of all 13 compatibility types."
    echo "Source this file in your scripts: source contract_templates.sh"
    echo ""
    echo "Available contracts:"
    echo "  assert_output_stable <before> <after> <args> <results_dir>"
    echo "  assert_input_backward_compat <before> <after> <args> <results_dir>"
    echo "  assert_return_code_stable <before> <after> <args> <results_dir>"
    echo "  assert_strace_no_new_syscalls <before> <after> <args> <results_dir>"
    echo "  assert_compile_test <file> <compiler> <flags> <results_dir>"
    echo "  assert_error_message_stable <before> <after> <args> <results_dir>"
    echo "  contract_summary <results_dir>"
fi
