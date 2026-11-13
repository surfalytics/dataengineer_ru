"""Глава 6: оценка retrieval на маленьком размеченном наборе.
Показывает: context precision, context recall, MRR, MAP, NDCG, и сравнение трёх retrievers:
term-based (BM25), embedding-based (игрушечные embeddings) и hybrid (RRF).
Для каждого запроса мы заранее разметили, какие документы релевантны (в реальности это делают люди или AI judge).
Запуск: python3 -I scripts/ai-engineering-code/ch06_retrieval_eval.py
(нужен соседний файл ch06_retrieval_lib.py; только стандартная библиотека)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch06_retrieval_lib import dense_search, rrf, term_search  # noqa: E402

# evaluation set: запрос -> множество релевантных документов (разметили все 12 документов под каждый запрос)
EVAL = {
    "transformer architecture neural network": {"d1"},
    "EADDRNOTAVAIL (99)": {"d4"},
    "I lost access to my profile": {"d5", "d6"},
    "how fast will my order arrive": {"d8"},
    "can I get cash back for a product": {"d7"},
    "find nearest vectors in a database": {"d12"},
    "how do search engines rank documents": {"d11"},
    "transformer": {"d1"},  # нужен документ про нейросети, но слово неоднозначно
    "tasty dinner with bread": {"d9"},  # ни одного общего слова, и словарь игрушечной модели его не знает
}
K = 3


def precision(found, relevant):
    """Context precision: какая доля найденных документов релевантна."""
    return sum(d in relevant for d in found) / len(found) if found else 0.0


def recall(found, relevant):
    """Context recall: какая доля всех релевантных документов найдена. Нужна разметка всей базы."""
    return sum(d in relevant for d in found) / len(relevant)


def reciprocal_rank(found, relevant):
    """1 / ранг первого релевантного документа (0, если его нет). Среднее по запросам = MRR."""
    for rank, d in enumerate(found, 1):
        if d in relevant:
            return 1 / rank
    return 0.0


def average_precision(found, relevant):
    """AP: средняя precision в позициях, где стоит релевантный документ. Среднее по запросам = MAP."""
    hits, total = 0, 0.0
    for rank, d in enumerate(found, 1):
        if d in relevant:
            hits += 1
            total += hits / rank
    return total / len(relevant)


def ndcg(found, relevant):
    """NDCG с бинарной релевантностью: награда 1/log2(rank+1), делим на идеальный порядок."""
    dcg = sum(1 / math.log2(r + 1) for r, d in enumerate(found, 1) if d in relevant)
    ideal = sum(1 / math.log2(r + 1) for r in range(1, min(len(relevant), len(found)) + 1))
    return dcg / ideal if ideal else 0.0


RETRIEVERS = {
    "BM25": term_search,
    "embeddings": dense_search,
    "hybrid RRF": lambda q: rrf([term_search(q), dense_search(q)])[0],
}


def evaluate(search, k=K):
    rows = []
    for q, rel in EVAL.items():
        found = search(q)[:k]
        rows.append((precision(found, rel), recall(found, rel), reciprocal_rank(found, rel),
                     average_precision(found, rel), ndcg(found, rel)))
    return [sum(col) / len(rows) for col in zip(*rows)]


print(f"== 1. Что нашёл каждый retriever (top-{K}); релевантные документы в скобках")
for q, rel in EVAL.items():
    print(f"запрос: {q!r}  (релевантно: {sorted(rel)})")
    for name, search in RETRIEVERS.items():
        print(f"  {name:11s} {search(q)[:K]}")

print(f"\n== 2. Метрики по retrievers (среднее по {len(EVAL)} запросам, k = {K})")
print(f"{'retriever':11s} {'precision':>10} {'recall':>7} {'MRR':>6} {'MAP':>6} {'NDCG':>6}")
for name, search in RETRIEVERS.items():
    p, r, mrr, ap, nd = evaluate(search)
    print(f"{name:11s} {p:>10.2f} {r:>7.2f} {mrr:>6.2f} {ap:>6.2f} {nd:>6.2f}")
print("Документы и запросы подобраны так, чтобы показать сильные и слабые стороны каждого метода.")
print("Hybrid не проваливается там, где проваливается один из retrievers. Но последний запрос не нашёл никто.")

print("\n== 3. Как меняются precision и recall, если брать больше документов (hybrid RRF)")
print(f"{'k':>3} {'precision':>10} {'recall':>7}")
for k in (1, 2, 3, 5, 8):
    p, r, *_ = evaluate(RETRIEVERS["hybrid RRF"], k)
    print(f"{k:>3} {p:>10.2f} {r:>7.2f}")
print("Больше k -> recall растёт, precision падает. Модели в контекст лучше давать мало, но точных документов.")

print("\n== 4. Один запрос подробно: «I lost access to my profile», k = 3")
q, rel = "I lost access to my profile", EVAL["I lost access to my profile"]
for name, search in RETRIEVERS.items():
    f = search(q)[:3]
    print(f"{name:11s} найдено {f}: precision {precision(f, rel):.2f}, recall {recall(f, rel):.2f}, "
          f"RR {reciprocal_rank(f, rel):.2f}, NDCG {ndcg(f, rel):.2f}")
