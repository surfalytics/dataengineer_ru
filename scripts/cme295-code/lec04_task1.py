"""Задача 1: преимущество по группе ответов (GRPO)."""
import numpy as np


def advantages(rewards):
    r = np.array(rewards, dtype=float)
    std = r.std()
    if std == 0:                       # все ответы одинаковы: сигнала нет
        return np.zeros_like(r)
    return (r - r.mean()) / std


print(np.round(advantages([1, 0, 0, 1, 1, 0, 0, 0]), 2))
print(np.round(advantages([0, 0, 0, 0]), 2))
print(np.round(advantages([1, 0, 0, 0]), 2))
