from __future__ import annotations

import subprocess
import time
from pathlib import Path


def evaluate_selection(project_root: str | Path, *, python_executable: str | Path, all_tests: list[str], selected_tests: list[str], known_failing_tests: list[str]) -> dict:
    """Execute selected and full regression suites and calculate MVP metrics."""
    root = Path(project_root).resolve()
    selected = sorted(set(selected_tests))
    population = sorted(set(all_tests))
    selected_run = _run_tests(root, python_executable, selected)
    full_run = _run_tests(root, python_executable, population)
    ground_truth = set(known_failing_tests)
    return {
        "schema_version": 1,
        "total_tests": len(population),
        "selected_tests": len(selected),
        "reduction_ratio": 1 - len(selected) / len(population) if population else 0.0,
        "known_failing_tests": sorted(ground_truth),
        "recall": len(set(selected) & ground_truth) / len(ground_truth) if ground_truth else None,
        "selected_run": selected_run,
        "full_run": full_run,
    }


def _run_tests(root: Path, python_executable: str | Path, test_ids: list[str]) -> dict:
    started = time.perf_counter()
    result = subprocess.run([str(python_executable), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", *test_ids], cwd=root, capture_output=True, text=True, check=False)
    return {"elapsed_seconds": round(time.perf_counter() - started, 4), "exit_code": result.returncode}
