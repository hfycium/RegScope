from __future__ import annotations

import json
from pathlib import Path

from .coverage_collector import collect_test_function_mappings
from .evaluation import evaluate_selection
from .impact_analysis import analyse_impact, write_impact
from .selector import select_tests


def run_pipeline(project_root: str | Path, base: str, head: str, output_dir: str | Path, *, python_executable: str | Path | None = None, known_failing_tests: list[str] | None = None) -> dict:
    """Run the MVP mapping, impact analysis, and selection workflow."""
    output = Path(output_dir).resolve()
    mapping = collect_test_function_mappings(project_root, output / "coverage", python_executable=python_executable, allow_test_failures=True)
    impact = analyse_impact(project_root, base, head)
    selection = select_tests(mapping, impact)
    evaluation = evaluate_selection(project_root, python_executable=python_executable or mapping["python_executable"], all_tests=[entry["test_id"] for entry in mapping["mappings"]], selected_tests=selection["selected_tests"], known_failing_tests=known_failing_tests or [])
    write_impact(impact, output / "impact.json")
    (output / "selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "evaluation.json").write_text(json.dumps(evaluation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "evaluation.md").write_text(f"# RegScope evaluation\n\n- Total tests: {evaluation['total_tests']}\n- Selected tests: {evaluation['selected_tests']}\n- Reduction ratio: {evaluation['reduction_ratio']:.2%}\n- Recall: {evaluation['recall']}\n", encoding="utf-8")
    return {"coverage_mapping": mapping, "impact": impact, "selection": selection, "evaluation": evaluation}
