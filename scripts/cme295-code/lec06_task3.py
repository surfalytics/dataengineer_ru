"""Задача 3: MRR и recall@3 по трём запросам."""
# для каждого запроса: релевантность найденных чанков по местам (1 = релевантен) и число всех релевантных в базе
queries = [
    ([0, 1, 0, 0], 1),
    ([1, 0, 1, 0], 3),
    ([0, 0, 0, 1], 2),
]


def rr(rels):
    return next((1 / i for i, r in enumerate(rels, 1) if r), 0.0)


mrr = sum(rr(r) for r, _ in queries) / len(queries)
rec3 = sum(sum(r[:3]) / total for r, total in queries) / len(queries)
print(f"MRR = {mrr:.3f}")
print(f"recall@3 = {rec3:.3f}")
