from __future__ import annotations

import json
from pathlib import Path

from .change_mapper import map_changed_lines_to_functions
from .git_diff import changed_files, changed_head_lines, resolve_revision
from .static_analysis import find_affected_endpoints


def analyse_impact(project_root: str | Path, base: str, head: str) -> dict:
    """Combine Git change data and static paths into an explainable impact result."""
    root = Path(project_root).resolve()
    base_id, head_id = resolve_revision(root, base), resolve_revision(root, head)
    files = changed_files(root, base_id, head_id)
    lines = changed_head_lines(root, base_id, head_id)
    functions: set[str] = set()
    module_changes: dict[str, list[int]] = {}
    warnings: list[str] = []
    for file_name, changed in lines.items():
        source = root / file_name
        if not file_name.startswith("app/") or source.suffix != ".py" or not source.is_file():
            continue
        mapped = map_changed_lines_to_functions(source, changed, project_root=root)
        functions.update(mapped["functions"])
        if mapped["module_level_lines"]:
            module_changes[file_name] = mapped["module_level_lines"]
    for file_name in files:
        if file_name not in lines:
            warnings.append(f"No head-side source lines available for changed file: {file_name}")
    if module_changes:
        warnings.append("Module-level business changes require conservative test selection")
    return {
        "schema_version": 1, "base": base_id, "head": head_id, "changed_files": files,
        "changed_functions": sorted(functions), "module_level_changes": module_changes,
        "affected_endpoints": find_affected_endpoints(root, sorted(functions)), "warnings": warnings,
    }


def write_impact(result: dict, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
