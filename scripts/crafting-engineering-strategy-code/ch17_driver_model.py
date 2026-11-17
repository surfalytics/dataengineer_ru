#!/usr/bin/env python3
"""Модель онбординга водителей (Theoretical Ride Sharing) из главы 17 на пакете lethain/systems.
Запуск: python3 -I ch17_driver_model.py
Для каждого сценария печатает число активных водителей на 50-м раунде."""
from systems.parse import parse


def spec(eligible=0.25, missing=0.1, departed=0.05, suspended=0.01):
    """eligible - доля заявок, ставших eligible за раунд; missing - доля, возвращённая за недостающими данными;
    departed / suspended - доли вернувшихся водителей за раунд."""
    lines = [
        "CityPop(10000)",
        "CityPop > AppliedDrivers @ 100",
        f"AppliedDrivers > EligibleDrivers @ Leak({eligible:g})",
    ]
    if missing:  # Leak(0) пакет не принимает, поэтому поток просто не пишем
        lines.append(f"EligibleDrivers > AppliedDrivers @ Leak({missing:g})")
    lines += [
        "EligibleDrivers > OnboardedDrivers @ Leak(0.25)",
        "OnboardedDrivers > ActiveDrivers @ Leak(0.5)",
        "ActiveDrivers > DepartedDrivers @ Leak(0.1)",
        "ActiveDrivers > SuspendedDrivers @ Leak(0.1)",
        f"DepartedDrivers > ActiveDrivers @ Leak({departed:g})",
        f"SuspendedDrivers > ActiveDrivers @ Leak({suspended:g})",
    ]
    return "\n".join(lines)


SCENARIOS = [
    ("1. База", spec()),
    ("2. Eligible в 2 раза быстрее (50%)", spec(eligible=0.5)),
    ("3. Без потерь на недостающих данных", spec(missing=0)),
    ("4. Вернувшихся departed 20% (было 5%)", spec(departed=0.2)),
    ("5. Вернувшихся suspended 2,5% (было 1%)", spec(suspended=0.025)),
    ("6. Оба: departed 20%, suspended 2,5%", spec(departed=0.2, suspended=0.025)),
]

ROUNDS = 50
print(f"{'Сценарий':<44}{'активные':>9}{'departed':>10}{'suspended':>11}")
for name, text in SCENARIOS:
    last = parse(text).run(rounds=ROUNDS)[-1]
    print(f"{name:<44}{last['ActiveDrivers']:>9}{last['DepartedDrivers']:>10}{last['SuspendedDrivers']:>11}")

# Разница Leak и Conversion: 100 заявок и 100 eligible, доля 0,25
leak = parse("AppliedDrivers(100)\nEligibleDrivers(100)\nAppliedDrivers > EligibleDrivers @ Leak(0.25)").run(rounds=1)[-1]
conv = parse("AppliedDrivers(100)\nEligibleDrivers(100)\nAppliedDrivers > EligibleDrivers @ Conversion(0.25)").run(rounds=1)[-1]
print("Leak(0.25):      applied", leak["AppliedDrivers"], "eligible", leak["EligibleDrivers"])
print("Conversion(0.25): applied", conv["AppliedDrivers"], "eligible", conv["EligibleDrivers"])
