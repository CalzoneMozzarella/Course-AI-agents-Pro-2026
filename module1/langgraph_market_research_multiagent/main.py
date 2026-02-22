from __future__ import annotations

import operator
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict

from ddgs import DDGS
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


MIN_RESEARCH_WORDS = 100
MAX_RESEARCH_RETRIES = 2
DEFAULT_TOPIC = "AI assistants for SMB market research in Ukraine"


class AgentState(TypedDict):
    topic: str
    research_results: str
    analysis_results: str
    final_report: str
    messages: Annotated[List[str], operator.add]
    timestamp: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    return sum(1 for p in parts if p.strip())


def slugify(value: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value.strip().lower())
    compact = re.sub(r"-{2,}", "-", clean).strip("-")
    return compact[:60] or "report"


def retry_events(messages: list[str]) -> int:
    return sum(1 for msg in messages if msg.startswith("[loop]"))


def search_web(topic: str, max_results: int = 6) -> tuple[str, list[str]]:
    query = f"{topic} market trends statistics 2025"
    lines: list[str] = []
    sources: list[str] = []

    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as exc:  # broad fallback for student script
        fallback = (
            f"Web search failed ({type(exc).__name__}). "
            "Using fallback research notes: demand is growing, adoption is uneven across segments, "
            "and buyers prioritize ROI, integration, and trust."
        )
        return fallback, []

    for idx, item in enumerate(results or [], start=1):
        title = (item or {}).get("title", "").strip()
        href = (item or {}).get("href", "").strip()
        body = (item or {}).get("body", "").strip()
        if href:
            sources.append(href)
        lines.append(f"{idx}. {title}\n   {body}")

    joined = "\n\n".join(lines).strip()
    if not joined:
        joined = (
            "No results returned by search engine. Fallback assumption: the market is evolving quickly, "
            "competition is increasing, and pricing pressure is expected."
        )
    return joined, sources


def llm_is_configured() -> bool:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return False
    if key.lower() in {"your_openai_api_key_here", "changeme", "replace_me"}:
        return False
    return True


def llm_extract_facts(text: str) -> str:
    if not llm_is_configured():
        return "LLM not configured. Facts extracted via rule-based path only."

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0.2)
    messages = [
        SystemMessage(content="Extract exactly 5 concise market-research facts from the input text."),
        HumanMessage(content=text),
    ]
    try:
        response = llm.invoke(messages)
        content = getattr(response, "content", "")
        return content if isinstance(content, str) and content.strip() else "LLM returned an empty response."
    except Exception as exc:  # broad fallback for robustness
        return f"LLM fact extraction failed ({type(exc).__name__})."


def llm_detect_trends(text: str) -> str:
    if not llm_is_configured():
        return "LLM not configured. Trends inferred with basic keyword analysis."

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model, temperature=0.2)
    messages = [
        SystemMessage(content="Identify 3-5 key market trends and patterns from the provided text."),
        HumanMessage(content=text),
    ]
    try:
        response = llm.invoke(messages)
        content = getattr(response, "content", "")
        return content if isinstance(content, str) and content.strip() else "LLM returned an empty response."
    except Exception as exc:
        return f"LLM trend detection failed ({type(exc).__name__})."


def extract_themes(text: str, limit: int = 5) -> list[str]:
    tokens = re.findall(r"\b[\w'-]+\b", text.lower(), flags=re.UNICODE)
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "about",
        "market",
        "research",
        "data",
        "results",
    }
    filtered = [tok for tok in tokens if len(tok) > 3 and tok not in stopwords]
    return [word for word, _ in Counter(filtered).most_common(limit)]


def save_markdown_report(topic: str, content: str) -> Path:
    base_dir = Path(__file__).resolve().parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(topic)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = reports_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def researcher_node(state: AgentState) -> AgentState:
    search_output, sources = search_web(state["topic"])
    facts = llm_extract_facts(search_output)
    sources_block = "\n".join(f"- {src}" for src in sources) if sources else "- No sources available"

    research_results = (
        f"## Raw research\n{search_output}\n\n"
        f"## Five key facts\n{facts}\n\n"
        f"## Sources\n{sources_block}"
    )

    return {
        "research_results": research_results,
        "messages": [f"[Researcher] Compiled research. Words={word_count(research_results)}"],
    }


def analyst_node(state: AgentState) -> AgentState:
    text = state["research_results"]
    wc = word_count(text)
    sc = sentence_count(text)
    themes = extract_themes(text, limit=5)
    trends = llm_detect_trends(text)
    insufficient = wc < MIN_RESEARCH_WORDS

    analysis_results = (
        f"## Text metrics\n- Words: {wc}\n- Sentences: {sc}\n\n"
        f"## Key themes\n- " + "\n- ".join(themes or ["No themes found"]) + "\n\n"
        f"## Trends and patterns\n{trends}\n\n"
        f"## Sufficiency check\n- Meets threshold ({MIN_RESEARCH_WORDS} words): {'yes' if not insufficient else 'no'}"
    )

    log = f"[Analyst] Analyzed research. Words={wc}; Sentences={sc}"
    if insufficient:
        loop_num = retry_events(state["messages"]) + 1
        log = f"[loop] [Analyst] Insufficient data (<{MIN_RESEARCH_WORDS} words). Retry #{loop_num}"

    return {
        "analysis_results": analysis_results,
        "messages": [log],
    }


def reporter_node(state: AgentState) -> AgentState:
    report_md = (
        f"# Market Research Report\n\n"
        f"- Topic: {state['topic']}\n"
        f"- Generated at: {state['timestamp']}\n\n"
        f"## Researcher Output\n\n{state['research_results']}\n\n"
        f"## Analyst Output\n\n{state['analysis_results']}\n\n"
        f"## Execution Log\n" + "\n".join(f"- {item}" for item in state["messages"])
    )

    report_path = save_markdown_report(state["topic"], report_md)
    final_report = f"{report_md}\n\n---\nSaved report: {report_path}"
    return {
        "final_report": final_report,
        "messages": [f"[Reporter] Saved final markdown report to {report_path}"],
    }


def analyst_router(state: AgentState) -> Literal["Researcher", "Reporter"]:
    wc = word_count(state["research_results"])
    retries_done = retry_events(state["messages"])
    if wc < MIN_RESEARCH_WORDS and retries_done < MAX_RESEARCH_RETRIES:
        return "Researcher"
    return "Reporter"


def build_app():
    workflow = StateGraph(AgentState)
    workflow.add_node("Researcher", researcher_node)
    workflow.add_node("Analyst", analyst_node)
    workflow.add_node("Reporter", reporter_node)
    workflow.set_entry_point("Researcher")
    workflow.add_edge("Researcher", "Analyst")
    workflow.add_conditional_edges(
        "Analyst",
        analyst_router,
        {
            "Researcher": "Researcher",
            "Reporter": "Reporter",
        },
    )
    workflow.add_edge("Reporter", END)
    return workflow.compile()


def run_workflow(topic: str) -> AgentState:
    app = build_app()
    initial_state: AgentState = {
        "topic": topic,
        "research_results": "",
        "analysis_results": "",
        "final_report": "",
        "messages": [],
        "timestamp": now_iso(),
    }
    return app.invoke(initial_state)


if __name__ == "__main__":
    load_dotenv()
    topic = os.getenv("RESEARCH_TOPIC", DEFAULT_TOPIC)
    result = run_workflow(topic)
    print("=== Final messages ===")
    for msg in result["messages"]:
        print("-", msg)
    print("\n=== Final report preview ===")
    print(result["final_report"][:1200])
