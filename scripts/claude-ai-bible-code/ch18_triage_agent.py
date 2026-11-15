#!/usr/bin/env python3
"""Глава 18: цикл агента без API-ключа.

Модель заменена правилами (fake_model), всё остальное как в Agent SDK:
инструменты из функций с docstring, цикл «решает -> инструмент -> видит результат»,
проверка перед каждым вызовом (can_run), журнал событий (on_event) и лимит шагов.
Запуск: python3 -I scripts/claude-ai-bible-code/ch18_triage_agent.py
"""
import tempfile
from pathlib import Path

TICKETS = {
    "ticket_4471.txt": "С карты дважды списали оплату за март. Верните лишний платёж.",
    "ticket_4472.txt": "Не могу войти в аккаунт после смены пароля.",
}
CATEGORIES = {"billing": ["оплат", "списал", "счёт"], "account": ["аккаунт", "пароль", "войти"]}


# ---------- инструменты: имя, описание (docstring) и сама функция ----------
def make_tools(folder: Path):
    def read_ticket(filename: str) -> str:
        """Прочитать полный текст тикета из папки tickets/."""
        path = folder / filename
        return path.read_text(encoding="utf-8") if path.exists() else f"Тикет {filename} не найден."

    def log_summary(line: str) -> str:
        """Дописать одну строку итога в triage_log.txt."""
        with open(folder / "triage_log.txt", "a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
        return "Записано."

    def delete_ticket(filename: str) -> str:
        """Удалить тикет. Опасно: нужна проверка человеком."""
        (folder / filename).unlink()
        return f"Тикет {filename} удалён."

    return {fn.__name__: fn for fn in (read_ticket, log_summary, delete_ticket)}


# ---------- «модель»: правила вместо Claude ----------
def fake_model(goal: str, history: list) -> dict:
    """Возвращает {'tool': имя, 'args': {...}} или {'final': текст}."""
    filename = goal.split()[-1]
    if "удали" in goal and not history:
        return {"tool": "delete_ticket", "args": {"filename": filename}}
    if not history or history[-1]["tool"] == "delete_ticket":
        return {"tool": "read_ticket", "args": {"filename": filename}}
    last = history[-1]
    if last["tool"] == "read_ticket":
        text = last["result"].lower()
        if "не найден" in text:
            return {"tool": "read_ticket", "args": {"filename": filename}}  # «застрял»
        category = next((c for c, words in CATEGORIES.items()
                         if any(w in text for w in words)), "other")
        urgency = "high" if category == "billing" else "medium"
        line = f"{filename} | {category} | {urgency} | {last['result'].split('.')[0]}"
        return {"tool": "log_summary", "args": {"line": line}}
    return {"final": "Тикет разобран, строка записана в журнал."}


# ---------- ограждения ----------
def can_run(tool_name: str, args: dict) -> bool:
    """Вызывается перед каждым инструментом. False — вызов запрещён."""
    if tool_name == "delete_ticket":
        print(f"  [gate] агент хочет удалить {args['filename']}. Человек ответил: нет")
        return False
    return True


def on_event(kind: str, text: str) -> None:
    print(f"  [{kind}] {text}")


# ---------- цикл агента ----------
def run_agent(goal: str, tools: dict, max_iterations: int = 8) -> str:
    history = []
    for step in range(1, max_iterations + 1):
        decision = fake_model(goal, history)                      # 1. модель решает
        if "final" in decision:
            return decision["final"]
        name, args = decision["tool"], decision["args"]
        on_event("tool_call", f"шаг {step}: {name}({args})")
        if not can_run(name, args):
            result = "Отказано: это действие требует одобрения."
        else:
            result = tools[name](**args)                          # 2. инструмент работает
        on_event("tool_result", result[:60])
        history.append({"tool": name, "args": args, "result": result})  # 3. модель видит итог
    return f"Остановлен: сработал лимит, max_iterations={max_iterations}."   # 4. или повтор


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for name, text in TICKETS.items():
            (folder / name).write_text(text, encoding="utf-8")
        tools = make_tools(folder)
        for goal, limit in [("Разбери тикет ticket_4471.txt", 8),
                            ("Разбери и удали тикет ticket_4472.txt", 8),
                            ("Разбери тикет ticket_9999.txt", 3)]:
            print(f"Цель: {goal}")
            print(f"Ответ: {run_agent(goal, tools, limit)}\n")
        print("triage_log.txt:")
        print((folder / "triage_log.txt").read_text(encoding="utf-8"), end="")
        print("Тикетов в папке:", len(list(folder.glob("ticket_*.txt"))))
