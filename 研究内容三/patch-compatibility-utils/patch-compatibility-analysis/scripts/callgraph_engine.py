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
    iter_source_files,
)


def build_graph(
    repo: Path,
    language: str,
    target_file: Optional[str],
    max_files: int,
) -> CallGraph:
    parser = None if language == "python" else configure_tree_sitter_parser(language)
    if language != "python" and parser is None:
        return CallGraph()

    graph = CallGraph()
    for path in iter_source_files(repo, language, target_file, max_files=max_files):
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
