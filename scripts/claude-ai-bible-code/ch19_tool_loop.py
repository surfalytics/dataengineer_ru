"""Глава 19: цикл tool use без API-ключа.
Вместо Claude здесь заготовленные ответы в том же формате блоков: tool_use, tool_result, text.
Показано: параллельные вызовы, ошибка с is_error и остановка цикла на опасном инструменте."""
import json
from concurrent.futures import ThreadPoolExecutor

STOCK = {"A-100001": 14, "A-100002": 0}
PRICE = {"A-100001": 39.90, "A-100002": 12.50}


def get_stock(sku):
    if sku not in STOCK:
        raise LookupError(f"Нет товара с SKU '{sku}'. SKU — буква, дефис и шесть цифр, "
                          "а здесь пять. Попроси пользователя проверить SKU.")
    return f"{sku}: на складе {STOCK[sku]} шт."


def get_price(sku):
    return f"{sku}: цена ${PRICE[sku]:.2f}"


SAFE_TOOLS = {"get_stock": get_stock, "get_price": get_price}  # только чтение


def fake_claude(scenario, turn, messages):
    """Заготовленные ответы модели. Настоящий вызов API — в тексте главы."""
    if scenario == "склад" and turn == 1:  # три независимых вызова за один ход
        calls = [("get_stock", "A-100001"), ("get_price", "A-100001"), ("get_stock", "A-10002")]
        return {"stop_reason": "tool_use", "content": [
            {"type": "tool_use", "id": f"tu_{i}", "name": n, "input": {"sku": s}}
            for i, (n, s) in enumerate(calls, 1)]}
    if scenario == "склад":
        bad = [r for r in messages[-1]["content"] if r.get("is_error")]
        text = "A-100001: 14 шт. по $39.90. "
        text += "Второй SKU не найден: уточните его, пожалуйста." if bad else ""
        return {"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}
    return {"stop_reason": "tool_use", "content": [  # сценарий «удаление»
        {"type": "tool_use", "id": "tu_9", "name": "delete_order", "input": {"order_id": "O-77"}}]}


def run_one(block):
    """Наш код решает, что выполнять. Ошибка поиска уходит модели, а не роняет программу."""
    try:
        return {"type": "tool_result", "tool_use_id": block["id"],
                "content": SAFE_TOOLS[block["name"]](**block["input"])}
    except LookupError as e:
        return {"type": "tool_result", "tool_use_id": block["id"], "is_error": True, "content": str(e)}


def agent(scenario):
    messages = [{"role": "user", "content": "Сколько стоят и есть ли на складе A-100001 и A-10002?"}]
    for turn in range(1, 5):
        resp = fake_claude(scenario, turn, messages)
        if resp["stop_reason"] != "tool_use":
            print("ответ:", resp["content"][0]["text"])
            return
        calls = [b for b in resp["content"] if b["type"] == "tool_use"]
        print(f"ход {turn}: модель просит инструменты:", ", ".join(c["name"] for c in calls))
        unknown = [c["name"] for c in calls if c["name"] not in SAFE_TOOLS]
        if unknown:  # опасный или чужой инструмент: не импровизируем, зовём человека
            print("СТОП: инструмент", unknown[0], "не разрешён. Цикл остановлен, нужен человек.")
            return
        with ThreadPoolExecutor() as pool:  # независимые вызовы — одновременно
            results = list(pool.map(run_one, calls))
        for r in results:
            print("  ", json.dumps(r, ensure_ascii=False))
        messages.append({"role": "assistant", "content": resp["content"]})
        messages.append({"role": "user", "content": results})  # все результаты одним сообщением


for name in ("склад", "удаление"):
    print(f"--- сценарий «{name}»")
    agent(name)
