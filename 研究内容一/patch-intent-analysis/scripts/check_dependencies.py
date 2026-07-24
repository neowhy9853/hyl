#!/usr/bin/env python3
from __future__ import annotations

import platform
import shutil
import sys

from analysis_core import bundled_ctags, find_ctags, managed_ctags, platform_key
from common import SKILL_DIR, emit


def main() -> None:
    ctags = find_ctags(SKILL_DIR)
    emit(
        {
            "ok": True,
            "platform": platform_key(),
            "python": {
                "available": sys.version_info >= (3, 10),
                "version": platform.python_version(),
            },
            "git": {
                "available": shutil.which("git") is not None,
                "path": shutil.which("git"),
            },
            "ctags": {
                "available": ctags.compatible,
                "path": ctags.executable,
                "source": ctags.source,
                "version": ctags.version,
                "bundled_candidate": str(bundled_ctags(SKILL_DIR)),
                "managed_candidate": str(managed_ctags(SKILL_DIR)),
            },
            "capabilities": {
                "universal_ctags_json": ctags.compatible,
                "python_ast_fallback": True,
                "source_pattern_fallback": True,
            },
        }
    )


if __name__ == "__main__":
    main()
