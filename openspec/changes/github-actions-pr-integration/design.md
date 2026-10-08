# Design: GitHub Actions PR Integration

## Workflow

- Keep the template's existing `Test Backend` full-suite workflow unchanged.
- On pushes to `master`, set up the same Python/uv/PostgreSQL environment,
  collect a baseline mapping at the pushed commit, and cache it under that
  exact commit plus the dependency/runtime configuration hash.
- On pull requests, restore only the cache for `pull_request.base.sha` and the
  same configuration hash. Do not restore a partial/older mapping.
- If the cache is missing, skip RegScope with a clear log message. The existing
  full-suite job still runs.
- If restored, run `regscope run --mapping ... --selected-only`. RegScope checks
  source revision, environment fingerprint, and test inventory; incompatible
  provenance conservatively selects the full current test inventory.
- Check out RegScope using repository/ref Actions variables so the consuming
  repository can select a published RegScope revision without embedding
  credentials or relying on uncommitted local code.

## Trust and failure behavior

- The job has read-only repository permissions and does not run on fork secrets.
- A selector/test failure fails the RegScope job and remains visible alongside
  the full-suite result.
- Missing baseline data is not interpreted as a passing selected-test run; it
  is an explicit skip while full tests remain required.
- The mapping cache contains test metadata/coverage relationships, not secrets.

## Out of scope

- Removing, weakening, or making the existing full test job conditional.
- Claiming CI time savings before measuring the complete added workflow cost.
- Automatically publishing RegScope, editing repository variables, or pushing
  either repository.
