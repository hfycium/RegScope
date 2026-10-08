# RegScope GitHub Actions Integration

## ADDED Requirements

### Requirement: Preserve the full-suite CI safety net

The target repository SHALL continue running its existing full backend test
workflow independently of RegScope selection.

#### Scenario: RegScope has no baseline mapping

- **WHEN** a pull request has no cached mapping for its exact base revision and
  dependency/runtime configuration
- **THEN** the RegScope selection job SHALL report that it skipped
- **AND** the existing full backend test workflow SHALL remain enabled

### Requirement: Reuse only a base-compatible mapping

The integration SHALL collect mappings on default-branch pushes and restore
only the mapping keyed to the pull request's exact base commit and matching
configuration hash.

#### Scenario: A compatible base mapping is available

- **WHEN** a pull request restores the mapping for its exact base commit
- **THEN** RegScope SHALL check mapping provenance before selecting tests
- **AND** run the selected tests or conservatively fall back to all discovered
  tests if provenance is incompatible
