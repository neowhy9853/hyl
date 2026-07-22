#!/usr/bin/env python3
"""Deterministically recommend PCA finding test priorities.

The semantic compatibility decision remains the agent's job. This script only
annotates ``findings[].test_priority`` after final findings exist, using the
effective package profile and candidate-stage API-surface matches as a
deterministic recommendation. It never overwrites the Agent-final priority.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from diff_parser import detect_api_surface  # noqa: E402
from profile_loader import load_profile  # noqa: E402


PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
RANK_PRIORITY = {value: key for key, value in PRIORITY_RANK.items()}
PRIORITIES = set(PRIORITY_RANK)
DISAGREEMENT_REASONS = {
    "opt_out_available",
    "additive_behavior_only",
    "internal_or_test_only",
    "narrow_surface",
    "no_external_observable_break",
    "profile_overmatched",
}

HIGH_VALUE_API_KINDS = {
    "cli_command",
    "cli_option",
    "config_key",
    "env_variable",
    "shared_library_symbol",
    "symbol_version",
    "pkgconfig_module",
    "syscall",
    "ioctl",
    "netlink_family",
    "procfs_entry",
    "sysfs_attribute",
    "sysctl_entry",
    "plugin_api",
    "callback_type",
}

PUBLIC_CODE_API_KINDS = {
    "exported_function",
    "public_function",
    "public_method",
    "public_class",
    "public_header",
    "struct_type",
    "enum_type",
    "macro",
    "daemon_handler",
}

HIGH_IMPACT_COMPATIBILITY_TYPES = {
    "API_SIGNATURE_CHANGE",
    "ABI_CHANGE",
    "INPUT_CONTRACT_CHANGE",
    "RETURN_CONTRACT_CHANGE",
    "ERROR_EXCEPTION_CHANGE",
    "OUTPUT_FORMAT_CHANGE",
    "PROC_SYS_OUTPUT_CHANGE",
    "SYSCALL_SEMANTIC_CHANGE",
    "IOCTL_NETLINK_ABI_CHANGE",
    "CONFIG_CLI_BEHAVIOR_CHANGE",
    "RESOURCE_LIFETIME_CHANGE",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def priority_max(*priorities: str) -> str:
    rank = 1
    for priority in priorities:
        rank = max(rank, PRIORITY_RANK.get(str(priority or ""), 0))
    return RANK_PRIORITY.get(rank, "low")


def normalize_priority(priority: Any, default: str = "low") -> str:
    priority = str(priority or "").lower()
    return priority if priority in PRIORITIES else default


def line_pair(value: Any) -> tuple[int, int] | None:
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    ):
        return int(value[0]), int(value[1])
    return None


def overlaps(a: tuple[int, int] | None, b: tuple[int, int] | None) -> bool:
    if not a or not b:
        return False
    return max(a[0], b[0]) <= min(a[1], b[1])


def candidate_line_pair(candidate: dict[str, Any], prefix: str) -> tuple[int, int] | None:
    start = candidate.get(f"{prefix}_start")
    end = candidate.get(f"{prefix}_end")
    if isinstance(start, int) and isinstance(end, int):
        return start, end
    return None


def finding_text(finding: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "affected_surface",
        "old_behavior",
        "new_behavior",
        "compatibility_reason",
        "why_not_internal_only",
        "test_recommendation",
        "test_priority_reason",
    ):
        value = finding.get(key)
        if value:
            parts.append(str(value))
    affected_api = finding.get("affected_api") or {}
    if isinstance(affected_api, dict):
        parts.extend(str(affected_api.get(key) or "") for key in ("name", "kind", "signature"))
    location = finding.get("location") or {}
    if isinstance(location, dict):
        parts.append(str(location.get("symbol") or ""))
    for evidence in finding.get("evidence") or []:
        if isinstance(evidence, dict):
            parts.append(str(evidence.get("snippet") or ""))
    return "\n".join(part for part in parts if part)


def candidate_match_score(finding: dict[str, Any], candidate: dict[str, Any]) -> int:
    location = finding.get("location") or {}
    if not isinstance(location, dict):
        return 0
    if location.get("file") != candidate.get("file"):
        return 0

    score = 10
    new_lines = line_pair(location.get("new_lines"))
    old_lines = line_pair(location.get("old_lines"))
    if overlaps(new_lines, candidate_line_pair(candidate, "new")):
        score += 8
    if overlaps(old_lines, candidate_line_pair(candidate, "old")):
        score += 6

    symbol = str(location.get("symbol") or "")
    changed_symbols = [str(item) for item in candidate.get("changed_symbols") or []]
    context_symbol = str((candidate.get("context") or {}).get("enclosing_function") or "")
    if symbol and (symbol in changed_symbols or symbol == context_symbol):
        score += 4

    for evidence in finding.get("evidence") or []:
        if not isinstance(evidence, dict) or evidence.get("file") != candidate.get("file"):
            continue
        evidence_lines = line_pair(evidence.get("lines"))
        if overlaps(evidence_lines, candidate_line_pair(candidate, "new")):
            score += 3
        if overlaps(evidence_lines, candidate_line_pair(candidate, "old")):
            score += 2
    return score


def matched_candidates(
    finding: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    scored = []
    for candidate in candidates:
        score = candidate_match_score(finding, candidate)
        if score:
            scored.append((score, candidate))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return []
    best_score = scored[0][0]
    return [candidate for score, candidate in scored if score == best_score or score >= 16]


def surface_summary(api_surface: dict[str, Any]) -> dict[str, Any]:
    matched = []
    for item in api_surface.get("matched_surfaces") or []:
        if not isinstance(item, dict):
            continue
        matched.append(
            {
                "name": item.get("name", ""),
                "test_priority": normalize_priority(item.get("test_priority")),
                "public": bool(item.get("public", True)),
                "description": item.get("description", ""),
            }
        )
    return {
        "is_public": bool(api_surface.get("is_public")),
        "is_test": bool(api_surface.get("is_test")),
        "is_doc": bool(api_surface.get("is_doc")),
        "surface_reasons": api_surface.get("surface_reasons") or [],
        "surface_test_priority": normalize_priority(api_surface.get("surface_test_priority")),
        "matched_surfaces": matched,
    }


def fallback_surface(
    finding: dict[str, Any], profile_name: str, repo_path: str | None
) -> dict[str, Any]:
    location = finding.get("location") or {}
    file_path = str(location.get("file") or "")
    if not file_path or not profile_name:
        return {}
    profile = load_profile(profile_name, repo_path)
    return detect_api_surface(file_path, finding_text(finding), profile)


def compute_priority(
    finding: dict[str, Any],
    candidates: list[dict[str, Any]],
    profile_name: str,
    repo_path: str | None,
) -> dict[str, Any]:
    trace: list[str] = []
    matched = matched_candidates(finding, candidates)
    candidate_surfaces = []
    surface_priority = "low"
    public_surface = False
    test_or_doc_only = False

    for candidate in matched:
        api_surface = candidate.get("api_surface") or {}
        summary = surface_summary(api_surface)
        candidate_surfaces.append(
            {
                "hunk_id": candidate.get("hunk_id"),
                "file": candidate.get("file"),
                "old_lines": [candidate.get("old_start"), candidate.get("old_end")],
                "new_lines": [candidate.get("new_start"), candidate.get("new_end")],
                **summary,
            }
        )
        if summary["is_public"]:
            public_surface = True
            surface_priority = priority_max(surface_priority, summary["surface_test_priority"])
        elif summary["is_test"] or summary["is_doc"]:
            test_or_doc_only = True

    if candidate_surfaces:
        trace.append(
            "candidate_surface_priority=%s from %d matched candidate hunk(s)"
            % (surface_priority, len(candidate_surfaces))
        )
    else:
        fallback = fallback_surface(finding, profile_name, repo_path)
        if fallback:
            fallback_summary = surface_summary(fallback)
            candidate_surfaces.append({"source": "profile_fallback", **fallback_summary})
            public_surface = bool(fallback_summary["is_public"])
            test_or_doc_only = bool(fallback_summary["is_test"] or fallback_summary["is_doc"])
            surface_priority = fallback_summary["surface_test_priority"]
            trace.append("fallback_surface_priority=%s from effective profile" % surface_priority)
        else:
            trace.append("no candidate/profile surface match; defaulting to low baseline")

    affected_api = finding.get("affected_api") or {}
    affected_kind = str(affected_api.get("kind") or "") if isinstance(affected_api, dict) else ""
    compatibility_type = str(finding.get("compatibility_type") or "")
    priority = normalize_priority(surface_priority)

    if test_or_doc_only and not public_surface:
        priority = "low"
        trace.append("matched only test/doc surfaces; priority forced to low")

    if affected_kind in HIGH_VALUE_API_KINDS and compatibility_type in HIGH_IMPACT_COMPATIBILITY_TYPES:
        priority = priority_max(priority, "high")
        trace.append(
            "high-value affected_api.kind=%s with compatibility_type=%s -> high"
            % (affected_kind, compatibility_type)
        )
    elif affected_kind in PUBLIC_CODE_API_KINDS and compatibility_type in {
        "API_SIGNATURE_CHANGE",
        "ABI_CHANGE",
        "INPUT_CONTRACT_CHANGE",
        "RETURN_CONTRACT_CHANGE",
        "ERROR_EXCEPTION_CHANGE",
        "RESOURCE_LIFETIME_CHANGE",
    }:
        priority = priority_max(priority, "high")
        trace.append(
            "public code API kind=%s with contract/signature type=%s -> high"
            % (affected_kind, compatibility_type)
        )
    elif affected_kind in PUBLIC_CODE_API_KINDS and public_surface:
        priority = priority_max(priority, "medium")
        trace.append("public code API kind=%s on public surface -> at least medium" % affected_kind)

    if public_surface and priority == "low":
        priority = "medium"
        trace.append("confirmed finding on public surface -> at least medium")

    return {
        "deterministic_priority": priority,
        "trace": trace,
        "matched_candidate_count": len(matched),
        "matched_surfaces": candidate_surfaces,
    }


def choose_final_priority(
    finding: dict[str, Any], deterministic: str, strict: bool
) -> tuple[str, str, str]:
    decision = finding.get("priority_decision") or {}
    if not isinstance(decision, dict):
        decision = {}
    agent_priority = normalize_priority(finding.get("test_priority"))
    final = agent_priority
    reason = str(decision.get("agent_decision_reason") or finding.get("test_priority_reason") or "").strip()
    return final, "agent_final_with_deterministic_recommendation", reason


def normalize_disagreement_reasons(value: Any) -> tuple[list[str], list[str]]:
    if value is None:
        return [], []
    raw_items = value if isinstance(value, list) else [value]
    valid: list[str] = []
    invalid: list[str] = []
    for raw in raw_items:
        reason = str(raw or "").strip()
        if not reason:
            continue
        if reason in DISAGREEMENT_REASONS:
            if reason not in valid:
                valid.append(reason)
        elif reason not in invalid:
            invalid.append(reason)
    return valid, invalid


def recount_summary(analysis: dict[str, Any]) -> None:
    findings = [item for item in analysis.get("findings") or [] if isinstance(item, dict)]
    summary = analysis.setdefault("summary", {})
    summary["compatibility_changes"] = len(findings)
    summary["high_priority"] = sum(1 for item in findings if item.get("test_priority") == "high")
    summary["medium_priority"] = sum(1 for item in findings if item.get("test_priority") == "medium")
    summary["low_priority"] = sum(1 for item in findings if item.get("test_priority") == "low")


def calibrate(
    analysis: dict[str, Any],
    candidates: list[dict[str, Any]],
    profile_name: str,
    repo_path: str | None,
    strict: bool,
    apply: bool,
) -> dict[str, Any]:
    report_findings = []
    disagreement_count = 0
    for index, finding in enumerate(analysis.get("findings") or []):
        if not isinstance(finding, dict):
            continue
        original_agent_priority = normalize_priority(finding.get("test_priority"))
        computed = compute_priority(finding, candidates, profile_name, repo_path)
        deterministic = computed["deterministic_priority"]
        final, policy, agent_reason = choose_final_priority(finding, deterministic, strict)
        disagreed = final != deterministic
        if disagreed:
            disagreement_count += 1
        existing_decision = finding.get("priority_decision") or {}
        if not isinstance(existing_decision, dict):
            existing_decision = {}
        disagreement_reasons, invalid_disagreement_reasons = normalize_disagreement_reasons(
            existing_decision.get("recommendation_disagreement_reasons")
        )
        missing_disagreement_reasons = bool(disagreed and not disagreement_reasons)

        decision = {
            "agent_priority": original_agent_priority,
            "recommended_priority": deterministic,
            "deterministic_priority": deterministic,
            "final_priority": final,
            "decision_policy": policy,
            "agent_decision_reason": agent_reason,
            "recommendation_disagreed": disagreed,
            "recommendation_disagreement_reasons": disagreement_reasons if disagreed else [],
            "invalid_disagreement_reasons": invalid_disagreement_reasons,
            "missing_disagreement_reasons": missing_disagreement_reasons,
            "deterministic_trace": computed["trace"],
            "matched_candidate_count": computed["matched_candidate_count"],
            "matched_surfaces": computed["matched_surfaces"],
        }
        report_item = {
            "finding_id": finding.get("id") or f"finding[{index}]",
            "location": finding.get("location") or {},
            "compatibility_type": finding.get("compatibility_type"),
            "affected_api": finding.get("affected_api") or {},
            "agent_priority": original_agent_priority,
            "recommended_priority": deterministic,
            "deterministic_priority": deterministic,
            "final_priority": final,
            "decision_policy": policy,
            "recommendation_disagreed": disagreed,
            "recommendation_disagreement_reasons": disagreement_reasons if disagreed else [],
            "invalid_disagreement_reasons": invalid_disagreement_reasons,
            "missing_disagreement_reasons": missing_disagreement_reasons,
            "changed": False,
            "deterministic_trace": computed["trace"],
        }
        report_findings.append(report_item)
        if apply:
            finding["priority_decision"] = decision
            if not finding.get("test_priority_reason"):
                finding["test_priority_reason"] = (
                    "Agent final priority is %s. Deterministic recommendation is %s: %s"
                    % (final, deterministic, "; ".join(computed["trace"]))
                )

    if apply:
        recount_summary(analysis)

    counts = {"high": 0, "medium": 0, "low": 0}
    recommended_counts = {"high": 0, "medium": 0, "low": 0}
    disagreement_reason_counts = {reason: 0 for reason in sorted(DISAGREEMENT_REASONS)}
    missing_disagreement_reason_count = 0
    invalid_disagreement_reason_count = 0
    for item in report_findings:
        counts[item["final_priority"]] += 1
        recommended_counts[item["recommended_priority"]] += 1
        if item.get("missing_disagreement_reasons"):
            missing_disagreement_reason_count += 1
        invalid_disagreement_reason_count += len(item.get("invalid_disagreement_reasons") or [])
        for reason in item.get("recommendation_disagreement_reasons") or []:
            disagreement_reason_counts[reason] += 1

    return {
        "profile": profile_name,
        "repo": repo_path or analysis.get("repo", ""),
        "strict": strict,
        "applied": apply,
        "finding_count": len(report_findings),
        "changed_priority_count": 0,
        "recommendation_disagreement_count": disagreement_count,
        "allowed_disagreement_reasons": sorted(DISAGREEMENT_REASONS),
        "disagreement_reason_counts": disagreement_reason_counts,
        "missing_disagreement_reason_count": missing_disagreement_reason_count,
        "invalid_disagreement_reason_count": invalid_disagreement_reason_count,
        "final_priority_counts": counts,
        "recommended_priority_counts": recommended_counts,
        "findings": report_findings,
    }


def load_candidates(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.is_file():
        return []
    data = load_json(path)
    if isinstance(data, dict):
        return [item for item in data.get("candidates") or [] if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def infer_profile(analysis: dict[str, Any], explicit: str | None) -> str:
    if explicit:
        return explicit
    for key in ("package_profile", "profile"):
        value = analysis.get(key)
        if value:
            return str(value)
    return "c_project"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate PCA finding test priorities")
    parser.add_argument("--analysis", required=True, help="Path to analysis.json")
    parser.add_argument("--candidates", help="Path to candidates.json")
    parser.add_argument("--profile", help="Effective profile name")
    parser.add_argument("--repo", help="Repository path used for profile variant detection")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Annotate analysis.json with deterministic priority recommendations without changing agent final test_priority",
    )
    parser.add_argument(
        "--allow-agent-override",
        action="store_true",
        help="Backward-compatible no-op; Agent-final findings[].test_priority is always preserved",
    )
    parser.add_argument("--report", help="Write priority calibration report JSON")
    args = parser.parse_args()

    analysis_path = Path(args.analysis)
    analysis = load_json(analysis_path)
    result_dir = analysis_path.parent
    candidates_path = Path(args.candidates) if args.candidates else result_dir / "candidates.json"
    candidates = load_candidates(candidates_path)
    profile_name = infer_profile(analysis, args.profile)
    strict = not args.allow_agent_override
    report = calibrate(
        analysis=analysis,
        candidates=candidates,
        profile_name=profile_name,
        repo_path=args.repo or analysis.get("repo"),
        strict=strict,
        apply=args.apply,
    )

    report_path = Path(args.report) if args.report else result_dir / "priority-calibration-report.json"
    write_json(report_path, report)
    if args.apply:
        write_json(analysis_path, analysis)
    print(
        "priority_calibration=%s findings=%d changed=%d counts=%s"
        % (
            report_path,
            report["finding_count"],
            report["changed_priority_count"],
            report["final_priority_counts"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
