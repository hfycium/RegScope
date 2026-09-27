import json
from pathlib import Path

import pytest

from regscope.mapping_store import functions_for_test, load_coverage_mapping


def write_mapping(tmp_path: Path, mapping: object) -> Path:
    path = tmp_path / "coverage-mapping.json"
    path.write_text(json.dumps(mapping), encoding="utf-8")
    return path


def test_functions_for_test_reads_one_persisted_mapping(tmp_path: Path):
    path = write_mapping(
        tmp_path,
        {
            "schema_version": 1,
            "mappings": [
                {"test_id": "tests/test_a.py::test_a", "functions": ["app.service:alpha"]},
                {"test_id": "tests/test_b.py::test_b", "functions": []},
            ],
        },
    )

    assert functions_for_test(path, "tests/test_a.py::test_a") == ["app.service:alpha"]
    assert functions_for_test(path, "tests/test_b.py::test_b") == []


def test_functions_for_test_rejects_unknown_test_id(tmp_path: Path):
    path = write_mapping(tmp_path, {"schema_version": 1, "mappings": []})

    with pytest.raises(KeyError, match="Test ID not present"):
        functions_for_test(path, "tests/test_missing.py::test_missing")


@pytest.mark.parametrize(
    "mapping",
    [
        {"schema_version": 2, "mappings": []},
        {"schema_version": 1, "mappings": "not-a-list"},
        {"schema_version": 1, "mappings": [{"test_id": 1, "functions": []}]},
        {"schema_version": 1, "mappings": [{"test_id": "test", "functions": [1]}]},
    ],
)
def test_load_coverage_mapping_rejects_invalid_shape(tmp_path: Path, mapping: dict):
    with pytest.raises(ValueError):
        load_coverage_mapping(write_mapping(tmp_path, mapping))
