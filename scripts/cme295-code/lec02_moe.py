"""Sparse MoE на numpy: маршрутизатор выбирает top-k экспертов для каждого токена."""
import numpy as np

rng = np.random.default_rng(0)
n_tokens, d, n_experts, k = 8, 4, 4, 2

x = rng.normal(size=(n_tokens, d))                  # 8 токенов, вектор из 4 чисел
w_gate = rng.normal(size=(d, n_experts))            # маршрутизатор: одна матрица
experts = rng.normal(size=(n_experts, d, d))        # эксперт: матрица d x d вместо feedforward


def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


probs = softmax(x @ w_gate)                         # P: вероятность каждого эксперта для токена
top = np.argsort(-probs, axis=1)[:, :k]             # индексы k лучших экспертов

y = np.zeros_like(x)
for t in range(n_tokens):
    w = probs[t, top[t]]
    w = w / w.sum()                                 # веса выбранных экспертов в сумме дают 1
    for weight, e in zip(w, top[t]):
        y[t] += weight * (x[t] @ experts[e])        # считаем только k экспертов из 4

print("Эксперты по токенам:", top.tolist())
print("Активно параметров экспертов:", k, "из", n_experts)

# Load balancing loss: n * сумма f_i * P_i
counts = np.bincount(top.ravel(), minlength=n_experts)
f = counts / counts.sum()                           # доля обращений к каждому эксперту
p = probs.mean(axis=0)                              # средняя вероятность каждого эксперта
print("f:", np.round(f, 2).tolist(), " P:", np.round(p, 2).tolist())
print("loss на этих данных:", round(float(n_experts * (f * p).sum()), 3))

uniform = np.full(n_experts, 1 / n_experts)
collapse = np.array([0.97, 0.01, 0.01, 0.01])
print("loss при равной загрузке:", round(float(n_experts * (uniform * uniform).sum()), 3))
print("loss при routing collapse:", round(float(n_experts * (collapse * collapse).sum()), 3))
