#!/usr/bin/env python3
"""Canonical compatibility-type registry for the testing skill.

Keep executable routing data here. Human-facing details live in
references/compatibility_type_test_matrix.md, while every testing script imports
this module so the supported type set cannot silently diverge.
"""

from __future__ import annotations

from typing import Any


TYPE_SUPPORT: dict[str, dict[str, Any]] = {
    "API_SIGNATURE_CHANGE": {
        "contract_id": "api_signature_compatibility",
        "comparison": "success",
        "entry_kind": "downstream_compile_link_harness",
        "observation": "old downstream source compiles and links against both versions",
        "input_axes": ["old declarations", "language modes", "compiler flags", "link modes"],
        "requires_explicit_probe": True,
    },
    "ABI_CHANGE": {
        "contract_id": "binary_abi_compatibility",
        "comparison": "success",
        "entry_kind": "abi_dump_and_consumer_harness",
        "observation": "symbol/version manifest plus size, alignment, offset, enum, and calling ABI",
        "input_axes": ["exported symbols", "symbol versions", "type layouts", "old binary consumer"],
        "requires_explicit_probe": True,
    },
    "INPUT_CONTRACT_CHANGE": {
        "contract_id": "backward_input_acceptance",
        "comparison": "acceptance",
        "entry_kind": "input_boundary_harness",
        "observation": "accept/reject result at old and new validation boundaries",
        "input_axes": ["old-valid", "old-invalid", "exact boundary", "null/empty", "maximum"],
        "requires_explicit_probe": False,
    },
    "RETURN_CONTRACT_CHANGE": {
        "contract_id": "return_contract_stability",
        "comparison": "exit_code",
        "entry_kind": "return_value_harness",
        "observation": "return value, exit status, output value, and ownership convention",
        "input_axes": ["success", "failure", "boundary", "null result", "partial result"],
        "requires_explicit_probe": False,
    },
    "ERROR_EXCEPTION_CHANGE": {
        "contract_id": "error_exception_stability",
        "comparison": "error",
        "entry_kind": "error_or_exception_harness",
        "observation": "errno/error code, exception type, message, and failure mode",
        "input_axes": ["each error path", "invalid input", "missing resource", "permission", "fault injection"],
        "requires_explicit_probe": False,
    },
    "SIDE_EFFECT_CHANGE": {
        "contract_id": "side_effect_manifest_stability",
        "comparison": "exact",
        "entry_kind": "state_and_side_effect_probe",
        "observation": "canonical before/after state, I/O, process, network, and concurrency manifest",
        "input_axes": ["normal path", "error path", "state snapshot", "concurrency", "signal interruption"],
        "requires_explicit_probe": True,
    },
    "OUTPUT_FORMAT_CHANGE": {
        "contract_id": "output_format_stability",
        "comparison": "exact",
        "entry_kind": "golden_output_probe",
        "observation": "byte-level stdout/stderr or parsed structured-output schema",
        "input_axes": ["machine format", "human format", "TTY/pipe", "locale", "extreme values"],
        "requires_explicit_probe": False,
    },
    "PROC_SYS_OUTPUT_CHANGE": {
        "contract_id": "proc_sys_interface_stability",
        "comparison": "exact",
        "entry_kind": "proc_sys_snapshot_probe",
        "observation": "node presence, mode, read/write errno, poll semantics, and canonical text/schema",
        "input_axes": ["read", "write", "boundary value", "permissions", "poll/seek", "namespace"],
        "requires_explicit_probe": True,
    },
    "SYSCALL_SEMANTIC_CHANGE": {
        "contract_id": "syscall_semantic_stability",
        "comparison": "exact",
        "entry_kind": "syscall_semantics_reproducer",
        "observation": "return value, errno, output buffers, blocking/timeout, signal, and compat behavior",
        "input_axes": ["flags", "boundary arguments", "invalid pointers", "compat mode", "signal", "timeout"],
        "requires_explicit_probe": True,
    },
    "IOCTL_NETLINK_ABI_CHANGE": {
        "contract_id": "ioctl_netlink_abi_stability",
        "comparison": "exact",
        "entry_kind": "ioctl_or_netlink_uapi_reproducer",
        "observation": "command/family availability, UAPI layout, attributes, policy, reply, and errno",
        "input_axes": ["command/operation", "struct size", "known attributes", "unknown attributes", "nested policy", "compat mode"],
        "requires_explicit_probe": True,
    },
    "CONFIG_CLI_BEHAVIOR_CHANGE": {
        "contract_id": "config_cli_behavior_stability",
        "comparison": "exact",
        "entry_kind": "config_cli_precedence_matrix",
        "observation": "acceptance, default, precedence, exit status, output, and resulting state",
        "input_axes": ["default", "explicit setting", "legacy alias", "invalid value", "CLI/config/env precedence"],
        "requires_explicit_probe": False,
    },
    "RESOURCE_LIFETIME_CHANGE": {
        "contract_id": "resource_lifetime_stability",
        "comparison": "exact",
        "entry_kind": "resource_lifecycle_probe",
        "observation": "allocation/free, fd, lock, refcount, sanitizer, and cleanup manifest",
        "input_axes": ["normal cleanup", "error cleanup", "repetition", "concurrency", "cancellation"],
        "requires_explicit_probe": True,
    },
    "PERFORMANCE_RESOURCE_SEMANTIC_CHANGE": {
        "contract_id": "performance_resource_semantics",
        "comparison": "numeric_tolerance",
        "entry_kind": "timeout_retry_resource_probe",
        "observation": "JSON numeric measurements for timeout, retries, limits, ordering, and resource use",
        "input_axes": ["idle", "nominal load", "boundary limit", "timeout", "retry", "contention"],
        "requires_explicit_probe": True,
        "default_tolerance_percent": 20.0,
    },
}

SUPPORTED_COMPATIBILITY_TYPES = tuple(TYPE_SUPPORT)
SUPPORTED_COMPARISONS = {
    "acceptance",
    "error",
    "exact",
    "exit_code",
    "numeric_tolerance",
    "set_no_additions",
    "success",
}


def get_type_support(compatibility_type: str) -> dict[str, Any]:
    """Return support metadata or raise a precise unsupported-type error."""

    try:
        return TYPE_SUPPORT[compatibility_type]
    except KeyError as exc:
        supported = ", ".join(SUPPORTED_COMPATIBILITY_TYPES)
        raise ValueError(
            f"unsupported compatibility_type {compatibility_type!r}; supported: {supported}"
        ) from exc


def validate_registry() -> list[str]:
    """Return registry consistency errors; an empty list means valid."""

    errors: list[str] = []
    required = {
        "contract_id",
        "comparison",
        "entry_kind",
        "observation",
        "input_axes",
        "requires_explicit_probe",
    }
    contract_ids: set[str] = set()
    for compatibility_type, support in TYPE_SUPPORT.items():
        missing = sorted(required - support.keys())
        if missing:
            errors.append(f"{compatibility_type}: missing {', '.join(missing)}")
        comparison = support.get("comparison")
        if comparison not in SUPPORTED_COMPARISONS:
            errors.append(f"{compatibility_type}: unsupported comparison {comparison!r}")
        contract_id = support.get("contract_id")
        if contract_id in contract_ids:
            errors.append(f"{compatibility_type}: duplicate contract_id {contract_id!r}")
        elif isinstance(contract_id, str):
            contract_ids.add(contract_id)
        if not isinstance(support.get("input_axes"), list) or not support.get("input_axes"):
            errors.append(f"{compatibility_type}: input_axes must be a non-empty list")
    return errors


if __name__ == "__main__":
    registry_errors = validate_registry()
    if registry_errors:
        for registry_error in registry_errors:
            print(f"ERROR: {registry_error}")
        raise SystemExit(1)
    print(f"OK: {len(SUPPORTED_COMPATIBILITY_TYPES)} compatibility types")
