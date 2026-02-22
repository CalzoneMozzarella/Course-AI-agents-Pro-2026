## ADDED Requirements

### Requirement: Sequential market research workflow execution
The system SHALL execute a market research workflow as a directed graph with the default node order `Researcher -> Analyst -> Reporter -> END`.

#### Scenario: Run completes through all required nodes
- **WHEN** a user invokes the compiled graph with a valid initial state containing a non-empty `topic`
- **THEN** the workflow executes `Researcher`, then `Analyst`, then `Reporter`, and terminates at `END`

### Requirement: Researcher node produces research output
The `Researcher` node MUST read `topic` from state and produce non-empty `research_results` before passing state forward.

#### Scenario: Research step populates state
- **WHEN** the `Researcher` node receives state with `topic`
- **THEN** the returned state includes populated `research_results` derived from the requested topic

### Requirement: Analyst node produces analysis output
The `Analyst` node MUST consume `research_results` and produce `analysis_results` that includes at least word and sentence counts.

#### Scenario: Analysis computes basic metrics
- **WHEN** the `Analyst` node receives state with non-empty `research_results`
- **THEN** the returned state contains `analysis_results` with computed text metrics and identified key themes

### Requirement: Reporter node produces and persists final report
The `Reporter` node SHALL combine `research_results` and `analysis_results` into a structured Markdown report and persist it to a file.

#### Scenario: Final report is generated and saved
- **WHEN** the `Reporter` node receives state with populated research and analysis outputs
- **THEN** the node writes a Markdown report file and returns state with non-empty `final_report`
