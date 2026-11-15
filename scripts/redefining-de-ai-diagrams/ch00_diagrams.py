#!/usr/bin/env python3
"""Overview page diagram: book map (Early Release: chapters 1-2 out, 3-9 planned).
Usage: python3 scripts/redefining-de-ai-diagrams/ch00_diagrams.py"""
from excb import N, E, Z, T, run_all

D = {}

D["ch00-book-map"] = dict(items=[
    Z("Основа: вышли в Early Release", 0, 0, 860, 230),
    N("c1", "Глава 1\nИнжиниринг данных\nв компании\nв эпоху AI", 25, 60, "p", 330, 140),
    N("c2", "Глава 2\nЭволюция AI\nи инструменты:\nLLM, RAG, MCP, агенты", 505, 60, "p", 330, 140),
    Z("Жизненный цикл проекта данных с AI: главы 3–9 ещё не вышли", 0, 340, 1520, 360),
    N("c3", "3. Планирование\n(Planning\nwith Intent)", 25, 400, "n", 260, 120),
    N("c4", "4. Проектирование\n(Designing\nwith Context)", 325, 400, "n", 260, 120),
    N("c5", "5. Фундамент\n(Building\nthe Foundation)", 625, 400, "n", 260, 120),
    N("c6", "6. Аналитика\n(Building\nwith Insight)", 925, 400, "n", 260, 120),
    N("c7", "7. Проверка\n(Validating\nwith Trust)", 1225, 400, "n", 270, 120),
    N("c9", "9. Поддержка\n(Supporting\nin Real Time)", 925, 560, "n", 260, 120),
    N("c8", "8. Выкладка\n(Deploying\nwith Confidence)", 1225, 560, "n", 270, 120),
    T("Названия глав 3–9 — из черновика оглавления, они могут измениться", 25, 730, 18, "#868e96"),
], edges=[E("c1", "c2"), E("c2", "c5", "база для глав 3–9", dashed=True),
          E("c3", "c4"), E("c4", "c5"), E("c5", "c6"), E("c6", "c7"), E("c7", "c8"), E("c8", "c9")])

if __name__ == "__main__":
    run_all(D)
