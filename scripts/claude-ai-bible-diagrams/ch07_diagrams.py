#!/usr/bin/env python3
"""Chapter 7 (Projects, memory, knowledge base) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)
The book chapter has no figures. All three diagrams are our own."""
from excb import N, E, Z, T, run_all

D = {}

# main: a Project is a container; every new conversation inherits instructions and knowledge
D["ch07-project-container"] = dict(items=[
    N("rq", "Ваш запрос: короткий,\nбез повторных объяснений", 440, -250, "n", 320, 100),
    Z("Проект", -30, -80, 820, 430),
    N("ins", "Инструкции проекта\n(system prompt):\nголос, правила, запреты", 0, -20, "p", 300, 120),
    N("kb", "База знаний проекта:\nгайды, шаблоны,\nэталоны работ", 0, 190, "db", 300, 120),
    N("cv", "Новый разговор\nв проекте: уже знает\nинструкции и файлы", 440, 80, "g", 320, 120),
    N("ans", "Ответ в нужном\nголосе и по\nвашим правилам", 950, 80, "g", 260, 120),
    N("bad", "Без проекта каждый разговор начинается с нуля:\nснова голос бренда, адреса, правила. Это «налог на повторный брифинг»", -30, 420, "r", 820, 100),
], edges=[E("rq", "cv"), E("ins", "cv"), E("kb", "cv"), E("cv", "ans")])

# custom instructions, memory and Project: three layers that stack
D["ch07-three-layers"] = dict(items=[
    T("Шире", -110, 40, 22, "#1971c2"), T("Уже", -100, 400, 22, "#1971c2"),
    N("ci", "Custom instructions:\nкак Claude общается с вами везде.\nЗадаёте один раз", 0, 0, "n", 420, 120),
    N("mem", "Память (memory):\nфакты о вас, которые Claude\nнакопил за разные разговоры", 0, 180, "y", 420, 120),
    N("prj", "Проект:\nсвои инструкции и база знаний.\nРаботают только внутри него", 0, 360, "p", 420, 120),
    N("cv", "Разговор в проекте:\nвсе три слоя\nработают вместе", 640, 180, "g", 300, 120),
], edges=[E("ci", "cv"), E("mem", "cv"), E("prj", "cv")])

# what goes into the knowledge base and what stays out
D["ch07-kb-filter"] = dict(items=[
    N("doc", "Новый документ", 0, 130, "n", 220, 90),
    N("q", "Будет ли он полезен\nновому сотруднику\nвесь год?", 340, 105, "y", 300, 140),
    N("kb", "В базу знаний проекта:\nгайды стиля, справочники,\nшаблоны, 2-3 эталона работ", 800, -40, "g", 380, 120),
    N("chat", "Вставить в один\nразговор и забыть", 800, 270, "p", 380, 100),
    N("upd", "Документ изменился: удалите\nстарую версию, не только\nдобавьте новую", 1300, -40, "y", 340, 120),
    N("out", "Не класть: то, что часто меняется, разовые заметки,\nархивы с шумом, лишние чувствительные данные", 0, 430, "r", 760, 100),
], edges=[E("doc", "q"), E("q", "kb", "да"), E("q", "chat", "нет"), E("kb", "upd", dashed=True)])

if __name__ == "__main__":
    run_all(D)
