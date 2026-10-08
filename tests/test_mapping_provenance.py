from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import regscope.mapping_provenance as provenance


def test_create_provenance_fingerprints_runtime_inputs_and_test_ids(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(provenance, "resolve_revision", lambda *args: "base-sha")
    monkeypatch.setattr(
        provenance,
        "_target_runtime",
        lambda *args: {"python_version": [3, 14, 3], "system": "Linux"},
    )
    monkeypatch.setattr(
        provenance,
        "_tracked_environment_input_hashes",
        lambda *args: {"uv.lock": "lock-hash"},
    )

    result = provenance.create_mapping_provenance(
        tmp_path, "python", ["tests/test_a.py::test_a", "tests/test_b.py::test_b"]
    )

    assert result["source_revision"] == "base-sha"
    assert len(result["environment_fingerprint"]) == 64
    assert len(result["test_inventory_fingerprint"]) == 64


def test_environment_fingerprint_inputs_include_target_configs_and_tests(
    tmp_path: Path,
):
    repo = tmp_path / "repo"
    target = repo / "backend"
    (target / "tests").mkdir(parents=True)
    (repo / "uv.lock").write_text("lock", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[tool.uv]", encoding="utf-8")
    (target / "pyproject.toml").write_text("[tool.pytest]", encoding="utf-8")
    test_source = target / "tests" / "test_api.py"
    test_source.write_text("def test_api(): pass\n", encoding="utf-8")
    (target / "app.py").write_text("def handler(): pass\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", "."], cwd=repo, check=True, capture_output=True
    )

    first = provenance._tracked_environment_input_hashes(target)
    first_lock_hash = first["uv.lock"]
    (repo / "uv.lock").write_text("changed lock", encoding="utf-8")
    test_source.write_text("def test_api(): assert True\n", encoding="utf-8")
    second = provenance._tracked_environment_input_hashes(target)

    assert "uv.lock" in first
    assert "pyproject.toml" in first
    assert "backend/pyproject.toml" in first
    assert "backend/tests/test_api.py" in first
    assert "backend/app.py" not in first
    assert first_lock_hash != second["uv.lock"]
    assert first["backend/tests/test_api.py"] != second["backend/tests/test_api.py"]


def test_mapping_compatibility_accepts_matching_provenance(tmp_path: Path, monkeypatch):
    test_ids = ["tests/test_api.py::test_route"]
    current = {
        "source_revision": "base-sha",
        "environment_fingerprint": "environment-sha",
        "test_inventory_fingerprint": "tests-sha",
    }
    monkeypatch.setattr(provenance, "resolve_revision", lambda *args: "base-sha")
    monkeypatch.setattr(provenance, "resolve_target_python", lambda *args: "python")
    monkeypatch.setattr(provenance, "discover_test_ids", lambda *args, **kwargs: test_ids)
    monkeypatch.setattr(provenance, "create_mapping_provenance", lambda *args: current)
    mapping = {
        "python_executable": "python",
        "provenance": current,
        "mappings": [{"test_id": test_ids[0], "functions": ["app.api:route"]}],
    }

    reasons, discovered = provenance.check_mapping_compatibility(
        tmp_path, "base", mapping, "python"
    )

    assert reasons == []
    assert discovered == test_ids


def test_mapping_compatibility_reports_missing_provenance_and_test_drift(
    tmp_path: Path, monkeypatch
):
    test_ids = ["tests/test_api.py::test_route"]
    monkeypatch.setattr(provenance, "resolve_revision", lambda *args: "base-sha")
    monkeypatch.setattr(provenance, "resolve_target_python", lambda *args: "python")
    monkeypatch.setattr(provenance, "discover_test_ids", lambda *args, **kwargs: test_ids)
    monkeypatch.setattr(
        provenance,
        "create_mapping_provenance",
        lambda *args: {
            "source_revision": "base-sha",
            "environment_fingerprint": "environment-sha",
            "test_inventory_fingerprint": "tests-sha",
        },
    )
    mapping = {
        "python_executable": "python",
        "mappings": [{"test_id": "old-test", "functions": []}],
    }

    reasons, discovered = provenance.check_mapping_compatibility(
        tmp_path, "base", mapping, "python"
    )

    assert "Coverage mapping has no provenance metadata" in reasons
    assert "Coverage mapping test IDs differ from current discovery" in reasons
    assert discovered == test_ids


@pytest.mark.parametrize(
    ("field", "changed_value", "expected_reason"),
    [
        (
            "source_revision",
            "different-base",
            "Coverage mapping source revision does not match base",
        ),
        (
            "environment_fingerprint",
            "different-environment",
            "Coverage mapping environment fingerprint does not match",
        ),
        (
            "test_inventory_fingerprint",
            "different-tests",
            "Coverage mapping test inventory fingerprint does not match",
        ),
    ],
)
def test_mapping_compatibility_detects_provenance_drift(
    tmp_path: Path, monkeypatch, field: str, changed_value: str, expected_reason: str
):
    test_ids = ["tests/test_api.py::test_route"]
    current = {
        "source_revision": "base-sha",
        "environment_fingerprint": "environment-sha",
        "test_inventory_fingerprint": "tests-sha",
    }
    monkeypatch.setattr(provenance, "resolve_revision", lambda *args: "base-sha")
    monkeypatch.setattr(provenance, "resolve_target_python", lambda *args: "python")
    monkeypatch.setattr(provenance, "discover_test_ids", lambda *args, **kwargs: test_ids)
    monkeypatch.setattr(provenance, "create_mapping_provenance", lambda *args: current)
    saved = current | {field: changed_value}
    mapping = {
        "python_executable": "python",
        "provenance": saved,
        "mappings": [{"test_id": test_ids[0], "functions": []}],
    }

    reasons, _ = provenance.check_mapping_compatibility(
        tmp_path, "base", mapping, "python"
    )

    assert expected_reason in reasons
