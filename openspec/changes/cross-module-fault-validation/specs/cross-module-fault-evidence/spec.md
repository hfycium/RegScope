## ADDED Requirements

### Requirement: Validate selection across independent target modules

The experiment SHALL include at least two isolated known-fault revisions in
distinct target Python modules outside `items.py`. Each revision SHALL identify
an existing test that passes at the clean base and fails at the fault head.
All selection strategies SHALL use the same recorded baseline coverage
mapping, and the report SHALL include selected counts and known-failure recall.

#### Scenario: A route-module fault is introduced
- **WHEN** a fault is committed to a route module with baseline test coverage
- **THEN** its known test is verified to pass at base and fail at head, and all
  four selection strategies are evaluated against that test ID

#### Scenario: The target test fixture has destructive cleanup
- **WHEN** a target test fixture deletes database rows during teardown
- **THEN** the experiment uses a dedicated database and leaves the configured
  application database unchanged
