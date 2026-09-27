from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


_PYTEST_NODE_ID = re.compile(r"^\S+\.py(?:::.+)+$")


def resolve_target_python(
    project_root: str | Path,
    python_executable: str | Path | None = None,
) -> Path:
    """Find the Python interpreter used to run tests in a target project."""
    if python_executable is not None:
        return Path(python_executable)

    root = Path(project_root).resolve()
    candidates = (
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), Path(sys.executable))


def discover_test_ids(
    project_root: str | Path,
    *,
    python_executable: str | Path | None = None,
) -> list[str]:
    """Return sorted, stable pytest node IDs collected from a target project."""
    root = Path(project_root).resolve()
    interpreter = resolve_target_python(root, python_executable)
    # A target may configure ``addopts = -q``. Combined quiet flags can make
    # pytest print only per-file counts, so explicitly clear addopts here while
    # retaining other project configuration such as ``pythonpath``.
    command = [
        str(interpreter),
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "-o",
        "addopts=",
    ]
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "pytest collection failed"
        raise RuntimeError(f"Could not collect tests from {root}: {message}")

    test_ids = _parse_pytest_node_ids(result.stdout)
    if not test_ids:
        raise RuntimeError(f"Pytest collected no test IDs from {root}")
    return test_ids


def _parse_pytest_node_ids(output: str) -> list[str]:
    """Extract node IDs from ``pytest --collect-only -q`` output."""
    return sorted(
        {
            line.strip()
            for line in output.splitlines()
            if _PYTEST_NODE_ID.fullmatch(line.strip())
        }
    )
