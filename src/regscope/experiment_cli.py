from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate_strategy_sets
from .experiment import build_comparative_selections


def run_comparison(mapping_path: str | Path, impact_path: str | Path, *, python_executable: str | Path, known_failing_tests: list[str], output_path: str | Path) -> dict:
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    impact = json.loads(Path(impact_path).read_text(encoding="utf-8"))
    strategy_tests = build_comparative_selections(mapping, impact)
    result = evaluate_strategy_sets(
        mapping["target_root"],
        python_executable=python_executable,
        all_tests=[entry["test_id"] for entry in mapping["mappings"]],
        strategy_tests=strategy_tests,
        known_failing_tests=known_failing_tests,
    )
    result["definitions"] = {
        "full-suite": "Run every discovered pytest node ID.",
        "file-level-coverage": "Select tests whose function mapping contains any changed Python module.",
        "dynamic-only": "Select tests whose runtime function mapping intersects changed function IDs only.",
        "hybrid": "Use RegScope's current changed-function and affected-endpoint selector.",
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(prog="regscope-compare")
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--impact", required=True)
    parser.add_argument("--python", dest="python_executable", required=True)
    parser.add_argument("--known-failing", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_comparison(
        args.mapping,
        args.impact,
        python_executable=args.python_executable,
        known_failing_tests=args.known_failing,
        output_path=args.output,
    )
    print(f"total={result['total_tests']} strategies={len(result['strategies'])} output={args.output}")


if __name__ == "__main__":
    main()
