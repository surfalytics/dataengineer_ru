"""Self-attention на 4 токенах: scaled dot-product и causal mask. Веса не обучены, поэтому смысла в картинке нет."""
import numpy as np

rng = np.random.default_rng(0)
tokens = ["A", "cute", "teddy", "bear"]
n, d_model, d_k = len(tokens), 8, 4

X = rng.normal(size=(n, d_model))        # embedding токенов (позиции здесь опущены)
Wq = rng.normal(size=(d_model, d_k))     # проекции в query, key, value
Wk = rng.normal(size=(d_model, d_k))
Wv = rng.normal(size=(d_model, d_k))
Q, K, V = X @ Wq, X @ Wk, X @ Wv


def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def attention(Q, K, V, causal=False):
    scores = Q @ K.T / np.sqrt(d_k)                 # n x n: сходство query и key
    if causal:
        scores = np.where(np.triu(np.ones_like(scores), k=1) == 1, -np.inf, scores)
    weights = softmax(scores)                       # каждая строка даёт в сумме 1
    return weights, weights @ V                     # взвешенная сумма value


np.set_printoptions(precision=2, suppress=True)
w, out = attention(Q, K, V)
print("Веса self-attention (строка = токен-query):")
print(w)
print("Сумма по строкам:", w.sum(axis=1))
print("Форма выхода:", out.shape, "(по строке на токен, размер d_k)")

wc, _ = attention(Q, K, V, causal=True)
print("\nВеса с causal mask (токен не видит будущее):")
print(wc)
