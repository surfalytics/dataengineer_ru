#!/usr/bin/env python3
"""Chapter 4 (Using DuckDB with Polars) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: Polars + DuckDB ----------
D["ch04-polars-duckdb"] = dict(items=[
    N("pl", "Polars DataFrame\nпеременная cars\n(данные в Arrow)", 0, 0, "n", 300, 120),
    N("sql", "duckdb.sql(\n'SELECT ... FROM cars')\nDuckDB находит\nпеременную по имени", 430, 0, "pu", 340, 140),
    N("rel", "DuckDBPyRelation\nплан запроса:\nещё не выполнен", 900, 0, "db", 300, 120),
    N("outpl", ".pl()\nPolars DataFrame", 1330, -110, "g", 260, 90),
    N("outdf", ".df()\npandas DataFrame", 1330, 40, "g", 260, 90),
    N("meth", "Методы:\nfilter, join,\naggregate, limit", 900, 230, "y", 300, 110),
    T("Данные не копируются в базу: DuckDB читает DataFrame через Apache Arrow (нужен pyarrow).", 0, 220, 20, GRAY),
], edges=[E("pl", "sql", "по имени"), E("sql", "rel"), E("rel", "outpl"), E("rel", "outdf"), E("rel", "meth")])

# ---------- Fig 4-10, 4-11: optimized vs unoptimized plan ----------
D["ch04-lazy-plan"] = dict(items=[
    Z("Без оптимизации: сначала всё, потом фильтр", 0, 0, 1000, 260),
    N("a1", "Прочитать CSV:\nвсе 31 колонка,\nвсе 5,8 млн строк", 40, 90, "r", 270, 110),
    N("a2", "SELECT:\n3 колонки", 380, 90, "n", 230, 110),
    N("a3", "FILTER:\nmonth, origin,\ndestination", 680, 90, "n", 270, 110),
    Z("С оптимизацией: читаем мало и сразу фильтруем", 0, 330, 1000, 260),
    N("b1", "Чтение CSV:\nтолько 3 колонки\n(projection pushdown)", 40, 420, "g", 270, 110),
    N("b2", "Фильтр уже\nпри чтении\n(predicate pushdown)", 380, 420, "g", 270, 110),
    N("b3", "collect():\nготовый DataFrame", 700, 420, "y", 250, 110),
], edges=[E("a1", "a2"), E("a2", "a3"), E("b1", "b2"), E("b2", "b3")])

# ---------- own: three read modes ----------
D["ch04-lazy-modes"] = dict(items=[
    Z("Eager: read_csv()", 0, 0, 1500, 170),
    N("e1", "read_csv\nчитает весь файл", 40, 50, "r", 300, 90),
    N("e2", "DataFrame\nв памяти", 440, 50, "n", 260, 90),
    N("e3", "select, filter\nпо шагам", 800, 50, "n", 260, 90),
    Z("Implicit lazy: scan_csv()", 0, 230, 1500, 170),
    N("i1", "scan_csv\nничего не читает", 40, 280, "g", 300, 90),
    N("i2", "LazyFrame:\nплан запроса", 440, 280, "pu", 260, 90),
    N("i3", "select, filter\nдобавляют шаги", 800, 280, "n", 260, 90),
    N("i4", "collect()\nоптимизация и запуск", 1150, 280, "y", 300, 90),
    Z("Explicit lazy: read_csv().lazy()", 0, 460, 1500, 170),
    N("x1", "read_csv\nчитает весь файл", 40, 510, "r", 300, 90),
    N("x2", ".lazy()\nLazyFrame", 440, 510, "pu", 260, 90),
    N("x3", "select, filter\nоптимизируются", 800, 510, "n", 260, 90),
    N("x4", "collect()", 1150, 510, "y", 300, 90),
], edges=[E("e1", "e2"), E("e2", "e3"), E("i1", "i2"), E("i2", "i3"), E("i3", "i4"),
          E("x1", "x2"), E("x2", "x3"), E("x3", "x4")])

# ---------- own: relation methods vs SQL ----------
D["ch04-relation-sql"] = dict(items=[
    T("Метод DuckDBPyRelation", 0, -50, 22, "#1971c2"),
    T("Что это в SQL", 560, -50, 22, "#1971c2"),
    N("m1", "conn.table('t')", 0, 0, "pu", 440, 70),
    N("s1", "FROM t", 560, 0, "n", 440, 70),
    N("m2", ".join(other, condition=...)", 0, 100, "pu", 440, 70),
    N("s2", "JOIN ... ON", 560, 100, "n", 440, 70),
    N("m3", ".filter('customer_id = 1')", 0, 200, "pu", 440, 70),
    N("s3", "WHERE", 560, 200, "n", 440, 70),
    N("m4", ".aggregate('sum(qty)', 'customer_id')", 0, 300, "pu", 440, 70),
    N("s4", "GROUP BY", 560, 300, "n", 440, 70),
    N("m5", ".project('name, qty')", 0, 400, "pu", 440, 70),
    N("s5", "SELECT name, qty", 560, 400, "n", 440, 70),
    N("m6", ".limit(3, 2)", 0, 500, "pu", 440, 70),
    N("s6", "LIMIT 3 OFFSET 2", 560, 500, "n", 440, 70),
], edges=[E("m1", "s1"), E("m2", "s2"), E("m3", "s3"), E("m4", "s4"), E("m5", "s5"), E("m6", "s6")])

if __name__ == "__main__":
    run_all(D)
