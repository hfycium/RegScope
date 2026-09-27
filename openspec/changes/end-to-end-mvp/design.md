## Context

The current repository contains a minimal V1 foundation:
`map_executed_lines_to_functions` parses Python source with `ast`, while
`build_test_function_mapping` converts one coverage JSON report into stable
function identifiers under a target project's `app/` directory. The companion
`../order-service` repository provides the FastAPI service, pytest tests, and
Git history. The platform and target must remain separate repositories.

## Goals / Non-Goals

**Goals:**

- Run the full pipeline for one target repository and two commits.
- Make every selected test explainable with changed functions, affected endpoint
  paths, or historical coverage evidence.
- Persist deterministic machine-readable artifacts and render a readable report.
- Produce a small repeatable experiment with reduction ratio, execution time,
  and recall when a known failing-test fixture is available.

**Non-Goals:**

- Multi-language, cross-repository, distributed, UI, CI-platform, or AI test
  generation support.
- Complete Python semantic analysis, reflection, monkey patching, background
  tasks, or arbitrary dynamic dispatch.
- Database or Redis persistence; local JSON artifacts are sufficient for MVP.
- V6 enhancements such as mutation testing beyond the minimum evaluation data.

## Decisions

1. **Use one vertical workflow, not six independent implementations.** Each
   component must feed the next one before moving on; this produces a useful
   result earlier and exposes contract mismatches immediately.
2. **Use stable IDs.** Tests use pytest node IDs and functions use
   `<project-relative-module>:<qualified-function>`. JSON lists are sorted so
   output is reproducible and diffs are reviewable.
3. **Execute target tests via subprocess.** RegScope never imports the target
   service, preserving the separate-repository decision and avoiding dependency
   coupling.
4. **Start with explicit boundaries.** Only Python source inside the target
   `app/` directory, direct calls resolvable by the selected AST approach, and
   FastAPI-decorated endpoint functions participate in static impact analysis.
   Unresolved calls are reported as limitations rather than silently assumed
   safe.
5. **Use conservative selection.** If analysis cannot confidently map a changed
   business function, the result must disclose that uncertainty and select a
   safe fallback set rather than claim precision.
6. **Keep artifacts beneath a caller-selected output directory.** Generated
   coverage, mappings, selections, and reports must not pollute either source
   repository by default.

## Pipeline and artifacts

```text
target path + base commit + head commit
  -> Git diff -> changed-function IDs
  -> AST call graph + FastAPI route discovery -> affected endpoints + paths
  -> per-test pytest/coverage -> test-to-function JSON
  -> selector -> selected tests + evidence JSON
  -> test execution + metrics -> Markdown/JSON report
```

The workflow will produce at least these artifacts:

- `coverage-mapping.json`: target revision, collection timestamp, and sorted
  test-to-function mappings.
- `impact.json`: base/head commits, changed files/functions, affected endpoints,
  and explainable reverse-call paths.
- `selection.json`: selected and unselected tests, reason records, and fallback
  status.
- `evaluation.json` and `evaluation.md`: population size, selected count,
  reduction ratio, elapsed times, failing-test ground truth, and recall.

## Risks / Trade-offs

- Line coverage includes import and initialization noise. The existing mapper
  excludes non-function lines but cannot prove a test asserted a business
  outcome; tests must have explicit assertions and results must state this
  limitation.
- AST-only call resolution misses aliases, dependency injection, inheritance,
  and dynamic calls. The MVP reports unresolved links and retains a conservative
  fallback rather than overstating confidence.
- Per-test coverage can be slow. It is intentionally acceptable for the small
  target baseline; timing is recorded so later optimization is evidence-driven.
- Comparing arbitrary commits requires both revisions to be available in the
  target Git repository. The runner validates this before writing a result.
