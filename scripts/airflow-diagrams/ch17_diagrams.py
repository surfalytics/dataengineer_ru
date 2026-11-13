#!/usr/bin/env python3
"""Глава 17 (Airflow): новые диаграммы. Старые (ch17-deploy-choice, ch17-dag-delivery) делает specs/ch17.py.
Usage: python3 scripts/airflow-diagrams/ch17_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- values-файлы накапливают правки ----------
def vrow(i, y, cells):
    kinds = ["p", "y", "db", "pu"]
    names = ["пользователь", "secret key", "внешняя БД", "доставка DAG"]
    items = [N(f"f{i}", f"values-0{i + 1}.yaml", 0, y, "n", 250, 80)]
    for j in range(cells):
        items.append(N(f"c{i}{j}", names[j], 290 + j * 250, y, kinds[j], 230, 80))
    return items

items = [T("Каждый новый values-файл повторяет все прежние правки", 0, -50, 22, "#1971c2")]
for i in range(4):
    items += vrow(i, i * 120, i + 1)
items.append(T("Если оставить только новую правку, helm вернёт остальное к значениям chart по умолчанию", 0, 500, 20, "#e03131"))
D["ch17-values-layers"] = dict(items=items, edges=[])

# ---------- два executor в одном DAG ----------
D["ch17-multi-executor"] = dict(items=[
    N("dag", "DAG\nдве task", 0, 150, "n", 220, 100),
    N("t1", "task on_celery", 360, 20, "p", 260, 90),
    N("t2", "task on_k8s", 360, 280, "g", 260, 90),
    N("w1", "Celery worker\nобщий image", 760, 20, "p", 280, 90),
    N("w2", "новый pod\nсвой image на одну task", 760, 280, "g", 280, 90),
    N("r1", "нет нужной библиотеки:\ntask падает", 1180, 20, "r", 280, 90),
    N("r2", "библиотека есть:\ntask успешна", 1180, 280, "g", 280, 90),
    T("CeleryExecutor", 380, -30, 20, "#1971c2"),
    T("KubernetesExecutor", 380, 230, 20, "#2f9e44"),
], edges=[E("dag", "t1"), E("dag", "t2"), E("t1", "w1"), E("t2", "w2"), E("w1", "r1"), E("w2", "r2")])

if __name__ == "__main__":
    run_all(D)
