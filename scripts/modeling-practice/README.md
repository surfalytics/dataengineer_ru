# Учебные файлы для курса «Базовый минимум Dimensional Modeling»

Уроки лежат в `src/content/docs/practice/modeling/`.

## Сборка

Запускайте из корня репозитория.

```bash
python3 scripts/modeling-practice/build.py            # архив public/assets/practice/modeling-practice.tar.gz
python3 scripts/modeling-practice/check_sql.py        # запускает все SQL-блоки уроков в DuckDB
python3 scripts/modeling-practice/check_sql.py --show scd   # печатает результаты блоков урока scd
```

- `build.py` — генератор с фиксированным seed. Архив каждый раз побайтно одинаковый.
- Схемы курса лежат в `scripts/modeling-diagrams/`: ER — Mermaid (`build.sh`), остальные — Excalidraw (`excalidraw_build.py`).
- `check_sql.py` — нужен `duckdb` CLI. Блоки идут по `sidebar.order`, в одной базе, как у ученика.

## Важно

Ответы в уроках («Проверка») посчитаны на этих данных.
Если меняете генератор или SQL, запустите `check_sql.py --show` и обновите ответы.
SQL-блоки в уроках должны запускаться повторно: используйте `CREATE OR REPLACE`.
