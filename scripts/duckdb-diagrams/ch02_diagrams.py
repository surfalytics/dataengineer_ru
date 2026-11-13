#!/usr/bin/env python3
"""Chapter 2 (Importing Data into DuckDB) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)
Размеры файлов взяты из нашего запуска ch02_parquet_excel.py (см. figures-ch02.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: sources -> DuckDB ----------
D["ch02-import-sources"] = dict(items=[
    N("csv", "CSV\nread_csv_auto, COPY", 0, 0, "n", 300, 90),
    N("pq", "Parquet\nread_parquet, COPY", 0, 130, "n", 300, 90),
    N("xl", "Excel\nst_read (spatial)\nили read_xlsx", 0, 260, "n", 300, 110),
    N("my", "MySQL\nATTACH (расширение)\nили Python-цикл", 0, 410, "n", 300, 110),
    N("duck", "DuckDB\nтаблица в памяти\nили в файле .duckdb", 520, 150, "pu", 320, 150),
    N("out", "Экспорт:\nCOPY ... TO\nCSV, Parquet, xlsx", 1060, 150, "g", 300, 150),
    T("Каждый источник читается одной функцией или командой.", 0, 570, 20, GRAY),
], edges=[E("csv", "duck"), E("pq", "duck"), E("xl", "duck"), E("my", "duck"), E("duck", "out")])

# ---------- CSV: three ways ----------
D["ch02-csv-ways"] = dict(items=[
    Z("Три способа загрузить CSV", 0, 0, 1500, 480),
    N("f", "файл.csv", 30, 190, "n", 200, 90),
    N("a", "1. CREATE TABLE AS\nSELECT * FROM\nread_csv_auto(...)\nтипы угадываются", 330, 40, "p", 340, 120),
    N("b", "2. CREATE TABLE со схемой\n+ COPY ... FROM\nтипы заданы вами,\nлучше для больших файлов", 330, 190, "g", 340, 130),
    N("c", "3. register(df)\nDataFrame виден в SQL\nкак виртуальная\nтаблица, без копии", 330, 350, "pu", 340, 120),
    N("ta", "таблица\nв DuckDB", 820, 55, "db", 220, 90),
    N("tb", "таблица\nв DuckDB", 820, 210, "db", 220, 90),
    N("tc", "view над\nDataFrame", 820, 365, "y", 220, 90),
    T("Быстрая разведка", 1090, 80, 20, GRAY),
    T("Пайплайн: ошибка типа видна сразу", 1090, 235, 20, GRAY),
    T("Временный доступ,\nбез копии данных", 1090, 385, 20, GRAY),
], edges=[E("f", "a"), E("f", "b"), E("f", "c"), E("a", "ta"), E("b", "tb"), E("c", "tc")])

# ---------- CSV vs Parquet ----------
D["ch02-csv-vs-parquet"] = dict(items=[
    Z("CSV: строки подряд", 0, 0, 640, 360),
    Z("Parquet: столбец к столбцу + схема внутри", 720, 0, 780, 360),
    N("r1", "1, SU, 5, route 1", 40, 60, "y", 560, 54),
    N("r2", "2, S7, -3, route 2", 40, 130, "y", 560, 54),
    N("r3", "3, DP, 12, route 3", 40, 200, "y", 560, 54),
    T("Читаем все поля, даже если нужен один столбец.", 40, 280, 19, "#e03131"),
    N("p0", "flight_id\n1\n2\n3", 750, 60, "g", 170, 150),
    N("p1", "carrier\nSU\nS7\nDP", 940, 60, "g", 170, 150),
    N("p2", "arr_delay\n5\n-3\n12", 1130, 60, "g", 170, 150),
    N("p3", "route\n...", 1320, 60, "g", 150, 150),
    T("Читаем только нужные столбцы. Каждый столбец сжимается отдельно.", 750, 250, 19, "#2f9e44"),
    T("Наш замер, 1 млн строк, 4 столбца:   CSV 21,7 МБ    Parquet 5,0 МБ", 0, 400, 22, "#1971c2"),
], edges=[])

# ---------- MySQL: two ways ----------
D["ch02-mysql-ways"] = dict(items=[
    Z("Путь 1: вручную (Python)", 0, 0, 1500, 250),
    N("m1", "MySQL\nSELECT *", 40, 70, "n", 230, 100),
    N("cur", "mysql-connector\nкурсор, fetchall", 360, 70, "p", 270, 100),
    N("ins", "INSERT каждой\nстроки в DuckDB", 720, 70, "r", 270, 100),
    N("d1", "таблица\nDuckDB", 1090, 70, "db", 230, 100),
    Z("Путь 2: расширение mysql", 0, 300, 1500, 210),
    N("m2", "MySQL", 40, 370, "n", 230, 100),
    N("att", "ATTACH '...' AS mysqldb\n(TYPE MYSQL)", 360, 370, "pu", 330, 100),
    N("d2", "таблицы MySQL видны\nв DuckDB, USE mysqldb", 790, 370, "g", 330, 100),
    T("Больше контроля,\nно медленно на больших данных", 1100, 190, 18, GRAY),
    T("Проще и быстрее.\nВыбор автора\nдля частой работы.", 1160, 385, 18, "#2f9e44"),
], edges=[E("m1", "cur"), E("cur", "ins"), E("ins", "d1"), E("m2", "att"), E("att", "d2")])

if __name__ == "__main__":
    run_all(D)
