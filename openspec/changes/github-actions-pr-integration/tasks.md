## 1. Specify and implement the consuming-repository workflow

- [x] 1.1 Document workflow behavior and safety requirements in OpenSpec.
- [x] 1.2 Add an isolated GitHub Actions workflow to the FastAPI template branch.
- [x] 1.3 Add an installable `regscope` console command for the consumer workflow.
- [ ] 1.4 Publish a RegScope revision containing reusable mapping and provenance support.
- [ ] 1.5 Configure `REGSCOPE_REPOSITORY` and `REGSCOPE_REF` in the target repository.

## 2. Validate end to end

- [x] 2.1 Validate workflow with actionlint and OpenSpec changes with strict validation.
- [ ] 2.2 Run a default-branch push to populate the exact-revision baseline cache.
- [ ] 2.3 Open a PR and verify selected tests execute; verify stale/missing mapping
  behavior remains conservative and the full backend workflow still runs.
- [ ] 2.4 Record hosted selected-vs-total tests, elapsed time, and the full-suite result in the Actions run.
