#!/usr/bin/env python3
"""Chapter 1 (Getting Started with DuckDB) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)
Числа скорости и памяти взяты из текста книги (см. figures-ch01.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: chapter map ----------
D["ch01-chapter-map"] = dict(items=[
    T("Глава 1: от идеи DuckDB до первых запросов", 0, -60, 24, "#1971c2"),
    N("why", "Зачем DuckDB\nSQL над файлами\nи DataFrame", 0, 0, "p", 280, 120),
    N("fast", "Почему быстрый\n6 приёмов:\nколонки, векторы...", 380, 0, "pu", 280, 120),
    N("use", "Удобство:\nязыки, SQL,\nopen source", 760, 0, "pu", 280, 120),
    N("start", "Быстрый старт:\nconnect, таблица,\nJOIN", 1140, 0, "g", 280, 120),
    N("pd", "pandas DataFrame\nчитается по имени\nв SQL", 1140, 230, "g", 280, 120),
    N("perf", "Опыт автора:\nCSV 5,8 млн строк,\nвремя и память", 760, 230, "y", 280, 120),
    N("sum", "Итог:\nбыстро, просто,\nна одной машине", 380, 230, "q", 280, 120),
    N("next", "Дальше: глава 2,\nимпорт CSV, Parquet,\nExcel, MySQL", 0, 230, "n", 280, 120),
], edges=[E("why", "fast"), E("fast", "use"), E("use", "start"), E("start", "pd"),
          E("pd", "perf"), E("perf", "sum"), E("sum", "next")])

# ---------- Fig 1-1, 1-2: traditional path vs DuckDB ----------
D["ch01-traditional-vs-duckdb"] = dict(items=[
    Z("Обычный путь: сначала загрузить в сервер БД", 0, 0, 1520, 200),
    N("f1", "CSV, Excel, JSON,\nParquet, базы", 40, 70, "n", 280, 100),
    N("srv", "Сервер БД\nзагрузка данных\nв таблицы", 420, 70, "db", 280, 100),
    N("q1", "SQL-запрос из\nприложения (Python)", 800, 70, "p", 280, 100),
    N("df1", "pandas DataFrame\nв памяти", 1180, 70, "g", 280, 100),
    Z("С DuckDB: SQL прямо над файлом", 0, 260, 1520, 200),
    N("f2", "CSV, Excel, JSON,\nParquet, базы", 40, 330, "n", 280, 100),
    N("duck", "DuckDB внутри\nвашей программы\n(без сервера)", 420, 330, "pu", 280, 100),
    N("df2", "Результат\n(DataFrame, таблица)", 800, 330, "g", 280, 100),
    T("Нет шага загрузки.\nНет отдельного сервера.", 1130, 350, 22, "#2f9e44"),
], edges=[E("f1", "srv", "load"), E("srv", "q1", "SQL"), E("q1", "df1"),
          E("f2", "duck", "SQL"), E("duck", "df2")])

# ---------- Fig 1-3: DuckDB on a DataFrame ----------
D["ch01-dataframe-flow"] = dict(items=[
    N("pdf", "pandas DataFrame\nemployees, sales\n(уже в памяти Python)", 0, 0, "n", 310, 120),
    N("sql", "SQL в DuckDB\nFROM employees e\nJOIN sales s ...", 440, 0, "pu", 310, 120),
    N("res", "Результат запроса\n.df() даёт новый\nDataFrame", 880, 0, "g", 310, 120),
    T("DuckDB находит DataFrame по имени переменной. Данные не копируются в таблицу.", 0, 170, 20, GRAY),
    T("Результат можно сразу отдать в pandas, график или следующий запрос.", 0, 205, 20, GRAY),
], edges=[E("pdf", "sql", "по имени"), E("sql", "res")])

# ---------- own: row store vs column store ----------
rows = [("1  Alice  30  HR"), ("2  Bob  35  Engineering"), ("3  Charlie  28  Marketing"), ("4  David  40  Engineering")]
items = [Z("Хранение по строкам (row store)", 0, 0, 600, 480),
         Z("Хранение по столбцам (columnar)", 680, 0, 760, 480)]
for i, r in enumerate(rows):
    items.append(N(f"r{i}", r, 40, 70 + i * 80, "y", 520, 66))
cols = [("id", "1\n2\n3\n4", "n"), ("name", "Alice\nBob\nCharlie\nDavid", "n"),
        ("age", "30\n35\n28\n40", "g"), ("department", "HR\nEngineering\nMarketing\nEngineering", "n")]
widths = [110, 160, 110, 220]
x = 710
for i, ((h, v, k), w) in enumerate(zip(cols, widths)):
    items.append(N(f"c{i}", f"{h}\n{v}", x, 70, k, w, 230))
    x += w + 15
items += [
    T("Запрос AVG(age): читаем ВСЕ поля\nвсех строк, хотя нужен один столбец.", 30, 400, 20, "#e03131"),
    T("Запрос AVG(age): читаем один столбец age.\nОстальные столбцы не трогаем.", 710, 400, 20, "#2f9e44"),
]
D["ch01-row-vs-column"] = dict(items=items, edges=[])

# ---------- own: what happens inside a query ----------
D["ch01-query-pipeline"] = dict(items=[
    T("Путь запроса внутри DuckDB", 0, -190, 24, "#1971c2"),
    N("sql", "SQL-запрос", 0, 0, "p", 230, 120),
    N("plan", "Планировщик\nфильтры ближе к\nданным, порядок JOIN", 300, 0, "pu", 300, 120),
    N("scan", "Чтение только\nнужных столбцов\nпорциями (векторы)", 670, 0, "db", 300, 120),
    N("c1", "Ядро CPU 1", 1050, -140, "g", 220, 80),
    N("c2", "Ядро CPU 2", 1050, 20, "g", 220, 80),
    N("c3", "Ядро CPU 3", 1050, 180, "g", 220, 80),
    N("out", "Итог:\nсклеить части,\nсобрать нужные\nстроки в конце", 1350, -10, "y", 260, 140),
    T("Late materialization: полные строки собираются как можно позже.", 0, 300, 20, GRAY),
    T("Каждое ядро берёт свою часть данных. Так работает parallel execution.", 0, 335, 20, GRAY),
], edges=[E("sql", "plan"), E("plan", "scan"), E("scan", "c1"), E("scan", "c2"), E("scan", "c3"),
          E("c1", "out"), E("c2", "out"), E("c3", "out")])

# ---------- own: where DuckDB sits ----------
D["ch01-where-duckdb"] = dict(items=[
    N("sqlite", "SQLite\nвстроенная база\nстроки, транзакции\n(OLTP)", 0, 0, "n", 330, 150),
    N("duck", "DuckDB\nвстроенная база\nколонки, аналитика\n(OLAP)", 430, 0, "g", 330, 150),
    N("spark", "Spark, Flink\nкластер из узлов\nпараллелизм по\nмногим машинам", 860, 0, "p", 330, 150),
    T("Есть в приложении,\nсервер не нужен", 20, 190, 20, GRAY),
    T("Есть в приложении,\nсервер не нужен", 450, 190, 20, GRAY),
    T("Нужен кластер,\nбольшая инфраструктура", 880, 190, 20, GRAY),
    T("DuckDB: простота SQLite + скорость аналитической базы, на одной машине.", 0, 280, 22, "#2f9e44"),
], edges=[])

# ---------- Fig: speed and memory (numbers from the book) ----------
items = [T("Время: загрузить CSV 5,8 млн строк и посчитать среднюю задержку", 0, -50, 22, "#1971c2")]
def bar(prefix, y, label, v, scale, k, txt):
    return [T(label, 0, y + 12, 20, GRAY), N(prefix, "", 150, y, k, v * scale, 50),
            T(txt, 150 + v * scale + 12, y + 12, 20, GRAY)]
items += bar("t0", 0, "pandas", 7.5, 80, "r", "около 7,5 с")
items += bar("t1", 70, "DuckDB", 0.5, 80, "g", "около 0,5 с")
items.append(T("Память: сколько занимает процесс после запроса", 0, 190, 22, "#1971c2"))
items += bar("m0", 240, "pandas", 4200, 0.14, "r", "около 4,2 ГБ")
items += bar("m1", 310, "DuckDB", 280, 0.14, "g", "около 280 МБ")
items.append(T("Это числа автора. Ваши цифры зависят от машины и версий.", 0, 400, 18))
D["ch01-speed-memory"] = dict(items=items, edges=[])

# ---------- own: history ----------
D["ch01-timeline"] = dict(items=[
    N("y18", "2018\nидея DuckDB:\nOLAP-база,\nпростая как SQLite", 0, 0, "p", 290, 140),
    N("y19", "2019\nпервый стабильный\nрелиз", 380, 0, "p", 290, 140),
    N("y21", "2021\nDuckDB Labs:\nподдержка и\nразвитие", 760, 0, "pu", 290, 140),
    N("md", "MotherDuck\nDuckDB как сервис\nв облаке\n(глава 9)", 1140, 0, "g", 290, 140),
], edges=[E("y18", "y19"), E("y19", "y21"), E("y21", "md")])

if __name__ == "__main__":
    run_all(D)
