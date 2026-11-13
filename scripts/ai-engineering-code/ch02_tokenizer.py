"""Глава 2: почему текст на разных языках стоит по-разному. Учим крошечный byte-level BPE-токенайзер
на корпусе, где почти всё по-английски, и считаем токены для одной и той же мысли на шести языках.
Это игрушка: настоящие токенайзеры учат на миллиардах слов, но механизм тот же.
Запуск: python3 -I scripts/ai-engineering-code/ch02_tokenizer.py   (только стандартная библиотека)"""
import random
from collections import Counter

def grid(subjects, verbs, objects, times, template):
    return [template.format(s=s, v=v, o=o, t=t) for s in subjects for v in verbs for o in objects for t in times]


# обучающие фразы собираем из комбинаций слов, чтобы токенайзер учил слова, а не запоминал целые фразы
EN = grid(["pipeline", "script", "service"], ["loads", "updates", "checks"], ["orders table", "customers table", "sales mart"],
          ["every night", "every day", "every hour"], "the {s} {v} the {o} {t}")
RU = grid(["конвейер", "скрипт", "сервис"], ["загружает", "обновляет", "проверяет"], ["таблицу заказов", "таблицу клиентов", "витрину продаж"],
          ["каждую ночь", "каждый день", "каждый час"], "{s} {v} {o} {t}")
ES = grid(["pipeline", "script", "servicio"], ["carga", "actualiza", "revisa"], ["tabla de pedidos", "tabla de clientes", "vitrina de ventas"],
          ["cada noche", "cada día", "cada hora"], "el {s} {v} la {o} {t}")


def make_corpus(share_en, share_ru, n=3000, seed=5):
    rng = random.Random(seed)
    langs = [EN, RU, ES]
    weights = [share_en, share_ru, 1 - share_en - share_ru]
    return " ".join(rng.choice(rng.choices(langs, weights)[0]) for _ in range(n))


def merge(ids, pair, new_id):
    out, i = [], 0
    while i < len(ids):
        if i + 1 < len(ids) and (ids[i], ids[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def train_bpe(text, n_merges):
    """Начинаем с 256 байтов. На каждом шаге склеиваем самую частую пару соседних токенов в новый токен."""
    ids = list(text.encode("utf-8"))
    merges = {}
    for step in range(n_merges):
        counts = Counter(zip(ids, ids[1:]))
        if not counts:
            break
        pair = max(counts, key=lambda p: (counts[p], -p[0], -p[1]))  # самая частая, при равенстве — по номерам
        merges[pair] = 256 + step
        ids = merge(ids, pair, 256 + step)
    return merges


def encode(text, merges):
    ids = list(text.encode("utf-8"))
    for pair, new_id in merges.items():  # merges хранятся в порядке обучения
        ids = merge(ids, pair, new_id)
    return ids


# одна и та же мысль («мы с друзьями каждое утро ходим на старый городской рынок»); таких слов в обучающем корпусе нет
SAMPLES = {
    "английский": "My friends and I walk to the old city market every morning.",
    "испанский": "Mis amigos y yo caminamos al viejo mercado de la ciudad cada mañana.",
    "немецкий": "Meine Freunde und ich gehen jeden Morgen zum alten Stadtmarkt.",
    "русский": "Мы с друзьями каждое утро ходим на старый городской рынок.",
    "греческий": "Οι φίλοι μου κι εγώ πηγαίνουμε κάθε πρωί στην παλιά αγορά της πόλης.",
    "хинди": "मैं और मेरे दोस्त हर सुबह पुराने शहर के बाज़ार जाते हैं।",
}


def report(merges, title):
    print(title)
    print(f"{'язык':11s} {'символов':>8s} {'байтов':>7s} {'токенов':>8s} {'к английскому':>14s}")
    base = len(encode(SAMPLES["английский"], merges))
    for lang, text in SAMPLES.items():
        n = len(encode(text, merges))
        print(f"{lang:11s} {len(text):8d} {len(text.encode('utf-8')):7d} {n:8d} {'×' + format(n / base, '.1f'):>14s}")


print("== 1. Токенайзер без обучения: токен = байт")
report({}, "каждый символ ASCII — 1 байт, кириллица и греческий — 2 байта, деванагари — 3 байта")

corpus = make_corpus(0.90, 0.07)
print(f"\n== 2. Токенайзер, обученный на английском корпусе (90% английский, 7% русский, 3% испанский; {len(corpus)} символов, 200 слияний)")
m1 = train_bpe(corpus, 200)
report(m1, "английский сжался сильнее всех: слияния учились в основном на нём")

corpus2 = make_corpus(0.40, 0.40)
print("\n== 3. Тот же токенайзер, но корпус «ровнее» (40% английский, 40% русский, 20% испанский)")
m2 = train_bpe(corpus2, 200)
report(m2, "русского в корпусе больше: русский подешевел, греческий и хинди не изменились (их нет в корпусе)")

print("\n== 4. Что значит разница для денег (цена гипотетическая: $10 за 1 млн токенов)")
base = len(encode(SAMPLES["английский"], m1))
for lang in ("английский", "русский", "хинди"):
    n = len(encode(SAMPLES[lang], m1))
    print(f"{lang:11s} {n:3d} токенов на фразу; 1 млн таких фраз = {n} млн токенов = ${n * 10} (английский: ${base * 10})")
