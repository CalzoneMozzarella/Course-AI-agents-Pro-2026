## 1. Setup & Project Skeleton

- [x] 1.1 Create a runnable script entrypoint (e.g., `main.py` or `agent.py`) for the student assistant
- [x] 1.2 Add Python dependencies (LangChain + OpenAI + DuckDuckGo + dotenv) to a dependency file (`requirements.txt` or equivalent)
- [x] 1.3 Add `.env.example` documenting required env vars (at least `OPENAI_API_KEY`)

## 2. Implement Required Tools

- [x] 2.1 Implement `get_current_date` tool that returns current date/time (ISO-8601 or consistent string format)
- [x] 2.2 Implement `search_web(query: str)` using DuckDuckGo (library `ddgs` / `duckduckgo-search`) and return a concise text result set
- [x] 2.3 Implement `save_report(content: str, filename: str | None)` to write a JSON file with `topic`, `result`, `timestamp`
- [x] 2.4 Add basic error handling for network/search failures and file write errors (fail gracefully with a useful message)

## 3. LangChain Agent Wiring

- [x] 3.1 Configure `ChatOpenAI` with model `gpt-4` (or project-approved equivalent) and load API key from environment
- [x] 3.2 Define Ukrainian `system_prompt` (student helper persona) and build the base prompt template
- [x] 3.3 Wire tools into the LLM flow (tool-calling agent via `bind_tools`/agent executor, not just a plain chain)
- [x] 3.4 Ensure the agent uses `search_web` for freshness and `get_current_date` for time context when appropriate

## 4. Report Generation & Persistence

- [x] 4.1 Use the provided `topic` variable as the report topic and generate a coherent Ukrainian report text
- [x] 4.2 Call `save_report` to persist the final output to JSON with correct fields and a valid timestamp
- [x] 4.3 Return/print the final report path so the user can find the saved JSON

## 5. Verification (Must Pass)

- [x] 5.1 Run the script end-to-end locally with a sample topic (e.g., “Штучний інтелект в освіті України 2025”) and confirm no runtime errors
- [x] 5.2 Verify the saved JSON file schema: `topic` (string), `result` (string), `timestamp` (string)
- [x] 5.3 Spot-check that the answer is in Ukrainian and includes information sourced from search results (not purely hallucinated)

