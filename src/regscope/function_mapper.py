from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path


def map_executed_lines_to_functions(
    source_file: str | Path,
    executed_lines: Iterable[int],
    *,
    project_root: str | Path,
) -> list[str]:
    """Map executed source lines to stable, qualified function identifiers."""
    path = Path(source_file).resolve()
    root = Path(project_root).resolve()
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    executed = set(executed_lines)
    module_name = _path_to_module_name(path.relative_to(root))
    result: list[str] = []

    def walk(node: ast.AST, parents: tuple[str, ...] = ()) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                walk(child, parents + (child.name,))
                continue

            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified_name = ".".join((*parents, child.name))
                start_line = _function_body_start_line(child)
                end_line = child.end_lineno

                if end_line is not None and any(
                    start_line <= line <= end_line for line in executed
                ):
                    result.append(f"{module_name}:{qualified_name}")

                walk(child, parents + (child.name,))
                continue

            walk(child, parents)

    walk(tree)
    return sorted(set(result))


def _function_body_start_line(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> int:
    """Return the first executable line in a function body, excluding ``def``."""
    return min(statement.lineno for statement in node.body)


def _path_to_module_name(path: Path) -> str:
    """Convert a project-relative Python path such as app/service.py to app.service."""
    return ".".join(path.with_suffix("").parts)
