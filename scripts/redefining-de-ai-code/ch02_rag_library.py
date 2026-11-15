"""Глава 2: самый простой RAG на выдуманной библиотеке.
Показывает три шага: chunking скользящим окном, поиск по сходству (косинусное сходство
векторов) и сборку system prompt из найденного контекста.
Вместо настоящей embedding-модели — игрушечный вектор «мешок основ слов»: он нужен,
чтобы код работал без сети и без ключей API. Принцип тот же: близкие по смыслу тексты
дают близкие векторы.
Запуск: python3 -I scripts/redefining-de-ai-code/ch02_rag_library.py   (только стандартная библиотека)"""
import math
import re
from collections import Counter

# Наша «база знаний»: книги, которых нет в интернете, а значит, и в обучении LLM.
BOOKS = [
    {"id": "LIB-01", "title": "Северный архив", "author": "Марта Ольсен", "year": 2022,
     "shelf": "A2", "summary": "Архивариус находит в подвале библиотеки письма, которые меняют историю города."},
    {"id": "LIB-02", "title": "Сад из стекла", "author": "Игорь Векшин", "year": 2024,
     "shelf": "C5", "summary": "Ботаник выращивает стеклянные растения и узнаёт, что они хранят память о людях."},
    {"id": "LIB-03", "title": "Ночной pipeline", "author": "Анна Ли", "year": 2023,
     "shelf": "T1", "summary": "Практическое пособие: как дата-инженеру чинить ночную загрузку данных и не терять заказы."},
    {"id": "LIB-04", "title": "Последний трамвай", "author": "Олег Рудин", "year": 2021,
     "shelf": "B7", "summary": "Водитель трамвая каждую ночь подвозит одного и того же пассажира, которого никто не видит."},
]


def stem(word):
    """Грубая основа слова: первые 5 букв. Так «книга» и «книги» совпадут."""
    return word[:5]


def embed(text):
    """Игрушечный embedding: сколько раз встречается каждая основа слова."""
    words = re.findall(r"[a-zа-яё0-9]+", text.lower())
    return Counter(stem(w) for w in words if len(w) > 2)


def cosine(a, b):
    """Косинусное сходство: 1 — векторы смотрят в одну сторону, 0 — общего нет."""
    dot = sum(a[k] * b[k] for k in a if k in b)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def sliding_chunks(words, size, overlap):
    """Chunking скользящим окном: соседние куски делят `overlap` слов."""
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words) - overlap, 1), step)]


print("== 1. Chunking скользящим окном (6 слов, перекрытие 2)")
text = BOOKS[2]["summary"].split()
for i, ch in enumerate(sliding_chunks(text, 6, 2), 1):
    print(f"chunk {i}: {ch}")

print("\n== 2. Индексация: один документ на книгу")
index = []
for b in BOOKS:
    doc = f"{b['title']}. Автор: {b['author']}. Год: {b['year']}. Полка: {b['shelf']}. {b['summary']}"
    index.append((b, doc, embed(doc)))
print("в индексе документов:", len(index))

print("\n== 3. Поиск по сходству")
question = "Кто написал книгу про стеклянный сад и на какой полке она стоит?"
q = embed(question)
ranked = sorted(index, key=lambda r: (-cosine(q, r[2]), r[0]["id"]))
for b, _, vec in ranked:
    print(f"{b['id']}  {cosine(q, vec):.3f}  {b['title']}")

top_k = 1
context = "\n".join(doc for _, doc, _ in ranked[:top_k])

print("\n== 4. Что уходит в LLM")
messages = [
    {"role": "system",
     "content": "Ты помощник библиотеки. Отвечай ТОЛЬКО по каталогу ниже. "
                "Если ответа в каталоге нет, так и скажи.\n\n" + context},
    {"role": "user", "content": question},
]
for m in messages:
    print(f"[{m['role']}] {m['content']}")
