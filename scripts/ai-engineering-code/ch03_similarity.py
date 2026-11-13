"""Глава 3: exact match, edit distance, n-gram overlap, cosine similarity.
Запуск: python3 scripts/ai-engineering-code/ch03_similarity.py   (только стандартная библиотека)"""
import math

print("== 1. Exact match и его слабое место")
question, ref = "В каком году вышел Python 3.0?", "2008"
good = "Python 3.0 вышел в 2008 году."
bad = "Python 3.0 вышел в 2009, а Python 2.6 в 2008."
for name, ans in {"верный ответ": good, "неверный ответ": bad}.items():
    print(f"{name}: точное совпадение = {ans == ref}; «содержит эталон» = {ref in ans}")
print("«Содержит эталон» принял неверный ответ: в нём есть '2008', но это год другой версии.")

print("\n== 2. Edit distance (вставка, удаление, замена)")


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


for a, b in [("bad", "bard"), ("bad", "cash"), ("brad", "bad")]:
    print(f"{a!r} -> {b!r}: {edit_distance(a, b)}")

print("\n== 3. Пересечение слов и n-gram (lexical similarity)")


def ngrams(words, n):
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]


def overlap(ref, cand, n):
    r, c = ngrams(ref.split(), n), set(ngrams(cand.split(), n))
    return sum(g in c for g in r) / len(r)


ref = "таблица заказов обновляется каждую ночь"
cands = {
    "A (неверный смысл)": "таблица заказов обновляется каждый час",
    "B (верный смысл)": "заказы в таблице обновляются каждую ночь",
}
print("эталон:", ref)
for name, c in cands.items():
    print(f"{name}: слова {overlap(ref, c, 1):.0%}, биграммы {overlap(ref, c, 2):.0%}")
print("Ответ A с неверным смыслом получил более высокий балл, чем верный ответ B.")

print("\n== 4. Cosine similarity (semantic similarity)")


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


# Учебные векторы из трёх чисел. Настоящие embeddings имеют 384-3072 числа.
emb = {
    "Кошка сидит на коврике": [0.90, 0.10, 0.20],
    "Собака играет на лужайке": [0.80, 0.20, 0.30],
    "Исследования ИИ — это весело": [0.10, 0.90, 0.10],
}
base = emb["Кошка сидит на коврике"]
for text, v in emb.items():
    print(f"{text:32s} cosine = {cosine(base, v):.3f}")
print("одинаковые векторы:", round(cosine([1, 2, 3], [1, 2, 3]), 3),
      "| противоположные:", round(cosine([1, 2, 3], [-1, -2, -3]), 3))
