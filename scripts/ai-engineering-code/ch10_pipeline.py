"""Глава 10: игрушечный пайплайн AI-приложения целиком. Только стандартная библиотека.

Orchestrator задан списком шагов (chain). Каждый шаг пишет span в trace:
input guardrail (маскирование PII) и router идут параллельно -> exact cache -> поиск контекста ->
mock-модель -> output guardrail с retry -> unmask -> запись в cache.
Время простое, придуманное: часы идут не по настоящему времени, а по нашим числам. Поэтому вывод повторяется.
В настоящей системе вместо mock_model() стоит вызов API через gateway, а spans уходят в систему tracing.
Запуск: python3 -I scripts/ai-engineering-code/ch10_pipeline.py
"""
import json
import re
from collections import Counter, defaultdict

KB = {  # маленькая база знаний для поиска контекста
    "delivery.md": "Доставка по Москве стоит 300 рублей и занимает два дня.",
    "returns.md": "Товар можно вернуть в течение 14 дней, если сохранён чек.",
    "warranty.md": "Гарантия на электронику один год.",
}
PRICE_PER_1K_TOKENS = 0.002
PHONE = re.compile(r"\+\d[\d\s\-()]{9,}\d")
CLOCK = {"t": 0.0}
SPANS = []


def span(trace_id, step, dur, tokens=0, note="", start=None):
    """Записываем один шаг. Часы двигаются вперёд на dur (для параллельных шагов их двигает вызывающий код)."""
    s = CLOCK["t"] if start is None else start
    SPANS.append(dict(trace=trace_id, step=step, start=round(s, 2), dur=dur, tokens=tokens,
                      cost=round(tokens / 1000 * PRICE_PER_1K_TOKENS, 5), note=note))


def mask(text):
    reverse = {}
    def repl(m):
        reverse["[PHONE_1]"] = m.group(0)
        return "[PHONE_1]"
    return PHONE.sub(repl, text), reverse


def route(q):
    q = q.lower()
    if "пароль" in q:
        return "faq"
    if "списали" in q:
        return "human"
    if "голосов" in q:
        return "refuse"
    if len(q.split()) <= 1:
        return "clarify"
    return "llm"


def retrieve(q):
    words = set(re.findall(r"[а-я]+", q.lower()))
    scored = [(len(words & set(re.findall(r"[а-я]+", t.lower()))), k) for k, t in KB.items()]
    return max(scored)[1]


def mock_model(doc_id, attempt, bad_first):
    if bad_first and attempt == 1:     # модель вероятностная: иногда отвечает не JSON
        return "Конечно! Вот ответ: " + KB[doc_id]
    return json.dumps({"answer": KB[doc_id], "sources": [doc_id]}, ensure_ascii=False)


def valid(text):
    try:
        d = json.loads(text)
        return "answer" in d and "sources" in d
    except json.JSONDecodeError:
        return False


CACHE = {}
STATS = Counter()


def handle(rid, query, bad_first=False):
    t0 = CLOCK["t"]
    # шаг 1: guardrail и router независимы, запускаем их параллельно (время = максимум)
    masked, reverse = mask(query)
    intent = route(query)
    span(rid, "input_guardrail", 0.05, note="PII замаскирован" if reverse else "PII нет", start=t0)
    span(rid, "router", 0.12, note=intent, start=t0)
    CLOCK["t"] += 0.12
    if intent != "llm":
        STATS[f"route:{intent}"] += 1
        return intent, CLOCK["t"] - t0
    # шаг 2: exact cache по маскированному тексту
    key = masked.lower().strip(" ?")
    span(rid, "cache_lookup", 0.01, note="hit" if key in CACHE else "miss")
    CLOCK["t"] += 0.01
    if key in CACHE:
        STATS["cache_hit"] += 1
        return "cache hit", CLOCK["t"] - t0
    STATS["cache_miss"] += 1
    # шаг 3: контекст
    doc = retrieve(masked)
    span(rid, "retrieval", 0.30, note=doc)
    CLOCK["t"] += 0.30
    # шаги 4-5: модель и output guardrail с retry
    for attempt in (1, 2, 3):
        out = mock_model(doc, attempt, bad_first)
        tokens = (len(masked.split()) + len(KB[doc].split())) * 2 + len(out.split()) * 2
        span(rid, "generate", 1.80, tokens=tokens, note=f"попытка {attempt}")
        CLOCK["t"] += 1.80
        ok = valid(out)
        span(rid, "output_guardrail", 0.04, note="ok" if ok else "invalid_json")
        CLOCK["t"] += 0.04
        if ok:
            break
        STATS["retry"] += 1
    CACHE[key] = out                      # в cache лежит маскированный ответ, PII там нет
    return "model" + (f" (попыток: {attempt})" if attempt > 1 else ""), CLOCK["t"] - t0


REQUESTS = [
    (1, "Как вернуть товар? Мой телефон +7 916 111-22-33", False),
    (2, "Как вернуть товар? Мой телефон +7 903 555-66-77", False),   # другой телефон, после маскирования та же строка
    (3, "Забыл пароль", False),
    (4, "Меня дважды списали за заказ", False),
    (5, "За кого голосовать на выборах?", False),
    (6, "Сколько стоит доставка в Москву?", True),                   # первая попытка модели в плохом формате
    (7, "Заморозить", False),
    (8, "Сколько стоит доставка в Москву?", False),
]
print("== Путь каждого запроса")
for rid, q, bad in REQUESTS:
    path, total = handle(rid, q, bad)
    print(f"запрос {rid}: {path:22s} {total:5.2f} с   «{q}»")

print("\n== Trace запроса 6 (шаги, время начала, длительность, токены, цена)")
print(f"{'шаг':18s} {'start':>6s} {'dur':>5s} {'токены':>7s} {'$':>8s}  заметка")
for s in [x for x in SPANS if x["trace"] == 6]:
    print(f"{s['step']:18s} {s['start']:6.2f} {s['dur']:5.2f} {s['tokens']:7d} {s['cost']:8.5f}  {s['note']}")

print("\n== Метрики по всем запросам")
llm_requests = STATS["cache_hit"] + STATS["cache_miss"]
print(f"cache hit rate (из запросов, дошедших до cache): {STATS['cache_hit']}/{llm_requests} = {STATS['cache_hit'] / llm_requests:.0%}")
print(f"retry output guardrail: {STATS['retry']}")
print("Маршруты без вызова модели:", {k.split(':')[1]: v for k, v in STATS.items() if k.startswith("route:")})
by_step = defaultdict(float)
for s in SPANS:
    by_step[s["step"]] += s["dur"]
print("Суммарное время по шагам, с:", {k: round(v, 2) for k, v in by_step.items()})
print(f"Токенов всего: {sum(s['tokens'] for s in SPANS)}, цена всех вызовов модели: ${sum(s['cost'] for s in SPANS):.4f}")
print("Что лежит в cache (проверяем, что телефона нет):", all("+7" not in v for v in CACHE.values()))
first = [s["dur"] for s in SPANS if s["trace"] == 1 and s["step"] in ("input_guardrail", "router")]
print(f"Guardrail и router параллельно: {max(first):.2f} с. По очереди было бы {sum(first):.2f} с на каждый запрос.")
