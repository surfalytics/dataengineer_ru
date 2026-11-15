#!/usr/bin/env python3
"""Chapter 28 (What to Do When You Don't Have a Baseline) diagrams. Usage: ch28_diagrams.py [name ...]  (no args = all)"""
import math
from excb import N, E, Z, T, run_all

D = {}

# Figs 28-1 + 28-2 (own numbers): 30 days of tests, conversion grows from 0.3% to 8.2%
# and slows down near a ceiling of about 9%. Curve: 9 - 8.7 * exp(-k * (day - 1)).
k = -math.log(0.8 / 8.7) / 29
days = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 30]
S, BW, GAP, BASE = 40, 70, 24, 420
items = [T("30 дней тестов регистрации: конверсия растёт всё медленнее", 0, -80, 24, "#1971c2")]
for i, d in enumerate(days):
    v = 9 - 8.7 * math.exp(-k * (d - 1))
    h = max(v * S, 6); x = i * (BW + GAP)
    items.append(N(f"b{i}", "", x, BASE - h, "p", BW, h))
    items.append(T(f"{v:.1f}%".replace(".", ","), x + 4, BASE - h - 28, 18, "#1971c2"))
    items.append(T(f"д. {d}", x + 10, BASE + 10, 18, "#495057"))
W_ALL = len(days) * (BW + GAP) - GAP
items += [
    N("ceil", "", 0, BASE - 9 * S - 2, "r", W_ALL, 4),
    T("потолок ≈ 9%: дальше без радикальных перемен не вырасти", W_ALL + 20, BASE - 9 * S - 14, 18, "#e03131"),
    N("goal", "", 0, BASE - 7 * S - 2, "g", W_ALL, 4),
    T("цель бизнес-модели: 7%", W_ALL + 20, BASE - 7 * S - 14, 18, "#2f9e44"),
    T("Трафик за месяц вырос примерно с 1200 до 1462 посетителей в день. Числа условные, форма — как в книге", 0, BASE + 50, 18, "#868e96"),
]
D["ch28-conversion-plateau"] = dict(items=items, edges=[])

# own: what to do when a metric reaches its plateau
items = [
    N("p", "Метрика вышла на плато:\nконверсия около 9%", 0, 100, "p", 340, 110),
    N("q", "Этого хватает\nбизнес-модели?", 460, 100, "y", 300, 110),
    N("yes", "Да (модели нужно 7%):\nпереходите к другой метрике,\nнапример к трафику", 900, -20, "g", 380, 120),
    N("no", "Нет: нужна радикальная\nсмена, например новая\nстратегия привлечения", 900, 220, "r", 380, 120),
    T("Плато — это ваш собственный ориентир, когда нормы рынка нет", 0, 380, 20, "#495057"),
]
D["ch28-plateau-decision"] = dict(items=items, edges=[E("p", "q"), E("q", "yes", "да"), E("q", "no", "нет")])

if __name__ == "__main__":
    run_all(D)
