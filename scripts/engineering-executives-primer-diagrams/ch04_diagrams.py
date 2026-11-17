#!/usr/bin/env python3
"""Chapter 4 (How to Plan) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Chapter map: three phases in sequence, each one feeds the next
D["ch04-three-phases"] = dict(items=[
    N("p1", "Фаза 1\nФинансовый план\nна год", 0, 0, "p", 320, 130),
    N("p2", "Фаза 2\nFunctional portfolio\nallocation", 480, 0, "g", 320, 130),
    N("p3", "Фаза 3\nRoadmap на квартал\nили полугодие", 960, 0, "y", 320, 130),
    N("r1", "P&L, бюджет,\nheadcount plan", 0, 260, "n", 320, 110),
    N("r2", "Проценты ресурсов\nпо месяцам: запросы\nи внутренние приоритеты", 480, 260, "n", 320, 110),
    N("r3", "Согласие функций:\nчто и когда делаем", 960, 260, "n", 320, 110),
    T("Новое знание в поздней фазе может вернуть к ранней. Это нормально.", 0, 410, 20, "#495057"),
], edges=[E("p1", "p2", "вход"), E("p2", "p3", "вход"), E("p1", "r1"), E("p2", "r2"), E("p3", "r3")])

# Fig 4-2 (own numbers): functional allocation by quarter, stacked bars
SC = 4.5
rows = [("x", "Кросс-функциональные проекты", "p", [70, 55, 50, 60]),
        ("t", "Продуктовая инженерия помогает", "y", [0, 10, 10, 0]),
        ("d", "Продуктивность разработчиков", "g", [10, 15, 20, 20]),
        ("i", "Инфраструктура", "n", [20, 20, 20, 20])]
items = []
for c, q in enumerate(["Q1", "Q2", "Q3", "Q4"]):
    x = c * 420
    items.append(T(q, x + 150, -10, 24, "#495057"))
    y = 40
    for key, name, k, vals in rows:
        v = vals[c]
        if v:
            h = max(int(v * SC), 44)
            lbl = f"{name} {v}%" if len(name) < 30 else f"{name}\n{v}%"
            items.append(N(f"{key}{c}", lbl, x, y, k, 400, h if "\n" not in lbl else max(h, 64)))
            y += h if "\n" not in lbl else max(h, 64)
D["ch04-allocation"] = dict(items=items, edges=[])

# Fig 4-3 (own version): planning calendar
cols = ["Конец прошлого года", "Q1", "Q2", "Q3", "Q4"]
cx = [270, 510, 750, 990, 1230]
it = []
for c, x in zip(cols, cx):
    it.append(T(c, x, 0, 18, "#495057"))
it += [
    N("l1", "Фаза 1\nФинансовый план", 0, 40, "p", 240, 100),
    N("l2", "Фаза 2\nFunctional portfolio\nallocation", 0, 180, "g", 240, 110),
    N("l3", "Фаза 3\nRoadmap", 0, 330, "y", 240, 100),
    N("b1", "Бюджет и\nheadcount plan", 270, 40, "p", 220, 100),
    N("b2", "Непрерывно, весь год: обновляем список вложений\nи целевое распределение", 270, 180, "g", 1180, 110),
]
for i, (q, x) in enumerate(zip(["Q1", "Q2", "Q3", "Q4"], cx[:4])):
    it.append(N(f"q{i}", f"Roadmap на {q}\nза несколько недель\nдо начала", x, 330, "y", 220, 110))
D["ch04-timeline"] = dict(items=it, edges=[])

if __name__ == "__main__":
    run_all(D)
