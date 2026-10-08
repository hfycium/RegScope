# Comparative regression-selection experiment

## Purpose and scope

This experiment compares RegScope with explicit baselines on a controlled
FastAPI service. The fixture has 10 tests and four isolated fault commits from
the same baseline. These are synthetic, deliberately introduced faults; this
is evidence about the prototype on this fixture, not a production benchmark.

Fixture: `../_regscope-expanded-fixture`  
Baseline: `9057a37`  
Interpreter: `../order-service/.venv/Scripts/python.exe`

The baseline suite passed all 10 tests. Each fault's named test was then run
independently and failed for the intended behavior.

## Baseline definitions

- **Full suite:** every discovered pytest node ID.
- **File-level coverage:** tests whose coverage mapping contains any function
  from a changed Python module. This is a coverage-based file granularity
  baseline, not test-file-name matching.
- **Dynamic-only:** tests whose runtime function mapping intersects the changed
  function IDs, without endpoint propagation or conservative fallback.
- **Hybrid:** RegScope's current selector using changed-function and affected
  endpoint evidence, including conservative fallback.

All strategies use the mapping collected for that fault head and the same test
population. Recall is the fraction of independently verified failing tests in
the candidate set. Reductions are test-count reductions, not end-to-end time
savings.

## Cases and results

Each cell is `selected / 10 tests (reduction; known-fault recall)`.

| Fault scenario (base `9057a37` → head) | Independently failing test | Full suite | File-level | Dynamic-only | Hybrid |
|---|---|---:|---:|---:|---:|
| Shipping cut constant `→ 40` (`28853b0`) | `test_create_order_applies_threshold_cut_after_discounts` | 10/10 (0%; 100%) | 9/10 (10%; 100%) | 0/10 (100%; 0%) | 10/10 (0%; 100%) |
| Percent discount `90% → 89%` (`f9e63f5`) | `test_create_order_applies_discounts_and_decreases_stock` | 10/10 (0%; 100%) | 9/10 (10%; 100%) | 5/10 (50%; 100%) | 8/10 (20%; 100%) |
| Fixed discount `20 → 21` (`9d140b2`) | `test_fixed_discount_is_applied_to_order_total` | 10/10 (0%; 100%) | 9/10 (10%; 100%) | 5/10 (50%; 100%) | 8/10 (20%; 100%) |
| Quantity limit `10 → 9` (`9f8d7c2`) | `test_quantity_limit_allows_exactly_ten_items` | 10/10 (0%; 100%) | 9/10 (10%; 100%) | 0/10 (100%; 0%) | 10/10 (0%; 100%) |

The two constant changes are module-level. The function-only baseline has no
changed function to intersect and selects nothing, so it misses the known
failures. Hybrid detects the incomplete mapping and falls back to the full
suite. The file-level baseline catches these cases but saves only one test.
For function-body faults, the hybrid method selects 8 tests, while
function-only selects 5; the hybrid's endpoint evidence is more conservative.

## Observed runtime

One selected-suite and one full-suite wall-clock observation were recorded per
strategy and case. Non-empty runs were approximately 1.00–1.08 seconds in this
environment. Empty function-only selections were skipped (0 seconds) rather
than passed to pytest. Each case has only one timing sample, so no speedup
conclusion is warranted. More importantly, coverage mapping itself executes
every test individually and is excluded from selected-suite time.

## Reproduction

The four fault branches are `expanded-fault-threshold`,
`expanded-fault-product-discount`, `expanded-fault-fixed-discount`, and
`expanded-fault-quantity`. Each branches from `expanded-baseline` at `9057a37`.
Check out the branch matching the desired head before running the commands.

```powershell
$env:PYTHONPATH = "src"
$target = "..\_regscope-expanded-fixture"
$python = "..\order-service\.venv\Scripts\python.exe"
$head = "<fault-head>"
$case = "<case-name>"
$known = "<known-failing-pytest-node-id>"

& .\.venv\Scripts\python.exe -m regscope.cli run `
  $target 9057a37 $head --python $python `
  --known-failing $known --output ".regscope-experiment-output\$case"

& .\.venv\Scripts\python.exe -m regscope.experiment_cli `
  --mapping ".regscope-experiment-output\$case\coverage\coverage-mapping.json" `
  --impact ".regscope-experiment-output\$case\impact.json" `
  --python $python --known-failing $known `
  --output ".regscope-experiment-output\$case\comparison.json"
```

The comparison command writes the exact baseline definitions, selected IDs,
counts, reduction, recall, exit codes, and observed elapsed time to JSON.
