"""Задача 1: токенизируем слово по готовому списку слияний BPE."""
merges = [("l", "o"), ("lo", "w"), ("e", "s"), ("es", "t"), ("n", "e"), ("ne", "w")]


def tokenize(word):
    parts = list(word)
    for a, b in merges:                      # слияния применяем строго по порядку
        i = 0
        while i + 1 < len(parts):
            if parts[i] == a and parts[i + 1] == b:
                parts[i:i + 2] = [a + b]
            else:
                i += 1
    return parts


for w in ["lowest", "newest", "slow", "wow"]:
    print(w, "->", tokenize(w))
