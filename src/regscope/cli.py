from __future__ import annotations

import argparse
from pathlib import Path

from .coverage_collector import collect_test_function_mappings
from .pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(prog="regscope")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="collect and save per-test coverage mappings")
    collect.add_argument("target")
    collect.add_argument("--output", required=True, help="path for coverage-mapping.json")
    collect.add_argument("--python", dest="python_executable")

    run = subparsers.add_parser("run", help="collect or reuse coverage, analyse impact, and select tests")
    run.add_argument("target")
    run.add_argument("base")
    run.add_argument("head")
    run.add_argument("--output", required=True)
    run.add_argument("--python", dest="python_executable")
    run.add_argument("--mapping", dest="mapping_path", help="reuse a saved coverage-mapping.json")
    run.add_argument("--selected-only", action="store_true", help="run selected tests without the full-suite comparison")
    run.add_argument("--known-failing", action="append", default=[])
    args = parser.parse_args()
    if args.command == "collect":
        mapping = collect_test_function_mappings(
            args.target,
            Path(args.output).resolve().parent,
            python_executable=args.python_executable,
            mapping_path=args.output,
        )
        print(f"tests={len(mapping['mappings'])} mapping={Path(args.output).resolve()}")
        return

    result = run_pipeline(args.target, args.base, args.head, args.output, python_executable=args.python_executable, mapping_path=args.mapping_path, selected_only=args.selected_only, known_failing_tests=args.known_failing)
    print(f"strategy={result['selection']['strategy']} selected={len(result['selection']['selected_tests'])}")
    if args.selected_only:
        raise SystemExit(result["evaluation"]["selected_run"]["exit_code"] or 0)


if __name__ == "__main__":
    main()
