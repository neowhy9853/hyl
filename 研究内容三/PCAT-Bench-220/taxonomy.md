# Compatibility taxonomy

Positive findings use exactly these primary/secondary labels:

| # | Enum |
|---:|---|
| 1 | `API_SIGNATURE_CHANGE` |
| 2 | `ABI_CHANGE` |
| 3 | `INPUT_CONTRACT_CHANGE` |
| 4 | `RETURN_CONTRACT_CHANGE` |
| 5 | `ERROR_EXCEPTION_CHANGE` |
| 6 | `SIDE_EFFECT_CHANGE` |
| 7 | `OUTPUT_FORMAT_CHANGE` |
| 8 | `PROC_SYS_OUTPUT_CHANGE` |
| 9 | `SYSCALL_SEMANTIC_CHANGE` |
| 10 | `IOCTL_NETLINK_ABI_CHANGE` |
| 11 | `CONFIG_CLI_BEHAVIOR_CHANGE` |
| 12 | `RESOURCE_LIFETIME_CHANGE` |
| 13 | `PERFORMANCE_RESOURCE_SEMANTIC_CHANGE` |

Negative items use: `INTERNAL_ONLY`, `BEHAVIOR_PRESERVING_REFACTOR`, `TEST_DOC_COMMENT_ONLY`, `BUGFIX_WITHIN_CONTRACT`, `UNREACHABLE_OR_DISABLED`, `ADDITIVE_NO_OLD_CLIENT_EFFECT`, `PROFILE_BOUNDARY_FALSE_POSITIVE`.

Imported raw values `TEST_ONLY` and `DOCUMENTATION_ONLY` are retained in `legacy_negative_category` but normalize to `TEST_DOC_COMMENT_ONLY`. “F” in N/F statistics means the strict `PROFILE_BOUNDARY_FALSE_POSITIVE` subset of Negative cases.

`change_kind` mirrors the primary Positive type or Negative kind for legacy scorer compatibility. A Positive is compatibility-relevant even when additive or corrective; a Negative requires a concrete non-observability, equivalence, profile-boundary, or reachability proof.
