## Context

The initial experiment used a seven-test FastAPI target and one known failing
test. It reported hybrid selection against full regression, without file-level
or Dynamic-only comparisons. The expanded experiment isolates target changes
from both the platform repository and the user's active `order-service`
worktree.

## Goals / Non-Goals

**Goals:**

- Build multiple controlled fault cases with independently identified failing
  tests.
- Compare all strategies using the same test population and per-test coverage
  data.
- Make all baseline definitions and limitations reproducible.

**Non-Goals:**

- Change the hybrid selector or claim it is generally superior.
- Treat synthetic mutations as representative production defects.
- Claim net CI-time savings from test counts alone; coverage acquisition cost
  remains separate.

## Decisions

1. **Use a new sibling fixture clone.** Keep the existing fixture and the
   developer's `order-service` untouched. Commit a test-enriched baseline, then
   branch each fault case from that baseline so every comparison has one
   isolated change.
2. **Define baselines from the same coverage mapping.** File-level coverage
   selects tests that executed any function in a changed Python module;
   dynamic-only selects tests whose mapping intersects the changed
   function IDs; hybrid uses the existing selector's changed-function and
   affected-endpoint evidence; full-suite selects every discovered test.
3. **Keep the comparison harness experiment-only.** It consumes saved impact
   and coverage artifacts and reports candidate sets and metrics without
   adding new selection modes to the public CLI.
4. **Separate effectiveness from cost.** Report selected-suite elapsed time
   alongside full-suite elapsed time, but disclose that per-test coverage
   collection runs the whole population and is excluded from those timings.

## Risks / Trade-offs

- **Small synthetic suite →** disclose exact cases and avoid general claims.
- **Timing noise →** record wall-clock values as observations, not stable
  performance claims; selected test counts and recall are primary metrics.
- **Baseline naming ambiguity →** specify the file-level rule and function ID
  intersection in the report.

## Migration Plan

No runtime migration. Create a sibling fixture, run the experiment harness,
review artifacts, and update the report. The fixture can be removed without
changing RegScope; preserve it for reproduction.

## Open Questions

None. The exact fault cases and baseline definitions are fixed in the spec.
