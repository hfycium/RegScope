## 1. Establish reproducible target baseline

- [x] 1.1 Audit `../order-service` routes, tests, dependencies, and Git history;
  document the exact target revision pair and experiment assumptions.
- [x] 1.2 Add only the missing target-service tests or fixture commits required
  to exercise at least one changed business function and one unaffected path.
- [x] 1.3 Add an integration test that validates RegScope can locate a target
  repository by path without importing its application modules.

## 2. Complete dynamic test-to-function collection

- [x] 2.1 Implement target test discovery with stable pytest node IDs.
- [x] 2.2 Run each selected target test through subprocess pytest and coverage,
  then write deterministic `coverage-mapping.json` output.
- [x] 2.3 Cover empty coverage, failed tests, malformed coverage reports,
  Windows paths, and target paths outside RegScope.
- [x] 2.4 Provide a query/read API or CLI view for one test's mapped functions.

## 3. Detect code changes and endpoint impact

- [x] 3.1 Implement Git commit validation and changed-line extraction for a
  target repository.
- [x] 3.2 Map changed lines in Python `app/` source to changed function IDs and
  report changed module-level code separately.
- [x] 3.3 Discover FastAPI endpoints and construct a bounded direct-call graph.
- [x] 3.4 Traverse reverse paths from each changed function to endpoints;
  persist paths and unresolved-analysis warnings in `impact.json`.
- [x] 3.5 Add unit and integration tests for direct calls, no-impact changes,
  nested functions, async endpoints, and conservative fallback behavior.

## 4. Select tests and explain results

- [x] 4.1 Define a deterministic selector joining changed functions, affected
  endpoints, and per-test function mappings.
- [x] 4.2 Emit `selection.json` with selected/unselected node IDs and one or
  more evidence records per selected test.
- [x] 4.3 Implement and test conservative fallback for incomplete mappings or
  unresolved static analysis.
- [x] 4.4 Add a CLI command that accepts target path, base/head commits,
  mapping path, and output directory.

## 5. Evaluate and document the MVP

- [x] 5.1 Create a repeatable known-change or known-failing-test experiment in
  the target repository without mixing its code into RegScope.
- [x] 5.2 Measure full regression, path match, dynamic-only, and hybrid
  selection when each method is implementable; report unavailable baselines
  explicitly instead of fabricating metrics.
- [x] 5.3 Calculate and report test reduction ratio, elapsed test time, and
  failing-test recall with inputs recorded for reproduction.
- [x] 5.4 Run the full RegScope and target test suites; validate OpenSpec and
  write the final MVP iteration report.
