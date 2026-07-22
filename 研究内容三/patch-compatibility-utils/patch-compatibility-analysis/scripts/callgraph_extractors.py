#!/usr/bin/env python3
"""AST function and call extractors for PCA call graphs.

Python uses the standard-library AST. C, Go, and Ruby require tree-sitter.
There is intentionally no regex or lexical fallback here: if AST dependencies
are absent, extraction returns no functions quickly.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Optional

from callgraph_types import (
    FunctionInfo,
    TREE_SITTER_NAMES,
    classify_entry,
    normalize_path,
    safe_read,
)


def all_ts_nodes(node) -> Iterable:
    yield node
    for child in getattr(node, "children", []):
        for descendant in all_ts_nodes(child):
            yield descendant


def node_text(source: bytes, node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def configure_tree_sitter_parser(language: str):
    ts_name = TREE_SITTER_NAMES.get(language)
    if not ts_name:
        return None

    try:
        from tree_sitter import Language, Parser
    except Exception:
        return None

    def make_parser(lang_obj):
        parser = Parser()
        if hasattr(parser, "set_language"):
            parser.set_language(lang_obj)
        else:
            parser.language = lang_obj
        return parser

    attempts = []

    try:
        from tree_sitter_language_pack import get_language

        attempts.append(lambda: get_language(ts_name))
    except Exception:
        pass

    try:
        from tree_sitter_languages import get_language

        attempts.append(lambda: get_language(ts_name))
    except Exception:
        pass

    module_name = "tree_sitter_%s" % ts_name
    try:
        module = __import__(module_name)

        def from_module():
            language_fn = getattr(module, "language")
            raw = language_fn()
            try:
                return Language(raw)
            except TypeError:
                return raw

        attempts.append(from_module)
    except Exception:
        pass

    for attempt in attempts:
        try:
            return make_parser(attempt())
        except Exception:
            continue
    return None


def ts_identifier_name(source: bytes, node) -> str:
    if node is None:
        return ""
    if node.type in {"identifier", "field_identifier", "property_identifier"}:
        return node_text(source, node)
    field = node.child_by_field_name("name") or node.child_by_field_name("field")
    if field is not None:
        found = ts_identifier_name(source, field)
        if found:
            return found
    declarator = node.child_by_field_name("declarator")
    if declarator is not None:
        found = ts_identifier_name(source, declarator)
        if found:
            return found
    found_names = [
        node_text(source, child)
        for child in all_ts_nodes(node)
        if child.type in {"identifier", "field_identifier", "property_identifier"}
    ]
    return found_names[-1] if found_names else ""


def ts_call_name(source: bytes, node) -> str:
    target = node.child_by_field_name("function")
    if target is None and node.children:
        target = node.children[0]
    return ts_identifier_name(source, target)


def ts_point_row(point) -> int:
    try:
        return point[0]
    except TypeError:
        return point.row


def extract_tree_sitter_functions(
    path: Path, repo: Path, language: str, parser
) -> List[FunctionInfo]:
    rel = normalize_path(path, repo)
    source_text = safe_read(path)
    if not source_text or parser is None:
        return []
    source = source_text.encode("utf-8", errors="replace")

    try:
        tree = parser.parse(source)
    except Exception:
        return []

    functions: List[FunctionInfo] = []
    root = tree.root_node
    for node in all_ts_nodes(root):
        if language == "c" and node.type != "function_definition":
            continue
        if language == "go" and node.type not in {
            "function_declaration",
            "method_declaration",
        }:
            continue
        if language == "ruby" and node.type not in {"method", "singleton_method"}:
            continue

        name_node = node.child_by_field_name("name")
        declarator = node.child_by_field_name("declarator")
        name = ts_identifier_name(source, name_node or declarator or node)
        if not name:
            continue

        body = node.child_by_field_name("body")
        call_root = body or node
        calls = {
            ts_call_name(source, call_node)
            for call_node in all_ts_nodes(call_root)
            if call_node.type in {"call_expression", "call", "command", "method_call"}
        }
        calls.discard("")

        function_text = node_text(source, node)
        header_text = function_text[: max(0, function_text.find("{"))]
        fn = FunctionInfo(
            name=name,
            qualname=name,
            file=rel,
            start_line=ts_point_row(node.start_point) + 1,
            end_line=ts_point_row(node.end_point) + 1,
            language=language,
            is_static=language == "c" and "static" in header_text.split(),
            calls=calls,
        )
        fn.entry_kind = classify_entry(fn)
        functions.append(fn)
    return functions


class PythonAstCollector(ast.NodeVisitor):
    def __init__(self, rel: str) -> None:
        self.rel = rel
        self.class_stack: List[str] = []
        self.functions: List[FunctionInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._add_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._add_function(node)

    def _add_function(self, node) -> None:
        qualname = (
            ".".join([*(self.class_stack), node.name])
            if self.class_stack
            else node.name
        )
        collector = PythonCallCollector()
        for stmt in node.body:
            collector.visit(stmt)
        fn = FunctionInfo(
            name=node.name,
            qualname=qualname,
            file=self.rel,
            start_line=getattr(node, "lineno", 1),
            end_line=getattr(node, "end_lineno", getattr(node, "lineno", 1)),
            language="python",
            calls=collector.calls,
        )
        fn.entry_kind = classify_entry(fn)
        self.functions.append(fn)


class PythonCallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls = set()

    def visit_Call(self, node: ast.Call) -> None:
        name = python_call_name(node.func)
        if name:
            self.calls.add(name)
        self.generic_visit(node)


def python_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = python_call_name(node.value)
        return "%s.%s" % (base, node.attr) if base else node.attr
    return ""


def extract_python_functions(path: Path, repo: Path) -> List[FunctionInfo]:
    rel = normalize_path(path, repo)
    text = safe_read(path)
    if not text:
        return []
    try:
        tree = ast.parse(text, filename=rel)
    except SyntaxError:
        return []
    collector = PythonAstCollector(rel)
    collector.visit(tree)
    return collector.functions


def extract_functions(path: Path, repo: Path, language: str, parser) -> List[FunctionInfo]:
    if language == "python":
        return extract_python_functions(path, repo)
    return extract_tree_sitter_functions(path, repo, language, parser)


def parser_available(language: str) -> bool:
    if language == "python":
        return True
    return configure_tree_sitter_parser(language) is not None
