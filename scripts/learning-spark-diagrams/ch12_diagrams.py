#!/usr/bin/env python3
"""Chapter 12 (Epilogue: Apache Spark 3.0) diagrams. Usage: ch12_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 12-1, 12-2: dynamic partition pruning with a broadcast join
D["ch12-dpp"] = dict(items=[
    N("dim", "Таблица измерений\ndim_date\nфильтр is_weekend", 0, 0, "y", 270, 110),
    N("ht", "Hash table\n(build relation)\nв broadcast variable", 330, 0, "p", 270, 110),
    N("ex", "Каждый executor\nпроверяет hash table", 660, 0, "g", 270, 110),
    N("scan", "Scan факт-таблицы\nsales", 990, 0, "q", 270, 110),
    N("p1", "partition\nsale_date = 03.01\nчитаем", 660, 260, "g", 270, 110),
    N("p2", "partition\nsale_date = 04.01\nпропускаем", 990, 260, "n", 270, 110),
    N("p3", "partition\nsale_date = 10.01\nчитаем", 1320, 260, "g", 270, 110),
    T("Фильтр из измерения попадает в scan факта: читаем только нужные partition", 0, 440, 20, "#495057"),
], edges=[E("dim", "ht"), E("ht", "ex"), E("ex", "scan"),
          E("scan", "p1"), E("scan", "p3")])

# Fig 12-3, 12-4: AQE loop at materialization points
D["ch12-aqe"] = dict(items=[
    N("a", "1. Выполняем stage\nдо shuffle или broadcast\n(materialization point)", 0, 0, "p", 330, 120),
    N("b", "2. Собираем статистику:\nчисло partition,\nбайты данных", 480, 0, "y", 330, 120),
    N("c", "3. Catalyst заново\nоптимизирует план", 480, 260, "q", 330, 120),
    N("d", "4. Новый план\nвыполняет следующий stage", 0, 260, "g", 330, 120),
    N("o1", "Склеить мелкие partition\nпосле shuffle", 1000, 0, "n", 340, 100),
    N("o2", "Заменить SortMergeJoin\nна BroadcastHashJoin", 1000, 150, "n", 340, 100),
    N("o3", "Разбить перекошенные\npartition (skew join)", 1000, 300, "n", 340, 100),
    T("Цикл повторяется, пока не выполнены все stage", 0, 440, 20, "#495057"),
], edges=[E("a", "b"), E("b", "c"), E("c", "d"), E("d", "a"),
          E("c", "o1"), E("c", "o2"), E("c", "o3")])

# Own: pandas UDF loads the model per batch vs once with Iterator
D["ch12-pandas-iterator"] = dict(items=[
    T("Обычная pandas UDF: модель грузится на каждый batch", 0, -50, 20, "#e03131"),
    N("b1", "batch 1", 0, 0, "db", 200, 80),
    N("b2", "batch 2", 0, 130, "db", 200, 80),
    N("b3", "batch 3", 0, 260, "db", 200, 80),
    N("m1", "загрузка модели\n+ predict", 300, 0, "r", 280, 80),
    N("m2", "загрузка модели\n+ predict", 300, 130, "r", 280, 80),
    N("m3", "загрузка модели\n+ predict", 300, 260, "r", 280, 80),
    T("UDF с Iterator: модель грузится один раз", 800, -50, 20, "#2f9e44"),
    N("c1", "batch 1", 800, 0, "db", 200, 80),
    N("c2", "batch 2", 800, 130, "db", 200, 80),
    N("c3", "batch 3", 800, 260, "db", 200, 80),
    N("m", "загрузка модели\nодин раз,\nцикл for по batch:\npredict", 1100, 90, "g", 300, 170),
], edges=[E("b1", "m1"), E("b2", "m2"), E("b3", "m3"),
          E("c1", "m"), E("c2", "m"), E("c3", "m")])

if __name__ == "__main__":
    run_all(D)
