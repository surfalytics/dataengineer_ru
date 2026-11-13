"""Глава 1: языковая модель в миниатюре.
Показывает три идеи главы на крошечном корпусе:
  1. self-supervision: метки берутся из самого текста (контекст -> следующий токен, с <BOS> и <EOS>);
  2. autoregressive модель: видит только токены слева, пишет текст по одному токену (completion machine);
  3. masked модель: заполняет пропуск, используя токены слева и справа.
Запуск: python3 -I scripts/ai-engineering-code/ch01_language_models.py   (только стандартная библиотека)"""
import random
from collections import Counter, defaultdict

# Наш маленький корпус. Каждое предложение уже разбито на токены (по словам).
CORPUS = [
    "my favorite color is blue .",
    "my favorite color is green .",
    "my favorite food is pizza .",
    "my favorite tool is duckdb .",
    "the sky is blue .",
    "the grass is green .",
    "the color of the sky is blue .",
    "my team loves clean data .",
    "my team loves duckdb .",
    "clean data makes the pipeline stable .",
]
sentences = [s.split() for s in CORPUS]

print("== 1. Self-supervision: из одного предложения получаем обучающие примеры")
sentence = sentences[0]
tokens = ["<BOS>"] + sentence + ["<EOS>"]
examples = [(tokens[: i + 1], tokens[i + 1]) for i in range(len(tokens) - 1)]
print("предложение:", " ".join(sentence), f"({len(sentence)} токенов)")
for context, target in examples:
    print(f"  вход: {' '.join(context):<42} -> метка: {target}")
print(f"примеров из одного предложения: {len(examples)} (токенов + 1). Человек ничего не размечал.")

print("\n== 2. Цена разметки при обычном supervised обучении")
price_per_label = 0.05  # доллары за одну разметку (пример из главы)
images, categories = 1_000_000, 1_000
per_category = images // categories
print(f"{images:,} картинок по ${price_per_label} = ${images * price_per_label:,.0f}".replace(",", " "))
print(f"двое разметчиков на картинку: ${2 * images * price_per_label:,.0f}".replace(",", " "))
big = 1_000_000 * per_category * price_per_label
print(f"1 000 000 категорий по {per_category} картинок: ${big:,.0f}".replace(",", " "))

print("\n== 3. Autoregressive модель: считаем, что следует за контекстом из одного токена")
next_counts = defaultdict(Counter)
for s in sentences:
    t = ["<BOS>"] + s + ["<EOS>"]
    for a, b in zip(t, t[1:]):
        next_counts[a][b] += 1


def next_probs(prev):
    c = next_counts[prev]
    total = sum(c.values())
    return {tok: n / total for tok, n in c.most_common()}


for prev in ["is", "color", "loves"]:
    print(f"после «{prev}»:", {k: round(v, 2) for k, v in next_probs(prev).items()})


def complete(prompt, rng, max_tokens=8):
    """Дописывает prompt по одному токену, пока не встретит <EOS>."""
    out = prompt.split()
    for _ in range(max_tokens):
        probs = next_probs(out[-1])
        tok = rng.choices(list(probs), weights=list(probs.values()))[0]
        if tok == "<EOS>":
            break
        out.append(tok)
    return " ".join(out)


print("\n== 4. Completion machine: один prompt, разные продолжения (sampling)")
for seed in range(5):
    print(f"  seed={seed}:", complete("my favorite", random.Random(seed)))
print("Продолжение зависит от вероятностей, поэтому оно не гарантирует правду и меняется от запуска к запуску.")

print("\n== 5. Masked модель: заполняем пропуск по соседям слева и справа")
# Считаем тройки (слева, слово, справа). Это упрощённый аналог обучения BERT.
fill_counts = defaultdict(Counter)
for s in sentences:
    t = ["<BOS>"] + s + ["<EOS>"]
    for left, mid, right in zip(t, t[1:], t[2:]):
        fill_counts[(left, right)][mid] += 1


def fill_blank(left, right):
    c = fill_counts[(left, right)]
    total = sum(c.values())
    return {tok: round(n / total, 2) for tok, n in c.most_common()} if total else {}


text = "the ___ is green ."
print("пропуск:", text)
print("masked  (слева «the», справа «is»):", fill_blank("the", "is"))
print("autoregressive (только слева, «the»):", {k: round(v, 2) for k, v in next_probs("the").items()})
print("Masked модель видит «is» справа и отбрасывает «color» и «pipeline»: после них «is» не стоит.")
print("Autoregressive модель слева видит только «the» и не может использовать «is green».")

print("\n== 6. Размер словаря и число параметров этой таблицы")
vocab = {tok for s in sentences for tok in s} | {"<BOS>", "<EOS>"}
params = sum(len(c) for c in next_counts.values())
print(f"токенов в словаре: {len(vocab)}; записей в таблице переходов: {params}")
