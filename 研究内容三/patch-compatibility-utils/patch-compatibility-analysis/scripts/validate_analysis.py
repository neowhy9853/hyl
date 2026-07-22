#!/usr/bin/env python3
"""Validate final Patch Compatibility Analyzer artifacts.

The schema describes the full output shape, but agents often fail in the
high-value fields first: finding IDs, compatibility type, code line locations,
and evidence snippets. This script keeps those checks dependency-free so it can
run in minimal distro environments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


COMPATIBILITY_TYPES = {
    "API_SIGNATURE_CHANGE",
    "ABI_CHANGE",
    "INPUT_CONTRACT_CHANGE",
    "RETURN_CONTRACT_CHANGE",
    "ERROR_EXCEPTION_CHANGE",
    "SIDE_EFFECT_CHANGE",
    "OUTPUT_FORMAT_CHANGE",
    "PROC_SYS_OUTPUT_CHANGE",
    "SYSCALL_SEMANTIC_CHANGE",
    "IOCTL_NETLINK_ABI_CHANGE",
    "CONFIG_CLI_BEHAVIOR_CHANGE",
    "RESOURCE_LIFETIME_CHANGE",
    "PERFORMANCE_RESOURCE_SEMANTIC_CHANGE",
}

API_KINDS = {
    "exported_function",
    "public_method",
    "public_class",
    "public_function",
    "public_header",
    "shared_library_symbol",
    "symbol_version",
    "pkgconfig_module",
    "syscall",
    "ioctl",
    "netlink_family",
    "procfs_entry",
    "sysfs_attribute",
    "sysctl_entry",
    "cli_command",
    "cli_option",
    "config_key",
    "env_variable",
    "plugin_api",
    "callback_type",
    "struct_type",
    "enum_type",
    "macro",
    "module_parameter",
    "tracepoint",
    "bpf_helper",
    "daemon_handler",
}

LANGUAGES = {"c", "cpp", "python", "go", "ruby", "tcl"}
PRIORITIES = {"high", "medium", "low"}
PATCH_APPLY_STATUSES = {"applied", "already_applied", "applied_3way"}
WORKTREE_STATUSES = {"available", "cleaned"}


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def is_line_pair(value) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) and item >= 0 for item in value)
    )


def check_required(obj: dict, keys: list[str], path: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{path}: missing required field `{key}`")


def validate_finding(
    finding: dict,
    index: int,
    errors: list[str],
    allow_legacy_ids: bool = False,
) -> None:
    path = f"findings[{index}]"
    check_required(
        finding,
        [
            "id",
            "compatibility_type",
            "test_priority",
            "confidence",
            "affected_api",
            "location",
            "old_behavior",
            "new_behavior",
            "compatibility_reason",
            "evidence",
        ],
        path,
        errors,
    )

    finding_id = finding.get("id")
    id_pattern = r"(?:PCA|PCIA)-\d{4}" if allow_legacy_ids else r"PCA-\d{4}"
    if not isinstance(finding_id, str) or not re.fullmatch(id_pattern, finding_id):
        errors.append(f"{path}.id: expected PCA-0001 style ID, got {finding_id!r}")

    compatibility_type = finding.get("compatibility_type")
    if compatibility_type not in COMPATIBILITY_TYPES:
        errors.append(
            f"{path}.compatibility_type: unsupported value {compatibility_type!r}"
        )

    priority = finding.get("test_priority")
    if priority not in PRIORITIES:
        errors.append(f"{path}.test_priority: expected high|medium|low")

    confidence = finding.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append(f"{path}.confidence: expected number in [0, 1]")

    affected_api = finding.get("affected_api")
    if not isinstance(affected_api, dict):
        errors.append(f"{path}.affected_api: expected object")
    else:
        check_required(affected_api, ["name", "kind", "language"], f"{path}.affected_api", errors)
        if affected_api.get("kind") not in API_KINDS:
            errors.append(f"{path}.affected_api.kind: unsupported value {affected_api.get('kind')!r}")
        if affected_api.get("language") not in LANGUAGES:
            errors.append(
                f"{path}.affected_api.language: unsupported value {affected_api.get('language')!r}"
            )

    location = finding.get("location")
    if not isinstance(location, dict):
        errors.append(f"{path}.location: expected object")
    else:
        check_required(location, ["file", "old_lines", "new_lines", "symbol"], f"{path}.location", errors)
        if not location.get("file"):
            errors.append(f"{path}.location.file: required")
        if not location.get("symbol"):
            errors.append(f"{path}.location.symbol: required")
        if not is_line_pair(location.get("old_lines")):
            errors.append(f"{path}.location.old_lines: expected [start, end] integers")
        if not is_line_pair(location.get("new_lines")):
            errors.append(f"{path}.location.new_lines: expected [start, end] integers")

    evidence = finding.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{path}.evidence: expected non-empty array")
    else:
        for ev_index, item in enumerate(evidence):
            ev_path = f"{path}.evidence[{ev_index}]"
            if not isinstance(item, dict):
                errors.append(f"{ev_path}: expected object")
                continue
            check_required(item, ["file", "lines", "snippet"], ev_path, errors)
            if not is_line_pair(item.get("lines")):
                errors.append(f"{ev_path}.lines: expected [start, end] integers")
            if not item.get("snippet"):
                errors.append(f"{ev_path}.snippet: required")


def validate_analysis(path: Path, allow_legacy_ids: bool = False) -> list[str]:
    data = load_json(path)
    errors: list[str] = []
    check_required(
        data,
        [
            "repo",
            "analysis_repo",
            "artifact_dir",
            "base_commit",
            "patch_id",
            "patch_apply_status",
            "summary",
            "findings",
        ],
        "$",
        errors,
    )

    if data.get("patch_apply_status") not in PATCH_APPLY_STATUSES:
        errors.append(
            "$.patch_apply_status: expected one of %s"
            % ", ".join(sorted(PATCH_APPLY_STATUSES))
        )

    analysis_repo = data.get("analysis_repo")
    if not isinstance(analysis_repo, str) or not analysis_repo:
        errors.append("$.analysis_repo: required patched analysis worktree path")

    base_commit = data.get("base_commit")
    if not isinstance(base_commit, str) or not re.fullmatch(r"[0-9a-fA-F]{7,40}", base_commit or ""):
        errors.append("$.base_commit: expected resolved git commit hash")

    worktree_status = data.get("analysis_worktree_status")
    if worktree_status is not None and worktree_status not in WORKTREE_STATUSES:
        errors.append("$.analysis_worktree_status: expected available|cleaned")

    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("$.findings: expected array")
        findings = []

    for index, finding in enumerate(findings):
        if isinstance(finding, dict):
            validate_finding(finding, index, errors, allow_legacy_ids)
        else:
            errors.append(f"findings[{index}]: expected object")

    summary = data.get("summary")
    if isinstance(summary, dict):
        counted = {
            "compatibility_changes": len(findings),
            "high_priority": sum(1 for item in findings if isinstance(item, dict) and item.get("test_priority") == "high"),
            "medium_priority": sum(1 for item in findings if isinstance(item, dict) and item.get("test_priority") == "medium"),
            "low_priority": sum(1 for item in findings if isinstance(item, dict) and item.get("test_priority") == "low"),
        }
        for key, value in counted.items():
            if summary.get(key) != value:
                errors.append(f"summary.{key}: expected {value}, got {summary.get(key)!r}")
    else:
        errors.append("$.summary: expected object")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PCA analysis.json")
    parser.add_argument("analysis", help="Path to analysis.json")
    parser.add_argument(
        "--allow-legacy-ids",
        action="store_true",
        help="Accept legacy PCIA-0001 IDs when ingesting older analysis results",
    )
    args = parser.parse_args()

    try:
        errors = validate_analysis(Path(args.analysis), args.allow_legacy_ids)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.analysis}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
