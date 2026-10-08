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
    assert result["full_run"]["exit_code"] == 0


def test_selected_only_skips_full_suite(tmp_path: Path, monkeypatch):
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(evaluation.subprocess, "run", fake_run)
    result = evaluation.evaluate_selection(
        tmp_path,
        python_executable="python",
        all_tests=["selected", "other"],
        selected_tests=["selected"],
        known_failing_tests=[],
        run_full_suite=False,
    )

    assert len(commands) == 1
    assert commands[0][-1] == "selected"
    assert result["selected_run"]["exit_code"] == 0
    assert result["full_run"] == {
        "elapsed_seconds": 0.0,
        "exit_code": None,
        "skipped": True,
        "reason": "Full-suite comparison disabled",
    }


def test_empty_selection_falls_back_to_population_and_reports_it(tmp_path: Path, monkeypatch):
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(evaluation.subprocess, "run", fake_run)
    result = evaluation.evaluate_selection(tmp_path, python_executable="python", all_tests=["a", "b"], selected_tests=[], known_failing_tests=[])
    assert result["selection_fallback"] is True
    assert result["selected_tests"] == 2
    assert result["reduction_ratio"] == 0
    assert commands[0][-2:] == ["a", "b"]


def test_empty_population_skips_pytest_discovery(tmp_path: Path, monkeypatch):
    def unexpected_run(*args, **kwargs):
        raise AssertionError("pytest should not run with an empty test population")

    monkeypatch.setattr(evaluation.subprocess, "run", unexpected_run)
    result = evaluation.evaluate_selection(tmp_path, python_executable="python", all_tests=[], selected_tests=[], known_failing_tests=[])
    assert result["selected_run"]["skipped"] is True
    assert result["full_run"]["skipped"] is True
