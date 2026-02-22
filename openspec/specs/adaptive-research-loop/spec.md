## Purpose

Define the conditional retry loop behavior that routes analysis back to research when collected data is insufficient.

## Requirements

### Requirement: Analyst-driven sufficiency gate
The workflow MUST evaluate research sufficiency after the `Analyst` step using a word-count threshold on `research_results`.

#### Scenario: Insufficient research is detected
- **WHEN** `research_results` contains fewer than 100 words
- **THEN** the workflow marks the current research output as insufficient for final reporting

### Requirement: Conditional routing back to researcher
The graph SHALL route execution from `Analyst` back to `Researcher` when the sufficiency gate fails.

#### Scenario: Retry path is selected on low word count
- **WHEN** the analyst determines that research is insufficient
- **THEN** the next executed node is `Researcher` rather than `Reporter`

### Requirement: Continue to reporter on sufficient research
The graph MUST route execution from `Analyst` to `Reporter` when the sufficiency gate passes.

#### Scenario: Success path proceeds to reporting
- **WHEN** `research_results` contains at least 100 words
- **THEN** the next executed node is `Reporter` and the workflow can terminate at `END`

### Requirement: Retry behavior is traceable in logs
The system SHALL append log entries indicating when a retry loop was triggered and when sufficiency was eventually met.

#### Scenario: Messages include loop events
- **WHEN** at least one retry cycle occurs
- **THEN** `messages` includes entries documenting insufficiency detection and re-routing decisions
