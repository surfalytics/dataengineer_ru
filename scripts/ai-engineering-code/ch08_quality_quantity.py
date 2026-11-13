#!/usr/bin/env python3
"""Глава 8: качество, разнообразие и объём данных на игрушечной задаче. Без внешних библиотек.

Что показывает скрипт:
  1. Качество x разнообразие. Три датасета одного размера (600 примеров):
     (a) чистые, но только из одной области; (b) из всех областей, но с шумными метками;
     (c) из всех областей и чистые. Модель: kNN. Как в главе: (c) лучше обоих.
  2. Кривая «качество от объёма»: обучаем на 25%, 50%, 100% данных и видим diminishing returns.
     Подгоняем кривую acc = a - b * n^(-c) и прогнозируем, что даст удвоение данных.
  3. Бюджет: сколько примеров можно оплатить и сколько примеров в токенах pre-training.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_quality_quantity.py
"""
import heapq
import random

# ---------- Игрушечный мир ----------
# 4 «области» (как темы запросов). В каждой области свой центр и своя граница между классами 0 и 1.
CENTERS = [(0.0, 0.0), (6.0, 0.0), (0.0, 6.0), (6.0, 6.0)]
NOISE_SD = 1.0


def label_of(domain, dx, dy):
    # В областях 0 и 3 класс зависит от dx, в областях 1 и 2 от dy (с разным знаком).
    # Поэтому правило одной области не подходит к другой.
    if domain in (0, 3):
        return 1 if dx > 0 else 0
    return 1 if dy < 0 else 0


def sample(rng, n, domains, flip=0.0):
    data = []
    for _ in range(n):
        d = rng.choice(domains)
        cx, cy = CENTERS[d]
        dx, dy = rng.gauss(0, NOISE_SD), rng.gauss(0, NOISE_SD)
        y = label_of(d, dx, dy)
        if rng.random() < flip:
            y = 1 - y
        data.append((cx + dx, cy + dy, y))
    return data


def knn_accuracy(train, test, k=7):
    ok = 0
    for x, y, lab in test:
        near = sorted(train, key=lambda t: (t[0] - x) ** 2 + (t[1] - y) ** 2)[:k]
        pred = 1 if sum(t[2] for t in near) * 2 > k else 0
        ok += pred == lab
    return ok / len(test)


SEEDS = range(5)
print("=== 1. Качество x разнообразие (600 примеров, kNN, среднее по 5 прогонам) ===")
configs = [("(a) чистые, одна область", [0], 0.0),
           ("(b) все области, 35% ошибок в метках", [0, 1, 2, 3], 0.35),
           ("(c) все области, чистые", [0, 1, 2, 3], 0.0)]
for name, doms, flip in configs:
    accs = []
    for s in SEEDS:
        rng = random.Random(100 + s)
        train = sample(rng, 600, doms, flip)
        test = sample(random.Random(500 + s), 300, [0, 1, 2, 3])
        accs.append(knn_accuracy(train, test))
    print(f"{name:<40} accuracy {sum(accs) / len(accs):.3f}")

# ---------- Кривая качества от объёма ----------
print("\n=== 2. Кривая «качество от объёма данных» (20% ошибок в метках, kNN, среднее по 20 прогонам) ===")
ALL_SIZES = [100, 200, 400, 800, 1600, 3200]
curve = {n: 0.0 for n in ALL_SIZES}
RUNS = 20
for s in range(RUNS):
    train = sample(random.Random(900 + s), ALL_SIZES[-1], [0, 1, 2, 3], 0.2)   # один растущий датасет
    test = sample(random.Random(700 + s), 500, [0, 1, 2, 3])
    ok = {n: 0 for n in ALL_SIZES}
    for x, y, lab in test:
        dist = [((t[0] - x) ** 2 + (t[1] - y) ** 2, t[2]) for t in train]
        for n in ALL_SIZES:                      # первые n примеров = «подвыборка размера n»
            near = heapq.nsmallest(15, dist[:n])
            ok[n] += (1 if sum(l for _, l in near) * 2 > 15 else 0) == lab
    for n in ALL_SIZES:
        curve[n] += ok[n] / len(test) / RUNS
prev = None
for n in ALL_SIZES:
    gain = "" if prev is None else f"   прирост от удвоения: {100 * (curve[n] - curve[prev]):+.1f} п.п."
    print(f"  {n:>5} примеров: accuracy {curve[n]:.3f}{gain}")
    prev = n

# Как оценить в реальном проекте: учим на 25%, 50%, 100% и подгоняем acc = a - b * n^(-c).
FULL = 1600
sizes = [FULL // 4, FULL // 2, FULL]
best = None
for c100 in range(5, 201):
    c = c100 / 100
    xs = [n ** -c for n in sizes]
    ys = [curve[n] for n in sizes]
    mx, my = sum(xs) / 3, sum(ys) / 3
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - slope * mx
    err = sum((a + slope * x - y) ** 2 for x, y in zip(xs, ys))
    if best is None or err < best[0]:
        best = (err, a, -slope, c)
_, a, b, c = best
print(f"\nПодгонка по 25%/50%/100% ({sizes[0]}, {sizes[1]}, {sizes[2]} примеров):")
print(f"  acc(n) = {a:.3f} - {b:.2f} * n^(-{c:.2f}); потолок около {a:.3f}")
print(f"  Прогноз для {FULL * 2} примеров: {a - b * (FULL * 2) ** -c:.3f}; реально получилось {curve[FULL * 2]:.3f}")

# ---------- Бюджет и масштаб ----------
print("\n=== 3. Бюджет и масштаб ===")
budget, price = 10_000, 2
print(f"Бюджет ${budget}, ${price} за пример: максимум {budget // price} примеров")
for model, tokens in [("Llama 2", 2e12), ("Llama 3 (около 15 трлн токенов)", 15e12)]:
    print(f"{model}: {tokens / 2000 / 1e9:.1f} млрд примеров по 2000 токенов")
print(f"Если бы Llama 3 учили на 16 трлн токенов: {16e12 / 2000 / 1e9:.1f} млрд примеров, а не 15")
