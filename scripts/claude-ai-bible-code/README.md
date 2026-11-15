# Код к конспекту Claude AI Bible

Запуск из корня репозитория: `python3 -I scripts/claude-ai-bible-code/<файл>`.
Большинство скриптов работает на стандартной библиотеке Python 3.10+. Платный ключ API не нужен: вызовы Claude заменены заготовками или mock.
Пакеты для глав 16-18 — в `requirements.txt` (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).
Проверка детерминизма: `python3 -I scripts/book-tools/same_output.py <скрипт>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | — | — | в главе нет кода |
| 2 | В главе нет кода. Есть только имена моделей в API (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`), они даны в тексте | — | ok (нечего запускать) |
| 3 | В главе нет кода | — | ok (нечего запускать) |
| 4 | В главе нет кода | — | ok: нечего запускать |
| 5 | Примеры prompt: слабый и сильный, system/user, рассуждение, few-shot, теги, формат, «сначала вопросы» | на странице, блоки `text` | ok (не код) |
| 6 | Проверка JSON по схеме и текст ошибки для цикла исправления (вместо ответов модели — строки) | ch06_json_check.py | ok (same x6) |
| 6 | Маленький `eval`: 12 писем, две версии классификатора (правила вместо модели) | ch06_eval.py | ok (same x6) |
| 7 | Инструкции проекта (текст `system prompt`, наш вариант для команды данных) | на странице, блок `text` | ok: это текст для Claude, а не код, запускать нечего |
| 8 | В главе нет кода. Только примеры запросов (prompt), они пересказаны на странице в блоках `text` | — | ok: нечего запускать |
| 9 | — | — | кода в главе нет |
| 10 | Поручение: утренний брифинг (текст для Cowork) | на странице, блок `text` | ok: текст, не код, запускать нечего |
| 10 | Поручение: еженедельный отчёт по Pipeline.xlsx | на странице, блок `text` | ok: текст, не код, запускать нечего |
| 10 | Пример `skill` для заметок встреч (формат SKILL.md) | на странице, блок `markdown` | ok: наш пример, в книге описан словами; front matter проверен как YAML |
| 11 | Запрос: извлечь список со страницы в таблицу | — (текст на странице) | ok: не код |
| 12 | В главе нет кода. Запросы к агенту (формула, очистка, прогноз денежного потока) пересказаны на странице как блоки `text` | — | ok: запускать нечего |
| 13 | Установка через npm, `claude --version`, `cd` + `claude` | на странице | ok: однострочные команды из книги; `claude --version` дал реальный вывод `2.1.325 (Claude Code)`, установку не запускали (меняет систему) |
| 13 | Пример сессии (валидация email и телефона) | на странице, блок `text`, наш пример | ok: это пересказ экрана сессии, не код |
| 13 | `hooks` в settings.json (PostToolUse) | на странице, обновлён под текущий формат (вложенный `hooks`, `"type": "command"`) | ok: JSON проверен `json.loads` |
| 13 | Hook против сброса базы (в книге только история) | `ch13_block_db_reset.py` + тест `ch13_hook_test.py` | ok, same x6 |
| 13 | settings.json: model и permissions | на странице, как в книге | ok: JSON проверен `json.loads` |
| 13 | CLAUDE.md | на странице, наш вариант для data-проекта | ok: Markdown, не запускается |
| 13 | Git: status, add, commit, restore, reset --hard, diff | на странице + `ch13_git_safety.sh` (временная папка) | ok, вывод на странице реальный |
| 13 | `.mcp.json` с mcpServers | на странице, ключ через `${DOCS_API_KEY}` | ok: JSON проверен; сам сервер `@yourco/docs-mcp-server` вымышленный, как в книге |
| 14 | SKILL.md недельной сводки (наша русская версия) | ch14_weekly-store-summary/SKILL.md | ok (текст, на странице совпадает с файлом) |
| 14 | Скрипт конверсии для skill | ch14_weekly-store-summary/scripts/conversion.py | ok (`python3 -I ... 412 3870` → 10.6%, same x6) |
| 14 | Образец результата | ch14_weekly-store-summary/resources/example-summary.md | ok (заглушка) |
| 15 | Сборка plugin release-notes-kit во временной папке, проверка manifest, проверка повышения версии (major/minor) | ch15_plugin_check.py | ok (только stdlib, same x6) |
| 15 | Команды `/plugin install/list/uninstall/marketplace add/update` | — (на странице как text) | не запускается: slash-команды Claude Code внутри сессии |
| 16 | Конфиг `host` с двумя серверами (файлы и база, пользователь read-only) | ch16_mcp_config.json | ok: JSON читается в ch16_mcp_demo.py |
| 16 | Минимальный `MCP server`: один tool, один resource, один prompt | ch16_mcp_server.py | ok: проверен через in-memory client и через настоящий stdio |
| 16 | Демо: список возможностей и два вызова tool | ch16_mcp_demo.py | ok: same x6 |
| 17 | `export ANTHROPIC_API_KEY`, `pip install anthropic` | — (одна строка на странице) | ok |
| 17 | Первый вызов через `curl` | — (описан в тексте) | ok: не запускали, нужен ключ; тот же запрос делает SDK в `ch17_api_mock.py` |
| 17 | Первый вызов и полный запрос (`system`, `max_tokens`) через SDK | ch17_api_mock.py, часть 1 | ok (mock) |
| 17 | `temperature` в запросе | — | не запускается: в SDK 2.8.0 у `messages.create` нет аргумента `temperature`; на странице есть пояснение |
| 17 | Многошаговый разговор, рост входных токенов | ch17_api_mock.py, часть 2 | ok (mock) |
| 17 | `streaming` (`text_stream`, `get_final_message`) | — (описан в тексте) | ok: метод `messages.stream` есть в SDK 2.8.0, через mock не запускали |
| 17 | `stop_sequences` и `prompt caching` (`cache_control`) | код на странице | ok: тело запроса проверено через mock, сам вызов платный |
| 17 | `Batch API` (`custom_id`) | — (описан в тексте) | ok: импорты `MessageCreateParamsNonStreaming`, `Request` и `messages.batches.create` есть в SDK 2.8.0 |
| 17 | Повторы на 429/529, без повтора на 400 | ch17_api_mock.py, часть 3 | ok (mock) |
| 18 | Цикл агента без ключа: инструменты, проверка can_run, журнал on_event, лимит шагов, разбор тикетов | ch18_triage_agent.py | ok: same x6 |
| 18 | Тот же агент на claude-agent-sdk: @tool, create_sdk_mcp_server, can_use_tool, max_turns, max_budget_usd | ch18_real_sdk.py | не запускается: нужен платный ключ API; py_compile ok, имена сверены с пакетом 0.2.182 |
| 19 | Цикл `tool use`: параллельные вызовы, `is_error`, остановка на запрещённом инструменте (ответы модели — заготовки) | ch19_tool_loop.py | ok (same x6) |
| 19 | Проверка полей счёта после зрения: сумма строк, пустые поля, сверка с заказом | ch19_invoice_check.py | ok (same x6) |
| 19 | Схема инструмента `run_backfill` (JSON на странице) | — | ok (json.loads) |
| 19 | Вызов API: зрение + `tool_choice` (`record_invoice`) | — | не запускается: нужен ключ API; синтаксис проверен (ast.parse) |
| 20 | Проверка ответа роутера, запасной путь к человеку и идемпотентная отправка (вместо ответов модели — строки) | ch20_ticket_router.py | ok (same x6) |
| 20 | Вызов `client.messages.create` из книги | на странице, отдельный блок | не запускается: нужен ANTHROPIC_API_KEY |
| 21 | — (в главе нет кода) | — | ok |
| 22 | В главе нет кода. На странице только текст `prompt` для проверки фактов (блок `text`, не запускается) | — | ok (кода нет) |

## Заметки по главам

- Глава 5: В главе нет программного кода, только примеры текстов prompt. На странице они даны в блоках `text` в нашей версии (примеры из мира данных). Запускать нечего.
- Глава 6: Запуск: `python3 -I scripts/claude-ai-bible-code/<файл>`. Только стандартная библиотека, API-ключ не нужен.
- Глава 9: В главе 9 нет кода: она про приложения Claude (web, desktop, телефон, голос). Строк в реестр нет.
- Глава 11: В главе нет кода. Есть только пример запроса на извлечение данных. На странице он дан нашими словами как блок `text`. Запускать нечего.
- Глава 16: Нужен пакет `mcp==1.27.0` (Python 3.10+; проверено на 3.14). Строка для requirements.txt: `mcp==1.27.0`.
- Глава 17: Все примеры книги вызывают платный Anthropic API. Мы запускаем настоящий SDK `anthropic==2.8.0` (`requirements-ch17.txt`), но запросы ловит `httpx2.MockTransport`. Ключ и оплата не нужны. Запуск: `python3 -m venv venv && venv/bin/pip install -r requirements-ch17.txt && venv/bin/python -I ch17_api_mock.py`. Проверка `same_output.py`: `same x6`.
- Глава 18: Мок-агент работает на стандартной библиотеке Python 3.10+. Настоящий SDK: `claude-agent-sdk==0.2.182` (строка для requirements.txt, нужен только для ch18_real_sdk.py).
- Глава 19: Запуск: `python3 -I scripts/claude-ai-bible-code/<файл>`. Только стандартная библиотека, API-ключ не нужен.
- Глава 20: Запуск: `python3 -I scripts/claude-ai-bible-code/ch20_ticket_router.py`. Только стандартная библиотека, API-ключ не нужен.
