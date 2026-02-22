## LangChain Student Agent (UA)

Консольний агент-помічник для студентів українських університетів, який:

- отримує поточну дату і час (`get_current_date`)
- шукає інформацію в інтернеті через DuckDuckGo (`search_web`, пакет `ddgs`)
- зберігає підсумковий звіт у JSON (`save_report`)

### Структура

- `main.py` — запуск агента
- `requirements.txt` — залежності
- `.env.example` — приклад змінних середовища
- `reports/` — збережені звіти у форматі JSON

### Встановлення

```powershell
python -m pip install -r module1\langchain_student_agent\requirements.txt
```

### Налаштування OpenAI

1) Скопіюйте `.env.example` → `.env` (у цій же папці)  
2) Вкажіть реальний ключ:

- `OPENAI_API_KEY=...`
- (опційно) `OPENAI_MODEL=gpt-4`

### Запуск

```powershell
python module1\langchain_student_agent\main.py
```

Скрипт:
- сформує український звіт по темі,
- збере 3–5 посилань із веб-пошуку,
- збереже результат у `reports/*.json`,
- виведе шлях до збереженого файлу.

### Формат звіту (JSON)

Файл у `reports/` має поля:

- `topic` — тема (рядок)
- `result` — текст звіту (рядок)
- `timestamp` — час генерації (рядок, ISO-8601)

### Примітки / Troubleshooting

- **Невірний або відсутній `OPENAI_API_KEY`**: скрипт автоматично перейде у демо-режим (без LLM), але все одно зробить веб-пошук і збереже JSON.
- **Windows кодування**: у `main.py` увімкнено UTF‑8 для `stdout/stderr`, щоб український текст не падав при `print()`.

