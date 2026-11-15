"""Глава 17: Messages API без ключа и без оплаты.
Настоящий SDK `anthropic` отправляет запросы, но их ловит поддельный HTTP-транспорт.
Так видно, что именно уходит в API, как растёт история и как SDK повторяет запросы.
Ответы и число токенов здесь выдуманы транспортом, это не ответы Claude."""
import json

import anthropic
import httpx2

calls = []          # тела запросов, которые ушли в "API"
plan = []           # какие HTTP-коды вернуть по очереди; пусто = 200


def fake_api(request: httpx2.Request) -> httpx2.Response:
    body = json.loads(request.content)
    calls.append(body)
    status = plan.pop(0) if plan else 200
    if status != 200:
        kind = {400: "invalid_request_error", 429: "rate_limit_error", 529: "overloaded_error"}[status]
        return httpx2.Response(status, headers={"retry-after-ms": "10"},
                               json={"type": "error", "error": {"type": kind, "message": kind}})
    # условные токены: одно слово = один токен
    words = sum(len(str(m["content"]).split()) for m in body["messages"])
    words += len(str(body.get("system", "")).split())
    n = len(calls)
    return httpx2.Response(200, json={
        "id": f"msg_{n}", "type": "message", "role": "assistant", "model": body["model"],
        "content": [{"type": "text", "text": f"ответ номер {n}"}],
        "stop_reason": "end_turn", "stop_sequence": None,
        "usage": {"input_tokens": words, "output_tokens": 3}})


client = anthropic.Anthropic(api_key="sk-ant-fake", max_retries=4,
                             http_client=httpx2.Client(transport=httpx2.MockTransport(fake_api)))

print("1. Что уходит в API")
msg = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    system="Ты аналитик службы доставки. Отвечай коротко.",
    messages=[{"role": "user", "content": "Сколько точек добавит третий фургон по 22 точки?"}],
)
print("  поля запроса:", ", ".join(sorted(calls[-1])))
print("  текст ответа:", msg.content[0].text, "| usage:", msg.usage.input_tokens, "/", msg.usage.output_tokens)

print("2. История хранится у вас")
history = [{"role": "user", "content": "Придумай название пекарни в Лиссабоне"}]
for question in ["Дай ещё три в том же стиле", "Выбери лучшее и объясни почему"]:
    reply = client.messages.create(model="claude-sonnet-4-6", max_tokens=200, messages=history)
    print(f"  сообщений: {len(history)}, роли: {'-'.join(m['role'][0] for m in history)},"
          f" input_tokens: {reply.usage.input_tokens}")
    history.append({"role": "assistant", "content": reply.content[0].text})
    history.append({"role": "user", "content": question})
reply = client.messages.create(model="claude-sonnet-4-6", max_tokens=200, messages=history)
print(f"  сообщений: {len(history)}, роли: {'-'.join(m['role'][0] for m in history)},"
      f" input_tokens: {reply.usage.input_tokens}")

print("3. Ошибки и повторы")
for title, codes in [("перегрузка 529, 529, потом успех", [529, 529]),
                     ("лимит 429 пять раз подряд", [429] * 5),
                     ("плохой запрос 400", [400])]:
    plan[:] = codes
    before = len(calls)
    try:
        client.messages.create(model="claude-sonnet-4-6", max_tokens=100,
                               messages=[{"role": "user", "content": "Итоги планёрки"}])
        result = "успех"
    except anthropic.RateLimitError:
        result = "RateLimitError: отложить задачу в очередь"
    except anthropic.APIStatusError as e:
        result = f"{type(e).__name__} {e.status_code}: не повторять, записать в лог"
    print(f"  {title}: попыток {len(calls) - before}, итог: {result}")
