#!/usr/bin/env python3
"""Chapter 2 (Opus, Sonnet, Haiku) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)
The book has no figures in this chapter. All three diagrams are our own."""
from excb import N, E, Z, T, run_all

D = {}

# own: the three tiers, from cheap and fast to strong and slow (main diagram)
D["ch02-model-family"] = dict(items=[
    N("h", "Haiku 4.5\nбыстрый и дешёвый", 0, 0, "g", 280, 110),
    N("s", "Sonnet 4.6\nмодель по умолчанию", 460, 0, "p", 280, 110),
    N("o", "Opus 4.8\nфлагман", 920, 0, "pu", 280, 110),
    N("ht", "Младший сотрудник:\nклассификация, извлечение,\nмаршрутизация потока", 0, 190, "n", 280, 150),
    N("st", "Опытный специалист:\nтексты, ответы, код,\nобычная автоматизация", 460, 190, "n", 280, 150),
    N("ot", "Старший партнёр:\nархитектура,\nтрудная отладка,\nдолгие задачи агента", 920, 190, "n", 280, 150),
    T("Цена за токен и время ответа растут слева направо →", 230, 380, 20, "#495057"),
], edges=[E("h", "s", "сложнее"), E("s", "o", "сложнее"),
          E("h", "ht", dashed=True), E("s", "st", dashed=True), E("o", "ot", dashed=True)])

# own: tiered routing, Haiku -> Sonnet -> Opus
D["ch02-tiered-routing"] = dict(items=[
    N("in", "Поток\nзапросов", 0, 0, "n", 220, 110),
    N("h", "Haiku\nразбирает всё", 420, 0, "g", 250, 110),
    N("s", "Sonnet\nсложные случаи", 870, 0, "p", 250, 110),
    N("o", "Opus\nсамые трудные", 1320, 0, "pu", 250, 110),
    N("out", "Готовый ответ", 420, 260, "y", 1150, 90),
], edges=[E("in", "h"), E("h", "s", "сложно\nили неясно"), E("s", "o", "Sonnet\nне уверен"),
          E("h", "out", "~80%"), E("s", "out"), E("o", "out", "редко")])

# own: decision framework
D["ch02-decision"] = dict(items=[
    N("q", "Насколько трудно\nрассуждение?", 450, 0, "y", 380, 100),
    N("c1", "Трудная, многошаговая,\nошибка дорого стоит", 0, 200, "n", 380, 100),
    N("c2", "Обычная работа:\nтексты, код, вопросы", 450, 200, "n", 380, 100),
    N("c3", "Простая и массовая:\nсотни и тысячи вызовов", 900, 200, "n", 380, 100),
    N("o", "Opus\n+ extended thinking", 60, 400, "pu", 260, 100),
    N("s", "Sonnet\n(по умолчанию)", 510, 400, "p", 260, 100),
    N("h", "Haiku", 960, 400, "g", 260, 100),
], edges=[E("q", "c1"), E("q", "c2"), E("q", "c3"), E("c1", "o"), E("c2", "s"), E("c3", "h"),
          E("s", "o", "не\nсправляется", dashed=True), E("s", "h", "избыточен", dashed=True)])

if __name__ == "__main__":
    run_all(D)
