"""Глава 6: hybrid search, слияние рангов RRF и reranking.
Показывает: как RRF складывает рейтинги term-based и embedding-based retrievers, последовательную схему
«дешёвый поиск -> точный reranking», reranking по времени и порядок документов в контексте.
Запуск: python3 -I scripts/ai-engineering-code/ch06_hybrid_rerank.py
(нужен соседний файл ch06_retrieval_lib.py; только стандартная библиотека)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch06_retrieval_lib import DOCS, VECTORS, cosine, dense_search, embed, rrf, term_search  # noqa: E402

print("== 1. RRF руками")
# Документ A: 1-й в одном рейтинге и 2-й в другом. Упрощённая версия без k: 1/1 + 1/2 = 1,5
print("упрощённо (без k): 1/1 + 1/2 =", 1 / 1 + 1 / 2)
for k in (0, 60):
    s_a = 1 / (k + 1) + 1 / (k + 2)  # A: ранг 1 и ранг 2
    s_b = 1 / (k + 3) + 1 / (k + 1)  # B: ранг 3 и ранг 1
    print(f"k = {k:2d}: A = {s_a:.4f}, B = {s_b:.4f}")
print("k = 60 сглаживает разницу между рангами: первое место уже не «в разы» лучше второго.")

print("\n== 2. Hybrid search: term-based + embedding-based -> RRF")
queries = {
    "EADDRNOTAVAIL (99)": "точный код: embedding не знает токен",
    "I lost access to my profile": "нет общих слов: BM25 ничего не находит",
    "transformer architecture": "оба метода находят",
}
for q, note in queries.items():
    term, dense = term_search(q), dense_search(q)
    fused, score = rrf([term, dense])
    print(f"запрос: {q!r} ({note})")
    print("  BM25 :", term[:3])
    print("  dense:", dense[:3])
    print("  RRF  :", [(d, round(score[d], 4)) for d in fused[:3]])
print("Один retriever подстраховывает другой: код ошибки находит BM25, перефразированный вопрос находит embedding.")

print("\n== 3. Последовательно: дешёвый retriever берёт кандидатов, reranker выбирает лучших")
query = "transformer for text models"
cands = term_search(query)  # шаг 1: BM25, дёшево
print("кандидаты BM25:", cands)
q = embed(query)
reranked = sorted(cands, key=lambda d: -cosine(q, VECTORS[d]))  # шаг 2: точнее и дороже, смотрит на смысл
print("после reranking по смыслу:", [(d, round(cosine(q, VECTORS[d]), 2)) for d in reranked])
print("d2 (про электрический трансформатор) ушёл вниз: BM25 видел только слово «transformer».")

print("\n== 4. Reranking по времени: свежее важнее")
news = [  # (id, релевантность запросу, возраст в днях)
    ("n1", 0.90, 400), ("n2", 0.80, 3), ("n3", 0.75, 10), ("n4", 0.70, 1), ("n5", 0.60, 90),
]
HALF_LIFE = 14  # через 14 дней вес падает вдвое
rows = [(i, rel, age, rel * 0.5 ** (age / HALF_LIFE)) for i, rel, age in news]
print(f"{'id':>3} {'relevance':>10} {'возраст':>8} {'с учётом времени':>17}")
for i, rel, age, adj in sorted(rows, key=lambda r: -r[3]):
    print(f"{i:>3} {rel:>10.2f} {age:>6} дн {adj:>17.3f}")
print("По одной релевантности первым был бы n1 (ему 400 дней). С учётом времени первый n2.")

print("\n== 5. Порядок в контексте: самое важное — в начало и в конец")


def order_for_context(ranked):
    """Модели лучше видят начало и конец контекста. Лучший документ в начало, второй — в конец."""
    front, back = [], []
    for i, d in enumerate(ranked):
        (front if i % 2 == 0 else back).append(d)
    return front + back[::-1]


ranked = ["r1", "r2", "r3", "r4", "r5"]
print("по рангу        :", ranked)
print("для контекста   :", order_for_context(ranked))
print("Важно: сам документ должен попасть в контекст. Порядок влияет слабее, чем ранг в поисковой выдаче.")
