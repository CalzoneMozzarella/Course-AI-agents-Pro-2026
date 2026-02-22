import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from ddgs import DDGS
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _is_placeholder_openai_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return True
    lowered = api_key.strip().lower()
    if lowered in {"your_openai_api_key_here", "changeme", "replace_me"}:
        return True
    if lowered.startswith("your_") and lowered.endswith("here"):
        return True
    return False


@tool
def get_current_date() -> str:
    """Return the current local date and time as ISO-8601."""
    return _now_iso()


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return concise results."""
    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:  # keep broad for a simple student script
        return f"SEARCH_ERROR: {type(e).__name__}: {e}"

    lines: list[str] = []
    for i, r in enumerate(results or [], start=1):
        title = (r or {}).get("title", "").strip()
        href = (r or {}).get("href", "").strip()
        body = (r or {}).get("body", "").strip()
        lines.append(f"{i}. {title}\n   {href}\n   {body}".strip())

    return "\n\n".join(lines) if lines else "NO_RESULTS"


@tool
def save_report(content: str, filename: Optional[str] = None, topic: Optional[str] = None) -> str:
    """Save the report content to a JSON file and return the saved path."""
    base_dir = Path(__file__).resolve().parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    ts = _now_iso()
    report: dict[str, Any] = {
        "topic": topic or "",
        "result": content,
        "timestamp": ts,
    }

    if not filename:
        safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in (topic or "report"))
        filename = f"{safe[:60].strip('-') or 'report'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    path = reports_dir / filename
    try:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        return f"FILE_ERROR: {type(e).__name__}: {e}"

    return str(path)


def run_agent(topic: str) -> tuple[str, str]:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4")

    if _is_placeholder_openai_key(api_key):
        now = _now_iso()
        web = search_web.func(f"{topic} 2025 Україна", max_results=5)  # type: ignore[attr-defined]
        fallback = (
            f"Станом на {now} я не бачу налаштованого `OPENAI_API_KEY`, тому згенерував демо-звіт без LLM.\n\n"
            f"Попередні результати пошуку:\n{web}\n\n"
            "Щоб увімкнути повний режим (LLM + інструменти), створіть `.env` з `OPENAI_API_KEY` "
            "або експортуйте змінну середовища."
        )
        saved_path = save_report.invoke({"content": fallback, "topic": topic})
        return fallback, saved_path

    llm = ChatOpenAI(model=model_name, temperature=0.7)

    system_prompt = (
        "Ви — розумний помічник для студентів українських університетів.\n"
        "Ваша задача — допомагати знаходити актуальну інформацію та формувати корисні відповіді.\n"
        "Відповідайте українською мовою.\n\n"
        "Використовуйте інструменти:\n"
        "- `get_current_date` щоб дізнатися поточну дату/час.\n"
        "- `search_web` щоб знайти актуальні факти та джерела.\n"
        "У фінальній відповіді обов'язково наведіть 3–5 джерел (посилання) з результатів пошуку."
    )

    tools = [get_current_date, search_web, save_report]
    llm_with_tools = llm.bind_tools(tools)

    messages: list[Any] = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Тема: {topic}\n\n"
                "Зроби короткий звіт (6–10 речень) з підсумком та ключовими пунктами.\n"
                "Спочатку отримай поточну дату/час, потім зроби веб-пошук, після чого підготуй відповідь."
            )
        ),
    ]

    final_text = ""
    for _step in range(6):
        try:
            ai_msg = llm_with_tools.invoke(messages)
        except Exception as e:  # keep broad: show useful fallback instead of crashing
            now = _now_iso()
            web = search_web.func(f"{topic} 2025 Україна", max_results=5)  # type: ignore[attr-defined]
            fallback = (
                f"Станом на {now} не вдалося викликати OpenAI API ({type(e).__name__}).\n\n"
                f"Демо-звіт без LLM. Попередні результати пошуку:\n{web}\n\n"
                "Перевірте `OPENAI_API_KEY` і спробуйте ще раз."
            )
            saved_path = save_report.invoke({"content": fallback, "topic": topic})
            return fallback, saved_path
        messages.append(ai_msg)

        if getattr(ai_msg, "tool_calls", None):
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call.get("name")
                tool_obj = next((t for t in tools if t.name == tool_name), None)
                if tool_obj is None:
                    continue
                tool_result_msg = tool_obj.invoke(tool_call)
                messages.append(tool_result_msg)
            continue

        content = getattr(ai_msg, "content", "")
        final_text = content if isinstance(content, str) else str(content)
        break

    saved_path = save_report.invoke({"content": final_text, "topic": topic})
    return final_text, saved_path


if __name__ == "__main__":
    topic = "Штучний інтелект в освіті України 2025"
    result, report_path = run_agent(topic)
    print(result)
    print("\nSaved report:", report_path)

