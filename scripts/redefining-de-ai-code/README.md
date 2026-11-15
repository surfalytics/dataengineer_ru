# Код к конспекту Redefining Data Engineering with AI

Только стандартная библиотека Python 3.10+ и DuckDB CLI (для SQL). Платных API нет.
Запуск из корня репозитория: `python3 -I scripts/redefining-de-ai-code/<файл>.py`.
Страницы глав собираются из шаблона командой `python3 scripts/redefining-de-ai-code/embed.py <шаблон.md> <страница.md>`.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | В главе нет кода | — | ok: кода нет, практика не нужна |
| 2 | Промпты из раздела о `prompt engineering` (плохой и лучший) | на странице, текст | ok: это текст, не код |
| 2 | `simple_rag.py` из репозитория книги: словарь книг + system prompt | `ch02_rag_library.py` (наша версия: chunking, поиск по сходству, сборка prompt; без API) | ok |
| 2 | `make load-data`, `generate-embeddings`, `assistant-rag`: 200 книг в DuckDB и вопрос «топ продаж по отделам» | SQL в разделе «Практика в DuckDB» на странице | ok (check_sql.py) |
| 2 | `library_server.py`: MCP tool `search_sales` | показан как фрагмент на странице, не запускается | не запускается: репозиторий книги ещё не открыт, нужен пакет `mcp` и LLM API |
| 2 | `make mcp-compare-modes`, `mcp-benchmark`: токены с `code execution` и без | `ch02_tool_tokens.py` (наша модель подсчёта токенов) | ok |
| 2 | `make assistant`, `make multi-agent` | — | не запускается: репозиторий книги ещё не открыт, нужен LLM API |
