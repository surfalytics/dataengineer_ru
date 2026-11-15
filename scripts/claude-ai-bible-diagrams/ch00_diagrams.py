#!/usr/bin/env python3
"""Overview page: book map (6 parts, 22 chapters). Usage: ch00_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

PARTS = [
    ("Часть I.\nОснова", "n", ["1. Машина\nс совестью", "2. Семейство\nмоделей", "3. Claude против\nконкурентов", "4. Планы, цены\nи приватность"]),
    ("Часть II.\nРемесло разговора", "p", ["5. Как писать\nprompt", "6. Продвинутые\nприёмы", "7. Проекты\nи память", "8. Artifacts\nи длинные тексты"]),
    ("Часть III.\nГде работает Claude", "db", ["9. Приложения\nи голос", "10. Cowork", "11. Claude\nin Chrome", "12. Claude\nin Excel"]),
    ("Часть IV.\nНабор строителя", "pu", ["13. Claude Code", "14. Skills", "15. Plugins\nи marketplaces", "16. MCP"]),
    ("Часть V.\nПлатформа\nразработчика", "y", ["17. Anthropic API", "18. Agent SDK", "19. Tool use,\ncomputer use\nи зрение", "20. Агенты\nи автоматизация"]),
    ("Часть VI.\nНа практике", "g", ["21. Сценарии\nпо отраслям", "22. Ограничения\nи риски"]),
]
items, edges = [], []
items.append(Z("Пользоваться Claude: чат, prompt, приложения", -30, -70, 1390, 520))
items.append(Z("Строить на Claude и применять в работе: код, агенты, API", -30, 490, 1390, 520))
for i, (part, k, chs) in enumerate(PARTS):
    y = i * 160 + (60 if i >= 3 else 0)
    items.append(N(f"p{i}", part, 0, y, k, 280, 110))
    for j, ch in enumerate(chs):
        items.append(N(f"c{i}{j}", ch, 340 + j * 250, y, k, 220, 110))
    if i and i != 3:  # no arrow across the zone border: it would cross the zone title
        edges.append(E(f"p{i-1}", f"p{i}"))
D["ch00-book-map"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
