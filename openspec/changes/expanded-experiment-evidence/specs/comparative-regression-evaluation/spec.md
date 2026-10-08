## ADDED Requirements

### Requirement: Compare explicit selection baselines on controlled changes

The experiment tooling SHALL evaluate full-suite, changed-file coverage,
dynamic-only coverage, and the existing hybrid selector against the
same discovered test population and per-test function mappings. The report
SHALL define each baseline and include selected count, reduction ratio,
known-failure recall when ground truth is provided, and selected/full run exit
status and elapsed time.

#### Scenario: A changed Python module has mapped tests
- **WHEN** a controlled change identifies changed files and changed functions
- **THEN** the experiment reports a file-level coverage candidate set, a
  dynamic-only candidate set, the hybrid candidate set, and full suite
  using the same test population

#### Scenario: A controlled change has known failing tests
- **WHEN** the experiment supplies independently verified failing test IDs
- **THEN** each strategy reports recall as selected known failures divided by
  all known failures

#### Scenario: A baseline has no candidates
- **WHEN** a strategy selects no tests
- **THEN** the harness reports the empty set explicitly and does not invoke
  pytest with an empty argument list that would trigger test discovery

### Requirement: Reproduce multiple isolated fault cases

The experiment SHALL use a separate target fixture and SHALL include at least
four isolated business-fault cases across at least three distinct behaviors.
Each case SHALL name its base/head revisions and independently verified known
failing test IDs. The report SHALL state that these controlled cases do not
establish general production accuracy.

#### Scenario: Reproduce a fault case
- **WHEN** a user follows the documented command for a case
- **THEN** the harness produces the same changed-function, candidate-set, and
  recall inputs from the recorded revisions and fixture tests
