## Context

RegScope can now create a mapping and run with `--mapping --selected-only`,
but the mapping has no source revision or environment identity. A CI job could
therefore use data from the wrong base, Python environment, dependencies, or
test inventory.

## Goals / Non-Goals

**Goals:**

- Stamp newly collected mappings with source commit and a reproducible
  environment/test inventory fingerprint.
- Verify compatibility before using a saved mapping.
- Run all current tests when the map cannot be proven compatible.

**Non-Goals:**

- Store or transfer mappings between GitHub Actions runs.
- Fingerprint secrets, databases, or arbitrary external services.
- Change the Hybrid selection algorithm.

## Decisions

1. Add a `provenance` object to mapping schema version 1. It contains the
   resolved `HEAD` commit, a SHA-256 environment fingerprint, and a SHA-256
   test-ID inventory fingerprint. Older schema-version-1 mappings remain
   readable but have no trusted provenance.
2. Build the environment fingerprint from target Python version and
   implementation, OS family and architecture, versions of pytest and
   coverage.py, plus tracked dependency/pytest configuration and test source
   files in the target project and its ancestor directories.
3. At `run --mapping`, resolve the requested base commit, rediscover test IDs,
   and recompute the environment fingerprint. Trust the mapping only if all
   three provenance values match and its mapped test IDs equal the discovered
   inventory.
4. On any mismatch, create a conservative selection containing every current
   test ID and record the reasons in `selection.json`. The normal selected-only
   evaluation then executes that complete set and propagates its exit status.
5. Keep the path-based target interpreter override. The mapping's recorded
   interpreter path is not part of the fingerprint, so mappings are portable
   between workspaces running the same Python/runtime and dependencies.

## Risks / Trade-offs

- Fingerprinting is intentionally conservative: changing test sources or
  dependency/configuration inputs causes a full-test fallback.
- External services and secret-provided configuration are not fingerprinted;
  workflow authors must keep those stable or choose full-suite execution.
- Filesystem metadata is read from the current checkout, while source revision
  is resolved from Git. CI checkouts should be clean and correspond to their
  advertised commits.

## Migration Plan

No data migration. Existing mappings without provenance trigger a conservative
full-test fallback when reused. Regenerate them with `regscope collect` to
enable precise selection.

## Open Questions

None for this scoped change.
