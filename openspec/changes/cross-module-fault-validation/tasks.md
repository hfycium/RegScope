## 1. Prepare safe cross-module cases

- [x] 1.1 Confirm the selected `users.py` and `login.py` functions and tests are
  present in the saved baseline mapping.
- [x] 1.2 Create two independent fault branches from the clean base without
  changing `master`.
- [x] 1.3 Provision a dedicated test database and apply the target migrations;
  do not use or alter the configured `app` database.

## 2. Verify and compare cases

- [x] 2.1 Verify each known test passes at base and fails at its fault head.
- [x] 2.2 Run full-suite, file-level, Dynamic-only, and Hybrid comparisons using
  the same 58-test baseline mapping.
- [x] 2.3 Verify selected IDs, recall, and execution status in the raw JSON.

## 3. Record evidence

- [x] 3.1 Update the real-project report with revisions, methods, results, and
  the limitation that the evidence covers only two additional route modules.
- [x] 3.2 Confirm target `master` is clean; run RegScope tests and strict
  OpenSpec validation.
