"""Глава 20: проверка ответа модели, запасной путь к человеку и идемпотентная отправка.
Ответы модели заданы строками: так пример работает без API-ключа."""
import json

ALLOWED = ("billing", "technical", "sales")
MIN_CONFIDENCE = 0.6

# Что могла бы вернуть модель-роутер (Haiku) на каждый тикет
MODEL_ANSWERS = {
    "T-101": '{"category": "billing", "confidence": 0.93}',
    "T-102": 'Конечно! Это тикет про оплату.',            # не JSON
    "T-103": '{"category": "refunds", "confidence": 0.88}',  # нет такой категории
    "T-104": '{"category": "technical", "confidence": 0.41}',  # модель не уверена
    "T-105": '{"category": "sales"}',                      # нет поля confidence
}


def categorize_and_route(ticket_id: str) -> str:
    raw = MODEL_ANSWERS[ticket_id]
    try:
        result = json.loads(raw)
        category = result["category"]
        confidence = float(result["confidence"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return "человеку: ответ не разобрать"           # запасной путь
    if category not in ALLOWED or confidence < MIN_CONFIDENCE:
        return "человеку: чужая категория или низкая уверенность"  # запасной путь
    return f"очередь {category}"


processed = {}  # ticket_id -> результат; в жизни это таблица в базе
outbox = []     # что реально ушло клиентам


def send_reply_once(ticket_id: str, body: str) -> str:
    if ticket_id in processed:          # этот тикет уже обработан
        return processed[ticket_id] + " (повтор, ничего не делаем)"
    outbox.append((ticket_id, body))    # настоящее действие: письмо клиенту
    processed[ticket_id] = f"письмо №{len(outbox)}"
    return processed[ticket_id]


for tid in MODEL_ANSWERS:
    print(f"{tid}: {categorize_and_route(tid)}")

print()
# Вебхук пришёл дважды, а потом процесс перезапустили: три вызова на один тикет
for _ in range(3):
    print("T-101:", send_reply_once("T-101", "Деньги вернули на карту."))
print("писем отправлено:", len(outbox))
