"""Глава 7: математика LoRA на маленьких матрицах.
1) low-rank факторизация, 2) W' = W + (alpha/r) * A @ B на матрице 4x4, 3) обучаем только A и B
на игрушечной задаче и сравниваем rank 1/2/4/8 с полным finetuning, 4) merge без лишней latency,
5) multi-LoRA: хранение 100 адаптеров, 6) подсчёт параметров для GPT-3 и Llama 2.
Нужен numpy (см. requirements-ch07.txt).
Запуск: python3 -I scripts/ai-engineering-code/ch07_lora_math.py"""
import numpy as np

rng = np.random.default_rng(42)
np.set_printoptions(precision=2, suppress=True, linewidth=120)

print("== 1. Low-rank факторизация: матрица 9x9 как произведение 9x1 и 1x9")
u, v = rng.integers(1, 4, 9), rng.integers(1, 4, 9)
M = np.outer(u, v).astype(float)          # матрица ранга 1
print(f"параметров в матрице: {M.size}; в двух множителях: {u.size + v.size}")
print("ранг матрицы:", np.linalg.matrix_rank(M), "-> множители восстанавливают её точно:", np.allclose(M, np.outer(u, v)))

R = rng.normal(size=(9, 9))               # обычная матрица: полный ранг, факторизация с потерей
U, S, Vt = np.linalg.svd(R)
print("\nПриближение случайной матрицы 9x9 рангом r (лучшее по SVD). Чем выше r, тем меньше потеря:")
print(f"{'r':>2} {'параметров':>11} {'ошибка':>8}")
for r in (1, 2, 3, 5, 9):
    approx = (U[:, :r] * S[:r]) @ Vt[:r]
    err = np.linalg.norm(R - approx) / np.linalg.norm(R)
    print(f"{r:>2} {r * 18:>11} {err:>8.1%}")

print("\n== 2. LoRA на матрице 4x4: W' = W + (alpha / r) * A @ B")
n = m = 4
r, alpha = 1, 2
W = rng.integers(-3, 4, (n, m)).astype(float)
A = rng.integers(-1, 2, (n, r)).astype(float)       # n x r
B = rng.integers(-1, 2, (r, m)).astype(float)       # r x m
W_new = W + (alpha / r) * (A @ B)
print("W (заморожена):\n", W)
print("A (n x r) =", A.ravel(), "; B (r x m) =", B.ravel())
print("(alpha/r) * A @ B (добавка того же размера, что W):\n", (alpha / r) * (A @ B))
print("W' = W + добавка:\n", W_new)
print(f"обучаем {A.size + B.size} параметров вместо {W.size}")

print("\n== 3. Обучаем только A и B. Игрушечная задача: нужная правка матрицы имеет ранг 3")
n = m = 64
W0 = rng.normal(0, 0.5, (n, m))                              # «предобученная» матрица, заморожена
true_delta = rng.normal(size=(n, 3)) @ rng.normal(size=(3, m)) * 0.15   # что нужно изменить: ранг 3
X = rng.normal(size=(512, n))
Y = X @ (W0 + true_delta)                                    # целевые выходы
base_loss = np.mean((X @ W0 - Y) ** 2)


def adam_step(p, g, state, lr=0.02, b1=0.9, b2=0.999, eps=1e-8):
    state["t"] += 1
    state["m"] = b1 * state["m"] + (1 - b1) * g
    state["v"] = b2 * state["v"] + (1 - b2) * g * g
    mh, vh = state["m"] / (1 - b1 ** state["t"]), state["v"] / (1 - b2 ** state["t"])
    return p - lr * mh / (np.sqrt(vh) + eps)


def new_state(shape):
    return {"t": 0, "m": np.zeros(shape), "v": np.zeros(shape)}


def train_lora(rank, alpha_ratio=1.0, steps=1500):
    gen = np.random.default_rng(rank)
    A = gen.normal(0, 0.05, (n, rank))     # как в LoRA: A случайная, B нулевая, добавка в начале равна нулю
    B = np.zeros((rank, m))
    s = alpha_ratio                        # s = alpha / r
    sa, sb = new_state(A.shape), new_state(B.shape)
    for _ in range(steps):
        E = X @ (W0 + s * A @ B) - Y
        G = s * (2 / E.size) * X.T @ E     # градиент по произведению A @ B
        A, B = adam_step(A, G @ B.T, sa), adam_step(B, A.T @ G, sb)
    return A, B, np.mean((X @ (W0 + s * A @ B) - Y) ** 2)


def train_full(steps=1500):
    D = np.zeros((n, m))
    st = new_state(D.shape)
    for _ in range(steps):
        E = X @ (W0 + D) - Y
        D = adam_step(D, (2 / E.size) * X.T @ E, st)
    return D, np.mean((X @ (W0 + D) - Y) ** 2)


print(f"ошибка до finetuning (MSE): {base_loss:.4f}")
print(f"{'способ':<22} {'trainable':>10} {'доля от полного':>16} {'MSE после':>10} {'убрано ошибки':>14}")
_, full_loss = train_full()
print(f"{'полный finetuning':<22} {n * m:>10} {1:>16.1%} {full_loss:>10.5f} {1 - full_loss / base_loss:>14.1%}")
trained = {}
for rank in (1, 2, 3, 4, 8):
    A_, B_, loss = train_lora(rank)
    trained[rank] = (A_, B_)
    cnt = A_.size + B_.size
    print(f"{'LoRA r=' + str(rank):<22} {cnt:>10} {cnt / (n * m):>16.1%} {loss:>10.5f} {1 - loss / base_loss:>14.1%}")
print("Нужная правка имеет ранг 3. При r=1 и r=2 её не хватает. При r>=3 LoRA догоняет полный finetuning.")
print("Рост r с 3 до 8 увеличивает параметры почти втрое, но ничего не даёт.")

print("\n== 4. Merge: W' = W + s*A@B даёт тот же выход, что и раздельный путь, но без лишних операций")
A4, B4 = trained[4]  # берём r=4
x = rng.normal(size=(1, n))
merged = x @ (W0 + A4 @ B4)
separate = x @ W0 + (x @ A4) @ B4
print("merged == separate:", np.allclose(merged, separate))
r4 = 4
print(f"умножений на один вход: только W = {n * m}; раздельный путь = {n * m + n * r4 + r4 * m} "
      f"(+{(n * r4 + r4 * m) / (n * m):.0%}); после merge = {n * m}")
delta = A4 @ B4
print(f"норма добавки ||A@B|| составляет {np.linalg.norm(delta) / np.linalg.norm(W0):.0%} от нормы ||W||")

print("\n== 5. Multi-LoRA: 100 клиентов на одной базовой матрице 4096 x 4096, r = 8")
d, rank, clients = 4096, 8, 100
full_w = d * d
lora = d * rank * 2
print(f"W: {full_w:,} параметров; A и B вместе: {lora:,}")
print(f"вариант 1, 100 слитых W': {full_w * clients:,} параметров = {full_w * clients * 2 / 1e9:.2f} ГБ в 16 бит")
print(f"вариант 2, одна W + 100 адаптеров: {full_w + lora * clients:,} параметров = {(full_w + lora * clients) * 2 / 1e9:.3f} ГБ")
print(f"экономия памяти: x{full_w * clients / (full_w + lora * clients):.0f}")

print("\n== 6. Сколько trainable-параметров у LoRA в больших моделях")


def lora_count(layers, d_model, rank, matrices):
    return layers * matrices * 2 * d_model * rank


gpt3 = dict(layers=96, d_model=12288, total=175e9)
print("GPT-3 175B, один и тот же бюджет разными способами:")
for label, rank, mats in [("1 матрица, r=8", 8, 1), ("2 матрицы, r=4", 4, 2), ("4 матрицы, r=2", 2, 4)]:
    c = lora_count(gpt3["layers"], gpt3["d_model"], rank, mats)
    print(f"  {label:<16} -> {c:>10,} параметров = {c / gpt3['total']:.4%} модели")
print(f"  в книге для GPT-3 упомянуто 4,7M trainable: {4.7e6 / gpt3['total']:.4%} модели")
llama13 = dict(layers=40, d_model=5120, total=13e9)
for label, mats in [("Wq и Wk", 2), ("Wq, Wk, Wv, Wo", 4)]:
    c = lora_count(llama13["layers"], llama13["d_model"], 2, mats)
    print(f"Llama 2 13B, r=2, {label:<15}: {c:>9,} параметров = {c * 2 / 1e6:.2f} МБ в 16 бит "
          f"(модель: {llama13['total'] * 2 / 1e9:.0f} ГБ, адаптер = {c * 2 / (llama13['total'] * 2):.3%})")
