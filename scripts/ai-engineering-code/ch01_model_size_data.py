"""Глава 1: почему большим моделям нужно больше данных.
Мини-эксперимент: «модель» это таблица n-грамм. Чем длиннее контекст, тем больше записей (параметров) и тем больше она может выучить.
Данные генерирует скрытый источник: следующий токен зависит в основном от последнего токена и чуть-чуть от двух последних.
На малом корпусе большая модель (trigram) проигрывает маленькой (bigram): ей не хватает примеров. На большом корпусе она выигрывает.
Качество меряем perplexity на отложенных данных (ниже = лучше).
Запуск: python3 -I scripts/ai-engineering-code/ch01_model_size_data.py   (только стандартная библиотека)"""
import math
import random
from collections import Counter, defaultdict

VOCAB = 8
ALPHA = 0.05  # сглаживание: небольшая вероятность для комбинаций, которых не было в обучении


def make_source(seed):
    """Скрытый источник: следующий токен зависит в основном от последнего токена (80%) и немного от двух последних (20%)."""
    rng = random.Random(seed)

    def sharp():
        w = [rng.random() ** 4 + 0.01 for _ in range(VOCAB)]
        s = sum(w)
        return [x / s for x in w]

    one = {a: sharp() for a in range(VOCAB)}
    table = {}
    for a in range(VOCAB):
        for b in range(VOCAB):
            two = sharp()
            table[(a, b)] = [0.8 * x + 0.2 * y for x, y in zip(one[b], two)]
    return table


def sample(table, n, seed):
    rng = random.Random(seed)
    seq = [rng.randrange(VOCAB), rng.randrange(VOCAB)]
    while len(seq) < n:
        seq.append(rng.choices(range(VOCAB), weights=table[(seq[-2], seq[-1])])[0])
    return seq


def train(seq, order):
    """order=1: контекст из 1 токена (bigram), order=2: из 2 токенов (trigram)."""
    counts = defaultdict(Counter)
    for i in range(order, len(seq)):
        counts[tuple(seq[i - order:i])][seq[i]] += 1
    return counts


def perplexity(counts, seq, order):
    log_sum, n = 0.0, 0
    for i in range(order, len(seq)):
        c = counts.get(tuple(seq[i - order:i]), Counter())
        p = (c[seq[i]] + ALPHA) / (sum(c.values()) + ALPHA * VOCAB)
        log_sum += -math.log2(p)
        n += 1
    return 2 ** (log_sum / n)


source = make_source(seed=7)
test = sample(source, 20_000, seed=99)

print(f"{'токенов в обучении':>20} | {'модель':<8} | {'параметров':>10} | perplexity на отложенных данных")
print("-" * 78)
for size in [50, 150, 1_000, 5_000, 50_000]:
    train_seq = sample(source, size, seed=size)
    row = []
    for order, name in [(1, "bigram"), (2, "trigram")]:
        counts = train(train_seq, order)
        params = sum(len(c) for c in counts.values())
        ppl = perplexity(counts, test, order)
        row.append((name, params, ppl))
        print(f"{size:>20} | {name:<8} | {params:>10} | {ppl:6.2f}")
    winner = min(row, key=lambda r: r[2])[0]
    print(f"{'':>20}   лучше: {winner}")
print()
print("Всего возможных записей: bigram =", VOCAB * VOCAB, ", trigram =", VOCAB ** 3)
