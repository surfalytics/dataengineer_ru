"""Глава 2: sampling. softmax, temperature, top-k, top-p, min-p и logprobs на маленьком словаре.
Запуск: python3 -I scripts/ai-engineering-code/ch02_sampling.py   (только стандартная библиотека)"""
import math
import random
import struct
from collections import Counter


def softmax(logits, t=1.0):
    """Logits -> вероятности. Делим на temperature и вычитаем максимум (так нет переполнения exp)."""
    scaled = [x / t for x in logits]
    m = max(scaled)
    exps = [math.exp(x - m) for x in scaled]
    s = sum(exps)
    return [e / s for e in exps]


def sample(probs, rng):
    """Случайный выбор индекса по вероятностям."""
    return rng.choices(range(len(probs)), weights=probs)[0]


def renorm(probs, keep):
    """Оставляем только токены из keep и пересчитываем вероятности так, чтобы сумма снова была 1."""
    s = sum(probs[i] for i in keep)
    return [probs[i] / s if i in keep else 0.0 for i in range(len(probs))]


def top_k(probs, k):
    order = sorted(range(len(probs)), key=lambda i: -probs[i])
    return set(order[:k])


def top_p(probs, p):
    """Самая маленькая группа лучших токенов, чья суммарная вероятность достигла p."""
    order = sorted(range(len(probs)), key=lambda i: -probs[i])
    keep, total = set(), 0.0
    for i in order:
        keep.add(i)
        total += probs[i]
        if total >= p - 1e-9:
            break
    return keep


def min_p(probs, threshold):
    """Оставляем токены, чья вероятность не ниже порога (вариант из книги)."""
    return {i for i, x in enumerate(probs) if x >= threshold}


print("== 1. Logits -> вероятности (softmax)")
vocab = ["зелёный", "красный", "синий", "дом", "и"]
logits = [2.2, 1.7, 0.9, -1.0, -1.5]
probs = softmax(logits)
for w, x, p in zip(vocab, logits, probs):
    print(f"{w:8s} logit = {x:5.1f}  вероятность = {p:6.1%}")
print(f"сумма logits = {sum(logits):.1f} (не 1), сумма вероятностей = {sum(probs):.1f}")

print("\n== 2. Temperature на примере из книги: logits [1, 2] для токенов A и B")
for t in (0.1, 0.5, 1, 2, 5):
    pa, pb = softmax([1, 2], t)
    print(f"T = {t:<4}  P(A) = {pa:.3f}  P(B) = {pb:.3f}")
print("T = 0: берём токен с наибольшим logit (argmax), softmax не считаем ->", "B")

print("\n== 3. Как temperature меняет частоты выбора (10 000 розыгрышей, seed = 42)")
rng = random.Random(42)
for t in (0.5, 1.0, 2.0):
    c = Counter(vocab[sample(softmax(logits, t), rng)] for _ in range(10_000))
    row = "  ".join(f"{w}: {c[w] / 100:5.1f}%" for w in vocab)
    print(f"T = {t:<3} {row}")
print("greedy (всегда argmax):", vocab[max(range(5), key=lambda i: logits[i])], "в 100% случаев")

print("\n== 4. Top-k, top-p, min-p. Токены: да 60%, возможно 31%, нет 8%, the 0,6%, … 0,4%")
v2 = ["да", "возможно", "нет", "the", "…"]
p2 = [0.60, 0.31, 0.08, 0.006, 0.004]
for name, keep in [("top-k, k = 2", top_k(p2, 2)), ("top-p = 0,90", top_p(p2, 0.90)), ("top-p = 0,99", top_p(p2, 0.99)),
                   ("min-p, порог 0,05", min_p(p2, 0.05))]:
    new = renorm(p2, keep)
    kept = ", ".join(f"{v2[i]} {new[i]:.1%}" for i in sorted(keep, key=lambda i: -p2[i]))
    print(f"{name:18s} -> {kept}")

print("\n== 5. Top-p подстраивается под ситуацию, top-k нет")
peaked = softmax([6.0, 5.2, 0.5, 0.2, 0.1] + [0.0] * 15)  # вопрос «Да или нет?»: два явных кандидата
flat = softmax([1.0, 0.9, 0.8, 0.7, 0.6] * 4)  # открытый вопрос: много равных кандидатов
for name, p in [("«Да или нет?»", peaked), ("«Смысл жизни?»", flat)]:
    print(f"{name:16s} top-p 0,9 оставляет {len(top_p(p, 0.9)):2d} из {len(p)} токенов, top-k (k = 5) всегда {len(top_k(p, 5))}")

print("\n== 6. Logprobs: зачем логарифм")
p_one = 1e-5  # вероятность одного токена
n = 70
prod = 1.0
for _ in range(n):
    prod *= p_one
print(f"произведение {n} вероятностей по {p_one}: {prod}  (истинное значение 1e-350 не помещается в float64)")
print(f"сумма логарифмов: {n * math.log(p_one):.2f}  (число спокойно хранится)")
tiny = struct.unpack("f", struct.pack("f", 1e-50))[0]
print(f"вероятность 1e-50 в float32: {tiny}, а её логарифм {math.log(1e-50):.2f}")
