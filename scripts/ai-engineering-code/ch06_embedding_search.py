"""Глава 6: embedding-based retrieval на игрушечных embeddings.
Настоящая embedding model обучена на больших данных. Здесь мы заменяем её словарём «понятий»:
каждое слово несёт вес в нескольких смысловых осях, текст = сумма слов. Это модель идеи
(близкий смысл -> близкие vectors), а не настоящая embedding model. В production вместо
функции embed() вызывают настоящую модель.
Показывает: embedding текста, cosine similarity, k-NN перебором, поиск без общих слов,
разбор многозначного слова по контексту, слабое место (редкий код ошибки), цену хранения vectors.
Запуск: python3 -I scripts/ai-engineering-code/ch06_embedding_search.py   (только стандартная библиотека)"""
import math
import re

DOCS = {
    "d1": "Transformer architecture: self-attention lets a neural network weigh every token against every other token.",
    "d2": "A power transformer changes the voltage of electricity between two circuits using coils.",
    "d3": "Transformers is a film series about robots that turn into cars.",
    "d4": "Error EADDRNOTAVAIL (99) means the address you try to bind is not available on this machine.",
    "d5": "How to reset your password: click Forgot password on the login page and follow the email link.",
    "d6": "I cannot sign in to my account after changing the phone number.",
    "d7": "Refund policy: you can return a product within 30 days and get your money back.",
    "d8": "Our delivery takes three to five days. Express delivery arrives the next day.",
    "d9": "Hot dog recipe for beginners: grill the sausage and warm the bun.",
    "d10": "Embedding models turn text into vectors so that similar meaning gives close vectors.",
    "d11": "BM25 ranks documents by term frequency, inverse document frequency and document length.",
    "d12": "Vector database stores embeddings and finds nearest neighbors quickly.",
}
AXES = ["account", "money", "shipping", "ml", "electric", "film", "food", "system", "search"]
LEX = {  # слово -> веса по осям смысла (ручной словарь, учебный)
    "password": {"account": 1}, "login": {"account": 1}, "sign": {"account": .8}, "account": {"account": 1},
    "profile": {"account": .9}, "access": {"account": .8}, "forgot": {"account": .6}, "reset": {"account": .6},
    "email": {"account": .3}, "credentials": {"account": 1}, "lost": {"account": .3}, "phone": {"account": .2},
    "refund": {"money": 1}, "money": {"money": 1}, "cash": {"money": 1}, "return": {"money": .6},
    "product": {"money": .3}, "back": {"money": .3}, "policy": {"money": .2},
    "delivery": {"shipping": 1}, "order": {"shipping": .6}, "arrive": {"shipping": 1}, "arrives": {"shipping": 1},
    "fast": {"shipping": .5}, "days": {"shipping": .4}, "express": {"shipping": .8}, "day": {"shipping": .2},
    "transformer": {"ml": .4, "electric": .4, "film": .2}, "transformers": {"film": .6, "ml": .2},
    "architecture": {"ml": .8}, "neural": {"ml": 1}, "network": {"ml": .5, "system": .3}, "attention": {"ml": .7},
    "token": {"ml": .7}, "self": {"ml": .2}, "models": {"ml": .6}, "text": {"ml": .3},
    "embedding": {"ml": .6, "search": .5}, "embeddings": {"ml": .6, "search": .5},
    "vector": {"search": .6, "ml": .4}, "vectors": {"search": .6, "ml": .4}, "database": {"search": .6},
    "nearest": {"search": 1}, "neighbors": {"search": 1}, "find": {"search": .7}, "finds": {"search": .7},
    "similar": {"search": .3, "ml": .3}, "meaning": {"search": .3, "ml": .3}, "bm25": {"search": 1},
    "term": {"search": .7}, "frequency": {"search": .7}, "documents": {"search": .7}, "document": {"search": .7},
    "ranks": {"search": .7},
    "voltage": {"electric": 1}, "electricity": {"electric": 1}, "circuits": {"electric": 1}, "coils": {"electric": 1},
    "power": {"electric": .8},
    "film": {"film": 1}, "series": {"film": .6}, "robots": {"film": .6, "ml": .1}, "cars": {"film": .3},
    "error": {"system": .8}, "address": {"system": .8}, "bind": {"system": .8}, "available": {"system": .4},
    "machine": {"system": .4},
    "hot": {"food": 1}, "dog": {"food": .6}, "recipe": {"food": 1}, "sausage": {"food": 1}, "grill": {"food": 1},
    "bun": {"food": 1}, "warm": {"food": .5}, "beginners": {"food": .2},
}


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def embed(text):
    """Учебный embedding: сумма смысловых весов слов, потом нормировка до длины 1."""
    v = [0.0] * len(AXES)
    for w in words(text):
        for axis, weight in LEX.get(w, {}).items():
            v[AXES.index(axis)] += weight
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm else v


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def knn(query, k=3):
    """Точный k-NN: считаем сходство со всеми vectors, сортируем, берём k лучших."""
    q = embed(query)
    scored = sorted(((cosine(q, VECTORS[d]), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [(d, round(s, 2)) for s, d in scored[:k] if s > 0]


print("== 1. Индексация: каждый документ -> vector")
VECTORS = {d: embed(t) for d, t in DOCS.items()}
print("оси:", AXES)
for d in ("d5", "d8", "d1"):
    nz = {a: round(x, 2) for a, x in zip(AXES, VECTORS[d]) if x}
    print(f"{d}: {nz}")

print("\n== 2. Запрос: тот же embed(), потом k ближайших (точный k-NN)")
for q in ("I lost access to my profile", "how fast will my order arrive", "can I get cash back for a product"):
    print(f"запрос: {q!r}")
    print("  k-NN:", knn(q))
print("Общих слов с d5, d6, d8, d7 почти нет, но по смыслу они найдены: слова из одной смысловой оси лежат рядом.")

print("\n== 3. Многозначное слово: контекст решает")
for q in ("transformer", "transformer architecture neural network", "transformer voltage coils"):
    print(f"запрос: {q!r}")
    print("  k-NN:", knn(q))
print("Одно слово «transformer»: d1 (нейросеть) и d2 (электрика) получают одинаковое сходство 0,73. Контекстные слова решают спор.")

print("\n== 4. Слабое место: редкий точный код")
q = "EADDRNOTAVAIL (99)"
print(f"запрос: {q!r}; vector запроса: {embed(q)}")
print("  k-NN:", knn(q), "(vector нулевой: игрушечная модель не знает этот токен, все сходства равны 0)")
print("запрос: 'error address bind' ->", knn("error address bind", 2))
print("Настоящая модель даст «размытый» vector про сетевые ошибки. Точный код она находит ненадёжно. Для этого есть term-based поиск.")

print("\n== 5. Сколько стоит хранить и обновлять vectors")
docs_per_day, dim, bytes_per_float = 100_000_000, 1536, 4
per_second = docs_per_day / 86_400
storage_gb = docs_per_day * dim * bytes_per_float / 1e9
print(f"Пересчёт 100 млн документов в день = {per_second:.0f} embeddings в секунду, всё время")
print(f"100 млн vectors по {dim} чисел float32 = {storage_gb:.0f} GB только на vectors (без индекса)")
print(f"Те же vectors в 1 байт на число (quantization) = {storage_gb / 4:.0f} GB")
