#!/usr/bin/env python3
"""Chapter 7 (stories, part 2) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

CW, GAP = 270, 40  # column width and gap
X = [i * (CW + GAP) for i in range(5)]

# own: map of the five stories (main diagram of the chapter)
D["ch07-five-stories"] = dict(items=[
    N("root", "Пять историй:\nкакой бывает работа Staff+", 470, 0, "n", 410, 100),
    N("rv", "Риту Винсент\nDropbox\nStaff-инженер", X[0], 260, "p", CW, 110),
    N("rb", "Рик Бун\nUber\nStrategic Advisor VP", X[1], 260, "pu", CW, 110),
    N("ne", "Нельсон Элхейдж\nStripe\nStaff-инженер", X[2], 260, "y", CW, 110),
    N("dp", "Диана Пожар\nSlack\nStaff Data Engineer", X[3], 260, "db", CW, 110),
    N("dn", "Дэн На\nSquarespace\nStaff-инженер, тимлид", X[4], 260, "p", CW, 110),
    N("rv2", "Техлид,\nпотом инкубатор", X[0], 450, "n", CW, 90),
    N("rb2", "Right Hand", X[1], 450, "n", CW, 90),
    N("ne2", "Solver (Sorbet),\nпотом Architect", X[2], 450, "n", CW, 90),
    N("dp2", "Техлид Data Platform,\nширокий профиль", X[3], 450, "n", CW, 90),
    N("dn2", "Техлид команды\n+ культура", X[4], 450, "n", CW, 90),
    N("rv3", "Просите трудные\nпроекты.\nЧестно говорите\nс менеджером", X[0], 620, "g", CW, 150),
    N("rb3", "Идите за своими\nинтересами и ищите,\nгде они нужны\nкомпании", X[1], 620, "g", CW, 150),
    N("ne3", "Берите 1-2 проблемы\nв год. Стройте\nотношения\nс руководством", X[2], 620, "g", CW, 150),
    N("dp3", "Поверьте, что\nсможете. Работа\nStaff больше,\nчем код", X[3], 620, "g", CW, 150),
    N("dn3", "Каждая ступень\nдобавляет слой\nзабот. Вы лидер,\nхотите или нет", X[4], 620, "g", CW, 150),
    T("архетип\n(наша оценка)", X[0] - 170, 465, 16),
    T("главный\nсовет", X[0] - 170, 670, 16),
], edges=[E("root", p) for p in ("rv", "rb", "ne", "dp", "dn")]
  + [E(p, p + "2") for p in ("rv", "rb", "ne", "dp", "dn")]
  + [E(p + "2", p + "3") for p in ("rv", "rb", "ne", "dp", "dn")])

# own: Dan Na's ladder of care
D["ch07-ladder-of-care"] = dict(items=[
    Z("Лестница забот", -30, -60, 420, 760),
    N("dir", "Директор:\nпродукты своей\nорганизации", 0, 0, "pu", 360, 120),
    N("lead", "Тимлид или менеджер:\nнабор функций продукта", 0, 190, "p", 360, 110),
    N("eng", "Инженер команды:\nвесь жизненный цикл\nфункции", 0, 370, "p", 360, 120),
    N("intern", "Стажёр:\nкусочек функции\nна три месяца", 0, 560, "n", 360, 110),
    N("staff", "Staff-инженер", 620, 120, "y", 400, 100),
    N("own", "Своя техническая\nобласть, как раньше", 520, 380, "g", 280, 120),
    N("gap", "Проблемы между\nкомандами: онбординг,\nпроцессы, культура", 840, 380, "r", 280, 120),
    T("Нижние заботы не уходят:\nк ним добавляется новый слой", 560, 580, 18, "#495057"),
], edges=[E("intern", "eng"), E("eng", "lead"), E("lead", "dir"),
          E("staff", "own"), E("staff", "gap"),
          E("lead", "staff", "тот же принцип", dashed=True)])

if __name__ == "__main__":
    run_all(D)
