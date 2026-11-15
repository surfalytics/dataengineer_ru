#!/usr/bin/env python3
"""Chapter 21 (Am I Good Enough?) diagrams. Usage: ch21_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: nine general lines in the sand (main diagram)
cx, cy, cw, ch = [0, 400, 800], [0, 190, 380], 370, 160
cards = [
    ("Рост", "5% в неделю — хорошо\n10% — отлично\n1% — продукт не найден", "p"),
    ("Вовлечённость", "30% зарегистрированных —\nраз в месяц, 10% — каждый\nдень (правило 30/10/10)", "p"),
    ("Цена", "найти пик выручки\nи поставить цену\nна 10% ниже", "y"),
    ("CAC", "не больше трети LTV\nклиента и тех,\nкого он пригласит", "y"),
    ("Virality", "выше 0,75 — хорошо\nвыше 1 — рост сам по себе\nниже 1 — дешевле CAC", "g"),
    ("Рассылки", "open rate 20–30%\nCTR больше 5%", "g"),
    ("Uptime", "платный сервис:\nне меньше 99,5%", "q"),
    ("Время на странице", "около 1 минуты\nвовлечённого времени", "q"),
    ("Скорость сайта", "меньше 5 секунд\nпосле 10 секунд —\nпотери", "q"),
]
items = [T("Линии на песке, общие для всех бизнес-моделей", 0, -60, 24, "#1971c2")]
for i, (head, body, k) in enumerate(cards):
    items.append(N(f"c{i}", f"{head}\n\n{body}", cx[i % 3], cy[i // 3], k, cw, ch))
items.append(T("Синие — рост и вовлечённость, жёлтые — деньги, зелёные — распространение,\nоранжевые — качество сервиса", 0, 560, 20, "#868e96"))
D["ch21-lines-in-the-sand"] = dict(items=items, edges=[])

# Fig 21-1 (own numbers): revenue by price, aim at the top of the curve
prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
rev = [2000, 2220, 2380, 2528, 2628, 2680, 2640, 2496, 2340, 2128, 1800]
S, BW, GAP, BASE = 0.14, 70, 30, 420
items = [T("Выручка при разной цене: ищем вершину кривой", 0, -60, 24, "#1971c2")]
for i, (p, r) in enumerate(zip(prices, rev)):
    h = int(r * S); x = i * (BW + GAP)
    k = "r" if p == 20 else "g" if p == 18 else "p"
    items.append(N(f"b{i}", "", x, BASE - h, k, BW, h))
    items.append(T(f"${p}", x + 15, BASE + 10, 20, "#495057"))
    items.append(T(f"{r:,}".replace(",", " "), x, BASE - h - 30, 18, "#1971c2"))
items += [
    T("Цена за единицу", 0, BASE + 45, 20, "#868e96"),
    T("Красный столбец — пик выручки ($20). Зелёный — цель: цена на 10% ниже пика, около $18", 0, BASE + 80, 20, "#495057"),
]
D["ch21-price-curve"] = dict(items=items, edges=[])

# own: virality lowers CAC (example from the text)
y = 0
D["ch21-viral-cac"] = dict(items=[
    N("ads", "Реклама: $1000", 0, y, "y", 220, 90),
    N("w1", "100 новых\nпользователей", 330, y, "p", 200, 90),
    N("w2", "+40", 640, y, "p", 120, 90),
    N("w3", "+16", 870, y, "p", 120, 90),
    N("w4", "+6,4 и дальше\nменьше", 1100, y, "p", 200, 90),
    N("r1", "Без virality:\nCAC = $1000 / 100 = $10", 160, 220, "n", 380, 100),
    N("r2", "С virality 0,4:\nоколо 165 пользователей,\nCAC = $1000 / 165 = $6,06", 700, 220, "g", 420, 120),
], edges=[E("ads", "w1"), E("w1", "w2", "×0,4"), E("w2", "w3", "×0,4"), E("w3", "w4", "×0,4"),
          E("w1", "r1", dashed=True), E("w4", "r2", dashed=True)])

# Fig 21-5 (own numbers): concurrent users fall with page load time
buckets = ["до 5 с", "5–10 с", "10–15 с", "15–20 с", "больше 20 с"]
users = [100, 55, 20, 5, 2]
items = [T("Одновременные пользователи и время загрузки страницы", 0, -60, 24, "#1971c2")]
BASE, BW, GAP = 330, 150, 40
for i, (b, u) in enumerate(zip(buckets, users)):
    h = max(int(u * 3), 6); x = i * (BW + GAP)
    k = "g" if i == 0 else "y" if i == 1 else "r"
    items.append(N(f"l{i}", "", x, BASE - h, k, BW, h))
    items.append(T(b, x + 20, BASE + 10, 20, "#495057"))
items += [
    T("Высота столбца — сколько людей одновременно на сайте (условные единицы)", 0, BASE + 50, 18, "#868e96"),
    N("hint", "После 15–18 секунд\nлюди просто не ждут", 600, 60, "r", 300, 80),
]
D["ch21-load-time"] = dict(items=items, edges=[E("hint", "l3")])

if __name__ == "__main__":
    run_all(D)
