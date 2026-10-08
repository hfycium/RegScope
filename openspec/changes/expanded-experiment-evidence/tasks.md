## 1. Establish isolated experiment fixture

- [x] 1.1 Create a new sibling fixture without changing `order-service` or
  `_regscope-fixture`.
- [x] 1.2 Add focused regression tests and at least four isolated known-fault
  revisions spanning at least three business behaviors.
- [x] 1.3 Independently run each fault's named test and record its failing node
  ID and expected/actual behavior.

## 2. Implement comparative experiment harness

- [x] 2.1 Define and unit-test file-level, dynamic-only, and hybrid
  candidate sets over one shared coverage mapping.
- [x] 2.2 Execute each candidate set and full suite safely; handle empty sets
  without accidentally invoking pytest discovery.
- [x] 2.3 Report selected count, reduction, recall, exit statuses, and elapsed
  times per strategy and fault case.

## 3. Reproduce and document evidence

- [x] 3.1 Run all fault cases and verify expected ground truth and artifacts.
- [x] 3.2 Update the experiment report with baseline definitions, results,
  reproduction commands, and limitations; do not claim general accuracy or net
  end-to-end speedup.
- [x] 3.3 Run platform tests and strict OpenSpec validation.
