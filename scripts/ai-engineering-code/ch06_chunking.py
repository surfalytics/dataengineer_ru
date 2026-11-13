"""Глава 6: стратегии chunking — как резать документы перед индексацией.
Показывает: фиксированные куски (символы, слова, предложения), overlap, рекурсивное
разбиение, разбиение по структуре (пары «вопрос-ответ»), chunking по токенам и то,
как размер chunk влияет на число chunks (и на число vectors).
Запуск: python3 -I scripts/ai-engineering-code/ch06_chunking.py   (только стандартная библиотека)"""
import random
import re

print("== 1. Overlap: фраза не рвётся посередине")
phrase = "Я оставил жене записку на столе".split()


def word_chunks(words, size, overlap=0):
    """Куски по `size` слов; соседние куски делят `overlap` слов."""
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step) if words[i:i + size]]


print("без overlap  :", word_chunks(phrase, 3, 0))
print("overlap = 1  :", word_chunks(phrase, 4, 1))
print("overlap = 2  :", word_chunks(phrase, 4, 2))
print("Без overlap ни один кусок не говорит, что оставили записку жене. С overlap первый кусок несёт ключевое.")

print("\n== 2. Разные единицы: символы, слова, предложения, абзацы")
doc = """Загрузка данных идёт каждую ночь. Сначала Airflow запускает задачу extract. Она читает новые заказы из PostgreSQL.

Потом идёт очистка. Мы убираем дубликаты и пустые строки. Даты приводим к UTC.

Последний шаг — запись в витрину. Таблица orders_daily обновляется инкрементально. Если шаг упал, Airflow повторяет его три раза.

Алерты уходят в Slack. Дежурный смотрит на них утром. Если упала загрузка, он запускает backfill."""


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def char_chunks(text, size, overlap=0):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


paragraphs = [p.strip() for p in doc.split("\n\n")]
print(f"символов в документе: {len(doc)}, слов: {len(doc.split())}, предложений: {len(sentences(doc))}, абзацев: {len(paragraphs)}")
for size in (120, 60):
    parts = char_chunks(doc, size)
    cut = sum(not p.rstrip().endswith((".", "!", "?")) for p in parts)
    print(f"по {size} символов: кусков {len(parts)}, оборваны посреди предложения: {cut}")
print("по 3 предложения: кусков", len([" ".join(sentences(doc)[i:i + 3]) for i in range(0, len(sentences(doc)), 3)]))
print("по абзацу: кусков", len(paragraphs))

print("\n== 3. Рекурсивное разбиение: от крупных единиц к мелким")


def recursive_split(text, max_len, seps=("\n\n", ". ", " ")):
    """Режем по самому крупному разделителю. Если кусок всё ещё длиннее max_len, берём следующий."""
    if len(text) <= max_len:
        return [text.strip()]
    for sep in seps:
        parts = text.split(sep)
        if len(parts) > 1:
            out, buf = [], ""
            for part in parts:
                piece = part if part.endswith((".", "!", "?")) or sep != ". " else part + "."
                if len(buf) + len(piece) + 1 <= max_len:
                    buf = (buf + " " + piece).strip()
                else:
                    if buf:
                        out.append(buf)
                    buf = piece
                    if len(buf) > max_len:  # кусок всё ещё велик: спускаемся ниже
                        out.extend(recursive_split(buf, max_len, seps[seps.index(sep) + 1:] or (" ",)))
                        buf = ""
            if buf:
                out.append(buf)
            return [o for o in out if o]
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


rec = recursive_split(doc, 100)
for i, c in enumerate(rec, 1):
    print(f"[{i}] ({len(c):3d} симв.) {c}")
print("все куски не длиннее 100:", all(len(c) <= 100 for c in rec))

print("\n== 4. Структура документа: пары «вопрос-ответ»")
faq = """В: Как сбросить пароль?
О: Нажмите «Забыли пароль» на странице входа. Мы пришлём ссылку на почту.
В: Как удалить аккаунт?
О: Напишите в поддержку. Удаление занимает до 7 дней."""
pairs = re.findall(r"В: (.+?)\nО: (.+?)(?=\nВ: |\Z)", faq, flags=re.S)
for q, a in pairs:
    print(f"chunk = вопрос + ответ: «{q}» -> «{a[:30]}…»")

print("\n== 5. Chunking по токенам: смена tokenizer требует переиндексации")


def tok_a(text):  # «токенизатор» A: слово = токен
    return re.findall(r"\w+|[^\w\s]", text)


def tok_b(text):  # «токенизатор» B: слово режется на куски по 4 символа
    out = []
    for t in re.findall(r"\w+|[^\w\s]", text):
        out.extend(t[i:i + 4] for i in range(0, len(t), 4))
    return out


for name, tk in (("A", tok_a), ("B", tok_b)):
    toks = tk(doc)
    chunks = [toks[i:i + 32] for i in range(0, len(toks), 32)]
    print(f"tokenizer {name}: токенов {len(toks)}, кусков по 32 токена {len(chunks)}")
print("Границы кусков у A и B разные. Сменили модель с другим tokenizer — пересчитайте chunks и embeddings.")

print("\n== 6. Размер chunk и число vectors")
rng = random.Random(42)
pool = ["Таблица обновляется каждую ночь.", "Дубликаты удаляются по ключу заказа.", "Ошибка пишется в лог.",
        "Алерт приходит в Slack.", "Витрина читает только чистые данные.", "Backfill запускают вручную.",
        "Схема проверяется перед записью.", "Партиции создаются по дате."]
big = " ".join(rng.choice(pool) for _ in range(600))
words = big.split()
print(f"слов в большом документе: {len(words)}")
print(f"{'размер chunk (слов)':>20} {'chunks':>8} {'vectors в базе':>15}")
for size in (200, 100, 50, 25):
    n = len(word_chunks(words, size, 0))
    print(f"{size:>20} {n:>8} {n:>15}")
print("Размер chunk вдвое меньше -> chunks вдвое больше: больше embeddings, больше хранение, дольше поиск.")
print("Зато в контекст модели влезает вдвое больше разных кусков.")
