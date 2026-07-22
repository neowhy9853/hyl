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
]

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate test-summary.json and render COVERAGE_REPORT.md"
    )
    parser.add_argument("summary_json", help="Path to test-summary.json")
    parser.add_argument("--output", help="Markdown output path")
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
        else summary_path.parent / "COVERAGE_REPORT.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(data), encoding="utf-8")
    print(f"Report written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
