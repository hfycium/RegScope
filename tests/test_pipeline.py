from pathlib import Path

import regscope.pipeline as pipeline


def test_run_pipeline_writes_impact_and_selection(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(pipeline, "collect_test_function_mappings", lambda *args, **kwargs: {"python_executable": "python", "mappings": [{"test_id": "t", "functions": ["app.s:f"]}]})
    monkeypatch.setattr(pipeline, "analyse_impact", lambda *args: {"changed_functions": ["app.s:f"], "affected_endpoints": [], "warnings": []})
    monkeypatch.setattr(pipeline, "evaluate_selection", lambda *args, **kwargs: {"total_tests": 1, "selected_tests": 1, "reduction_ratio": 0.0, "recall": None})
    result = pipeline.run_pipeline(tmp_path, "base", "head", tmp_path / "output")
    assert result["selection"]["selected_tests"] == ["t"]
    assert (tmp_path / "output" / "impact.json").is_file()
    assert (tmp_path / "output" / "selection.json").is_file()
    assert (tmp_path / "output" / "evaluation.json").is_file()
