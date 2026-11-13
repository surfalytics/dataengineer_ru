"""Глава 4: хватает ли примеров в evaluation set.
1) Bootstrap: тянем выборки с возвратом и смотрим, как скачет score. Чем меньше набор, тем больше разброс.
2) Сколько примеров нужно, чтобы поверить в разницу между двумя prompts. Формула и правило «разница в 3 раза меньше — примеров в 10 раз больше».
3) Шум: как часто бесполезное изменение выглядит как улучшение на малом наборе.
Данные генерируются с фиксированным seed. Запуск: python3 scripts/ai-engineering-code/ch04_bootstrap_sample_size.py
(только стандартная библиотека)"""
import random
from statistics import mean, pstdev

rng = random.Random(2024)

# ---------- 1. bootstrap ----------
def make_outcomes(n, p):
    return [1 if rng.random() < p else 0 for _ in range(n)]   # 1 = модель ответила верно


def bootstrap_scores(outcomes, rounds=1000):
    n = len(outcomes)
    return sorted(mean(rng.choices(outcomes, k=n)) for _ in range(rounds))   # k=n, с возвратом


print("== 1. Bootstrap: 1000 выборок с возвратом из eval set")
for n in (20, 100, 1000):
    outcomes = make_outcomes(n, 0.75)
    s = bootstrap_scores(outcomes)
    lo, hi = s[int(0.025 * len(s))], s[int(0.975 * len(s))]
    print(f"eval set {n:4d}: score {mean(outcomes):.2f}, разброс от {s[0]:.2f} до {s[-1]:.2f}, "
          f"95% интервал {lo:.2f}-{hi:.2f}, std {pstdev(s):.3f}")
print("Набор из 20 примеров даёт и 55%, и 95%: ему нельзя верить. Набору из 1000 примеров можно.")

# ---------- 2. сколько примеров нужно ----------
Z_95 = 1.645   # односторонний уровень 95%: «новая версия лучше»


def needed_n(diff, p=0.5):
    """Грубая оценка для двух долей около p: n = z^2 * (дисперсия A + дисперсия B) / diff^2."""
    var = p * (1 - p) * 2
    return Z_95 ** 2 * var / diff ** 2


print("\n== 2. Сколько примеров нужно, чтобы заметить разницу score (95% уверенности)")
print(f"{'разница':>8} {'по формуле':>11} {'таблица OpenAI':>15}")
book = {0.30: "~10", 0.10: "~100", 0.03: "~1 000", 0.01: "~10 000"}
for d in (0.30, 0.10, 0.03, 0.01):
    print(f"{d:8.0%} {needed_n(d):11,.0f} {book[d]:>15}")
print(f"разница в 3 раза меньше -> примеров в {needed_n(0.03) / needed_n(0.10):.0f} раз больше (n растёт как 1/разница²)")

# ---------- 3. шум на малом наборе ----------
def measured_diff(n, p_old, p_new):
    old = sum(rng.random() < p_old for _ in range(n)) / n
    new = sum(rng.random() < p_new for _ in range(n)) / n
    return new - old


print("\n== 3. Шум: обе версии одинаково хороши (70%), набор из 100 примеров, 2000 повторов")
diffs = [measured_diff(100, 0.70, 0.70) for _ in range(2000)]
fake_gain = sum(d >= 0.05 for d in diffs) / len(diffs)
print(f"в {fake_gain:.0%} случаев «новая версия» выглядит лучше на 5 пунктов и больше, хотя разницы нет")

print("\n== 4. Мощность: настоящая разница 10 пунктов (60% против 70%), как часто тест это замечает")
for n in (30, 100, 300):
    wins = 0
    for _ in range(600):
        a = sum(rng.random() < 0.60 for _ in range(n))
        b = sum(rng.random() < 0.70 for _ in range(n))
        pa, pb = a / n, b / n
        pooled = (a + b) / (2 * n)
        se = (2 * pooled * (1 - pooled) / n) ** 0.5
        wins += (pb - pa) / se > Z_95
    print(f"n={n:3d}: разницу видим в {wins / 600:.0%} запусков")
