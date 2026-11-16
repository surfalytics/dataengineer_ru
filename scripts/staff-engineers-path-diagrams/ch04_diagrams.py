#!/usr/bin/env python3
"""Chapter 4 (Finite Time) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 4-6 redrawn + own: main diagram, a new project changes time and five resources
BW, BG = 240, 30
RES = [
    ("time", "Время\n168 часов\nв неделю,\nне больше", "n"),
    ("en", "Энергия\n+ работа, которая\nзаряжает\n− встречи, стресс,\nзаботы дома", "p"),
    ("ql", "Качество жизни\n+ любимая работа,\nхорошие люди\n− скука, грубость,\nчуждые цели", "p"),
    ("cr", "Доверие к вам\n+ трудные задачи,\nясность, спокойствие\n− отрыв от кода,\nабсолютизм", "p"),
    ("sc", "Социальный\nкапитал\n+ помощь, успехи\n− отказы,\nброшенные проекты", "p"),
    ("sk", "Навыки\n+ учёба, сильные\nколлеги, практика\n− сами понемногу\nустаревают", "p"),
]
D["ch04-needs-dashboard"] = dict(items=[
    N("proj", "Новый проект или задача: что он даст и что заберёт?", 0, 0, "y", 6 * (BW + BG) - BG, 90),
    *[N(i, t, k * (BW + BG), 230, c, BW, 200) for k, (i, t, c) in enumerate(RES)],
    *[N("p" + i, "", k * (BW + BG) + BW / 2 - 15, 86, "y", 30, 8) for k, (i, t, c) in enumerate(RES)],
    T("Серый блок — время: его нельзя добавить. Синие — пять ресурсов вашей «панели потребностей».\n«+» — что их пополняет, «−» — что тратит.", 0, 470, 18, "#495057"),
], edges=[E("p" + i, i) for i, _, _ in RES])

# Fig 4-3 redrawn (our heights): how full is the schedule, room for a spike
COL = 240
def person(k, name, load, note):
    x = k * (COL + 120)
    top = 60
    buf = 400 - load
    items = [N(f"l{k}", "обычная\nнагрузка", x, top + buf, "p", COL, load)]
    if buf >= 60:
        items.append(N(f"b{k}", "запас\nна всплеск", x, top, "g", COL, buf))
    else:
        items.append(N(f"s{k}", "всплеск\nне влезает", x, top - 110, "r", COL, 90))
    items.append(T(name, x + 100, top + 415, 22, "#1971c2"))
    items.append(T(note, x, top + 455, 18, "#495057"))
    return items
D["ch04-load-buffer"] = dict(items=[
    N("lim", "", -20, 56, "r", 3 * COL + 280, 4),
    T("предел сил", 3 * COL + 270, 40, 18, "#e03131"),
    *person(0, "A", 160, "Спокойно берёт\nлишние часы\nв кризис"),
    *person(1, "B", 300, "Справится\nс небольшим\nвсплеском"),
    *person(2, "C", 380, "Всегда на пределе:\nлюбой всплеск —\nстресс и срыв"),
], edges=[])

# Fig 4-13 redrawn: impact vs effort, the snacking quadrant
QW, QH = 330, 170
D["ch04-snacking"] = dict(items=[
    N("q1", "Мало усилий,\nбольшая польза:\nделать в первую очередь", 120, 0, "g", QW, QH),
    N("q2", "Много усилий,\nбольшая польза:\nглавная работа,\nпланировать", 120 + QW + 20, 0, "p", QW, QH),
    N("q3", "Мало усилий,\nмалая польза:\nsnacking — «перекусы»,\nне увлекаться", 120, QH + 20, "y", QW, QH),
    N("q4", "Много усилий,\nмалая польза:\nне делать", 120 + QW + 20, QH + 20, "r", QW, QH),
    T("польза\n↑", 20, 40, 20, "#495057"),
    T("усилия →", 120 + QW + 20 + QW - 110, 2 * QH + 40, 20, "#495057"),
    T("«Перекусы» быстры и приятны, поэтому их легко оправдать.\nНо если есть только их, на главную работу сил не останется.", 0, 2 * QH + 90, 18, "#495057"),
], edges=[])

# own: what to do when an important project does not fit you
OW = 250
OPTS = [
    ("o1", "Сделать\nвсё равно:\nтолько на время,\nс критериями выхода", "r"),
    ("o2", "Компенсировать:\nосвободить место\nили добрать\nресурс в другом", "p"),
    ("o3", "Отдать другому:\nпусть растёт\nколлега", "g"),
    ("o4", "Изменить форму:\nмесяц, роль\nконсультанта,\nодна встреча", "p"),
    ("o5", "Отказаться:\nваше «нет» —\nподарок себе\nв будущем", "y"),
]
D["ch04-wrong-project"] = dict(items=[
    N("src", "Проект важен для компании, но не подходит вам сейчас", 0, 0, "q", 5 * (OW + 30) - 30, 90),
    *[N(i, t, k * (OW + 30), 230, c, OW, 150) for k, (i, t, c) in enumerate(OPTS)],
    *[N("p" + i, "", k * (OW + 30) + OW / 2 - 15, 86, "q", 30, 8) for k, (i, t, c) in enumerate(OPTS)],
], edges=[E("p" + i, i) for i, _, _ in OPTS])

if __name__ == "__main__":
    run_all(D)
