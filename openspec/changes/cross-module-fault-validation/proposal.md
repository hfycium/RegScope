## Why

The existing real-project experiment has three known faults, but all three
change `items.py`. We need evidence from other route modules before claiming
that the observed selection behavior is not specific to item endpoints.

## What Changes

- Add two isolated known-fault cases in distinct modules outside `items.py`.
- Reuse the recorded clean-baseline coverage mapping and compare the same four
  strategies: full suite, file-level coverage, Dynamic-only, and Hybrid.
- Record the exact revisions, failing test IDs, selected sets, and limitations.
- Keep the project's clean `master` branch and configured `app` database
  untouched.

## Capabilities

### New Capabilities

- `cross-module-fault-evidence`: reproducible known-fault validation across
  multiple target modules.

### Modified Capabilities

None.

## Impact

- New experiment branches and output artifacts in the existing isolated target
  clone and evaluation directory.
- OpenSpec and experiment documentation in RegScope.
- No production algorithm change or new dependency is intended.

## Acceptance Criteria

- Two isolated fault revisions affect two distinct Python modules other than
  `items.py`.
- Each fault has a named test that passes on the clean base and fails on its
  fault head.
- Hybrid, Dynamic-only, file-level, and full-suite results use the existing
  58-test baseline mapping and report recall and selected counts.
- The target `master` worktree remains clean, the `app` database is untouched,
  and RegScope tests plus strict OpenSpec validation pass.
