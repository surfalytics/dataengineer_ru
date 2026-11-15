#!/usr/bin/env python3
"""Chapter 12 (Claude in Excel) diagrams. Usage: ch12_diagrams.py [name ...]  (no args = all)
The book chapter has no figures: all three diagrams are our own."""
from excb import N, E, Z, T, run_all

D = {}

# own (main): who does what. Agent does the mechanics, the human keeps judgment and checks
D["ch12-division-of-labor"] = dict(items=[
    Z("Человек: суждение и проверка", -25, -70, 1610, 200),
    N("h1", "1. Бриф: какой\nнужен результат", 0, 0, "p", 260, 100),
    N("h3", "4. Решает по пометкам:\nчто удалить, что оставить", 640, 0, "q", 260, 100),
    N("h4", "5. Проверяет цифры:\nпорядок, сверка", 960, 0, "q", 260, 100),
    N("dec", "Цифра уходит\nв решение", 1280, 0, "g", 260, 100),
    Z("Агент: механическая работа", -25, 190, 950, 200),
    N("a1", "2. Пишет и объясняет\nформулы", 0, 260, "pu", 260, 100),
    N("a2", "Чистит данные,\nстроит модель", 320, 260, "pu", 260, 100),
    N("a3", "3. Ищет ошибки,\nпомечает спорное", 640, 260, "pu", 260, 100),
], edges=[E("h1", "a1"), E("a1", "a2"), E("a2", "a3"), E("a3", "h3"), E("h3", "h4"), E("h4", "dec")])

# own: verification order before a number leaves the workbook
D["ch12-verification"] = dict(items=[
    N("s1", "1. Порядок величины:\nчисло в разумном\nдиапазоне?", 0, 0, "y", 250, 120),
    N("s2", "2. Проследить\nформулы\nнескольких ячеек", 310, 0, "p", 250, 120),
    N("s3", "3. Изменить вход:\nитог сдвинулся\nкак ожидали?", 620, 0, "p", 250, 120),
    N("s4", "4. Сверить с числом,\nкоторому доверяете", 930, 0, "p", 250, 120),
    N("ok", "Цифра покидает\nкнигу Excel", 1240, 0, "g", 250, 120),
    N("bad", "Выручка ~200 тыс. в месяц,\nа модель даёт 4 млн:\nошибка, как бы ни выглядела формула", 0, 200, "r", 560, 110),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "ok"), E("s1", "bad", dashed=True)])

# own: Excel as one link in a larger flow
D["ch12-workflow-chain"] = dict(items=[
    N("src", "Источник данных:\nCRM, продажи", 0, 0, "db", 240, 100),
    N("con", "Коннектор\n(connector)", 300, 0, "n", 240, 100),
    N("xl", "Excel + Claude:\nочистка, модель", 600, 0, "pu", 240, 100),
    N("cw", "Cowork: задача\nпо расписанию", 900, 0, "q", 240, 100),
    N("out", "Сводка\nво входящих", 1200, 0, "g", 240, 100),
    T("Данные приходят сами", 300, 130),
    T("Результат уходит сам", 900, 130),
], edges=[E("src", "con"), E("con", "xl"), E("xl", "cw"), E("cw", "out")])

if __name__ == "__main__":
    run_all(D)
