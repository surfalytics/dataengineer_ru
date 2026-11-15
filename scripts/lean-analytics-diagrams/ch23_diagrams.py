#!/usr/bin/env python3
"""Chapter 23 (SaaS: Lines in the Sand) diagrams. Usage: ch23_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Tables 23-2 and 23-3 (main diagram): three funnels from 5000 serious evaluators
cols = [
    ("С картой", 100, 50, 30, "0,6%", "r", "2%", "50%", "−20 (40%)"),
    ("Без карты", 500, 75, 60, "1,2%", "y", "10%", "15%", "−15 (20%)"),
    ("Без карты + фокус\nна серьёзных", 500, 125, 100, "2%", "g", "10%", "25%", "−25 (20%)"),
]
items = [T("Три воронки из 5000 серьёзных посетителей", 0, -70, 24, "#1971c2"),
         N("v", "5000 серьёзных посетителей", 300, 0, "n", 520, 80)]
edges = []
for i, (head, tr, sub, rem, pct, k, l1, l2, l3) in enumerate(cols):
    x = i * 420
    items += [
        N(f"t{i}", f"{head}:\n{tr} попробовали", x, 220, "p", 340, 100),
        N(f"s{i}", f"{sub} подписались", x, 440, "p", 340, 80),
        N(f"r{i}", f"{rem} остались ({pct})", x, 640, k, 340, 80),
    ]
    edges += [E("v", f"t{i}", l1), E(f"t{i}", f"s{i}", l2), E(f"s{i}", f"r{i}", l3)]
items.append(T("Подписи на стрелках — доля перехода. Последний шаг — churn в первый платёжный период", 0, 760, 20, "#868e96"))
D["ch23-three-funnels"] = dict(items=items, edges=edges)

# Fig 23-1 (own numbers): smile graph, share of a cohort that comes back each month
vals = [45, 31, 26, 24, 23, 23, 24, 26, 28, 30, 33, 36, 38]
marks = {0: "старт", 4: "1 год", 8: "2 года", 12: "3 года"}
S, BW, GAP, BASE = 8, 60, 20, 420
items = [T("Улыбка Evernote: доля когорты, которая возвращается в месяц", 0, -60, 24, "#1971c2")]
for i, v in enumerate(vals):
    h = v * S; x = i * (BW + GAP)
    k = "g" if i in (0, 12) else "y" if v <= 24 else "p"
    items.append(N(f"b{i}", "", x, BASE - h, k, BW, h))
    items.append(T(f"{v}%", x + 8, BASE - h - 28, 18, "#1971c2"))
    if i in marks:
        items.append(T(marks[i], x, BASE + 10, 20, "#495057"))
items += [
    T("Шаг — квартал после регистрации. Числа условные, форма — как в книге", 0, BASE + 50, 18, "#868e96"),
    T("Сначала люди уходят, потом возвращаются: дно около года, к трём годам доля снова растёт", 0, BASE + 80, 18, "#495057"),
]
D["ch23-smile-graph"] = dict(items=items, edges=[])

# own: monthly churn lines in the sand for SaaS
items = [
    T("Churn в месяц для SaaS: где проходят границы", 0, -60, 24, "#1971c2"),
    N("c1", "до 2%\nотлично: можно\nрасти до больших масштабов", 0, 0, "g", 330, 120),
    N("c2", "2–5%\nнормально для\nраннего этапа", 450, 0, "y", 330, 120),
    N("c3", "больше 5%\nпродукт не липкий:\nсначала чините удержание", 900, 0, "r", 330, 120),
    T("Лучшие SaaS: 1,5–3% в месяц. OfficeDrop: цель — меньше 4%, факт — 2%", 0, 160, 20, "#495057"),
    T("В первый платёж churn бывает до 40–50%, если списание стало для клиента сюрпризом", 0, 195, 20, "#c92a2a"),
]
D["ch23-churn-lines"] = dict(items=items, edges=[E("c1", "c2"), E("c2", "c3")])

if __name__ == "__main__":
    run_all(D)
