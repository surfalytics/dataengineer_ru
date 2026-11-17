#!/usr/bin/env python3
"""Модель устаревания API (Stripe) из главы 22 на пакете lethain/systems.
Запуск: python3 -I ch22_api_deprecation_model.py
Сравнивает четыре сценария по числу интегрированных клиентов (IntegratedCustomers)."""
from systems.parse import parse


def spec(deprecation=0.5, baseline_churn=0.1):
    """deprecation - доля интегрированных клиентов, которых задело устаревание API за раунд;
    baseline_churn - доля клиентов, которые уходят по любым другим причинам."""
    lines = [
        "[PotentialCustomers] > EngagedCustomers @ 100",
        "EngagedCustomers > IntegratedCustomers @ Leak(0.5)",
        f"IntegratedCustomers > DeprecationImpactedCustomers @ Leak({deprecation:g})",
        "DeprecationImpactedCustomers > IntegratedCustomers @ Leak(0.9)",
        "DeprecationImpactedCustomers > ChurnedCustomers @ Leak(0.1)",
    ]
    if baseline_churn > 0:  # Leak(0) пакет не принимает: нулевой поток просто не пишем
        lines.insert(2, f"IntegratedCustomers > ChurnedCustomers @ Leak({baseline_churn:g})")
    return "\n".join(lines)


SCENARIOS = [
    ("1. Устаревание 50%, обычный уход 10%", spec(0.5, 0.1)),
    ("2. Устаревание 10%, обычный уход 10%", spec(0.1, 0.1)),
    ("3. Устаревание 50%, обычного ухода нет", spec(0.5, 0)),
    ("4. Устаревание 10%, обычного ухода нет", spec(0.1, 0)),
]

print(f"{'Сценарий':<42}{'раунд 40':>10}{'раунд 100':>11}{'затронуты':>11}")
for name, text in SCENARIOS:
    rows = parse(text).run(rounds=100)
    r40, r100 = rows[40], rows[-1]
    print(f"{name:<42}{r40['IntegratedCustomers']:>10.0f}{r100['IntegratedCustomers']:>11.0f}"
          f"{r100['DeprecationImpactedCustomers']:>11.0f}")
