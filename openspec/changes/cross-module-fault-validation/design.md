## Context

Three completed fault scenarios in the full-stack FastAPI target all changed
`backend/app/api/routes/items.py`. The clean baseline mapping contains
coverage for `users.py` and `login.py` as well, so two independently failing
route changes can test whether the experiment generalizes beyond items.

The target's pytest session fixture deletes user and item rows from its
configured database at teardown. Its `.env` currently points to a database
named `app`; experiments must therefore run against a newly created,
dedicated database, never against that configured database.

## Goals / Non-Goals

**Goals:**

- Test one authorization behavior in `users.py` and one login error behavior
  in `login.py`.
- Reuse the fixed 58-test clean-baseline coverage mapping.
- Compare all four strategies with known-failure ground truth.

**Non-Goals:**

- Change RegScope's selection algorithm or the upstream project's `master`.
- Claim broad generalization from two additional cases.
- Modify or clean the existing `app` database.

## Decisions

1. **Use separate Git branches from the recorded base.** Each branch contains
   one fault so changes do not accumulate and results remain attributable.
2. **Use existing tests as ground truth.** The permission test in
   `test_users.py` and invalid-password test in `test_login.py` already assert
   the intended behavior; no test is added just to make the selector appear
   successful.
3. **Create a disposable database for test execution.** The target's fixture
   deletes rows during teardown. Reusing the configured `app` database would
   risk user data, so create a uniquely named database and leave the configured
   one unchanged.
4. **Reuse the clean baseline mapping.** The test population and historical
   coverage stay fixed across fault cases, making strategy counts comparable.

## Risks / Trade-offs

- **Fault is caught by only one existing test →** report exact ground truth and
  avoid general accuracy claims.
- **Hybrid static paths may omit router prefixes →** compare using function IDs
  and test selection; disclose that endpoint path display remains incomplete.
- **Database creation permission unavailable →** stop before test execution and
  request a safe isolated test database rather than using `app`.

## Migration Plan

No product migration. Add two experiment branches, run named tests and
comparisons against the dedicated database, update the report, and return the
target worktree to its clean `master` branch.

## Open Questions

None; the candidate modules and test cases are identified from the existing
baseline mapping and test suite.
