## Context

Module 1 already includes a single-agent LangChain project. This change adds a second project that demonstrates a stateful multi-agent architecture in LangGraph, where each node consumes and extends shared state. The required flow is `Researcher -> Analyst -> Reporter -> END`, with an optional loop from `Analyst` back to `Researcher` when research text is too short (less than 100 words). The implementation should remain practical for course learners, with visible execution logs and a saved Markdown report.

Constraints:

- Keep the state schema explicit and typed with `TypedDict`.
- Preserve deterministic node ordering for the default path.
- Make optional LLM usage non-blocking (fallback behavior if LLM is unavailable).
- Ensure file output is reproducible and easy to inspect.

## Goals / Non-Goals

**Goals:**

- Provide a runnable LangGraph example of multi-agent market research in module 1.
- Define `AgentState` as the single contract between nodes.
- Record additive execution logs via `messages: Annotated[List[str], operator.add]`.
- Save a structured final Markdown report to disk.
- Support conditional retry routing when analyst input quality is insufficient.

**Non-Goals:**

- Building a production-grade autonomous research platform.
- Implementing advanced retrieval pipelines or persistent vector storage.
- Supporting multiple branching strategies beyond the single quality gate.
- Guaranteeing factual correctness of external web data.

## Decisions

1. Use a single shared `AgentState` object for all nodes.
  - Rationale: keeps data flow explicit, testable, and aligned with LangGraph state semantics.
  - Alternative considered: separate payload per node with adapters; rejected due to added complexity for teaching.
2. Implement nodes as pure state-transform functions returning partial updates.
  - Rationale: predictable behavior, easier unit tests, and straightforward graph integration.
  - Alternative considered: class-based agents with internal mutable state; rejected to avoid hidden coupling.
3. Keep graph topology linear by default, with one conditional edge from `Analyst`.
  - Rationale: satisfies required architecture while introducing one meaningful control-flow concept.
  - Alternative considered: fully dynamic planner/executor loops; rejected as out of scope for module 1.
4. Define insufficiency rule as word-count threshold (`< 100` words in `research_results`).
  - Rationale: objective, simple to explain, and directly tied to the assignment rubric.
  - Alternative considered: LLM-based adequacy scoring; rejected as less deterministic and harder to debug.
5. Generate report in Markdown and persist to a local reports directory.
  - Rationale: human-readable output and parity with current module artifact style.
  - Alternative considered: JSON-only output; rejected because Markdown is required and easier for grading.
6. Treat LLM and web search integrations as optional adapters with safe fallbacks.
  - Rationale: workflow must run in restricted or offline environments for students.
  - Alternative considered: mandatory external APIs; rejected due to setup fragility.

## Risks / Trade-offs

- [External web data may be noisy or unavailable] -> Mitigation: fallback to placeholder research text and log source failures in `messages`.
- [Conditional loop can repeat indefinitely on poor data] -> Mitigation: include max retry count in state or hard limit in analyst routing logic.
- [State keys may be overwritten inconsistently across nodes] -> Mitigation: enforce node-specific write ownership (`research_results`, `analysis_results`, `final_report`) and add tests.
- [Optional LLM path may produce non-deterministic output] -> Mitigation: keep deterministic baseline logic and mark LLM enrichment as additive.

## Migration Plan

1. Add a new module 1 project directory for the LangGraph multi-agent assignment implementation.
2. Implement `AgentState`, three nodes, graph wiring, conditional edge, and report persistence.
3. Add a runnable entry point and example initial state payload.
4. Validate end-to-end execution and output file creation using a sample topic.
5. Rollback strategy: remove new module directory/files and keep existing module 1 agent unchanged (no shared runtime dependencies modified).

## Open Questions

- Should the retry guard be encoded directly in `AgentState` (for example, `retry_count`) or handled outside state in invocation config?
- Which search utility should be the default for the course environment when internet access is available?
- Should the final report filename include topic slug + timestamp for uniqueness, or use a deterministic name per run?

