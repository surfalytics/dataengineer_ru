#!/usr/bin/env python3
"""Глава 5 (Airflow): новые диаграммы. Старую (ch05-context-flow) делает specs/ch05.py.
Usage: python3 scripts/airflow-diagrams/ch05_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 5.7-5.9: как Python раздаёт аргументы функции ----------
D["ch05-kwargs-routing"] = dict(items=[
    T("Airflow вызывает функцию со всеми переменными context как keyword-аргументами", 0, -50, 22, "#1971c2"),
    N("call", "_get_data(conf=..., dag=..., dag_run=...,\ndata_interval_start=..., ...)", 0, 0, "p", 560, 100),
    N("sig", "def _get_data(data_interval_start, **context)", 0, 220, "y", 560, 90),
    N("own", "data_interval_start\nесть в сигнатуре", 700, 130, "g", 340, 90),
    N("rest", "conf, dag, dag_run и остальное\nпопадают в **context", 700, 300, "n", 340, 100),
    T("Если аргумента в сигнатуре нет, он не теряется: он идёт в **context.", 0, 380, 20, GRAY),
    T("Если аргумент есть в сигнатуре без значения по умолчанию, а context его не дал, функция упадёт.", 0, 415, 20, GRAY),
], edges=[E("call", "sig", "вызов"), E("sig", "own"), E("sig", "rest")])

# ---------- Fig 5.12, 5.15: StockSense и роль hook ----------
D["ch05-stocksense-hook"] = dict(items=[
    T("StockSense: четыре шага на каждый час", 0, -50, 22, "#1971c2"),
    N("s1", "get_data\nскачать .gz", 0, 0, "p", 230, 90),
    N("s2", "extract_gz\nраспаковать", 290, 0, "p", 230, 90),
    N("s3", "fetch_pageviews\nнайти 5 страниц\nи записать .sql", 580, 0, "p", 260, 90),
    N("s4", "write_to_postgres\nSQLExecuteQuery-\nOperator", 900, 0, "g", 270, 90),
    T("Шаги общаются через файлы в общем хранилище, а не через память.", 0, 120, 20, GRAY),
    Z("Что происходит внутри write_to_postgres", 560, 190, 800, 340),
    N("op", "Operator: что сделать\nconn_id + sql", 600, 250, "y", 250, 90),
    N("hook", "Hook (DbApiHook):\nкак сделать", 1080, 250, "y", 240, 90),
    N("meta", "Metastore\n(Connection)", 780, 410, "n", 220, 80),
    N("pg", "PostgreSQL", 1080, 410, "db", 240, 80),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"),
          E("op", "hook", "передаёт"), E("meta", "hook", "credentials", dashed=True), E("hook", "pg", "запрос")])

if __name__ == "__main__":
    run_all(D)
