## Why

The MVP result is based on one seven-test service and one independently known
failure, so a 100% recall result is too weak to assess selection quality. The
existing report also lacks explicit file-level and dynamic-only comparisons.
This change adds controlled fault cases and reproducible baselines so the
project can state what the prototype did and did not demonstrate.

## What Changes

- Add a separate, reproducible target fixture with several known-failing
  business changes and matching tests.
- Compare full-suite, file-level coverage, dynamic-only, and
  the existing static-plus-dynamic selector on identical test mappings.
- Record per-case selected count, reduction, known-failure recall, and observed
  execution time; label sample limitations explicitly.
- Do not alter RegScope's selection algorithm or claim production-level benefit.

## Capabilities

### New Capabilities

- `comparative-regression-evaluation`: reproducible fault cases and like-for-like
  evaluation of explicitly defined test-selection baselines.

### Modified Capabilities

None.

## Impact

- New experiment tooling and report under `docs/experiments/`.
- A separate sibling fixture repository; the user's `order-service` working
  tree and the existing `_regscope-fixture` must remain unchanged.
- No runtime dependencies or changes to RegScope's production selection flow.
