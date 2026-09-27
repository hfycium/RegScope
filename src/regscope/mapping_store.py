from __future__ import annotations

import json
from pathlib import Path


def load_coverage_mapping(mapping_path: str | Path) -> dict:
    """Load and validate a persisted version-1 coverage mapping."""
    path = Path(mapping_path)
    try:
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid coverage mapping JSON at {path}: {exc.msg}") from exc

    if not isinstance(mapping, dict) or mapping.get("schema_version") != 1:
        raise ValueError(f"Coverage mapping at {path} is not schema version 1")

    entries = mapping.get("mappings")
    if not isinstance(entries, list):
        raise ValueError(f"Coverage mapping at {path} has no mappings list")

    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("test_id"), str):
            raise ValueError(f"Coverage mapping at {path} contains an invalid test entry")
        functions = entry.get("functions")
        if not isinstance(functions, list) or not all(isinstance(item, str) for item in functions):
            raise ValueError(f"Coverage mapping at {path} contains invalid function IDs")
    return mapping


def functions_for_test(mapping_path: str | Path, test_id: str) -> list[str]:
    """Return the persisted function IDs for one stable pytest node ID."""
    mapping = load_coverage_mapping(mapping_path)
    for entry in mapping["mappings"]:
        if entry["test_id"] == test_id:
            return list(entry["functions"])
    raise KeyError(f"Test ID not present in coverage mapping: {test_id}")
