#!/usr/bin/env python3
"""Chapter 21 (The Goals to Come) diagrams. Usage: ch21_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: OKR as a launch pad for many areas of life (main diagram)
D["ch21-launchpad"] = dict(items=[
    T("OKR как стартовая площадка", 0, -50, 22, "#1971c2"),
    N("okr", "OKR и CFR:\nцели, разговоры,\nобратная связь", 420, 260, "g", 300, 120),
    N("a1", "Бизнес", 0, 0, "y", 270, 90),
    N("a2", "Здравоохранение", 420, 0, "y", 270, 90),
    N("a3", "Школа", 840, 0, "y", 270, 90),
    N("a4", "Государство", 0, 520, "y", 270, 90),
    N("a5", "Рост ВВП", 420, 520, "y", 270, 90),
    N("a6", "Общественный\nпрогресс", 840, 520, "y", 270, 90),
], edges=[E("okr", "a1"), E("okr", "a2"), E("okr", "a3"),
          E("okr", "a4"), E("okr", "a5"), E("okr", "a6")])

# own: Doerr-Campbell chain for every new entrepreneur
D["ch21-coach-model"] = dict(items=[
    T("Цепочка Дёрра и Кэмпбелла", 0, -50, 22, "#1971c2"),
    N("a", "Kleiner Perkins\nинвестирует", 0, 0, "y", 270, 110),
    N("b", "Дёрр становится\nспонсором", 340, 0, "y", 270, 110),
    N("c", "Дёрр звонит\nКэмпбеллу", 680, 0, "y", 270, 110),
    N("d", "Кэмпбелл тренирует\nкоманду", 1020, 0, "g", 270, 110),
], edges=[E("a", "b"), E("b", "c"), E("c", "d")])

if __name__ == "__main__":
    run_all(D)
