"""Самовнимание для одного токена «teddy bear» на пяти токенах. Векторы заданы вручную."""
import numpy as np

tokens = ["a", "cute", "teddy bear", "is", "reading"]
d_k = 2

# key каждого токена (по строке на токен) и value, размер 2
K = np.array([[0.1, 0.2], [1.5, 0.5], [0.8, 0.9], [0.0, 0.3], [0.3, -0.2]])
V = np.array([[1.0, 0.0], [0.0, 3.0], [2.0, 2.0], [0.0, 1.0], [1.0, 1.0]])
q = np.array([2.0, 0.5])                 # query токена «teddy bear»

scores = K @ q                           # скалярное произведение query и каждого key
scaled = scores / np.sqrt(d_k)           # делим на sqrt(d_k)
e = np.exp(scaled - scaled.max())
weights = e / e.sum()                    # softmax: веса с суммой 1
out = weights @ V                        # сумма value с этими весами

print("токен        score  /sqrt(d_k)  вес")
for t, s, c, w in zip(tokens, scores, scaled, weights):
    print(f"{t:<12} {s:5.2f}  {c:9.2f}  {w:6.2f}")
print("Сумма весов:", round(float(weights.sum()), 2))
print("Новое представление teddy bear:", np.round(out, 2))
