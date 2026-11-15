#!/usr/bin/env python3
"""Chapter 2 (getting started with Claude Code) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 2-2: the request loop; read-only returns at once, writes and shell pass the permission gate (main diagram)
D["ch02-request-loop"] = dict(items=[
    Z("Нужно ваше согласие", 1350, -70, 310, 680),
    N("n1", "1. Вы описываете\nнужный результат", 0, 0, "y"),
    N("n2", "2. Claude Code\nпланирует шаги", 320, 0, "p"),
    N("n3", "3. Читает файлы\nи папки проекта", 640, 0, "db"),
    N("n4", "4. Какое\nдействие?", 960, -20, "pu", 250, 140, "diamond"),
    N("n5", "5. Запрос\nразрешения\n(permission gate)", 1380, 0, "r"),
    N("ans", "Ответ сразу,\nбез разрешения", 960, 260, "g"),
    N("n6", "6. Вы: одобрить,\nотклонить, изменить", 1380, 260, "y"),
    N("n7", "7. Изменение\nв проекте", 1380, 480, "db"),
    N("n8", "8. Отчёт\nо сделанном", 960, 480, "g"),
    N("rep", "Вы смотрите,\nуточняете,\nповторяете", 0, 480, "y"),
], edges=[E("n1", "n2"), E("n2", "n3"), E("n3", "n4"),
          E("n4", "ans", "только чтение"), E("n4", "n5", "запись\nили shell"),
          E("n5", "n6"), E("n6", "n7", "одобрено"), E("n7", "n8"),
          E("ans", "rep"), E("n8", "rep"), E("rep", "n1", "новый запрос", dashed=True)])

# own: from install to the first session
D["ch02-first-launch"] = dict(items=[
    N("i", "1. Установка:\nnative installer\n(обновляется сам)", 0, 0, "p", 260, 120),
    N("v", "2. claude --version\nв новом терминале", 340, 0, "p", 260, 120),
    N("fix", "Нет команды:\nдобавить ~/.local/bin\nв PATH", 340, 230, "r", 260, 120),
    N("doc", "Что-то не так:\nclaude doctor", 680, 230, "q", 260, 120),
    N("c", "3. claude в папке\nпроекта: стиль,\nдоверие к папке", 680, 0, "p", 260, 120),
    N("l", "4. Вход", 1020, 10, "pu", 200, 100),
    N("sub", "Обычно: подписка\nPro / Max,\nвход через браузер", 1320, -140, "g", 270, 120),
    N("key", "Можно: API key,\nоплата за токены,\nбыстро дорожает", 1320, 140, "r", 270, 120),
    N("s", "5. Сессия:\nэкран приветствия,\n/help", 1690, 0, "g", 260, 120),
], edges=[E("i", "v"), E("v", "c"), E("v", "fix", "не найдено"),
          E("c", "doc", "проблемы", dashed=True), E("c", "l"),
          E("l", "sub"), E("l", "key"), E("sub", "s"), E("key", "s")])

if __name__ == "__main__":
    run_all(D)
