#!/usr/bin/env python3
"""Глава 15 (Airflow): новые диаграммы. Старые (ch15-executors, ch15-metrics-stack) делает specs/ch15.py.
Usage: python3 scripts/airflow-diagrams/ch15_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 15.8: путь task и кто за него отвечает ----------
D["ch15-task-states"] = dict(items=[
    Z("Task scheduler решает, что готово", 0, 0, 640, 200),
    N("s1", "scheduled\nусловия выполнены", 30, 60, "y", 260, 90),
    N("s2", "queued\nесть слоты, команда в очереди", 340, 60, "y", 270, 90),
    Z("Task executor запускает", 0, 260, 700, 340),
    N("s3", "running\nairflow tasks run\nв отдельном процессе", 30, 380, "p", 280, 100),
    N("s4", "success\nкод возврата 0", 420, 310, "g", 240, 80),
    N("s5", "failed\nкод возврата не 0", 420, 450, "r", 240, 80),
    T("пока task идёт, она шлёт heartbeat в metastore\n(каждые 5 секунд по умолчанию)", 30, 625, 18, GRAY),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s3", "s5")])

# ---------- таблица 15.2: лимиты параллелизма ----------
D["ch15-concurrency-limits"] = dict(items=[
    T("Лимиты работают вместе: действует самый строгий", 0, -50, 22, "#1971c2"),
    N("d1", "DAG A\nготово 40 tasks", 0, 20, "n", 200, 80),
    N("d2", "DAG B\nготово 40 tasks", 0, 170, "n", 200, 80),
    N("l1", "max_active_tasks_per_dag\n16 на каждый DAG", 320, 90, "p", 280, 90),
    N("l2", "parallelism\n32 на всю систему", 700, 90, "y", 240, 90),
    N("l3", "default_pool\n128 слотов", 1040, 90, "pu", 220, 90),
    N("w", "Celery: worker_concurrency\n16 процессов на worker", 700, 260, "g", 300, 90),
    T("итог: 16 + 16 = 32 tasks работают, остальные ждут", 320, 400, 18, GRAY),
], edges=[E("d1", "l1"), E("d2", "l1"), E("l1", "l2"), E("l2", "l3"), E("l2", "w")])

if __name__ == "__main__":
    run_all(D)
