"""Задача 1: разбить документ на фрагменты (chunk) с перекрытием."""


def chunk(words, size, overlap):
    step = size - overlap
    return [words[i:i + size] for i in range(0, len(words), step) if i == 0 or i < len(words) - overlap]


words = [f"w{i}" for i in range(1000)]
parts = chunk(words, size=200, overlap=20)
print("фрагментов:", len(parts))
print("первый:", parts[0][0], "..", parts[0][-1])
print("второй:", parts[1][0], "..", parts[1][-1])
print("последний:", parts[-1][0], "..", parts[-1][-1], f"({len(parts[-1])} слов)")
