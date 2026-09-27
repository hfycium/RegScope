from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path


def map_changed_lines_to_functions(source_file: str | Path, changed_lines: Iterable[int], *, project_root: str | Path) -> dict:
    """Map changed source lines to containing functions and separate module-level lines."""
    path = Path(source_file).resolve()
    root = Path(project_root).resolve()
    changed = set(changed_lines)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module = ".".join(path.relative_to(root).with_suffix("").parts)
    functions: set[str] = set()
    function_lines: set[int] = set()

    def walk(node: ast.AST, parents: tuple[str, ...] = ()) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                walk(child, parents + (child.name,))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([child.lineno, *(decorator.lineno for decorator in child.decorator_list)])
                end = child.end_lineno or child.lineno
                covered = set(range(start, end + 1))
                function_lines.update(covered)
                if changed & covered:
                    functions.add(f"{module}:{'.'.join((*parents, child.name))}")
                walk(child, parents + (child.name,))
            else:
                walk(child, parents)

    walk(tree)
    return {"functions": sorted(functions), "module_level_lines": sorted(changed - function_lines)}
