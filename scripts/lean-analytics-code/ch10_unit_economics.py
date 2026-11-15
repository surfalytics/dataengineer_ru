#!/usr/bin/env python3
"""Глава 10: юнит-экономика бесплатной мобильной игры (пример из книги, рисунок 10-1).
Запуск: python3 -I scripts/lean-analytics-code/ch10_unit_economics.py  (только стандартная библиотека)"""

downloads = 12_304      # загрузки за месяц
launch_rate = 0.96      # доля загрузивших, кто запустил игру
engagement_rate = 0.30  # доля запустивших, кто играл в три разных дня
arpu = 3.20             # доход в месяц на вовлечённого игрока, $
churn = 0.15            # доля игроков, которые уходят за месяц
cac = 11.21             # стоимость привлечения вовлечённого игрока, $

launches = downloads * launch_rate
engaged = launches * engagement_rate
revenue_month = engaged * arpu
lifetime = 1 / churn                 # средний срок жизни игрока, месяцев
ltv = arpu * lifetime
cohort_revenue = revenue_month * lifetime

print(f"Запуски:              {launches:,.0f}")
print(f"Вовлечённые игроки:   {engaged:,.0f}")
print(f"Доход за месяц:       ${revenue_month:,.2f}")
print(f"Срок жизни игрока:    {lifetime:.2f} мес.")
print(f"LTV игрока:           ${ltv:.2f}")
print(f"Доход когорты:        ${cohort_revenue:,.2f}")
print(f"Вклад игрока:         ${ltv - cac:.2f}")
print(f"ROI привлечения:      {ltv / cac:.1f}x")
print(f"Окупаемость CAC:      {cac / arpu:.2f} мес.")
