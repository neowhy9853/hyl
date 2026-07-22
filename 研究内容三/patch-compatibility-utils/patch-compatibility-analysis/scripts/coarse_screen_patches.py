#!/usr/bin/env python3
"""Coarse pre-screening for PCA patch batches.

This script is intentionally conservative. It is allowed to use textual
signals to reduce a large patch queue, but it must not be treated as final
semantic adjudication. The output separates:

- keep: clear compatibility-surface signal, should receive full PCA analysis
- review: not enough evidence to drop safely
- drop: no compatibility signal found, generally docs/tests-only or internal
  mechanical cleanup
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


PATCH_FROM_RE = re.compile(r"^From ([0-9a-f]{40}) ", re.MULTILINE)
PATCH_SUBJECT_RE = re.compile(r"^Subject:\s*(.*)$", re.MULTILINE)
DIFF_FILE_RE = re.compile(r"^\+\+\+ b/(.*)$", re.MULTILINE)


DOC_PREFIXES = ("Documentation/", "doc/", "docs/")
TEST_PREFIXES = ("t/", "test/", "tests/", "Lib/test/", "src/test/")
BUILD_FILES = {
    "Makefile",
    "config.mak.uname",
    "meson.build",
    "CMakeLists.txt",
    "configure.ac",
}

REFRACTOR_SUBJECT_HINTS = (
    "factor out",
    "extract",
    "rename",
    "stop using",
    "replace use of",
    "use strset",
    "use strvec",
    "simplify internals",
    "prepare for",
    "fix test order",
)

PUBLIC_HEADER_PREFIXES = (
    "include/",
    "Include/",
    "src/include/",
    "libraries/lib",
)

GIT_CLI_FILES = (
    "git.c",
    "parse-options.c",
    "parse-options.h",
)

GIT_PROTOCOL_FILES = (
    "fetch-pack.c",
    "fetch-pack.h",
    "send-pack.c",
    "send-pack.h",
    "transport.c",
    "transport.h",
    "upload-pack.c",
    "serve.c",
    "pkt-line.c",
    "protocol.c",
    "protocol-caps.c",
    "remote-curl.c",
    "connect.c",
)

PUBLIC_SIGNAL_RE = re.compile(
    r"("
    r"\bOPT_[A-Z0-9_]+\s*\(|"
    r"\bOPT_ALIAS\s*\(|"
    r"\bPARSE_OPT|"
    r"\bgetopt_long\s*\(|"
    r"\bargparse\b|"
    r"\bPyAPI_(?:FUNC|DATA)\b|"
    r"\bEXPORT_SYMBOL(?:_GPL|_NS)?\s*\(|"
    r"\bSYSCALL_DEFINE\d*\s*\(|"
    r"\bCOMPAT_SYSCALL_DEFINE\d*\s*\(|"
    r"\b_IO(?:R|W|WR)?\s*\(|"
    r"\bgenl_family\b|"
    r"\bnla_policy\b|"
    r"\bproc_create(?:_data|_seq)?\b|"
    r"\bDEVICE_ATTR(?:_RO|_RW)?\b|"
    r"\bregister_sysctl\b|"
    r"\bsysfs_emit(?:_at)?\b"
    r")"
)

CONFIG_SIGNAL_RE = re.compile(
    r"("
    r"\bgit_config\b|"
    r"\brepo_config\b|"
    r"\bgit_config_get(?:_[A-Za-z0-9_]+)?\b|"
    r"\bgit_default_config\b|"
    r"\bconfig_fn_t\b|"
    r"[`\"](?:[a-z][a-z0-9-]*|remote\.\*)\.[A-Za-z][A-Za-z0-9_.-]*[`\"]|"
    r"remote\.\*\.[A-Za-z]"
    r")"
)

PROTOCOL_SIGNAL_RE = re.compile(
    r"("
    r"\bpacket_(?:write|buf_write|reader|flush|line)\b|"
    r"\bcapability\b|"
    r"\bwant\b|"
    r"\bhave\b|"
    r"\bfetch-pack\b|"
    r"\bsend-pack\b|"
    r"\btransport\b"
    r")"
)

ERROR_OUTPUT_SIGNAL_RE = re.compile(
    r"("
    r"\bdie\s*\(|"
    r"\berror\s*\(|"
    r"\bwarning\s*\(|"
    r"\bfprintf\s*\(|"
    r"\bprintf\s*\(|"
    r"\bputs\s*\(|"
    r"\bstrbuf_addf\s*\("
    r")"
)

CLI_OPTION_RE = re.compile(
    r"("
    r"\bOPT_[A-Z0-9_]+\s*\(|"
    r"\bOPT_ALIAS\s*\(|"
    r"`--[A-Za-z0-9][A-Za-z0-9_-]+|"
    r"\"--[A-Za-z0-9][A-Za-z0-9_-]+\""
    r")"
)


@dataclass
class PatchInfo:
    path: str
    commit: str
    subject: str
    files: list[str]
    score: int = 0
    signals: list[str] = field(default_factory=list)
    decision: str = "review"
    reason: str = ""


def read_patch(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def changed_files(text: str) -> list[str]:
    return sorted(set(DIFF_FILE_RE.findall(text)))


def patch_subject(text: str) -> str:
    match = PATCH_SUBJECT_RE.search(text)
    return match.group(1).strip() if match else ""


def patch_commit(text: str) -> str:
    match = PATCH_FROM_RE.search(text)
    return match.group(1) if match else ""


def is_docs_or_tests_only(files: list[str]) -> bool:
    if not files:
        return False
    for file in files:
        if file.startswith(DOC_PREFIXES) or file.startswith(TEST_PREFIXES):
            continue
        return False
    return True


def is_build_only(files: list[str]) -> bool:
    if not files:
        return False
    for file in files:
        name = Path(file).name
        if name in BUILD_FILES or file.endswith((".mk", ".cmake")):
            continue
        return False
    return True


def add_signal(info: PatchInfo, score: int, signal: str) -> None:
    info.score += score
    if signal not in info.signals:
        info.signals.append(signal)


def display_path(path: Path, root: Path) -> str:
    try:
        rendered = path.relative_to(root)
    except ValueError:
        rendered = path
    return str(rendered).replace("\\", "/")


def classify_patch(path: Path, root: Path) -> PatchInfo:
    text = read_patch(path)
    files = changed_files(text)
    subject = patch_subject(text)
    info = PatchInfo(
        path=display_path(path, root),
        commit=patch_commit(text),
        subject=subject,
        files=files,
    )

    lower_subject = subject.lower()

    if is_docs_or_tests_only(files):
        info.decision = "drop"
        info.reason = "docs/tests-only patch; no runtime compatibility surface changed"
        return info

    if is_build_only(files):
        info.decision = "review"
        info.reason = "build-only patch; may affect packaging/build compatibility"
        add_signal(info, 1, "build surface")
        return info

    added_deleted = "\n".join(
        line
        for line in text.splitlines()
        if (line.startswith("+") and not line.startswith("+++"))
        or (line.startswith("-") and not line.startswith("---"))
    )

    if any(file.startswith("builtin/") for file in files):
        add_signal(info, 1, "git builtin command implementation")
    if any(file in GIT_CLI_FILES for file in files):
        add_signal(info, 2, "git command/option parser")
    if any(file.startswith(PUBLIC_HEADER_PREFIXES) for file in files):
        add_signal(info, 3, "public/header surface")
    if any(file in GIT_PROTOCOL_FILES for file in files):
        add_signal(info, 1, "transport/protocol surface")
    if any(file.startswith("Documentation/") for file in files):
        add_signal(info, 1, "documentation changed with code")

    if PUBLIC_SIGNAL_RE.search(added_deleted):
        add_signal(info, 5, "public API/CLI/system interface token")
    if CONFIG_SIGNAL_RE.search(added_deleted):
        add_signal(info, 4, "configuration key/parser signal")
    if PROTOCOL_SIGNAL_RE.search(added_deleted):
        add_signal(info, 2, "wire/protocol negotiation signal")
    if ERROR_OUTPUT_SIGNAL_RE.search(added_deleted):
        add_signal(info, 1, "observable error/output signal")

    if CLI_OPTION_RE.search(added_deleted):
        add_signal(info, 4, "CLI option added/changed")

    if any(hint in lower_subject for hint in REFRACTOR_SUBJECT_HINTS):
        add_signal(info, -3, "refactor/mechanical subject hint")

    if info.score >= 6:
        info.decision = "keep"
        info.reason = "compatibility-surface signal present; run full PCA"
    elif info.score <= 1 and any(hint in lower_subject for hint in REFRACTOR_SUBJECT_HINTS):
        info.decision = "drop"
        info.reason = "internal/mechanical refactor signal only"
    elif info.score <= 0:
        info.decision = "drop"
        info.reason = "no public/API/CLI/config/protocol compatibility signal found"
    else:
        info.decision = "review"
        info.reason = "weak or indirect signal; keep for lightweight manual triage"

    return info


def write_markdown(path: Path, repo: Path, patch_dir: Path, infos: list[PatchInfo]) -> None:
    groups = {
        "keep": [i for i in infos if i.decision == "keep"],
        "review": [i for i in infos if i.decision == "review"],
        "drop": [i for i in infos if i.decision == "drop"],
    }
    lines = [
        "# PCA Coarse Patch Screen",
        "",
        "## Environment",
        "",
        f"- Repository path: {repo}",
        f"- Patch directory: {patch_dir}",
        f"- Total patches: {len(infos)}",
        f"- Keep for full PCA: {len(groups['keep'])}",
        f"- Manual/lightweight review: {len(groups['review'])}",
        f"- Screened out: {len(groups['drop'])}",
        "",
        "This is a conservative pre-screen. Only `keep` patches are strong candidates",
        "for full compatibility analysis. `review` patches should not be deleted without",
        "a quick human/agent check. `drop` patches have no compatibility signal found by",
        "this coarse pass.",
        "",
    ]
    for decision, title in [
        ("keep", "Keep For Full PCA"),
        ("review", "Manual Or Lightweight Review"),
        ("drop", "Screened Out"),
    ]:
        lines.extend(
            [
                f"## {title}",
                "",
                "| # | Patch | Commit | Score | Subject | Reason | Signals |",
                "|---:|---|---|---:|---|---|---|",
            ]
        )
        for idx, info in enumerate(groups[decision], 1):
            commit = info.commit[:12] if info.commit else ""
            signals = ", ".join(info.signals)
            subject = info.subject.replace("|", "\\|")
            reason = info.reason.replace("|", "\\|")
            lines.append(
                f"| {idx} | `{info.path}` | `{commit}` | {info.score} | {subject} | {reason} | {signals} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Repository root")
    parser.add_argument("--patch-dir", required=True, help="Directory of patch files")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    patch_dir = Path(args.patch_dir).resolve()
    patches = sorted(patch_dir.glob("*.patch"))
    infos = [classify_patch(path, repo) for path in patches]

    result = {
        "repo": str(repo),
        "patch_dir": str(patch_dir),
        "total": len(infos),
        "summary": {
            "keep": sum(1 for i in infos if i.decision == "keep"),
            "review": sum(1 for i in infos if i.decision == "review"),
            "drop": sum(1 for i in infos if i.decision == "drop"),
        },
        "patches": [info.__dict__ for info in infos],
    }
    Path(args.output_json).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(Path(args.markdown), repo, patch_dir, infos)
    print(
        "coarse screen: keep={keep} review={review} drop={drop}".format(
            **result["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
