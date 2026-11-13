"""Глава 4: выбор модели. Три шага на выдуманных данных.
1) Hard attributes и жёсткие пороги: что отсеивает модели ещё до оценки качества.
2) Агрегация публичных benchmarks: среднее (как у Hugging Face) и mean win rate (как у HELM), корреляция benchmarks.
3) Свой leaderboard: веса benchmarks зависят от вашего приложения, и победитель меняется.
Названия моделей и все числа выдуманы. Запуск: python3 scripts/ai-engineering-code/ch04_model_selection.py
(только стандартная библиотека, Python 3.10+)"""
import random
from statistics import correlation, mean

# ---------- 1. hard attributes и жёсткие пороги ----------
# name, лицензия допускает коммерческое использование, где работает, $ за 1M output-токенов,
# TTFT P90 (мс), задержка запроса P90 (с), pass@1 на вашем наборе SQL-задач, factual consistency
MODELS = [
    ("api-large",  True,  "api",  30.0, 350, 20, 0.92, 0.91),
    ("api-medium", True,  "api",  10.0, 180, 9,  0.84, 0.86),
    ("api-small",  True,  "api",  1.5,  90,  4,  0.66, 0.78),
    ("open-70b",   True,  "self", 6.0,  190, 14, 0.82, 0.84),
    ("open-34b",   True,  "self", 3.0,  160, 8,  0.74, 0.81),
    ("open-8b",    True,  "self", 0.8,  70,  3,  0.58, 0.72),
    ("research-x", False, "self", 2.0,  120, 6,  0.80, 0.85),   # лицензия без коммерческого использования
]
# метрика: (индекс, жёсткий порог, идеал, True = чем меньше, тем лучше)
CRITERIA = {"цена за 1M токенов": (3, 20.0, 10.0, True), "TTFT P90, мс": (4, 200, 100, True),
            "латентность P90, с": (5, 15, 10, True), "SQL pass@1": (6, 0.75, 0.85, False),
            "factual consistency": (7, 0.80, 0.90, False)}


def passes(model, name):
    idx, hard, _, lower = CRITERIA[name]
    return model[idx] <= hard if lower else model[idx] >= hard


print("== 1a. Hard attributes: лицензия и «данные не уходят наружу»")
step_a = [m for m in MODELS if m[1]]
print("после лицензии:", [m[0] for m in step_a])
step_b = [m for m in step_a if m[2] == "self"]
print("после требования «данные остаются у нас»:", [m[0] for m in step_b])

print("\n== 1b. Жёсткие пороги по метрикам (без требования приватности)")
survivors = []
for m in step_a:
    failed = [n for n in CRITERIA if not passes(m, n)]
    print(f"{m[0]:11s} {'проходит' if not failed else 'отсеян: ' + ', '.join(failed)}")
    if not failed:
        survivors.append(m)
print("остались:", [m[0] for m in survivors])
print("Среди оставшихся выбираем по приоритетам: идеал по качеству или по цене.")

# ---------- 2. агрегация benchmarks ----------
BENCH = ["knowledge", "math", "truthful", "code"]
SCORES = {"M1": [80, 40, 50, 30], "M2": [70, 55, 52, 45], "M3": [60, 50, 55, 80],
          "M4": [65, 52, 48, 40], "M5": [75, 58, 54, 42]}


def mean_score(name):
    return mean(SCORES[name])


def mean_win_rate(name):
    rates = []
    for other in SCORES:
        if other != name:
            wins = sum(a > b for a, b in zip(SCORES[name], SCORES[other]))
            rates.append(wins / len(BENCH))
    return mean(rates)


print("\n== 2a. Среднее и mean win rate на одних и тех же оценках")
by_mean = sorted(SCORES, key=mean_score, reverse=True)
by_win = sorted(SCORES, key=mean_win_rate, reverse=True)
for name in SCORES:
    print(f"{name}: среднее {mean_score(name):5.2f}  mean win rate {mean_win_rate(name):.2f}")
print("ранг по среднему:     ", by_mean)
print("ранг по mean win rate:", by_win)

print("\n== 2b. Корреляция benchmarks на 40 моделях (искусственные данные)")
rng = random.Random(11)
rows = []
for _ in range(40):
    skill = rng.gauss(0, 1)      # общий «уровень рассуждений»
    honesty = rng.gauss(0, 1)    # отдельное свойство: правдивость
    rows.append([skill + rng.gauss(0, 0.35), skill + rng.gauss(0, 0.45),
                 0.7 * skill + 0.7 * honesty + rng.gauss(0, 0.3), skill * 0.9 + rng.gauss(0, 0.5)])
names = ["knowledge", "math", "truthful", "code"]
print("            " + "  ".join(f"{n:>9s}" for n in names))
for i, a in enumerate(names):
    cells = [correlation([r[i] for r in rows], [r[j] for r in rows]) for j in range(4)]
    print(f"{a:>10s}  " + "  ".join(f"{c:9.2f}" for c in cells))
print("knowledge и math связаны сильнее всего (0.89): второй из них почти не добавляет информации.")
print("truthful связан слабее всех: он измеряет другое, и его стоит оставить в наборе.")

# ---------- 3. свой leaderboard с весами ----------
def minmax(col):
    lo, hi = min(col), max(col)
    return [(v - lo) / (hi - lo) for v in col]


cols = [minmax([SCORES[m][i] for m in SCORES]) for i in range(len(BENCH))]
norm = {m: [cols[i][k] for i in range(len(BENCH))] for k, m in enumerate(SCORES)}
print("\n== 3. Свой leaderboard: шкалы приводим к 0..1 и задаём веса")
for title, w in [("универсальный чат", [0.4, 0.2, 0.3, 0.1]), ("ассистент по коду и SQL", [0.1, 0.2, 0.0, 0.7])]:
    score = {m: sum(a * b for a, b in zip(norm[m], w)) for m in SCORES}
    top = sorted(score, key=score.get, reverse=True)
    print(f"{title:24s} веса {w} -> " + ", ".join(f"{m} {score[m]:.2f}" for m in top))
