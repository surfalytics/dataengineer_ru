#!/usr/bin/env python3
"""Глава 2 (Airflow): новые диаграммы. Старые (ch02-rocket-dag, ch02-failure-clear) делает specs/ch02.py.
Usage: python3 scripts/airflow-diagrams/ch02_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 2.5: DAG, task, operator ----------
D["ch02-dag-task-operator"] = dict(items=[
    Z("DAG: порядок tasks и расписание", 0, 0, 1000, 460),
    N("t1", "task\ndownload_launches", 40, 70, "p", 280, 80), N("t2", "task\nget_pictures", 360, 70, "p", 280, 80),
    N("t3", "task\nnotify", 680, 70, "p", 280, 80),
    N("o1", "operator\nBashOperator\n(команда curl)", 40, 230, "g", 280, 100), N("o2", "operator\nPythonOperator\n(функция Python)", 360, 230, "g", 280, 100),
    N("o3", "operator\nBashOperator\n(команда echo)", 680, 230, "g", 280, 100),
    T("task = оболочка: состояние, ошибки, зависимости. operator = сама работа.", 40, 390, 20, GRAY),
], edges=[E("t1", "t2"), E("t2", "t3"), E("t1", "o1"), E("t2", "o2"), E("t3", "o3")])

# ---------- Fig 2.19-2.21: DAG versioning ----------
D["ch02-dag-versions"] = dict(items=[
    T("v1: код DAG до правки", 0, -40, 20, "#1971c2"),
    N("a1", "download_launches", 0, 0, "p", 260, 80), N("a2", "get_pictures", 330, 0, "p", 260, 80), N("a3", "notify", 660, 0, "p", 260, 80),
    T("v2: DAG processor увидел правку и создал версию, добавлена task", 0, 160, 20, "#2f9e44"),
    N("b1", "download_launches", 0, 220, "p", 260, 80), N("b2", "get_pictures", 330, 220, "p", 260, 80),
    N("b3", "notify", 660, 220, "p", 260, 80), N("b4", "versioning_example_task", 990, 220, "g", 300, 80),
    T("Запуск идёт по последней версии (v2). Старые версии видно в меню Versions.", 0, 350, 20, GRAY),
], edges=[E("a1", "a2"), E("a2", "a3"), E("b1", "b2"), E("b2", "b3"), E("b3", "b4")])

if __name__ == "__main__":
    run_all(D)
