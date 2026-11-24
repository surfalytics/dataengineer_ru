"""Bradley-Terry: вероятность предпочтения и обучение маленькой модели вознаграждения."""
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# 1. Чем больше разница вознаграждений, тем увереннее предпочтение
print("r_w - r_l | P(y_w лучше) | loss = -ln P")
for diff in [-2.0, 0.0, 1.0, 3.0]:
    p = sigmoid(diff)
    print(f"{diff:9.1f} | {p:12.3f} | {-np.log(p):.3f}")

# 2. Модель вознаграждения: r = w · признаки ответа
rng = np.random.default_rng(7)
w_true = np.array([2.0, 1.0, -1.0])              # вкус «людей»: полезность, вежливость, лишняя длина
n = 400
a = rng.normal(size=(n, 3))                      # признаки первого ответа пары
b = rng.normal(size=(n, 3))                      # признаки второго ответа пары
a_wins = rng.random(n) < sigmoid((a - b) @ w_true)
win = np.where(a_wins[:, None], a, b)            # победитель и проигравший
lose = np.where(a_wins[:, None], b, a)

w = np.zeros(3)
def accuracy(w):
    d = (win - lose) @ w                         # при равенстве считаем «угадал в половине случаев»
    return float(np.mean((d > 0) + 0.5 * (d == 0)))

print("точность до обучения :", round(accuracy(w), 3))
for step in range(300):
    diff = (win - lose) @ w
    grad = -((1 - sigmoid(diff))[:, None] * (win - lose)).mean(axis=0)   # градиент -ln sigmoid(diff)
    w -= 0.5 * grad
print("точность после       :", round(accuracy(w), 3))
print("веса модели          :", np.round(w, 2))
