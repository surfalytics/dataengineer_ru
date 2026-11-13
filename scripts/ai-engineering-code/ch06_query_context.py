"""Глава 6: query rewriting и contextual retrieval на простом BM25.
Показывает: почему реплика диалога «А Эмили Доу?» нельзя отправлять в поиск как есть, как работает
переписывание запроса (здесь rewriter — простое правило; в реальной системе это вызов модели с промптом
«перепиши последний вопрос так, чтобы он был понятен без диалога»), как rewriter отказывается решать то, чего не знает,
и как контекст, дописанный к chunk (метаданные, коды, вопросы, описание места в документе), возвращает chunk в выдачу.
Запуск: python3 -I scripts/ai-engineering-code/ch06_query_context.py   (только стандартная библиотека)"""
import math
import re
from collections import Counter

STOP = {"a", "the", "of", "to", "in", "on", "is", "and", "from", "for", "us", "did", "was", "how", "about", "what", "when",
        "time", "by", "with", "it", "an", "that", "this", "at", "her", "she", "they"}


def tok(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.toks = {d: tok(t) for d, t in docs.items()}
        self.avg = sum(map(len, self.toks.values())) / len(docs)
        self.df = Counter(t for ts in self.toks.values() for t in set(ts))

    def search(self, q, k=3):
        n, out = len(self.docs), []
        for d, ts in self.toks.items():
            f, s = Counter(ts), 0.0
            for t in tok(q):
                if f[t]:
                    idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                    s += idf * f[t] * (self.k1 + 1) / (f[t] + self.k1 * (1 - self.b + self.b * len(ts) / self.avg))
            if s > 0:
                out.append((round(s, 2), d))
        return [d for s, d in sorted(out, key=lambda x: (-x[0], x[1]))][:k]


print("== 1. Query rewriting: реплика диалога без контекста")
PURCHASES = {
    "p1": "John Doe last bought a Fruity Fedora hat two weeks ago.",
    "p2": "Emily Doe last bought a Tabby Tie three days ago.",
    "p3": "Emily Doe asked support about the delivery of her order.",
    "p4": "Emily Doe changed her email address and phone number.",
}
index = BM25(PURCHASES)
dialog = ["When was the last time John Doe bought something from us?",
          "John last bought a Fruity Fedora hat from us two weeks ago.",
          "How about Emily Doe?"]
raw = dialog[-1]
print(f"запрос как есть: {raw!r} -> найдено {index.search(raw)}")


def rewrite(history, last):
    """MOCK-rewriter: берёт шаблон предыдущего вопроса пользователя и подставляет новое имя.
    Если в реплике нет имени, которое можно подставить, честно говорит, что вопрос не решается."""
    names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", last)
    if not names:
        return "CANNOT_RESOLVE"
    prev_question = next(m for m in reversed(history) if m.endswith("?"))
    return re.sub(r"[A-Z][a-z]+ [A-Z][a-z]+", names[0], prev_question)


new_q = rewrite(dialog[:-1], raw)
print(f"после rewriting: {new_q!r} -> найдено {index.search(new_q)}")
print("Без rewriting среди документов Эмили нет приоритета: вопрос о покупке потерялся. После rewriting покупка первая.")

print("\n== 2. Rewriter не должен выдумывать")
for last in ("How about Emily Doe?", "What about his wife?"):
    r = rewrite(dialog[:-1], last)
    print(f"{last!r} -> {r!r}")
print("Для «his wife» имени в запросе нет. Rewriter возвращает CANNOT_RESOLVE и не придумывает имя.")
print("Сначала нужно спросить базу, кто жена этого клиента, и только потом переписывать запрос.")

print("\n== 3. Contextual retrieval: chunk без контекста не находится")
chunks = {
    "c1": "It grew by 3% over the previous quarter.",
    "c2": "They hired 40 engineers and opened a new office.",
    "c3": "Error EADDRNOTAVAIL (99) appeared in the nightly job logs.",
    "c4": "Customers can try again after five minutes.",
}
# Контекст пишет модель по паре (документ, chunk). Здесь он записан руками, как мог бы ответить rewriter.
CONTEXT = {
    "c1": "From the ACME Q2 2030 report, section on revenue growth.",
    "c2": "From the ACME Q2 2030 report, section on hiring and offices.",
    "c3": "From the infrastructure incident log of Q2 2030.",
    "c4": "From the help center article about account lockout after wrong passwords.",
}
query = "ACME Q2 2030 revenue growth"
plain = BM25(chunks)
print(f"запрос: {query!r}")
print("chunks как есть        ->", plain.search(query) or "[]  (в chunk нет ни названия компании, ни слов «revenue growth»)")
with_context = {c: f"{CONTEXT[c]} {t}" for c, t in chunks.items()}
print("+ контекст документа   ->", BM25(with_context).search(query))
print("\n== 4. Метаданные и вопросы к chunk")
meta = dict(chunks)
meta["c3"] += " keywords: EADDRNOTAVAIL, cannot assign requested address, bind error"
meta["c4"] += " questions: I forgot my password. I cannot log in. Why is my account locked?"
for q in ("cannot assign requested address", "I forgot my password", "why is my account locked"):
    print(f"{q!r:36s} без: {plain.search(q) or '[]'}   с метаданными: {BM25(meta).search(q) or '[]'}")
print("Ключевые слова и типовые вопросы в метаданных дают поиску зацепки. Они же помогают после превращения chunk в embedding.")
