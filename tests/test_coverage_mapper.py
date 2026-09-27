import json
from pathlib import Path

import pytest

import regscope.coverage_mapper as coverage_mapper
from regscope.coverage_mapper import build_test_function_mapping


def test_build_mapping_from_windows_style_paths(tmp_path: Path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    service_file = app_dir / "service.py"

    service_file.write_text(
        """
def beta():
    return 2


def alpha():
    return 1
""".lstrip(),
        encoding="utf-8",
    )

    coverage_data = {
        "files": {
            "app\\service.py": {
                "executed_lines": [2, 6],
            }
        }
    }

    coverage_json = tmp_path / "coverage.json"
    coverage_json.write_text(
        json.dumps(coverage_data),
        encoding="utf-8",
    )

    result = build_test_function_mapping(
        test_id="tests/test_orders.py::test_create_order",
        coverage_json_path=coverage_json,
        project_root=tmp_path,
    )

    assert result == {
        "test_id": "tests/test_orders.py::test_create_order",
        "functions": [
            "app.service:alpha",
            "app.service:beta",
        ],
    }


def test_ignore_tests_and_missing_files(tmp_path: Path):
    app_dir = tmp_path / "app"
    tests_dir = tmp_path / "tests"

    app_dir.mkdir()
    tests_dir.mkdir()

    (app_dir / "service.py").write_text(
        """
def create_order():
    return 1
""".lstrip(),
        encoding="utf-8",
    )

    (tests_dir / "test_service.py").write_text(
        """
def test_create_order():
    return 1
""".lstrip(),
        encoding="utf-8",
    )

    coverage_data = {
        "files": {
            "app/service.py": {
                "executed_lines": [2],
            },
            "tests/test_service.py": {
                "executed_lines": [2],
            },
            "app/missing.py": {
                "executed_lines": [1],
            },
        }
    }

    coverage_json = tmp_path / "coverage.json"
    coverage_json.write_text(
        json.dumps(coverage_data),
        encoding="utf-8",
    )

    result = build_test_function_mapping(
        test_id="test_create_order",
        coverage_json_path=coverage_json,
        project_root=tmp_path,
    )

    assert result == {
        "test_id": "test_create_order",
        "functions": [
            "app.service:create_order",
        ],
    }


def test_functions_are_deduplicated_and_sorted(
    tmp_path: Path,
    monkeypatch,
):
    app_dir = tmp_path / "app"
    app_dir.mkdir()

    source_file = app_dir / "service.py"
    source_file.write_text(
        "def example():\n    return 1\n",
        encoding="utf-8",
    )

    coverage_data = {
        "files": {
            "app/service.py": {
                "executed_lines": [2],
            }
        }
    }

    coverage_json = tmp_path / "coverage.json"
    coverage_json.write_text(
        json.dumps(coverage_data),
        encoding="utf-8",
    )

    def fake_mapper(source_file, executed_lines, *, project_root):
        return [
            "app.service:zeta",
            "app.service:alpha",
            "app.service:zeta",
        ]

    monkeypatch.setattr(
        coverage_mapper,
        "map_executed_lines_to_functions",
        fake_mapper,
    )

    result = build_test_function_mapping(
        test_id="test_example",
        coverage_json_path=coverage_json,
        project_root=tmp_path,
    )

    assert result == {
        "test_id": "test_example",
        "functions": [
            "app.service:alpha",
            "app.service:zeta",
        ],
    }


def test_invalid_coverage_json_has_actionable_error(tmp_path: Path):
    coverage_json = tmp_path / "coverage.json"
    coverage_json.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid coverage JSON"):
        build_test_function_mapping("test_example", coverage_json, tmp_path)


def test_empty_coverage_produces_an_empty_mapping(tmp_path: Path):
    coverage_json = tmp_path / "coverage.json"
    coverage_json.write_text(json.dumps({"files": {}}), encoding="utf-8")

    assert build_test_function_mapping("test_example", coverage_json, tmp_path) == {
        "test_id": "test_example",
        "functions": [],
    }
