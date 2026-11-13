"""Глава 3: entropy, cross entropy, perplexity, BPC и BPB на маленьких примерах.
Запуск: python3 scripts/ai-engineering-code/ch03_perplexity.py   (только стандартная библиотека)"""
import math
from collections import Counter, defaultdict


def entropy(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


def cross_entropy(p, q):
    return -sum(px * math.log2(qx) for px, qx in zip(p, q) if px > 0)


print("== 1. Entropy двух «языков» (рис. 3-4)")
print("язык (a), 2 токена:", entropy([0.5, 0.5]), "бит")
print("язык (b), 4 токена:", entropy([0.25] * 4), "бит")

print("\n== 2. Cross entropy = entropy данных + KL-дивергенция")
P = [0.5, 0.25, 0.125, 0.125]  # настоящее распределение токенов в данных
models = {"точная модель": [0.5, 0.25, 0.125, 0.125], "модель без знаний": [0.25] * 4}
hp = entropy(P)
print(f"H(P) = {hp:.3f}")
for name, q in models.items():
    h = cross_entropy(P, q)
    print(f"{name}: H(P,Q) = {h:.3f}, KL = {h - hp:.3f}, perplexity = {2 ** h:.3f}")

print("\n== 3. Perplexity последовательности по вероятностям токенов (logprobs)")
probs = [0.5, 0.25, 0.5, 0.125]  # вероятности, которые модель дала реальным токенам
bits = [-math.log2(p) for p in probs]
avg = sum(bits) / len(bits)
print("биты на токен:", bits, "среднее:", avg)
print(f"perplexity = 2^{avg} = {2 ** avg:.3f}")
nats = [-math.log(p) for p in probs]
print(f"то же в nat: e^{sum(nats) / len(nats):.4f} = {math.exp(sum(nats) / len(nats)):.3f}")

print("\n== 4. BPC и BPB")
bits_per_token, chars_per_token, bytes_per_char = 6, 2, 7 / 8
bpc = bits_per_token / chars_per_token
bpb = bpc / bytes_per_char
print(f"BPC = {bits_per_token}/{chars_per_token} = {bpc}; BPB = {bpc}/(7/8) = {bpb:.2f}")
print(f"сжатие: {bpb:.2f} бит вместо 8 на байт -> {bpb / 8:.0%} от исходного размера")

print("\n== 5. Мини-языковая модель: perplexity как детектор «виденных» и странных текстов")
train = ("таблица заказов обновляется каждую ночь. витрина данных строится из таблицы заказов. "
         "пайплайн загружает данные в хранилище. отчёт показывает заказы по дням.")
alphabet = sorted(set(train) | set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,"))
counts = defaultdict(Counter)
for a, b in zip(train, train[1:]):
    counts[a][b] += 1


def ppl(text):  # символьная биграммная модель со сглаживанием +1
    total = 0.0
    for a, b in zip(text, text[1:]):
        p = (counts[a][b] + 1) / (sum(counts[a].values()) + len(alphabet))
        total += -math.log2(p)
    return 2 ** (total / (len(text) - 1))


tests = {
    "из обучающих данных": "таблица заказов обновляется каждую ночь.",
    "новый, но похожий текст": "витрина заказов строится каждую ночь.",
    "бессмыслица": "щъф кзю ыэбж пцчх яйьо.",
}
for name, t in tests.items():
    print(f"{name:26s} perplexity = {ppl(t):6.2f}")
