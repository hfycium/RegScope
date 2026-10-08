## ADDED Requirements

### Requirement: Verify mapping provenance before precise selection

New coverage mappings SHALL record the source target commit, runtime and
dependency/test-environment fingerprint, and discovered test inventory.
Before using a saved mapping for selection, RegScope SHALL verify that the
mapping matches the requested base commit, current runtime/environment, and
current discovered test IDs.

#### Scenario: Mapping provenance matches
- **WHEN** the saved mapping source commit equals the requested base, its
  environment fingerprint matches, and its test inventory is unchanged
- **THEN** RegScope uses the mapping for precise selection

#### Scenario: Mapping metadata is missing or does not match
- **WHEN** the source commit, environment fingerprint, or test inventory is
  absent or differs from the current run
- **THEN** RegScope selects all currently discovered tests and records the
  mismatch reasons as conservative fallback evidence
