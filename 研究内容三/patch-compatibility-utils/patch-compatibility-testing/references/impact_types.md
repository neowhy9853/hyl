# Compatibility Impact Type Reference

## Contents

- Classification framework and all 13 compatibility types
- Priority assignment
- Confidence scoring

## Classification Framework

Each compatibility change must be classified into exactly one type. If a change could fit multiple types, choose the one with the most specific matching criteria.

### API_SIGNATURE_CHANGE

**Check**: Did the function signature change? (parameters, return type, calling convention, const-ness, noexcept)

**Indicators**:
- Function parameter count changed
- Parameter types changed (even implicit conversions)
- Return type changed
- Function became `const`, `noexcept`, `[[nodiscard]]`
- Calling convention changed (cdecl → stdcall)
- Template constraints added/removed

**Severity**: HIGH if the function is in a public header or exported; MEDIUM if internal but widely used; LOW if static/file-local.

### ABI_CHANGE

**Check**: Did a binary-visible layout, value, symbol, version, or calling ABI change while source may still compile?

**Indicators**:
- Public struct size, alignment, field offset, bitfield, or packing changed
- Public enum or macro value changed
- Exported symbol was removed, renamed, versioned differently, or changed binding/visibility
- Vtable, object layout, calling convention, or binary serialization layout changed
- An old already-built consumer can no longer load, link, or interoperate

**Severity**: HIGH for UAPI/shared-library ABI and old binary consumers; MEDIUM for optional plugin ABI; LOW only for non-exported binary details.

### SIDE_EFFECT_CHANGE

**Check**: Did the function's observable side effects change? (locking, I/O, error paths, state mutation, logging)

**Indicators**:
- Lock acquisition added/removed/reordered
- New system calls (I/O, memory allocation, process spawn)
- Error handling path changed (new `goto err`, new return path)
- State mutation moved earlier/later in the function
- Logging added/removed/changed
- Signal handlers modified
- Atomics or memory ordering changed

**Severity**: HIGH if the side effect is user-triggerable or affects correctness (deadlocks, UAF); MEDIUM if performance-related; LOW if purely diagnostic.

### INPUT_CONTRACT_CHANGE

**Check**: Did the acceptable range/format of inputs change? (including CLI arguments, config files, API parameters)

**Indicators**:
- Previously rejected input now accepted (permissive change)
- Previously accepted input now rejected (restrictive change)
- Validation logic added/removed
- Default values changed
- Case sensitivity changed
- Encoding expectations changed

**Severity**: HIGH for CLI options and public APIs; MEDIUM for config file parsing; LOW for internal functions.

### OUTPUT_FORMAT_CHANGE

**Check**: Did the output format, encoding, or structure change?

**Indicators**:
- Printf format specifier changed (`%u` → `%llu`, `%d` → `%ld`)
- JSON/XML/YAML output structure changed
- Log message text changed
- Whitespace/formatting changed in output intended for machine parsing
- Exit code changed for same error condition

**Severity**: HIGH if output is parsed by scripts/tools; MEDIUM if human-readable only; LOW if debug-only output.

### RETURN_CONTRACT_CHANGE

**Check**: Did the semantics of return values change?

**Indicators**:
- Previously impossible return value now possible (e.g., `NULL` from function that never returned `NULL`)
- Error code meaning changed
- Success/failure boundary shifted
- Returned pointer lifetime changed
- Returned value ownership changed

**Severity**: HIGH if callers depend on specific return semantics; MEDIUM if defensive coding covers the change; LOW if trivially handled.

### RESOURCE_LIFETIME_CHANGE

**Check**: Did resource allocation, deallocation, or lifecycle change?

**Indicators**:
- Memory allocation moved (stack → heap, heap → stack)
- Reference counting added/removed
- Resource cleanup timing changed
- File descriptor lifecycle changed

**Severity**: HIGH if it affects memory safety or hangs; MEDIUM if performance/resource usage; LOW if debug resources.

### PERFORMANCE_RESOURCE_SEMANTIC_CHANGE

**Check**: Did externally relevant timeout, retry, limit, ordering, batching, scheduling, or resource-consumption semantics change?

**Indicators**:
- Timeout or blocking duration changed
- Retry count, backoff, or retryable-error set changed
- Queue/batch/connection/cache limit changed
- Ordering, fairness, scheduling, or wake-up behavior changed
- Memory, CPU, I/O, or network consumption changes a documented or relied-on bound

**Severity**: HIGH when it can cause timeouts, starvation, overload, or protocol failure; MEDIUM for documented operational changes; LOW for unobservable micro-optimizations.

### ERROR_EXCEPTION_CHANGE

**Check**: Did error handling behavior change? (new errors, different errors for same input, exception type change)

**Indicators**:
- New error message for existing condition
- Different errno set for same failure
- New exception type thrown
- Error path now recovers instead of aborting
- Error path now aborts instead of recovering

**Severity**: HIGH if callers catch specific error types/codes; MEDIUM if error handling is generic; LOW if error is unrecoverable either way.

### PROC_SYS_OUTPUT_CHANGE

**Check**: Did `/proc`, `/sys`, or similar kernel ABI outputs change?

**Indicators**:
- Format of `/proc/<pid>/...` or `/sys/...` file changed
- Newline handling changed
- Field ordering changed in multi-field output
- Truncation behavior changed

**Severity**: HIGH if tools parse these files; MEDIUM if only human-consumed; LOW if rarely accessed.

### SYSCALL_SEMANTIC_CHANGE

**Check**: Did a system call number, argument, flag, errno, compat translation, blocking, signal, restart, or timeout rule change?

**Indicators**:
- Syscall number/table or availability changed
- Accepted flags, flag combinations, argument sizes, or validation changed
- Return value, errno, output buffer, partial-progress, or restart behavior changed
- 32-bit compat behavior differs from native behavior
- Blocking, wake-up, cancellation, signal interruption, or timeout semantics changed

**Severity**: HIGH for UAPI-visible semantics or common callers; MEDIUM for privileged/rare paths; LOW only for unreachable internal plumbing.

### IOCTL_NETLINK_ABI_CHANGE

**Check**: Did an ioctl command/UAPI struct or netlink family, operation, attribute, policy, encoding, reply, or error contract change?

**Indicators**:
- `_IO*` command number/direction/size changed
- UAPI struct size, alignment, reserved field, versioning, or compat translation changed
- Netlink family name/version, command, multicast group, or attribute ID changed
- `nla_policy`, required/optional attributes, nesting, byte order, or validation changed
- Kernel reply attributes, ACK/extack, errno, or dump behavior changed

**Severity**: HIGH for userspace-kernel ABI; MEDIUM for opt-in family extensions; LOW only for undocumented and unreachable internals.

### CONFIG_CLI_BEHAVIOR_CHANGE

**Check**: Did CLI option parsing or config file behavior change?

**Indicators**:
- Option renamed with alias retained
- New option added that changes default behavior
- Option removed
- Config key changed
- Config value format changed

**Severity**: HIGH if widely-used option; MEDIUM if obscure option; LOW if option was broken before.

## Priority Assignment

| Factor | Weight |
|---|---|
| User-triggerable (any user can hit this path) | +2 levels |
| Affects public API / ABI | +2 levels |
| Affects protocol semantics (DNS, HTTP, DHCP) | +2 levels |
| Can cause crash, deadlock, or UAF | +2 levels (always HIGH) |
| Affects shared library exported symbol | +1 level |
| Affects CLI option parsing | +1 level |
| Affects config file parsing | +1 level |
| Affects error message text only | -1 level |
| Static/file-local function | -1 level |
| Debug/tracing code only | -2 levels |
| Documentation change only | -2 levels |

## Confidence Scoring

- **0.9-1.0**: Code evidence is direct and unambiguous, behavior change is certain
- **0.7-0.9**: Strong evidence but some runtime conditions could alter behavior
- **0.5-0.7**: Plausible impact but needs runtime verification
- **Below 0.5**: Do NOT include as a finding — too speculative
