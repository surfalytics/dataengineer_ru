#!/usr/bin/env python3
"""Глава 3 (Airflow): новые диаграммы. Старые (ch03-trigger-vs-interval, ch03-incremental-partitions) делает specs/ch03.py.
Usage: python3 scripts/airflow-diagrams/ch03_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 3.7/3.8: интервалы и момент старта run ----------
items = [T("Data interval timetable: время режется на интервалы, run идёт в конце интервала", 0, -50, 22, "#1971c2")]
edges = []
for i, (a, b) in enumerate([("01-01", "01-02"), ("01-02", "01-03"), ("01-03", "01-04")]):
    x = i * 380
    items.append(N(f"i{i}", f"Интервал {i + 1}\n{a} 00:00 → {b} 00:00", x, 0, "p", 330, 90))
    items.append(N(f"r{i}", f"run стартует {b} 00:00\nlogical_date = {a}", x, 190, "g", 330, 90))
    edges.append(E(f"i{i}", f"r{i}", "после конца"))
items.append(T("data_interval_start = начало интервала (включено), data_interval_end = конец (не включён).", 0, 330, 20, GRAY))
D["ch03-interval-timeline"] = dict(items=items, edges=edges)

# ---------- Fig 3.10: атомарность ----------
D["ch03-atomicity"] = dict(items=[
    T("Плохо: две работы в одной task", 0, -50, 22, "#e03131"),
    N("a1", "fetch_events", 0, 0, "p", 260, 80),
    N("a2", "calculate_stats\n+ отправка письма", 360, 0, "r", 320, 80),
    N("a3", "stats.csv записан,\nписьмо не ушло,\ntask failed", 780, 0, "y", 300, 80),
    T("Task упала, но результат уже записан: состояние системы неясно.", 0, 100, 20, GRAY),
    T("Хорошо: каждая task делает всё или ничего", 0, 190, 22, "#2f9e44"),
    N("b1", "fetch_events", 0, 250, "p", 260, 80),
    N("b2", "calculate_stats", 360, 250, "g", 260, 80),
    N("b3", "send_stats", 720, 250, "g", 260, 80),
    T("Письмо не ушло: упала только send_stats, stats.csv верный. Повтор запускает одну task.", 0, 350, 20, GRAY),
], edges=[E("a1", "a2"), E("a2", "a3"), E("b1", "b2"), E("b2", "b3")])

if __name__ == "__main__":
    run_all(D)
