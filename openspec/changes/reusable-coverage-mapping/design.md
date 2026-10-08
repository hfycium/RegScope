## Context

`run_pipeline()` currently performs coverage collection, impact analysis,
selection, and evaluation in one call. CI needs to collect a baseline mapping
once and reuse it when analyzing later changes.

## Goals / Non-Goals

**Goals:**

- Provide a standalone `collect` command that writes the mapping to an explicit
  file path.
- Add an optional mapping-file input to the existing `run` command.
- Add an explicit selected-only option for operational runs that should avoid
  the full-suite comparison.
- Preserve collection behavior when no mapping file is provided.
- Keep all downstream paths and test execution rooted at the current target
  worktree, not at the machine-specific path recorded in the mapping.

**Non-Goals:**

- Add a GitHub Actions workflow or baseline artifact storage.
- Change coverage mapping format or selection behavior.
- Claim that reusing a mapping alone provides net CI time savings.

## Decisions

1. Add an optional `mapping_path` keyword to `run_pipeline()` and a `--mapping`
   CLI option. If present, load the JSON mapping rather than calling the
   collector; otherwise retain the existing collector call.
2. Add `collect <target> --output <file>` as a small wrapper around the existing
   collector. The mapping is written exactly at the requested path; per-test
   coverage details remain beside it in the output directory.
3. Add `--selected-only` as an explicit opt-in. By default, retain the existing
   full-suite comparison; when enabled, represent that run as skipped in the
   evaluation output, execute only the selected set, and propagate its pytest
   exit status as the CLI exit status.
4. Continue to use the target path passed to `run` for impact analysis and test
  evaluation. The target Python interpreter comes from `--python` when given,
  otherwise from the mapping's recorded interpreter.
5. Copy the supplied mapping into the output directory so the run remains
  self-contained and auditable.
6. Reject unsupported or structurally invalid mapping JSON with a clear
   `ValueError` before selection starts.

## Risks / Trade-offs

- A syntactically valid mapping may be stale or belong to a different test
  suite. This change validates its shape only; future CI work must key mappings
  by base commit and environment/dependency identity.
- Selected-only mode removes the full-suite comparison data for that run; it
  should be used for operational CI, while experiments should keep the default.
- The serialized interpreter path may not exist on another machine. CI callers
  should pass the target interpreter explicitly with `--python`.

## Migration Plan

No migration. Existing `run` invocations continue collecting coverage as
before. Users opt into reuse by passing a compatible mapping file.

## Open Questions

None for this change; mapping freshness and artifact lifecycle belong to the
subsequent CI integration work.
