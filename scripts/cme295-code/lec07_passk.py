"""pass@k: несмещённая оценка по n попыткам, из которых c успешных. И consensus@k."""
from collections import Counter
from math import comb

import numpy as np


def pass_at_k(n, c, k):
    if n - c < k:                      # неудач меньше k: среди k попыток успех гарантирован
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


n, c = 10, 3
rng = np.random.default_rng(0)
results = np.array([1] * c + [0] * (n - c))
order = rng.random((100_000, n)).argsort(axis=1)           # 100 000 случайных перестановок
print("k   формула   наивно   симуляция")
for k in (1, 3, 5):
    exact = pass_at_k(n, c, k)
    naive = 1 - ((n - c) / n) ** k                         # так было бы с возвращением
    sim = results[order[:, :k]].max(axis=1).mean()         # берём k попыток без возвращения
    print(f"{k}   {exact:.4f}    {naive:.4f}   {sim:.4f}")

answers = ["6", "6", "5", "6", "7"]                        # пять ответов модели на задачу по математике
print("consensus@5:", Counter(answers).most_common(1)[0][0])
