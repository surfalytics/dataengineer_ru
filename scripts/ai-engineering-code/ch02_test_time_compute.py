"""Глава 2: test-time compute. Вероятность последовательности, средний logprob, голосование (self-consistency)
и best of N с несовершенным verifier. Модель и verifier здесь игрушечные: настоящий вызов модели
заменит функции mock_model и verifier_score. Числа показывают механизм, а не данные OpenAI.
Запуск: python3 -I scripts/ai-engineering-code/ch02_test_time_compute.py   (только стандартная библиотека)"""
import math
import random
from collections import Counter

print("== 1. Вероятность последовательности = произведение вероятностей токенов")
tokens = [("Я", 0.2), ("люблю", 0.1), ("есть", 0.3)]
p = 1.0
lp = 0.0
for w, x in tokens:
    p *= x
    lp += math.log(x)
print("токены:", [w for w, _ in tokens], "вероятности:", [x for _, x in tokens])
print(f"p = {p:.3f}, logprob = {lp:.3f}, exp(logprob) = {math.exp(lp):.3f}  (логарифм произведения = сумма логарифмов)")

print("\n== 2. Чем выбирать: суммой или средним logprob")
cands = {"короткий ответ (2 токена)": [0.5, 0.4], "длинный ответ (5 токенов)": [0.6, 0.7, 0.8, 0.6, 0.7]}
for name, ps in cands.items():
    total = sum(math.log(x) for x in ps)
    print(f"{name}: сумма logprob = {total:6.3f}, средний logprob = {total / len(ps):6.3f}")
best_sum = max(cands, key=lambda k: sum(math.log(x) for x in cands[k]))
best_avg = max(cands, key=lambda k: sum(math.log(x) for x in cands[k]) / len(cands[k]))
print("по сумме выигрывает:", best_sum)
print("по среднему выигрывает:", best_avg)

print("\n== 3. Self-consistency: самый частый ответ из N (500 вопросов, seed = 1)")
rng = random.Random(1)
ANSWERS = ["42", "41", "43", "44", "40"]
WEIGHTS = [0.45, 0.20, 0.15, 0.12, 0.08]  # верный ответ "42" модель даёт в 45% случаев


def mock_model():
    return rng.choices(ANSWERS, weights=WEIGHTS)[0]


for n in (1, 3, 5, 11, 32):
    ok = 0
    for _ in range(500):
        votes = Counter(mock_model() for _ in range(n))
        ok += votes.most_common(1)[0][0] == "42"
    print(f"N = {n:2d}: точность {ok / 500:5.1%}, цена ×{n}")

print("\n== 4. Best of N с несовершенным verifier (200 повторов, seed = 7)")
rng = random.Random(7)
P_TRICK = 0.0005  # доля ответов, которые обманывают verifier


def candidate():
    """Возвращает (настоящее качество, оценка verifier)."""
    if rng.random() < P_TRICK:  # «обманный» ответ: качество плохое, оценка очень высокая
        return -2.0, 5.0 + rng.gauss(0, 0.5)
    q = rng.gauss(0, 1)
    return q, q + rng.gauss(0, 0.7)  # verifier видит качество с шумом


print("   N   среднее настоящее качество выбранного ответа")
for n in (1, 4, 16, 64, 256, 1024, 4096):
    total = 0.0
    for _ in range(200):
        pool = [candidate() for _ in range(n)]
        total += max(pool, key=lambda c: c[1])[0]
    print(f"{n:5d}   {total / 200:6.2f}")
