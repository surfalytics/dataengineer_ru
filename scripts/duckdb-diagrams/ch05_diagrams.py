#!/usr/bin/env python3
"""Chapter 5 (Performing EDA with DuckDB) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)
Числа взяты из текста книги (см. figures-ch05.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: EDA flow ----------
D["ch05-eda-flow"] = dict(items=[
    T("Глава 5: EDA на одном датасете, рейсы США 2015", 0, -60, 24, "#1971c2"),
    N("csv", "3 CSV:\nairlines, airports,\nflights", 0, 0, "n", 260, 120),
    N("db", "Таблицы DuckDB\nread_csv_auto()", 340, 0, "db", 260, 120),
    N("geo", "Геоанализ\nspatial: Point,\nST_DWithin, ST_Distance", 700, -110, "pu", 300, 120),
    N("desc", "Описательная\nаналитика: GROUP BY,\nдоли, CTE, CASE", 700, 110, "p", 300, 120),
    N("py", "Python:\nfolium, matplotlib,\n.df(), pivot()", 1100, 0, "g", 260, 120),
    T("SQL считает, Python только рисует карту и график.", 0, 200, 20, GRAY),
], edges=[E("csv", "db"), E("db", "geo"), E("db", "desc"), E("geo", "py"), E("desc", "py")])

# ---------- own: lat/lng to point and nearest ----------
D["ch05-nearest-airports"] = dict(items=[
    N("ll", "Столбцы\nlatitude, longitude", 0, 0, "n", 260, 110),
    N("pt", "ST_Point(lng, lat)\nсначала ДОЛГОТА,\nпотом широта", 360, 0, "y", 290, 110),
    N("dw", "ST_DWithin(a, b, 3)\nвсе точки в радиусе\n(фильтр WHERE)", 780, -90, "pu", 300, 110),
    N("di", "ST_Distance(a, b)\nрасстояние для каждой;\nORDER BY ... LIMIT 3", 780, 90, "pu", 300, 110),
    N("res", "Ближайшие\nаэропорты", 1180, 0, "g", 220, 110),
    T("Расстояние на плоскости считается в градусах, не в километрах.", 0, 230, 20, "#e03131"),
], edges=[E("ll", "pt"), E("pt", "dw"), E("pt", "di"), E("dw", "res"), E("di", "res")])

# ---------- own: count vs share ----------
items = [T("Задержанные рейсы: число и доля", 0, -50, 22, "#1971c2")]
def bar(prefix, y, label, v, scale, k, txt):
    return [T(label, 0, y + 12, 20, GRAY), N(prefix, "", 150, y, k, v * scale, 50),
            T(txt, 150 + v * scale + 12, y + 12, 20, GRAY)]
items.append(T("По числу лидирует большая компания A", 0, 0, 20, GRAY))
items += bar("a1", 40, "A", 879, 0.5, "r", "879 рейсов")
items += bar("b1", 110, "B", 721, 0.5, "y", "721")
items += bar("c1", 180, "C", 566, 0.5, "g", "566")
items.append(T("По доле лидирует маленькая компания C", 0, 270, 20, GRAY))
items += bar("a2", 310, "A", 30.5, 10, "g", "30,5%")
items += bar("b2", 380, "B", 39.5, 10, "y", "39,5%")
items += bar("c2", 450, "C", 49.8, 10, "r", "49,8%")
items.append(T("Наш пример из scripts/duckdb-code/ch05_flights_eda.py", 0, 540, 18))
D["ch05-count-vs-share"] = dict(items=items, edges=[])

# ---------- own: time slots ----------
D["ch05-timeslots"] = dict(items=[
    T("Задержки по слотам времени вылета (CASE WHEN по часу)", 0, -50, 22, "#1971c2"),
    N("s1", "00-06", 0, 0, "g", 240, 90), N("s2", "06-12", 300, 0, "g", 240, 90),
    N("s3", "12-18", 600, 0, "y", 240, 90), N("s4", "18-24", 900, 0, "r", 240, 90),
    T("AVG(arrival_delay) для каждого слота.\nВывод автора: вечерний слот самый плохой.", 0, 130, 20, GRAY),
    T("Слоты лучше брать по расписанию вылета, не по факту.", 0, 200, 18),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4")])

if __name__ == "__main__":
    run_all(D)
