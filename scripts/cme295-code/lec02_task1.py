"""Задача 1: сколько токенов на параметр и хватает ли данных."""
models = {"A": (7e9, 140e9), "B": (175e9, 300e9), "C": (13e9, 2.6e12)}   # параметры, токены

for name, (params, tokens) in models.items():
    ratio = tokens / params
    if ratio < 10:
        verdict = "недообучена"
    elif ratio > 40:
        verdict = "обучена с запасом данных"
    else:
        verdict = "близко к Chinchilla"
    print(f"{name}: токенов на параметр {ratio:.0f}: {verdict}")
