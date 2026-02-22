## ADDED Requirements

### Requirement: Shared state contract across nodes
The workflow MUST use a shared typed state contract that includes `topic`, `research_results`, `analysis_results`, `final_report`, `messages`, and `timestamp`.

#### Scenario: Workflow starts with required state keys
- **WHEN** the workflow is invoked
- **THEN** the initial state conforms to the defined shared contract and is accepted by all nodes

### Requirement: State propagation preserves prior outputs
Each node SHALL receive state from the previous node and preserve existing fields while adding or updating only its own outputs.

#### Scenario: Intermediate outputs are not lost between nodes
- **WHEN** state transitions from `Researcher` to `Analyst` to `Reporter`
- **THEN** previously generated values remain available unless intentionally updated by the current node

### Requirement: Additive execution log in messages
The system MUST append human-readable execution entries to `messages` throughout the workflow lifecycle.

#### Scenario: Messages log reflects node progression
- **WHEN** a workflow run completes
- **THEN** `messages` contains ordered log entries showing execution of `Researcher`, `Analyst`, and `Reporter`

### Requirement: Timestamp availability for the run
The state SHALL include a timestamp value associated with the workflow execution context.

#### Scenario: Timestamp is present in final state
- **WHEN** the run reaches `END`
- **THEN** the returned state contains a non-empty `timestamp` value
