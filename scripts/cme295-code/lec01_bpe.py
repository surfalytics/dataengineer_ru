"""BPE на маленьком корпусе: словарь растёт слиянием самой частой пары."""
from collections import Counter

# Слова корпуса и сколько раз каждое встречается
corpus = {"low": 5, "lower": 2, "newest": 6, "widest": 3}

# Начинаем с отдельных букв
words = {w: list(w) for w in corpus}
vocab = sorted({ch for w in corpus for ch in w})
print("Начальный словарь:", vocab)


def count_pairs():
    pairs = Counter()
    for w, freq in corpus.items():
        parts = words[w]
        for a, b in zip(parts, parts[1:]):
            pairs[(a, b)] += freq
    return pairs


def merge(pair):
    new = pair[0] + pair[1]
    for w, parts in words.items():
        out, i = [], 0
        while i < len(parts):
            if i + 1 < len(parts) and (parts[i], parts[i + 1]) == pair:
                out.append(new)
                i += 2
            else:
                out.append(parts[i])
                i += 1
        words[w] = out
    return new


merges = []
for step in range(1, 9):
    pairs = count_pairs()
    # при равенстве берём пару, которая раньше по алфавиту
    best = min(pairs, key=lambda p: (-pairs[p], p))
    new = merge(best)
    merges.append(best)
    vocab.append(new)
    print(f"Шаг {step}: пара {best} встречается {pairs[best]} раз -> токен '{new}'")

print("Слова после слияний:", words)


def tokenize(word):
    """Применяем выученные слияния по порядку к новому слову."""
    parts = list(word)
    for pair in merges:
        i = 0
        while i + 1 < len(parts):
            if (parts[i], parts[i + 1]) == pair:
                parts[i:i + 2] = [pair[0] + pair[1]]
            else:
                i += 1
    return parts


print("Новое слово 'lowest':", tokenize("lowest"))
print("Размер словаря:", len(vocab))
