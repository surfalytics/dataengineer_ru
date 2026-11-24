"""Позиция через синусы и через поворот: сходство зависит только от разницы позиций."""
import numpy as np


def sinusoid(m, d=8):
    pe = np.zeros(d)
    for i in range(d // 2):
        omega = 1 / 10000 ** (2 * i / d)            # низкий индекс i: высокая частота
        pe[2 * i] = np.sin(m * omega)
        pe[2 * i + 1] = np.cos(m * omega)
    return pe


print("Синусоидальный embedding: скалярное произведение позиций m и n")
for m, n in [(5, 5), (5, 6), (5, 10), (5, 50), (105, 110), (205, 210)]:
    print(f"  m={m:3d} n={n:3d} разница {abs(m - n):2d}: {sinusoid(m) @ sinusoid(n):6.3f}")


def rotate(v, pos, base=10000):
    """RoPE: каждую пару чисел вектора поворачиваем на угол pos * omega_i."""
    out = np.zeros_like(v)
    d = len(v)
    for i in range(d // 2):
        angle = pos * (1 / base ** (2 * i / d))
        c, s = np.cos(angle), np.sin(angle)
        a, b = v[2 * i], v[2 * i + 1]
        out[2 * i] = c * a - s * b
        out[2 * i + 1] = s * a + c * b
    return out


rng = np.random.default_rng(1)
q, key = rng.normal(size=8), rng.normal(size=8)

print()
print("RoPE: score = (повёрнутый query) @ (повёрнутый key)")
for m, n in [(3, 1), (13, 11), (103, 101), (7, 1), (107, 101)]:
    score = rotate(q, m) @ rotate(key, n)
    print(f"  query на {m:3d}, key на {n:3d}, разница {m - n}: {score:7.4f}")
