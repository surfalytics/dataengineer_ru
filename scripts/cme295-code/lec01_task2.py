"""Задача 2: синусоидальные position embedding. Близкие позиции похожи, далёкие нет."""
import numpy as np

d_model = 16


def pos_embedding(pos):
    i = np.arange(d_model // 2)
    freq = 1.0 / (10000 ** (2 * i / d_model))      # частоты от высокой к низкой, как стрелки часов
    return np.concatenate([np.sin(pos * freq), np.cos(pos * freq)])


def cos_sim(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


p10 = pos_embedding(10)
for other in [11, 12, 20, 100]:
    print(f"позиция 10 и {other}: cosine = {cos_sim(p10, pos_embedding(other)):.3f}")
