from __future__ import annotations

from pathlib import Path
import re

from .python_ast import extract_symbols as python_symbols
from .symbols import ChangedFile, Symbol


GENERIC_SYMBOL = re.compile(
    r"^\s*(?:pub\s+|export\s+|static\s+|async\s+|inline\s+)*"
    r"(?:def|class|func|fn|function|interface|struct|enum|type)\s+([A-Za-z_$][\w$]*)"
)
C_FUNCTION = re.compile(
    r"^\s*(?:[A-Za-z_][\w\s*]+)\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:\{|$)"
)


def fallback_symbols(root: Path, files: list[ChangedFile]) -> tuple[list[Symbol], list[str]]:
    symbols: list[Symbol] = []
    warnings: list[str] = []
    for item in files:
        path = (root / item.path).resolve()
        if path.suffix == ".py":
            found, warning = python_symbols(path, item.path)
            if found:
                symbols.extend(found)
                continue
            if warning:
                warnings.append(warning)
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            match = GENERIC_SYMBOL.match(line) or C_FUNCTION.match(line)
            if match:
                symbols.append(
                    Symbol(
                        name=match.group(1),
                        kind="approximate",
                        file=item.path,
                        line=number,
                        precision="approximate",
                    )
                )
    return symbols, warnings
