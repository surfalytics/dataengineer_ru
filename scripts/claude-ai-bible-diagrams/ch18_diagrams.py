#!/usr/bin/env python3
"""Chapter 18 (Claude Agent SDK) diagrams. Usage: ch18_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# redraw of the book's text sketch "the loop the SDK runs for you" (main diagram)
D["ch18-agent-loop"] = dict(items=[
    N("goal", "Вы задаёте:\nцель + инструменты\n+ лимиты", -40, 0, "y"),
    N("dec", "1. Модель решает:\nчто делать дальше", 330, 0, "p"),
    N("want", "Нужен\nинструмент?", 700, -20, "q", 240, 140, "diamond"),
    N("fin", "Финальный ответ,\nцикл закончен", 1080, 0, "g"),
    N("run", "2. SDK запускает\nинструмент:\nфайл, команда, база", 700, 300, "db"),
    N("obs", "3. Модель видит\nрезультат:\nданные или ошибку", 330, 300, "pu"),
    N("cap", "Лимит шагов\nили бюджета:\nстоп", 1080, 300, "r"),
    T("4. Повтор, пока модель не закончит\nили не сработает лимит", 230, 470, 18),
], edges=[E("goal", "dec"), E("dec", "want"), E("want", "fin", "нет"),
          E("want", "run", "да"), E("run", "obs"), E("obs", "dec", "повтор"),
          E("run", "cap", "лимит", dashed=True)])

# own: the four guardrail layers on the way from intent to action
D["ch18-guardrails"] = dict(items=[
    N("want", "Агент хочет\nсделать действие", -40, 0, "p"),
    N("has", "Есть такой\nинструмент?", 330, -20, "q", 240, 140, "diamond"),
    N("no", "Действие\nневозможно", 330, -300, "n"),
    N("risk", "Нужно\nодобрение?", 700, -20, "q", 240, 140, "diamond"),
    N("human", "Человек или код\nпроверяет:\nда / нет", 700, -300, "y"),
    N("box", "Инструмент работает\nв песочнице:\nсвоя папка, без сети", 1080, 0, "db", 270, 100),
    N("lim", "Лимиты шагов\nи бюджета\nостановят цикл", 1080, 300, "r"),
    T("1. Набор инструментов   2. Одобрение\n3. Песочница   4. Жёсткие лимиты", 230, 300, 18),
], edges=[E("want", "has"), E("has", "no", "нет"), E("has", "risk", "да"),
          E("risk", "human", "да"), E("risk", "box", "нет"), E("human", "box", "да"), E("human", "no", "нет"),
          E("box", "lim")])

# "orchestration" is not drawn: the same idea is ch13-subagents.png (see figures.md)

if __name__ == "__main__":
    run_all(D)
