#!/usr/bin/env python3
"""Generate a package profile draft for Patch Compatibility Analyzer.

The generator creates a conservative YAML profile that extends reusable layers
and adds package-specific surface candidates inferred from repository layout.
It is intentionally deterministic and reviewable; generated profiles should be
checked by a human/agent before being treated as authoritative.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROFILES_DIR = SCRIPT_DIR.parent / "profiles"
PACKAGES_DIR = PROFILES_DIR / "packages"
EXCLUDED_SCAN_DIRS = {
    ".git",
    "pca-results",
    "_worktrees",
    "test",
    "tests",
    "t",
    "spec",
    "docs",
    "doc",
    "Documentation",
    "contrib",
    "examples",
    "vendor",
    "third_party",
    "submodules",
}


def run_git(repo: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo)] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def safe_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\.git$", "", value)
    value = re.sub(r"[^a-z0-9_+-]+", "-", value).strip("-")
    value = value.replace("+", "plus")
    return value or "generated_profile"


def infer_name(repo: Path, requested: str | None) -> str:
    if requested:
        return safe_name(requested)
    remote = run_git(repo, ["remote", "get-url", "origin"])
    if remote:
        tail = remote.rstrip("/").rsplit("/", 1)[-1]
        return safe_name(tail)
    return safe_name(repo.name)


def exists(repo: Path, *parts: str) -> bool:
    return (repo.joinpath(*parts)).exists()


def relevant_files(repo: Path) -> list[Path]:
    files = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if any(part in EXCLUDED_SCAN_DIRS for part in rel.parts):
            continue
        files.append(rel)
    return files


def has_any(repo: Path, patterns: list[str]) -> bool:
    files = relevant_files(repo)
    for rel in files:
        rel_text = rel.as_posix()
        if any(fnmatch.fnmatchcase(rel_text, pattern) for pattern in patterns):
            return True
    return any((repo / pattern.rstrip("/**")).exists() for pattern in patterns if pattern.endswith("/**"))


def infer_languages(repo: Path) -> list[str]:
    languages = []
    files = relevant_files(repo)
    counts = {
        "c": sum(1 for path in files if path.suffix.lower() in {".c", ".h", ".cc", ".cpp", ".hpp", ".cxx", ".hxx"}),
        "python": sum(1 for path in files if path.suffix.lower() == ".py"),
        "go": sum(1 for path in files if path.suffix.lower() == ".go"),
        "ruby": sum(1 for path in files if path.suffix.lower() == ".rb"),
    }
    if counts["c"]:
        languages.append("c")
    if counts["python"] >= 3 or (counts["python"] and "c" not in languages):
        languages.append("python")
    if counts["go"] >= 3 or (counts["go"] and not languages):
        languages.append("go")
    if counts["ruby"] >= 3 or (counts["ruby"] and not languages):
        languages.append("ruby")
    return languages or ["mixed"]


def infer_extends(repo: Path, languages: list[str]) -> list[str]:
    extends = ["default"]
    if "c" in languages:
        extends.extend(["c_family", "cli_tool"])
    if "python" in languages:
        extends.append("python_base")
    if "go" in languages:
        extends.append("go_base")
    if "ruby" in languages:
        extends.append("ruby_base")

    daemon_markers = [
        "src/*server*",
        "src/*daemon*",
        "daemon/**",
        "daemons/**",
        "protocol/**",
        "net/**",
        "**/*dbus*",
        "**/*http*",
        "**/*dns*",
        "**/*ldap*",
    ]
    if has_any(repo, daemon_markers):
        extends.append("daemon_network")

    if exists(repo, "include", "uapi") and (exists(repo, "Kconfig") or exists(repo, "kernel")):
        extends.append("kernel_base")

    output = []
    for item in extends:
        if item not in output:
            output.append(item)
    return output


def yaml_list(items: list[str], indent: int = 6) -> list[str]:
    prefix = " " * indent
    return [f"{prefix}- {item}" for item in items]


def surface_block(name: str, paths: list[str], patterns: list[str], priority: str, description: str) -> list[str]:
    lines = [
        f"  {name}:",
        "    public: true",
        f"    test_priority: {priority}",
        f"    description: {description}",
    ]
    if paths:
        lines.append("    paths:")
        lines.extend(yaml_list(paths, 6))
    if patterns:
        lines.append("    patterns:")
        lines.extend(yaml_list(patterns, 6))
    return lines


def infer_surface_blocks(repo: Path) -> list[str]:
    blocks: list[str] = []
    if exists(repo, "include") or has_any(repo, ["**/*.h", "**/*.hpp"]):
        blocks.extend(
            surface_block(
                "package_public_headers",
                ["include/**", "src/include/**", "**/*.h", "**/*.hpp"],
                ["API", "EXPORT", "PUBLIC"],
                "high",
                "Package public headers and declarations inferred from repository layout",
            )
        )
    if has_any(repo, ["**/*.pc", "**/*.pc.in", "**/*Config.cmake", "**/*Targets.cmake"]):
        blocks.extend(
            surface_block(
                "package_build_metadata",
                ["**/*.pc", "**/*.pc.in", "**/*Config.cmake", "**/*Targets.cmake"],
                [],
                "high",
                "Build metadata consumed by downstream projects",
            )
        )
    if has_any(repo, ["bin/**", "cmd/**", "src/cmd/**", "tools/**"]):
        blocks.extend(
            surface_block(
                "package_cli",
                ["bin/**", "cmd/**", "src/cmd/**", "tools/**"],
                ["getopt", "argparse", "parse_options", "flag."],
                "high",
                "Command-line commands, options, output, and exit behavior",
            )
        )
    if has_any(repo, ["**/*.conf", "**/*.conf.in", "etc/**", "conf/**", "config/**"]):
        blocks.extend(
            surface_block(
                "package_config",
                ["**/*.conf", "**/*.conf.in", "etc/**", "conf/**", "config/**"],
                ["config", "option", "setting"],
                "medium",
                "Configuration keys, defaults, and parser behavior",
            )
        )
    if has_any(repo, ["**/*proto*", "**/*http*", "**/*dns*", "**/*ldap*", "protocol/**", "net/**"]):
        blocks.extend(
            surface_block(
                "package_protocol",
                ["**/*proto*", "**/*http*", "**/*dns*", "**/*ldap*", "protocol/**", "net/**"],
                ["protocol", "packet", "request", "response", "query", "answer"],
                "high",
                "Network or data protocol behavior inferred from file layout",
            )
        )
    if not blocks:
        blocks.extend(
            surface_block(
                "package_main_surface",
                ["src/**", "lib/**"],
                [],
                "medium",
                "Main package implementation surface; review and narrow this generated rule",
            )
        )
    return blocks


def render_profile(repo: Path, name: str, extends: list[str], languages: list[str]) -> str:
    remote = run_git(repo, ["remote", "get-url", "origin"])
    branch = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    description = f"Generated package profile for {name}; review before production use"
    lines = [
        f"# Generated PCA package profile for {name}",
        "# Review paths, patterns, stability, and public flags before relying on this profile.",
        "",
        f"name: {name}",
        f"language: {','.join(languages)}",
        f"description: {description}",
        "extends:",
    ]
    lines.extend(yaml_list(extends, 2))
    if remote:
        lines.extend(
            [
                "",
                "variants:",
                "  detected_origin:",
                "    detect:",
                "      remotes:",
                f"        - '*{remote}*'",
            ]
        )
        if branch and branch != "HEAD":
            lines.extend(["      branches:", f"        - '{branch}'"])
        lines.extend(["    overlay:", "      api_surfaces:"])

    lines.extend(["", "api_surfaces:"])
    lines.extend(infer_surface_blocks(repo))
    lines.extend(
        [
            "",
            "compatibility_types:",
            "  - API_SIGNATURE_CHANGE: Public API signature changed",
            "  - ABI_CHANGE: ABI-relevant exported symbol, layout, enum, macro, or metadata changed",
            "  - INPUT_CONTRACT_CHANGE: Accepted input, validation, range, or required field changed",
            "  - RETURN_CONTRACT_CHANGE: Return value, status, exception, errno, or output contract changed",
            "  - ERROR_EXCEPTION_CHANGE: Error type, code, message, or failure path changed",
            "  - SIDE_EFFECT_CHANGE: Externally observable state, resource, network, or file side effect changed",
            "  - OUTPUT_FORMAT_CHANGE: CLI, log, protocol, structured, or file output format changed",
            "  - CONFIG_CLI_BEHAVIOR_CHANGE: CLI/config/default/environment behavior changed",
            "",
            "ignore_patterns:",
            "  - test/**",
            "  - tests/**",
            "  - docs/**",
            "  - examples/**",
            "  - generated profile rules marked for review",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a PCA package profile draft")
    parser.add_argument("--repo", required=True, help="Repository path")
    parser.add_argument("--name", help="Profile name; defaults to repo/remote name")
    parser.add_argument("--output", help="Output YAML path; defaults to stdout")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Write to profiles/packages/<name>.yaml unless --output is set",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output profile",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: repo does not exist: {repo}", file=sys.stderr)
        return 2

    name = infer_name(repo, args.name)
    languages = infer_languages(repo)
    extends = infer_extends(repo, languages)
    rendered = render_profile(repo, name, extends, languages)

    output = Path(args.output).resolve() if args.output else None
    if args.install and output is None:
        output = PACKAGES_DIR / f"{name}.yaml"

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and not args.force:
            print(f"ERROR: output exists, pass --force to overwrite: {output}", file=sys.stderr)
            return 1
        output.write_text(rendered, encoding="utf-8")
        print(f"Profile draft written to: {output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
