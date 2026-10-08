from __future__ import annotations

import json
from pathlib import Path

from .coverage_collector import collect_test_function_mappings   # 建表
from .evaluation import evaluate_selection                       # 评估
from .impact_analysis import analyse_impact, write_impact        # 影响分析
from .mapping_provenance import check_mapping_compatibility
from .selector import select_tests                               # 选测试


def run_pipeline(project_root: str | Path, base: str, head: str, output_dir: str | Path, *, python_executable: str | Path | None = None, mapping_path: str | Path | None = None, selected_only: bool = False, known_failing_tests: list[str] | None = None) -> dict:
    """Run the MVP mapping, impact analysis, and selection workflow."""
    output = Path(output_dir).resolve()
    compatibility_reasons: list[str] = []
    current_test_ids: list[str] | None = None
    if mapping_path is None:
        mapping = collect_test_function_mappings(project_root, output / "coverage", python_executable=python_executable, allow_test_failures=True)
    else:
        mapping = _load_coverage_mapping(mapping_path)
        compatibility_reasons, current_test_ids = check_mapping_compatibility(
            project_root, base, mapping, python_executable
        )
        mapping_output = output / "coverage" / "coverage-mapping.json"
        mapping_output.parent.mkdir(parents=True, exist_ok=True)
        mapping_output.write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    impact = analyse_impact(project_root, base, head)
    if compatibility_reasons:
        assert current_test_ids is not None
        selection = {
            "schema_version": 1,
            "strategy": "conservative-fallback",
            "selected_tests": current_test_ids,
            "unselected_tests": [],
            "reasons": {
                test_id: compatibility_reasons for test_id in current_test_ids
            },
        }
        all_tests = current_test_ids
    else:
        selection = select_tests(mapping, impact)
        all_tests = [entry["test_id"] for entry in mapping["mappings"]]
    evaluation = evaluate_selection(project_root, python_executable=python_executable or mapping["python_executable"], all_tests=all_tests, selected_tests=selection["selected_tests"], known_failing_tests=known_failing_tests or [], run_full_suite=not selected_only)
    full_run = evaluation["full_run"]
    full_run_status = (
        "skipped"
        if full_run.get("skipped")
        else f"exit code {full_run['exit_code']}"
    )
    write_impact(impact, output / "impact.json")
    (output / "selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "evaluation.json").write_text(json.dumps(evaluation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "evaluation.md").write_text(f"# RegScope evaluation\n\n- Total tests: {evaluation['total_tests']}\n- Selected tests: {evaluation['selected_tests']}\n- Selected run exit code: {evaluation['selected_run']['exit_code']}\n- Full-suite comparison: {full_run_status}\n- Selection fallback: {evaluation['selection_fallback']}\n- Reduction ratio: {evaluation['reduction_ratio']:.2%}\n- Recall: {evaluation['recall']}\n", encoding="utf-8")
    return {"coverage_mapping": mapping, "impact": impact, "selection": selection, "evaluation": evaluation}


def _load_coverage_mapping(mapping_path: str | Path) -> dict:
    path = Path(mapping_path)
    try:
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read coverage mapping from {path}: {exc}") from exc

    if not isinstance(mapping, dict) or mapping.get("schema_version") != 1:
        raise ValueError("Coverage mapping must be a schema_version 1 JSON object")
    entries = mapping.get("mappings")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Coverage mapping must contain a non-empty 'mappings' list")
    for index, entry in enumerate(entries):
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("test_id"), str)
            or not isinstance(entry.get("functions"), list)
            or any(not isinstance(function, str) for function in entry["functions"])
        ):
            raise ValueError(
                f"Coverage mapping entry {index} must contain a string test_id "
                "and a list of string functions"
            )
    if not isinstance(mapping.get("python_executable"), str):
        raise ValueError("Coverage mapping must contain a string 'python_executable'")
    return mapping
