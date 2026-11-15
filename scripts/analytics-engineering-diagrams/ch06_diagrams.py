#!/usr/bin/env python3
"""Chapter 6 (end-to-end use case) Excalidraw diagrams. Usage: ch06_diagrams.py [name ...]  (no args = all)
ER diagrams of this chapter are Mermaid: ch06_mermaid.sh."""
from excb import N, E, Z, T, run_all

D = {}

# Fig 6-4 + the whole chapter path: source -> ETL -> raw -> dbt -> analytics -> SQL
D["ch06-architecture"] = dict(items=[
    Z("BigQuery", 640, -60, 740, 700),
    N("mysql", "MySQL\nOMNI_MANAGEMENT\nоперационная база", 0, 0, "n", 260, 120),
    N("etl", "Python-скрипт ETL\nextract → transform\n→ load", 340, 0, "pu", 240, 120),
    N("raw", "omnichannel_raw\nсырые таблицы\n1:1 с источником", 700, 0, "db", 260, 120),
    N("stg", "dbt: staging\nstg_* — по одной\nмодели на таблицу", 700, 240, "p", 260, 120),
    N("mart", "dbt: marts\ndim_* и fct_*\nstar schema", 1080, 240, "p", 260, 120),
    N("prod", "omnichannel_analytics\nproduction-датасет\n(job в dbt Cloud)", 1080, 480, "db", 260, 120),
    N("sql", "SQL-анализ\nответы на\nбизнес-вопросы", 340, 480, "g", 240, 120),
    T("Тесты и документация dbt\nпроверяют модели перед production", 700, 420, 18, "#2f9e44"),
], edges=[E("mysql", "etl"), E("etl", "raw"), E("raw", "stg", "source()"), E("stg", "mart", "ref()"),
          E("mart", "prod", "dbt build"), E("prod", "sql", "запросы")])

if __name__ == "__main__":
    run_all(D)
