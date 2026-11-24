"""Выбор следующего токена: temperature, top-k, top-p и недетерминизм чисел с плавающей точкой."""
import numpy as np

tokens = ["читает", "спит", "милый", "зелёный", "кот"]
logits = np.array([2.0, 1.5, 1.0, 0.0, -1.0])


def softmax(z, t=1.0):
    e = np.exp((z - z.max()) / t)
    return e / e.sum()


print("temperature -> вероятности токенов")
for t in [0.3, 1.0, 3.0]:
    print(f"  T={t}:", np.round(softmax(logits, t), 3).tolist())

p = softmax(logits)
order = np.argsort(-p)
print("\ngreedy:", tokens[order[0]])


def top_k(p, k):
    keep = np.argsort(-p)[:k]
    out = np.zeros_like(p)
    out[keep] = p[keep]
    return out / out.sum()                           # оставляем k токенов и нормируем


def top_p(p, threshold):
    order = np.argsort(-p)
    cum = np.cumsum(p[order])
    n = int(np.searchsorted(cum, threshold) + 1)     # наименьший набор с суммой >= threshold
    out = np.zeros_like(p)
    out[order[:n]] = p[order[:n]]
    return out / out.sum()


print("top-k=2:", np.round(top_k(p, 2), 3).tolist())
print("top-p=0.9:", np.round(top_p(p, 0.9), 3).tolist())

rng = np.random.default_rng(42)
for name, dist in [("T=1", p), ("T=0.3", softmax(logits, 0.3)), ("T=3", softmax(logits, 3.0))]:
    draws = rng.choice(tokens, size=8, p=dist)
    print(f"8 выборок при {name}:", draws.tolist())

# Сложение чисел с плавающей точкой зависит от порядка
a = (1e16 + 1.0) - 1e16
b = 1.0 + (1e16 - 1e16)
print("\n(1e16 + 1) - 1e16 =", a, "; 1 + (1e16 - 1e16) =", b)
