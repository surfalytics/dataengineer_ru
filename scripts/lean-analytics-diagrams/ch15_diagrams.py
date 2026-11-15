#!/usr/bin/env python3
"""Chapter 15 (Empathy stage) diagrams. Usage: ch15_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: the whole Empathy stage, from idea to MVP (main diagram)
D["ch15-empathy-flow"] = dict(items=[
    Z("Проблема: стоит ли её решать?", -25, -70, 1440, 210),
    N("idea", "Идея:\nжалобы людей,\nсвой опыт", 0, 0, "n", 230, 110),
    N("sniff", "«Тест на запах»:\nспросить друзей\nи советников", 290, 0, "p", 230, 110),
    N("pi", "Проблемные\nинтервью:\n15+ человек", 580, 0, "p", 230, 110),
    N("score", "Оценка\nинтервью:\n31+ из 43", 870, 0, "y", 230, 110),
    N("scale", "Ответы\nв масштабе:\nопросы, реклама", 1160, 0, "q", 230, 110),
    Z("Решение: построй, прежде чем строить", -25, 200, 1440, 210),
    N("si", "Интервью\nо решении:\nмакеты, прототипы", 1160, 270, "p", 230, 110),
    N("proxy", "Проверка\nчерез чужую\nсистему (proxy)", 870, 270, "p", 230, 110),
    N("early", "Ранние\nпользователи:\nбета, соцсети", 580, 270, "q", 230, 110),
    N("mvp", "MVP:\nодин OMTM,\nитерации", 290, 270, "y", 230, 110),
    N("next", "Этап\nStickiness", 0, 270, "g", 230, 110),
], edges=[E("idea", "sniff"), E("sniff", "pi"), E("pi", "score"), E("score", "scale"), E("scale", "si"),
          E("si", "proxy"), E("proxy", "early"), E("early", "mvp"), E("mvp", "next")])

# own: problem interview script (after Ash Maurya, Running Lean)
D["ch15-problem-interview"] = dict(items=[
    Z("По сценарию", -25, -70, 920, 210),
    N("s1", "1. Вступление:\nкак пройдёт\nразговор и зачем", 0, 0, "p", 250, 110),
    N("s2", "2. Демография:\nкто человек,\nкакой сегмент", 320, 0, "p", 250, 110),
    N("s3", "3. История:\nкак мы нашли\nпроблемы", 640, 0, "p", 250, 110),
    Z("Свободный разговор и финал", -25, 200, 920, 210),
    N("s4", "4. Ранжирование:\nкакая проблема\nважнее", 640, 270, "p", 250, 110),
    N("s5", "5. Как решает\nсейчас: человек\nговорит, мы слушаем", 320, 270, "y", 250, 110),
    N("s6", "6. Просьба:\nвторая встреча\nи контакты", 0, 270, "g", 250, 110),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "s5"), E("s5", "s6")])

# own: mental model, behaviors above, products below (idea of Fig 15-2)
cols = [("b1", "Выключить\nбудильник", "p1", "Приложение-\nбудильник"),
        ("b2", "Выпить\nкофе", "p2", "Кофемашина"),
        ("b3", "Принять\nдуш", "p3", "Гель\nдля душа"),
        ("b4", "Выбрать\nодежду", "p4", "Прогноз\nпогоды"),
        ("b5", "Позавтракать", "p5", "Доставка\nпродуктов"),
        ("b6", "Проверить\nпробки", "p6", "Навигатор")]
items = [Z("Проснуться", -15, -60, 445, 180), Z("Одеться", 445, -60, 445, 180),
         Z("Поесть", 905, -60, 215, 180), Z("Доехать", 1135, -60, 230, 180),
         T("Что делает человек", -250, 30, 20, "#495057"), T("Что ему помогает", -250, 270, 20, "#495057")]
edges = []
for i, (b, bt, p, pt) in enumerate(cols):
    items += [N(b, bt, i * 230, 0, "q", 200, 90), N(p, pt, i * 230, 240, "g", 200, 90)]
    edges.append(E(b, p, dashed=True))
D["ch15-mental-model"] = dict(items=items, edges=edges)

# Fig 15-9: Static Pixels checkout with and without InstaOrder
left = ["Нажать\n«Оформить»", "Войти в PayPal", "Страница\nподтверждения", "Подтвердить\nзаказ",
        "Снова в PayPal", "Разрешить\nавтоплатежи", "Готово"]
right = ["Нажать\n«Оформить»", "Войти в PayPal", "Страница\nподтверждения", "Подтвердить\nзаказ", "Готово"]
items = [Z("С InstaOrder: 7 шагов", -30, -70, 340, 860), Z("Без InstaOrder: 5 шагов", 420, -70, 340, 860)]
edges = []
for col, steps, x in (("l", left, 0), ("r", right, 450)):
    for i, t in enumerate(steps):
        k = "r" if col == "l" and i in (4, 5) else ("g" if t == "Готово" else "p")
        items.append(N(f"{col}{i}", t, x, i * 110, k, 280, 70))
        if i: edges.append(E(f"{col}{i-1}", f"{col}{i}"))
D["ch15-static-pixels"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
