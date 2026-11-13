"""Глава 2: attention с нуля на чистом Python (без numpy). Маленькая модель: 5 токенов, d_model = 8, 2 головы.
Показывает: Q, K, V = x·W, softmax(Q·Kᵀ/√d)·V, маску будущих токенов, несколько голов, prefill и decode с KV cache.
Запуск: python3 -I scripts/ai-engineering-code/ch02_attention.py   (только стандартная библиотека)"""
import math
import random

rng = random.Random(0)
D_MODEL, HEADS = 8, 2
D_HEAD = D_MODEL // HEADS
TOKENS = ["Как", "дела", "?", "How", "are"]


def rand_matrix(rows, cols):
    return [[rng.uniform(-1, 1) for _ in range(cols)] for _ in range(rows)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transpose(a):
    return [list(r) for r in zip(*a)]


def softmax(row):
    m = max(row)
    e = [math.exp(x - m) for x in row]
    s = sum(e)
    return [x / s for x in e]


def attention(q, k, v, causal=True):
    """softmax(Q·Kᵀ / √d) · V. Если causal, токен не смотрит на будущие токены."""
    d = len(q[0])
    scores = [[x / math.sqrt(d) for x in row] for row in matmul(q, transpose(k))]
    if causal:
        for i, row in enumerate(scores):
            for j in range(len(row)):
                if j > i:
                    row[j] = float("-inf")  # будущее закрыто маской
    weights = [softmax(row) for row in scores]
    return matmul(weights, v), weights


def split_heads(m):
    return [[row[h * D_HEAD:(h + 1) * D_HEAD] for row in m] for h in range(HEADS)]


def show(m):
    for t, row in zip(TOKENS, m):
        print(f"  {t:5s}", " ".join(f"{x:5.2f}" for x in row))


x = rand_matrix(len(TOKENS), D_MODEL)  # embeddings токенов (случайные, для примера)
wq, wk, wv, wo = (rand_matrix(D_MODEL, D_MODEL) for _ in range(4))

print("== 1. Q, K, V = x · W (каждая матрица d_model × d_model)")
q, k, v = matmul(x, wq), matmul(x, wk), matmul(x, wv)
print(f"x: {len(x)}×{len(x[0])}, Q/K/V: {len(q)}×{len(q[0])}")

print("\n== 2. Веса внимания одной головы (строка = какой токен смотрит, столбец = на кого)")
qh, kh, vh = split_heads(q), split_heads(k), split_heads(v)
_, w = attention(qh[0], kh[0], vh[0])
print("      ", " ".join(f"{t:>5s}" for t in TOKENS))
for t, row in zip(TOKENS, w):
    print(f"  {t:5s}", " ".join(f"{a:5.2f}" for a in row), f"| сумма = {sum(row):.2f}")
print("Верхний правый треугольник равен 0: токены не видят будущее.")

print("\n== 3. Несколько голов: считаем отдельно, склеиваем и проецируем")
outs = [attention(qh[h], kh[h], vh[h])[0] for h in range(HEADS)]
concat = [outs[0][i] + outs[1][i] for i in range(len(TOKENS))]
y = matmul(concat, wo)
print(f"каждая голова даёт {len(outs[0])}×{len(outs[0][0])}, после склейки {len(concat)}×{len(concat[0])}, после Wo {len(y)}×{len(y[0])}")
show(y)

print("\n== 4. Размеры Llama 2-7B")
d, heads = 4096, 32
print(f"d_model = {d}, голов = {heads}, размер головы = {d} / {heads} = {d // heads}")
print(f"одна матрица Q, K, V или O: {d}×{d} = {d * d / 1e6:.1f} млн параметров, четыре матрицы: {4 * d * d / 1e6:.1f} млн на блок")

print("\n== 5. Prefill и decode с KV cache дают тот же результат, что полный пересчёт")
PROMPT = 4  # первые 4 токена — prompt, пятый «генерируем»
# полный пересчёт: все токены сразу
full_out = attention(qh[0], kh[0], vh[0])[0]
# prefill: K и V для prompt считаем один раз (параллельно) и кладём в кэш
cache_k = [kh[0][i] for i in range(PROMPT)]
cache_v = [vh[0][i] for i in range(PROMPT)]
computed_kv = PROMPT
# decode: новый токен считает только свои q, k, v и читает кэш
new_q, new_k, new_v = qh[0][PROMPT], kh[0][PROMPT], vh[0][PROMPT]
cache_k.append(new_k)
cache_v.append(new_v)
computed_kv += 1
out_cached, _ = attention([new_q], cache_k, cache_v, causal=False)
same = all(abs(a - b) < 1e-9 for a, b in zip(out_cached[0], full_out[PROMPT]))
print("выход последнего токена совпал с полным пересчётом:", same)
steps = 3  # сколько токенов дальше генерируем
no_cache = sum(range(PROMPT + 1, PROMPT + steps + 1))
print(f"сколько раз считаем K и V за {steps} шага decode: с кэшем {steps}, без кэша {no_cache} (каждый шаг заново для всех токенов)")
print(f"размер кэша растёт на 1 пару K, V на каждый токен: сейчас {len(cache_k)} пар")
