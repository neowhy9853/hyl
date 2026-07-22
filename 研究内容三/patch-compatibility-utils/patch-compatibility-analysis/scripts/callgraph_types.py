#!/usr/bin/env python3
"""Shared types and path helpers for PCA call-graph construction."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


LANGUAGE_EXTENSIONS = {
    "c": {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh"},
    "python": {".py"},
    "go": {".go"},
    "ruby": {".rb"},
}

TREE_SITTER_NAMES = {
    "c": "c",
    "go": "go",
    "ruby": "ruby",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "build",
    "dist",
    "node_modules",
    "vendor",
}

ENTRY_KIND_PRIORITY = {
    "test_entry": 0,
    "cli_entry": 1,
    "http_handler": 2,
    "config_parser": 3,
    "plugin_callback": 4,
    "exported_api": 5,
    "syscall": 6,
    "ioctl": 7,
    "netlink": 8,
    "procfs": 9,
    "sysfs": 10,
    "sysctl": 11,
    "daemon_handler": 12,
}


@dataclass
class FunctionInfo:
    name: str
    qualname: str
    file: str
    start_line: int
    end_line: int
    language: str
    is_static: bool = False
    calls: Set[str] = field(default_factory=set)
    entry_kind: str = ""

    @property
    def key(self) -> str:
        return "%s::%s@%s" % (self.file, self.qualname, self.start_line)

    @property
    def chain_name(self) -> str:
        return self.qualname or self.name

    @property
    def entry_label(self) -> str:
        return "%s::%s" % (self.file, self.qualname.replace(".", "::"))


@dataclass
class CallGraph:
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)
    callers_by_name: Dict[str, Set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    defs_by_name: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    def add_function(self, fn: FunctionInfo) -> None:
        self.functions[fn.key] = fn
        self.defs_by_name[fn.name].append(fn.key)
        self.defs_by_name[fn.qualname].append(fn.key)
        for call in fn.calls:
            for name in candidate_call_names(call):
                self.callers_by_name[name].add(fn.key)


def candidate_call_names(name: str) -> Set[str]:
    clean = name.strip()
    if not clean:
        return set()
    names = {clean}
    for sep in ("::", ".", "->"):
        if sep in clean:
            names.add(clean.split(sep)[-1])
    return {item for item in names if item}


def normalize_path(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def infer_language(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    for language, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return language
    return "c"


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def iter_source_files(
    repo: Path,
    language: str,
    target_file: Optional[str] = None,
    max_files: int = 5000,
) -> List[Path]:
    exts = LANGUAGE_EXTENSIONS.get(language, set())
    files: List[Path] = []
    target_path = (repo / target_file).resolve() if target_file else None

    if target_path and target_path.exists():
        files.append(target_path)

    for root, dirs, names in os.walk(str(repo)):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        root_path = Path(root)
        for name in names:
            path = root_path / name
            if path.suffix.lower() not in exts:
                continue
            resolved = path.resolve()
            if target_path and resolved == target_path:
                continue
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def is_test_path(file_path: str) -> bool:
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
        or name.endswith("_test.rb")
        or name.endswith("_spec.rb")
    )


def is_test_function(fn: FunctionInfo) -> bool:
    name = fn.name.lower()
    qual = fn.qualname.lower()
    if fn.language == "python":
        return name.startswith("test") or ".test" in qual
    if fn.language == "go":
        return name.startswith(("test", "benchmark", "example"))
    if fn.language == "ruby":
        return name.startswith("test_") or "spec" in fn.file.lower()
    return name.startswith("test") or "test" in name


def classify_entry(fn: FunctionInfo) -> str:
    name = fn.name
    lower_name = name.lower()
    lower_file = fn.file.lower()

    if is_test_path(fn.file) and is_test_function(fn):
        return "test_entry"
    if name in {"main", "cmd_main", "handle_main"} or lower_name.endswith("_main"):
        return "cli_entry"
    if (
        "handler" in lower_name
        or lower_name.startswith("serve_")
        or lower_name.startswith("route_")
        or "http" in lower_file
    ):
        return "http_handler"
    if (
        "config" in lower_name
        and ("parse" in lower_name or "read" in lower_name or "load" in lower_name)
    ):
        return "config_parser"
    if (
        lower_name.startswith("plugin_")
        or lower_name.endswith("_callback")
        or lower_name.endswith("_hook")
        or lower_name in {"module_init", "init_module"}
    ):
        return "plugin_callback"
    if lower_name.startswith(("sys_", "syscall_")):
        return "syscall"
    if "ioctl" in lower_name:
        return "ioctl"
    if "netlink" in lower_name:
        return "netlink"
    if "proc" in lower_name and ("show" in lower_name or "read" in lower_name):
        return "procfs"
    if "sysfs" in lower_name or lower_name.endswith(("_show", "_store")):
        return "sysfs"
    if "sysctl" in lower_name:
        return "sysctl"
    if (
        "dbus" in lower_name
        or "signal" in lower_name
        or "admin" in lower_name
        or "daemon" in lower_file
    ):
        return "daemon_handler"
    if fn.language == "go" and name[:1].isupper():
        return "exported_api"
    if fn.language == "python" and not name.startswith("_") and not is_test_path(fn.file):
        return "exported_api"
    if fn.language == "c" and not fn.is_static and not is_test_path(fn.file):
        return "exported_api"
    if fn.language == "ruby" and not name.startswith("_") and not is_test_path(fn.file):
        return "exported_api"
    return ""
