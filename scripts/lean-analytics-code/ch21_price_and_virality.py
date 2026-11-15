#!/usr/bin/env python3
"""Глава 21: точка максимальной выручки по тесту цен и CAC с учётом virality.
Числа выдуманы. Запуск: python3 -I scripts/lean-analytics-code/ch21_price_and_virality.py"""

# 1. Тест цен: сколько покупателей в месяц при каждой цене
prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
buyers = [200, 185, 170, 158, 146, 134, 120, 104, 90, 76, 60]
revenue = [p * b for p, b in zip(prices, buyers)]
for p, b, r in zip(prices, buyers, revenue):
    print(f"${p:>2}  покупателей {b:>3}  выручка ${r:,}")
best = max(range(len(prices)), key=lambda i: revenue[i])
target = prices[best] * 0.9                       # совет книги: на 10% ниже пика
print(f"Пик выручки: ${prices[best]} (${revenue[best]:,})")
print(f"Цена для роста базы: около ${target:.0f}")

# 2. Virality снижает CAC: каждый пользователь приводит k новых
spend, paid, k = 1000, 100, 0.4
users, wave = 0.0, float(paid)
for _ in range(5):                                # пять волн приглашений
    users += wave
    wave *= k
print(f"\nCAC без virality: ${spend / paid:.2f}")
print(f"После 5 волн: {users:.0f} пользователей, CAC ${spend / users:.2f}")
limit = paid / (1 - k)                            # сумма бесконечного ряда
print(f"Предел ряда: {limit:.1f} пользователя, CAC ${spend / limit:.2f}")
