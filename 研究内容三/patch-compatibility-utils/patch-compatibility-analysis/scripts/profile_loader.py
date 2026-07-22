#!/usr/bin/env python3
"""Profile loader for Patch Compatibility Analyzer package profiles.

Profiles can be plain package YAML files, or composable profiles with:

  extends:
    - default
    - c_family
  variants:
    openeuler:
      detect:
        remotes:
          - '*atomgit.com/openeuler*'
      overlay:
        api_surfaces: ...

The loader resolves a deterministic "effective profile" by deep-merging base
profiles, the package profile, and matching variant overlays. This keeps common
API-surface rules in reusable layers instead of copying them into every package
profile.
"""

from __future__ import annotations

import copy
import fnmatch
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

try:
    import yaml

    def _load_yaml(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _dump_yaml(data: dict) -> str:
        return yaml.dump(data, default_flow_style=False)

except ImportError:
    def _parse_scalar(value: str) -> object:
        value = value.strip()
        if not value:
            return ""
        if value in {"true", "True"}:
            return True
        if value in {"false", "False"}:
            return False
        if value in {"null", "Null", "~"}:
            return None
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        return value

    def _strip_comment(line: str) -> str:
        in_single = False
        in_double = False
        for i, ch in enumerate(line):
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "#" and not in_single and not in_double:
                return line[:i].rstrip()
        return line.rstrip()

    def _prepare_lines(text: str) -> list[tuple[int, str]]:
        prepared = []
        raw_lines = text.splitlines()
        i = 0
        while i < len(raw_lines):
            raw = raw_lines[i].rstrip("\n")
            stripped_comment = _strip_comment(raw)
            stripped = stripped_comment.strip()
            if not stripped:
                i += 1
                continue
            indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
            prepared.append((indent, stripped))
            i += 1
        return prepared

    def _parse_block_scalar(
        raw_lines: list[str], start_index: int, parent_indent: int
    ) -> tuple[str, int]:
        block_lines = []
        i = start_index
        while i < len(raw_lines):
            raw = raw_lines[i].rstrip("\n")
            if not raw.strip():
                block_lines.append("")
                i += 1
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent <= parent_indent:
                break
            block_lines.append(raw[parent_indent + 2 :])
            i += 1
        return "\n".join(block_lines).rstrip(), i

    def _parse_simple_yaml(text: str) -> dict:
        """Parse the YAML subset used by bundled package profiles."""
        raw_lines = text.splitlines()

        def next_content_index(index: int) -> int:
            while index < len(raw_lines):
                raw = _strip_comment(raw_lines[index])
                if raw.strip():
                    return index
                index += 1
            return index

        def parse_mapping(index: int, indent: int) -> tuple[dict, int]:
            mapping = {}
            while index < len(raw_lines):
                index = next_content_index(index)
                if index >= len(raw_lines):
                    break
                raw = _strip_comment(raw_lines[index])
                current_indent = len(raw) - len(raw.lstrip(" "))
                stripped = raw.strip()
                if current_indent < indent:
                    break
                if current_indent > indent or stripped.startswith("- "):
                    break
                key, sep, value = stripped.partition(":")
                if not sep:
                    index += 1
                    continue
                key = key.strip()
                value = value.strip()
                if value in {"|", ">"}:
                    parsed, index = _parse_block_scalar(
                        raw_lines, index + 1, current_indent
                    )
                    mapping[key] = parsed
                    continue
                if value:
                    mapping[key] = _parse_scalar(value)
                    index += 1
                    continue
                child_index = next_content_index(index + 1)
                if child_index >= len(raw_lines):
                    mapping[key] = {}
                    index = child_index
                    continue
                child_raw = _strip_comment(raw_lines[child_index])
                child_indent = len(child_raw) - len(child_raw.lstrip(" "))
                child_stripped = child_raw.strip()
                if child_indent <= current_indent:
                    mapping[key] = {}
                    index += 1
                elif child_stripped.startswith("- "):
                    mapping[key], index = parse_list(child_index, child_indent)
                else:
                    mapping[key], index = parse_mapping(child_index, child_indent)
            return mapping, index

        def parse_list(index: int, indent: int) -> tuple[list, int]:
            items = []
            while index < len(raw_lines):
                index = next_content_index(index)
                if index >= len(raw_lines):
                    break
                raw = _strip_comment(raw_lines[index])
                current_indent = len(raw) - len(raw.lstrip(" "))
                stripped = raw.strip()
                if current_indent < indent or not stripped.startswith("- "):
                    break
                value = stripped[2:].strip()
                if value:
                    items.append(_parse_scalar(value))
                    index += 1
                else:
                    child_index = next_content_index(index + 1)
                    if child_index >= len(raw_lines):
                        items.append(None)
                        index = child_index
                        continue
                    child_raw = _strip_comment(raw_lines[child_index])
                    child_indent = len(child_raw) - len(child_raw.lstrip(" "))
                    child_stripped = child_raw.strip()
                    if child_stripped.startswith("- "):
                        item, index = parse_list(child_index, child_indent)
                    else:
                        item, index = parse_mapping(child_index, child_indent)
                    items.append(item)
            return items, index

        parsed, _ = parse_mapping(0, 0)
        return parsed

    def _load_yaml(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return _parse_simple_yaml(f.read())

    def _dump_yaml(data: dict) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)


_PROFILES_DIR = Path(__file__).parent.parent / "profiles"

_RAW_PROFILE_CACHE: dict[str, dict] = {}
_PROFILE_INDEX_CACHE: Optional[dict[str, Path]] = None


def profile_index() -> dict[str, Path]:
    """Return profile name -> YAML path for all layered profile directories."""
    global _PROFILE_INDEX_CACHE
    if _PROFILE_INDEX_CACHE is not None:
        return dict(_PROFILE_INDEX_CACHE)

    index: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}
    for path in sorted(_PROFILES_DIR.rglob("*.yaml")):
        name = path.stem
        if name in index:
            duplicates.setdefault(name, [index[name]]).append(path)
            continue
        index[name] = path
    if duplicates:
        detail = "; ".join(
            "%s: %s" % (name, ", ".join(str(path) for path in paths))
            for name, paths in sorted(duplicates.items())
        )
        raise RuntimeError("duplicate profile names found: %s" % detail)

    _PROFILE_INDEX_CACHE = index
    return dict(index)


def profile_path(name: str) -> Path:
    index = profile_index()
    if name not in index:
        available = ", ".join(sorted(index))
        raise FileNotFoundError("Profile not found: %s. Available: %s" % (name, available))
    return index[name]


def _dedupe_list(items: list) -> list:
    seen = set()
    output = []
    for item in items:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, (dict, list)) else item
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def _apply_removals(target: dict, removals: dict) -> None:
    for key, values in removals.items():
        if key not in target:
            continue
        if isinstance(target[key], dict) and isinstance(values, list):
            for value in values:
                target[key].pop(value, None)
        elif isinstance(target[key], list) and isinstance(values, list):
            remove_keys = set(values)
            target[key] = [item for item in target[key] if item not in remove_keys]


def deep_merge(base: dict, overlay: dict) -> dict:
    """Merge profile dictionaries.

    Dict values merge recursively. List values append with stable de-duplication.
    A mapping may contain ``override: true`` to replace the base mapping at that
    key. A top-level or nested ``remove`` mapping can delete keys/list values
    from the already-merged base.
    """
    result = copy.deepcopy(base)
    overlay = copy.deepcopy(overlay or {})

    removals = overlay.pop("remove", None)
    if isinstance(removals, dict):
        _apply_removals(result, removals)

    for key, value in overlay.items():
        if key in {"extends", "variants"}:
            continue
        current = result.get(key)
        if isinstance(value, dict) and value.pop("override", False):
            result[key] = value
        elif isinstance(current, dict) and isinstance(value, dict):
            result[key] = deep_merge(current, value)
        elif isinstance(current, list) and isinstance(value, list):
            result[key] = _dedupe_list(current + value)
        else:
            result[key] = value
    return result


def load_raw_profile(name: str) -> dict:
    """Load a profile YAML file by name without resolving extends/variants."""
    if name in _RAW_PROFILE_CACHE:
        return copy.deepcopy(_RAW_PROFILE_CACHE[name])

    path = profile_path(name)
    profile = _load_yaml(path)
    if profile is None:
        profile = {}

    _RAW_PROFILE_CACHE[name] = profile
    return copy.deepcopy(profile)


def _run_git(repo_path: str, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def repo_facts(repo_path: Optional[str]) -> dict:
    if not repo_path:
        return {"path": "", "branch": "", "remotes": []}
    repo = str(Path(repo_path).resolve())
    branch = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    remotes = []
    for line in _run_git(repo, ["remote", "-v"]).splitlines():
        parts = line.split()
        if len(parts) >= 2:
            remotes.append(parts[1])
    return {"path": repo, "branch": branch, "remotes": sorted(set(remotes))}


def _matches_any(value: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(value, pattern) for pattern in patterns)


def variant_matches(variant: dict, facts: dict) -> bool:
    detect = variant.get("detect") or {}
    if not detect:
        return False

    branches = detect.get("branches") or []
    if branches and not _matches_any(facts.get("branch", ""), branches):
        return False

    remotes = detect.get("remotes") or []
    if remotes and not any(_matches_any(remote, remotes) for remote in facts.get("remotes", [])):
        return False

    paths = detect.get("paths") or []
    if paths:
        repo = Path(facts.get("path") or "")
        if not repo.exists():
            return False
        if not all(any(repo.glob(pattern)) for pattern in paths):
            return False

    return True


def resolve_profile(name: str, repo_path: Optional[str] = None, stack: Optional[list[str]] = None) -> dict:
    """Resolve extends and matching variants into one effective profile."""
    stack = stack or []
    if name in stack:
        raise ValueError("cyclic profile extends: %s -> %s" % (" -> ".join(stack), name))

    raw = load_raw_profile(name)
    merged: dict = {}
    for parent in raw.get("extends") or []:
        merged = deep_merge(merged, resolve_profile(str(parent), repo_path, stack + [name]))

    merged = deep_merge(merged, raw)
    facts = repo_facts(repo_path)
    applied_variants = []
    for variant_name, variant in (raw.get("variants") or {}).items():
        if isinstance(variant, dict) and variant_matches(variant, facts):
            merged = deep_merge(merged, variant.get("overlay") or {})
            applied_variants.append(variant_name)

    metadata = merged.setdefault("profile_metadata", {})
    metadata["requested_profile"] = name
    metadata["profile_path"] = profile_path(name).relative_to(_PROFILES_DIR).as_posix()
    metadata["resolved_extends"] = raw.get("extends") or []
    metadata["applied_variants"] = applied_variants
    metadata["repo_facts"] = facts
    return merged


def load_profile(name: str, repo_path: Optional[str] = None) -> dict:
    """Load an effective profile. Backward compatible with old callers."""
    return resolve_profile(name, repo_path)


def auto_detect_profile(repo_path: str) -> str:
    """Auto-detect the package profile from repository structure."""
    repo = Path(repo_path)

    detection_rules = [
        # (profile_name, check_function)
        ("kernel_6_6", lambda r: (r / "Makefile").exists() and (r / "Kconfig").exists() and (r / "include" / "uapi").exists()),
        ("cpython", lambda r: (r / "Python").is_dir() and (r / "Include").is_dir() and (r / "Lib").is_dir() and (r / "setup.py").exists()),
        ("golang", lambda r: (r / "src" / "runtime").is_dir() and (r / "src" / "cmd" / "go").is_dir()),
        ("ruby", lambda r: (r / "ruby.c").exists() and (r / "lib").is_dir() and (r / "ext").is_dir() and (r / "common.mk").exists()),
        ("dnf", lambda r: (r / "dnf").is_dir() and (r / "setup.py").exists()),
        ("libsoup", lambda r: (r / "libsoup").is_dir() and (r / "meson.build").exists()),
        ("grub2", lambda r: (r / "grub-core").is_dir() and (r / "util").is_dir()),
        ("libxml2", lambda r: (r / "parser.c").exists() and (r / "tree.c").exists() and (r / "include" / "libxml").is_dir()),
        ("httpd", lambda r: (r / "modules").is_dir() and (r / "server").is_dir() and (r / "include" / "httpd.h").exists()),
        ("vim", lambda r: (r / "src" / "vim.h").exists() and (r / "src" / "eval.c").exists()),
        ("git", lambda r: (r / "git.c").exists() and (r / "builtin").is_dir() and (r / "Documentation").is_dir()),
        ("glib2", lambda r: (r / "glib").is_dir() and (r / "gobject").is_dir() and (r / "gio").is_dir()),
        ("networkmanager", lambda r: (r / "src" / "core").is_dir() and (r / "src" / "libnm").is_dir()),
        ("dnsmasq", lambda r: (r / "src" / "dnsmasq.c").exists() and (r / "src" / "dnsmasq.h").exists()),
        ("haproxy", lambda r: (r / "src" / "haproxy.c").exists() and (r / "include" / "haproxy").is_dir()),
        ("rsyslog", lambda r: (r / "runtime").is_dir() and (r / "plugins").is_dir()),
        ("lvm2", lambda r: (r / "lib").is_dir() and (r / "tools").is_dir() and (r / "daemons").is_dir()),
        ("openldap", lambda r: (r / "servers" / "slapd").is_dir() and (r / "libraries" / "libldap").is_dir()),
        ("procps-ng", lambda r: ((r / "src" / "ps" / "sortformat.c").exists() or (r / "ps" / "sortformat.c").exists()) and ((r / "src").is_dir() or (r / "proc").is_dir())),
        ("util-linux", lambda r: (r / "libsmartcols").is_dir() and ((r / "sys-utils").is_dir() or (r / "misc-utils").is_dir())),
        ("grep", lambda r: (r / "src" / "grep.c").exists() and ((r / "lib").is_dir() or (r / "tests").is_dir())),
        ("systemd", lambda r: (r / "src" / "systemctl").is_dir() and (r / "src" / "core").is_dir() and (r / "meson.build").exists()),
        ("openssh", lambda r: (r / "scp.c").exists() and (r / "sftp.c").exists() and (r / "ssh.c").exists()),
        ("gcc", lambda r: (r / "gcc").is_dir() and (r / "libstdc++-v3").is_dir()),
    ]

    for profile_name, check_fn in detection_rules:
        try:
            if check_fn(repo):
                return profile_name
        except (OSError, PermissionError):
            continue

    return "c_project"


def get_api_surfaces(profile_name: str, repo_path: Optional[str] = None) -> dict:
    """Get API surface definitions for a given profile."""
    profile = load_profile(profile_name, repo_path)
    return profile.get("api_surfaces", {})


def get_compatibility_types(profile_name: str, repo_path: Optional[str] = None) -> list[str]:
    """Get applicable compatibility types for a given profile."""
    profile = load_profile(profile_name, repo_path)
    return profile.get("compatibility_types", [])


def get_ignore_patterns(profile_name: str, repo_path: Optional[str] = None) -> list[str]:
    """Get ignore patterns for a given profile."""
    profile = load_profile(profile_name, repo_path)
    return profile.get("ignore_patterns", [])


def get_language(profile_name: str, repo_path: Optional[str] = None) -> str:
    """Get primary language for a given profile."""
    profile = load_profile(profile_name, repo_path)
    return profile.get("language", "c")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Patch Compatibility Analyzer profile loader")
    parser.add_argument("--detect", metavar="REPO_PATH", help="Auto-detect profile")
    parser.add_argument("--show", metavar="PROFILE", help="Show effective profile details")
    parser.add_argument("--raw", metavar="PROFILE", help="Show raw profile without extends/variants")
    parser.add_argument("--repo", help="Repository path used for variant detection")
    parser.add_argument("--output", help="Write --show/--raw output to this file")
    parser.add_argument("--list", action="store_true", help="List available profiles")

    args = parser.parse_args()

    if args.list:
        for name, path in sorted(profile_index().items()):
            print("%s\t%s" % (name, path.relative_to(_PROFILES_DIR).as_posix()))
    elif args.detect:
        profile = auto_detect_profile(args.detect)
        print(profile)
    elif args.raw:
        profile = load_raw_profile(args.raw)
        rendered = _dump_yaml(profile)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)
    elif args.show:
        profile = load_profile(args.show, args.repo)
        rendered = _dump_yaml(profile)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)
