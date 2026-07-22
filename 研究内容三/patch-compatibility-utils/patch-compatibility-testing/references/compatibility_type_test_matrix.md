# Compatibility Type Test Matrix

Use this matrix after validating `analysis.json` and before generating entries.
The canonical executable registry is `scripts/compatibility_types.py`. Every
finding must have at least one type-specific input axis and one contract result.
If the required environment or probe cannot be built, record a concrete
`skipped` contract plus `blocked_or_not_run`; never relabel it as another type.

## Probe protocol

Add `contract_probe` to the finding's entry. A probe may provide one `command`
that uses `BINARY` or `{VERSION_DIR}`, or separate `before_command` and
`after_command`. The runner also expands `{BEFORE_DIR}`, `{AFTER_DIR}`,
`{BEFORE_BIN}`, and `{AFTER_BIN}`. Commands must emit a canonical observation:
stable ordering, normalized volatile IDs/timestamps, and no unrelated logs.

Comparisons:

- `success`: the baseline probe must succeed and the patched probe must remain
  successful. Use for downstream compile/link or ABI-check commands.
- `acceptance`: compare whether return code zero means accepted. Both tightening
  and loosening are reported as breaches.
- `exit_code`: compare return/exit status exactly. Put non-status return values
  in canonical stdout and use `exact` when they also matter.
- `error`: compare return status, stderr, and stdout to preserve errno,
  exception type, error code, and message emitted by the harness.
- `exact`: compare status, stdout, and stderr byte-for-byte after probe-side
  normalization.
- `set_no_additions`: require the patched stdout line set to add no manifest
  entries and preserve the status. Use only for explicitly additive-forbidden
  side-effect manifests.
- `numeric_tolerance`: require both commands to print the same non-empty JSON
  object of numeric values. Fail when any relative change exceeds
  `tolerance_percent` (20% default for performance/resource semantics).

## Type matrix

| Compatibility type | Required probe and observation | Minimum axes | Default comparison |
|---|---|---|---|
| `API_SIGNATURE_CHANGE` | Compile the same downstream source using the old declaration against each version; include link/load when the API is exported. Observe diagnostics and success. | Old call shape, each language/compiler mode, default arguments/qualifiers, static/shared link | `success` |
| `ABI_CHANGE` | Run `abidiff`/ABI checker where available and an old-binary consumer or layout harness for affected `sizeof`, alignment, offsets, enum values, symbols, and versions. A symbol-only check is insufficient for type-layout claims. | Exported symbols, versions, layouts/values, old binary load/call | `success` |
| `INPUT_CONTRACT_CHANGE` | Exercise values on both sides of every changed validation boundary. Observe acceptance plus precise error when rejected. | Old-valid, old-invalid, exact boundary, null/empty, maximum/overflow | `acceptance` |
| `RETURN_CONTRACT_CHANGE` | Call the same path and emit canonical return value, exit status, out-parameters, sentinel values, and ownership where relevant. | Success, each failure, boundary, null/partial result | `exit_code` or `exact` |
| `ERROR_EXCEPTION_CHANGE` | Trigger each affected failure and emit errno/error code, exception class/hierarchy, message, and abort/recovery mode. | Invalid input, missing resource, permission, fault injection, nested/wrapped error | `error` |
| `SIDE_EFFECT_CHANGE` | Snapshot externally observable state before/after the operation: files, DB/state, syscalls, processes, network, logs, permissions, ordering, and concurrency. Normalize unrelated nondeterminism. | Normal/error paths, state snapshot, concurrent invocation, signal/cancellation | `exact` or `set_no_additions` |
| `OUTPUT_FORMAT_CHANGE` | Capture byte output and, for structured formats, parse and canonicalize the schema, field types/order rules, escaping, encoding, and newline behavior. | Human/machine format, TTY/pipe, locale, empty/extreme values | `exact` |
| `PROC_SYS_OUTPUT_CHANGE` | In matched before/after kernels, verify node presence/type/mode, read/write/seek/poll behavior, errno, namespace visibility, and canonical text/schema. | Read, write, boundary, permissions, poll/seek, namespace | `exact` |
| `SYSCALL_SEMANTIC_CHANGE` | Use a direct C/kselftest/syzkaller-derived reproducer that prints return, errno, output buffers, elapsed/blocking state, signals/restart, and native/compat result. | Flags, boundary arguments, invalid pointers, native/compat, signal, timeout | `exact` |
| `IOCTL_NETLINK_ABI_CHANGE` | Compile against the relevant UAPI and emit ioctl numbers/layout/compat results or netlink family/version/operation/attribute/policy/reply/extack results. | Each command/op, struct sizes, known/unknown/nested attrs, native/compat | `exact` |
| `CONFIG_CLI_BEHAVIOR_CHANGE` | Run a temporary isolated config/CLI/env matrix and emit acceptance, parsed/effective value, defaults, precedence, status, output, and resulting state. | Default, explicit value, legacy alias, invalid value, CLI/config/env precedence | `exact` |
| `RESOURCE_LIFETIME_CHANGE` | Emit canonical allocation/free, fd, lock, refcount, ownership, cleanup, and sanitizer/Valgrind/lockdep observations. Avoid using syscall-name equality alone as proof. | Normal/error cleanup, repetition, concurrency, cancellation, teardown | `exact` |
| `PERFORMANCE_RESOURCE_SEMANTIC_CHANGE` | Measure documented semantic quantities—not microbenchmark noise—and print numeric JSON for timeout, retries, limits, ordering/batching, and bounded resource use. Pin workload/environment and repeat enough to stabilize. | Idle, nominal load, boundary limit, timeout/retry, contention | `numeric_tolerance` |

## Evidence rules

- A `PASS` proves only the observations emitted by that probe. Record omitted ABI
  layout, compat, privilege, hardware, timing, or namespace dimensions as
  blockers/limitations.
- Run the exact same logical workload against baseline and patched versions.
- Do not treat missing tools, missing binaries, failed baseline harnesses, or
  unbuilt artifacts as evidence of compatibility or incompatibility.
- Keep intended behavior differences as `BREACH` observations and explain the
  compatibility consequence; intent does not make an observable contract stable.
- Correlate every runtime observation with reachability or patch-line coverage.
