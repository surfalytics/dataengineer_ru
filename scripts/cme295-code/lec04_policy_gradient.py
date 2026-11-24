"""Градиент политики на игрушечной «модели»: три возможных ответа, softmax по logit."""
import numpy as np

rng = np.random.default_rng(0)


def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()


# Часть 1. Шум градиента без baseline и с baseline (пример 101 против 100 с лекции).
# Ответов два: хороший (reward около 101) и плохой (около 100). Начальная политика 50 на 50.
logits = np.zeros(2)
p = softmax(logits)
mean_reward = np.array([101.0, 100.0])
N = 20000
actions = rng.choice(2, size=N, p=p)
rewards = mean_reward[actions] + rng.normal(0, 0.5, size=N)   # небольшой шум оценки
# d log pi(a) / d logit_хорошего = 1[a == хороший] - p_хорошего
dlogp = (actions == 0).astype(float) - p[0]

for name, baseline in [("без baseline", 0.0), ("с baseline 100.5", 100.5)]:
    g = (rewards - baseline) * dlogp                           # оценка градиента по одному ответу
    print(f"{name:18s} среднее {g.mean():7.3f}  разброс (std) {g.std():7.3f}")

# Часть 2. Обучение REINFORCE с baseline: вероятность хорошего ответа растёт.
logits = np.zeros(3)                                          # три ответа: A хороший, B средний, C плохой
true_reward = np.array([1.0, 0.3, 0.0])
lr = 0.5
print("\nшаг   P(A)   P(B)   P(C)")
for step in range(201):
    p = softmax(logits)
    if step % 50 == 0:
        print(f"{step:3d}  {p[0]:.3f}  {p[1]:.3f}  {p[2]:.3f}")
    batch = rng.choice(3, size=16, p=p)                       # 16 ответов из текущей политики
    r = true_reward[batch]
    adv = r - r.mean()                                        # baseline: среднее по пачке
    grad = np.zeros(3)
    for a, A in zip(batch, adv):
        onehot = np.eye(3)[a]
        grad += A * (onehot - p)                              # A * grad log pi
    logits += lr * grad / len(batch)                          # градиентный подъём: плюс, не минус
