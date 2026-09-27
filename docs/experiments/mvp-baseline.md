# MVP experiment report

## Reproduction

Target fixture: `../_regscope-fixture`; interpreter:
`../order-service/.venv/Scripts/python.exe`.

```powershell
python -m regscope.cli run ../_regscope-fixture <base> <head> \
  --python ../order-service/.venv/Scripts/python.exe \
  --known-failing tests/test_orders.py::test_create_order_applies_threshold_cut_after_discounts \
  --output <output-directory>
```

The known failing test is established independently by directly running it at
each head revision. It expects total `550`; both changed revisions return `560`.

## Results

| Scenario | Base → head | Strategy | Selected / total | Reduction | Recall |
|---|---|---:|---:|---:|---:|
| Module-level constant change | `9047fa4 → 4fdfcd9` | conservative fallback | 7 / 7 | 0.00% | 100% |
| Function-body rule change | `9047fa4 → 4262c0c` | coverage intersection | 5 / 7 | 28.57% | 100% |

## Baselines

Full regression is the denominator in both rows. The MVP currently does not
implement a path-match selector or a separately reported dynamic-only selector;
both are **unavailable**, not zero-valued results. The Hybrid function-body case
uses changed-function and affected-endpoint evidence joined with historical
per-test coverage.

## Interpretation and limits

The module-level change deliberately proves the safe failure mode: a global
business constant cannot be assigned to a function, so RegScope runs all tests.
The function-body change proves a positive selection result with no known-test
miss. It still selects five tests because API dependency setup and shared order
creation paths are present in their runtime coverage. Therefore this MVP shows
safe, explainable reduction, not minimal test selection or a general benchmark.
