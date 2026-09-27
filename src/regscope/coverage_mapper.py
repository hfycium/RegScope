from __future__ import annotations

import json
from pathlib import Path

from .function_mapper import map_executed_lines_to_functions


def build_test_function_mapping(
    test_id: str,
    coverage_json_path: str | Path,
    project_root: str | Path,
) -> dict:
    """Convert one test's coverage report into a test-to-function mapping."""
    root = Path(project_root).resolve()
    coverage_path = Path(coverage_json_path)
    try:
        coverage_data = json.loads(coverage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid coverage JSON at {coverage_path}: {exc.msg}") from exc

    if not isinstance(coverage_data, dict):
        raise ValueError(f"Coverage JSON at {coverage_path} must contain an object")

    files = coverage_data.get("files", {})
    if not isinstance(files, dict):
        raise ValueError(f"Coverage JSON at {coverage_path} has a non-object files field")
    function_ids: set[str] = set()

    for file_name, file_info in files.items():
        if not isinstance(file_info, dict):
            continue
        normalized_name = file_name.replace("\\", "/")
        source_path = Path(normalized_name)

        if not source_path.is_absolute():
            source_path = root / source_path

        if source_path.suffix.lower() != ".py":
            continue

        source_path = source_path.resolve()

        try:
            relative_path = source_path.relative_to(root)
        except ValueError:
            continue

        if not relative_path.parts or relative_path.parts[0] != "app":
            continue

        if not source_path.is_file():
            continue

        functions = map_executed_lines_to_functions(
            source_path,
            file_info.get("executed_lines", []),
            project_root=root,
        )
        function_ids.update(functions)

    return {"test_id": test_id, "functions": sorted(function_ids)}
