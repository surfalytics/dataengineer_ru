"""Глава 3: comparative evaluation. Из матчей между моделями считаем рейтинг: Elo и Bradley-Terry.
Матчи генерируем с фиксированным seed из «настоящей» силы моделей, поэтому можно проверить рейтинг.
Запуск: python3 scripts/ai-engineering-code/ch03_rating.py   (только стандартная библиотека)"""
import itertools
import math
import random

TRUE = {"модель-A": 0.0, "модель-B": 0.6, "модель-C": 1.0, "модель-D": 1.7, "модель-E": 2.4}  # логит силы
rng = random.Random(42)


def play(a, b):  # побеждает a с вероятностью 1 / (1 + e^(sb - sa))
    return a if rng.random() < 1 / (1 + math.exp(TRUE[b] - TRUE[a])) else b


pairs = list(itertools.combinations(TRUE, 2))
matches = []
for a, b in pairs:
    for _ in range(300):
        matches.append((a, b, play(a, b)))
rng.shuffle(matches)
print("матчей:", len(matches), "| пар моделей:", len(pairs))

print("\n== 1. Win rate по парам")
for a, b in pairs:
    m = [w for x, y, w in matches if (x, y) == (a, b)]
    print(f"{a} побеждает {b}: {m.count(a) / len(m):.0%}")


def elo(order, k=16, start=1000):
    r = dict.fromkeys(TRUE, float(start))
    for a, b, w in order:
        ea = 1 / (1 + 10 ** ((r[b] - r[a]) / 400))
        sa = 1.0 if w == a else 0.0
        r[a] += k * (sa - ea)
        r[b] += k * ((1 - sa) - (1 - ea))
    return r


def bradley_terry(ms, iters=200):
    p = dict.fromkeys(TRUE, 1.0)
    wins = {m: sum(w == m for _, _, w in ms) for m in TRUE}
    for _ in range(iters):
        new = {}
        for i in TRUE:
            den = 0.0
            for a, b, _ in ms:
                if i in (a, b):
                    j = b if i == a else a
                    den += 1 / (p[i] + p[j])
            new[i] = wins[i] / den
        s = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        p = {k: v / s for k, v in new.items()}
    return {k: math.log(v) for k, v in p.items()}


print("\n== 2. Рейтинги (настоящий порядок: A < B < C < D < E)")
r1 = elo(matches)
shuffled = matches[:]
random.Random(1).shuffle(shuffled)
r2 = elo(shuffled)
bt = bradley_terry(matches)
print(f"{'модель':10s} {'настоящая':>9s} {'Elo':>8s} {'Elo(другой порядок)':>20s} {'Bradley-Terry':>14s}")
for m in TRUE:
    print(f"{m:10s} {TRUE[m]:9.2f} {r1[m]:8.1f} {r2[m]:20.1f} {bt[m] - bt['модель-A']:14.2f}")
print("Elo зависит от порядка матчей: баллы в двух колонках различаются.")

print("\n== 3. Рост числа пар")
for n in (5, 10, 57, 100):
    print(f"{n:3d} моделей -> {n * (n - 1) // 2:5d} пар")
print(f"57 моделей, 244 000 сравнений: {244000 / (57 * 56 // 2):.0f} сравнений на пару")
