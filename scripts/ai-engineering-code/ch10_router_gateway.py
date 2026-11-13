"""Глава 10: router и gateway. Игрушечная версия, только стандартная библиотека.

1) Router: intent classifier по ключевым словам направляет запрос службы поддержки
   в нужное место: FAQ, живой оператор, специальный бот, отказ или уточняющий вопрос.
2) Context fit: запрос не влезает в лимит модели. Обрезаем контекст или берём модель побольше.
3) Gateway: единый интерфейс к разным провайдерам, доступ по приложениям, лимит токенов,
   fallback на другую модель при сбое.
4) Цена: сколько экономит router, если простые запросы идут в дешёвую модель.

В настоящей системе intent classifier это маленькая модель (BERT, Llama 7B или свой классификатор),
а провайдеры вызываются через их SDK. Цены ниже придуманы для примера.
Запуск: python3 -I scripts/ai-engineering-code/ch10_router_gateway.py
"""

# --- 1. Router ---------------------------------------------------------------
INTENTS = {
    "password_reset": (["пароль", "сбросить", "войти", "забыл"], "страница FAQ про пароль"),
    "billing_error": (["счёт", "списали", "оплат", "возврат"], "живой оператор"),
    "tech_issue": (["ошибка", "не работает", "падает", "завис"], "бот по техническим проблемам"),
}
OFF_TOPIC = ["выбор", "президент", "политик", "погода", "анекдот"]


def route(query):
    q = query.lower()
    if any(w in q for w in OFF_TOPIC):
        return "off_topic", "стандартный отказ без вызова модели"
    scores = {name: sum(w in q for w in words) for name, (words, _) in INTENTS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        if len(q.split()) <= 2:
            return "ambiguous", "уточняющий вопрос"
        return "unknown", "универсальная модель"
    return best, INTENTS[best][1]


print("== 1. Router: куда идёт запрос")
for q in ["Забыл пароль, не могу войти", "Меня дважды списали за заказ, нужен возврат",
          "Ошибка 500, приложение не работает", "Заморозить", "За кого вы проголосуете на выборах?",
          "Как подключить второго пользователя?"]:
    intent, where = route(q)
    print(f"{q:42s} -> {intent:15s} -> {where}")

# --- 2. Router и лимит контекста ---------------------------------------------
MODELS = {"small-4k": 4_000, "large-32k": 32_000}


def fit_context(query_tokens, context_tokens, model, prefer="bigger"):
    """Если не влезает: либо режем контекст, либо идём в модель с большим лимитом."""
    limit = MODELS[model]
    total = query_tokens + context_tokens
    if total <= limit:
        return model, context_tokens, "влезает"
    bigger = [m for m, lim in MODELS.items() if lim >= total]
    if prefer == "bigger" and bigger:
        return bigger[0], context_tokens, "берём модель с большим лимитом"
    cut = max(limit - query_tokens, 0)
    return model, cut, f"режем контекст до {cut} токенов"


print("\n== 2. Запрос на 1000 токенов, поиск вернул 8000 токенов контекста (модель small-4k)")
print("Вариант A, идём в большую модель:", fit_context(1000, 8000, "small-4k", "bigger"))
print("Вариант Б, режем контекст:      ", fit_context(1000, 8000, "small-4k", "cut"))
print("Контекст короткий:              ", fit_context(1000, 1500, "small-4k"))


# --- 3. Gateway ---------------------------------------------------------------
class RateLimit(Exception):
    pass


def provider_a(prompt, model, max_tokens, state):
    state["a_calls"] += 1
    if state["a_calls"] <= 2:                 # первые два вызова провайдер A отвечает ошибкой rate limit
        raise RateLimit("429 Too Many Requests")
    return {"text": f"[A:{model}] {prompt[:20]}...", "tokens": min(max_tokens, 120)}


def provider_b(prompt, model, max_tokens, state):  # у B другая сигнатура ответа, gateway скрывает это
    return {"choices": [{"message": {"content": f"[B:{model}] {prompt[:20]}..."}}], "usage": min(max_tokens, 100)}


class Gateway:
    """Единая точка доступа: один метод generate() вместо SDK каждого провайдера."""

    def __init__(self):
        self.state = {"a_calls": 0}
        self.access = {"support-bot": {"model-a", "model-b"}, "report-bot": {"model-b"}}
        self.budget = {"support-bot": 300, "report-bot": 150}   # лимит токенов на приложение
        self.used = {app: 0 for app in self.access}
        self.fallback = {"model-a": "model-b"}
        self.log = []

    def _call(self, model, prompt, max_tokens):
        if model == "model-a":
            r = provider_a(prompt, model, max_tokens, self.state)
            return r["text"], r["tokens"]
        r = provider_b(prompt, model, max_tokens, self.state)
        return r["choices"][0]["message"]["content"], r["usage"]

    def generate(self, app, model, prompt, max_tokens=100):
        if model not in self.access.get(app, set()):
            self.log.append((app, model, "denied"))
            return "доступ запрещён"
        if self.used[app] + max_tokens > self.budget[app]:
            self.log.append((app, model, "over budget"))
            return "лимит токенов исчерпан"
        try:
            text, tokens = self._call(model, prompt, max_tokens)
            status = "ok"
        except RateLimit:
            fb = self.fallback[model]
            text, tokens = self._call(fb, prompt, max_tokens)
            status, model = f"fallback -> {fb}", fb
        self.used[app] += tokens
        self.log.append((app, model, status))
        return text


print("\n== 3. Gateway: доступ, лимит токенов и fallback")
gw = Gateway()
print(gw.generate("support-bot", "model-a", "Сколько стоит доставка?"))
print(gw.generate("support-bot", "model-a", "Где мой заказ?"))
print(gw.generate("support-bot", "model-a", "Как вернуть товар?"))
print(gw.generate("report-bot", "model-a", "Сводка по продажам"))     # нет доступа к model-a
print(gw.generate("report-bot", "model-b", "Сводка по продажам", 200))  # лимит 150 токенов
for row in gw.log:
    print("лог:", row)
print("Использовано токенов:", gw.used)

# --- 4. Сколько экономит router ----------------------------------------------
REQUESTS = 100_000
TOKENS = 1_500                 # токенов на запрос (вход и выход вместе)
PRICE = {"large": 5.00, "small": 0.25, "router": 0.05}   # $ за 1 млн токенов
ROUTER_TOKENS = 100
SHARE_EASY = 0.60
MISROUTED_HARD = 0.05          # доля сложных запросов, которые router ошибочно отправил в small

all_large = REQUESTS * TOKENS / 1e6 * PRICE["large"]
easy = REQUESTS * SHARE_EASY
hard = REQUESTS - easy
with_router = (easy * TOKENS / 1e6 * PRICE["small"]
               + hard * TOKENS / 1e6 * PRICE["large"]
               + REQUESTS * ROUTER_TOKENS / 1e6 * PRICE["router"])
print("\n== 4. Цена: все запросы в large против router")
print(f"Только large:          ${all_large:,.0f}")
print(f"Router + small/large:  ${with_router:,.0f}  (router сам стоит ${REQUESTS * ROUTER_TOKENS / 1e6 * PRICE['router']:.2f})")
print(f"Экономия:              ${all_large - with_router:,.0f}  ({(all_large - with_router) / all_large:.0%})")
bad = hard * MISROUTED_HARD
print(f"Но {MISROUTED_HARD:.0%} сложных запросов ушли в small по ошибке: {bad:,.0f} запросов с риском плохого ответа.")
