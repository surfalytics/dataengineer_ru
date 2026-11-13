"""Глава 9: KV cache. Формула размера, влияние batch и длины, приёмы сжатия и крошечный attention с кэшем и без.
Из книги: размер KV cache без оптимизаций = 2 * B * S * L * H * M, пример Llama 2 13B (L = 40, H = 5120).
Наши добавления: число голов Llama 2 13B (40) и проверка, что кэш не меняет ответ модели.
Запуск: python3 scripts/ai-engineering-code/ch09_kv_cache.py   (только стандартная библиотека)"""
import math
import random

GB = 1e9


def kv_bytes(batch, seq, layers, hidden, bytes_per_value):
    """2 (key и value) * B * S * L * H * M."""
    return 2 * batch * seq * layers * hidden * bytes_per_value


L13, H13, M16 = 40, 5120, 2   # Llama 2 13B: слоёв, размерность модели; FP16 = 2 байта
WEIGHTS_13B = 13e9 * 2        # веса в FP16

print("== 1. Формула из книги: Llama 2 13B, batch 32, длина 2048, FP16")
size = kv_bytes(32, 2048, L13, H13, M16)
print(f"2 * 32 * 2048 * 40 * 5120 * 2 = {size:,} байт = {size / GB:.1f} GB".replace(",", " "))
print(f"веса модели в FP16: {WEIGHTS_13B / GB:.0f} GB, то есть кэш в {size / WEIGHTS_13B:.1f} раза больше весов")

print("\n== 2. Кэш растёт линейно по длине и по batch (Llama 2 13B, FP16)")
print(f"{'длина':>7}{'batch 1, GB':>13}{'batch 32, GB':>14}")
for seq in (512, 2048, 8192, 32768):
    print(f"{seq:>7}{kv_bytes(1, seq, L13, H13, M16) / GB:>13.2f}{kv_bytes(32, seq, L13, H13, M16) / GB:>14.1f}")

print("\n== 3. Сколько запросов помещается в GPU на 80 GB")
gpu = 80e9
per_request = kv_bytes(1, 2048, L13, H13, M16)
free = gpu - WEIGHTS_13B
print(f"после весов (26 GB) остаётся {free / GB:.0f} GB; на один запрос длиной 2048 нужно {per_request / GB:.2f} GB")
print(f"запросов в batch: примерно {int(free // per_request)}; при длине 8192: примерно {int(free // (4 * per_request))}")
print("Длинный контекст прямо уменьшает размер batch, а значит throughput.")

print("\n== 4. Приёмы, которые уменьшают кэш (множитель к размеру)")
heads = 40
tricks = [
    ("окно 1 000 токенов вместо 10 000 (local attention)", 1000 / 10000),
    ("multi-query attention: один набор K/V на все 40 голов", 1 / heads),
    ("grouped-query attention: 8 групп вместо 40 голов", 8 / heads),
    ("cross-layer attention: 3 соседних слоя делят K/V", 1 / 3),
    ("KV cache в INT8 вместо FP16", 1 / 2),
]
base = kv_bytes(32, 2048, L13, H13, M16)
for name, factor in tricks:
    print(f"{name:<54} x{factor:.3f} -> {base * factor / GB:>5.1f} GB (кэш меньше: ×{1 / factor:.0f})")
combo = (8 / heads) * (1 / 3)
print(f"grouped-query + cross-layer вместе: x{combo:.3f} (кэш меньше: ×{1 / combo:.0f}). Character.AI заявляет больше ×20 тремя приёмами")

print("\n== 5. Крошечный attention: кэш не меняет ответ, но убирает пересчёт")
V, D = 12, 8
rng = random.Random(17)


def mat(rows, cols):
    return [[rng.gauss(0, 1) for _ in range(cols)] for _ in range(rows)]


E, P = mat(V, D), mat(64, D)   # embedding токена и вектор позиции
Wq, Wk, Wv, Wo = mat(D, D), mat(D, D), mat(D, D), mat(D, V)


def embed(token, pos):
    return [e + p for e, p in zip(E[token], P[pos])]


def vecmat(v, m):
    return [sum(v[i] * m[i][j] for i in range(len(v))) for j in range(len(m[0]))]


def next_token(context, cache, counters):
    """Один шаг: attention последнего токена по всем токенам контекста."""
    if cache is None:                                   # без кэша: считаем K и V для всего контекста заново
        keys = [vecmat(embed(t, i), Wk) for i, t in enumerate(context)]
        vals = [vecmat(embed(t, i), Wv) for i, t in enumerate(context)]
        counters["kv"] += len(context)
    else:                                               # с кэшем: считаем только то, чего ещё нет
        for i in range(len(cache["k"]), len(context)):
            cache["k"].append(vecmat(embed(context[i], i), Wk))
            cache["v"].append(vecmat(embed(context[i], i), Wv))
            counters["kv"] += 1
        keys, vals = cache["k"], cache["v"]
    q = vecmat(embed(context[-1], len(context) - 1), Wq)
    scores = [sum(a * b for a, b in zip(q, k)) / math.sqrt(D) for k in keys]
    counters["dots"] += len(scores)
    mx = max(scores)
    w = [math.exp(s - mx) for s in scores]
    z = sum(w)
    h = [sum(w[i] / z * vals[i][j] for i in range(len(vals))) for j in range(D)]
    logits = vecmat(h, Wo)
    return max(range(V), key=lambda i: logits[i])


def generate(prompt, steps, use_cache):
    counters = {"kv": 0, "dots": 0}
    cache = {"k": [], "v": []} if use_cache else None
    seq = list(prompt)
    for _ in range(steps):
        seq.append(next_token(seq, cache, counters))
    return seq, counters


prompt, steps = [3, 1, 4, 1, 5], 40
a, ca = generate(prompt, steps, use_cache=False)
b, cb = generate(prompt, steps, use_cache=True)
print("токены без кэша:", a[len(prompt):][:12], "...")
print("токены с кэшем: ", b[len(prompt):][:12], "...")
print("ответы совпадают:", a == b)
print(f"расчётов K и V: без кэша {ca['kv']}, с кэшем {cb['kv']} (меньше: ×{ca['kv'] / cb['kv']:.0f})")
print(f"скалярных произведений q*k: {ca['dots']} в обоих случаях: сам attention растёт квадратично с длиной")
