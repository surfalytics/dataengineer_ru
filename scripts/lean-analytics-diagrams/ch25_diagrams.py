#!/usr/bin/env python3
"""Chapter 25 (Media Site: Lines in the Sand) diagrams. Usage: ch25_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: the lines in the sand along the reader's path (main diagram)
W5, H5, X5 = 250, 130, 330
steps = [
    ("imp", "Показы рекламы\n100 000", "n"),
    ("clk", "Клики: 500–2 000\nCTR 0,5–2%", "p"),
    ("vis", "Визиты на сайт\n≈95% кликов,\n≈5% теряется", "y"),
    ("read", "Чтение статьи:\n90+ секунд\nвовлечённого времени", "g"),
    ("shr", "Репост в узком кругу:\n1 репост ≈ 9 просмотров", "pu"),
]
items = [T("Ориентиры медиасайта на пути читателя", 0, -70, 24, "#1971c2")]
for i, (sid, text, k) in enumerate(steps):
    items.append(N(sid, text, i * X5, 0, k, W5, H5))
items += [
    N("bad", "CTR ниже 0,08%\n(как у пустого баннера):\nчто-то сломано", 0, 230, "r", 330, 110),
    N("top", "Потолок: даже лучшие\nобъявления редко\nдают больше 5%", 660, 230, "q", 330, 110),
    T("Числа из книги (2010–2012 годы). Это ориентиры, а не стандарт.", 0, 380, 18, "#868e96"),
]
D["ch25-media-lines"] = dict(items=items, edges=[
    E("imp", "clk"), E("clk", "vis"), E("vis", "read"), E("read", "shr"),
    E("bad", "clk", dashed=True), E("top", "clk", dashed=True)])

# Fig 25-1 (redrawn, values read from the chart; only media values are exact in the text)
groups = [("Медиа", 47, 90), ("Транзакции\n(e-commerce)", 70, 54), ("SaaS", 38, 27)]
S, BW, GG, BASE = 3.2, 90, 140, 360
items = [T("Среднее вовлечённое время по типу сайта, секунды", 0, -60, 24, "#1971c2")]
for i, (name, land, other) in enumerate(groups):
    x = i * (2 * BW + GG)
    for j, (v, k) in enumerate([(land, "y"), (other, "r")]):
        h = int(v * S); bx = x + j * BW
        items.append(N(f"b{i}{j}", "", bx, BASE - h, k, BW, h))
        items.append(T(f"≈{v}" if i else f"{v}", bx + 25, BASE - h - 30, 20, "#495057"))
    items.append(T(name, x + 20, BASE + 12, 20, "#495057"))
items += [
    N("lg1", "", 1000, 40, "y", 40, 30), T("Посадочная страница", 1055, 42, 20, "#495057"),
    N("lg2", "", 1000, 90, "r", 40, 30), T("Остальные страницы", 1055, 92, 20, "#495057"),
    T("Медиасайту нужно долгое чтение статей.\nSaaS хочет, чтобы человек быстро сделал дело.", 0, BASE + 90, 20, "#868e96"),
]
D["ch25-engaged-time"] = dict(items=items, edges=[])

# own: referrers vs social traffic (Chartbeat numbers from the text)
refs = [("Тематические сайты", 9510, 70, "g"), ("Facebook", 2670, 51, "p"), ("Twitter", 917, 28, "pu")]
S, BW, GAP, BASE = 0.035, 200, 120, 380
items = [T("Вовлечённые минуты за две недели после одного упоминания", 0, -60, 24, "#1971c2")]
for i, (name, mins, peak, k) in enumerate(refs):
    h = max(int(mins * S), 8); x = i * (BW + GAP)
    items.append(N(f"r{i}", "", x, BASE - h, k, BW, h))
    items.append(T(f"{mins:,}".replace(",", " ") + " мин", x + 40, BASE - h - 32, 20, "#495057"))
    items.append(T(f"{name}\nпик: {peak} человек онлайн", x, BASE + 12, 20, "#495057"))
items += [T("Ссылка с сайта даёт поток на дни. Всплеск из соцсетей быстро гаснет.", 0, BASE + 90, 20, "#868e96")]
D["ch25-referrers"] = dict(items=items, edges=[])

if __name__ == "__main__":
    run_all(D)
