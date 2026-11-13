"""Глава 10: exact cache и semantic cache. Игрушечная версия, только стандартная библиотека.

Мы гоняем поток из 3000 запросов по пяти политикам cache и считаем:
hit rate, сколько ответов из cache оказались неверными (утечка чужих данных, устаревший ответ,
другой смысл), среднюю latency и стоимость.
Настоящий embedding заменён игрушечным: убираем стоп-слова и берём первые 5 букв слова.
Так перефразы получают высокую похожесть, а запросы «в Москву» и «в Минск» тоже получают высокую.
Это и есть главный риск semantic cache. Модель в примере не вызывается: ответ это просто метка.
Запуск: python3 -I scripts/ai-engineering-code/ch10_cache.py
"""
import math
import random
import re
from collections import Counter, OrderedDict

STOP = set("как какая какой какие что это мне в на и ли подскажите скажите пожалуйста объясни значит "
           "называется а по для у нас вам есть можно же нужно знать вопрос".split())


def embed(text):
    words = re.findall(r"[а-яa-z0-9]+", text.lower())
    return Counter(w[:5] for w in words if w not in STOP)


def cosine(a, b):
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


# тема: (перефразы, личное_видно_в_тексте, ответ_строится_из_данных_пользователя, зависит_от_времени, вес)
TOPICS = {
    "capital_vn": (["Какая столица Вьетнама?", "Как называется столица Вьетнама?", "Скажите, пожалуйста, столица Вьетнама?"], False, False, False, 8),
    "sql_join": (["Что такое JOIN в SQL?", "Объясни, что такое JOIN в SQL", "Что значит JOIN в SQL?"], False, False, False, 10),
    "delivery_msk": (["Сколько стоит доставка в Москву?", "Подскажите, сколько стоит доставка в Москву"], False, False, False, 6),
    "delivery_minsk": (["Сколько стоит доставка в Минск?", "Подскажите, сколько стоит доставка в Минск"], False, False, False, 6),
    "return_policy": (["Какие условия возврата электроники?", "Условия возврата электроники", "Можно ли вернуть электронику?"], False, True, False, 5),
    "order_status": (["Каков статус моего заказа?", "Где мой заказ сейчас?"], True, True, False, 4),
    "weather": (["Какая погода сегодня?", "Что с погодой сегодня?"], True, False, True, 3),
}
RULE_WORDS = ("мой", "моего", "сейчас", "сегодня")   # правило «этот запрос кэшировать нельзя»
N_QUERIES, N_USERS, BUCKET = 3000, 40, 150            # BUCKET: «час» для ответов, зависящих от времени


def tier(user):
    return "gold" if user % 3 == 0 else "basic"


def truth(topic, user, i):
    """Правильный ответ как метка. Он зависит от темы и, возможно, от пользователя или времени."""
    _, _, uses_user, timely, _ = TOPICS[topic]
    key = [topic]
    if topic == "order_status":
        key.append(f"user{user}")
    elif uses_user:
        key.append(tier(user))
    if timely:
        key.append(f"t{i // BUCKET}")
    return "|".join(key)


PREFIXES = ["", "Подскажите, ", "Скажите, пожалуйста, ", "Мне нужно знать: ", "Вопрос: "]


def make_stream(seed=5):
    """Люди пишут один вопрос по-разному: вежливые приставки и вопросительный знак меняют строку, но не смысл."""
    rng = random.Random(seed)
    names = list(TOPICS)
    weights = [TOPICS[t][4] for t in names]
    out = []
    for i in range(N_QUERIES):
        topic = rng.choices(names, weights)[0]
        base = rng.choice(TOPICS[topic][0])
        prefix = rng.choice(PREFIXES)
        text = prefix + (base[0].lower() + base[1:] if prefix else base)
        if rng.random() < 0.5:
            text = text.rstrip("?")
        out.append((i, topic, text, rng.randrange(N_USERS)))
    return out


def run(policy, threshold=None):
    """policy: 'all' кэшируем всё, 'rules' пропускаем запросы с «мой/сегодня», 'scoped' + ключ с пользователем."""
    exact, sem = {}, []   # sem: список (embedding, scope, ответ)
    st = Counter()
    latency = cost = 0.0
    for i, topic, text, user in make_stream():
        true_ans = truth(topic, user, i)
        skip = policy != "all" and any(w in text.lower() for w in RULE_WORDS)
        scope = user if policy == "scoped" and TOPICS[topic][2] else None
        key = (text.lower(), scope)
        served = None
        if not skip:
            if key in exact:
                served, latency = exact[key], latency + 0.01
                st["exact_hit"] += 1
            elif threshold is not None:
                cost += 0.0005
                latency += 0.1                      # embedding + vector search
                e = embed(text)
                best = max(((cosine(e, se), a) for se, sc, a in sem if sc == scope), default=(0, None))
                if best[0] >= threshold:
                    served = best[1]
                    st["semantic_hit"] += 1
        if served is None:                          # промах или кэширование запрещено: зовём модель
            served = true_ans
            cost += 0.01
            latency += 2.0
            if not skip:
                exact[key] = served
                if threshold is not None:
                    sem.append((embed(text), scope, served))
            continue
        if served != true_ans:
            st["wrong"] += 1
            same_topic = served.split("|")[0] == topic
            if same_topic and topic in ("order_status", "return_policy"):
                st["leak"] += 1
            elif same_topic:
                st["stale"] += 1
            else:
                st["other_meaning"] += 1
    return st, cost, latency / N_QUERIES


print(f"== Поток из {N_QUERIES} запросов, {N_USERS} пользователей. Модель стоит $0,01 и 2 с, lookup в semantic cache $0,0005 и 0,1 с")
print(f"{'политика':38s} {'hit':>6s} {'неверных':>9s} {'утечек':>7s} {'устар.':>7s} {'смысл':>6s} {'$':>7s} {'сек':>6s}")
rows = [("exact, кэшируем всё", "all", None), ("exact + правило «мой/сегодня»", "rules", None),
        ("exact + правило + ключ по пользователю", "scoped", None),
        ("semantic, порог 0,70 (+ правила, ключ)", "scoped", 0.70), ("semantic, порог 0,90 (+ правила, ключ)", "scoped", 0.90)]
for name, pol, th in rows:
    st, cost, lat = run(pol, th)
    hits = st["exact_hit"] + st["semantic_hit"]
    print(f"{name:38s} {hits / N_QUERIES:6.1%} {st['wrong']:9d} {st['leak']:7d} {st['stale']:7d} {st['other_meaning']:6d} {cost:7.2f} {lat:6.2f}")

print("\n== Похожесть пар запросов в игрушечном embedding")
pairs = [("Какая столица Вьетнама?", "Как называется столица Вьетнама?"),
         ("Сколько стоит доставка в Москву?", "Сколько стоит доставка в Минск?"),
         ("Какие условия возврата электроники?", "Можно ли вернуть электронику?")]
for a, b in pairs:
    print(f"{cosine(embed(a), embed(b)):.2f}  {a}  |  {b}")

# --- LRU: размер cache и hit rate ---------------------------------------------
print("\n== Eviction policy LRU: hit rate exact cache при разном размере")
stream = [(t, u) for _, topic, t, u in make_stream() if not any(w in t.lower() for w in RULE_WORDS)]
for cap in (2, 5, 10, 1000):
    lru, hits = OrderedDict(), 0
    for text, _ in stream:
        k = text.lower()
        if k in lru:
            hits += 1
            lru.move_to_end(k)
        else:
            lru[k] = True
            if len(lru) > cap:
                lru.popitem(last=False)
    print(f"размер {cap:4d}: hit rate {hits / len(stream):.1%}")
