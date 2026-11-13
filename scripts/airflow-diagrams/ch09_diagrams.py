#!/usr/bin/env python3
"""Глава 9 (Airflow): новые диаграммы. Старые (ch09-layers, ch09-deferrable) делает specs/ch09.py.
Usage: python3 scripts/airflow-diagrams/ch09_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 9.6: worker slots, обычный и deferrable подход ----------
D["ch09-worker-slots"] = dict(items=[
    T("Кто ждёт внешнюю систему: worker или triggerer", 0, -50, 22, "#1971c2"),
    Z("Обычный task: один task держит один worker slot", -20, 0, 760, 420),
    N("a1", "Task 1", 20, 70, "p", 160, 70),
    N("a2", "Task 2", 20, 170, "p", 160, 70),
    N("a3", "Task n", 20, 270, "p", 160, 70),
    N("w1", "Worker 1\n(ждёт)", 300, 70, "r", 200, 70),
    N("w2", "Worker 2\n(ждёт)", 300, 170, "r", 200, 70),
    N("w3", "Worker n\n(ждёт)", 300, 270, "r", 200, 70),
    N("ext1", "Внешняя\nсистема", 570, 170, "n", 150, 90),
    T("100 задач по часу на 10 workers: 10 часов", 20, 370, 18, "#e03131"),
    Z("Deferrable task: ждёт triggerer, slots свободны", 840, 0, 760, 420),
    N("b1", "Task 1", 880, 70, "pu", 160, 70),
    N("b2", "Task 2", 880, 170, "pu", 160, 70),
    N("b3", "Task n", 880, 270, "pu", 160, 70),
    N("trg", "Triggerer\nasyncio, один процесс", 1160, 135, "y", 240, 120),
    N("ext2", "Внешняя\nсистема", 1470, 170, "n", 110, 90),
    T("Сотни ожидающих tasks. Workers свободны для готовых tasks", 880, 370, 18, "#2f9e44"),
], edges=[E("a1", "w1"), E("a2", "w2"), E("a3", "w3"), E("w2", "ext1"),
          E("b1", "trg"), E("b2", "trg"), E("b3", "trg"), E("trg", "ext2")])

# ---------- 9.6: пакет с custom-компонентами ----------
D["ch09-package"] = dict(items=[
    T("Custom-компоненты в пакете и где его нужно поставить", 0, -50, 22, "#1971c2"),
    N("src", "airflow-orders/\nsetup.py\nsrc/airflow_orders/\nhooks.py operators.py sensors.py", 0, 40, "y", 380, 150),
    N("pip", "pip install ./airflow-orders\n(или git+https, PyPI, private index)", 480, 60, "n", 340, 110),
    N("sch", "scheduler / DAG processor", 920, -10, "p", 300, 70),
    N("wrk", "workers", 920, 80, "p", 300, 70),
    N("trg", "triggerer\n(если есть свой trigger)", 920, 170, "pu", 300, 80),
    T("Пакет и его зависимости ставят во все окружения Airflow.", 0, 260, 20, GRAY),
    T("Лучший путь для общего кода: добавить operator в существующий provider.", 0, 295, 20, GRAY),
], edges=[E("src", "pip"), E("pip", "sch"), E("pip", "wrk"), E("pip", "trg")])

if __name__ == "__main__":
    run_all(D)
