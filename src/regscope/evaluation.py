from __future__ import annotations

import subprocess
import time
from pathlib import Path


def evaluate_selection(project_root: str | Path, *, python_executable: str | Path, all_tests: list[str], selected_tests: list[str], known_failing_tests: list[str], run_full_suite: bool = True) -> dict:
    """Execute selected and full regression suites and calculate MVP metrics."""
    root = Path(project_root).resolve()
    selected = sorted(set(selected_tests))
    population = sorted(set(all_tests))
    selection_fallback = not selected and bool(population)
    if selection_fallback:
        selected = population
    selected_run = _run_tests(root, python_executable, selected)
    full_run = (
        _run_tests(root, python_executable, population)
        if run_full_suite
        else {
            "elapsed_seconds": 0.0,
            "exit_code": None,
            "skipped": True,
            "reason": "Full-suite comparison disabled",
        }
    )
    ground_truth = set(known_failing_tests)
    return {
        "schema_version": 1,
        "total_tests": len(population),
        "selected_tests": len(selected),
        "selection_fallback": selection_fallback,
        "reduction_ratio": 1 - len(selected) / len(population) if population else 0.0,
        "known_failing_tests": sorted(ground_truth),
        "recall": len(set(selected) & ground_truth) / len(ground_truth) if ground_truth else None,
        "selected_run": selected_run,
        "full_run": full_run,
    }


def evaluate_strategy_sets(project_root: str | Path, *, python_executable: str | Path, all_tests: list[str], strategy_tests: dict[str, list[str]], known_failing_tests: list[str]) -> dict:
    """Evaluate named candidate sets, preserving intentional empty baselines."""
    root = Path(project_root).resolve()
    population = sorted(set(all_tests))
    ground_truth = set(known_failing_tests)
    results = {}
    for strategy, candidates in sorted(strategy_tests.items()):
        selected = sorted(set(candidates))
        selected_run = _run_tests(root, python_executable, selected)
        results[strategy] = {
            "selected_test_ids": selected,
            "selected_tests": len(selected),
            "reduction_ratio": 1 - len(selected) / len(population) if population else 0.0,
            "known_failing_tests": sorted(ground_truth),
            "recall": len(set(selected) & ground_truth) / len(ground_truth) if ground_truth else None,
            "selected_run": selected_run,
        }
    return {
        "schema_version": 1,
        "total_tests": len(population),
        "strategies": results,
        "full_run": _run_tests(root, python_executable, population),
    }


def _run_tests(root: Path, python_executable: str | Path, test_ids: list[str]) -> dict:
    if not test_ids:
        return {"elapsed_seconds": 0.0, "exit_code": 0, "skipped": True, "reason": "No tests were provided"}
    started = time.perf_counter()
    result = subprocess.run([str(python_executable), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", *test_ids], cwd=root, capture_output=True, text=True, check=False)
    return {"elapsed_seconds": round(time.perf_counter() - started, 4), "exit_code": result.returncode}
