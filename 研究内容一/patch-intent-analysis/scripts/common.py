from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import NoReturn

from analysis_core import AnalysisError
from analysis_core.backend import bundled_ctags as _bundled_ctags
from analysis_core.backend import find_ctags as _find_ctags
from analysis_core.backend import platform_key


SKILL_DIR = Path(__file__).resolve().parent.parent


def bundled_ctags() -> Path:
    return _bundled_ctags(SKILL_DIR)


def find_ctags() -> tuple[str | None, str, str]:
    backend = _find_ctags(SKILL_DIR)
    source = backend.source if backend.compatible else f"{backend.source}-incompatible"
    if backend.executable is None:
        source = "missing"
    return backend.executable, source, backend.version


def emit(data: object, *, stream: object = sys.stdout) -> None:
    print(json.dumps(data, ensure_ascii=False, sort_keys=True), file=stream)


def fail(code: str, message: str, *, exit_code: int = 2) -> NoReturn:
    emit({"ok": False, "error": {"code": code, "message": message}}, stream=sys.stderr)
    raise SystemExit(exit_code)


def fail_analysis(error: AnalysisError, *, exit_code: int = 2) -> NoReturn:
    fail(error.code, error.message, exit_code=exit_code)
