#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile
import time

from analysis_core import (
    AnalysisError,
    changed_lines,
    fallback_symbols,
    find_ctags,
    map_changed_symbols,
    materialize_files,
    resolve_commit,
    resolve_repo,
)
from analysis_core.ctags import extract_symbols as ctags_symbols
from common import SKILL_DIR, emit, fail_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map changed lines in a Git commit to nearby symbols.")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--max-files", type=int, default=40)
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_files < 1:
        fail_analysis(AnalysisError("E_INVALID_ARGUMENT", "max-files must be positive"))
    if args.timeout <= 0:
        fail_analysis(AnalysisError("E_INVALID_ARGUMENT", "timeout must be positive"))

    started = time.monotonic()
    try:
        repo = resolve_repo(args.repo, timeout=min(args.timeout, 5.0))
        commit = resolve_commit(repo, args.commit, timeout=min(args.timeout, 5.0))
        files = changed_lines(repo, commit, timeout=args.timeout)[: args.max_files]
        warnings: list[str] = []

        with tempfile.TemporaryDirectory(prefix="commit-analysis-") as raw:
            root = Path(raw)
            present, materialize_warnings = materialize_files(
                repo,
                commit,
                files,
                root,
                timeout=args.timeout,
            )
            warnings.extend(materialize_warnings)
            ctags = find_ctags(SKILL_DIR)
            backend = "fallback"
            if ctags.compatible and ctags.executable:
                try:
                    symbols = ctags_symbols(ctags.executable, root, present, timeout=args.timeout)
                    backend = f"universal-ctags:{ctags.source}"
                except AnalysisError as error:
                    warnings.append(f"{error.code}: {error.message}")
                    symbols, fallback_warnings = fallback_symbols(root, present)
                    warnings.extend(fallback_warnings)
            else:
                warning = (
                    "INCOMPATIBLE_CTAGS: Universal Ctags JSON output is required"
                    if ctags.executable
                    else "CTAGS_UNAVAILABLE"
                )
                warnings.append(warning)
                symbols, fallback_warnings = fallback_symbols(root, present)
                warnings.extend(fallback_warnings)

            precisions = {symbol.precision for symbol in symbols}
            if not precisions:
                precision = "unknown"
            elif len(precisions) == 1:
                precision = next(iter(precisions))
            else:
                precision = "mixed"

            emit(
                {
                    "ok": True,
                    "tool": "patch_symbol_map",
                    "version": "v1",
                    "repository": str(repo),
                    "commit_id": commit,
                    "backend": backend,
                    "precision": precision,
                    "files": [item.as_dict() for item in present],
                    "changed_symbols": map_changed_symbols(present, symbols),
                    "warnings": warnings,
                    "stats": {
                        "elapsed_ms": int((time.monotonic() - started) * 1000),
                        "scanned_files": len(present),
                        "returned_items": len(symbols),
                    },
                }
            )
    except AnalysisError as error:
        fail_analysis(error)
    except subprocess.TimeoutExpired:
        fail_analysis(AnalysisError("E_ANALYSIS_TIMEOUT", "analysis timed out"))


if __name__ == "__main__":
    main()
