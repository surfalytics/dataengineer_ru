#!/usr/bin/env python3
"""Глава 8: model collapse на игрушечной «модели». Без внешних библиотек.

Что показывает скрипт:
  «Модель» это распределение по 50 событиям: частые и редкие (как слова в языке).
  Каждое поколение модель учится на выборке из предыдущего поколения и снова даёт выборку.
  Три режима:
    A) только синтетика: каждое поколение учится на выходе предыдущего;
    B) смесь: половина обучающей выборки каждый раз свежая реальная, половина синтетическая;
    C) накопление: реальные данные остаются в обучении, синтетика только добавляется.
  Смотрим, сколько событий «выжило» и как меняется entropy. Редкие события исчезают первыми.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_model_collapse.py
"""
import math
import random

K = 50            # число событий
S = 200           # размер обучающей выборки на поколение
GENS = 20
RUNS = 30
weights = [1 / (i + 1) for i in range(K)]
total = sum(weights)
REAL = [w / total for w in weights]            # настоящее распределение


def sample(probs, n, rng):
    return rng.choices(range(K), weights=probs, k=n)


def fit(data):
    counts = [0] * K
    for x in data:
        counts[x] += 1
    n = len(data)
    return [c / n for c in counts]


def entropy_bits(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


def run(mode, seed):
    rng = random.Random(seed)
    real0 = sample(REAL, S, rng)
    model = fit(real0)                           # поколение 0: обучены на реальных данных
    history = [model]
    pool = list(real0)                           # для режима C: реальные данные хранятся
    for _ in range(GENS):
        synth = sample(model, S, rng)
        if mode == "A":
            train = synth
        elif mode == "B":
            train = sample(REAL, S // 2, rng) + synth[: S // 2]
        else:
            pool = pool + synth                  # реальные примеры остаются навсегда
            train = pool
        model = fit(train)
        history.append(model)
    return history


print(f"Настоящее распределение: {K} событий, entropy {entropy_bits(REAL):.2f} бит. Выборка на поколение: {S}.")
print(f"Среднее по {RUNS} запускам. «Выжило» = событие, у которого вероятность в модели больше нуля.\n")
shown = [0, 1, 2, 5, 10, 20]
print(f"{'поколение':<11}" + "".join(f"{g:>7}" for g in shown))
names = {"A": "A) только синтетика", "B": "B) смесь с реальными", "C": "C) накопление"}
for mode in "ABC":
    runs = [run(mode, 1000 + r) for r in range(RUNS)]
    alive = [sum(sum(1 for p in h[g] if p > 0) for h in runs) / RUNS for g in shown]
    ent = [sum(entropy_bits(h[g]) for h in runs) / RUNS for g in shown]
    print(f"{names[mode]}")
    print(f"{'  выжило':<11}" + "".join(f"{v:>7.1f}" for v in alive))
    print(f"{'  entropy':<11}" + "".join(f"{v:>7.2f}" for v in ent))
print("\nВ режиме A редкие события исчезают и не возвращаются: у модели нет шанса увидеть их снова.")
print("В режимах B и C реальные данные «напоминают» модели о редких событиях, распределение остаётся стабильным.")
