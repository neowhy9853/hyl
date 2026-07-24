from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .errors import AnalysisError
from .symbols import ChangedFile, Symbol


def extract_symbols(
    executable: str,
    root: Path,
    files: list[ChangedFile],
    *,
    timeout: float,
) -> list[Symbol]:
    command = [
        executable,
        "--output-format=json",
        "--fields=+neK",
        "--extras=-F",
        "--sort=no",
        *[item.path for item in files],
    ]
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AnalysisError("E_ANALYSIS_TIMEOUT", "ctags indexing timed out") from error
    except OSError as error:
        raise AnalysisError("E_CTAGS_UNAVAILABLE", str(error)) from error
    if result.returncode not in {0, 1}:
        raise AnalysisError("E_CTAGS", result.stderr.strip() or "ctags failed")

    symbols: list[Symbol] = []
    for line in result.stdout.splitlines():
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if raw.get("_type") != "tag" or not raw.get("line") or not raw.get("name"):
            continue
        symbols.append(
            Symbol(
                name=str(raw["name"]),
                kind=str(raw.get("kind", "")),
                file=str(raw.get("path", "")),
                line=int(raw["line"]),
                end_line=int(raw["end"]) if raw.get("end") else None,
                precision="exact",
            )
        )
    return symbols
