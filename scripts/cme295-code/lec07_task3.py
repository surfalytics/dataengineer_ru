"""Задача 3: граница Парето по паре «цена за задачу — оценка качества»."""
models = {"A": (0.5, 40), "B": (1.0, 55), "C": (1.2, 50), "D": (3.0, 70), "E": (2.0, 70), "F": (8.0, 78)}


def dominated(m):
    cost, score = models[m]
    return any(c <= cost and s >= score and (c, s) != (cost, score) for c, s in models.values())


frontier = [m for m in models if not dominated(m)]
print("граница Парето:", sorted(frontier, key=lambda m: models[m][0]))
