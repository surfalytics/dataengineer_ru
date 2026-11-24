"""Задача 1: pass@1 и pass@5 по набору задач. Для каждой задачи сгенерировали n=20 решений."""
from math import comb


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


n = 20
successes = {"задача A": 20, "задача B": 12, "задача C": 5, "задача D": 0}   # c = сколько решений прошли тесты

for k in (1, 5):
    per_task = [pass_at_k(n, c, k) for c in successes.values()]
    print(f"pass@{k} по задачам:", [round(p, 3) for p in per_task], " среднее:", round(sum(per_task) / len(per_task), 3))
