#!/usr/bin/env python3
"""Глава 12: как меняется воронка вовлечения UGC-сайта от месяца к месяцу.
Числа выдуманы. Запуск: python3 -I scripts/lean-analytics-code/ch12_funnel_changes.py"""

months = ["Янв", "Фев", "Мар", "Апр"]
# Активные пользователи на каждом уровне воронки по месяцам
funnel = {
    "Посетители":   [10000, 15000, 19500, 25000],
    "Вернувшиеся":  [5000, 8100, 9300, 12500],
    "Голосующие":   [2000, 3000, 3700, 5200],
    "Комментаторы": [800, 1100, 1550, 2000],
    "Авторы":       [200, 260, 410, 500],
}
tiers = list(funnel)

print("Конверсия из предыдущего уровня, %")
for prev, cur in zip(tiers, tiers[1:]):
    rates = [100 * c / p for c, p in zip(funnel[cur], funnel[prev])]
    print(f"{cur:<13}" + "".join(f"{r:>8.1f}" for r in rates))

print("\nИзменение конверсии к прошлому месяцу, %")
for prev, cur in zip(tiers, tiers[1:]):
    rates = [c / p for c, p in zip(funnel[cur], funnel[prev])]
    row = []
    for before, now in zip(rates, rates[1:]):
        change = 100 * now / before
        row.append(f"{change:>7.1f}{'+' if change >= 100 else '-'}")
    print(f"{cur:<13}" + "     n/a" + "".join(row))
