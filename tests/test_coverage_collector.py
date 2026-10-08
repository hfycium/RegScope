import json
import hashlib
from pathlib import Path
from subprocess import CompletedProcess

import pytest

import regscope.coverage_collector as collector
from regscope.coverage_collector import collect_test_function_mappings


def test_collects_one_coverage_report_per_test_and_persists_mapping(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "service.py").write_text(
        "def alpha():\n    return 1\n\ndef beta():\n    return 2\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    commands = []

    def fake_run(command, **kwargs):
        commands.append((command, kwargs))
        if command[3] == "json":
            coverage_json = Path(command[command.index("-o") + 1])
            coverage_json.write_text(
                json.dumps({"files": {"app/service.py": {"executed_lines": [2]}}}),
                encoding="utf-8",
            )
        return CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)
    monkeypatch.setattr(
        collector,
        "create_mapping_provenance",
        lambda *args: {"source_revision": "test-revision"},
    )

    result = collect_test_function_mappings(
        tmp_path,
        output_dir,
        python_executable=tmp_path / "target-python",
        test_ids=["tests/test_b.py::test_b", "tests/test_a.py::test_a"],
    )

    assert [mapping["test_id"] for mapping in result["mappings"]] == [
        "tests/test_a.py::test_a",
        "tests/test_b.py::test_b",
    ]
    assert all(mapping["functions"] == ["app.service:alpha"] for mapping in result["mappings"])
    assert json.loads((output_dir / "coverage-mapping.json").read_text(encoding="utf-8")) == result
    assert len(commands) == 4
    assert commands[0][0][-1] == "tests/test_a.py::test_a"
    assert commands[0][1]["cwd"] == tmp_path.resolve()
    expected_digest = hashlib.sha256("tests/test_a.py::test_a".encode("utf-8")).hexdigest()[:12]
    assert commands[0][1]["env"]["COVERAGE_FILE"].endswith(f"0001-{expected_digest}")
    assert "no:cacheprovider" in commands[0][0]


def test_collect_writes_mapping_to_requested_file(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "service.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    mapping_output = tmp_path / "artifacts" / "baseline.json"

    def fake_run(command, **kwargs):
        if command[3] == "json":
            Path(command[command.index("-o") + 1]).write_text(
                json.dumps({"files": {"app/service.py": {"executed_lines": [2]}}}),
                encoding="utf-8",
            )
        return CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)
    monkeypatch.setattr(
        collector,
        "create_mapping_provenance",
        lambda *args: {"source_revision": "test-revision"},
    )

    result = collect_test_function_mappings(
        tmp_path,
        tmp_path / "work",
        python_executable=tmp_path / "target-python",
        test_ids=["tests/test_api.py::test_route"],
        mapping_path=mapping_output,
    )

    assert json.loads(mapping_output.read_text(encoding="utf-8")) == result
    assert (tmp_path / "work" / "per-test-coverage").is_dir()
    assert not (tmp_path / "work" / "coverage-mapping.json").exists()


def test_collect_raises_when_a_test_fails(tmp_path: Path, monkeypatch):
    def fake_run(command, **kwargs):
        return CompletedProcess(command, 1, stdout="", stderr="test failure")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="collect coverage for tests/test_a.py::test_a: test failure"):
        collect_test_function_mappings(
            tmp_path,
            tmp_path / "output",
            python_executable=tmp_path / "target-python",
            test_ids=["tests/test_a.py::test_a"],
        )


def test_collect_requires_at_least_one_test(tmp_path: Path):
    with pytest.raises(ValueError, match="At least one test ID"):
        collect_test_function_mappings(
            tmp_path,
            tmp_path / "output",
            python_executable=tmp_path / "target-python",
            test_ids=[],
        )


def test_collect_wraps_malformed_coverage_json_with_test_id(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "service.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    def fake_run(command, **kwargs):
        if command[3] == "json":
            Path(command[command.index("-o") + 1]).write_text("not-json", encoding="utf-8")
        return CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="Could not map coverage for tests/test_a.py::test_a"):
        collect_test_function_mappings(
            tmp_path,
            tmp_path / "output",
            python_executable=tmp_path / "target-python",
            test_ids=["tests/test_a.py::test_a"],
        )
