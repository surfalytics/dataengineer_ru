"""Лекция 6: цикл ReAct (observe, plan, act) на примере термостата для замёрзшего медведя.
«Модель» — сценарий, комната — словарь. Цикл и условие остановки настоящие."""
room = {"temp": 15.0}
COMFORT = 22.0


def get_temperature():
    return room["temp"]


def increase_temperature(delta):
    room["temp"] += delta
    return room["temp"]


def fake_llm(history):
    """Смотрит на последнее наблюдение и решает: ещё действие или ответ."""
    last = history[-1]
    if last["kind"] == "user":
        return "Медведю холодно, значит, нужна температура.", ("get_temperature", {})
    if last["kind"] == "observation" and last["value"] < COMFORT:
        need = round(COMFORT - last["value"], 1)
        return f"Сейчас {last['value']}, нужно {COMFORT}. Поднимаю на {need}.", ("increase_temperature", {"delta": need})
    return f"Теперь {last['value']}, это комфортно.", None


TOOLS = {"get_temperature": get_temperature, "increase_temperature": increase_temperature}
history = [{"kind": "user", "value": "Медведю холодно"}]
for step in range(1, 7):  # лимит шагов: защита от бесконечного цикла
    thought, action = fake_llm(history)
    print(f"шаг {step}. Plan: {thought}")
    if action is None:
        print("Ответ пользователю: в комнате комфортно.")
        break
    name, args = action
    value = TOOLS[name](**args)
    print(f"        Act: {name}({args}) -> Observe: {value}")
    history.append({"kind": "observation", "value": value})
