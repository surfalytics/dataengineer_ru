#!/usr/bin/env python3
"""Chapter 3 (A Primer on SQL) diagrams. Usage: ch03_diagrams.py [name ...]  (no args = all)
ER-схема магазина: Mermaid, см. scripts/duckdb-diagrams/src/ch03-shop-er.mmd и build-ch03-er.sh."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: CLI map (book text, Figure 3-2 idea) ----------
D["ch03-cli-map"] = dict(items=[
    Z("Откуда начинаем", 0, 0, 640, 330),
    N("mem", "duckdb\nбаза в памяти\n(пропадёт при выходе)", 340, 70, "n", 260, 110),
    N("file", "duckdb mydb.duckdb\nбаза в файле\n(живёт между сессиями)", 40, 70, "db", 260, 110),
    N("open", ".open file.duckdb\nзакрыть текущую\nи открыть другую", 340, 210, "p", 260, 90),
    N("att", "ATTACH + USE\nподключить вторую базу,\nне закрывая первую", 40, 210, "p", 260, 90),
    N("exp", "EXPORT DATABASE 'dir'", 780, 70, "pu", 300, 90),
    N("dir", "Папка dir:\nschema.sql  load.sql\nкаждая таблица в .csv", 780, 210, "y", 300, 110),
    N("imp", "IMPORT DATABASE 'dir'\nв новой базе", 1220, 210, "g", 300, 110),
], edges=[E("mem", "open"), E("file", "att"), E("mem", "exp"), E("exp", "dir"), E("dir", "imp")])

# ---------- Fig 3-4..3-7 idea: join types ----------
def box(k, title, body, x, kind):
    return N(k, f"{title}\n{body}", x, 120, kind, 280, 200)

D["ch03-joins"] = dict(items=[
    T("Слева таблица L с ключами 1, 2, 3. Справа таблица R с ключами 2, 3, 4.", 0, 0, 22, "#1971c2"),
    T("Совпадают ключи 2 и 3. Ключ 1 есть только слева, ключ 4 только справа.", 0, 40, 20, GRAY),
    box("inner", "INNER JOIN", "\n2\n3\n\nтолько пары", 0, "g"),
    box("left", "LEFT JOIN", "1 (справа NULL)\n2\n3\n\nвсе из L", 320, "p"),
    box("right", "RIGHT JOIN", "2\n3\n4 (слева NULL)\n\nвсе из R", 640, "pu"),
    box("full", "FULL JOIN", "1 (справа NULL)\n2\n3\n4 (слева NULL)\nвсе из обеих", 960, "y"),
    box("cross", "CROSS JOIN", "\nвсе пары:\n3 x 3 = 9 строк\n\nбез условия", 1280, "r"),
], edges=[])

# ---------- Fig 3-8: nested query ----------
D["ch03-nested-query"] = dict(items=[
    N("s1", "1. Самый внутренний\nSELECT count(*) ...\nGROUP BY product_id\nчисло заказов\nна каждый товар", 0, 0, "p", 300, 150),
    N("s2", "2. Средний\nSELECT max(cnt)\nнаибольшее число\nзаказов у одного\nтовара", 400, 0, "pu", 300, 150),
    N("s3", "3. HAVING / WHERE ... IN\nоставить товары,\nу которых число\nзаказов = максимум\n(их может быть\nнесколько)", 800, 0, "y", 300, 150),
    N("s4", "4. Внешний SELECT\nJOIN с products:\nназвание и число\nзаказов", 1200, 0, "g", 300, 150),
    T("Читаем изнутри наружу. Результат каждого уровня идёт на уровень выше.", 0, 210, 20, GRAY),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4")])

if __name__ == "__main__":
    run_all(D)
