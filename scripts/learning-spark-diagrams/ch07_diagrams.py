#!/usr/bin/env python3
"""Chapter 7 (Optimizing and Tuning Spark Applications) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own: order of precedence of Spark settings
D["ch07-config-order"] = dict(items=[
    T("От слабого уровня к сильному", 0, -50, 22, "#495057"),
    N("a", "spark-defaults.conf\nвсе приложения кластера", 0, 0, "n", 300, 110),
    N("b", "spark-submit --conf\nодно приложение", 520, 0, "y", 300, 110),
    N("c", "SparkSession\nв коде приложения", 1040, 0, "p", 300, 110),
    N("d", "Итоговое значение\nпобеждает самый сильный уровень", 500, 240, "g", 360, 110),
], edges=[E("a", "b", "перекрывает"), E("b", "c", "перекрывает"), E("c", "d"), E("b", "d", dashed=True), E("a", "d", dashed=True)])

# Fig 7-2: executor memory layout
D["ch07-memory"] = dict(items=[
    N("top", "spark.executor.memory\nпамять одного executor", 300, 0, "n", 520, 100),
    N("res", "Reserved memory\n300 МБ от сбоев OOM", 0, 230, "r", 300, 110),
    N("ex", "Execution memory\nshuffle, join, sort, агрегации", 520, 230, "p", 340, 110),
    N("st", "Storage memory\nкэш DataFrame и partition", 1160, 230, "g", 340, 110),
    T("Unified memory: spark.memory.fraction = 0,6", 520, 380, 20, "#495057"),
], edges=[E("top", "res"), E("top", "ex"), E("top", "st"), E("ex", "st", "занимают друг у друга")])

# Fig 7-6: broadcast hash join
D["ch07-broadcast-join"] = dict(items=[
    N("small", "Маленькая таблица\nменьше 10 МБ", 0, 150, "y", 260, 110),
    N("e1", "Executor 1\nбольшая partition A\n+ копия маленькой таблицы", 560, 0, "g", 340, 130),
    N("e2", "Executor 2\nбольшая partition B\n+ копия маленькой таблицы", 560, 300, "g", 340, 130),
    N("o1", "join на месте\nбез shuffle", 1060, 0, "p", 240, 130),
    N("o2", "join на месте\nбез shuffle", 1060, 300, "p", 240, 130),
], edges=[E("small", "e1", "broadcast"), E("small", "e2", "broadcast"), E("e1", "o1"), E("e2", "o2")])

# Fig 7-7..7-9: sort merge join with and without bucketing
D["ch07-smj-bucketing"] = dict(items=[
    T("Без bucketing: обе таблицы перемешивают по сети", 0, -50, 22, "#e03131"),
    N("a1", "Две большие\nтаблицы", 0, 0, "db", 240, 100),
    N("a2", "Exchange\nshuffle по ключу", 330, 0, "r", 260, 100),
    N("a3", "Sort", 680, 0, "y", 200, 100),
    N("a4", "Merge", 970, 0, "g", 200, 100),
    T("С bucketing: таблицы уже лежат по бакетам ключа", 0, 190, 22, "#2f9e44"),
    N("b1", "Две таблицы\nbucketBy(8, ключ)", 0, 240, "db", 240, 100),
    N("b3", "Sort\n(данные уже по бакетам)", 330, 240, "y", 260, 100),
    N("b4", "Merge", 680, 240, "g", 200, 100),
    T("Exchange не нужен", 970, 275, 22, "#2f9e44"),
], edges=[E("a1", "a2"), E("a2", "a3"), E("a3", "a4"), E("b1", "b3"), E("b3", "b4")])

if __name__ == "__main__":
    run_all(D)
