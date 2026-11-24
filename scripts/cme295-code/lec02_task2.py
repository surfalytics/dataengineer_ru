"""Задача 2: top-p (nucleus) sampling руками."""
probs = {"кот": 0.45, "пёс": 0.25, "лис": 0.15, "ёж": 0.10, "краб": 0.05}


def nucleus(probs, threshold):
    result, total = {}, 0.0
    for token, p in sorted(probs.items(), key=lambda item: -item[1]):
        result[token] = p
        total += p
        if total >= threshold:                       # остановились, когда сумма дошла до порога
            break
    norm = sum(result.values())
    return {t: round(p / norm, 3) for t, p in result.items()}


print("top-p 0.7:", nucleus(probs, 0.7))
print("top-p 0.9:", nucleus(probs, 0.9))
