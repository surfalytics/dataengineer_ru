#!/usr/bin/env python3
"""Chapter 3 (Structured APIs) diagrams. Usage: ch03_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own (main): RDD is opaque to Spark, DataFrame code shows the intent
D["ch03-opaque-vs-structured"] = dict(items=[
    T("RDD: мы говорим Spark, КАК считать", 0, -50, 22, "#e03131"),
    N("r1", "Код с lambda\nmap, reduceByKey", 0, 0, "r", 260, 100),
    N("r2", "Spark видит\nчёрный ящик", 360, 0, "n", 260, 100),
    N("r3", "Плана нет:\nоптимизировать нечего", 720, 0, "r", 280, 100),
    T("DataFrame: мы говорим Spark, ЧТО нужно", 0, 190, 22, "#2f9e44"),
    N("d1", "Операторы DSL\ngroupBy, agg, avg", 0, 240, "g", 260, 100),
    N("d2", "Spark видит\nнамерение", 360, 240, "p", 260, 100),
    N("d3", "Catalyst строит\nи улучшает план", 720, 240, "g", 280, 100),
    N("d4", "Компактный\nкод для JVM", 1100, 240, "g", 230, 100),
], edges=[E("r1", "r2"), E("r2", "r3"), E("d1", "d2"), E("d2", "d3"), E("d3", "d4")])

# Fig 3-1: Structured APIs in Spark 2.x
D["ch03-structured-apis"] = dict(items=[
    N("py", "Python, R\nтолько DataFrame", 0, 0, "y", 330, 100),
    N("sc", "Scala, Java\nDataset[T] и DataFrame", 480, 0, "y", 330, 100),
    N("df", "DataFrame\nDataset[Row]: строки без типа", 0, 220, "p", 330, 110),
    N("ds", "Dataset[T]\nобъекты со строгим типом", 480, 220, "pu", 330, 110),
    N("sql", "Spark SQL: Catalyst и Tungsten", 0, 440, "g", 810, 100),
    N("rdd", "RDD: низкий уровень, внутри всё сводится к нему", 0, 640, "n", 810, 100),
], edges=[E("py", "df"), E("sc", "df"), E("sc", "ds"), E("df", "sql"), E("ds", "sql"), E("sql", "rdd")])

# Fig 3-4: four phases of Catalyst
D["ch03-catalyst-phases"] = dict(items=[
    N("q", "Запрос:\nSQL или DataFrame", 0, 0, "n", 230, 110),
    N("a", "1. Analysis\nимена и типы через Catalog", 320, 0, "p", 270, 110),
    N("l", "2. Logical optimization\nправила и оценка стоимости", 680, 0, "g", 300, 110),
    N("p", "3. Physical planning\nвыбор физических операторов", 1070, 0, "y", 300, 110),
    N("c", "4. Code generation\nбайт-код для JVM (Tungsten)", 1070, 240, "q", 300, 110),
    N("x", "Выполнение\nна executors", 680, 240, "db", 300, 110),
    N("cat", "Catalog:\nтаблицы, колонки, типы, функции", 320, 240, "n", 270, 110),
], edges=[E("q", "a"), E("a", "l"), E("l", "p"), E("p", "c"), E("c", "x"), E("cat", "a")])

# Fig 3-5: predicate pushdown example
D["ch03-pushdown"] = dict(items=[
    T("До оптимизации: фильтр стоит после join", 0, -50, 22, "#e03131"),
    N("b1", "Scan users", 0, 0, "db", 200, 90),
    N("b2", "Scan events", 0, 130, "db", 200, 90),
    N("bj", "Join\nusers.id = events.uid", 330, 55, "r", 280, 110),
    N("bf", "Filter\ndate > 2015-01-01", 740, 55, "r", 260, 110),
    T("После Catalyst: фильтр сдвинут ниже, join получает меньше строк", 0, 290, 22, "#2f9e44"),
    N("a1", "Scan users", 0, 340, "db", 200, 90),
    N("a2", "Scan events", 0, 470, "db", 200, 90),
    N("af", "Filter\ndate > 2015-01-01", 330, 470, "g", 260, 90),
    N("aj", "Join\nusers.id = events.uid", 740, 395, "g", 280, 110),
], edges=[E("b1", "bj"), E("b2", "bj"), E("bj", "bf"),
          E("a1", "aj"), E("a2", "af"), E("af", "aj")])

if __name__ == "__main__":
    run_all(D)
