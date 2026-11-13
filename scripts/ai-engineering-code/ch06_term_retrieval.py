"""Глава 6: term-based retrieval с нуля: токенизация, inverted index, TF-IDF и BM25.
Показывает: как строится inverted index, как считают TF, IDF и итоговый балл, чем BM25
отличается от наивного TF-IDF (нормализация по длине документа), сильные стороны
(точный код ошибки) и слабые стороны (синонимы, многозначные слова) term-based поиска.
Запуск: python3 -I scripts/ai-engineering-code/ch06_term_retrieval.py   (только стандартная библиотека)"""
import math
import re
from collections import Counter, defaultdict

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
    """Нижний регистр, только слова и числа, без стоп-слов."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


print("== 1. Токенизация и inverted index")
tokens = {d: tokenize(t) for d, t in DOCS.items()}
print("d1 ->", tokens["d1"])
index = defaultdict(dict)  # term -> {doc: частота term в doc}
for d, toks in tokens.items():
    for term, f in Counter(toks).items():
        index[term][d] = f
for term in ("transformer", "vectors", "delivery", "eaddrnotavail"):
    print(f"{term:14s} документов: {len(index[term])}  (doc, частота): {sorted(index[term].items())}")

N = len(DOCS)


def idf_naive(term):
    """IDF по книге: log(N / C(t)), C(t) — число документов с термином."""
    return math.log(N / len(index[term])) if term in index else 0.0


def tfidf_score(query, doc):
    """Наивный TF-IDF: сумма IDF(t) * f(t, D) по терминам запроса."""
    f = Counter(tokens[doc])
    return sum(idf_naive(t) * f[t] for t in tokenize(query))


print("\n== 2. IDF: редкие термины важнее частых")
for term in ("days", "transformer", "vectors", "eaddrnotavail"):
    print(f"IDF({term}) = log({N}/{len(index[term])}) = {idf_naive(term):.2f}")

AVG_LEN = sum(len(t) for t in tokens.values()) / N


def idf_bm25(term):
    n = len(index.get(term, {}))
    return math.log(1 + (N - n + 0.5) / (n + 0.5))


def bm25_score(query, doc, k1=1.5, b=0.75):
    """BM25: насыщение частоты (k1) и нормализация по длине документа (b)."""
    f = Counter(tokens[doc])
    length = len(tokens[doc])
    score = 0.0
    for t in tokenize(query):
        if f[t]:
            tf = f[t] * (k1 + 1) / (f[t] + k1 * (1 - b + b * length / AVG_LEN))
            score += idf_bm25(t) * tf
    return score


def search(query, scorer, k=3):
    scored = sorted(((scorer(query, d), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [(d, round(s, 2)) for s, d in scored[:k] if s > 0]


print("\n== 3. Поиск: TF-IDF и BM25")
for q in ("transformer architecture neural network", "vector nearest neighbors", "EADDRNOTAVAIL (99)"):
    print(f"запрос: {q!r}")
    print("  TF-IDF:", search(q, tfidf_score))
    print("  BM25  :", search(q, bm25_score))

print("\n== 4. Длинный документ: BM25 гасит эффект длины")
short = "refund policy refund"
long_ = "refund " + " ".join(["lorem"] * 60) + " refund"
tokens["s"], tokens["l"] = tokenize(short), tokenize(long_)
for t in ("s", "l"):
    for term, f in Counter(tokens[t]).items():
        index[term][t] = f
N += 2
AVG_LEN = sum(len(t) for t in tokens.values()) / len(tokens)
print(f"короткий документ: длина {len(tokens['s'])}, refund встречается 2 раза")
print(f"длинный документ : длина {len(tokens['l'])}, refund встречается 2 раза")
print(f"TF-IDF: короткий {tfidf_score('refund', 's'):.2f}, длинный {tfidf_score('refund', 'l'):.2f}  (одинаково, длина не учтена)")
print(f"BM25  : короткий {bm25_score('refund', 's'):.2f}, длинный {bm25_score('refund', 'l'):.2f}  (длинный документ получает меньше)")
N -= 2

print("\n== 5. Слабое место: нет общих слов — нет результата")
for q in ("I lost access to my profile", "how fast will my order arrive"):
    print(f"запрос: {q!r} -> BM25: {search(q, bm25_score)}")
print("«profile» и «access» не встречаются в d5/d6, «arrive» не равно «arrives». Term-based поиск не знает синонимов.")

print("\n== 6. Токены из нескольких слов: «hot dog»")
print("по словам      :", tokenize("hot dog recipe"))
bigram_terms = {"hot dog"}


def tokenize_with_bigrams(text):
    words = [t for t in re.findall(r"[a-z0-9]+", text.lower())]
    out, i = [], 0
    while i < len(words):
        if i + 1 < len(words) and f"{words[i]} {words[i + 1]}" in bigram_terms:
            out.append(f"{words[i]} {words[i + 1]}")
            i += 2
        else:
            if words[i] not in STOP:
                out.append(words[i])
            i += 1
    return out


print("с bigram-токеном:", tokenize_with_bigrams("hot dog recipe"))
print("Частый bigram считаем одним термином, иначе «hot» и «dog» теряют смысл.")
