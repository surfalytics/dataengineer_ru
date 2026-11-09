#!/usr/bin/env bash
# Собирает учебную базу sql-tutorial.duckdb из открытых источников.
# Нужны: python3 (+ openpyxl), duckdb CLI 1.2+.
# Результат: scripts/sql-tutorial-db/.cache/sql-tutorial.duckdb
set -euo pipefail
cd "$(dirname "$0")"

python3 fetch.py
python3 prepare.py
python3 generate_football.py .cache/csv
python3 generate_yammer.py .cache/csv

cd .cache
rm -f sql-tutorial.duckdb
duckdb sql-tutorial.duckdb < ../build.sql
duckdb sql-tutorial.duckdb -c "CHECKPOINT;" > /dev/null
ls -lh sql-tutorial.duckdb
