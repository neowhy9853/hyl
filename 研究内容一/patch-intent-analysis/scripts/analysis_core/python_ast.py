from __future__ import annotations

import ast
from pathlib import Path

from .symbols import Symbol


def extract_symbols(path: Path, relative_path: str) -> tuple[list[Symbol], str | None]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text, filename=relative_path)
    except SyntaxError as error:
        return [], f"PYTHON_SYNTAX_ERROR: {relative_path}:{error.lineno or 1}: {error.msg}"

    symbols = [
        Symbol(
            name=node.name,
            kind=node.__class__.__name__,
            file=relative_path,
            line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            precision="exact",
        )
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    return symbols, None
