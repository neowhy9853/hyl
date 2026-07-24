from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .errors import AnalysisError
from .symbols import ChangedFile


DIFF_FILE = re.compile(r"^\+\+\+ b/(.+)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _run(
    repo: Path,
    args: list[str],
    *,
    timeout: float,
    text: bool = True,
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AnalysisError("E_ANALYSIS_TIMEOUT", f"git command timed out: {' '.join(args)}") from error
    except OSError as error:
        raise AnalysisError("E_GIT_UNAVAILABLE", str(error)) from error
    if result.returncode != 0:
        stderr = result.stderr if isinstance(result.stderr, str) else result.stderr.decode("utf-8", errors="replace")
        raise AnalysisError("E_GIT", stderr.strip() or f"git command failed: {' '.join(args)}")
    return result


def resolve_repo(raw: str, *, timeout: float = 5.0) -> Path:
    repo = Path(raw).expanduser().resolve()
    if not repo.is_dir():
        raise AnalysisError("E_REPO_NOT_FOUND", f"repository is not a directory: {repo}")
    result = _run(repo, ["rev-parse", "--show-toplevel"], timeout=timeout)
    root = Path(result.stdout.strip()).resolve()
    if not root.is_dir():
        raise AnalysisError("E_NOT_GIT_REPOSITORY", str(repo))
    return root


def resolve_commit(repo: Path, raw: str, *, timeout: float = 5.0) -> str:
    value = raw.strip()
    if not value or value.startswith("-"):
        raise AnalysisError("E_INVALID_COMMIT", "commit must be a non-option revision")
    try:
        result = _run(repo, ["rev-parse", "--verify", f"{value}^{{commit}}"], timeout=timeout)
    except AnalysisError as error:
        raise AnalysisError("E_INVALID_COMMIT", f"commit not found: {value}") from error
    return result.stdout.strip()


def changed_lines(repo: Path, commit: str, *, timeout: float) -> list[ChangedFile]:
    result = _run(
        repo,
        [
            "-c",
            "core.quotePath=false",
            "show",
            "--format=",
            "--unified=0",
            "--find-renames",
            "--no-ext-diff",
            commit,
        ],
        timeout=timeout,
    )
    files: list[ChangedFile] = []
    current: ChangedFile | None = None
    for line in result.stdout.splitlines():
        file_match = DIFF_FILE.match(line)
        if file_match:
            current = ChangedFile(file_match.group(1))
            files.append(current)
            continue
        hunk = HUNK.match(line)
        if hunk and current is not None:
            start = int(hunk.group(1))
            count = int(hunk.group(2) or "1")
            current.lines.update(range(start, start + count))
    return files


def materialize_files(
    repo: Path,
    commit: str,
    files: list[ChangedFile],
    destination: Path,
    *,
    timeout: float,
) -> tuple[list[ChangedFile], list[str]]:
    root = destination.resolve()
    present: list[ChangedFile] = []
    warnings: list[str] = []
    for item in files:
        target = (root / item.path).resolve()
        try:
            target.relative_to(root)
        except ValueError as error:
            raise AnalysisError("E_PATH_FORBIDDEN", f"path escapes analysis directory: {item.path}") from error
        try:
            result = _run(repo, ["show", f"{commit}:{item.path}"], timeout=timeout, text=False)
        except AnalysisError:
            warnings.append(f"HISTORICAL_FILE_UNAVAILABLE: {item.path}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result.stdout)
        present.append(item)
    return present, warnings
