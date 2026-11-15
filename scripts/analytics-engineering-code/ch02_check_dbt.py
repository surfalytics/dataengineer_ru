#!/usr/bin/env python3
"""Check the dbt code of chapter 2 without dbt: run every ```sql block of the page in DuckDB,
then render each ```jinja block (ref() and source() become table names, config() is removed)
and build it on the same data. Models become views (tables if materialized='table'),
tests are run and their failing rows counted. Standard library + duckdb CLI.
Usage: python3 -I scripts/analytics-engineering-code/ch02_check_dbt.py"""
import re, subprocess, sys
from pathlib import Path

PAGE = Path(__file__).resolve().parents[2] / (
    "src/content/docs/book-summaries/engineering/analytics-engineering-with-sql-and-dbt/"
    "02-data-modeling-for-analytics.md")
text = PAGE.read_text(encoding="utf-8")
sql = re.findall(r"```sql\n(.*?)```", text, re.S)
jinja = re.findall(r"```jinja\n(.*?)```", text, re.S)

def render(code, **params):
    code = re.sub(r"\{\{\s*source\('(\w+)',\s*'(\w+)'\)\s*\}\}", r"\1_\2", code)
    code = re.sub(r"\{\{\s*ref\('(\w+)'\)\s*\}\}", r"\1", code)
    code = re.sub(r"\{\{\s*config\(.*?\)\s*\}\}", "", code, flags=re.S)
    for k, v in params.items():
        code = re.sub(r"\{\{\s*%s\s*\}\}" % k, v, code)
    return code.strip()

steps = []
for block in jinja:
    path = block.splitlines()[0].removeprefix("-- ").strip()
    name = Path(path).stem
    if path.startswith("models/"):
        kind = "TABLE" if "materialized='table'" in block else "VIEW"
        steps.append(f"CREATE OR REPLACE {kind} {name} AS\n{render(block)};")
        steps.append(f"SELECT '{path}' AS model, COUNT(*) AS rows FROM {name};")
    elif path.startswith("tests/generic/"):
        body = re.search(r"\{% test \w+\(model, column_name\) %\}(.*?)\{% endtest %\}", block, re.S).group(1)
        steps.append(f"SELECT '{path} on stg_books.price' AS test, COUNT(*) AS failing_rows "
                     f"FROM ({render(body, model='stg_books', column_name='price')});")
    elif path.startswith("tests/"):
        steps.append(f"SELECT '{path}' AS test, COUNT(*) AS failing_rows FROM ({render(block)});")
script = ".output /dev/null\n" + "\n".join(sql) + "\n.output stdout\n.mode list\n.headers off\n" + "\n".join(steps)
r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
if r.returncode:
    sys.exit("FAIL\n" + r.stderr[:1500])
print(r.stdout.strip()); print("OK")
