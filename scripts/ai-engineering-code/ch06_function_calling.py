"""Глава 6: function calling и проверки безопасности при вызове tools.
Показывает: описание tools (имя, параметры, документация), режимы tool_choice (required / none / auto),
ответ модели с tool_calls, проверку вызова перед выполнением (неверный tool, неверные параметры),
разделение read- и write-действий и подтверждение человеком.
Модель здесь — mock: простая функция с правилами. В реальной системе вместо mock_model()
вы вызываете API модели с теми же tools и tool_choice (пример блока API — в конце файла, в комментарии).
Запуск: python3 -I scripts/ai-engineering-code/ch06_function_calling.py   (только стандартная библиотека)"""
import json
import re

print("== 1. Описываем tools (как в API: имя, описание, параметры)")


def lbs_to_kg(lbs):
    return round(lbs * 0.45359237, 2)


def ft_to_meters(ft):
    return round(ft * 0.3048, 2)


def delete_orders(order_ids):
    return f"удалено заказов: {len(order_ids)}"


TOOLS = {
    "lbs_to_kg": dict(fn=lbs_to_kg, access="read", description="Convert from pounds to kilograms",
                      params={"lbs": "number"}),
    "ft_to_meters": dict(fn=ft_to_meters, access="read", description="Convert from feet to meters",
                         params={"ft": "number"}),
    "delete_orders": dict(fn=delete_orders, access="write", description="Delete orders by id",
                          params={"order_ids": "list"}),
}
for name, t in TOOLS.items():
    print(f"{name}({', '.join(f'{p}: {ty}' for p, ty in t['params'].items())}) [{t['access']}] — {t['description']}")

print("\n== 2. Mock-модель: по запросу решает, какой tool вызвать, и отдаёт имя и аргументы строкой JSON")


def mock_model(query, tool_names, tool_choice="auto"):
    """Возвращает словарь в форме ответа API: finish_reason + tool_calls или текст."""
    if tool_choice == "none":
        return {"finish_reason": "stop", "content": "Отвечаю без tools: примерно 18 кг.", "tool_calls": []}
    call = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:pounds|lbs)", query)
    if m and "lbs_to_kg" in tool_names:
        call = {"name": "lbs_to_kg", "arguments": json.dumps({"lbs": float(m.group(1))})}
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:feet|ft)", query)
    if m and "ft_to_meters" in tool_names:
        call = {"name": "ft_to_meters", "arguments": json.dumps({"ft": float(m.group(1))})}
    if call is None and tool_choice == "required":
        call = {"name": tool_names[0], "arguments": json.dumps({})}  # обязаны вызвать хоть что-то
    if call is None:
        return {"finish_reason": "stop", "content": "Tool не нужен.", "tool_calls": []}
    return {"finish_reason": "tool_calls", "content": None, "tool_calls": [{"function": call, "type": "function"}]}


for choice in ("auto", "none", "required"):
    r = mock_model("How many kg are 40 pounds?", ["lbs_to_kg", "ft_to_meters"], choice)
    print(f"tool_choice={choice:8s} -> finish_reason={r['finish_reason']}, tool_calls={r['tool_calls']}")
r = mock_model("Say hello", ["lbs_to_kg", "ft_to_meters"], "required")
print("required без подходящего tool -> модель вынуждена вызвать tool с пустыми аргументами:", r["tool_calls"][0]["function"])

print("\n== 3. Проверяем вызов ДО выполнения")


def validate_call(call):
    """Возвращает список проблем. Пустой список — вызов допустим."""
    name, args = call["name"], json.loads(call["arguments"])
    if name not in TOOLS:
        return [f"invalid tool: {name!r} нет в списке tools"]
    problems = []
    expected = TOOLS[name]["params"]
    for p in expected:
        if p not in args:
            problems.append(f"пропущен параметр {p!r}")
    for p, v in args.items():
        if p not in expected:
            problems.append(f"лишний параметр {p!r}")
        elif expected[p] == "number" and not isinstance(v, (int, float)):
            problems.append(f"параметр {p!r} должен быть числом, пришло {v!r}")
        elif expected[p] == "list" and not isinstance(v, list):
            problems.append(f"параметр {p!r} должен быть списком")
    return problems


cases = {
    "верный вызов": {"name": "lbs_to_kg", "arguments": '{"lbs": 40}'},
    "invalid tool": {"name": "bing_search", "arguments": '{"q": "weather"}'},
    "valid tool, invalid params": {"name": "lbs_to_kg", "arguments": '{"lbs": 40, "extra": 1}'},
    "неверный тип": {"name": "lbs_to_kg", "arguments": '{"lbs": "forty"}'},
    "valid tool, wrong value": {"name": "lbs_to_kg", "arguments": '{"lbs": 100}'},
}
for label, call in cases.items():
    print(f"{label:28s} -> {validate_call(call) or 'схема в порядке'}")
print("Последний случай (lbs=100 вместо 40) схема не поймает: значение выбрала модель. Его проверяют отдельно:")
query = "How many kg are 40 pounds?"
numbers_in_query = {float(x) for x in re.findall(r"\d+(?:\.\d+)?", query)}
args = json.loads(cases["valid tool, wrong value"]["arguments"])
print(f"  числа в запросе: {sorted(numbers_in_query)}; аргумент lbs = {args['lbs']} -> "
      f"{'ok' if args['lbs'] in numbers_in_query else 'подозрительно: такого числа нет в запросе'}")

print("\n== 4. Read и write: write-действия идут через подтверждение человека")
AUDIT_LOG = []


def run_tool(call, approve=None):
    problems = validate_call(call)
    if problems:
        return f"отклонено: {problems}"
    tool = TOOLS[call["name"]]
    args = json.loads(call["arguments"])
    if tool["access"] == "write" and not (approve and approve(call)):
        AUDIT_LOG.append((call["name"], args, "ждёт подтверждения"))
        return "write-действие не выполнено: нужно подтверждение человека"
    AUDIT_LOG.append((call["name"], args, "выполнено"))
    return tool["fn"](**args)


print("read :", run_tool({"name": "lbs_to_kg", "arguments": '{"lbs": 40}'}))
delete_call = {"name": "delete_orders", "arguments": '{"order_ids": [1, 2, 3]}'}
print("write без подтверждения:", run_tool(delete_call))
print("write с подтверждением  :", run_tool(delete_call, approve=lambda c: True))
print("журнал вызовов:")
for entry in AUDIT_LOG:
    print("  ", entry)

print("\n== 5. Полный цикл: запрос -> tool_calls -> выполнение -> ответ")
r = mock_model("How many kg are 40 pounds?", ["lbs_to_kg", "ft_to_meters"], "auto")
call = r["tool_calls"][0]["function"]
result = run_tool(call)
print(f"модель выбрала {call['name']}({call['arguments']}); результат: {result}")
print(f"ответ пользователю: «40 фунтов — это около {result} кг»")

# --- Как это выглядит с настоящей моделью (в этом файле не выполняется, нужен ключ API): ---
# response = model_client.chat.completions.create(
#     model=MODEL_NAME, messages=[{"role": "user", "content": query}],
#     tools=[lbs_to_kg_declaration, ft_to_meters_declaration], tool_choice="auto")
# call = response.choices[0].message.tool_calls[0].function   # имя и аргументы
# result = run_tool({"name": call.name, "arguments": call.arguments})
