#!/usr/bin/env python3
"""AST-only static call-chain builder for Patch Compatibility Analyzer.

Python uses the standard-library ast module. C, Go, and Ruby require a
tree-sitter parser; when unavailable this command returns [] quickly. Run
check_dependencies.py before asking for call-chain output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from callgraph_engine import build_graph, find_call_chains
from callgraph_types import infer_language


def write_json_output(path: Optional[str], chains: List[dict]) -> None:
    data = json.dumps(chains, indent=2, ensure_ascii=False)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch Compatibility Analyzer AST-only call-chain builder"
    )
    parser.add_argument("--repo", required=True, help="Target repository path")
    parser.add_argument("--target", required=True, help="Target function/symbol name")
    parser.add_argument("--file", required=True, help="Target file path relative to repo")
    parser.add_argument(
        "--language",
        required=True,
        choices=["auto", "c", "python", "go", "ruby"],
        help="Target language",
    )
    parser.add_argument("--output", help="Output JSON path; stdout when omitted")
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--max-chains", type=int, default=20)
    parser.add_argument("--max-files", type=int, default=5000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        write_json_output(args.output, [])
        return 0

    language = infer_language(args.file) if args.language == "auto" else args.language
    try:
        graph = build_graph(
            repo=repo,
            language=language,
            target_file=args.file,
            max_files=args.max_files,
        )
        chains = find_call_chains(
            graph,
            args.target,
            max_depth=args.max_depth,
            max_chains=args.max_chains,
        )
        write_json_output(args.output, chains)
        return 0
    except Exception as exc:
        print("callgraph warning: %s" % exc, file=sys.stderr)
        write_json_output(args.output, [])
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
