## ADDED Requirements

### Requirement: Collect a baseline mapping independently

The CLI SHALL provide a `collect` command that runs per-test coverage
collection and writes a `coverage-mapping.json` file at the requested path,
without running impact analysis or test evaluation.

#### Scenario: Generate a mapping for a baseline revision
- **WHEN** the user runs `regscope collect` with a target repository and output
  path
- **THEN** RegScope collects each target test's function mapping and writes the
  resulting JSON exactly to the requested path

### Requirement: Reuse a saved coverage mapping

The CLI SHALL accept an optional saved coverage mapping. When one is supplied,
RegScope SHALL skip coverage collection and use that mapping for test selection.
When no mapping is supplied, the existing collection behavior SHALL remain.
The CLI SHALL provide an opt-in mode that runs only selected tests and skips
the full-suite comparison.

#### Scenario: A compatible mapping is supplied
- **WHEN** the user runs `regscope run` with `--mapping` pointing to a valid
  mapping file
- **THEN** RegScope uses the supplied test-to-function mapping, does not invoke
  coverage collection, and writes the mapping and downstream analysis results
  to the output directory

#### Scenario: No mapping is supplied
- **WHEN** the user runs `regscope run` without `--mapping`
- **THEN** RegScope collects coverage as it does today before analyzing impact

#### Scenario: The mapping file is invalid
- **WHEN** the supplied file is not valid supported mapping JSON
- **THEN** RegScope reports an actionable validation error and does not start
  test evaluation

#### Scenario: Selected-only execution is requested
- **WHEN** the user runs `regscope run` with `--selected-only`
- **THEN** RegScope executes the selected tests and records the full-suite run
  as skipped without invoking pytest for the full test population, and the CLI
  returns the selected test process exit status
