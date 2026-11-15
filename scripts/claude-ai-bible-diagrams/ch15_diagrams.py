#!/usr/bin/env python3
"""Chapter 15 (plugins and marketplaces) diagrams. Usage: ch15_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own (main): what is inside the release-notes plugin
D["ch15-plugin-bundle"] = dict(items=[
    Z("plugin release-notes-kit, версия 1.2.0: одна установка", -30, -70, 1170, 470),
    N("man", "plugin.json: имя, версия,\nописание, ссылки на части", 300, 0, "y", 420, 100),
    N("sk", "skill\nformat-release-notes:\nпишет заметки", 0, 230, "p", 250, 130),
    N("cmd", "slash-команда\n/release-notes:\nзапуск одной строкой", 290, 230, "pu", 250, 130),
    N("ag", "агент\nstyle-checker:\nсверяет со стилем", 580, 230, "g", 250, 130),
    N("mcp", "MCP server:\nсвязь с трекером\nзадач", 870, 230, "q", 250, 130),
    N("tr", "Трекер задач:\nчто вышло в релиз", 1260, 230, "db", 250, 130),
], edges=[E("man", "sk", dashed=True), E("man", "cmd", dashed=True), E("man", "ag", dashed=True),
          E("man", "mcp", dashed=True), E("mcp", "tr", "читает")])

# own: author -> marketplace -> install (personal or project) -> update
D["ch15-marketplace-flow"] = dict(items=[
    N("a", "Автор: проверил\nкаждую часть,\nсобрал plugin", 0, 110, "p", 260, 130),
    N("mp", "Внутренний marketplace:\ngit-репозиторий\n(одна полка)", 470, 110, "db", 300, 130),
    N("pub", "Публичный каталог\nили marketplace\nпоставщика", 470, -110, "n", 300, 120),
    N("u1", "Для себя:\nвидят только\nваши сессии", 1010, 0, "n", 280, 120),
    N("u2", "Уровень проекта:\nполучит каждый,\nкто открыл репозиторий", 1010, 220, "g", 280, 120),
    N("v", "Новая версия 1.3:\n/plugin update —\nвсе на одной версии", 470, 360, "y", 300, 120),
], edges=[E("a", "mp", "публикует"), E("mp", "u1", "install"), E("mp", "u2", "install"),
          E("pub", "u1", dashed=True), E("a", "v"), E("v", "mp")])

# own: vetting chain + governance loop
D["ch15-vetting"] = dict(items=[
    Z("Проверка до установки: по важности", -30, -70, 1320, 230),
    N("s1", "1. Источник:\nкто опубликовал?", 0, 0, "p", 270, 110),
    N("s2", "2. Содержимое:\nкакие части внутри?", 330, 0, "p", 270, 110),
    N("s3", "3. Доступы и ключи:\nнужны ли для задачи?", 660, 0, "p", 270, 110),
    N("s4", "4. Минимальные права:\nтолько чтение, узкий токен", 990, 0, "p", 270, 110),
    Z("Порядок для команды", -30, 200, 1320, 260),
    N("own", "Пятиминутный обзор:\nчто внутри, куда ходит,\nкакой ключ, кто владелец", 990, 270, "y", 270, 130),
    N("shelf", "Внутренний\nmarketplace —\nединственный источник", 660, 270, "g", 270, 130),
    N("rec", "Учёт: что\nи где установлено", 330, 270, "n", 270, 130),
    N("rev", "Раз в квартал: кто\nпользуется? Лишнее снять,\nключи отозвать", 0, 270, "r", 270, 130),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "own"), E("own", "shelf"),
          E("shelf", "rec"), E("rec", "rev")])

if __name__ == "__main__":
    run_all(D)
