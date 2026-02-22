## Purpose

Define requirements for the module 1 student assistant agent built with LangChain tools, Ukrainian responses, and report persistence.

## Requirements

### Requirement: Get Current Date Tool
Агент МАЄ (SHALL) мати інструмент `get_current_date`, який повертає поточну дату та час.

#### Scenario: Agent requests current date
- **WHEN** агент потребує знати поточну дату для правильної відповіді на питання (наприклад, "який зараз рік?")
- **THEN** агент викликає інструмент `get_current_date` і отримує рядок з поточною датою та часом

### Requirement: Web Search Tool
Агент МАЄ (SHALL) мати інструмент `search_web`, який використовує DuckDuckGo для пошуку інформації в інтернеті.

#### Scenario: Agent searches for specific topic
- **WHEN** агент отримує запит про подію чи інформацію, якої немає в його базових знаннях (наприклад, актуальні новини)
- **THEN** агент викликає інструмент `search_web` із відповідним запитом та отримує текстові результати пошуку

### Requirement: Save Report Tool
Агент МАЄ (SHALL) мати інструмент `save_report`, який зберігає результати його роботи у форматі JSON.

#### Scenario: Agent saves final report
- **WHEN** агент успішно зібрав інформацію та сформував відповідь на запит користувача
- **THEN** агент викликає інструмент `save_report`, який створює або перезаписує JSON-файл з полями `topic`, `result` (згенерований звіт) та `timestamp`

### Requirement: Ukrainian System Prompt
Агент МАЄ (SHALL) бути налаштований за допомогою system prompt, який вказує йому відповідати українською мовою та позиціонує його як помічника для студентів.

#### Scenario: Agent responds to a query
- **WHEN** агент генерує фінальну відповідь користувачеві
- **THEN** відповідь обов'язково формується українською мовою, незалежно від мови знайдених в інтернеті джерел

### Requirement: LangChain LCEL Integration
Система МАЄ (SHALL) використовувати LangChain (ChatPromptTemplate, ChatOpenAI, StrOutputParser) для створення ланцюжка обробки, який зв'язує промпт, LLM (gpt-4) та інструменти.

#### Scenario: Execution of the chain
- **WHEN** користувач запускає скрипт із заданою темою (`topic`)
- **THEN** скрипт успішно ініціалізує ланцюжок, викликає LLM, LLM при потребі використовує інструменти, і в результаті формується фінальний звіт, який зберігається у файл та/або виводиться у консоль
