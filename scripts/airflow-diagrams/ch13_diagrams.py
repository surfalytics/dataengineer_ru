#!/usr/bin/env python3
"""Глава 13 (Airflow): новые диаграммы. Старые (ch13-nyc-pipeline, ch13-idempotent-write) делает specs/ch13.py.
Usage: python3 scripts/airflow-diagrams/ch13_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 13.x: PandasOperator ----------
D["ch13-pandas-operator"] = dict(items=[
    Z("PandasOperator: одна задача склеивает три функции вокруг DataFrame", 0, 0, 1100, 330),
    N("in", "input_callable\nчитает данные", 40, 70, "p", 230, 90),
    N("df1", "DataFrame", 340, 70, "y", 150, 90),
    N("tr", "transform_callable\n(необязательная)", 560, 70, "p", 230, 90),
    N("df2", "DataFrame", 860, 70, "y", 150, 90),
    N("out", "output_callable\nзаписывает данные", 560, 210, "p", 230, 90),
    T("raw: CSV или JSON", 40, 175, 18, GRAY),
    T("processed: Parquet", 830, 270, 18, GRAY),
    T("Меняем формат входа: pd.read_csv на pd.read_parquet. Код не дублируется.", 0, 360, 20, "#2f9e44"),
], edges=[E("in", "df1"), E("df1", "tr"), E("tr", "df2"), E("df2", "out")])

if __name__ == "__main__":
    run_all(D)
