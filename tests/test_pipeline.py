import json
from pathlib import Path

import pytest

import regscope.pipeline as pipeline


def test_run_pipeline_writes_impact_and_selection(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(pipeline, "collect_test_function_mappings", lambda *args, **kwargs: {"python_executable": "python", "mappings": [{"test_id": "t", "functions": ["app.s:f"]}]})
    monkeypatch.setattr(pipeline, "analyse_impact", lambda *args: {"changed_functions": ["app.s:f"], "affected_endpoints": [], "warnings": []})
    monkeypatch.setattr(pipeline, "evaluate_selection", lambda *args, **kwargs: {"total_tests": 1, "selected_tests": 1, "selection_fallback": False, "reduction_ratio": 0.0, "recall": None, "selected_run": {"exit_code": 0}, "full_run": {"exit_code": 0}})
    result = pipeline.run_pipeline(tmp_path, "base", "head", tmp_path / "output")
    assert result["selection"]["selected_tests"] == ["t"]
    assert (tmp_path / "output" / "impact.json").is_file()
    assert (tmp_path / "output" / "selection.json").is_file()
    assert (tmp_path / "output" / "evaluation.json").is_file()


def test_run_pipeline_reuses_saved_mapping_without_collecting(
    tmp_path: Path, monkeypatch
):
    mapping = {
        "schema_version": 1,
        "target_root": "old/target/path",
        "python_executable": "python",
        "mappings": [{"test_id": "tests/test_api.py::test_route", "functions": ["app.s:f"]}],
    }
    mapping_path = tmp_path / "baseline-mapping.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
    evaluation_options = {}

    def fake_evaluate(*args, **kwargs):
        evaluation_options.update(kwargs)
        return {
            "total_tests": 1,
            "selected_tests": 1,
            "selection_fallback": False,
            "reduction_ratio": 0.0,
            "recall": None,
            "selected_run": {"exit_code": 0},
            "full_run": {"skipped": True, "exit_code": None},
        }

    monkeypatch.setattr(
        pipeline,
        "collect_test_function_mappings",
        lambda *args, **kwargs: pytest.fail("coverage collection should be skipped"),
    )
    monkeypatch.setattr(
        pipeline,
        "analyse_impact",
        lambda *args: {"changed_functions": ["app.s:f"], "affected_endpoints": [], "warnings": []},
    )
    monkeypatch.setattr(
        pipeline,
        "check_mapping_compatibility",
        lambda *args: ([], ["tests/test_api.py::test_route"]),
    )
    monkeypatch.setattr(
        pipeline,
        "evaluate_selection",
        fake_evaluate,
    )

    result = pipeline.run_pipeline(
        tmp_path,
        "base",
        "head",
        tmp_path / "output",
        mapping_path=mapping_path,
        python_executable="target-python",
        selected_only=True,
    )

    assert result["selection"]["selected_tests"] == ["tests/test_api.py::test_route"]
    assert evaluation_options["run_full_suite"] is False
    report = (tmp_path / "output" / "evaluation.md").read_text(encoding="utf-8")
    assert "Full-suite comparison: skipped" in report
    saved_mapping = tmp_path / "output" / "coverage" / "coverage-mapping.json"
    assert json.loads(saved_mapping.read_text(encoding="utf-8")) == mapping


def test_incompatible_mapping_falls_back_to_current_test_inventory(
    tmp_path: Path, monkeypatch
):
    mapping = {
        "schema_version": 1,
        "python_executable": "python",
        "mappings": [{"test_id": "old_test", "functions": ["app.s:f"]}],
    }
    mapping_path = tmp_path / "stale-mapping.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
    monkeypatch.setattr(
        pipeline,
        "check_mapping_compatibility",
        lambda *args: (["Coverage mapping source revision does not match base"], ["new_test_a", "new_test_b"]),
    )
    monkeypatch.setattr(
        pipeline,
        "analyse_impact",
        lambda *args: {"changed_functions": [], "affected_endpoints": [], "warnings": []},
    )
    evaluation_args = {}

    def fake_evaluate(*args, **kwargs):
        evaluation_args.update(kwargs)
        return {
            "total_tests": 2,
            "selected_tests": 2,
            "selection_fallback": False,
            "reduction_ratio": 0.0,
            "recall": None,
            "selected_run": {"exit_code": 0},
            "full_run": {"skipped": True, "exit_code": None},
        }

    monkeypatch.setattr(pipeline, "evaluate_selection", fake_evaluate)

    result = pipeline.run_pipeline(
        tmp_path,
        "base",
        "head",
        tmp_path / "output",
        mapping_path=mapping_path,
        python_executable="target-python",
        selected_only=True,
    )

    assert result["selection"]["strategy"] == "conservative-fallback"
    assert result["selection"]["selected_tests"] == ["new_test_a", "new_test_b"]
    assert result["selection"]["reasons"]["new_test_a"] == [
        "Coverage mapping source revision does not match base"
    ]
    assert evaluation_args["all_tests"] == ["new_test_a", "new_test_b"]
    assert evaluation_args["selected_tests"] == ["new_test_a", "new_test_b"]


@pytest.mark.parametrize(
    "contents",
    ["not json", "{}", '{"schema_version": 2, "mappings": []}'],
)
def test_run_pipeline_rejects_invalid_mapping(tmp_path: Path, contents: str, monkeypatch):
    mapping_path = tmp_path / "invalid-mapping.json"
    mapping_path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(
        pipeline,
        "collect_test_function_mappings",
        lambda *args, **kwargs: pytest.fail("invalid mapping should fail before collection"),
    )

    with pytest.raises(ValueError, match="coverage mapping|Coverage mapping"):
        pipeline.run_pipeline(
            tmp_path,
            "base",
            "head",
            tmp_path / "output",
            mapping_path=mapping_path,
        )
