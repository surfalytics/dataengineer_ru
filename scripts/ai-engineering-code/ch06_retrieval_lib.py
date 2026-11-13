"""Глава 6: общие кирпичики для примеров hybrid search и оценки retrieval.
Здесь: учебная база документов, токенизация, BM25 (term-based), игрушечные embeddings (semantic),
cosine similarity и слияние рангов RRF. Это библиотека, а не самостоятельный скрипт:
её подключают ch06_hybrid_rerank.py и ch06_retrieval_eval.py.
Подробное объяснение каждой части: ch06_term_retrieval.py (BM25) и ch06_embedding_search.py (embeddings)."""
import math
import re
from collections import Counter

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
STOP = {"a", "the", "of", "to", "in", "on", "is", "and", "you", "your", "how", "can", "i", "my", "that", "so", "by",
        "for", "this", "into", "it", "an", "or", "with", "every", "other", "our", "after", "about", "against"}


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


# ---------- term-based: BM25 ----------
TOKENS = {d: tokenize(t) for d, t in DOCS.items()}
N = len(DOCS)
AVG_LEN = sum(map(len, TOKENS.values())) / N
DF = Counter(t for toks in TOKENS.values() for t in set(toks))  # в скольких документах есть термин


def bm25(query, doc, k1=1.5, b=0.75):
    f, length, score = Counter(TOKENS[doc]), len(TOKENS[doc]), 0.0
    for t in tokenize(query):
        if f[t]:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            score += idf * f[t] * (k1 + 1) / (f[t] + k1 * (1 - b + b * length / AVG_LEN))
    return score


def term_search(query):
    """Полный рейтинг по BM25. В выдачу попадают только документы с общими терминами."""
    scored = sorted(((bm25(query, d), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [d for s, d in scored if s > 0]


# ---------- embedding-based: игрушечные embeddings ----------
AXES = ["account", "money", "shipping", "ml", "electric", "film", "food", "system", "search"]
LEX = {
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


def embed(text):
    v = [0.0] * len(AXES)
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        for axis, weight in LEX.get(w, {}).items():
            v[AXES.index(axis)] += weight
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm else v


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


VECTORS = {d: embed(t) for d, t in DOCS.items()}


def dense_search(query):
    """Рейтинг по cosine similarity. В выдачу попадают документы с положительным сходством."""
    q = embed(query)
    scored = sorted(((cosine(q, VECTORS[d]), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [d for s, d in scored if s > 0]


# ---------- слияние рангов ----------
def rrf(rankings, k=60):
    """Reciprocal rank fusion: score(D) = сумма 1 / (k + rank_i(D)) по всем рейтингам."""
    score = Counter()
    for ranking in rankings:
        for rank, d in enumerate(ranking, 1):
            score[d] += 1 / (k + rank)
    return sorted(score, key=lambda d: (-score[d], d)), score
