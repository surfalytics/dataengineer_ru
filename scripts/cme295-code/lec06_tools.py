"""Лекция 6: вызов инструментов. Модель видит описание функции, а код не видит.
«Модель» здесь — простой сценарий, а не настоящая LLM: важен порядок шагов."""
import inspect
import json


def find_my_position() -> dict:
    """Возвращает координаты пользователя: lat и lon."""
    return {"lat": 37.43, "lon": -122.17}


def find_teddy_bear(lat: float, lon: float, radius_km: float = 1.0) -> list:
    """Ищет плюшевых медведей рядом с точкой. Возвращает name, distance_m, mood."""
    return [{"name": "Teddy", "distance_m": 350, "mood": "happy"}]


TOOLS = {f.__name__: f for f in (find_my_position, find_teddy_bear)}


def tool_spec(fn):
    """То, что получает модель: имя, описание и типы аргументов. Тело функции не попадает."""
    params = {n: p.annotation.__name__ for n, p in inspect.signature(fn).parameters.items()}
    return {"name": fn.__name__, "description": fn.__doc__, "arguments": params}


def fake_llm(messages):
    """Сценарий вместо модели: сначала координаты, потом поиск, потом ответ."""
    calls = [m for m in messages if m["role"] == "tool"]
    if len(calls) == 0:
        return {"tool": "find_my_position", "args": {}}
    if len(calls) == 1:
        return {"tool": "find_teddy_bear", "args": calls[0]["content"]}
    bear = calls[1]["content"][0]
    return {"text": f"Рядом с вами {bear['name']}: {bear['distance_m']} м, настроение {bear['mood']}."}


print("Что видит модель:")
for fn in TOOLS.values():
    print(" ", json.dumps(tool_spec(fn), ensure_ascii=False))

messages = [{"role": "user", "content": "Найди плюшевого медведя рядом со мной"}]
for step in range(1, 6):
    out = fake_llm(messages)
    if "text" in out:
        print(f"шаг {step}: ответ пользователю -> {out['text']}")
        break
    result = TOOLS[out["tool"]](**out["args"])
    print(f"шаг {step}: вызов {out['tool']}({out['args']}) -> {result}")
    messages.append({"role": "tool", "content": result})
