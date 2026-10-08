from __future__ import annotations

from pathlib import PurePosixPath

from .selector import select_tests


def build_comparative_selections(coverage_mapping: dict, impact: dict) -> dict[str, list[str]]:
    """Build file-level, changed-function-only, and current hybrid candidates."""
    mappings = coverage_mapping["mappings"]
    changed_files = {
        str(PurePosixPath(path))
        for path in impact.get("changed_files", [])
        if str(path).endswith(".py")
    }
    changed_functions = set(impact.get("changed_functions", []))

    file_level = []
    function_only = []
    for entry in mappings:
        functions = set(entry.get("functions", []))
        covered_files = {
            str(PurePosixPath(function.partition(":")[0].replace(".", "/") + ".py"))
            for function in functions
            if ":" in function
        }
        if changed_files.intersection(covered_files):
            file_level.append(entry["test_id"])
        if changed_functions.intersection(functions):
            function_only.append(entry["test_id"])

    hybrid = select_tests(coverage_mapping, impact)["selected_tests"]
    return {
        "full-suite": sorted({entry["test_id"] for entry in mappings}),
        "file-level-coverage": sorted(set(file_level)),
        "dynamic-only": sorted(set(function_only)),
        "hybrid": sorted(set(hybrid)),
    }
