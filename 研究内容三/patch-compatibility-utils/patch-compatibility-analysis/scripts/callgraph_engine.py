#!/usr/bin/env python3
"""Call-graph engine for Patch Compatibility Analyzer."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from callgraph_extractors import configure_tree_sitter_parser, extract_functions
from callgraph_types import (
    CallGraph,
    ENTRY_KIND_PRIORITY,
    FunctionInfo,
    candidate_call_names,
    is_test_function,
    iter_source_files,
)


def build_graph(
    repo: Path,
    language: str,
    target_file: Optional[str],
    max_files: int,
) -> CallGraph:
    files = iter_source_files(repo, language, target_file, max_files=max_files)
    return build_graph_for_files(repo, language, files)


def build_graph_for_files(repo: Path, language: str, files: List[Path]) -> CallGraph:
    parser = None if language == "python" else configure_tree_sitter_parser(language)
    if language != "python" and parser is None:
        return CallGraph()

    graph = CallGraph()
    for path in files:
        for fn in extract_functions(path, repo, language, parser):
            graph.add_function(fn)
    return graph


def find_call_chains(
    graph: CallGraph,
    target: str,
    max_depth: int = 6,
    max_chains: int = 20,
) -> List[Dict[str, object]]:
    chains: List[Dict[str, object]] = []
    seen_chains: Set[Tuple[str, ...]] = set()
    queue = deque()  # type: deque[Tuple[str, List[str], Set[str]]]

    start_names = {target}
    for key in graph.defs_by_name.get(target, []):
        fn = graph.functions[key]
        start_names.add(fn.name)
        start_names.add(fn.qualname)

    for name in start_names:
        queue.append((name, [target], set()))

    while queue and len(chains) < max_chains:
        current_name, suffix, visited = queue.popleft()
        for caller_key in sorted(graph.callers_by_name.get(current_name, [])):
            if caller_key in visited:
                continue
            caller = graph.functions[caller_key]
            new_suffix = [caller.chain_name] + suffix
            chain_tuple = tuple(new_suffix)
            if caller.entry_kind and chain_tuple not in seen_chains:
                seen_chains.add(chain_tuple)
                chains.append(
                    {
                        "entry_kind": caller.entry_kind,
                        "entry": caller.entry_label,
                        "chain": new_suffix,
                    }
                )
                if len(chains) >= max_chains:
                    break
            if len(new_suffix) <= max_depth:
                next_visited = set(visited)
                next_visited.add(caller_key)
                queue.append((caller.name, new_suffix, next_visited))
                if caller.qualname != caller.name:
                    queue.append((caller.qualname, new_suffix, next_visited))

    chains.sort(
        key=lambda item: (
            ENTRY_KIND_PRIORITY.get(str(item["entry_kind"]), 99),
            len(item["chain"]),  # type: ignore[arg-type]
            str(item["entry"]),
        )
    )
    return chains[:max_chains]


def _matching_call_lines(fn: FunctionInfo, callee_names: Set[str]) -> List[int]:
    lines: Set[int] = set()
    for site_name, site_lines in fn.call_sites.items():
        if callee_names & candidate_call_names(site_name):
            lines.update(site_lines)
    return sorted(lines)


def find_impact_scope(
    graph: CallGraph,
    target: str,
    max_depth: int = 3,
    max_nodes: int = 200,
) -> Dict[str, object]:
    """Reverse-closure of functions that depend on `target`.

    Walks `callers_by_name` upward from the target function, classifying every
    caller found at distance 1 as a direct caller and deeper callers as
    transitive dependents. The target's own definitions seed `visited`, so
    recursive self-calls are not reported as additional affected code.
    """
    definition_keys = list(graph.defs_by_name.get(target, []))
    target_keys = set(definition_keys)
    seed_names: Set[str] = {target}
    for key in definition_keys:
        fn = graph.functions[key]
        seed_names.add(fn.name)
        seed_names.add(fn.qualname)

    direct: List[Dict[str, object]] = []
    transitive: List[Dict[str, object]] = []
    visited: Set[str] = set(target_keys)
    queue: deque = deque((name, 0) for name in sorted(seed_names))
    truncated = False
    recorded = 0

    while queue:
        current_name, distance = queue.popleft()
        if distance >= max_depth:
            continue
        for caller_key in sorted(graph.callers_by_name.get(current_name, [])):
            if caller_key in visited:
                continue
            caller = graph.functions.get(caller_key)
            if caller is None:
                continue
            visited.add(caller_key)
            recorded += 1
            if recorded > max_nodes:
                truncated = True
                break
            record = {
                "file": caller.file,
                "symbol": caller.name,
                "qualname": caller.qualname,
                "line": caller.start_line,
                "call_lines": _matching_call_lines(
                    caller, candidate_call_names(current_name)
                ),
                "entry_kind": caller.entry_kind,
                "is_test": is_test_function(caller),
            }
            if distance == 0:
                direct.append(record)
            else:
                deeper = dict(record)
                deeper["depth"] = distance + 1
                transitive.append(deeper)
            if distance + 1 < max_depth:
                queue.append((caller.name, distance + 1))
                if caller.qualname != caller.name:
                    queue.append((caller.qualname, distance + 1))
        if truncated:
            break

    affected_files: Dict[str, Dict[str, object]] = {}
    entry_kinds_by_file: Dict[str, Set[str]] = {}
    for record in direct + transitive:
        file_path = str(record["file"])
        info = affected_files.setdefault(
            file_path,
            {
                "file": file_path,
                "dependent_count": 0,
                "max_depth": 0,
            },
        )
        info["dependent_count"] = int(info["dependent_count"]) + 1
        depth = int(record.get("depth", 1))  # type: ignore[arg-type]
        if depth > int(info["max_depth"]):
            info["max_depth"] = depth
        entry_kind = str(record.get("entry_kind") or "")
        if entry_kind:
            entry_kinds_by_file.setdefault(file_path, set()).add(entry_kind)

    files_out = [
        {
            "file": info["file"],
            "dependent_count": info["dependent_count"],
            "max_depth": info["max_depth"],
            "entry_kinds": sorted(entry_kinds_by_file.get(str(info["file"]), set())),
        }
        for info in affected_files.values()
    ]
    files_out.sort(key=lambda item: (-int(item["dependent_count"]), str(item["file"])))

    entry_points = [
        {
            "entry_kind": record["entry_kind"],
            "entry": "%s::%s" % (record["file"], record["qualname"]),
            "file": record["file"],
            "symbol": record["symbol"],
            "depth": int(record.get("depth", 1)),  # type: ignore[arg-type]
        }
        for record in direct + transitive
        if record.get("entry_kind")
    ]
    entry_points.sort(
        key=lambda item: (str(item["entry_kind"]), str(item["entry"]), int(item["depth"]))
    )

    test_dependents = [
        {
            "file": record["file"],
            "symbol": record["symbol"],
            "line": record["line"],
            "depth": int(record.get("depth", 1)),  # type: ignore[arg-type]
        }
        for record in direct + transitive
        if record.get("is_test")
    ]
    test_dependents.sort(
        key=lambda item: (
            int(item["depth"]),
            str(item["file"]),
            int(item["line"]),
            str(item["symbol"]),
        )
    )

    direct.sort(key=lambda item: (str(item["file"]), int(item["line"]), str(item["symbol"])))
    transitive.sort(
        key=lambda item: (
            int(item.get("depth", 1)),  # type: ignore[arg-type]
            str(item["file"]),
            int(item["line"]),
            str(item["symbol"]),
        )
    )

    return {
        "direct_callers": direct,
        "transitive_dependents": transitive,
        "affected_files": files_out,
        "affected_entry_points": entry_points,
        "test_dependents": test_dependents,
        "truncated": truncated,
        "recorded_nodes": recorded,
    }
