## Why

A saved coverage mapping is useful only when it belongs to the requested base
revision and a compatible test environment. Reusing a stale mapping can omit
tests added or changed since collection.

## What Changes

- Record the target HEAD revision, target runtime/dependency fingerprint, and
  pytest test-inventory fingerprint in newly collected mappings.
- Validate those values when reusing a mapping.
- Select the complete current test inventory when metadata is absent or does
  not match, rather than trusting stale function mappings.

## Capabilities

### New Capabilities

- `mapping-provenance`: identify the baseline and environment represented by a
  saved coverage mapping and fall back safely when it is incompatible.

### Modified Capabilities

- `reusable-coverage-mapping`: validate provenance before using a saved mapping.

## Impact

- Add mapping provenance and compatibility checks.
- Add metadata and safe-fallback tests and document the limitations.
- No dependency or CI workflow changes.

## Acceptance Criteria

- New mappings record the current target HEAD, runtime/dependency fingerprint,
  and discovered test inventory.
- Reuse checks the requested base revision, current runtime/dependency files,
  and current test inventory before trusting the mapping.
- Any mismatch selects the complete currently discovered test set.
- RegScope tests and strict OpenSpec validation pass.
