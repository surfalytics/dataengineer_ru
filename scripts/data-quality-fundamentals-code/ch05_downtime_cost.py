#!/usr/bin/env python3
"""Глава 5: цена data downtime, годовая цена плохих данных, допустимый простой по SLO.
Цифры из главы: 59 $/час инженер, 75 $/час аналитик. Остальное: наши примеры.
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch05_downtime_cost.py"""

# 1. Цена одного часа простоя данных
engineer_rate = 59.0          # $/час, зарплата и бонусы дата-инженера
engineer_share = 0.25         # инженер тратит четверть каждого часа простоя
engineer_cost = engineer_rate * engineer_share

analyst_rate, analysts = 75.0, 10
analyst_cost = analyst_rate * analysts            # все простаивают: 750 $/час
analyst_cost_real = analyst_cost * (1 - 0.60)     # задет только 4 из 10: скидка 60%

print(f"инженер: {engineer_cost:.2f} $/час; аналитики: {analyst_cost:.0f} -> {analyst_cost_real:.0f} $/час")

# 2. Формула: (TTD + TTR) x цена часа
ttd_hours, ttr_hours = 36, 6      # в этом примере проблему заметили через 36 часов
hourly = engineer_cost + analyst_cost_real
one_incident = (ttd_hours + ttr_hours) * hourly
print(f"один инцидент: ({ttd_hours} + {ttr_hours}) x {hourly:.2f} = {one_incident:,.2f} $")

# 3. Год: около 100 часов простоя в месяц
year_analysts = 100 * analyst_cost_real * 12
year_all = 100 * hourly * 12
print(f"год, только аналитики: 100 x {analyst_cost_real:.0f} x 12 = {year_analysts:,.0f} $")
print(f"год, аналитики и инженер: {year_all:,.0f} $")

# 4. Цена плохих данных в год: labor + compliance + opportunity (сноска главы)
engineers, salary, revenue = 6, 120_000, 50_000_000     # наши числа
labor = engineers * salary * 0.30
compliance = revenue * 0.04
opportunity = 500_000                                   # наша оценка упущенной выручки
print(f"labor {labor:,.0f} + compliance {compliance:,.0f} + opportunity {opportunity:,.0f} "
      f"= {labor + compliance + opportunity:,.0f} $ в год")

# 5. SLO не равен 100%: сколько простоя он разрешает за квартал (90 дней)
quarter_minutes = 90 * 24 * 60
for slo in (0.99, 0.999, 0.9999):
    print(f"SLO {slo:.2%}: можно {quarter_minutes * (1 - slo):,.1f} минут простоя за квартал")

# 6. Blinkist: 6 инженеров, 50% рабочей недели на пожары
week_hours = 6 * 40
print(f"Blinkist: 50% от {week_hours} часов = {week_hours * 0.5:.0f} часов в неделю")
