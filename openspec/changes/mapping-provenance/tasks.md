## 1. Record mapping identity

- [x] 1.1 Compute portable runtime, dependency/configuration, and test-inventory
  fingerprints for a target project.
- [x] 1.2 Store provenance and resolved target HEAD in newly collected mappings.
- [x] 1.3 Unit-test fingerprint stability and changes to relevant inputs.

## 2. Validate before reuse

- [x] 2.1 Compare saved source revision with the requested base commit.
- [x] 2.2 Compare runtime/environment fingerprint and current test inventory.
- [x] 2.3 Fall back to all current tests and record reasons on every mismatch,
  including legacy mappings without provenance.
- [x] 2.4 Test compatible and incompatible mapping behavior.

## 3. Verify and document

- [x] 3.1 Regenerate and reuse the real FastAPI baseline mapping; verify a
  compatible map still selects the known impacted tests.
- [x] 3.2 Run the RegScope suite and strict OpenSpec validation.
- [x] 3.3 Update the Wiki with the provenance checks and fallback behavior.
