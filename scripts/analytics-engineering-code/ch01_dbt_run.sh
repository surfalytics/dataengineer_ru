#!/usr/bin/env bash
# Глава 1: запуск dbt-модели total_revenue на DuckDB во временной папке.
# Нужен venv с dbt-duckdb==1.11.1 (dbt-core 1.12.7).
# Использование: VENV=<путь к venv> bash scripts/analytics-engineering-code/ch01_dbt_run.sh
set -euo pipefail
VENV="${VENV:?укажите VENV с dbt-duckdb}"
WORK="$(mktemp -d)"
cp -R "$(dirname "$0")/ch01_dbt/." "$WORK/"
cd "$WORK"
"$VENV/bin/dbt" seed --profiles-dir . -q
"$VENV/bin/dbt" run --profiles-dir . -q
"$VENV/bin/python" -I -c "import duckdb; duckdb.connect('ch01.duckdb').sql('select * from total_revenue').show()"
rm -rf "$WORK"
