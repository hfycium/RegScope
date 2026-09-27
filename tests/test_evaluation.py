from pathlib import Path
from subprocess import CompletedProcess

import pytest

import regscope.evaluation as evaluation


def test_evaluation_calculates_recall_and_reduction(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(evaluation.subprocess, "run", lambda *args, **kwargs: CompletedProcess(args[0], 0, "", ""))
    result = evaluation.evaluate_selection(tmp_path, python_executable="python", all_tests=["a", "b", "c", "c"], selected_tests=["b", "b"], known_failing_tests=["b"])
    assert result["total_tests"] == 3
    assert result["selected_tests"] == 1
    assert result["reduction_ratio"] == pytest.approx(2 / 3)
    assert result["recall"] == 1.0
    assert result["selected_run"]["exit_code"] == 0
