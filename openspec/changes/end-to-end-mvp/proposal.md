## Why

RegScope currently has a documented roadmap and an initial V1 implementation,
but it cannot yet answer the complete user question after a code change: which
tests should run, why, and how much work is avoided. Building V1 through V5 as
isolated milestones risks accumulating disconnected prototypes. This change
delivers one small, real, end-to-end path on the existing `order-service`
FastAPI repository so that every later improvement has a measurable baseline.

## What Changes

- Add a path-parameter-driven workflow that collects per-test coverage and
  persists stable `test_id -> function_id` mappings.
- Add Git diff analysis that maps changed Python lines to stable function IDs.
- Add static, explainable tracing from changed functions to FastAPI endpoints
  for direct, synchronous calls in the target service.
- Add a selector that joins static impact and dynamic coverage, reporting the
  selected tests and their evidence.
- Add a small evaluation runner/report that compares full regression, path
  matching, dynamic coverage only, and the hybrid selection where data permits.
- Record implementation evidence and learning notes for each iteration.

## Capabilities

### New Capabilities

- `change-aware-regression-selection`: Analyse one Python/FastAPI target
  repository between two Git commits and produce an explainable test selection
  plus MVP evaluation results.

### Modified Capabilities

- None.

## Impact

- New platform modules under `src/regscope/` and corresponding pytest coverage.
- New command-line entry point(s) that invoke Git, pytest, and coverage in the
  target repository through subprocesses.
- New persisted JSON and Markdown artifacts owned by RegScope, never by the
  target service.
- `order-service` is used as the initial target and experiment fixture; it
  remains a separate repository.
