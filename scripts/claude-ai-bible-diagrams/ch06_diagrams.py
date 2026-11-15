#!/usr/bin/env python3
"""Chapter 6 (advanced prompting and reasoning control) diagrams. Usage: ch06_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Our diagram (main): match the controls to task difficulty
D["ch06-match-difficulty"] = dict(items=[
    N("q", "Насколько сложна задача\nи дорога ли ошибка?", 380, 0, "n", 420, 100),
    N("easy", "Простая, массовая\nклассификация, извлечение\n\nHaiku\nбез extended thinking\nнизкая temperature", 0, 230, "g", 340, 220),
    N("mid", "Обычная работа\nписьма, анализ, тексты\n\nSonnet\nнастройки по умолчанию", 420, 230, "p", 340, 220),
    N("hard", "Сложная, много шагов,\nошибка стоит дорого\n\nOpus\nextended thinking\nрассуждение до вывода", 840, 230, "y", 340, 220),
    T("Ошибка в обе стороны: платить за глубину на простой задаче или экономить на сложной", 0, 490, 20, "#e03131"),
], edges=[E("q", "easy"), E("q", "mid"), E("q", "hard")])

# Our diagram: validate structured output, short correction loop
D["ch06-json-loop"] = dict(items=[
    N("p", "Prompt\nточная схема, пример,\nnull вместо пропуска", 0, 0, "p", 280, 120),
    N("c", "Claude", 400, 10, "pu", 200, 100),
    N("v", "Проверка схемы\nна нашей стороне", 720, 0, "y", 280, 120),
    N("ok", "Дальше по\nконвейеру", 1120, 10, "g", 220, 100),
    N("err", "Конкретная ошибка:\n«urgency = urgent,\nдопустимо low, medium, high»", 640, 260, "r", 440, 120),
], edges=[E("p", "c"), E("c", "v", "JSON"), E("v", "ok", "OK"), E("v", "err", "ошибка"),
          E("err", "c", "исправь")])

# Our diagram: prompt chain with checkpoints
D["ch06-prompt-chain"] = dict(items=[
    N("s1", "Шаг 1\nкакие типы\nконкурентов и\nпо каким факторам", 0, 0, "p", 260, 140),
    N("s2", "Шаг 2\nсильные и слабые\nстороны, угроза\nот 1 до 5", 480, 0, "p", 260, 140),
    N("s3", "Шаг 3\nтри стратегии\nпозиционирования\nи риски", 960, 0, "p", 260, 140),
    N("k1", "Проверка: убрать\nлишний тип, пока\nошибка дешёвая", 0, 250, "y", 260, 110),
    N("k2", "Проверка: оценки\nугрозы разумны?", 480, 250, "y", 260, 110),
    T("Вывод каждого шага идёт на вход следующему", 0, 400, 20, "#1971c2"),
], edges=[E("s1", "s2", "вывод"), E("s2", "s3", "вывод"),
          E("s1", "k1", dashed=True), E("s2", "k2", dashed=True)])

if __name__ == "__main__":
    run_all(D)
