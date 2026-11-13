"""Глава 7: model merging на игрушечных моделях.
Модель здесь это вектор весов линейного предсказателя y = x · w. Две задачи (A и B) дообучают одну
базовую модель. Потом мы сливаем модели: среднее, task vectors, вычитание, SLERP, pruning как в TIES,
LoRA concatenation и depth up-scaling (счёт слоёв).
Это модель для понимания идей, а не рецепт для LLM. Нужен numpy (см. requirements-ch07.txt).
Запуск: python3 -I scripts/ai-engineering-code/ch07_model_merging.py"""
import numpy as np

np.set_printoptions(precision=3, suppress=True, linewidth=120)
D = 60
SHARED, SA, SB = slice(0, 10), slice(10, 30), slice(30, 50)   # признаки: общие, только A, только B
gen = np.random.default_rng(5)

w0 = gen.normal(0, 0.5, D)                      # базовая модель
target_A, target_B = w0.copy(), w0.copy()       # «идеальные» модели для задач
target_A[SA] += gen.choice([-1.5, 0, 0, 1.5, 0.8], 20)
target_B[SB] += gen.choice([-1.5, 0, 0, 1.5, -0.8], 20)


def make_inputs(task, n):
    X = np.zeros((n, D))
    cols = np.r_[0:10, 10:30] if task == "A" else np.r_[0:10, 30:50]
    X[:, cols] = gen.normal(size=(n, len(cols)))
    return X


Xa_train, Xb_train = make_inputs("A", 200), make_inputs("B", 200)
Xa_test, Xb_test = make_inputs("A", 2000), make_inputs("B", 2000)
ya_clean, yb_clean = Xa_test @ target_A, Xb_test @ target_B


def finetune(X, target, seed, epochs=30, lr=0.01, label_noise=2.0):
    """Мини-батчевый SGD по шумным меткам. Из-за шума все активные веса немного «дрожат»."""
    g = np.random.default_rng(seed)
    y = X @ target + g.normal(0, label_noise, len(X))
    w = w0.copy()
    for _ in range(epochs):
        idx = g.permutation(len(X))
        for i in range(0, len(X), 20):
            b = idx[i:i + 20]
            w -= lr * 2 * X[b].T @ (X[b] @ w - y[b]) / len(b)
    return w


def mse(w):
    return (np.mean((Xa_test @ w - ya_clean) ** 2), np.mean((Xb_test @ w - yb_clean) ** 2))


wA = finetune(Xa_train, target_A, 1)
wB = finetune(Xb_train, target_B, 2)
dA, dB = wA - w0, wB - w0                      # task vectors (delta parameters)


def show(name, w):
    a, b = mse(w)
    print(f"{name:<44} {a:>8.2f} {b:>8.2f} {(a + b) / 2:>8.2f}")


print("== 1. Среднее и task vectors. Качество = ошибка MSE на тестах задач A и B (меньше лучше)")
print(f"{'модель':<44} {'MSE A':>8} {'MSE B':>8} {'среднее':>8}")
show("базовая модель", w0)
show("дообучена на A", wA)
show("дообучена на B", wB)
show("среднее весов: (A + B) / 2", (wA + wB) / 2)
show("взвешенное: 0.7 A + 0.3 B", 0.7 * wA + 0.3 * wB)
show("task arithmetic: base + dA + dB", w0 + dA + dB)
show("вычитание: base + dA - dB", w0 + dA - dB)
print("Среднее уменьшает обе правки вдвое. Сумма task vectors возвращает обе способности.")
print("Вычитание dB делает задачу B хуже, чем у базовой модели: способность сдвинулась в обратную сторону.")

print("\n== 2. Для линейной модели среднее весов и среднее ответов совпадают (ensembling = merging)")
x = gen.normal(size=D)
print(f"ensemble (2 вызова модели): {(x @ wA + x @ wB) / 2:.6f}; merge (1 вызов): {x @ ((wA + wB) / 2):.6f}")
print("У нейросети с нелинейностями результаты разные. Merge стоит дешевле: нужен один inference.")


def prune_top(delta, keep):
    """Оставляем долю `keep` самых больших по модулю изменений, остальные возвращаем к значениям базовой модели."""
    k = int(len(delta) * keep)
    out = np.zeros_like(delta)
    top = np.argsort(-np.abs(delta))[:k]
    out[top] = delta[top]
    return out


print("\n== 3. Лишние изменения: pruning task vectors как в TIES / DARE")
print(f"ненулевых значений в dA: {np.count_nonzero(np.abs(dA) > 1e-9)} из {D}; "
      f"значимых (|d| > 0.5): {np.count_nonzero(np.abs(dA) > 0.5)}")
print(f"{'способ':<44} {'MSE A':>8} {'MSE B':>8} {'среднее':>8}")
show("сумма task vectors, все изменения", w0 + dA + dB)
for keep in (0.5, 0.3, 0.2, 0.1):
    show(f"сумма, оставили топ-{keep:.0%} изменений", w0 + prune_top(dA, keep) + prune_top(dB, keep))
print("Большинство изменений мелкие. Общие признаки (первые 10) получают шум от обеих задач:")
print("после pruning этот шум пропадает, и слитая модель точнее. Слишком сильный pruning уже вредит.")

print("\n== 4. SLERP: путь по сфере сохраняет длину вектора, линейное среднее её сжимает")


def slerp(v0, v1, t):
    a, b = v0 / np.linalg.norm(v0), v1 / np.linalg.norm(v1)
    omega = np.arccos(np.clip(a @ b, -1, 1))
    if omega < 1e-8:
        return (1 - t) * v0 + t * v1
    return (np.sin((1 - t) * omega) * v0 + np.sin(t * omega) * v1) / np.sin(omega)


v1, v2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
print(f"{'t':>5} {'SLERP':>16} {'длина':>7} {'линейно':>16} {'длина':>7}")
for t in (0, 0.25, 0.5, 0.75, 1):
    s, lin = slerp(v1, v2, t), (1 - t) * v1 + t * v2
    print(f"{t:>5} {str(np.round(s, 3)):>16} {np.linalg.norm(s):>7.3f} {str(np.round(lin, 3)):>16} {np.linalg.norm(lin):>7.3f}")
angle = np.degrees(np.arccos(dA @ dB / np.linalg.norm(dA) / np.linalg.norm(dB)))
print(f"угол между task vectors dA и dB: {angle:.0f} градусов; "
      f"длина dA = {np.linalg.norm(dA):.2f}, dB = {np.linalg.norm(dB):.2f}")
print(f"SLERP(dA, dB, 0.5): длина {np.linalg.norm(slerp(dA, dB, 0.5)):.2f}; "
      f"линейное среднее: длина {np.linalg.norm((dA + dB) / 2):.2f}")
print("SLERP сливает только два вектора. Для трёх: сначала A и B, потом результат и C.")

print("\n== 5. LoRA concatenation: ранг растёт до r1 + r2, память не экономится")
n_, m_, r1, r2 = 16, 12, 2, 3
A1, B1 = gen.normal(size=(n_, r1)), gen.normal(size=(r1, m_))
A2, B2 = gen.normal(size=(n_, r2)), gen.normal(size=(r2, m_))
A_cat, B_cat = np.hstack([A1, A2]), np.vstack([B1, B2])
print(f"[A1 | A2] @ [B1 ; B2] == A1@B1 + A2@B2: {np.allclose(A_cat @ B_cat, A1 @ B1 + A2 @ B2)}")
print(f"ранг объединённого адаптера: {A_cat.shape[1]} = {r1} + {r2}")
print(f"параметров отдельно: {A1.size + B1.size + A2.size + B2.size}; после concatenation: {A_cat.size + B_cat.size}")
A3, B3 = gen.normal(size=(n_, r1)), gen.normal(size=(r1, m_))   # второй адаптер того же ранга r1
avg_AB = ((A1 + A3) / 2) @ ((B1 + B3) / 2)
print(f"усреднить A и B по отдельности НЕ равно усреднению правок: {not np.allclose(avg_AB, (A1 @ B1 + A3 @ B3) / 2)}")

print("\n== 6. Depth up-scaling: сколько слоёв получается")
layers, cut = 32, 8
stacked = (layers - cut) + (layers - cut)
print(f"две копии по {layers} слоя; у первой убрали {cut} верхних, у второй {cut} нижних")
print(f"итог: {layers - cut} + {layers - cut} = {stacked} слоёв (= {layers} x 2 - {2 * cut})")
print(f"оценка параметров для 7B: 7 x {stacked}/{layers} = {7 * stacked / layers:.1f}B "
      f"(у SOLAR 10.7B немного меньше: слой embeddings не дублируется)")
print("После такой «сшивки» модель нужно ещё дообучать (continued pre-training).")
