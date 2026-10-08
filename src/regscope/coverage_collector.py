from __future__ import annotations

import hashlib
import os
import subprocess
from collections.abc import Iterable
from pathlib import Path

from .coverage_mapper import build_test_function_mapping
from .mapping_provenance import create_mapping_provenance
from .test_discovery import discover_test_ids, resolve_target_python


def collect_test_function_mappings(
    project_root: str | Path,
    output_dir: str | Path,
    *,
    python_executable: str | Path | None = None,
    test_ids: Iterable[str] | None = None,
    allow_test_failures: bool = False,
    mapping_path: str | Path | None = None,
) -> dict:
    """Collect and persist deterministic function coverage for target pytest tests."""
    root = Path(project_root).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    coverage_dir = output / "per-test-coverage"
    coverage_dir.mkdir(exist_ok=True)

    interpreter = resolve_target_python(root, python_executable)
    if test_ids is None:
        selected_test_ids = discover_test_ids(root, python_executable=interpreter)
    else:
        selected_test_ids = sorted(set(test_ids))
    if not selected_test_ids:
        raise ValueError("At least one test ID is required to collect coverage")

    mappings: list[dict] = []
    for index, test_id in enumerate(selected_test_ids, start=1):
        digest = hashlib.sha256(test_id.encode("utf-8")).hexdigest()[:12]
        coverage_data = coverage_dir / f"{index:04d}-{digest}"
        coverage_json = coverage_dir / f"{index:04d}-{digest}.json"
        environment = os.environ | {"COVERAGE_FILE": str(coverage_data)}

        _run_checked(
            [
                str(interpreter),
                "-m",
                "coverage",
                "run",
                "--source=app",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "-o",
                "addopts=",
                test_id,
            ],
            cwd=root,
            env=environment,
            action=f"collect coverage for {test_id}",
            allow_failure=allow_test_failures,
        )
        _run_checked(
            [str(interpreter), "-m", "coverage", "json", "-o", str(coverage_json)],
            cwd=root,
            env=environment,
            action=f"write coverage JSON for {test_id}",
        )
        try:
            mapping = build_test_function_mapping(
                test_id=test_id,
                coverage_json_path=coverage_json,
                project_root=root,
            )
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Could not map coverage for {test_id}: {exc}") from exc
        mappings.append(mapping)

    result = {
        "schema_version": 1,
        "target_root": str(root),
        "python_executable": str(interpreter),
        "mappings": mappings,
        "provenance": create_mapping_provenance(
            root, interpreter, selected_test_ids
        ),
    }
    mapping_output = (
        Path(mapping_path).resolve()
        if mapping_path is not None
        else output / "coverage-mapping.json"
    )
    mapping_output.parent.mkdir(parents=True, exist_ok=True)
    mapping_output.write_text(_as_json(result), encoding="utf-8")
    return result


def _run_checked(command: list[str], *, cwd: Path, env: dict[str, str], action: str, allow_failure: bool = False) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise RuntimeError(f"Could not {action}: {message}")


def _as_json(value: dict) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
