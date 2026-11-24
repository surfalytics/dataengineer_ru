"""LoRA: сколько параметров обучаем и почему выход сначала не меняется."""
import numpy as np

# 1. Считаем параметры одной матрицы весов
d_out, d_in, r = 4096, 4096, 8
full = d_out * d_in
lora = r * (d_out + d_in)                        # B: d_out x r, A: r x d_in
print("полная матрица  :", full)
print("LoRA (r=8)      :", lora)
print("доля обучаемого :", round(100 * lora / full, 2), "%")

# 2. Маленькая матрица, чтобы увидеть механику
rng = np.random.default_rng(0)
W0 = rng.normal(size=(6, 6))                     # готовые веса, заморожены
A = rng.normal(size=(2, 6)) * 0.1                # r = 2
B = np.zeros((6, 2))                             # B стартует с нуля
x = rng.normal(size=6)
print("старт: выход не изменился:", np.allclose(W0 @ x, (W0 + B @ A) @ x))

B = rng.normal(size=(6, 2)) * 0.1                # после «обучения» B стала ненулевой
delta = B @ A
print("ранг добавки B@A:", np.linalg.matrix_rank(delta), "из", delta.shape[0])
print("выход изменился :", not np.allclose(W0 @ x, (W0 + delta) @ x))

# 3. Хранение: один W0 и по паре (B, A) на задачу
tasks = ["spam", "sentiment", "translation"]
print("без LoRA хранить:", len(tasks) * full, "чисел")
print("с LoRA хранить  :", full + len(tasks) * lora, "чисел")
