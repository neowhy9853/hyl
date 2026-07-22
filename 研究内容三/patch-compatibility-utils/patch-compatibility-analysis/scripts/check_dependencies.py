#!/usr/bin/env python3
"""Dependency checker for Patch Compatibility Analyzer scripts.

Run this before expensive analysis. If a required dependency is missing, the
agent should stop and ask the user whether to install/configure it.
"""

from __future__ import annotations

import argparse
import importlib
import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCRIPTS = [
    "diff_parser.py",
    "profile_loader.py",
    "orchestrator.py",
    "validate_analysis.py",
]
CALLGRAPH_SCRIPTS = [
    "callgraph.py",
    "callgraph_types.py",
    "callgraph_extractors.py",
    "callgraph_engine.py",
]


def parse_languages(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def compile_scripts(include_callgraph: bool) -> List[str]:
    errors: List[str] = []
    names = list(DEFAULT_SCRIPTS)
    if include_callgraph:
        names.extend(CALLGRAPH_SCRIPTS)
    for name in names:
        path = SCRIPT_DIR / name
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append("%s failed to compile: %s" % (name, exc))
    return errors


def check_command_available(command: List[str]) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except Exception as exc:
        return False, str(exc)
    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip()
    return True, result.stdout.strip()


def make_tree_sitter_parser(language: str):
    try:
        from tree_sitter import Language, Parser
    except Exception as exc:
        return None, "missing tree_sitter: %s" % exc

    attempts = []
    try:
        from tree_sitter_language_pack import get_language

        attempts.append(lambda: get_language(language))
    except Exception:
        pass

    try:
        from tree_sitter_languages import get_language

        attempts.append(lambda: get_language(language))
    except Exception:
        pass

    try:
        module = importlib.import_module("tree_sitter_%s" % language)

        def from_module():
            raw = getattr(module, "language")()
            try:
                return Language(raw)
            except TypeError:
                return raw

        attempts.append(from_module)
    except Exception:
        pass

    if not attempts:
        return None, "missing tree-sitter grammar for %s" % language

    for attempt in attempts:
        try:
            lang_obj = attempt()
            parser = Parser()
            if hasattr(parser, "set_language"):
                parser.set_language(lang_obj)
            else:
                parser.language = lang_obj
            return parser, ""
        except Exception as exc:
            last_error = str(exc)

    return None, "could not initialize tree-sitter grammar for %s: %s" % (
        language,
        last_error,
    )


def check_language(language: str) -> Tuple[bool, str]:
    if language == "python":
        return True, "stdlib ast available"
    if language not in {"c", "go", "ruby"}:
        return False, "unsupported language: %s" % language
    parser, error = make_tree_sitter_parser(language)
    if parser is None:
        return False, error
    return True, "tree-sitter parser available"


def run_checks(languages: List[str], include_callgraph: bool) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []
    language_results: Dict[str, Dict[str, object]] = {}

    if sys.version_info < (3, 9):
        errors.append(
            "Python >= 3.9 is required, current is %s.%s.%s"
            % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        )

    git_ok, git_message = check_command_available(["git", "--version"])
    if not git_ok:
        errors.append("git is required for reproducible analysis worktrees: %s" % git_message)

    errors.extend(compile_scripts(include_callgraph))

    if include_callgraph:
        for language in languages:
            ok, message = check_language(language)
            language_results[language] = {"ok": ok, "message": message}
            if not ok:
                errors.append("callgraph %s dependency missing: %s" % (language, message))
    elif languages:
        warnings.append("languages ignored because --include-callgraph was not set")

    return {
        "ok": not errors,
        "python": "%s.%s.%s"
        % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        "git": git_message if git_ok else "",
        "languages": language_results,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check PCA script dependencies")
    parser.add_argument(
        "--languages",
        default="python",
        help="Comma-separated languages needed for callgraph, e.g. c,python",
    )
    parser.add_argument(
        "--include-callgraph",
        action="store_true",
        help="Also check tree-sitter dependencies for requested languages",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_checks(parse_languages(args.languages), args.include_callgraph)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["ok"]:
            print("OK: PCA dependencies satisfied")
        else:
            print("PCA dependency check failed", file=sys.stderr)
            for error in result["errors"]:
                print("ERROR: %s" % error, file=sys.stderr)
            print(
                "Ask the user whether to install/configure the missing dependencies.",
                file=sys.stderr,
            )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
