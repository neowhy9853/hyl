#!/usr/bin/env python3
"""Create an isolated Git view with a sanitized target commit message.

The source repository is never modified.  A clone is created at OUTPUT_REPO,
the target commit object is copied with the same headers/tree/parents and a
sanitized message, and ``git replace`` maps the original commit id to the new
object inside the clone.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


LEGACY_LABELS = (
    "feat",
    "fix",
    "refactor",
    "perf",
    "docs",
    "style",
    "test",
    "chore",
    "build",
    "ci",
    "revert",
)
_LABEL_ALT = "|".join(sorted(LEGACY_LABELS, key=len, reverse=True))
_CONVENTIONAL_PREFIX = re.compile(
    rf"^\s*(?:{_LABEL_ALT})(?:\([^)]+\))?!?:\s*",
    re.IGNORECASE,
)
_LABELISH_PREFIX = re.compile(
    rf"^\s*(?:{_LABEL_ALT})(?:/[^:]+)?\s*:\s*",
    re.IGNORECASE,
)
_LEADING_TOKEN = re.compile(r"^\s*([A-Za-z]+)\b")
_LABEL_SET = set(LEGACY_LABELS)


def sanitize_commit_message(message: str) -> str:
    """Remove an old-taxonomy label prefix from the first message line."""

    raw = (message or "").strip()
    if not raw:
        return ""
    first, *rest = raw.splitlines()
    stripped = _CONVENTIONAL_PREFIX.sub("", first, count=1)
    if stripped == first:
        stripped = _LABELISH_PREFIX.sub("", first, count=1)
    if stripped == first:
        token = _LEADING_TOKEN.match(first)
        if token and token.group(1).lower() in _LABEL_SET:
            remainder = first[token.end() :]
            remainder = re.sub(r"^\s*[:/_-]\s*", "", remainder, count=1)
            stripped = remainder.lstrip()
    stripped = stripped.strip() or "Message intentionally sanitized."
    if not rest:
        return stripped
    return "\n".join([stripped, *rest]).strip()


def _git(
    repo: Path,
    args: list[str],
    *,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(error or f"git {' '.join(args)} failed")
    return result


def _clone(source_repo: Path, output_repo: Path, clone_mode: str) -> None:
    if output_repo.exists():
        raise FileExistsError(f"output repository already exists: {output_repo}")
    output_repo.parent.mkdir(parents=True, exist_ok=True)
    # Git disables local clone optimizations for a partial source and invokes
    # upload-pack, which cannot serve missing promisor blobs. Build the shared
    # view explicitly; never ask the cache to manufacture a complete pack.
    partial = subprocess.run(["git", "-C", str(source_repo), "config", "--get-regexp",
                              r"remote\..*\.promisor"], capture_output=True).returncode == 0
    shallow = _git(source_repo, ["rev-parse", "--is-shallow-repository"]).stdout.strip() == b"true"
    if clone_mode == "shared" and (partial or shallow):
        output_repo.mkdir()
        _git(output_repo, ["init", "-q"])
        source_git = Path(_git(source_repo, ["rev-parse", "--absolute-git-dir"]).stdout.decode().strip())
        (output_repo / ".git/objects/info/alternates").write_text(str(source_git / "objects") + "\n")
        if (source_git / "shallow").exists():
            shutil.copyfile(source_git / "shallow", output_repo / ".git/shallow")
        refs = _git(source_repo, ["for-each-ref", "--format=%(objectname) %(refname)",
                                  "refs/heads", "refs/tags"]).stdout.decode().splitlines()
        # A fresh clone needs no reflogs. Preserve all branch/tag refs in one
        # native packed-refs file instead of creating hundreds of loose files.
        packed = "# pack-refs with: sorted\n" + "\n".join(sorted(refs, key=lambda line: line.split(" ", 1)[1])) + "\n"
        (output_repo / ".git/packed-refs").write_text(packed)
        _git(output_repo, ["remote", "add", "origin", str(source_repo)])
        _git(output_repo, ["config", "remote.origin.promisor", "true"])
        _git(output_repo, ["config", "remote.origin.partialclonefilter", "blob:none"])
        _git(output_repo, ["update-ref", "--no-deref", "HEAD",
                          _git(source_repo, ["rev-parse", "HEAD"]).stdout.decode().strip()])
        return
    mode_args = ["--shared"] if clone_mode == "shared" else ["--no-local"]
    result = subprocess.run(
        [
            "git",
            "clone",
            *mode_args,
            "--no-checkout",
            "--quiet",
            "--",
            str(source_repo),
            str(output_repo),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(error or "git clone failed")


def prepare_sanitized_repository(
    source_repo: Path,
    commit_id: str,
    output_repo: Path,
    *,
    clone_mode: str = "shared",
    replacement_message: str | None = None,
    checkout: bool = True,
) -> dict[str, Any]:
    """Clone SOURCE_REPO and replace only the target commit's message view."""

    source_repo = source_repo.resolve()
    output_repo = output_repo.resolve()
    if clone_mode not in {"shared", "full"}:
        raise ValueError("clone_mode must be 'shared' or 'full'")
    if not source_repo.is_dir():
        raise FileNotFoundError(f"source repository does not exist: {source_repo}")
    _git(source_repo, ["rev-parse", "--is-inside-work-tree"])
    _clone(source_repo, output_repo, clone_mode)

    canonical = (
        _git(output_repo, ["rev-parse", "--verify", f"{commit_id}^{{commit}}"])
        .stdout.decode()
        .strip()
    )
    original = _git(output_repo, ["cat-file", "commit", canonical]).stdout
    headers, separator, message_bytes = original.partition(b"\n\n")
    if not separator:
        raise RuntimeError("target commit object has no message separator")

    original_message = message_bytes.decode("utf-8", errors="replace")
    visible_message = (
        replacement_message.strip()
        if replacement_message is not None
        else sanitize_commit_message(original_message)
    )
    if not visible_message:
        visible_message = "Message intentionally sanitized."

    replacement_id = canonical
    replacement_applied = visible_message.strip() != original_message.strip()
    if replacement_applied:
        replacement = headers + b"\n\n" + visible_message.encode("utf-8") + b"\n"
        replacement_id = (
            _git(
                output_repo,
                ["hash-object", "-t", "commit", "-w", "--stdin"],
                input_bytes=replacement,
            )
            .stdout.decode()
            .strip()
        )
        _git(output_repo, ["replace", canonical, replacement_id])

    original_tree = _git(
        output_repo,
        ["--no-replace-objects", "show", "-s", "--format=%T", canonical],
    ).stdout
    visible_tree = _git(
        output_repo, ["show", "-s", "--format=%T", canonical]
    ).stdout
    original_parents = _git(
        output_repo,
        ["--no-replace-objects", "show", "-s", "--format=%P", canonical],
    ).stdout
    visible_parents = _git(
        output_repo, ["show", "-s", "--format=%P", canonical]
    ).stdout
    if original_tree != visible_tree or original_parents != visible_parents:
        raise RuntimeError("replacement changed the target commit tree or parents")

    if checkout:
        _git(output_repo, ["-c", "advice.detachedHead=false", "checkout", "--detach", "--quiet", canonical])
    visible_subject = (
        _git(output_repo, ["show", "-s", "--format=%s", canonical])
        .stdout.decode("utf-8", errors="replace")
        .strip()
    )

    return {
        "source_repo": str(source_repo),
        "output_repo": str(output_repo),
        "clone_mode": clone_mode,
        "checked_out": checkout,
        "commit_id": canonical,
        "replacement_applied": replacement_applied,
        "replacement_commit_id": replacement_id,
        "original_subject": original_message.splitlines()[0] if original_message else "",
        "visible_subject": visible_subject,
        "tree_unchanged": original_tree == visible_tree,
        "parents_unchanged": original_parents == visible_parents,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone a repository and sanitize one commit message with git replace."
    )
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output-repo", type=Path, required=True)
    parser.add_argument(
        "--clone-mode",
        choices=("shared", "full"),
        default="shared",
        help="shared is fast and depends on the source repo; full copies Git objects.",
    )
    parser.add_argument(
        "--message-file",
        type=Path,
        help="Use this complete replacement message instead of automatic prefix removal.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    replacement_message = None
    if args.message_file is not None:
        replacement_message = args.message_file.read_text(encoding="utf-8")
    result = prepare_sanitized_repository(
        args.source_repo,
        args.commit,
        args.output_repo,
        clone_mode=args.clone_mode,
        replacement_message=replacement_message,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
