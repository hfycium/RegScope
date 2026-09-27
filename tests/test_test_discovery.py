from pathlib import Path
from subprocess import CompletedProcess
import sys

import pytest

import regscope.test_discovery as test_discovery
from regscope.test_discovery import discover_test_ids, resolve_target_python


def test_parse_pytest_node_ids_ignores_collection_noise():
    output = """\
tests/test_orders.py::test_create_order
tests/test_orders.py::TestOrders::test_rejects_empty_order
============================= test session starts =============================
2 tests collected in 0.01s
"""

    assert test_discovery._parse_pytest_node_ids(output) == [
        "tests/test_orders.py::TestOrders::test_rejects_empty_order",
        "tests/test_orders.py::test_create_order",
    ]


def test_discover_test_ids_uses_target_python_and_stable_sorting(tmp_path: Path, monkeypatch):
    interpreter = tmp_path / "target-python"
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return CompletedProcess(
            command,
            0,
            stdout="tests/test_z.py::test_z\ntests/test_a.py::test_a\n",
            stderr="",
        )

    monkeypatch.setattr(test_discovery.subprocess, "run", fake_run)

    result = discover_test_ids(tmp_path, python_executable=interpreter)

    assert result == ["tests/test_a.py::test_a", "tests/test_z.py::test_z"]
    assert calls == [
        (
            [
                str(interpreter),
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "-o",
                "addopts=",
            ],
            {"cwd": tmp_path.resolve(), "capture_output": True, "text": True, "check": False},
        )
    ]


def test_discover_test_ids_raises_with_pytest_error(tmp_path: Path, monkeypatch):
    def fake_run(command, **kwargs):
        return CompletedProcess(command, 1, stdout="", stderr="ImportError: missing app")

    monkeypatch.setattr(test_discovery.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="ImportError: missing app"):
        discover_test_ids(tmp_path, python_executable=tmp_path / "target-python")


def test_resolve_target_python_prefers_target_virtual_environment(tmp_path: Path):
    interpreter = tmp_path / ".venv" / "Scripts" / "python.exe"
    interpreter.parent.mkdir(parents=True)
    interpreter.touch()

    assert resolve_target_python(tmp_path) == interpreter


def test_discover_test_ids_runs_an_external_target_by_path(tmp_path: Path):
    target = tmp_path / "external-target"
    (target / "app").mkdir(parents=True)
    (target / "tests").mkdir()
    (target / "app" / "service.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    (target / "tests" / "test_service.py").write_text(
        "from app.service import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        encoding="utf-8",
    )
    (target / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\npythonpath = ['.']\naddopts = '-q'\n",
        encoding="utf-8",
    )

    assert discover_test_ids(target, python_executable=sys.executable) == [
        "tests/test_service.py::test_answer"
    ]
