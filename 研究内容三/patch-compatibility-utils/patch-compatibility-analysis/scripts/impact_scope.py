#!/usr/bin/env python3
"""Deterministic reverse-dependency (affected scope) builder for PCA findings.

For every confirmed compatibility finding, this script computes the additional
code affected by the change using an AST-only reverse call graph built from the
patched analysis worktree: direct callers, transitive dependents, affected
files, reachable entry points, and test dependents. Results are written to
`affected-scope.json`; with `--apply` they are also attached to each finding as
`affected_scope` in `analysis.json`.

This is best-effort static evidence: macro/type-only changes and dynamic
dispatch may not resolve. Findings that cannot be resolved are marked
`not_available` instead of being silently omitted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from callgraph_engine import build_graph_for_files, find_impact_scope
from callgraph_extractors import parser_available
from callgraph_types import infer_language, iter_source_files

SUPPORTED_LANGUAGES = {"c", "python", "go", "ruby"}
LANGUAGE_ALIASES = {"cpp": "c", "c++": "c"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError("%s: invalid JSON: %s" % (path, exc)) from exc
    if not isinstance(payload, dict):
        raise ValueError("%s: top-level JSON must be an object" % path)
    return payload


def result_dir_for(analysis: Dict[str, Any], analysis_path: Path) -> Path:
    artifact_dir = analysis.get("artifact_dir")
    if isinstance(artifact_dir, str) and artifact_dir.strip():
        return Path(artifact_dir).expanduser().resolve()
    return analysis_path.parent


def language_for_finding(finding: Dict[str, Any]) -> str:
    affected_api = finding.get("affected_api") or {}
    location = finding.get("location") or {}
    language = str(affected_api.get("language") or "").strip().lower()
    language = LANGUAGE_ALIASES.get(language, language)
    if not language:
        language = infer_language(str(location.get("file") or ""))
    return language


def empty_scope(language: str, max_depth: int) -> Dict[str, Any]:
    return {
        "status": "not_available",
        "method": "unavailable",
        "language": language,
        "max_depth": max_depth,
        "direct_callers": [],
        "transitive_dependents": [],
        "affected_files": [],
        "affected_entry_points": [],
        "test_dependents": [],
        "external_dependents": [],
        "summary": "",
        "notes": [],
    }


def collect_language_graphs(
    repo: Path,
    languages: List[str],
    max_files: int,
) -> Dict[str, Dict[str, Any]]:
    infos: Dict[str, Dict[str, Any]] = {}
    for language in sorted(languages):
        info: Dict[str, Any] = {"graph": None, "error": "", "truncated": False}
        if not parser_available(language):
            info["error"] = (
                "tree-sitter parser for %s unavailable; run "
                "check_dependencies.py --include-callgraph --languages %s"
                % (language, language)
            )
            infos[language] = info
            continue
        try:
            files = iter_source_files(repo, language, None, max_files=max_files)
            info["truncated"] = len(files) >= max_files
            info["graph"] = build_graph_for_files(repo, language, files)
        except Exception as exc:  # best-effort static analysis
            info["error"] = "call graph build failed: %s" % str(exc)[:300]
        infos[language] = info
    return infos


def summarize_scope(
    symbol: str,
    status: str,
    scope: Dict[str, Any],
    reason: str,
    zh: bool,
) -> str:
    if status == "not_available":
        if zh:
            return (
                "未能基于 AST 调用图计算 %s 的额外影响范围：%s。"
                "需人工复核直接调用方与下游依赖。" % (symbol, reason)
            )
        return (
            "Could not compute the affected scope of %s from the AST call graph: %s. "
            "Manually verify direct callers and downstream dependencies."
            % (symbol, reason)
        )

    direct = scope["direct_callers"]
    transitive = scope["transitive_dependents"]
    files = scope["affected_files"]
    entries = scope["affected_entry_points"]
    tests = scope["test_dependents"]
    direct_files = {item["file"] for item in direct}
    max_depth = scope["max_depth"]
    if zh:
        summary = (
            "变更符号 %s 的反向依赖分析完成：直接调用方 %d 个（涉及文件 %d 个），"
            "间接依赖 %d 个，额外受影响文件共 %d 个，可达入口点 %d 个，"
            "测试依赖 %d 个；最远追溯深度 %d。"
            % (
                symbol,
                len(direct),
                len(direct_files),
                len(transitive),
                len(files),
                len(entries),
                len(tests),
                max_depth,
            )
        )
        if status == "degraded":
            summary += "（注意：因源码扫描上限或节点上限，调用图可能不完整）"
        return summary

    summary = (
        "Reverse-dependency analysis for %s: %d direct caller(s) in %d file(s), "
        "%d transitive dependent(s), %d additionally affected file(s), "
        "%d reachable entry point(s), %d test dependent(s); maximum traced depth %d."
        % (
            symbol,
            len(direct),
            len(direct_files),
            len(transitive),
            len(files),
            len(entries),
            len(tests),
            max_depth,
        )
    )
    if status == "degraded":
        summary += " (note: source scan or node cap reached; the call graph may be incomplete)"
    return summary


def scope_for_target(
    symbol: str,
    language: str,
    info: Optional[Dict[str, Any]],
    max_depth: int,
    max_nodes: int,
    zh: bool,
) -> Dict[str, Any]:
    scope = empty_scope(language, max_depth)
    if not symbol:
        scope["summary"] = summarize_scope(
            "<unknown>", "not_available", scope, "finding has no symbol", zh
        )
        return scope
    if info is None:
        scope["summary"] = summarize_scope(
            symbol, "not_available", scope, "no call graph available for this language", zh
        )
        return scope
    graph = info.get("graph")
    if graph is None:
        reason = str(info.get("error") or "call graph unavailable")
        scope["notes"].append(reason)
        scope["summary"] = summarize_scope(symbol, "not_available", scope, reason, zh)
        return scope

    found = symbol in graph.defs_by_name or symbol in graph.callers_by_name
    if not found:
        reason = (
            "symbol not found in the AST call graph; it may be a macro, type, "
            "or a change outside the scanned source files"
        )
        scope["notes"].append(reason)
        scope["summary"] = summarize_scope(symbol, "not_available", scope, reason, zh)
        return scope

    result = find_impact_scope(graph, symbol, max_depth=max_depth, max_nodes=max_nodes)
    scope.update(
        {
            "status": "degraded" if (info.get("truncated") or result["truncated"]) else "computed",
            "method": "ast_reverse_callgraph",
            "direct_callers": result["direct_callers"],
            "transitive_dependents": result["transitive_dependents"],
            "affected_files": result["affected_files"],
            "affected_entry_points": result["affected_entry_points"],
            "test_dependents": result["test_dependents"],
        }
    )
    if info.get("truncated"):
        scope["notes"].append(
            "candidate scan hit the --max-files cap; the call graph may be incomplete"
        )
    if result["truncated"]:
        scope["notes"].append(
            "dependent traversal hit the --max-nodes cap; the scope may be incomplete"
        )
    scope["summary"] = summarize_scope(symbol, scope["status"], scope, "", zh)
    return scope


def preserve_agent_fields(new_scope: Dict[str, Any], previous: Any) -> None:
    if not isinstance(previous, dict):
        return
    external = previous.get("external_dependents")
    if isinstance(external, list) and external:
        new_scope["external_dependents"] = external
    notes: List[str] = []
    seen = set()
    for note in list(new_scope.get("notes", [])) + list(previous.get("notes", [])):
        if isinstance(note, str) and note and note not in seen:
            seen.add(note)
            notes.append(note)
    new_scope["notes"] = notes


def build_scopes(
    analysis: Dict[str, Any],
    repo: Path,
    max_depth: int,
    max_nodes: int,
    max_files: int,
    zh: bool,
) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    findings = [item for item in analysis.get("findings", []) if isinstance(item, dict)]
    languages = sorted(
        {
            language
            for language in (language_for_finding(item) for item in findings)
            if language
        }
    )
    supported = [language for language in languages if language in SUPPORTED_LANGUAGES]
    graph_infos = collect_language_graphs(repo, supported, max_files)

    cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
    scopes: Dict[str, Dict[str, Any]] = {}
    for index, finding in enumerate(findings):
        finding_id = str(finding.get("id") or "finding-%d" % (index + 1))
        location = finding.get("location") or {}
        affected_api = finding.get("affected_api") or {}
        symbol = str(location.get("symbol") or affected_api.get("name") or "")
        language = language_for_finding(finding)
        if language in SUPPORTED_LANGUAGES:
            key = (language, symbol)
            if key not in cache:
                cache[key] = scope_for_target(
                    symbol, language, graph_infos.get(language), max_depth, max_nodes, zh
                )
            scopes[finding_id] = json.loads(json.dumps(cache[key]))
        else:
            scope = empty_scope(language, max_depth)
            reason = "unsupported language for AST impact analysis: %s" % (language or "unknown")
            scope["notes"].append(reason)
            scope["summary"] = summarize_scope(
                symbol or "<unknown>", "not_available", scope, reason, zh
            )
            scopes[finding_id] = scope
    return scopes, languages


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build per-finding affected scope (downstream dependencies) from analysis.json"
    )
    parser.add_argument("--analysis", required=True, help="Path to analysis.json")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Attach affected_scope to each finding and update analysis.json",
    )
    parser.add_argument(
        "--output",
        help="Affected-scope artifact path; default <artifact_dir>/affected-scope.json",
    )
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-nodes", type=int, default=200)
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--report-language", default="zh-CN")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analysis_path = Path(args.analysis).expanduser().resolve()
    try:
        analysis = load_json(analysis_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    repo_raw = analysis.get("analysis_repo")
    if not repo_raw:
        print(
            "analysis.json has no analysis_repo; run orchestrator.py --ensure-worktree first",
            file=sys.stderr,
        )
        return 2
    repo = Path(str(repo_raw)).expanduser().resolve()
    if not repo.is_dir():
        print(
            "analysis_repo does not exist: %s; run orchestrator.py --ensure-worktree first"
            % repo,
            file=sys.stderr,
        )
        return 2

    result_dir = result_dir_for(analysis, analysis_path)
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else result_dir / "affected-scope.json"
    )
    zh = str(args.report_language).lower().startswith("zh")

    scopes, languages = build_scopes(
        analysis,
        repo,
        max_depth=args.max_depth,
        max_nodes=args.max_nodes,
        max_files=args.max_files,
        zh=zh,
    )

    payload = {
        "schema_version": "1.0",
        "analysis_json": str(analysis_path),
        "repo": str(repo),
        "max_depth": args.max_depth,
        "max_nodes": args.max_nodes,
        "max_files": args.max_files,
        "languages": languages,
        "findings": scopes,
    }
    write_json(output_path, payload)

    if args.apply:
        try:
            artifact_name = output_path.relative_to(result_dir).as_posix()
        except ValueError:
            artifact_name = str(output_path)
        for finding in analysis.get("findings", []):
            if not isinstance(finding, dict):
                continue
            finding_id = str(finding.get("id") or "")
            if finding_id not in scopes:
                continue
            new_scope = json.loads(json.dumps(scopes[finding_id]))
            preserve_agent_fields(new_scope, finding.get("affected_scope"))
            finding["affected_scope"] = new_scope

        candidate_artifacts = analysis.setdefault("candidate_artifacts", {})
        candidate_artifacts["affected_scope"] = artifact_name
        candidate_artifacts["affected_scope_findings"] = sum(
            1 for scope in scopes.values() if scope.get("status") in {"computed", "degraded"}
        )
        write_json(analysis_path, analysis)

    computed = sum(1 for scope in scopes.values() if scope.get("status") == "computed")
    degraded = sum(1 for scope in scopes.values() if scope.get("status") == "degraded")
    unavailable = len(scopes) - computed - degraded
    print("Affected scope written to: %s" % output_path)
    print(
        "Findings: %d computed, %d degraded, %d not_available"
        % (computed, degraded, unavailable)
    )
    if args.apply:
        print("analysis.json updated: %s" % analysis_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
