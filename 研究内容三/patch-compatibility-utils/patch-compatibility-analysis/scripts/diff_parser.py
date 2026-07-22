#!/usr/bin/env python3
"""
Patch Compatibility Analyzer Diff Parser — deterministic static analysis front-end.

Parses a patch/diff file against a target repository and outputs structured
candidates for LLM semantic adjudication.

Usage:
  python3 diff_parser.py \
    --repo /path/to/repo \
    --patch /path/to/patch.diff \
    --profile kernel_6_6 \
    --output /tmp/patch_compatibility_candidates.json

Output: JSON array of candidate objects, each containing:
  - hunk info (file, lines, changed_symbols)
  - signature diff (old/new signatures)
  - contract diff (old/new contracts)
  - behavior diff (old/new behavior summary)
  - api_surface flag
  - context (callers, docs, tests)
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from profile_loader import load_profile


SURFACE_METADATA_KEYS = (
    "analysis_guidance",
    "compatibility_focus",
    "risk_examples",
)


def run(cmd: list[str], cwd: Optional[str] = None) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=60
        )
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


# ---------------------------------------------------------------------------
# 1. Patch parsing
# ---------------------------------------------------------------------------

def parse_patch(patch_path: str) -> list[dict]:
    """Parse a unified diff / patch file into structured hunks."""
    with open(patch_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    hunks = []
    current_file = None
    current_hunk = None

    file_re = re.compile(r"^\+\+\+\s+b/(.*)$")
    hunk_re = re.compile(r"^@@\s+-(\d+),?(\d*)\s+\+(\d+),?(\d*)\s+@@(.*)$")

    lines = content.split("\n")

    for i, line in enumerate(lines):
        # File header
        if line.startswith("--- a/"):
            pass  # handled by the +++ line
        elif line.startswith("+++ b/"):
            m = file_re.match(line)
            if m:
                current_file = m.group(1)
        elif line.startswith("@@") and current_file:
            m = hunk_re.match(line)
            if m:
                old_start = int(m.group(1))
                old_count = int(m.group(2)) if m.group(2) else 1
                new_start = int(m.group(3))
                new_count = int(m.group(4)) if m.group(4) else 1
                context_hint = m.group(5).strip()

                current_hunk = {
                    "file": current_file,
                    "old_start": old_start,
                    "old_end": old_start + old_count - 1,
                    "new_start": new_start,
                    "new_end": new_start + new_count - 1,
                    "context_hint": context_hint,
                    "added_lines": [],
                    "deleted_lines": [],
                    "context_lines": [],
                    "raw_hunk_lines": [],
                }
                hunks.append(current_hunk)
        elif current_hunk is not None:
            current_hunk["raw_hunk_lines"].append(line)
            if line.startswith("+") and not line.startswith("+++"):
                current_hunk["added_lines"].append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                current_hunk["deleted_lines"].append(line[1:])
            elif line.startswith(" ") or line == "":
                current_hunk["context_lines"].append(line[1:])

    return hunks


# ---------------------------------------------------------------------------
# 2. Symbol extraction
# ---------------------------------------------------------------------------

C_FUNC_RE = re.compile(
    r"^\s*([\w\s\*]+)\s+(\w+)\s*\(([^)]*)\)\s*(\{|;)?", re.MULTILINE
)
C_EXPORT_RE = re.compile(r"EXPORT_SYMBOL(_GPL|_NS)?\s*\((\w+)\)")
SYSCALL_RE = re.compile(
    r"\b(?:COMPAT_)?SYSCALL_DEFINE\d*\s*\(|\b__SYSCALL\b|\b__NR_[A-Za-z0-9_]+"
)
IOCTL_RE = re.compile(
    r"\b(?:unlocked_ioctl|compat_ioctl|ioctl)\b|"
    r"\b_IO(?:R|W|WR)?\s*\("
)
NETLINK_RE = re.compile(
    r"\b(?:NETLINK_[A-Za-z0-9_]+|nla_policy|nla_parse|nla_put|genl_family|genl_ops)\b"
)
PROCFS_RE = re.compile(
    r"\b(?:proc_create(?:_data|_seq)?|proc_ops|single_open|seq_printf|seq_puts|seq_putc|seq_read)\b"
)
SYSFS_RE = re.compile(
    r"\b(?:sysfs_create_(?:file|group)|device_create_file|DEVICE_ATTR(?:_RO|_RW)?|__ATTR|sysfs_emit(?:_at)?|kobj_attribute)\b"
)
SYSCTL_RE = re.compile(
    r"\b(?:register_sysctl|unregister_sysctl_table|ctl_table|proc_do(?:intvec|uintvec|string|bool|ulongvec_minmax))\b"
)

PYTHON_FUNC_RE = re.compile(r"^\s*def\s+(\w+)\s*\(([^)]*)\)", re.MULTILINE)
PYTHON_CLASS_RE = re.compile(r"^\s*class\s+(\w+)", re.MULTILINE)

GO_FUNC_RE = re.compile(r"^\s*func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(([^)]*)\)", re.MULTILINE)

RUBY_DEF_RE = re.compile(r"^\s*def\s+(self\.)?(\w+)", re.MULTILINE)

CONTROL_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "return",
    "sizeof",
    "case",
    "do",
    "else",
}


def symbol_from_context_hint(context_hint: str) -> str:
    """Extract a likely enclosing symbol from a unified-diff hunk header."""
    if context_hint:
        type_match = re.search(
            r"\b(struct|union|enum|class)\s+([A-Za-z_]\w*)\b", context_hint
        )
        if type_match:
            return type_match.group(2)

    if not context_hint or "(" not in context_hint:
        return ""
    prefix = context_hint.split("(", 1)[0].strip()
    match = re.search(r"([A-Za-z_]\w*)\s*$", prefix)
    if not match:
        return ""
    name = match.group(1)
    return "" if name in CONTROL_KEYWORDS else name


def extract_c_symbols(repo_path: str, file_path: str) -> list[dict]:
    """Extract C function definitions and exported symbols from a file."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return []

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    symbols = []
    for m in C_FUNC_RE.finditer(content):
        ret_type = m.group(1).strip()
        name = m.group(2)
        params = m.group(3).strip()
        if name in CONTROL_KEYWORDS:
            continue
        line_start = content.count("\n", 0, m.start()) + 1
        symbols.append(
            {
                "name": name,
                "kind": "function",
                "language": "c",
                "line_start": line_start,
                "return_type": ret_type,
                "parameters": params,
                "signature": f"{ret_type} {name}({params})",
            }
        )

    # Exported symbols
    for m in C_EXPORT_RE.finditer(content):
        line_start = content.count("\n", 0, m.start()) + 1
        symbols.append(
            {"name": m.group(2), "kind": "exported_symbol", "language": "c", "line_start": line_start}
        )

    return symbols


def extract_python_symbols(repo_path: str, file_path: str) -> list[dict]:
    """Extract Python function/class definitions."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return []

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    symbols = []
    for m in PYTHON_CLASS_RE.finditer(content):
        line_start = content.count("\n", 0, m.start()) + 1
        symbols.append(
            {"name": m.group(1), "kind": "class", "language": "python", "line_start": line_start}
        )

    for m in PYTHON_FUNC_RE.finditer(content):
        name = m.group(1)
        params = m.group(2).strip()
        line_start = content.count("\n", 0, m.start()) + 1
        symbols.append(
            {
                "name": name,
                "kind": "function",
                "language": "python",
                "line_start": line_start,
                "signature": f"def {name}({params})",
            }
        )

    return symbols


def extract_go_symbols(repo_path: str, file_path: str) -> list[dict]:
    """Extract Go exported functions/types from a file."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return []

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    symbols = []
    for m in GO_FUNC_RE.finditer(content):
        name = m.group(1)
        if name and name[0].isupper():  # exported
            params = m.group(2).strip()
            line_start = content.count("\n", 0, m.start()) + 1
            symbols.append(
                {
                    "name": name,
                    "kind": "function",
                    "language": "go",
                    "line_start": line_start,
                    "exported": True,
                    "signature": f"func {name}({params})",
                }
            )
    return symbols


def extract_ruby_symbols(repo_path: str, file_path: str) -> list[dict]:
    """Extract Ruby method definitions."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return []

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    symbols = []
    for m in RUBY_DEF_RE.finditer(content):
        is_self = m.group(1) is not None
        name = m.group(2)
        line_start = content.count("\n", 0, m.start()) + 1
        symbols.append(
            {
                "name": name,
                "kind": "method",
                "language": "ruby",
                "line_start": line_start,
                "class_method": is_self,
            }
        )
    return symbols


SYMBOL_EXTRACTORS = {
    ".c": extract_c_symbols,
    ".h": extract_c_symbols,
    ".cpp": extract_c_symbols,
    ".cc": extract_c_symbols,
    ".cxx": extract_c_symbols,
    ".py": extract_python_symbols,
    ".go": extract_go_symbols,
    ".rb": extract_ruby_symbols,
}


def extract_symbols(repo_path: str, file_path: str) -> list[dict]:
    """Dispatch to the right extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    extractor = SYMBOL_EXTRACTORS.get(ext)
    if extractor:
        return extractor(repo_path, file_path)
    return []


IDENTIFIER_STOPWORDS = CONTROL_KEYWORDS | {
    "auto",
    "bool",
    "char",
    "const",
    "double",
    "enum",
    "extern",
    "float",
    "int",
    "long",
    "register",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
}


def identifiers_from_changed_lines(hunk: dict) -> list[str]:
    text = "\n".join(hunk.get("added_lines", []) + hunk.get("deleted_lines", []))
    seen: set[str] = set()
    identifiers: list[str] = []
    for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text):
        if name in IDENTIFIER_STOPWORDS or name in seen:
            continue
        seen.add(name)
        identifiers.append(name)
        if len(identifiers) >= 12:
            break
    return identifiers


def select_changed_symbols(hunk: dict, symbols: list[dict], hint_symbol: str) -> list[str]:
    """Return a compact symbol list for a hunk.

    The previous fallback returned every symbol in the file when a hunk header
    had no function context. Large files then produced huge candidate records
    that wasted agent context. Prefer the hunk hint, identifiers changed by the
    hunk, and at most the nearest preceding symbol with line metadata.
    """
    selected: list[str] = []

    def add(value: str) -> None:
        value = (value or "").strip()
        if value and value not in selected:
            selected.append(value)

    add(hint_symbol)
    symbol_names = {item.get("name", "") for item in symbols}
    for identifier in identifiers_from_changed_lines(hunk):
        if identifier in symbol_names or not selected:
            add(identifier)
        elif len(selected) < 6:
            add(identifier)

    line_start = int(hunk.get("new_start") or hunk.get("old_start") or 0)
    with_lines = [
        item
        for item in symbols
        if isinstance(item.get("line_start"), int) and item.get("line_start") <= line_start
        and item.get("name", "") not in CONTROL_KEYWORDS
    ]
    if with_lines:
        nearest = max(with_lines, key=lambda item: item.get("line_start", 0))
        add(nearest.get("name", ""))

    return selected[:20] or ["unknown"]


# ---------------------------------------------------------------------------
# 3. API surface detection
# ---------------------------------------------------------------------------

def is_header_file(file_path: str) -> bool:
    return file_path.endswith((".h", ".hpp", ".hxx", ".hh"))


def is_uapi(file_path: str) -> bool:
    return "include/uapi/" in file_path or "/uapi/" in file_path


def is_exported_symbol(content: str) -> bool:
    return bool(C_EXPORT_RE.search(content))


def is_symbol_version_file(file_path: str) -> bool:
    return file_path.endswith((".map", ".symver", ".sym", ".symbols", ".def", ".exports"))


def is_pkgconfig_file(file_path: str) -> bool:
    return file_path.endswith((".pc", ".pc.in")) or file_path.endswith(
        ("Config.cmake", "Targets.cmake")
    )


def matches(pattern: re.Pattern[str], content: str) -> bool:
    return bool(pattern.search(content))


def is_test_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/").lower()
    parts = [part for part in normalized.split("/") if part]
    if any(part in {"test", "tests", "t", "spec", "testing"} for part in parts):
        return True
    name = parts[-1] if parts else normalized
    return (
        name.startswith("test_")
        or "_test." in name
        or name.endswith("_test.c")
        or name.endswith("_test.cpp")
        or name.endswith("_test.go")
        or name.endswith("_test.py")
    )


def is_config_file(file_path: str) -> bool:
    config_patterns = [".conf", ".cfg", ".ini", "Kconfig", "Makefile", "CMakeLists.txt"]
    return any(file_path.endswith(p) or p in file_path for p in config_patterns)


def is_doc_file(file_path: str) -> bool:
    doc_patterns = ["doc/", "docs/", "man/", "README", "CHANGES", "NEWS", "CHANGELOG"]
    return any(p in file_path.lower() for p in doc_patterns)


def normalize_path(file_path: str) -> str:
    return file_path.replace("\\", "/").lstrip("/")


def _path_matches(pattern: str, file_path: str) -> bool:
    normalized = normalize_path(file_path)
    pattern = normalize_path(pattern)
    return fnmatch.fnmatchcase(normalized, pattern)


def _path_matches_any(patterns: list[str], file_path: str) -> bool:
    return any(_path_matches(pattern, file_path) for pattern in patterns)


def _content_matches(pattern: str, content: str) -> bool:
    if not pattern:
        return False
    try:
        return bool(re.search(pattern, content, re.MULTILINE))
    except re.error:
        literal = pattern.strip("*")
        if "*" in pattern:
            return literal in content
        return pattern in content


def _content_matches_any(patterns: list[str], content: str) -> bool:
    return any(_content_matches(pattern, content) for pattern in patterns)


def _surface_rule_matches(rule: dict, file_path: str, file_content: str) -> bool:
    paths = rule.get("paths") or []
    files = rule.get("files") or []
    patterns = rule.get("patterns") or []
    excludes = rule.get("exclude") or []

    if excludes and _path_matches_any(excludes, file_path):
        return False

    path_hit = _path_matches_any(paths, file_path) if paths else False
    file_hit = _path_matches_any(files, file_path) if files else False
    content_hit = _content_matches_any(patterns, file_content) if patterns else False

    if paths or files or patterns:
        return path_hit or file_hit or content_hit
    return False


def _priority_rank(priority: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(priority, 0)


def detect_api_surface(file_path: str, file_content: str, profile: dict) -> dict:
    """Determine whether a hunk touches profile-declared API surface."""
    legacy = {
        "is_header": is_header_file(file_path),
        "is_uapi": is_uapi(file_path),
        "is_exported": is_exported_symbol(file_content),
        "is_symbol_version": is_symbol_version_file(file_path),
        "is_pkgconfig": is_pkgconfig_file(file_path),
        "is_syscall": matches(SYSCALL_RE, file_content),
        "is_ioctl": matches(IOCTL_RE, file_content),
        "is_netlink": matches(NETLINK_RE, file_content),
        "is_procfs": matches(PROCFS_RE, file_content),
        "is_sysfs": matches(SYSFS_RE, file_content),
        "is_sysctl": matches(SYSCTL_RE, file_content),
        "is_test": is_test_file(file_path),
        "is_config": is_config_file(file_path),
        "is_doc": is_doc_file(file_path),
    }

    matched_surfaces = []
    for name, rule in (profile.get("api_surfaces") or {}).items():
        if isinstance(rule, dict) and _surface_rule_matches(rule, file_path, file_content):
            matched_surface = {
                "name": name,
                "public": rule.get("public", True),
                "test_priority": rule.get("test_priority", "medium"),
                "stability": rule.get("stability", "unknown"),
                "semantic_dimensions": rule.get("semantic_dimensions", []),
                "description": rule.get("description", ""),
            }
            for key in SURFACE_METADATA_KEYS:
                if key in rule:
                    matched_surface[key] = rule.get(key)
            matched_surfaces.append(matched_surface)

    legacy_public_reasons = [
        key
        for key in (
            "is_header",
            "is_uapi",
            "is_exported",
            "is_symbol_version",
            "is_pkgconfig",
            "is_syscall",
            "is_ioctl",
            "is_netlink",
            "is_procfs",
            "is_sysfs",
            "is_sysctl",
        )
        if legacy[key]
    ]

    matched_names = [item["name"] for item in matched_surfaces]
    priority = "low"
    for item in matched_surfaces:
        if _priority_rank(item.get("test_priority", "")) > _priority_rank(priority):
            priority = item.get("test_priority", "medium")

    is_test = legacy["is_test"] or "tests" in matched_names
    is_doc = legacy["is_doc"] or "docs" in matched_names
    public_by_profile = any(item.get("public", True) for item in matched_surfaces)
    public_by_legacy = bool(legacy_public_reasons) if not matched_surfaces else False

    surface = {
        **legacy,
        "matched_surfaces": matched_surfaces,
        "surface_reasons": matched_names or legacy_public_reasons,
        "profile": profile.get("name") or profile.get("profile_metadata", {}).get("requested_profile", ""),
        "effective_profile_layers": profile.get("profile_metadata", {}).get("resolved_extends", []),
        "applied_profile_variants": profile.get("profile_metadata", {}).get("applied_variants", []),
        "surface_test_priority": priority,
        "is_test": is_test,
        "is_doc": is_doc,
    }
    surface["is_public"] = bool(public_by_profile or public_by_legacy) and not is_test and not is_doc
    return surface


# ---------------------------------------------------------------------------
# 4. Context retrieval
# ---------------------------------------------------------------------------

def get_function_context(
    repo_path: str, file_path: str, line_start: int, line_end: int
) -> dict:
    """
    Given a file and line range (from a hunk), extract:
    - The enclosing function name and full source
    - Lines before and after for context
    """
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return {}

    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()

    # Extend range to find enclosing function
    context_before = 30
    context_after = 30
    start = max(0, line_start - context_before)
    end = min(len(all_lines), line_end + context_after)

    snippet_lines = all_lines[start:end]

    # Try to find function name from the context
    func_name = "unknown"
    for line in reversed(all_lines[:line_start]):
        func_match = re.match(r"^\s*[\w\s\*]+\s+(\w+)\s*\([^)]*\)\s*\{?", line)
        if func_match and func_match.group(1) not in CONTROL_KEYWORDS:
            func_name = func_match.group(1)
            break

    return {
        "enclosing_function": func_name,
        "snippet_start_line": start + 1,
        "snippet_end_line": end,
        "snippet": "".join(snippet_lines),
    }


# ---------------------------------------------------------------------------
# 5. Main processing pipeline
# ---------------------------------------------------------------------------

def process_patch(
    repo_path: str,
    patch_path: str,
    profile: str,
) -> tuple[list[dict], dict]:
    """Main pipeline: parse patch, extract symbols, detect API surface,
    retrieve context, and output structured candidates."""

    profile_data = load_profile(profile, repo_path)
    hunks = parse_patch(patch_path)

    candidates = []
    skipped_docs = 0
    for index, hunk in enumerate(hunks, start=1):
        file_path = hunk["file"]

        # Read file content
        full_path = os.path.join(repo_path, file_path)
        file_content = ""
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                file_content = f.read()

        # Get function context
        ctx = get_function_context(
            repo_path, file_path, hunk["old_start"], hunk["new_end"]
        )
        hint_symbol = symbol_from_context_hint(hunk.get("context_hint", ""))
        if hint_symbol:
            ctx["enclosing_function"] = hint_symbol

        surface_content = "\n".join(
            hunk.get("added_lines", [])
            + hunk.get("deleted_lines", [])
            + hunk.get("context_lines", [])
            + [hunk.get("context_hint", ""), ctx.get("snippet", "")]
        )

        # Path rules use the file path; content rules use hunk/function context.
        api_surface = detect_api_surface(file_path, surface_content, profile_data)
        if api_surface["is_doc"]:
            skipped_docs += 1
            continue

        hunk["hunk_id"] = "HUNK-%04d" % index

        # Extract symbols from this file and keep only hunk-local identifiers.
        symbols = extract_symbols(repo_path, file_path)
        hunk["changed_symbols"] = select_changed_symbols(hunk, symbols, hint_symbol)

        hunk["api_surface"] = api_surface

        # Add context
        hunk["context"] = ctx

        # Remove raw hunk lines from output (too verbose)
        hunk.pop("raw_hunk_lines", None)

        candidates.append(hunk)

    metrics = compute_patch_metrics(patch_path, hunks, candidates, skipped_docs)
    return candidates, metrics


def compute_patch_metrics(
    patch_path: str,
    parsed_hunks: list[dict],
    candidates: list[dict],
    skipped_docs: int,
) -> dict:
    text = Path(patch_path).read_text(encoding="utf-8", errors="replace")
    added = 0
    deleted = 0
    context = 0
    for line in text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            deleted += 1
        elif line.startswith(" "):
            context += 1

    surface_counts: dict[str, int] = {}
    public_candidates = 0
    context_bytes = 0
    changed_files = sorted({candidate["file"] for candidate in candidates})
    for candidate in candidates:
        api_surface = candidate.get("api_surface") or {}
        if api_surface.get("is_public"):
            public_candidates += 1
        context_bytes += len((candidate.get("context") or {}).get("snippet", "").encode("utf-8", errors="replace"))
        for item in api_surface.get("matched_surfaces") or []:
            name = item.get("name")
            if name:
                surface_counts[name] = surface_counts.get(name, 0) + 1

    return {
        "patch_bytes": len(text.encode("utf-8", errors="replace")),
        "patch_lines": len(text.splitlines()),
        "diff_added_lines": added,
        "diff_deleted_lines": deleted,
        "diff_context_lines": context,
        "churn": added + deleted,
        "raw_hunks": len(parsed_hunks),
        "candidate_hunks": len(candidates),
        "skipped_doc_hunks": skipped_docs,
        "changed_files": len(changed_files),
        "candidate_context_bytes": context_bytes,
        "public_candidate_hunks": public_candidates,
        "surface_counts": surface_counts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Patch Compatibility Analyzer diff parser"
    )
    parser.add_argument("--repo", required=True, help="Path to target repository")
    parser.add_argument("--patch", required=True, help="Path to patch/diff file")
    parser.add_argument(
        "--profile",
        default="c_project",
        help="Package profile (kernel_6_6, openeuler_24_03, cpython, golang, ruby, dnf, c_project)",
    )
    parser.add_argument(
        "--output",
        default="/tmp/patch_compatibility_candidates.json",
        help="Output JSON file path",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.repo):
        print(f"ERROR: repo path does not exist: {args.repo}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.patch):
        print(f"ERROR: patch file does not exist: {args.patch}", file=sys.stderr)
        sys.exit(1)

    candidates, patch_metrics = process_patch(
        args.repo,
        args.patch,
        args.profile,
    )

    # Build summary
    changed_files = list(set(c["file"] for c in candidates))
    public_candidates = [
        c for c in candidates if c.get("api_surface", {}).get("is_public")
    ]

    output = {
        "repo": os.path.abspath(args.repo),
        "patch_file": os.path.abspath(args.patch),
        "profile": args.profile,
        "summary": {
            "total_changed_files": len(changed_files),
            "changed_files": changed_files,
            "total_hunks": len(candidates),
            "public_api_hunks": len(public_candidates),
            "patch_metrics": patch_metrics,
        },
        "candidates": candidates,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(candidates)} hunks across {len(changed_files)} files")
    print(f"  Public API hunks: {len(public_candidates)}")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
