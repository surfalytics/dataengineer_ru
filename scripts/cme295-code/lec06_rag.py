"""Лекция 6: поиск кандидатов. Семантика, BM25 и их объединение (hybrid).
Эмбеддинги здесь игрушечные: слова-синонимы попадают в одно «понятие».
Так пример идёт без загрузки модели и всегда даёт один результат."""
import math
import re
from collections import Counter

import numpy as np

DOCS = [
    "Huggy likes to work downstairs",
    "Where is Paris located?",
    "He was in a cuddly mood",
    "Cuddly spends most days surrounded by books",
]
QUERY = "Where is Cuddly?"
STOP = {"is", "was", "in", "a", "he", "to", "by", "where"}  # служебные слова для BM25

# понятия игрушечного энкодера: у каждого понятия своя ось вектора
CONCEPTS = {
    "hug": {"cuddly", "huggy", "cuddle"},
    "place": {"where", "located", "downstairs"},
    "paris": {"paris"},
    "work": {"work", "likes"},
    "books": {"books", "surrounded"},
    "mood": {"mood"},
    "days": {"days"},
}
AXES = list(CONCEPTS)


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def embed(text):
    vec = np.zeros(len(AXES))
    for w in words(text):
        for i, name in enumerate(AXES):
            if w in CONCEPTS[name]:
                vec[i] += 1
    return vec


def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def bm25_scores(query, docs, k1=1.5, b=0.75):
    toks = [[w for w in words(d) if w not in STOP] for d in docs]
    avg = sum(len(t) for t in toks) / len(toks)
    n = len(docs)
    scores = []
    for t in toks:
        tf = Counter(t)
        s = 0.0
        for q in words(query):
            if q in STOP:
                continue
            df = sum(1 for x in toks if q in x)
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
            s += idf * tf[q] * (k1 + 1) / (tf[q] + k1 * (1 - b + b * len(t) / avg))
        scores.append(s)
    return scores


def ranks(scores):
    """Номера мест (с 1). Документ с нулевым счётом места не получает."""
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    return {i: r + 1 for r, i in enumerate(order) if scores[i] > 0}


sem = [cosine(embed(QUERY), embed(d)) for d in DOCS]
bm = bm25_scores(QUERY, DOCS)
r_sem, r_bm = ranks(sem), ranks(bm)
rrf = [sum(1 / (60 + r[i]) for r in (r_sem, r_bm) if i in r) for i in range(len(DOCS))]
r_rrf = ranks(rrf)

print(f"{'документ':<46}{'semantic':>9}{'BM25':>7}{'hybrid':>8}")
for i, d in enumerate(DOCS):
    print(f"{d:<46}{r_sem.get(i, '-'):>9}{r_bm.get(i, '-'):>7}{r_rrf.get(i, '-'):>8}")
top2 = lambda r: sorted(r, key=r.get)[:2]
print("top-2 semantic:", [DOCS[i] for i in top2(r_sem)])
print("top-2 BM25    :", [DOCS[i] for i in top2(r_bm)])
print("top-2 hybrid  :", [DOCS[i] for i in top2(r_rrf)])
