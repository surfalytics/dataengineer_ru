#!/usr/bin/env python3
"""Overview page (book map) diagram. Usage: ch00_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: book map - five parts and what each gives the reader
D["ch00-book-map"] = dict(items=[
    T("Карта книги: пять частей", 0, -50, 22, "#1971c2"),
    N("p1", "Часть I\nЧто такое стратегия\nглавы 1–4", 0, 0, "p", 280, 110),
    N("p2", "Часть II\nПять шагов стратегии\nглавы 5–12", 360, 0, "g", 280, 110),
    N("p3", "Часть III\nИнструменты уточнения\nглавы 13–15", 720, 0, "y", 280, 110),
    N("p4", "Часть IV\nРеальные стратегии\nглавы 16–22", 1080, 0, "q", 280, 110),
    N("p5", "Часть V\nЧто дальше\nглавы 23–24", 1440, 0, "p", 280, 110),
    N("d1", "Зачем писать стратегию,\nкто её делает\nи когда пора", 0, 200, "n", 280, 120),
    N("d2", "Исследование, диагноз,\nуточнение, политика,\noperations", 360, 200, "n", 280, 120),
    N("d3", "strategy testing,\nsystems modeling,\nWardley mapping", 720, 200, "n", 280, 120),
    N("d4", "Uber, Calm, Stripe\nи вымышленные\nкомпании", 1080, 200, "n", 280, 120),
    N("d5", "Как оценить стратегию\nи как расти\nв этом навыке", 1440, 200, "n", 280, 120),
], edges=[E("p1", "p2"), E("p2", "p3"), E("p3", "p4"), E("p4", "p5"),
          E("p1", "d1", dashed=True, head=False), E("p2", "d2", dashed=True, head=False),
          E("p3", "d3", dashed=True, head=False), E("p4", "d4", dashed=True, head=False),
          E("p5", "d5", dashed=True, head=False)])

if __name__ == "__main__":
    run_all(D)
