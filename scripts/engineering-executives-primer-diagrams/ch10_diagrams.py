#!/usr/bin/env python3
"""Chapter 10 (meetings) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from excb import N, E, Z, T, run_all

D = {}

# Table 10-1: monthly calendar, four weeks x four days
days = ["Пн", "Вт", "Ср", "Чт"]
tue = ["Engineering Q&A", "Встреча\nengineering manager", "Встреча\nStaff-инженеров", "Нет ежемесячной\nвстречи"]
items = [T(d, i * 300 + 110, -50, 24, "#495057") for i, d in enumerate(days)]
for w in range(4):
    y = w * 140
    items.append(T(f"Неделя {w+1}", -170, y + 40, 20, "#495057"))
    items += [N(f"m{w}", "Встреча\nкоманды", 0, y, "p", 260, 100),
              N(f"t{w}", tue[w], 300, y, ["y", "q", "pu", "n"][w], 260, 100),
              N(f"s{w}", "Spec review", 600, y, "g", 260, 100),
              N(f"i{w}", "Incident review", 900, y, "r", 260, 100)]
D["ch10-monthly-calendar"] = dict(items=items, edges=[])

# own: six meetings by purpose
cols = [
    ("Операционные\n(каждую неделю)", "Встреча команды\nруководителей\nSpec review\nIncident review", "Организация идёт\nв одном темпе\nи к общим целям", "p"),
    ("Развивающие\n(раз в месяц)", "Встреча engineering\nmanager\nВстреча\nStaff-инженеров", "Люди растут в своём\nремесле и верят,\nчто в них вкладываются", "y"),
    ("Обратная связь\n(раз в месяц)", "Engineering Q&A\nдля всей\nорганизации", "Вы слышите, что\nорганизация думает\nна самом деле", "g"),
]
items, edges = [], []
for i, (h, m, g, k) in enumerate(cols):
    x = i * 420
    items += [N(f"h{i}", h, x, 0, k, 360, 100), N(f"m{i}", m, x, 190, "n", 360, 150), N(f"g{i}", g, x, 430, k, 360, 120)]
    edges += [E(f"h{i}", f"m{i}"), E(f"m{i}", f"g{i}")]
D["ch10-six-meetings"] = dict(items=items, edges=edges)

# own: bad review vs good review
items = [
    T("Плохой review", 0, -50, 24, "#e03131"), T("Хороший review", 0, 300, 24, "#2f9e44"),
    N("b1", "Автор выходит\nк экрану", 0, 0, "r", 250, 100),
    N("b2", "Читает свой документ\nвслух", 350, 0, "r", 250, 100),
    N("b3", "Аудитория молчит\nи слушает", 700, 0, "r", 250, 100),
    N("b4", "Тысячи часов потрачены,\nполезных замечаний нет", 1050, 0, "r", 280, 100),
    N("g1", "Короткий понятный\nдокумент", 0, 350, "g", 250, 100),
    N("g2", "Все читают до встречи\n(10 минут или блок\nв календаре)", 350, 350, "g", 250, 100),
    N("g3", "Обсуждение: аудитория\nи автор", 700, 350, "g", 250, 100),
    N("g4", "Спецификация или\nвыводы по инциденту\nстановятся лучше", 1050, 350, "g", 280, 100),
]
edges = [E("b1", "b2"), E("b2", "b3"), E("b3", "b4"), E("g1", "g2"), E("g2", "g3"), E("g3", "g4")]
D["ch10-good-bad-review"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
