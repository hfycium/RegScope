from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath

from .git_diff import resolve_revision
from .test_discovery import discover_test_ids, resolve_target_python


_CONFIG_NAMES = {
    ".python-version",
    "Pipfile.lock",
    "poetry.lock",
    "pyproject.toml",
    "pytest.ini",
    "setup.cfg",
    "tox.ini",
    "uv.lock",
}


def create_mapping_provenance(
    project_root: str | Path,
    python_executable: str | Path,
    test_ids: list[str],
) -> dict:
    """Describe the Git base, runtime, relevant files, and test population."""
    root = Path(project_root).resolve()
    try:
        source_revision = resolve_revision(root, "HEAD")
    except ValueError:
        # Unit tests and local scratch targets may not be Git repositories.
        source_revision = None

    runtime = _target_runtime(python_executable)
    input_hashes = _tracked_environment_input_hashes(root)
    environment_fingerprint = _fingerprint(
        {"runtime": runtime, "inputs": input_hashes}
    )
    return {
        "source_revision": source_revision,
        "environment_fingerprint": environment_fingerprint,
        "test_inventory_fingerprint": _fingerprint(sorted(test_ids)),
    }


def check_mapping_compatibility(
    project_root: str | Path,
    base: str,
    mapping: dict,
    python_executable: str | Path | None,
) -> tuple[list[str], list[str]]:
    """Return incompatibility reasons and the current target test IDs."""
    root = Path(project_root).resolve()
    interpreter = resolve_target_python(
        root, python_executable or mapping.get("python_executable")
    )
    current_test_ids = discover_test_ids(root, python_executable=interpreter)
    reasons: list[str] = []
    provenance = mapping.get("provenance")

    if not isinstance(provenance, dict):
        reasons.append("Coverage mapping has no provenance metadata")
        provenance = {}

    try:
        base_revision = resolve_revision(root, base)
    except ValueError as exc:
        reasons.append(f"Could not resolve requested base revision: {exc}")
    else:
        if provenance.get("source_revision") != base_revision:
            reasons.append("Coverage mapping source revision does not match base")

    current_provenance = create_mapping_provenance(
        root, interpreter, current_test_ids
    )
    if (
        provenance.get("environment_fingerprint")
        != current_provenance["environment_fingerprint"]
    ):
        reasons.append("Coverage mapping environment fingerprint does not match")
    if (
        provenance.get("test_inventory_fingerprint")
        != current_provenance["test_inventory_fingerprint"]
    ):
        reasons.append("Coverage mapping test inventory fingerprint does not match")

    mapped_test_ids = sorted(
        entry["test_id"] for entry in mapping.get("mappings", [])
    )
    if mapped_test_ids != current_test_ids:
        reasons.append("Coverage mapping test IDs differ from current discovery")

    return sorted(set(reasons)), current_test_ids


def _target_runtime(python_executable: str | Path) -> dict:
    script = (
        "import importlib.metadata, json, platform, sys; "
        "print(json.dumps({"
        "'implementation': sys.implementation.name, "
        "'python_version': list(sys.version_info[:3]), "
        "'system': platform.system(), 'machine': platform.machine(), "
        "'pytest_version': importlib.metadata.version('pytest'), "
        "'coverage_version': importlib.metadata.version('coverage')"
        "}))"
    )
    result = subprocess.run(
        [str(python_executable), "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "runtime probe failed"
        raise RuntimeError(f"Could not inspect target Python environment: {message}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Target Python returned invalid environment metadata") from exc


def _tracked_environment_input_hashes(project_root: Path) -> dict[str, str]:
    repo_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if repo_result.returncode != 0:
        return {}
    repo_root = Path(repo_result.stdout.strip()).resolve()
    files_result = subprocess.run(
        ["git", "ls-files", "--full-name", "-z"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if files_result.returncode != 0:
        return {}

    tracked_paths = [
        PurePosixPath(value.decode("utf-8"))
        for value in files_result.stdout.split(b"\0")
        if value
    ]
    target_relative = PurePosixPath(project_root.relative_to(repo_root).as_posix())
    target_ancestors = {
        (repo_root / Path(*ancestor.parts)).resolve()
        for ancestor in [target_relative, *target_relative.parents]
    }
    result: dict[str, str] = {}
    for relative_path in tracked_paths:
        path = repo_root / Path(*relative_path.parts)
        if not path.is_file():
            continue
        name = path.name
        under_target = path.resolve().is_relative_to(project_root)
        is_config = (
            name in _CONFIG_NAMES
            or (name.startswith("requirements") and name.endswith(".txt"))
            or name == "conftest.py"
        )
        is_test_source = (
            under_target
            and path.suffix == ".py"
            and (
                "tests" in relative_path.parts
                or "test" in relative_path.parts
                or name.startswith("test_")
                or name.endswith("_test.py")
                or name == "conftest.py"
            )
        )
        if (
            is_config
            and (under_target or path.resolve().parent in target_ancestors)
        ) or is_test_source:
            result[relative_path.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def _fingerprint(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
