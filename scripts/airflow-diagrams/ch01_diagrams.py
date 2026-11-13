#!/usr/bin/env python3
"""Глава 1 (Airflow): новые диаграммы. Старые (ch01-airflow-components, ch01-umbrella-dag) делает specs/ch01.py.
Usage: python3 scripts/airflow-diagrams/ch01_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 1.3: acyclic vs cyclic ----------
D["ch01-dag-vs-cycle"] = dict(items=[
    T("DAG: циклов нет, у графа есть путь выполнения", 0, -50, 22, "#2f9e44"),
    N("a1", "task 1", 0, 0, "g", 200, 80), N("a2", "task 2", 320, 0, "g", 200, 80), N("a3", "task 3", 640, 0, "g", 200, 80),
    T("Граф с циклом: task 2 ждёт task 3, а task 3 ждёт task 2", 0, 170, 22, "#e03131"),
    N("c1", "task 1", 0, 240, "n", 200, 80), N("c2", "task 2", 320, 240, "r", 200, 80), N("c3", "task 3", 640, 240, "r", 200, 80),
    T("Обе стоят: это deadlock. Поэтому в Airflow граф должен быть acyclic.", 0, 380, 20, GRAY),
], edges=[E("a1", "a2"), E("a2", "a3"), E("c1", "c2"), E("c2", "c3"), E("c3", "c2")])

# ---------- Fig 1.4: execution loops ----------
def row(prefix, y, title, states):
    kinds = {"done": "g", "ready": "y", "wait": "n"}
    labels = {"done": "готова", "ready": "идёт в очередь", "wait": "ждёт upstream"}
    items = [T(title, 0, y - 36, 20, "#1971c2")]
    for i, (name, st) in enumerate(zip(["fetch", "clean", "push"], states)):
        items.append(N(f"{prefix}{i}", f"{name}\n{labels[st]}", i * 330, y, kinds[st], 270, 90))
    return items

items = (row("l1", 0, "Loop 1: у fetch нет upstream, остальные ждут", ["ready", "wait", "wait"])
         + row("l2", 190, "Loop 2: fetch готова, теперь clean может идти", ["done", "ready", "wait"])
         + row("l3", 380, "Loop 3: clean готова, очередь push", ["done", "done", "ready"])
         + [T("Конец: все tasks готовы, pipeline завершён.", 0, 520, 20, GRAY)])
edges = [E("l10", "l11"), E("l11", "l12"), E("l20", "l21"), E("l21", "l22"), E("l30", "l31"), E("l31", "l32")]
D["ch01-execution-loops"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
