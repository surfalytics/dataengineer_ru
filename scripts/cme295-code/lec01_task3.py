"""Задача 3: зачем делить на sqrt(d_k). Без деления softmax становится почти one-hot."""
import numpy as np

rng = np.random.default_rng(1)
n = 6                                    # токенов в тексте


def softmax(s):
    e = np.exp(s - s.max())
    return e / e.sum()


for d_k in [4, 256]:
    q = rng.normal(size=d_k)
    K = rng.normal(size=(n, d_k))
    raw = K @ q
    print(f"d_k={d_k}")
    print("  разброс (std) скалярных произведений:", round(float(np.std(raw)), 2))
    print("  максимальный вес без деления:        ", round(float(softmax(raw).max()), 2))
    print("  максимальный вес с делением:         ", round(float(softmax(raw / np.sqrt(d_k)).max()), 2))
