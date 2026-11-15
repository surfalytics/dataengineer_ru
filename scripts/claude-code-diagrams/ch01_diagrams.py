#!/usr/bin/env python3
"""Chapter 1 (the rise of Agent-Driven Development) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: who drives what in Agent-Driven Development (main diagram of the chapter)
D["ch01-agdd-roles"] = dict(items=[
    T("Agent-Driven Development: кто что ведёт", 0, -60, 24, "#1971c2"),
    N("hum", "Человек ведёт\nнаправление и проверку:\n• какой нужен результат\n• условия успеха\n• проверка результата\n• хватит ли первого ответа",
      0, 120, "g", 340, 230),
    N("req", "Запрос:\nрезультат + условия успеха", 430, 0, "y", 320, 100),
    N("ag", "Агент ведёт\nproduction-работу:\n• читает файлы\n• пишет и правит код\n• запускает команды и тесты\n• сообщает, что сделал",
      840, 120, "p", 340, 230),
    N("rep", "Изменения + отчёт:\nчто сделано и чем\nэто подтверждено", 430, 480, "n", 320, 110),
], edges=[E("hum", "req"), E("req", "ag"), E("ag", "rep"), E("rep", "hum", "принять, поправить\nили отклонить")])

# Fig 1-2: three project scales
D["ch01-three-scales"] = dict(items=[
    N("dog", "doghouse\n\nмаленький проект\nна выходные;\nкод никто не проверяет;\nместо для vibe coding", 0, 0, "g", 320, 230),
    N("cab", "cabin\n\nскромный, но надёжный;\nявные договорённости,\nграницы и\nтестируемое ядро", 620, 0, "p", 320, 230),
    N("sky", "skyscraper\n\nбольшая система:\nкоординация, CI/CD,\nобщие процессы,\nревью безопасности", 1240, 0, "pu", 320, 230),
    N("ex1", "certificate-service,\nпервая версия", 30, 330, "n", 260, 90),
    N("ex2", "certificate-service\nсейчас", 650, 330, "n", 260, 90),
    T("Дисциплину задают ставки: цель, кто пользуется, срок жизни, ответственность.\nРазмер кода (LOC) её не задаёт.", 0, 470, 20, "#495057"),
], edges=[E("dog", "cab", "на нём начали\nзависеть люди"), E("cab", "sky", "в проекте работают\nдругие люди"),
          E("ex1", "dog", dashed=True), E("ex2", "cab", dashed=True)])

# own: Claude Code = harness around the model
D["ch01-harness"] = dict(items=[
    Z("Claude Code — это harness вокруг модели", -30, -70, 1250, 560),
    N("loop", "Цикл агента:\nзапрос → много шагов", 0, 0, "p", 260, 100),
    N("term", "Терминал:\nздесь вы с ним\nговорите", 310, 0, "n", 260, 100),
    N("ctx", "Контекст проекта:\nфайлы, история,\nCLAUDE.md", 620, 0, "db", 260, 100),
    N("tools", "Инструменты:\nфайлы, shell,\nвеб-поиск", 930, 0, "pu", 260, 100),
    N("perm", "Запросы\nразрешения перед\nрискованным шагом", 0, 190, "y", 260, 100),
    N("model", "Модель (Fable, Opus, Sonnet):\nдвижок, который читает,\nпланирует и решает", 340, 180, "g", 510, 120),
    N("mcp", "MCP:\nвнешние сервисы", 930, 190, "pu", 260, 100),
    N("hooks", "hooks:\nскрипты на события", 150, 370, "pu", 260, 100),
    N("skills", "skills:\nновые умения", 465, 370, "pu", 260, 100),
    N("ws", "Понимание\nрабочей папки", 780, 370, "n", 260, 100),
], edges=[E(a, "model", head=False) for a in ("loop", "term", "ctx", "tools", "perm", "mcp", "hooks", "skills", "ws")])

if __name__ == "__main__":
    run_all(D)
