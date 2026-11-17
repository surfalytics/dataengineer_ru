#!/usr/bin/env python3
"""Модель состава инженеров по уровням (глава 18) на пакете lethain/systems.
Запуск: python3 -I ch18_seniority_model.py
Четыре уровня SWE1-SWE4. Печатает число людей на каждом уровне на 50-м раунде
и отношение SWE1 к SWE4 (цель из книги: около 5 к 1)."""
from systems.parse import parse

LEVELS = 4
ROUNDS = 50


def spec(initial, hiring_rate, backfill_down, cap=None):
    """initial - стартовые размеры SWE1..SWE4; hiring_rate - найм на каждый уровень за раунд;
    backfill_down - True: уход с уровня N закрываем наймом на уровень N-1 (SWE1 остаётся SWE1);
    cap - максимум для SWE4 (None: без лимита)."""
    lines = [f"HiringRate({hiring_rate})"]
    for n in range(1, LEVELS + 1):
        size = f"{initial[n - 1]}, {cap}" if (n == LEVELS and cap) else f"{initial[n - 1]}"
        lines.append(f"[Candidates] > SWE{n}({size}) @ HiringRate")
        if n > 1:
            lines.append(f"SWE{n - 1} > SWE{n} @ Leak(0.1)")
        lines.append(f"SWE{n} > DepartedSWE{n} @ Leak(0.1)")
        target = n - 1 if (backfill_down and n > 1) else n
        lines.append(f"DepartedSWE{n} > SWE{target} @ Leak(0.5)")
    return "\n".join(lines)


EVEN = [10, 10, 10, 0]
BIG = [100, 100, 100, 10]
SCENARIOS = [
    ("1. Замена на том же уровне", spec(EVEN, 2, False)),
    ("2. Замена на уровень ниже (N-1)", spec(EVEN, 2, True)),
    ("3. N-1 и найма нет", spec(BIG, 0, True)),
    ("4. N-1, найма нет, потолок SWE4 = 20", spec(BIG, 0, True, cap=20)),
]

print(f"{'Сценарий':<42}{'SWE1':>7}{'SWE2':>7}{'SWE3':>7}{'SWE4':>7}{'SWE1:SWE4':>11}")
for name, text in SCENARIOS:
    last = parse(text).run(rounds=ROUNDS)[-1]
    s = [last[f"SWE{n}"] for n in range(1, LEVELS + 1)]
    print(f"{name:<42}{s[0]:>7.0f}{s[1]:>7.0f}{s[2]:>7.0f}{s[3]:>7.0f}{s[0] / s[3]:>11.2f}")
