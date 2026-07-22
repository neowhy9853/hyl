# Test Input Generation Strategies by Compatibility Type

## Contents

- General constraint-intention framework
- Input strategies for all 13 compatibility types
- Protocol-specific strategies
- Fault injection
- Input diversity checklist

## General Framework

The core algorithm for generating test inputs that maximize patch coverage:

```
1. For each finding → trace call chain → read ALL source along chain
2. For each function in chain → extract constraints (branch conditions, validation, error checks)
3. For each constraint → classify as path-critical or path-irrelevant
4. For each changed code line → identify which constraint combination reaches it
5. Generate inputs satisfying each combination → one input per distinct path
```

## Constraint-Intention Analysis

Adapted from `constraint-intention-analysis-skill`. For each function in the call chain:

### Extract Constraints

Read the source and identify:
1. **Input validation**: `if (x == NULL) return error`, `if (len > MAX) die(...)`
2. **Branch conditions**: `if (transport->smart_options)`, `if (msg_type == DHCP6REQUEST)`
3. **Protocol/version selection**: `if (protocol.version >= 2)`
4. **Error handling**: `if (result < 0) goto err`, `case ERROR_CODE:`
5. **Configuration guards**: `if (option_bool(OPT_DNSSEC))`, `#ifdef HAVE_DNSSEC`
6. **Resource state**: `if (daemon->pipe_to_parent != -1)`, `if (state->is_unicast)`

### Classify Constraints

For each constraint, determine:

| Classification | Meaning | Test Strategy |
|---|---|---|
| **path-critical** | Must be satisfied to reach target | Generate input that satisfies it |
| **path-blocking** | Must NOT be satisfied to reach target | Generate input that fails/violates it |
| **path-irrelevant** | Does not affect reaching target | Ignore for this target |
| **path-optional** | May or may not be satisfied | Test both cases |

### Summarize in Natural Language

For each function, write a concise summary:

```markdown
## Function: explore_rrset (src/dnssec.c:370-414)
### Intention: Validate RRSIG records in a DNS reply, extracting signer name for type-matching RRSIGs only
### Constraints:
  - path-critical: GETSHORT(type_covered, p) must succeed (valid DNS wire format)
  - path-critical: type_covered == type (only process RRSIGs matching target type)
  - path-blocking: extract_name() failure returns early (malformed DNS)
  - path-optional: hostname_issubdomain() result determines sig accumulation
### Test Input Implications:
  - To reach L411 (sig accumulation): provide DNS response with type_covered matching target type
  - To reach L386 (skip spurious): provide DNS response with type_covered != target type
```

## Strategy by Compatibility Type

Use `compatibility_type_test_matrix.md` for the required oracle and probe
protocol. The rules below focus on input selection.

### API_SIGNATURE_CHANGE

1. Compile an unchanged old downstream call site against each version
2. Cover every changed parameter/default/qualifier and language mode
3. Link/load the consumer when the API is exported
4. Include source-only and binary-consumer checks; one does not replace the other

### ABI_CHANGE

1. Exercise every changed symbol/version and old binary consumer
2. Probe `sizeof`, alignment, offsets, enum/macro values, packing, and calling ABI
3. Cover static/shared builds and enabled feature configurations
4. Use an ABI checker plus focused harness when public type layout is involved

### SIDE_EFFECT_CHANGE

**The most complex type** — requires the most diverse inputs.

1. **Locking changes**: If the patch adds/removes/reorders locks, test concurrent execution
   - Input: concurrent process spawning (`&` forking, `xargs -P`)
   - Input: signal delivery during locked section

2. **I/O changes**: If the patch changes I/O behavior
   - Input: normal I/O (file exists, readable)
   - Input: error I/O (file missing, permission denied)
   - Input: slow I/O (large file, network delay)

3. **Error path changes**: If the patch adds new error handling
   - Input: triggers the error condition
   - Input: triggers the condition just before the error boundary
   - For unreachable error paths: use fault injection (see below)

4. **Logging changes**: If the patch adds log messages
   - Input: triggers the condition that produces the log
   - Input: triggers a "near miss" that should NOT produce the log

### INPUT_CONTRACT_CHANGE

1. **Boundary values**: Test at exact boundary of old and new acceptable ranges
2. **Cross-boundary values**: Test values that were valid/invalid under old contract but inverse under new
3. **Edge cases**: null, empty, zero-length, maximum-length
4. **Old behavior regression**: Input that worked under old contract should still work (or fail cleanly)

### OUTPUT_FORMAT_CHANGE

1. **Same-output values**: Values producing identical output in old and new formats
2. **Different-output values**: Values crossing the format boundary (e.g., UINT_MAX for %u→%llu)
3. **Extreme values**: 0, maximum, overflow
4. **Each output width**: If the patch dispatches by field size, test each size

### RETURN_CONTRACT_CHANGE

1. **Old return paths**: Inputs that produce the same return value as before (regression)
2. **New return paths**: Inputs that produce each new possible return value
3. **Previously impossible**: Inputs that produce returns that were impossible before
4. **NULL/error propagation**: If return semantics changed for error cases

### ERROR_EXCEPTION_CHANGE

1. Trigger every affected error branch, not only a generic invalid flag
2. Capture errno/error code, exception type/hierarchy, message, and recovery/abort
3. Cover wrapped/nested errors and fault-injection-only paths where necessary
4. Exercise locale or verbosity modes when they affect diagnostics

### PROC_SYS_OUTPUT_CHANGE

1. Read/write the affected node at boundary values and with invalid values
2. Test permissions, namespaces, seek/poll behavior, and partial reads
3. Verify node name/type/mode and parser-visible field order/newlines
4. Repeat on native baseline/patched kernels with matched configuration

### SYSCALL_SEMANTIC_CHANGE

1. Invoke the syscall directly for every affected flag and argument boundary
2. Capture return, errno, output buffers, partial progress, and restart behavior
3. Exercise blocking/nonblocking, signals, cancellation, and timeout edges
4. Compare native and compat execution when compat translation is in scope

### IOCTL_NETLINK_ABI_CHANGE

1. Exercise each affected ioctl command or netlink operation
2. Cover UAPI struct sizes/versions/reserved fields and native/compat layouts
3. Send known, unknown, missing, duplicate, and nested netlink attributes
4. Capture reply attributes, ACK/extack, dump completion, policy rejection, and errno

### CONFIG_CLI_BEHAVIOR_CHANGE

1. **New option name** with valid argument
2. **Old alias name** with valid argument (backward compat)
3. **Both names mixed**
4. **Invalid arguments** to both names
5. **Combination** with interacting options

### RESOURCE_LIFETIME_CHANGE

1. Normal completion, every error cleanup, cancellation, and teardown
2. Repeated execution to expose leaks, stale state, or refcount imbalance
3. Concurrent execution for locks, ownership transfer, and race-sensitive cleanup
4. Sanitizer/Valgrind/lockdep plus explicit fd/handle/state counts

### PERFORMANCE_RESOURCE_SEMANTIC_CHANGE

1. Idle, nominal, boundary, overload, and contention workloads
2. Exact timeout and retry boundaries, including interrupted waits
3. Documented limits, ordering, fairness, batching, and backoff sequences
4. Repeated pinned measurements emitted as numeric JSON with justified tolerance

## Protocol-Specific Strategies

### Multi-Protocol Code (v0/v1/v2 in git fetch-pack)

```
# Force protocol v0
git -c protocol.version=0 fetch ...

# Force protocol v1
git -c protocol.version=1 fetch ...

# Force protocol v2 (default)
git -c protocol.version=2 fetch ...
```

Each version may have a completely separate code path for the same logical operation.

### Smart vs Non-Smart Transport

```
# Smart transport (file://)
git fetch file:///path/to/repo ...

# Non-smart transport (bundle)
git bundle create test.bundle HEAD
git fetch test.bundle HEAD

# Remote helper transport
GIT_TRANSPORT_HELPER_DEBUG=1 git fetch "helper-name::args" ...
```

### DHCPv6 Protocol Testing

```
# Unicast vs multicast
sudo python3 send_unicast_dhcpv6.py --server fd00:test::1 --type request

# Raw socket for precise control
sudo python3 test_dhcp6_unicast.py --dnsmasq-bin ./src/dnsmasq --iface lo
```

## Fault Injection Strategy

Adapted from `cpp-fault-inject-skill`. Use when normal input variation cannot reach an error-handling path.

### When to Use

- Error-handling code guarded by conditions that are impossible/hard to trigger with normal inputs
- Timeout paths (SIGALRM with 150s CHILD_LIFETIME)
- Resource exhaustion paths (memory allocation failure, fd exhaustion)
- Rare hardware error paths

### How to Apply

1. Back up the original source: `cp file.c file.c.bak`
2. At the target line, insert fault injection:
   ```c
   /* FAULT INJECT: force error path */
   if (getenv("PCA_FAULT_INJECT")) {
       result = ERROR_CODE;
       goto error_cleanup;
   }
   ```
3. Rebuild with coverage flags
4. Run test with `PCA_FAULT_INJECT=1`
5. After testing, restore original source

### Alternative: Signal Injection

For timeout paths, inject signals instead of waiting:

```bash
# Start dnsmasq, get PID, send SIGALRM
dnsmasq --no-daemon ... &
DNSMASQ_PID=$!
sleep 1
kill -ALRM $DNSMASQ_PID
# Check log for timeout message
```

## Input Diversity Checklist

Before executing Phase 4, verify:

- [ ] Each compatibility finding has ≥1 input
- [ ] Each if/else branch has ≥1 input per direction
- [ ] Each protocol version has ≥1 input (if multi-protocol code)
- [ ] Each transport type has ≥1 input (if transport-dependent code)
- [ ] Both valid and invalid input values are tested
- [ ] Boundary values tested (0, MAX, overflow)
- [ ] Error/fault injection applied if error paths unreachable
- [ ] Concurrent/multi-process tested if locking changed
- [ ] Different build configs tested if #ifdef guards present
- [ ] Daemon start/stop lifecycle handled (if testing daemons)
