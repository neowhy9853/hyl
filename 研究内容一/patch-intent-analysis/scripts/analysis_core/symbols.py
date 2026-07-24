from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ChangedFile:
    path: str
    lines: set[int] = field(default_factory=set)

    def as_dict(self) -> dict[str, object]:
        return {"path": self.path, "changed_lines": sorted(self.lines)}


@dataclass(frozen=True, slots=True)
class Symbol:
    name: str
    kind: str
    file: str
    line: int
    end_line: int | None = None
    precision: str = "exact"


def map_changed_symbols(
    files: list[ChangedFile],
    symbols: list[Symbol],
    *,
    rangeless_max_distance: int = 40,
) -> list[dict[str, object]]:
    mapped: dict[tuple[str, str, int], dict[str, object]] = {}
    by_file: dict[str, list[Symbol]] = {}
    for symbol in symbols:
        by_file.setdefault(symbol.file, []).append(symbol)

    for item in files:
        ordered = sorted(by_file.get(item.path, []), key=lambda row: row.line)
        for changed in sorted(item.lines):
            candidates = [
                row
                for row in ordered
                if row.line <= changed and (row.end_line is None or changed <= row.end_line)
            ]
            if not candidates:
                continue
            symbol = candidates[-1]
            if symbol.end_line is None and changed - symbol.line > rangeless_max_distance:
                continue
            key = (symbol.file, symbol.name, symbol.line)
            record = mapped.setdefault(
                key,
                {
                    "name": symbol.name,
                    "kind": symbol.kind,
                    "file": symbol.file,
                    "line": symbol.line,
                    "end_line": symbol.end_line,
                    "precision": symbol.precision,
                    "changed_lines": [],
                },
            )
            changed_lines = record["changed_lines"]
            assert isinstance(changed_lines, list)
            changed_lines.append(changed)
    return list(mapped.values())
