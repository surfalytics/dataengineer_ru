#!/usr/bin/env python3
"""Chapter 19 (tool use, computer use, vision) diagrams. Usage: ch19_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Our diagram (main): one round trip of tool use
D["ch19-round-trip"] = dict(items=[
    N("app", "Ваш код\nзапрос + список tools", 0, 0, "n", 300, 110),
    N("cl", "Claude\nрешает, нужен ли\nинструмент", 460, 0, "pu", 300, 110),
    N("tu", "Блок tool_use\nимя + аргументы\nid = tu_1", 920, 0, "p", 300, 110),
    N("run", "Ваш код выполняет\nнастоящую функцию", 920, 270, "g", 300, 110),
    N("tr", "Блок tool_result\nс тем же tool_use_id", 460, 270, "p", 300, 110),
    N("ans", "Финальный ответ\nили новый tool_use", 0, 270, "y", 300, 110),
    T("Claude только просит. Выполняет всегда ваш код", 0, 430, 20, "#e03131"),
], edges=[E("app", "cl", "запрос"), E("cl", "tu"), E("tu", "run", "просьба"),
          E("run", "tr", "результат"), E("tr", "cl"), E("cl", "ans")])

# Our diagram: what to do when a tool fails
D["ch19-tool-errors"] = dict(items=[
    N("fail", "Инструмент не сработал\nбаза недоступна, нет SKU,\nтайм-аут, плохие аргументы", 360, 0, "n", 380, 120),
    N("back", "tool_result с is_error\nи понятным текстом:\n«SKU из шести цифр,\nа здесь пять»", 0, 260, "g", 340, 140),
    N("cl", "Claude меняет подход\nили уточняет\nу пользователя", 0, 520, "p", 340, 120),
    N("stop", "Остановить цикл\nзапись без прав,\nнарушена граница", 760, 260, "r", 340, 140),
    N("hum", "Сообщить человеку", 760, 520, "y", 340, 120),
], edges=[E("fail", "back", "можно исправить"), E("fail", "stop", "опасно"),
          E("back", "cl"), E("stop", "hum")])

# Our diagram: API first, computer use as the last resort
D["ch19-api-or-screen"] = dict(items=[
    N("task", "Нужно автоматизировать\nработу в программе", 380, 0, "n", 360, 110),
    N("tool", "Tool use\nбыстрее, дешевле,\nнадёжнее", 0, 260, "g", 340, 130),
    N("cu", "Computer use\nскриншот → клик → скриншот\nмедленно, дорого,\nчаще ошибается", 780, 260, "y", 360, 150),
    N("guard", "Обязательно:\nпесочница (sandbox)\nчеловек подтверждает важные шаги\nтекст на экране — данные, не команды", 740, 530, "r", 440, 150),
], edges=[E("task", "tool", "API есть"), E("task", "cu", "API нет"), E("cu", "guard")])

# Our diagram: vision for perception, tool use for action, human for exceptions
D["ch19-invoice-flow"] = dict(items=[
    N("mail", "Письмо\nсо счётом в PDF", 0, 0, "n", 300, 120),
    N("vis", "Vision\nизвлекает поставщика,\nсумму, PO, строки", 380, 0, "pu", 300, 120),
    N("sum", "Наш код:\nсумма строк\nравна итогу?", 760, 0, "y", 300, 120),
    N("po", "Tool use\nlookup_vendor\ncheck_purchase_order", 760, 300, "p", 300, 120),
    N("ok", "Провести\nавтоматически", 1220, 300, "g", 280, 120),
    N("flag", "flag_for_review\nчеловек проверяет", 220, 300, "r", 300, 120),
    T("Человек смотрит только исключения", 220, 470, 20, "#e03131"),
], edges=[E("mail", "vis"), E("vis", "sum"), E("sum", "po", "да"), E("sum", "flag", "нет"),
          E("po", "ok", "совпало"), E("po", "flag", "расхождение")])

if __name__ == "__main__":
    run_all(D)
