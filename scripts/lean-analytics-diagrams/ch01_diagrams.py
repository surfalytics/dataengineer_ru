#!/usr/bin/env python3
"""Chapter 1 (We're All Liars) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: the Airbnb photo experiment, from gut feeling to scale (main diagram)
D["ch01-airbnb-concierge-mvp"] = dict(items=[
    T("Кейс Airbnb: от интуиции к проверенному росту", 0, -50, 22, "#1971c2"),
    N("gut", "Интуиция:\nхорошие фото\nпомогут бизнесу", 0, 0, "n", 270, 120),
    N("hyp", "Гипотеза: с проф.\nфото больше броней,\nхозяева хотят услугу", 330, 0, "y", 270, 120),
    N("mvp", "Concierge MVP:\nфотографы снимают\nвручную, без кода", 660, 0, "p", 270, 120),
    N("res", "Результат: броней\nв 2–3 раза больше\nсреднего по рынку", 990, 0, "g", 270, 120),
    N("scale", "Масштаб: почти\n5000 съёмок в месяц\n(февраль 2012)", 1320, 0, "g", 270, 120),
    N("exp", "Новые опыты: водяной\nзнак, предложение через\nподдержку, строже к фото", 990, 230, "pu", 270, 120),
    N("kpi", "Ключевая метрика:\nсъёмок в месяц", 1320, 230, "q", 270, 120),
    T("Каждый шаг измеряют и при нужде меняют", 990, 380, 18, "#495057"),
], edges=[E("gut", "hyp"), E("hyp", "mvp"), E("mvp", "res"), E("res", "scale"),
          E("scale", "kpi"), E("exp", "kpi")])

# Fig 1-1 redrawn: hockey-stick growth of booked nights (our own example numbers)
B = [("2009", 20), ("2010 I", 35), ("2010 II", 55), ("2011 I", 90), ("2011 II", 170), ("2012 I", 300)]
items = [T("Забронированные ночи (условные числа, форма роста как в книге)", -20, -60, 20, "#1971c2")]
for i, (lab, h) in enumerate(B):
    x = i * 160
    items.append(N(f"b{i}", "", x, 400 - h, "g" if i >= 4 else "p", 120, h))
    items.append(T(lab, x + 25, 420, 18, "#495057"))
items += [N("axis", "", -20, 400, "n", 940, 4),
          N("ph", "20 фотографов\nснимают жильё", 60, 40, "y", 250, 90),
          T("Рост «хоккейной клюшкой»", 520, 470, 20, "#2f9e44")]
D["ch01-hockey-stick"] = dict(items=items, edges=[E("ph", "b4")])

if __name__ == "__main__":
    run_all(D)
