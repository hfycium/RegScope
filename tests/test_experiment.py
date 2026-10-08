from pathlib import Path
from subprocess import CompletedProcess
import json

import regscope.evaluation as evaluation
import regscope.experiment_cli as experiment_cli
from regscope.experiment import build_comparative_selections


def test_comparative_selections_define_file_function_and_hybrid_baselines():
    mapping = {
        "mappings": [
            {"test_id": "service", "functions": ["app.service:Order.run"]},
            {"test_id": "api", "functions": ["app.api:create_order"]},
            {"test_id": "other", "functions": ["app.user:list_users"]},
        ]
    }
    impact = {
        "changed_files": ["app/service.py"],
        "changed_functions": ["app.service:Order.run"],
        "affected_endpoints": [{"call_path": ["app.api:create_order", "app.service:Order.run"]}],
        "warnings": [],
    }

    result = build_comparative_selections(mapping, impact)

    assert result == {
        "full-suite": ["api", "other", "service"],
        "file-level-coverage": ["service"],
        "dynamic-only": ["service"],
        "hybrid": ["api", "service"],
    }


def test_empty_comparative_baseline_is_not_run_as_full_pytest_discovery(tmp_path: Path, monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(evaluation.subprocess, "run", fake_run)
    result = evaluation.evaluate_strategy_sets(
        tmp_path,
        python_executable="python",
        all_tests=["a", "b"],
        strategy_tests={"empty": [], "one": ["a"]},
        known_failing_tests=["a"],
    )

    assert result["strategies"]["empty"]["selected_tests"] == 0
    assert result["strategies"]["empty"]["recall"] == 0
    assert result["strategies"]["empty"]["selected_run"]["skipped"] is True
    assert len(calls) == 2  # only the non-empty candidate and full suite


def test_comparison_cli_persists_definitions_and_metrics(tmp_path: Path, monkeypatch):
    mapping_path = tmp_path / "coverage-mapping.json"
    impact_path = tmp_path / "impact.json"
    output_path = tmp_path / "reports" / "comparison.json"
    mapping_path.write_text(
        json.dumps({"target_root": str(tmp_path), "mappings": [{"test_id": "t", "functions": ["app.service:f"]}]}),
        encoding="utf-8",
    )
    impact_path.write_text(
        json.dumps({"changed_files": ["app/service.py"], "changed_functions": ["app.service:f"], "affected_endpoints": [], "warnings": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        experiment_cli,
        "evaluate_strategy_sets",
        lambda *args, **kwargs: {"schema_version": 1, "total_tests": 1, "strategies": {}, "full_run": {"exit_code": 0}},
    )

    result = experiment_cli.run_comparison(
        mapping_path,
        impact_path,
        python_executable="python",
        known_failing_tests=["tests/test_service.py::test_f"],
        output_path=output_path,
    )

    stored = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["definitions"] == stored["definitions"]
    assert set(result["definitions"]) == {"full-suite", "file-level-coverage", "dynamic-only", "hybrid"}
