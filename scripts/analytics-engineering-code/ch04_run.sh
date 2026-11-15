#!/usr/bin/env bash
# Глава 4: собирает учебный проект dbt на DuckDB с нуля.
# Запуск: bash scripts/analytics-engineering-code/ch04_run.sh
# Нужен venv: uv venv --python 3.13 .venv && uv pip install -r requirements-ch04.txt
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/.venv/bin/python"
DBT="$HERE/.venv/bin/dbt"
cd "$HERE/ch04_jaffle"
rm -rf jaffle.duckdb target logs
"$PY" -c "import duckdb; duckdb.connect('jaffle.duckdb').execute(open('raw.sql').read())"
export DBT_PROFILES_DIR="$PWD"
"$DBT" --quiet seed
"$DBT" --quiet run
"$DBT" test 2>&1 | grep -E "PASS=|FAIL |WARN " || true
"$DBT" source freshness 2>&1 | grep -E "PASS|WARN|ERROR" | sed -E 's/^[0-9:]+ +//' || true
"$DBT" --quiet compile
for f in most_valuable_customers customer_range_based_on_total_paid_amount; do
  echo "== $f"
  "$PY" - "$f" <<'PY'
import duckdb, sys
sql = open(f"target/compiled/jaffle_book/analyses/{sys.argv[1]}.sql").read()
duckdb.connect("jaffle.duckdb", read_only=True).sql(sql).show()
PY
done
