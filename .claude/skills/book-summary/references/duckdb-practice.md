# DuckDB practice inside a chapter

Read this file only if the chapter page gets a `## Практика в DuckDB` section.

Use it for technical books where SQL shows the idea (modeling, SQL, ETL).

- Start: `Запустите \`duckdb\` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.`
- `### Шаг 1. Создаём ...` - create small tables with `VALUES` and `generate_series`. No files to download.
- `### Шаг 2. Проверяем` - a sanity query (row counts, "this must return 0 rows").
- Keep it short: one setup block, one check, 2-3 tasks.
- `### Задания` - 2-3 tasks. Each solution is in `<details><summary>Решение</summary> ... </details>`, with one line that explains the result.
- All blocks run top to bottom in one in-memory session.
- Check the chapter: `python3 scripts/kimball-diagrams/check_sql.py <chapter.md>` (needs DuckDB CLI). It must print `OK`.
