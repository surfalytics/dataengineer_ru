#!/usr/bin/env python3
"""Chapter 13 (working with CEO, peers, engineering) diagrams. Usage: ch13_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: three kinds of relationship (main diagram)
D["ch13-supported-tolerated-resented"] = dict(items=[
    N("res", "Resented\nмешаете им работать", 0, 0, "r", 330, 100),
    N("tol", "Tolerated\nим всё равно", 420, 0, "y", 330, 100),
    N("sup", "Supported\nпомогают сами", 840, 0, "g", 330, 100),
    N("er", "Просьбы считают помехой.\nТикеты миграции лежат,\nпока вы громко не\nпоставите эскалацию", 0, 200, "n", 330, 140),
    N("et", "Тикеты берут в спринт,\nно слабые места\nвашего плана\nникто не показывает", 420, 200, "n", 330, 140),
    N("es", "Приходят с конкретными\nрисками и идеями,\nкак поправить\nваш план", 840, 200, "n", 330, 140),
    T("Цель: двигаться вправо, от Resented к Supported", 0, -60, 22, "#1971c2"),
], edges=[E("res", "er"), E("tol", "et"), E("sup", "es"),
          E("res", "tol", dashed=True), E("tol", "sup", dashed=True)])

# own: bridging narratives
D["ch13-bridging-narratives"] = dict(items=[
    N("ceo", "CEO: инженерия\nработает слабо", 0, 0, "p", 360, 100),
    N("brd", "Board и коллеги:\nсрываются сроки", 0, 140, "p", 360, 100),
    N("eng", "Инженеры: CEO часто\nменяет направление", 0, 280, "p", 360, 100),
    N("oth", "Продукт, дизайн, продажи:\nкаждый винит соседа", 0, 420, "p", 360, 100),
    N("dbg", "Разбор расхождений:\nслушаем всех, пока\nне ищем виноватого", 560, 190, "y", 330, 140),
    N("one", "Единая картина:\nсоставные части\nпроблемы и решение", 1090, 190, "g", 330, 140),
], edges=[E("ceo", "dbg"), E("brd", "dbg"), E("eng", "dbg"), E("oth", "dbg"), E("dbg", "one")])

# own: LinkedIn structured escalation
D["ch13-structured-escalation"] = dict(items=[
    N("s1", "1. Договорились:\nрешим спор\nза 5 дней", 0, 0, "p", 270, 120),
    N("s2", "2. Встреча:\nпонять позиции\nи найти путь вместе", 430, 0, "p", 270, 120),
    N("s3", "3. Чистая эскалация:\nидём вместе,\nодин общий документ", 860, 0, "y", 270, 120),
    N("s4", "4. Выполняем решение\nтого, к кому пришли", 1290, 0, "g", 270, 120),
    N("ok", "Спор решён\nбез эскалации", 430, 250, "g", 270, 100),
], edges=[E("s1", "s2"), E("s2", "s3", "не вышло"), E("s3", "s4"), E("s2", "ok", "вышло")])

if __name__ == "__main__":
    run_all(D)
