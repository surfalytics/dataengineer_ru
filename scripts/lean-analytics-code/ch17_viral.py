#!/usr/bin/env python3
"""Глава 17 (этап Virality): viral coefficient и влияние viral cycle time.
Только стандартная библиотека. Запуск: python3 -I ch17_viral.py"""

# 1. Viral coefficient по шагам из книги (пример таблицы 17-1)
users, invites, accepted = 2000, 5000, 500
invite_rate = invites / users          # приглашений на одного пользователя
accept_rate = accepted / invites       # доля принятых приглашений
k = invite_rate * accept_rate
print(f"invite_rate={invite_rate}  accept_rate={accept_rate:.0%}  K={k:.0%}")

# 2. Пример Дэвида Скока: 10 первых пользователей, K=2, считаем 20 дней.
#    Каждый цикл новички приводят K новых людей.
def total_users(start, k, days, cycle_days):
    total = new = start
    for _ in range(days // cycle_days):
        new = new * k
        total += new
    return total

for cycle in (2, 1):
    print(f"цикл {cycle} дн. -> {total_users(10, 2, 20, cycle):,} пользователей за 20 дней")
