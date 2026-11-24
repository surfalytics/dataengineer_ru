"""GRPO: преимущество по группе ответов и смещение к длинным ответам."""
import numpy as np


def group_advantages(rewards, eps=1e-8):
    r = np.array(rewards, dtype=float)
    return (r - r.mean()) / (r.std() + eps)                   # (reward - среднее группы) / std группы


# Часть 1. Группа из 6 ответов на один prompt: 1 = верно, 0 = неверно.
rewards = [1, 0, 0, 1, 0, 0]
print("rewards   ", rewards)
print("advantages", np.round(group_advantages(rewards), 2))

# Если все ответы одинаковы, сигнала нет: преимущество равно 0.
print("все верные", np.round(group_advantages([1, 1, 1, 1, 1, 1]), 2))

# Часть 2. Вес одного токена в цели при разной нормализации.
# Два ответа с одним и тем же преимуществом: короткий (10 токенов) и длинный (100 токенов).
lengths = np.array([10, 100])
print("\nвес одного токена (умножается на преимущество):")
print("GRPO, 1/|o|       :", 1 / lengths)
print("DAPO, 1/(сумма |o|):", np.round(np.full(2, 1 / lengths.sum()), 4))
print("Dr. GRPO, без нормы:", np.ones(2))

A = -1.0                                                      # оба ответа плохие
print("\nштраф на токен плохого ответа при 1/|o|:", A / lengths)
print("весь ответ целиком при 1/|o|          :", A / lengths * lengths)
