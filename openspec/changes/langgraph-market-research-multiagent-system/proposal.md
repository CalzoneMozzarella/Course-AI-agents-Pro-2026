## Why

In module 1, we need a second agent project that moves beyond a single-agent flow and demonstrates practical multi-agent orchestration with shared state. This change is needed now to teach sequential agent collaboration patterns in LangGraph, including optional feedback loops when data quality is insufficient.

## What Changes

- Add a new module 1 project implementing a LangGraph-based multi-agent market research workflow.
- Define a typed shared state (`AgentState`) carrying topic, intermediate outputs, execution log, and timestamp across agents.
- Implement three sequential agent nodes: `Researcher`, `Analyst`, and `Reporter`.
- Build and execute a directed graph with ordered transitions: `Researcher -> Analyst -> Reporter -> END`.
- Persist the final markdown report to disk and include execution messages in state for traceability.
- Add a conditional transition for iterative research when analyst input is too short (less than 100 words), routing back to `Researcher`.

## Capabilities

### New Capabilities
- `langgraph-market-research-workflow`: Define and run a stateful multi-agent LangGraph pipeline for market research from topic input to saved final report.
- `agent-state-propagation-and-logging`: Guarantee correct state passing and additive message logging across all agent nodes.
- `adaptive-research-loop`: Support conditional graph routing from analyst back to researcher when collected research data is insufficient.

### Modified Capabilities
- None.

## Impact

- Affected code: new module 1 agent package/files for graph, nodes, state model, and report output.
- APIs/Interfaces: introduces a new internal workflow contract based on `AgentState` fields and node return semantics.
- Dependencies: relies on `langgraph`; may optionally use an LLM provider and/or web search utilities already available in the course environment.
- Tooling and outputs: adds a report artifact written to a local file path (Markdown), plus execution trace in `messages`.
