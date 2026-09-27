from __future__ import annotations


def select_tests(coverage_mapping: dict, impact: dict) -> dict:
    """Select affected tests, falling back to all tests on incomplete impact data."""
    mappings = coverage_mapping["mappings"]
    fallback_reasons = list(impact.get("warnings", []))
    if impact.get("module_level_changes"):
        fallback_reasons.append("Module-level changes cannot be safely mapped to functions")
    if fallback_reasons:
        return {
            "schema_version": 1,
            "strategy": "conservative-fallback",
            "selected_tests": [entry["test_id"] for entry in mappings],
            "unselected_tests": [],
            "reasons": {entry["test_id"]: fallback_reasons for entry in mappings},
        }

    affected = set(impact.get("changed_functions", []))
    affected.update(endpoint["call_path"][0] for endpoint in impact.get("affected_endpoints", []) if endpoint.get("call_path"))
    reasons: dict[str, list[str]] = {}
    for entry in mappings:
        shared = sorted(affected.intersection(entry["functions"]))
        if shared:
            reasons[entry["test_id"]] = shared
    return {
        "schema_version": 1,
        "strategy": "coverage-intersection",
        "selected_tests": sorted(reasons),
        "unselected_tests": sorted(entry["test_id"] for entry in mappings if entry["test_id"] not in reasons),
        "reasons": reasons,
    }
