#!/usr/bin/env python3
"""Chapter 3 (SQL for Analytics) diagrams. Usage: ch03_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main, Fig 3-5: SQL languages and their commands
D["ch03-sql-languages"] = dict(items=[
    N("sql", "SQL: как мы говорим с СУБД", 380, 0, "n", 420, 80),
    N("ddl", "DDL\nструктура: таблицы,\nview, индексы", 0, 190, "p", 260, 110),
    N("dml", "DML\nсами данные:\nчитать и менять", 310, 190, "p", 260, 110),
    N("dcl", "DCL\nправа доступа", 620, 190, "n", 260, 110),
    N("tcl", "TCL\nтранзакции", 930, 190, "n", 260, 110),
    N("ddl2", "CREATE, ALTER,\nDROP, RENAME,\nTRUNCATE", 0, 380, "p", 260, 110),
    N("dml2", "SELECT, INSERT,\nUPDATE, DELETE", 310, 380, "p", 260, 110),
    N("dcl2", "GRANT, REVOKE", 620, 380, "n", 260, 110),
    N("tcl2", "COMMIT, ROLLBACK,\nSAVEPOINT", 930, 380, "n", 260, 110),
    N("who", "Аналитик данных: в основном SELECT.  analytics engineer: DML и часть DDL, которую прячет dbt.\nДата-инженер: DDL и DML целиком.  DCL и TCL — задачи администратора, в главе их нет.",
      0, 560, "y", 1190, 90),
], edges=[E("sql", "ddl"), E("sql", "dml"), E("sql", "dcl"), E("sql", "tcl"),
          E("ddl", "ddl2"), E("dml", "dml2"), E("dcl", "dcl2"), E("tcl", "tcl2")])

# Fig 3-1: DIKW pyramid with our examples
D["ch03-dikw"] = dict(items=[
    N("w", "Мудрость\n(wisdom)", 170, 0, "g", 260, 90),
    N("k", "Знание\n(knowledge)", 120, 190, "pu", 360, 90),
    N("i", "Информация\n(information)", 70, 380, "p", 460, 90),
    N("d", "Данные\n(data)", 20, 570, "n", 560, 90),
    N("we", "«Учителю пора думать\nо пенсионных накоплениях»", 720, 0, "g", 440, 90),
    N("ke", "«Учитель родился в 1989 году,\nзначит, он взрослый»", 720, 190, "pu", 440, 90),
    N("ie", "«Мой учитель математики\nродился в 1989 году»", 720, 380, "p", 440, 90),
    N("de", "«1989», «учитель»,\n«зелёный»", 720, 570, "n", 440, 90),
    T("Базы данных хранят нижний уровень и помогают подняться выше", 20, 700, 20, "#495057"),
], edges=[E("d", "i", "контекст"), E("i", "k", "опыт"), E("k", "w", "суждение"),
          E("w", "we", dashed=True), E("k", "ke", dashed=True), E("i", "ie", dashed=True), E("d", "de", dashed=True)])

# Figs 3-6, 3-8, 3-10, 3-12, 3-13: which rows each join returns (A = authors, B = books)
rows = [("INNER JOIN", "g0"), ("LEFT JOIN", "g1"), ("RIGHT JOIN", "g2"), ("FULL JOIN", "g3")]
cells = {"INNER JOIN": ("n", "g", "n"), "LEFT JOIN": ("g", "g", "n"),
         "RIGHT JOIN": ("n", "g", "g"), "FULL JOIN": ("g", "g", "g")}
txt = {("g", 0): "да, поля B = NULL", ("g", 1): "да", ("g", 2): "да, поля A = NULL"}
items = [T("Строки A без пары", 285, -45, 20, "#495057"), T("Строки с парой", 535, -45, 20, "#495057"),
         T("Строки B без пары", 765, -45, 20, "#495057")]
for r, (name, _) in enumerate(rows):
    y = r * 95
    items.append(N(f"j{r}", name, 0, y, "p", 230, 75))
    for c, k in enumerate(cells[name]):
        items.append(N(f"c{r}{c}", txt.get((k, c), "нет"), 260 + c * 240, y, k, 220, 75))
items += [N("cj", "CROSS JOIN", 0, 400, "p", 230, 75),
          N("cx", "каждая строка A с каждой строкой B: 6 × 5 = 30 строк", 260, 400, "y", 700, 75),
          T("A = authors (6 авторов), B = books (5 книг). Автор без книг виден только в LEFT и FULL JOIN", 0, 505, 20, "#495057")]
D["ch03-joins"] = dict(items=items, edges=[])

# own: GROUP BY collapses rows, a window function keeps them
D["ch03-groupby-vs-window"] = dict(items=[
    N("src", "sales: customer_id | amount\n101 | 30\n101 | 55\n103 | 30\n103 | 55", 330, 0, "db", 360, 170),
    N("gb", "SUM(amount) ... GROUP BY customer_id\n\n101 | 85\n103 | 85\n\n2 строки: детали продаж пропали", 0, 330, "p", 450, 220),
    N("wf", "SUM(amount) OVER\n(PARTITION BY customer_id)\n101 | 30 | 85\n101 | 55 | 85\n103 | 30 | 85\n103 | 55 | 85\n4 строки: каждая на месте", 570, 330, "g", 450, 250),
], edges=[E("src", "gb"), E("src", "wf")])

if __name__ == "__main__":
    run_all(D)
