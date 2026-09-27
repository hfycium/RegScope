# 001 — End-to-end MVP iteration record

## Purpose

This document is the learning and evidence companion to OpenSpec change
[`end-to-end-mvp`](../../openspec/changes/end-to-end-mvp/). OpenSpec defines the
contract; this record captures what was actually tried, observed, decided, and
verified while meeting that contract.

## Locked scope

- **Goal:** on one separate Python/FastAPI target repository, run `Git diff ->
  changed functions -> affected API -> selected pytest tests -> evaluation`.
- **In scope:** Python 3.12, FastAPI, pytest, coverage.py, Git, local JSON and
  Markdown artifacts, direct synchronous calls, and source rooted at `app/`.
- **Out of scope:** V6 enhancements, UI, CI integration, multi-language and
  cross-repository analysis, distributed execution, test generation, database
  persistence, and comprehensive dynamic-call resolution.
- **Primary target:** sibling repository `../order-service`; it remains outside
  this repository and is addressed exclusively through a path parameter.

## Baseline observed before implementation

| Item | Observation | Evidence |
|---|---|---|
| Platform status | Project documents V0–V6; implementation has an initial V1 mapper only. | `PROJECT.md`, `ROADMAP.md`, `src/regscope/` |
| Dynamic mapping | Executed coverage lines are mapped to qualified function IDs using `ast`. | `src/regscope/function_mapper.py` |
| Mapping wrapper | One coverage JSON is converted to `{test_id, functions}`, limited to `app/`. | `src/regscope/coverage_mapper.py` |
| Platform tests | 9 unit tests passed before this plan was recorded. | `.venv\\Scripts\\python.exe -m pytest` |
| Target boundary | `order-service` is a separate FastAPI/pytest Git repository. | `docs/decisions/0001-separate-repositories.md` |

## Iteration log

### 2026-09-27 — Plan recorded

**Decision.** Deliver V0–V5 as one deliberately narrow vertical slice rather
than treating each roadmap heading as a separate finished product.

**Why.** A mapping module alone cannot show whether regression selection is
correct. The smallest meaningful proof needs an input change, impact analysis,
selection evidence, and an observed evaluation result.

**Artifacts created.**

- `openspec/changes/end-to-end-mvp/`: proposal, design, requirements, tasks.
- `openspec/specs/`: reserved for the post-implementation source of truth.
- This document: implementation evidence and learning record.

**Operational note.** OpenSpec CLI 1.6.0 is installed. On this Windows host the
PowerShell `.ps1` launcher is blocked by execution policy; use `openspec.cmd`
instead. OpenSpec initialized its project structure, but could not write global
Codex prompt files because the user profile is protected. Project-local OpenSpec
artifacts are unaffected.

### 2026-09-27 — Target baseline audited

**Question / hypothesis.** Does the sibling `order-service` repository provide
an isolated, repeatable FastAPI/pytest target and a useful Git revision pair?

**Observed target.** The service contains 11 routes: `GET /hello`; user create,
list, and get; product create, list, get, and stock update; and order create,
list, and get. Its API layer delegates to service classes, whose business logic
uses in-memory repositories. The suite contains seven pytest tests, including
success, discount, threshold-cut, insufficient-stock, missing-resource, and
quantity-limit paths.

**Commands run.**

```powershell
git -C ../order-service log --oneline --decorate --all
git -C ../order-service diff --check
.\\.venv\\Scripts\\python.exe -m pytest
```

**Result.** All 7 tests passed in 1.46 seconds. The available commits are
`eb8942c` (initialisation), `07d2ac0` (service baseline), and `9047fa4`
(ignore local agent notes). The pair `07d2ac0 -> 9047fa4` is a valid
no-business-impact control because it changes only `.gitignore`; it must not be
used as the recall fixture. The target's working tree additionally has
uncommitted changes to `.gitignore`, `pyproject.toml`, and `uv.lock`; these are
not owned by this iteration.

**Decision and trade-off.** The original target directory will be read-only for
RegScope development. A separate Git worktree rooted at the clean `9047fa4`
revision will later host controlled business-change commits and experiment
execution. This creates the required known-change data without discarding,
committing, or mixing the user's target-service work.

**Learning note.** A regression-selection evaluation needs two different kinds
of Git change. A non-business change checks that the analyser does not invent
impact; a small business-rule change with a known failing test checks recall.
Using a worktree keeps both experiments reproducible and protects the developer's
active working tree.

**Next boundary.** Create the isolated target worktree and a single controlled
business-rule change only after the dynamic-mapping input contract is settled.

### 2026-09-27 — Stable pytest node-ID discovery implemented

**Question / hypothesis.** Can RegScope obtain a deterministic test list from a
target project without importing its app modules or relying on pytest's human
summary output?

**Change.** Added `src/regscope/test_discovery.py`. It resolves an explicitly
provided target interpreter, otherwise prefers the target virtual environment,
and invokes `python -m pytest --collect-only -q -o addopts=` in the target
directory. It parses only syntactically valid Python pytest node IDs, then
deduplicates and sorts them. Added four tests for parsing, command construction,
collection errors, and virtual-environment selection.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
.\\.venv\\Scripts\\python.exe -c "... discover_test_ids('../order-service') ..."
```

**Result.** The platform suite passed: 13 tests in 0.10 seconds. Real discovery
returned all seven `order-service` node IDs. The first real attempt returned no
IDs because the target's `addopts = -q` combined with the collector's `-q` and
pytest 9 printed only per-file counts. Clearing only `addopts` restores node-ID
output while retaining target settings such as `pythonpath`.

**Decision and trade-off.** Test discovery deliberately overrides `addopts` for
collection. This avoids parsing presentation-dependent summaries, but means any
target that requires test-selection flags inside `addopts` will need an explicit
future configuration option. The MVP prioritises complete stable discovery over
respecting optional quiet/filter flags.

**Learning note.** A pytest node ID, such as
`tests/test_orders.py::test_create_order_applies_threshold_cut_after_discounts`,
is the stable handle needed to run one test later. Tool output meant for people
is not a reliable API: project configuration can silently change its shape, so
the producer command must be controlled before its output is persisted.

**Next boundary.** Run each discovered node ID under an isolated coverage data
file and turn its JSON report into a persisted test-to-function mapping.

### 2026-09-27 — Per-test coverage mapping collected

**Question / hypothesis.** Can every discovered target test be run in isolation
and converted into a deterministic mapping without creating coverage or cache
files in the target repository?

**Change.** Added `src/regscope/coverage_collector.py` and three focused tests.
For each node ID it creates a digest-named `COVERAGE_FILE` below the caller's
output directory, invokes target `python -m coverage run --source=app -m
pytest`, converts that data to JSON, and passes the JSON through the existing
line-to-function mapper. The collector writes one sorted `coverage-mapping.json`
with schema version, target root, interpreter, and mappings.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
$env:PYTHONPATH='src'
.\\.venv\\Scripts\\python.exe -c "... collect_test_function_mappings('../order-service', temp_output) ..."
git -C ../order-service status --short
```

**Result.** The platform suite passed: 16 tests in 0.13 seconds. A real run
collected seven mappings and wrote `coverage-mapping.json` under a temporary
output directory. The target Git status remained exactly its three pre-existing
uncommitted files, confirming the collector did not add `.coverage` or pytest
cache output.

**Decision and trade-off.** Coverage artifacts are intentionally stored outside
the target. The real mapping includes dependency-provider, constructor, and
reset functions because line coverage records application initialisation and
test fixture execution. This is valid runtime evidence, not proof of business
assertion; the MVP will keep it visible and make later selection conservative
rather than silently pretending it is a precise business-only graph.

**Learning note.** Per-test coverage is the dynamic half of regression test
selection: it answers what code a test actually executed, not what code looks
related in source. Isolation matters because a shared coverage file would merge
multiple tests and destroy the `test -> function` relation that the selector
needs.

**Next boundary.** Add malformed-report and target-path boundary tests, then
provide a small read/query interface for inspecting a stored test mapping.

### 2026-09-27 — Coverage-input failure modes made explicit

**Question / hypothesis.** Can malformed or empty coverage data fail with
actionable context while preserving the valid empty-mapping case?

**Change.** Hardened `coverage_mapper.py` to validate the JSON root and `files`
field, reject malformed JSON as `ValueError`, and ignore malformed per-file
metadata. The collector now wraps mapping failures with the exact test ID.
Added tests for invalid JSON, an empty coverage map, and a malformed per-test
coverage report; existing tests already exercise Windows paths, unavailable
source files, failed pytest execution, and target paths that are independent of
RegScope's location.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
```

**Result.** The platform suite passed: 19 tests in 0.15 seconds. An empty report
now deliberately yields `{ "test_id": ..., "functions": [] }`; malformed JSON
reports the report path and, at collection level, the affected test ID.

**Decision and trade-off.** Empty coverage is treated as valid information, not
an error, because a test may legitimately exercise no `app/` function. Broken
coverage syntax or structure is an acquisition failure and stops the run: using
partial or guessed mappings could silently omit regression tests.

**Learning note.** Data-pipeline validation distinguishes “nothing happened”
from “we cannot know what happened.” In RegScope, an empty function list is a
result; unreadable coverage data is uncertainty and must propagate to a safe
decision rather than be converted to an empty list.

**Next boundary.** Add a read/query interface over `coverage-mapping.json` so a
developer can inspect what functions a particular pytest node ID executed.

### 2026-09-27 — Persisted mapping query API added

**Question / hypothesis.** Can a user inspect a prior mapping by Test ID without
re-running the target suite, while rejecting an artifact with an incompatible
or corrupted shape?

**Change.** Added `src/regscope/mapping_store.py`. `load_coverage_mapping`
validates version 1 mapping artifacts and entry shapes; `functions_for_test`
returns a copy of one test's function IDs or raises a clear unknown-ID error.
Added six tests covering normal lookup, an empty function list, unknown IDs, and
four invalid artifact shapes.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
$env:PYTHONPATH='src'
.\\.venv\\Scripts\\python.exe -c "... functions_for_test(coverage_mapping, test_id) ..."
```

**Result.** The platform suite passed: 25 tests in 0.17 seconds. Querying the
real persisted artifact for `tests/test_hello.py::test_say_hello` returned
`['app.main:hello']` without starting pytest.

**Decision and trade-off.** The first public read surface is a Python API,
rather than a CLI, because it gives the selection engine a tested contract and
avoids committing to command syntax before the full end-to-end command exists.
The later CLI will call this same validated format.

**Learning note.** Persisting data is not enough for reproducibility; readers
must validate the artifact version and shape. Otherwise a later code change can
silently interpret old or damaged mapping data as valid regression evidence.

**Next boundary.** Build a clean controlled target worktree and a small
business-rule change, then implement Git diff-to-function analysis against its
two commits.

### 2026-09-27 — Controlled revision pair and external-path integration test created

**Question / hypothesis.** Can the MVP evaluate a known business regression
without changing the developer's active target repository, and can RegScope run
an unrelated target purely through its filesystem path?

**Change.** Created a clean local clone at `../_regscope-fixture` from the
committed `order-service` state. Its base is `9047fa4`; branch
`fixture-threshold-cut` changes only `FREE_SHIPPING_CUT` from 50 to 40 in commit
`4fdfcd9`. Added an external-path integration test that creates a minimal
independent `app/` plus pytest project and discovers its test through a
subprocess, using no RegScope import in that target.

**Commands run.**

```powershell
git clone --no-hardlinks ../order-service ../_regscope-fixture
git -C ../_regscope-fixture switch -c fixture-threshold-cut
git -C ../_regscope-fixture commit -m "fixture: change threshold cut rule"
& ../order-service/.venv/Scripts/python.exe -m pytest
.\\.venv\\Scripts\\python.exe -m pytest
```

**Result.** At head `4fdfcd9`, the fixture's full suite has 1 expected failure
and 6 passes. The ground-truth failing node ID is
`tests/test_orders.py::test_create_order_applies_threshold_cut_after_discounts`:
its total is 560 while the baseline expectation is 550. The RegScope suite
passed: 26 tests in 0.50 seconds. The original `order-service` working tree was
not modified; it retains only its three pre-existing uncommitted files.

**Decision and trade-off.** The fixture uses the original service virtual
environment by absolute interpreter path because a Git clone correctly omits
`.venv`. This is appropriate for the local controlled experiment but must be
made explicit in the eventual CLI rather than assumed for arbitrary target
repositories.

**Learning note.** A regression benchmark needs ground truth that is independent
of the selection algorithm. Here the changed constant is known before analysis,
and an existing assertion demonstrably fails at head. That lets Recall later be
computed instead of inferred from whether a selector “looks reasonable.”

**Next boundary.** Implement Git revision validation and changed-line extraction
for the fixture pair `9047fa4 -> 4fdfcd9`.

### 2026-09-27 — Git revision and changed-line analysis implemented

**Question / hypothesis.** Can RegScope resolve immutable target commits and
extract head-side changed lines without reading uncommitted working-tree changes?

**Change.** Added `src/regscope/git_diff.py`: revision resolution via `git
rev-parse --verify <revision>^{commit}`, sorted changed-file listing, and
unified-diff parsing for changed head lines. Added real temporary-Git-repository
tests for changed functions, deleted files, and invalid revisions.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
... changed_files('../_regscope-fixture', '9047fa4', '4fdfcd9') ...
... changed_head_lines('../_regscope-fixture', '9047fa4', '4fdfcd9') ...
openspec.cmd validate end-to-end-mvp --strict
```

**Result.** The platform suite passed: 29 tests in 2.65 seconds. The fixture
pair reports `app/service.py` as changed and head line 14 as the changed rule.
Pure deletions remain visible in changed files but have no head line to map.
The OpenSpec change remains valid.

**Decision and trade-off.** The MVP maps only head-side changed lines, because
selection runs against the head checkout and must link to source that exists
there. Deleted functions will be represented as an explicit changed-file/
unmapped condition and later invoke conservative fallback; attempting to map
them into head source would falsely claim precision.

**Learning note.** Git's hunk coordinates have an old side and a new side.
Impact analysis must choose deliberately: the new-side coordinates identify
functions in the version about to be tested. Adjacent changes can include blank
lines in a hunk, which is harmless when the next AST stage maps only lines that
belong to a function.

**Next boundary.** Map changed head lines to function identifiers, including
function definitions and module-level code that cannot safely map to a function.

### 2026-09-27 — Changed-line classification added

**Question / hypothesis.** Can RegScope map edits to a function even when the
changed line is its `def` declaration, while not falsely assigning module
constants to an arbitrary function?

**Change.** Added `src/regscope/change_mapper.py`. It parses head source with
Python AST, maps changed lines through decorator/definition-to-end function
ranges, and returns separate sorted `functions` and `module_level_lines`.
Added a test covering a class method definition, a standalone helper body, and
a module constant.

**Result.** The platform suite passed: 30 tests in 2.69 seconds. The controlled
fixture's changed line 14 is correctly classified as module-level and produces
no changed function. This is expected because the fixture changes a global
pricing constant rather than a line in `_apply_threshold_cut`.

**Decision and trade-off.** Module-level business constants are intentionally
not guessed into a nearby function. The later impact stage will treat such
unmapped business-source changes as uncertain and select conservatively. This
avoids a precise-looking but unsupported impact path.

**Learning note.** Runtime coverage intentionally begins at a function body,
but source-change analysis must include decorators and `def` lines: changing a
signature or decorator can change behaviour even if that line never appears in
coverage. These are different mappings with different boundaries.

**Next boundary.** Discover FastAPI routes and direct calls, then define the
conservative outcome for the fixture's module-level configuration change.

### 2026-09-27 — FastAPI route discovery and bounded call graph implemented

**Question / hypothesis.** Can static analysis identify target endpoints and
the direct path from an endpoint's typed service parameter into service methods,
without claiming support for arbitrary Python dispatch?

**Change.** Added `src/regscope/static_analysis.py`. It discovers functions
decorated directly with `@app.<verb>` or `@router.<verb>`, then builds a call
graph for `app/` functions using same-module calls, `self.method()` calls, and
methods called on parameters with resolvable type annotations. Added a focused
route plus chained service-method test.

**Commands run.**

```powershell
.\\.venv\\Scripts\\python.exe -m pytest
... discover_fastapi_endpoints('../_regscope-fixture') ...
... build_direct_call_graph(...)["app.api:create_order"] ...
```

**Result.** The platform suite passed: 31 tests in 2.76 seconds. The fixture
contains 11 endpoints (correcting the earlier baseline count), and
`app.api:create_order` resolves directly to
`app.service:OrderService.create_order`.

**Decision and trade-off.** The graph is intentionally bounded to direct,
statically resolvable calls. Dependency injection provider construction,
repository attributes, aliases, inheritance, reflection, and runtime monkey
patching are excluded rather than guessed. This is sufficient for the current
API-to-service path and keeps unsupported edges visible as omissions.

**Learning note.** A call graph is a directed relation, not execution proof.
Type annotations bridge the API layer's `service.create_order()` syntax to the
actual `OrderService.create_order` symbol; without that resolution, the route
and service layers look disconnected even though tests execute both.

**Next boundary.** Reverse-traverse this graph from changed functions to endpoint
functions and serialize each discovered impact path; module-level changes must
fall back conservatively.

### 2026-09-27 — MVP end-to-end validation and experiment closeout

**Result.** The CLI now produces coverage mapping, impact, selection, and
evaluation JSON/Markdown artifacts from a target path plus base/head commits.
The module-level fixture selected 7/7 tests with 100% recall by conservative
fallback. The function-body fixture selected 5/7 tests (28.57% reduction) with
100% recall for the independently observed failing test. Full experiment inputs,
commands, limits, and unavailable baselines are recorded in
`docs/experiments/mvp-baseline.md`.

**Final limitation.** Path Match and separately reported Dynamic Coverage Only
baselines remain unavailable; they are explicitly documented rather than
represented by invented metrics. The direct-call AST analysis also remains an
MVP boundary, not a complete Python call graph.

## Entry template for each implementation step

### YYYY-MM-DD — <short outcome>

**Question / hypothesis.** What must be true or what uncertainty is being tested?

**Change.** Files, interfaces, and data-format changes.

**Commands run.** Exact commands and their important output.

**Result.** Pass/fail, produced artifact paths, and observed metrics.

**Decision and trade-off.** Why this approach was retained, changed, or rejected.

**Learning note.** Transferable concept, the RegScope-specific example, and why
it matters here.

**Next boundary.** The smallest following task; no automatic scope expansion.
