#!/usr/bin/env python3
"""Chapter 7 (JupySQL) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main + Fig 7-1, 7-2: DataFrame path vs JupySQL path ----------
D["ch07-jupysql-flow"] = dict(items=[
    Z("Обычный путь: всё в память, потом график", 0, 0, 1520, 200),
    N("s1", "Сервер БД или CSV", 40, 70, "n", 280, 100),
    N("df", "pandas DataFrame\nвесь набор данных\nв памяти", 420, 70, "r", 300, 100),
    N("mp1", "matplotlib\nрисует график", 820, 70, "y", 280, 100),
    Z("С JupySQL: SQL считает итог в DuckDB", 0, 260, 1520, 200),
    N("s2", "Сервер БД или CSV\nили Parquet", 40, 330, "n", 280, 100),
    N("duck", "DuckDB\nSQL: фильтр и\nагрегация", 420, 330, "pu", 300, 100),
    N("small", "Маленькая\nтаблица итогов", 820, 330, "g", 280, 100),
    N("mp2", "%sqlplot\nграфик", 1200, 330, "y", 240, 100),
    T("Большой набор не попадает\nв память ноутбука.", 1150, 70, 20, "#e03131"),
], edges=[E("s1", "df", "всё"), E("df", "mp1"),
          E("s2", "duck", "SQL"), E("duck", "small"), E("small", "mp2")])

# ---------- own: magic commands map ----------
D["ch07-magics"] = dict(items=[
    T("Команды JupySQL в ноутбуке", 0, -60, 24, "#1971c2"),
    N("ext", "%load_ext sql\n%sql duckdb://\n(подключение)", 0, 0, "n", 280, 110),
    N("l", "%sql\nодна строка SQL", 400, -140, "p", 280, 100),
    N("c", "%%sql\nмногострочный SQL\n(--save имя)", 400, 0, "p", 280, 110),
    N("cmd", "%sqlcmd\ntables, columns,\nprofile", 400, 150, "db", 280, 110),
    N("res", "ResultSet\n.DataFrame()", 840, -140, "g", 260, 100),
    N("snip", "Snippet\n(живёт в ноутбуке,\nне в файле базы)", 840, 0, "y", 260, 110),
    N("plot", "%sqlplot\nhistogram, boxplot,\npie, bar", 1220, 0, "pu", 260, 110),
], edges=[E("ext", "l"), E("ext", "c"), E("ext", "cmd"), E("l", "res"), E("c", "snip"), E("snip", "plot")])

# ---------- Fig 7-12 .. 7-26: which plot for which question ----------
D["ch07-plots"] = dict(items=[
    T("%sqlplot: какой график для какого вопроса", 0, -60, 24, "#1971c2"),
    N("h", "histogram\nкак распределено число\n(--bins, --binwidth)", 0, 0, "p", 300, 120),
    N("b", "boxplot\nмедиана, квартили,\nвыбросы (--orient h)", 380, 0, "pu", 300, 120),
    N("p", "pie\nдоли целого,\nмало категорий (топ-5)", 760, 0, "y", 300, 120),
    N("bar", "bar\nсравнить категории\n(--show-numbers)", 1140, 0, "g", 300, 120),
    T("Всегда: SQL сначала сжимает данные до малой таблицы, потом график.", 0, 190, 20, GRAY),
    T("Результат команды: объект осей matplotlib, его можно менять (цвет, заголовок).", 0, 225, 20, GRAY),
], edges=[])

# ---------- Fig 7-27..7-33: three ways to keep the DB password ----------
D["ch07-connect-ways"] = dict(items=[
    T("Подключение к MySQL: три способа хранить доступ", 0, -60, 24, "#1971c2"),
    N("env", "Переменная\nDATABASE_URL\nпароль через getpass()", 0, 0, "y", 330, 120),
    N("ini", "Файл connections.ini\nсекции [mysqldb]\n--section имя", 0, 180, "r", 330, 120),
    N("key", "keyring\nпароль в хранилище ОС", 0, 360, "g", 330, 120),
    N("m1", "Безопасно, но пароль\nвводят при каждом запуске", 480, 0, "n", 380, 120),
    N("m2", "Пароль лежит в файле\nоткрытым текстом", 480, 180, "n", 380, 120),
    N("m3", "Безопаснее всех.\nРекомендация автора", 480, 360, "n", 380, 120),
    N("conn", "%sql ... \n%sql --connections", 1000, 180, "pu", 300, 120),
], edges=[E("env", "m1"), E("ini", "m2"), E("key", "m3"), E("m1", "conn"), E("m2", "conn"), E("m3", "conn")])

if __name__ == "__main__":
    run_all(D)
