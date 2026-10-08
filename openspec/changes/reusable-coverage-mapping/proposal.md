## Why

The current `run` pipeline recollects per-test coverage on every invocation.
That makes it unsuitable for a PR workflow that should reuse a mapping built
for the base revision.

## What Changes

- Allow the pipeline and CLI to accept an existing `coverage-mapping.json`.
- Add a `collect` CLI command that creates a baseline mapping without running
  impact analysis or the comparison evaluator.
- When supplied, skip coverage collection and continue impact analysis,
  selection, and evaluation against the checked-out target worktree.
- Add an opt-in selected-only mode that skips the full-suite comparison run.
- Keep the current collect-on-run behavior when no mapping is supplied.

## Capabilities

### New Capabilities

- `reusable-coverage-mapping`: run change analysis using a previously collected
  per-test function mapping.

### Modified Capabilities

None.

## Impact

- Update `src/regscope/cli.py`, `src/regscope/pipeline.py`, and pipeline tests.
- No dependency, GitHub Actions workflow, or selection algorithm changes.

## Acceptance Criteria

- `regscope run --mapping <path>` reads the supplied mapping and does not invoke
  coverage collection.
- `regscope collect <target> --output <path>` creates a mapping at the requested
  file path.
- `regscope run --mapping <path> --selected-only` executes the selected tests
  without also executing the full test suite, and returns the selected test
  process exit status to the caller.
- Existing behavior is unchanged when `--mapping` is omitted.
- Evaluation executes selected tests in the target path supplied to the CLI,
  using `--python` when provided.
- Platform tests and strict OpenSpec validation pass.
