"""Лекция 6: метрики поиска NDCG@k, RR, recall@k, precision@k на одном примере."""
import math


def dcg(rels, k):
    # место i считаем с 1: вклад = rel / log2(i + 1)
    return sum(r / math.log2(i + 1) for i, r in enumerate(rels[:k], start=1))


def ndcg(rels, total_relevant, k):
    ideal = [1] * total_relevant + [0] * (k - total_relevant)
    return dcg(rels, k) / dcg(ideal, k)


def rr(rels):
    for i, r in enumerate(rels, start=1):
        if r:
            return 1 / i
    return 0.0


def recall(rels, total_relevant, k):
    return sum(rels[:k]) / total_relevant


def precision(rels, k):
    return sum(rels[:k]) / k


# 1 = чанк релевантен. Всего в базе релевантных чанков: 3
total = 3
runs = {
    "наша система": [0, 1, 1, 0, 0, 1],
    "идеальный порядок": [1, 1, 1, 0, 0, 0],
    "релевантные в конце": [0, 0, 0, 0, 1, 1],
}
k = 5
print(f"{'система':<22}{'NDCG@5':>8}{'RR':>7}{'recall@5':>10}{'prec@5':>8}")
for name, rels in runs.items():
    print(f"{name:<22}{ndcg(rels, total, k):>8.3f}{rr(rels):>7.2f}"
          f"{recall(rels, total, k):>10.2f}{precision(rels, k):>8.2f}")
