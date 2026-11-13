#!/usr/bin/env python3
"""Глава 8: дедупликация текстов, от точных копий до MinHash + LSH. Без внешних библиотек.

Что показывает скрипт:
  1. Строим корпус из 500 документов с заранее известными дубликатами (точные копии,
     копии с другим регистром и пробелами, почти-копии с заменой 1-2 слов).
  2. Три способа найти дубликаты: hash точного текста, hash нормализованного текста,
     MinHash + LSH для почти-копий. Сравниваем с «правдой» (мы сами внесли дубликаты).
  3. Считаем, сколько пар пришлось бы сравнить попарно и сколько проверил LSH.
  4. Показываем утечку train/test: дубликат в test и оригинал в train портят метрику.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_dedup.py
"""
import hashlib
import random
import re
from itertools import combinations

rng = random.Random(8)

# ---------- 1. Корпус с известными дубликатами ----------
VOCAB = ("заказ оплата доставка склад курьер возврат счёт товар адрес телефон сайт карта скидка "
         "промокод корзина статус отмена обмен гарантия ремонт отзыв рейтинг магазин партия цена "
         "налог чек документ договор подпись платёж банк перевод остаток тариф подписка аккаунт "
         "пароль почта уведомление ошибка сбой обновление версия файл отчёт таблица данные запрос "
         "ответ клиент менеджер оператор очередь звонок письмо чат форма поле кнопка страница").split()
HEADERS = ["Здравствуйте, команда поддержки.", "Добрый день, обращаюсь по вопросу.",
           "Пишу по поводу обращения.", "Коллеги, нужна помощь."]


def make_doc():
    words = [rng.choice(VOCAB) for _ in range(30)]
    return rng.choice(HEADERS) + " " + " ".join(words) + "."


def format_variant(text):
    """Тот же текст, но другой регистр, лишние пробелы и знаки."""
    t = text.upper() if rng.random() < 0.5 else text.lower()
    return "  " + t.replace(" ", "  ", 2).replace(".", "..") + " "


def near_variant(text):
    """Почти копия: заменяем 1-2 слова на другие."""
    words = text.split(" ")
    for _ in range(rng.choice([1, 2])):
        words[rng.randrange(3, len(words))] = rng.choice(VOCAB)
    return " ".join(words)


docs, group = [], []        # group[i] = номер исходного документа
for g in range(400):
    docs.append(make_doc()); group.append(g)
for g in rng.sample(range(400), 40):          # 40 точных копий
    docs.append(docs[g]); group.append(g)
for g in rng.sample(range(400), 30):          # 30 копий с другим форматом
    docs.append(format_variant(docs[g])); group.append(g)
for g in rng.sample(range(400), 30):          # 30 почти-копий
    docs.append(near_variant(docs[g])); group.append(g)
N = len(docs)
true_pairs = {(i, j) for i, j in combinations(range(N), 2) if group[i] == group[j]}
print(f"Документов: {N}. Настоящих уникальных: {len(set(group))}. Пар-дубликатов: {len(true_pairs)}")


def report(name, pairs):
    pairs = set(pairs)
    tp = len(pairs & true_pairs)
    p = tp / len(pairs) if pairs else 1.0
    r = tp / len(true_pairs)
    print(f"{name:<38} пар найдено {len(pairs):>4}  precision {p:.2f}  recall {r:.2f}")


def pairs_from_buckets(buckets):
    out = set()
    for ids in buckets.values():
        out.update(combinations(sorted(ids), 2))
    return out


# ---------- 2a. Точный hash сырого текста ----------
raw = {}
for i, d in enumerate(docs):
    raw.setdefault(hashlib.sha256(d.encode()).hexdigest(), []).append(i)
print("\n--- Способы поиска ---")
report("hash сырого текста", pairs_from_buckets(raw))


# ---------- 2b. Hash нормализованного текста ----------
def normalize(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", t.lower())).strip()


norm = {}
for i, d in enumerate(docs):
    norm.setdefault(hashlib.sha256(normalize(d).encode()).hexdigest(), []).append(i)
report("hash нормализованного текста", pairs_from_buckets(norm))


# ---------- 2c. Shingles и точный Jaccard (попарно) ----------
def shingles(t, n=3):
    w = normalize(t).split()
    return {" ".join(w[k:k + n]) for k in range(len(w) - n + 1)}


SH = [shingles(d) for d in docs]


def jaccard(a, b):
    return len(a & b) / len(a | b)


THRESHOLD = 0.6
pair_found = {(i, j) for i, j in combinations(range(N), 2) if jaccard(SH[i], SH[j]) >= THRESHOLD}
total_pairs = N * (N - 1) // 2
report(f"попарно, Jaccard >= {THRESHOLD}", pair_found)
print(f"  сравнений при попарном подходе: {total_pairs}")

# ---------- 2d. MinHash + LSH ----------
P = (1 << 61) - 1
NUM_PERM, BANDS = 64, 16          # 16 полос по 4 значения
ROWS = NUM_PERM // BANDS
coef = [(rng.randrange(1, P), rng.randrange(0, P)) for _ in range(NUM_PERM)]


def h64(s):  # стабильный hash (встроенный hash() в Python меняется между запусками)
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


def minhash(sh):
    base = [h64(s) for s in sh]
    return [min((a * x + b) % P for x in base) for a, b in coef]


SIG = [minhash(s) for s in SH]
buckets = {}
for i, sig in enumerate(SIG):
    for b in range(BANDS):
        key = (b, tuple(sig[b * ROWS:(b + 1) * ROWS]))
        buckets.setdefault(key, set()).add(i)
cand = pairs_from_buckets(buckets)
lsh_found = {(i, j) for i, j in cand if jaccard(SH[i], SH[j]) >= THRESHOLD}  # проверяем только кандидатов
report("MinHash + LSH (кандидаты + проверка)", lsh_found)
print(f"  кандидатов после LSH: {len(cand)} из {total_pairs} пар ({100 * len(cand) / total_pairs:.1f}%)")

# Насколько точна оценка MinHash? Сравним с настоящим Jaccard на нескольких парах.
print("\n--- Оценка Jaccard по подписи из 64 чисел ---")
sample = sorted((p for p in true_pairs if jaccard(SH[p[0]], SH[p[1]]) < 0.999),
                key=lambda p: -jaccard(SH[p[0]], SH[p[1]]))   # только почти-копии
for i, j in [sample[0], sample[len(sample) // 2], sample[-1]]:
    est = sum(x == y for x, y in zip(SIG[i], SIG[j])) / NUM_PERM
    print(f"  пара ({i:>3},{j:>3}): настоящий Jaccard {jaccard(SH[i], SH[j]):.2f}, оценка MinHash {est:.2f}")


# ---------- 3. Группы и итоговый датасет ----------
parent = list(range(N))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for i, j in lsh_found:
    parent[find(j)] = find(i)
keep = sorted({find(i) for i in range(N)})
print(f"\nПосле дедупликации осталось {len(keep)} документов (правильный ответ: {len(set(group))})")

# ---------- 4. Утечка между train и test ----------
def leakage(test_ids, train_ids):
    train_sh = [SH[i] for i in train_ids]
    return sum(any(jaccard(SH[t], s) >= THRESHOLD for s in train_sh) for t in test_ids)


ids = list(range(N))
rng.shuffle(ids)
cut = int(N * 0.8)
train, test = ids[:cut], ids[cut:]
print("\n--- Утечка train/test ---")
print(f"Случайный split до дедупликации: {leakage(test, train)} из {len(test)} тестовых документов имеют копию в train")
root_side = {}
for r in keep:
    root_side[r] = "train" if rng.random() < 0.8 else "test"
train2 = [i for i in ids if root_side[find(i)] == "train"]
test2 = [i for i in ids if root_side[find(i)] == "test"]
print(f"Split по группам дубликатов: {leakage(test2, train2)} из {len(test2)} тестовых документов имеют копию в train")
