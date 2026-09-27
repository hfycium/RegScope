from __future__ import annotations

import argparse

from .pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(prog="regscope")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="collect coverage, analyse impact, and select tests")
    run.add_argument("target")
    run.add_argument("base")
    run.add_argument("head")
    run.add_argument("--output", required=True)
    run.add_argument("--python", dest="python_executable")
    run.add_argument("--known-failing", action="append", default=[])
    args = parser.parse_args()
    result = run_pipeline(args.target, args.base, args.head, args.output, python_executable=args.python_executable, known_failing_tests=args.known_failing)
    print(f"strategy={result['selection']['strategy']} selected={len(result['selection']['selected_tests'])}")


if __name__ == "__main__":
    main()
