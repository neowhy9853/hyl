#!/usr/bin/env python3
"""Validate test-summary.json and deterministically render COVERAGE_REPORT.md."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from compatibility_types import SUPPORTED_COMPATIBILITY_TYPES, validate_registry


TOP_REQUIRED = [
    "schema_version",
    "report_language",
    "analysis_json",
    "patch_id",
    "result_dir",
    "status",
    "target",
    "environment",
    "summary",
    "finding_results",
    "blocked_or_not_run",
    "artifacts",
    "conclusion",
    "coverage_report",
]

COVERAGE_CLASSIFICATIONS = {
    "coverable",
    "architecturally_unreachable",
    "fault_injection_needed",
    "not_attempted",
}

CLASSIFICATION_LABELS = {
    "zh": {
        "coverable": "可覆盖",
        "architecturally_unreachable": "架构不可达",
        "fault_injection_needed": "需故障注入",
        "not_attempted": "未尝试",
    },
    "en": {
        "coverable": "coverable",
        "architecturally_unreachable": "architecturally unreachable",
        "fault_injection_needed": "fault injection needed",
        "not_attempted": "not attempted",
    },
}

SUMMARY_FIELDS = [
    "findings_total",
    "findings_targeted",
    "entries_planned",
    "entries_generated",
    "entries_verified",
    "inputs_planned",
    "inputs_executed",
    "contracts_total",
    "contracts_passed",
    "contracts_breached",
    "contracts_skipped",
    "patch_executable_lines",
    "patch_lines_covered",
    "patch_lines_uncovered",
    "patch_line_coverage_rate",
]

ARTIFACT_FIELDS = [
    "impact_map",
    "test_entry_tasks",
    "test_entries",
    "test_inputs",
    "execution_results",
    "contract_summary",
    "coverage_data",
    "report",
]

FINDING_ID_PATTERN = re.compile(r"^(?:PCA|PCIA)-[0-9]{4}$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return payload


def require_fields(obj: Any, fields: list[str], path: str, errors: list[str]) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{path}: expected object")
        return
    for field in fields:
        if field not in obj:
            errors.append(f"{path}: missing required field `{field}`")


def is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_rate(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 100


def require_string(
    value: Any,
    path: str,
    errors: list[str],
    *,
    min_length: int = 0,
) -> None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected string")
    elif len(value) < min_length:
        errors.append(f"{path}: expected at least {min_length} characters")


def validate_finding(item: Any, index: int, errors: list[str]) -> None:
    path = f"finding_results[{index}]"
    required = [
        "finding_id",
        "compatibility_type",
        "test_priority",
        "status",
        "target_location",
        "entries",
        "contracts",
        "coverage",
        "behavior_differences",
        "notes",
    ]
    require_fields(item, required, path, errors)
    if not isinstance(item, dict):
        return
    finding_id = item.get("finding_id")
    if not isinstance(finding_id, str) or FINDING_ID_PATTERN.fullmatch(finding_id) is None:
        errors.append(f"{path}.finding_id: expected PCA-0001 or legacy PCIA-0001")
    compatibility_type = item.get("compatibility_type")
    require_string(compatibility_type, f"{path}.compatibility_type", errors)
    if compatibility_type not in SUPPORTED_COMPATIBILITY_TYPES:
        errors.append(f"{path}.compatibility_type: unsupported compatibility type")
    if item.get("test_priority") not in {"high", "medium", "low"}:
        errors.append(f"{path}.test_priority: expected high|medium|low")
    if item.get("status") not in {"passed", "failed", "partial", "blocked", "not_run"}:
        errors.append(f"{path}.status: unsupported status")

    location = item.get("target_location")
    require_fields(location, ["file", "new_lines", "symbol"], f"{path}.target_location", errors)
    if isinstance(location, dict):
        require_string(location.get("file"), f"{path}.target_location.file", errors)
        require_string(location.get("symbol"), f"{path}.target_location.symbol", errors)
        lines = location.get("new_lines")
        if not (
            isinstance(lines, list)
            and len(lines) == 2
            and all(is_non_negative_int(value) for value in lines)
        ):
            errors.append(f"{path}.target_location.new_lines: expected [start, end]")
        elif lines[0] > lines[1]:
            errors.append(f"{path}.target_location.new_lines: start cannot exceed end")

    for field in ("entries", "contracts", "behavior_differences", "notes"):
        if not isinstance(item.get(field), list):
            errors.append(f"{path}.{field}: expected array")

    if isinstance(item.get("entries"), list):
        if item.get("status") == "passed" and not item["entries"]:
            errors.append(f"{path}.entries: passed finding requires at least one entry")
        for entry_index, entry in enumerate(item["entries"]):
            entry_path = f"{path}.entries[{entry_index}]"
            require_fields(
                entry,
                [
                    "entry_id",
                    "status",
                    "artifact_path",
                    "run_command",
                    "expected_signal",
                    "reachability_signal",
                ],
                entry_path,
                errors,
            )
            if isinstance(entry, dict):
                for field in (
                    "entry_id",
                    "status",
                    "artifact_path",
                    "run_command",
                    "expected_signal",
                    "reachability_signal",
                ):
                    require_string(entry.get(field), f"{entry_path}.{field}", errors)
    if isinstance(item.get("contracts"), list):
        for contract_index, contract in enumerate(item["contracts"]):
            contract_path = f"{path}.contracts[{contract_index}]"
            require_fields(contract, ["contract_id", "status", "detail"], contract_path, errors)
            if isinstance(contract, dict):
                require_string(contract.get("contract_id"), f"{contract_path}.contract_id", errors)
                require_string(contract.get("detail"), f"{contract_path}.detail", errors)
                if contract.get("status") not in {"passed", "breached", "skipped"}:
                    errors.append(f"{contract_path}.status: expected passed|breached|skipped")
    if isinstance(item.get("behavior_differences"), list):
        for diff_index, difference in enumerate(item["behavior_differences"]):
            difference_path = f"{path}.behavior_differences[{diff_index}]"
            require_fields(
                difference,
                ["input_id", "diff_type", "before", "after", "evidence"],
                difference_path,
                errors,
            )
            if isinstance(difference, dict):
                for field in ("input_id", "diff_type", "before", "after", "evidence"):
                    require_string(difference.get(field), f"{difference_path}.{field}", errors)
                if difference.get("diff_type") not in SUPPORTED_COMPATIBILITY_TYPES:
                    errors.append(f"{difference_path}.diff_type: unsupported compatibility type")
    if isinstance(item.get("notes"), list) and not all(isinstance(note, str) for note in item["notes"]):
        errors.append(f"{path}.notes: every item must be a string")

    coverage = item.get("coverage")
    require_fields(
        coverage,
        ["executable_lines", "covered_lines", "uncovered_lines", "rate"],
        f"{path}.coverage",
        errors,
    )
    if isinstance(coverage, dict):
        executable = coverage.get("executable_lines")
        covered = coverage.get("covered_lines")
        uncovered = coverage.get("uncovered_lines")
        rate = coverage.get("rate")
        if not is_non_negative_int(executable):
            errors.append(f"{path}.coverage.executable_lines: expected non-negative integer")
        if not is_non_negative_int(covered):
            errors.append(f"{path}.coverage.covered_lines: expected non-negative integer")
        if not isinstance(uncovered, list):
            errors.append(f"{path}.coverage.uncovered_lines: expected array")
        elif not all(isinstance(line, str) for line in uncovered):
            errors.append(f"{path}.coverage.uncovered_lines: every item must be a string")
        if not is_rate(rate):
            errors.append(f"{path}.coverage.rate: expected percentage in [0, 100]")
        if is_non_negative_int(executable) and is_non_negative_int(covered) and covered > executable:
            errors.append(f"{path}.coverage.covered_lines: cannot exceed executable_lines")
        if (
            is_non_negative_int(executable)
            and is_non_negative_int(covered)
            and isinstance(uncovered, list)
            and executable != covered + len(uncovered)
        ):
            errors.append(
                f"{path}.coverage: executable_lines must equal covered_lines + len(uncovered_lines)"
            )
        if is_non_negative_int(executable) and is_non_negative_int(covered) and is_rate(rate):
            expected_rate = 0.0 if executable == 0 else covered * 100.0 / executable
            if not math.isclose(float(rate), expected_rate, abs_tol=0.05):
                errors.append(
                    f"{path}.coverage.rate: expected {expected_rate:.2f} from coverage counts"
                )


def coverage_count_fields(item: dict[str, Any], path: str, errors: list[str]) -> None:
    executable = item.get("executable_lines")
    covered = item.get("covered_lines")
    uncovered = item.get("uncovered_lines")
    rate = item.get("rate")
    if not is_non_negative_int(executable):
        errors.append(f"{path}.executable_lines: expected non-negative integer")
    if not is_non_negative_int(covered):
        errors.append(f"{path}.covered_lines: expected non-negative integer")
    if not isinstance(uncovered, list):
        errors.append(f"{path}.uncovered_lines: expected array")
    elif not all(isinstance(line, str) for line in uncovered):
        errors.append(f"{path}.uncovered_lines: every item must be a string")
    if not is_rate(rate):
        errors.append(f"{path}.rate: expected percentage in [0, 100]")
    if (
        is_non_negative_int(executable)
        and is_non_negative_int(covered)
        and covered > executable
    ):
        errors.append(f"{path}.covered_lines: cannot exceed executable_lines")
    if (
        is_non_negative_int(executable)
        and is_non_negative_int(covered)
        and isinstance(uncovered, list)
        and executable != covered + len(uncovered)
    ):
        errors.append(
            f"{path}: executable_lines must equal covered_lines + len(uncovered_lines)"
        )
    if is_non_negative_int(executable) and is_non_negative_int(covered) and is_rate(rate):
        expected = 0.0 if executable == 0 else covered * 100.0 / executable
        if not math.isclose(float(rate), expected, abs_tol=0.05):
            errors.append(f"{path}.rate: expected {expected:.2f} from coverage counts")


def validate_coverage_report(data: dict[str, Any], errors: list[str]) -> None:
    path = "coverage_report"
    section = data.get(path)
    require_fields(
        section,
        [
            "tool",
            "gate",
            "findings",
            "files",
            "uncovered_line_analysis",
            "iterations",
            "caveats",
        ],
        path,
        errors,
    )
    if not isinstance(section, dict):
        return
    require_string(section.get("tool"), f"{path}.tool", errors, min_length=1)
    for field in ("optimization", "coverage_data"):
        if field in section:
            require_string(section.get(field), f"{path}.{field}", errors)

    summary = data.get("summary")
    conclusion = data.get("conclusion")

    gate = section.get("gate")
    require_fields(gate, ["threshold", "rate", "met"], f"{path}.gate", errors)
    if isinstance(gate, dict):
        if not is_rate(gate.get("threshold")):
            errors.append(f"{path}.gate.threshold: expected percentage in [0, 100]")
        if not is_rate(gate.get("rate")):
            errors.append(f"{path}.gate.rate: expected percentage in [0, 100]")
        if not isinstance(gate.get("met"), bool):
            errors.append(f"{path}.gate.met: expected boolean")
        declared_gate = data.get("coverage_gate", 80)
        if is_rate(gate.get("threshold")) and is_rate(declared_gate):
            if float(gate["threshold"]) != float(declared_gate):
                errors.append(f"{path}.gate.threshold: must equal coverage_gate")
        if (
            is_rate(gate.get("rate"))
            and isinstance(summary, dict)
            and is_rate(summary.get("patch_line_coverage_rate"))
            and not math.isclose(
                float(gate["rate"]),
                float(summary["patch_line_coverage_rate"]),
                abs_tol=0.05,
            )
        ):
            errors.append(
                f"{path}.gate.rate: must match summary.patch_line_coverage_rate"
            )
        if (
            isinstance(gate.get("met"), bool)
            and isinstance(conclusion, dict)
            and isinstance(conclusion.get("coverage_gate_met"), bool)
            and gate["met"] != conclusion["coverage_gate_met"]
        ):
            errors.append(f"{path}.gate.met: must match conclusion.coverage_gate_met")

    finding_results = data.get("finding_results")
    finding_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(finding_results, list):
        for finding in finding_results:
            if isinstance(finding, dict) and isinstance(finding.get("finding_id"), str):
                finding_by_id[finding["finding_id"]] = finding

    coverage_findings = section.get("findings")
    if not isinstance(coverage_findings, list):
        errors.append(f"{path}.findings: expected array")
        coverage_findings = []
    seen_findings: set[str] = set()
    for index, item in enumerate(coverage_findings):
        item_path = f"{path}.findings[{index}]"
        require_fields(
            item,
            [
                "finding_id",
                "file",
                "new_lines",
                "executable_lines",
                "covered_lines",
                "uncovered_lines",
                "rate",
            ],
            item_path,
            errors,
        )
        if not isinstance(item, dict):
            continue
        finding_id = item.get("finding_id")
        require_string(finding_id, f"{item_path}.finding_id", errors)
        if isinstance(finding_id, str) and finding_id:
            if finding_id in seen_findings:
                errors.append(f"{item_path}.finding_id: duplicate entry")
            seen_findings.add(finding_id)
            target = finding_by_id.get(finding_id)
            if target is None:
                errors.append(
                    f"{item_path}.finding_id: no matching finding_results entry"
                )
            else:
                target_coverage = target.get("coverage")
                if isinstance(target_coverage, dict):
                    for field in ("executable_lines", "covered_lines"):
                        if item.get(field) != target_coverage.get(field):
                            errors.append(
                                f"{item_path}.{field}: must match finding_results coverage"
                            )
                    if isinstance(item.get("uncovered_lines"), list) and isinstance(
                        target_coverage.get("uncovered_lines"), list
                    ):
                        if len(item["uncovered_lines"]) != len(
                            target_coverage["uncovered_lines"]
                        ):
                            errors.append(
                                f"{item_path}.uncovered_lines: must match finding_results coverage"
                            )
        require_string(item.get("file"), f"{item_path}.file", errors)
        lines = item.get("new_lines")
        if not (
            isinstance(lines, list)
            and len(lines) == 2
            and all(is_non_negative_int(value) for value in lines)
        ):
            errors.append(f"{item_path}.new_lines: expected [start, end]")
        coverage_count_fields(item, item_path, errors)

    files_list = section.get("files")
    if not isinstance(files_list, list):
        errors.append(f"{path}.files: expected array")
        files_list = []
    sum_executable = 0
    sum_covered = 0
    sum_uncovered = 0
    file_uncovered_keys: list[str] = []
    for index, item in enumerate(files_list):
        item_path = f"{path}.files[{index}]"
        require_fields(
            item,
            ["file", "executable_lines", "covered_lines", "uncovered_lines", "rate"],
            item_path,
            errors,
        )
        if not isinstance(item, dict):
            continue
        require_string(item.get("file"), f"{item_path}.file", errors)
        coverage_count_fields(item, item_path, errors)
        if is_non_negative_int(item.get("executable_lines")):
            sum_executable += item["executable_lines"]
        if is_non_negative_int(item.get("covered_lines")):
            sum_covered += item["covered_lines"]
        uncovered = item.get("uncovered_lines")
        if isinstance(uncovered, list):
            for entry in uncovered:
                if (
                    not isinstance(entry, str)
                    or ":" not in entry
                    or not entry.rsplit(":", 1)[1].isdigit()
                ):
                    errors.append(
                        f"{item_path}.uncovered_lines: expected '<file>:<line>' entries"
                    )
                    continue
                sum_uncovered += 1
                file_uncovered_keys.append(entry)

    if isinstance(summary, dict) and is_non_negative_int(
        summary.get("patch_executable_lines")
    ):
        executable_total = summary.get("patch_executable_lines")
        if executable_total > 0 and not files_list:
            errors.append(f"{path}.files: required when patch_executable_lines > 0")
        if files_list:
            if sum_executable != executable_total:
                errors.append(
                    f"{path}.files: executable_lines total must match summary.patch_executable_lines"
                )
            if (
                is_non_negative_int(summary.get("patch_lines_covered"))
                and sum_covered != summary["patch_lines_covered"]
            ):
                errors.append(
                    f"{path}.files: covered_lines total must match summary.patch_lines_covered"
                )
            if (
                is_non_negative_int(summary.get("patch_lines_uncovered"))
                and sum_uncovered != summary["patch_lines_uncovered"]
            ):
                errors.append(
                    f"{path}.files: uncovered_lines count must match summary.patch_lines_uncovered"
                )

    analysis_entries = section.get("uncovered_line_analysis")
    if not isinstance(analysis_entries, list):
        errors.append(f"{path}.uncovered_line_analysis: expected array")
        analysis_entries = []
    analyzed_keys: set[str] = set()
    for index, item in enumerate(analysis_entries):
        item_path = f"{path}.uncovered_line_analysis[{index}]"
        require_fields(
            item, ["file", "line", "classification", "reason"], item_path, errors
        )
        if not isinstance(item, dict):
            continue
        require_string(item.get("file"), f"{item_path}.file", errors)
        line = item.get("line")
        if not is_non_negative_int(line):
            errors.append(f"{item_path}.line: expected non-negative integer")
        if item.get("classification") not in COVERAGE_CLASSIFICATIONS:
            errors.append(f"{item_path}.classification: unsupported value")
        require_string(item.get("reason"), f"{item_path}.reason", errors, min_length=1)
        if isinstance(item.get("file"), str) and is_non_negative_int(line):
            analyzed_keys.add("%s:%d" % (item["file"], line))
    for entry in file_uncovered_keys:
        if entry not in analyzed_keys:
            errors.append(
                f"{path}: uncovered line {entry} has no uncovered_line_analysis entry"
            )

    iterations = section.get("iterations")
    if not isinstance(iterations, list):
        errors.append(f"{path}.iterations: expected array")
    else:
        for index, item in enumerate(iterations):
            item_path = f"{path}.iterations[{index}]"
            require_fields(item, ["round", "rate", "inputs_added"], item_path, errors)
            if not isinstance(item, dict):
                continue
            if not (is_non_negative_int(item.get("round")) and item["round"] >= 1):
                errors.append(f"{item_path}.round: expected integer >= 1")
            if not is_rate(item.get("rate")):
                errors.append(f"{item_path}.rate: expected percentage in [0, 100]")
            if not is_non_negative_int(item.get("inputs_added")):
                errors.append(
                    f"{item_path}.inputs_added: expected non-negative integer"
                )
            if "rate_before" in item and not is_rate(item.get("rate_before")):
                errors.append(
                    f"{item_path}.rate_before: expected percentage in [0, 100]"
                )

    caveats = section.get("caveats")
    if not isinstance(caveats, list):
        errors.append(f"{path}.caveats: expected array")
    elif not all(isinstance(caveat, str) for caveat in caveats):
        errors.append(f"{path}.caveats: every item must be a string")


def validate_result(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(f"compatibility type registry: {error}" for error in validate_registry())
    require_fields(data, TOP_REQUIRED, "$", errors)
    if data.get("schema_version") != "1.0":
        errors.append("schema_version: expected `1.0`")
    require_string(data.get("report_language"), "report_language", errors, min_length=2)
    for field in ("analysis_json", "patch_id", "result_dir"):
        require_string(data.get(field), field, errors, min_length=1)
    if data.get("status") not in {"passed", "failed", "partial", "blocked"}:
        errors.append("status: expected passed|failed|partial|blocked")

    target = data.get("target")
    require_fields(target, ["repo", "base_commit", "analysis_repo", "package_profile"], "target", errors)
    if isinstance(target, dict):
        for field in ("repo", "base_commit", "analysis_repo", "package_profile"):
            require_string(target.get(field), f"target.{field}", errors)
    environment = data.get("environment")
    require_fields(
        environment,
        ["kind", "before_build", "after_build", "compiler", "optimization", "coverage_tool", "notes"],
        "environment",
        errors,
    )
    if isinstance(environment, dict):
        if environment.get("kind") not in {"host", "container", "vm", "mixed", "not_available"}:
            errors.append("environment.kind: unsupported value")
        for field in ("before_build", "after_build"):
            if environment.get(field) not in {"passed", "failed", "not_run", "blocked"}:
                errors.append(f"environment.{field}: unsupported value")
        for field in ("compiler", "optimization", "coverage_tool"):
            require_string(environment.get(field), f"environment.{field}", errors)
        if not isinstance(environment.get("notes"), list):
            errors.append("environment.notes: expected array")
        elif not all(isinstance(note, str) for note in environment["notes"]):
            errors.append("environment.notes: every item must be a string")

    summary = data.get("summary")
    require_fields(summary, SUMMARY_FIELDS, "summary", errors)
    if isinstance(summary, dict):
        for field in SUMMARY_FIELDS[:-1]:
            if not is_non_negative_int(summary.get(field)):
                errors.append(f"summary.{field}: expected non-negative integer")
        rate = summary.get("patch_line_coverage_rate")
        if not is_rate(rate):
            errors.append("summary.patch_line_coverage_rate: expected percentage in [0, 100]")
        executable = summary.get("patch_executable_lines")
        covered = summary.get("patch_lines_covered")
        uncovered = summary.get("patch_lines_uncovered")
        if all(is_non_negative_int(value) for value in (executable, covered, uncovered)):
            if executable != covered + uncovered:
                errors.append(
                    "summary coverage counts: patch_executable_lines must equal "
                    "patch_lines_covered + patch_lines_uncovered"
                )
            expected_rate = 0.0 if executable == 0 else covered * 100.0 / executable
            if is_rate(rate) and not math.isclose(float(rate), expected_rate, abs_tol=0.05):
                errors.append(
                    "summary.patch_line_coverage_rate: expected %.2f from coverage counts, got %r"
                    % (expected_rate, rate)
                )
        contract_values = [
            summary.get("contracts_passed"),
            summary.get("contracts_breached"),
            summary.get("contracts_skipped"),
        ]
        if all(is_non_negative_int(value) for value in contract_values):
            if summary.get("contracts_total") != sum(contract_values):
                errors.append(
                    "summary.contracts_total must equal passed + breached + skipped"
                )
        for smaller, larger in (
            ("findings_targeted", "findings_total"),
            ("entries_verified", "entries_generated"),
            ("inputs_executed", "inputs_planned"),
        ):
            if is_non_negative_int(summary.get(smaller)) and is_non_negative_int(summary.get(larger)):
                if summary[smaller] > summary[larger]:
                    errors.append(f"summary.{smaller} cannot exceed {larger}")

    findings = data.get("finding_results")
    if not isinstance(findings, list):
        errors.append("finding_results: expected array")
        findings = []
    for index, finding in enumerate(findings):
        validate_finding(finding, index, errors)
    if isinstance(summary, dict) and is_non_negative_int(summary.get("findings_targeted")):
        if summary["findings_targeted"] != len(findings):
            errors.append("summary.findings_targeted must equal len(finding_results)")

    blockers = data.get("blocked_or_not_run")
    if not isinstance(blockers, list):
        errors.append("blocked_or_not_run: expected array")
        blockers = []
    for index, blocker in enumerate(blockers):
        blocker_path = f"blocked_or_not_run[{index}]"
        require_fields(blocker, ["scope", "id", "reason", "required_action"], blocker_path, errors)
        if isinstance(blocker, dict):
            if blocker.get("scope") not in {
                "environment",
                "build",
                "entry",
                "input",
                "contract",
                "coverage",
                "finding",
            }:
                errors.append(f"{blocker_path}.scope: unsupported value")
            require_string(blocker.get("id"), f"{blocker_path}.id", errors)
            require_string(blocker.get("reason"), f"{blocker_path}.reason", errors, min_length=1)
            require_string(
                blocker.get("required_action"),
                f"{blocker_path}.required_action",
                errors,
                min_length=1,
            )

    artifacts = data.get("artifacts")
    require_fields(artifacts, ARTIFACT_FIELDS, "artifacts", errors)
    if isinstance(artifacts, dict):
        for key, value in artifacts.items():
            if not isinstance(value, str):
                errors.append(f"artifacts.{key}: expected string path")
    conclusion = data.get("conclusion")
    require_fields(
        conclusion,
        ["backward_compatibility", "coverage_gate_met", "rationale", "recommended_actions"],
        "conclusion",
        errors,
    )
    if isinstance(conclusion, dict):
        if conclusion.get("backward_compatibility") not in {"compatible", "incompatible", "inconclusive"}:
            errors.append("conclusion.backward_compatibility: unsupported value")
        if not isinstance(conclusion.get("coverage_gate_met"), bool):
            errors.append("conclusion.coverage_gate_met: expected boolean")
        require_string(conclusion.get("rationale"), "conclusion.rationale", errors)
        if not isinstance(conclusion.get("recommended_actions"), list):
            errors.append("conclusion.recommended_actions: expected array")
        elif not all(isinstance(action, str) for action in conclusion["recommended_actions"]):
            errors.append("conclusion.recommended_actions: every item must be a string")
        gate = data.get("coverage_gate", 80)
        if not is_rate(gate):
            errors.append("coverage_gate: expected percentage in [0, 100]")
        elif isinstance(summary, dict) and is_rate(summary.get("patch_line_coverage_rate")):
            expected_gate = (
                summary.get("patch_executable_lines", 0) > 0
                and summary["patch_line_coverage_rate"] >= gate
            )
            if conclusion.get("coverage_gate_met") is not expected_gate:
                errors.append(
                    "conclusion.coverage_gate_met does not match coverage rate and gate"
                )

    validate_coverage_report(data, errors)

    status = data.get("status")
    if status == "passed" and isinstance(summary, dict):
        if summary.get("contracts_breached") != 0 or blockers:
            errors.append("status passed requires zero contract breaches and no blockers")
        if isinstance(conclusion, dict) and not conclusion.get("coverage_gate_met"):
            errors.append("status passed requires coverage_gate_met=true")
        if isinstance(environment, dict) and (
            environment.get("before_build") != "passed"
            or environment.get("after_build") != "passed"
        ):
            errors.append("status passed requires before_build=passed and after_build=passed")
        if any(
            isinstance(finding, dict) and finding.get("status") != "passed"
            for finding in findings
        ):
            errors.append("status passed requires every finding result to be passed")
        if summary.get("inputs_executed", 0) == 0:
            errors.append("status passed requires at least one executed input")
        if summary.get("findings_targeted", 0) > 0 and summary.get("entries_verified", 0) == 0:
            errors.append("status passed requires a verified entry for targeted findings")
    if status == "blocked" and not blockers:
        errors.append("status blocked requires at least one blocked_or_not_run item")
    if status == "blocked" and isinstance(summary, dict) and summary.get("inputs_executed") != 0:
        errors.append("status blocked requires inputs_executed=0; use partial after meaningful execution")
    if isinstance(conclusion, dict) and conclusion.get("backward_compatibility") == "compatible":
        if blockers or (isinstance(summary, dict) and summary.get("contracts_breached") != 0):
            errors.append("compatible conclusion requires no blockers or contract breaches")
        if not conclusion.get("coverage_gate_met"):
            errors.append("compatible conclusion requires coverage_gate_met=true")
        if isinstance(summary, dict) and summary.get("inputs_executed", 0) == 0:
            errors.append("compatible conclusion requires executed inputs")

    return errors


def cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", "<br>").replace("|", "\\|")


def location_text(location: dict[str, Any]) -> str:
    lines = location.get("new_lines") or ["", ""]
    return f"{location.get('file', '')}:{lines[0]}-{lines[1]} ({location.get('symbol', '')})"


def render_report(data: dict[str, Any]) -> str:
    zh = str(data.get("report_language", "zh-CN")).lower().startswith("zh")
    summary = data["summary"]
    target = data["target"]
    environment = data["environment"]
    conclusion = data["conclusion"]
    title = "补丁兼容性测试报告" if zh else "Patch Compatibility Test Report"
    lines = [f"# {title}", ""]

    if zh:
        lines.extend([
            "## 目标与结论", "",
            "| 字段 | 值 |", "|---|---|",
            f"| Patch ID | `{cell(data['patch_id'])}` |",
            f"| 仓库 | `{cell(target.get('repo'))}` |",
            f"| 基线 | `{cell(target.get('base_commit'))}` |",
            f"| Profile | `{cell(target.get('package_profile'))}` |",
            f"| 执行状态 | `{cell(data['status'])}` |",
            f"| 向后兼容结论 | `{cell(conclusion.get('backward_compatibility'))}` |",
            f"| 覆盖率门槛 | `{cell(data.get('coverage_gate', 80))}%` |",
            f"| 是否达标 | `{cell(conclusion.get('coverage_gate_met'))}` |",
            "", f"**结论依据**：{cell(conclusion.get('rationale'))}", "",
            "## 汇总", "",
            "| 指标 | 数值 |", "|---|---:|",
        ])
    else:
        lines.extend([
            "## Target and conclusion", "",
            "| Field | Value |", "|---|---|",
            f"| Patch ID | `{cell(data['patch_id'])}` |",
            f"| Repository | `{cell(target.get('repo'))}` |",
            f"| Baseline | `{cell(target.get('base_commit'))}` |",
            f"| Profile | `{cell(target.get('package_profile'))}` |",
            f"| Execution status | `{cell(data['status'])}` |",
            f"| Backward compatibility | `{cell(conclusion.get('backward_compatibility'))}` |",
            f"| Coverage gate | `{cell(data.get('coverage_gate', 80))}%` |",
            f"| Gate met | `{cell(conclusion.get('coverage_gate_met'))}` |",
            "", f"**Rationale**: {cell(conclusion.get('rationale'))}", "",
            "## Summary", "",
            "| Metric | Value |", "|---|---:|",
        ])

    summary_labels = {
        "findings_total": ("分析 findings", "Analysis findings"),
        "findings_targeted": ("测试 findings", "Targeted findings"),
        "entries_planned": ("规划入口", "Planned entries"),
        "entries_generated": ("生成入口", "Generated entries"),
        "entries_verified": ("验证入口", "Verified entries"),
        "inputs_planned": ("规划输入", "Planned inputs"),
        "inputs_executed": ("执行输入", "Executed inputs"),
        "contracts_passed": ("契约通过", "Contracts passed"),
        "contracts_breached": ("契约违约", "Contracts breached"),
        "contracts_skipped": ("契约跳过", "Contracts skipped"),
        "patch_executable_lines": ("补丁可执行行", "Patch executable lines"),
        "patch_lines_covered": ("已覆盖行", "Covered lines"),
        "patch_lines_uncovered": ("未覆盖行", "Uncovered lines"),
        "patch_line_coverage_rate": ("补丁行覆盖率", "Patch line coverage rate"),
    }
    for key, labels in summary_labels.items():
        value = summary[key]
        if key == "patch_line_coverage_rate":
            value = f"{value:.2f}%"
        lines.append(f"| {labels[0] if zh else labels[1]} | {cell(value)} |")

    lines.extend([
        "", "## 测试环境" if zh else "## Test environment", "",
        "| 字段 | 值 |" if zh else "| Field | Value |", "|---|---|",
        f"| {'类型' if zh else 'Kind'} | `{cell(environment.get('kind'))}` |",
        f"| {'基线构建' if zh else 'Before build'} | `{cell(environment.get('before_build'))}` |",
        f"| {'补丁后构建' if zh else 'After build'} | `{cell(environment.get('after_build'))}` |",
        f"| {'编译器' if zh else 'Compiler'} | `{cell(environment.get('compiler'))}` |",
        f"| {'优化级别' if zh else 'Optimization'} | `{cell(environment.get('optimization'))}` |",
        f"| {'覆盖率工具' if zh else 'Coverage tool'} | `{cell(environment.get('coverage_tool'))}` |",
    ])
    for note in environment.get("notes", []):
        lines.append(f"- {cell(note)}")

    lines.extend(["", "## Finding 测试结果" if zh else "## Finding results", ""])
    for finding in data["finding_results"]:
        lines.extend([
            f"### {cell(finding['finding_id'])}: {cell(finding['compatibility_type'])}", "",
            f"- **{'优先级' if zh else 'Priority'}**: `{cell(finding['test_priority'])}`",
            f"- **{'状态' if zh else 'Status'}**: `{cell(finding['status'])}`",
            f"- **{'目标' if zh else 'Target'}**: `{cell(location_text(finding['target_location']))}`",
            "",
            "#### 测试入口" if zh else "#### Test entries", "",
            "| Entry | Status | Artifact | Command | Expected | Reachability |",
            "|---|---|---|---|---|---|",
        ])
        for entry in finding["entries"]:
            lines.append(
                "| {entry_id} | {status} | `{artifact}` | `{command}` | {expected} | {reachability} |".format(
                    entry_id=cell(entry.get("entry_id")),
                    status=cell(entry.get("status")),
                    artifact=cell(entry.get("artifact_path")),
                    command=cell(entry.get("run_command")),
                    expected=cell(entry.get("expected_signal")),
                    reachability=cell(entry.get("reachability_signal")),
                )
            )
        if not finding["entries"]:
            lines.append("| - | - | - | - | - | - |")

        coverage = finding["coverage"]
        lines.extend([
            "", "#### 契约与覆盖率" if zh else "#### Contracts and coverage", "",
            "| Contract | Status | Detail |", "|---|---|---|",
        ])
        for contract in finding["contracts"]:
            lines.append(
                f"| {cell(contract.get('contract_id'))} | {cell(contract.get('status'))} | {cell(contract.get('detail'))} |"
            )
        if not finding["contracts"]:
            lines.append("| - | - | - |")
        lines.extend([
            "",
            f"- **{'覆盖率' if zh else 'Coverage'}**: {coverage['covered_lines']}/{coverage['executable_lines']} ({coverage['rate']:.2f}%)",
            f"- **{'未覆盖行' if zh else 'Uncovered lines'}**: {cell(', '.join(coverage['uncovered_lines']) or '-')}",
        ])

        if finding["behavior_differences"]:
            lines.extend([
                "", "#### 行为差异" if zh else "#### Behavior differences", "",
                "| Input | Type | Before | After | Evidence |", "|---|---|---|---|---|",
            ])
            for difference in finding["behavior_differences"]:
                lines.append(
                    f"| {cell(difference.get('input_id'))} | {cell(difference.get('diff_type'))} | "
                    f"{cell(difference.get('before'))} | {cell(difference.get('after'))} | {cell(difference.get('evidence'))} |"
                )
        for note in finding["notes"]:
            lines.append(f"- {cell(note)}")
        lines.append("")

    lines.extend(["## 阻塞与未执行项" if zh else "## Blocked and not-run items", ""])
    if data["blocked_or_not_run"]:
        lines.extend([
            "| Scope | ID | Reason | Required action |", "|---|---|---|---|",
        ])
        for blocker in data["blocked_or_not_run"]:
            lines.append(
                f"| {cell(blocker.get('scope'))} | {cell(blocker.get('id'))} | "
                f"{cell(blocker.get('reason'))} | {cell(blocker.get('required_action'))} |"
            )
    else:
        lines.append("无。" if zh else "None.")

    lines.extend(["", "## 产物" if zh else "## Artifacts", "", "| Artifact | Path |", "|---|---|"])
    for key in sorted(data["artifacts"]):
        lines.append(f"| {cell(key)} | `{cell(data['artifacts'][key])}` |")

    lines.extend(["", "## 建议" if zh else "## Recommendations", ""])
    actions = conclusion.get("recommended_actions", [])
    lines.extend(f"- {cell(action)}" for action in actions)
    if not actions:
        lines.append("- 无。" if zh else "- None.")
    return "\n".join(lines).rstrip() + "\n"


def coverage_target_text(item: dict[str, Any], meta: dict[str, Any]) -> str:
    location = meta.get("target_location") if isinstance(meta, dict) else None
    if isinstance(location, dict) and location.get("file"):
        return location_text(location)
    lines = item.get("new_lines") or ["", ""]
    return f"{item.get('file', '')}:{lines[0]}-{lines[1]}"


def _rate_text(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:.2f}%"
    return cell(value)


def render_coverage_report(data: dict[str, Any]) -> str:
    zh = str(data.get("report_language", "zh-CN")).lower().startswith("zh")

    def L(zh_text: str, en_text: str) -> str:
        return zh_text if zh else en_text

    section = data["coverage_report"]
    summary = data["summary"]
    gate = section.get("gate", {})
    classification_labels = CLASSIFICATION_LABELS["zh" if zh else "en"]
    finding_meta = {
        finding.get("finding_id"): finding
        for finding in data.get("finding_results", [])
        if isinstance(finding, dict)
    }

    lines = [f"# {L('补丁行覆盖率报告', 'Patch Line Coverage Report')}", ""]

    lines.extend(
        [
            f"## {L('覆盖率结论', 'Coverage conclusion')}",
            "",
            f"| {L('字段', 'Field')} | {L('值', 'Value')} |",
            "|---|---|",
            f"| {L('覆盖率工具', 'Coverage tool')} | `{cell(section.get('tool'))}` |",
        ]
    )
    if section.get("optimization"):
        lines.append(
            f"| {L('优化级别', 'Optimization')} | `{cell(section['optimization'])}` |"
        )
    lines.extend(
        [
            f"| {L('覆盖率门槛', 'Coverage gate')} | `{cell(gate.get('threshold'))}%` |",
            f"| {L('实际覆盖率', 'Actual coverage')} | `{_rate_text(gate.get('rate'))}` |",
            f"| {L('是否达标', 'Gate met')} | `{L('通过', 'met') if gate.get('met') else L('未通过', 'not met')}` |",
        ]
    )
    if section.get("coverage_data"):
        lines.append(
            f"| {L('原始覆盖率数据', 'Raw coverage data')} | `{cell(section['coverage_data'])}` |"
        )

    lines.extend(
        [
            "",
            f"## {L('覆盖率总览', 'Coverage summary')}",
            "",
            f"| {L('指标', 'Metric')} | {L('数值', 'Value')} |",
            "|---|---:|",
            f"| {L('补丁可执行行', 'Patch executable lines')} | {summary['patch_executable_lines']} |",
            f"| {L('已覆盖行', 'Covered lines')} | {summary['patch_lines_covered']} |",
            f"| {L('未覆盖行', 'Uncovered lines')} | {summary['patch_lines_uncovered']} |",
            f"| {L('补丁行覆盖率', 'Patch line coverage rate')} | {summary['patch_line_coverage_rate']:.2f}% |",
        ]
    )

    lines.extend(
        [
            "",
            f"## {L('按 Finding 覆盖率', 'Per-finding coverage')}",
            "",
            f"| Finding | {L('类型', 'Type')} | {L('优先级', 'Priority')} | {L('目标', 'Target')} | "
            f"{L('可执行行', 'Executable')} | {L('已覆盖', 'Covered')} | {L('覆盖率', 'Rate')} | "
            f"{L('未覆盖行', 'Uncovered')} | {L('状态', 'Status')} |",
            "|---|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for item in section.get("findings", []):
        meta = finding_meta.get(item.get("finding_id"), {})
        lines.append(
            "| {fid} | {ctype} | {priority} | {target} | {exe} | {cov} | {rate} | {unc} | {status} |".format(
                fid=cell(item.get("finding_id")),
                ctype=cell(meta.get("compatibility_type")),
                priority=cell(meta.get("test_priority")),
                target=cell(coverage_target_text(item, meta)),
                exe=cell(item.get("executable_lines")),
                cov=cell(item.get("covered_lines")),
                rate=_rate_text(item.get("rate")),
                unc=cell(", ".join(item.get("uncovered_lines") or []) or "-"),
                status=cell(meta.get("status")),
            )
        )
    if not section.get("findings"):
        lines.append("| - | - | - | - | - | - | - | - | - |")

    lines.extend(
        [
            "",
            f"## {L('按文件覆盖率', 'Per-file coverage')}",
            "",
            f"| {L('文件', 'File')} | {L('可执行行', 'Executable')} | {L('已覆盖', 'Covered')} | "
            f"{L('覆盖率', 'Rate')} | {L('未覆盖行', 'Uncovered')} |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for item in section.get("files", []):
        lines.append(
            "| {file} | {exe} | {cov} | {rate} | {unc} |".format(
                file=cell(item.get("file")),
                exe=cell(item.get("executable_lines")),
                cov=cell(item.get("covered_lines")),
                rate=_rate_text(item.get("rate")),
                unc=cell(", ".join(item.get("uncovered_lines") or []) or "-"),
            )
        )
    if not section.get("files"):
        lines.append("| - | - | - | - | - |")

    lines.extend(
        [
            "",
            f"## {L('未覆盖行分析', 'Uncovered line analysis')}",
            "",
            f"| {L('位置', 'Location')} | Finding | {L('分类', 'Classification')} | "
            f"{L('根因说明', 'Reason')} | {L('尝试输入', 'Attempted inputs')} |",
            "|---|---|---|---|---|",
        ]
    )
    for item in section.get("uncovered_line_analysis", []):
        classification = classification_labels.get(
            str(item.get("classification")), str(item.get("classification"))
        )
        lines.append(
            "| {loc} | {fid} | {cls} | {reason} | {attempted} |".format(
                loc=cell("%s:%s" % (item.get("file"), item.get("line"))),
                fid=cell(item.get("finding_id")),
                cls=cell(classification),
                reason=cell(item.get("reason")),
                attempted=cell(", ".join(item.get("attempted_inputs") or []) or "-"),
            )
        )
    if not section.get("uncovered_line_analysis"):
        lines.append("| - | - | - | - | - |")

    lines.extend(
        [
            "",
            f"## {L('覆盖率迭代历史', 'Coverage iteration history')}",
            "",
            f"| {L('轮次', 'Round')} | {L('覆盖率', 'Rate')} | {L('变化', 'Delta')} | "
            f"{L('新增输入', 'Inputs added')} | {L('说明', 'Notes')} |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for item in section.get("iterations", []):
        delta = "-"
        rate = item.get("rate")
        before = item.get("rate_before")
        if (
            isinstance(rate, (int, float))
            and not isinstance(rate, bool)
            and isinstance(before, (int, float))
            and not isinstance(before, bool)
        ):
            delta = "%+.2f%%" % (rate - before)
        lines.append(
            "| {round} | {rate} | {delta} | {added} | {notes} |".format(
                round=cell(item.get("round")),
                rate=_rate_text(rate),
                delta=cell(delta),
                added=cell(item.get("inputs_added")),
                notes=cell(item.get("notes")),
            )
        )
    if not section.get("iterations"):
        lines.append("| - | - | - | - | - |")

    lines.extend(["", f"## {L('覆盖率方法与注意事项', 'Coverage method and caveats')}", ""])
    caveats = section.get("caveats") or []
    if caveats:
        lines.extend(f"- {cell(caveat)}" for caveat in caveats)
    else:
        lines.append(L("- 无。", "- None."))

    lines.extend(
        [
            "",
            f"## {L('产物', 'Artifacts')}",
            "",
            f"| {L('产物', 'Artifact')} | {L('路径', 'Path')} |",
            "|---|---|",
        ]
    )
    artifact_rows: list[tuple[str, str]] = []
    if section.get("coverage_data"):
        artifact_rows.append(("coverage_data", str(section["coverage_data"])))
    for key in (
        "execution_results",
        "coverage_data",
        "test_inputs",
        "test_entries",
        "report",
    ):
        value = (data.get("artifacts") or {}).get(key)
        if isinstance(value, str) and value and all(
            value != row[1] for row in artifact_rows
        ):
            artifact_rows.append((key, value))
    if artifact_rows:
        for key, value in artifact_rows:
            lines.append(f"| {cell(key)} | `{cell(value)}` |")
    else:
        lines.append("| - | - |")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate test-summary.json and render TEST_REPORT.md plus the "
            "dedicated COVERAGE_REPORT.md"
        )
    )
    parser.add_argument("summary_json", help="Path to test-summary.json")
    parser.add_argument(
        "--output",
        help="Overall test report path (default <result-dir>/TEST_REPORT.md)",
    )
    parser.add_argument(
        "--coverage-output",
        help="Dedicated coverage report path (default <result-dir>/COVERAGE_REPORT.md)",
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    summary_path = Path(args.summary_json).resolve()
    try:
        data = load_json(summary_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    errors = validate_result(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {summary_path}")
    if args.validate_only:
        return 0

    output_path = (
        Path(args.output).resolve()
        if args.output
        else summary_path.parent / "TEST_REPORT.md"
    )
    coverage_output_path = (
        Path(args.coverage_output).resolve()
        if args.coverage_output
        else summary_path.parent / "COVERAGE_REPORT.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(data), encoding="utf-8")
    coverage_output_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_output_path.write_text(render_coverage_report(data), encoding="utf-8")
    print(f"Report written to: {output_path}")
    print(f"Coverage report written to: {coverage_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
