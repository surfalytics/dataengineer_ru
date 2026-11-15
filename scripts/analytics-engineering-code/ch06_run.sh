#!/usr/bin/env bash
# Глава 6: собирает проект omnichannel (dbt) на DuckDB с нуля: deps, build.
# Запуск: bash scripts/analytics-engineering-code/ch06_run.sh
# Нужен venv: uv venv --python 3.13 .venv && uv pip install -r requirements-ch06.txt
# Сеть нужна для dbt deps. Можно задать свой venv: VENV=/path/to/venv bash ch06_run.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="${VENV:-$HERE/.venv}"
PY="$VENV/bin/python"
DBT="$VENV/bin/dbt"
cd "$HERE/ch06_dbt"
rm -rf omnichannel.duckdb target logs dbt_packages package-lock.yml
"$PY" -c "import duckdb; duckdb.connect('omnichannel.duckdb').execute(open('raw.sql').read())"
export DBT_PROFILES_DIR="$PWD"
"$DBT" --quiet deps
"$DBT" build
