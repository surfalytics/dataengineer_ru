#!/usr/bin/env python3
"""Overview page diagram: book map (Early Release: chapters 1-4 out, 5-12 planned).
Usage: python3 scripts/claude-code-diagrams/ch00_diagrams.py"""
from excb import N, E, Z, T, run_all

D = {}

D["ch00-book-map"] = dict(items=[
    Z("Вышли в Early Release: главы 1–4 (doghouse и первый шаг к cabin)", 0, 0, 1240, 220),
    N("c1", "1. Подъём\nAgent-Driven\nDevelopment", 25, 60, "g", 270, 130),
    N("c2", "2. Начало работы:\nустановка и\nпервый doghouse", 330, 60, "g", 270, 130),
    N("c3", "3. Как говорить\nс Claude Code:\nprompt, plan mode", 635, 60, "g", 270, 130),
    N("c4", "4. Когда vibe coding\nне хватает: тесты,\nCLAUDE.md, память", 940, 60, "p", 280, 130),
    Z("Ещё не вышли: главы 5–12 (cabin и skyscraper)", 0, 320, 1240, 420),
    N("c8", "8. Чужая\nкодовая база", 25, 380, "n", 270, 120),
    N("c7", "7. Subagents,\nagent teams,\nplugins", 330, 380, "n", 270, 120),
    N("c6", "6. Skills\nи hooks", 635, 380, "n", 270, 120),
    N("c5", "5. Права,\nбезопасность,\nграницы доверия", 940, 380, "n", 280, 120),
    N("c9", "9. MCP и внешние\nинтеграции", 25, 580, "n", 270, 120),
    N("c10", "10. От prompt\nдо pull request", 330, 580, "n", 270, 120),
    N("c11", "11. Ревью, тесты,\nотладка, восстановление", 635, 580, "n", 270, 120),
    N("c12", "12. За пределами\nClaude Code", 940, 580, "n", 280, 120),
    T("Названия глав 5–12 — из черновика оглавления, они могут измениться", 25, 770, 18, "#868e96"),
], edges=[E("c1", "c2"), E("c2", "c3"), E("c3", "c4"), E("c4", "c5", dashed=True),
          E("c5", "c6"), E("c6", "c7"), E("c7", "c8"), E("c8", "c9"), E("c9", "c10"), E("c10", "c11"), E("c11", "c12")])

if __name__ == "__main__":
    run_all(D)
