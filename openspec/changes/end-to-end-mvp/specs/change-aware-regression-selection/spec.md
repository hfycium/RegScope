## ADDED Requirements

### Requirement: Analyse an explicit target repository and revision pair

The system SHALL accept a path to a Git target repository and explicit base and
head revisions. It SHALL validate that both revisions resolve in that repository
before analysing changes, and SHALL not import target application modules into
the RegScope process.

#### Scenario: Valid target and revisions
- **WHEN** a caller provides an existing Git repository path and two resolvable revisions
- **THEN** the system analyses that target only and records the resolved revision IDs

#### Scenario: Invalid target or revision
- **WHEN** the target path is not a Git repository or either revision cannot resolve
- **THEN** the system exits with a clear error and writes no misleading selection result

### Requirement: Persist deterministic per-test function coverage

The system SHALL collect per-test coverage from pytest tests in the target
repository and persist a sorted mapping from stable pytest node IDs to qualified
Python function IDs. It SHALL identify business source by the target `app/`
directory for this MVP.

#### Scenario: A test executes business functions
- **WHEN** a target test executes functions in `app/`
- **THEN** its mapping contains sorted, deduplicated qualified function IDs

#### Scenario: Coverage contains tests or unavailable source files
- **WHEN** coverage lists test files, non-Python files, or missing source files
- **THEN** those files do not produce business-function mappings and a relevant warning is available

### Requirement: Report changed functions and affected endpoints

The system SHALL map changed Python lines under `app/` to function IDs and
trace resolvable direct call paths to FastAPI endpoint functions. It SHALL
preserve each endpoint's HTTP method, route path, and path to the changed
function.

#### Scenario: A changed service function is directly called by an endpoint path
- **WHEN** a changed business function has a resolvable reverse call path to a FastAPI endpoint
- **THEN** the impact result includes the changed function, endpoint method/path, and ordered path evidence

#### Scenario: Static resolution is incomplete
- **WHEN** a call cannot be resolved within the MVP analysis boundary
- **THEN** the result records an unresolved-analysis warning and does not represent the function as proven unaffected

### Requirement: Select tests with evidence and a safe fallback

The system SHALL select tests whose historical coverage intersects changed
business functions or affected endpoint paths according to the configured MVP
rules. Each selected test SHALL carry evidence. If required analysis data is
incomplete, the system SHALL disclose the fallback and select a conservative
safe set.

#### Scenario: Historical coverage intersects a changed function
- **WHEN** a mapped test covers a changed function
- **THEN** that test appears in the selected set with the shared function ID as evidence

#### Scenario: Required mapping is absent or analysis is unresolved
- **WHEN** the selector cannot safely establish the candidate set
- **THEN** it reports the condition and selects the configured conservative fallback rather than silently excluding tests

### Requirement: Produce reproducible MVP evaluation

The system SHALL produce machine-readable and Markdown evaluation reports for a
recorded target revision pair. The report SHALL include total and selected test
counts, reduction ratio, elapsed execution time, known failing-test ground
truth when available, and recall. It SHALL label unavailable metrics or
baselines as unavailable.

#### Scenario: A known failing-test fixture exists
- **WHEN** the experiment specifies known failing tests for the analysed change
- **THEN** the report calculates recall as selected known-failing tests divided by all known-failing tests

#### Scenario: A comparison baseline cannot run
- **WHEN** a requested baseline is not yet applicable to the target data
- **THEN** the report marks it unavailable with the reason and does not invent a value
