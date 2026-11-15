"""Глава 6: проверяем JSON от модели на своей стороне и готовим сообщение для исправления.
Ответы модели здесь заданы строками: так пример работает без API-ключа."""
import json

SCHEMA = {  # поле -> допустимые значения (None = любая строка или null)
    "customer_name": None,
    "product": None,
    "issue_category": {"billing", "shipping", "technical", "other"},
    "urgency": {"low", "medium", "high"},
    "refund_requested": {True, False},
}


def check(raw: str) -> list[str]:
    """Возвращает список ошибок. Пустой список = ответ годится."""
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return [f"ответ не JSON: {e.msg}"]
    errors = [f"нет поля '{f}'" for f in SCHEMA if f not in obj]
    errors += [f"лишнее поле '{f}'" for f in obj if f not in SCHEMA]
    for field, allowed in SCHEMA.items():
        value = obj.get(field)
        if allowed is not None and field in obj and value not in allowed:
            ok = ", ".join(sorted(map(str, allowed)))
            errors.append(f"поле '{field}' = {value!r}, допустимо: {ok}")
    return errors


answers = {
    "ответ 1": '{"customer_name": "Anya", "product": "dashboard widget", '
               '"issue_category": "technical", "urgency": "high", "refund_requested": false}',
    "ответ 2": '{"customer_name": "Anya", "product": null, '
               '"issue_category": "technical", "urgency": "urgent", "refund_requested": false}',
    "ответ 3": 'Конечно! Вот JSON: {"customer_name": "Anya"}',
}

for name, raw in answers.items():
    errors = check(raw)
    if not errors:
        print(f"{name}: OK, отдаём дальше")
        continue
    print(f"{name}: отправляем модели на исправление:")
    for e in errors:
        print(f"  - {e}")
