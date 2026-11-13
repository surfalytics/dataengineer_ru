#!/usr/bin/env python3
"""Глава 10: годовой простой данных (часы) и цена работы инженеров по формулам книги.
Формулы и константы из главы: 1 таблица из 15 в год задета инцидентом, 1804 часа в году, $62 в час.
Таблицы, число инженеров и уровни зрелости ниже: наши примеры.
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch10_labor_cost.py"""

HOURS_IN_YEAR = 8760          # потолок простоя: все часы года
WORK_HOURS = 1804             # рабочих часов в году на человека (данные книги)
RATE = 62                     # $ в час, дата-инженер (данные книги)
TABLES_PER_INCIDENT = 15      # в год инцидент бывает у 1 таблицы из 15

# уровень зрелости: (TTD + TTR в часах, доля времени инженера на качество данных)
MATURITY = {"low": (8, 0.50), "average": (6, 0.35), "high": (4, 0.20)}


def downtime_hours(tables, ttd_plus_ttr):
    incidents = tables / TABLES_PER_INCIDENT           # N
    return min(incidents * ttd_plus_ttr, HOURS_IN_YEAR)  # DDT = N * (TTD + TTR)


def labor_cost(engineers, share):
    return engineers * WORK_HOURS * RATE * share


tables, engineers = 5000, 5
print(f"{tables} таблиц, {engineers} инженеров")
for level, (hours, share) in MATURITY.items():
    ddt = downtime_hours(tables, hours)
    cost = labor_cost(engineers, share)
    print(f"{level:8} TTD+TTR={hours} ч, доля {share:.0%}: простой {ddt:,.0f} ч, работа {cost:,.0f} $")

# число таблиц, при котором простой упирается в потолок (low)
limit = HOURS_IN_YEAR / MATURITY["low"][0] * TABLES_PER_INCIDENT
print(f"потолок 8 760 ч при low: {limit:,.0f} таблиц")
print(f"20 000 таблиц, low: {downtime_hours(20000, 8):,.0f} ч (обрезано до потолка)")
