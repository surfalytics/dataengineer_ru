#!/usr/bin/env python3
"""Chapter 1 (what is a Staff engineer) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Figure "Typical dual-track engineering career ladder"
D["ch01-dual-track-ladder"] = dict(items=[
    N("jr", "Junior-инженер", 415, 0, "n", 270, 90),
    N("sr", "Senior-инженер\n(career level:\nдальше расти не обязательно)", 385, 170, "y", 330, 120),
    N("em", "Engineering manager", 0, 420, "pu", 280, 90),
    N("dir", "Director", 0, 570, "pu", 280, 90),
    N("vp", "VP Engineering", 0, 720, "pu", 280, 90),
    N("st", "Staff-инженер", 820, 420, "p", 280, 90),
    N("pr", "Principal-инженер", 820, 570, "p", 280, 90),
    N("di", "Distinguished engineer", 820, 720, "p", 280, 90),
    T("Путь менеджера\n(management track)", 0, 830, 20, "#9c36b5"),
    T("Путь IC: техническое лидерство.\nStaff+ = Staff, Principal и Distinguished", 820, 830, 20, "#1971c2"),
], edges=[E("jr", "sr"), E("sr", "em"), E("sr", "st"),
          E("em", "dir"), E("dir", "vp"), E("st", "pr"), E("pr", "di")])

# own: four archetypes and how their work feels (main diagram of the chapter)
D["ch01-four-archetypes"] = dict(items=[
    N("root", "Staff-инженер:\nчетыре архетипа", 495, 0, "n", 300, 90),
    N("tl", "Техлид (Tech Lead)\nведёт подход и работу\nодной или нескольких\nкоманд\n\nесть почти везде,\n~1 на 8 инженеров", 0, 320, "p", 300, 230),
    N("ar", "Architect\nотвечает за важную\nобласть: API, frontend,\nхранение, облако\n\nчасто появляется\nс ~100 инженеров", 330, 320, "p", 300, 230),
    N("so", "Solver\nуходит в трудную\nпроблему, решает её\nи идёт к следующей\n\nтам, где задачу\nдают человеку", 660, 320, "pu", 300, 230),
    N("rh", "Right Hand\nрасширяет внимание\nруководителя,\nберёт его полномочия\n\nобычно появляется\nс ~1000 инженеров", 990, 320, "pu", 300, 230),
    N("same", "Те же люди и задачи годами:\nсильное чувство команды", 0, 660, "g", 630, 100),
    N("fire", "От пожара к пожару: ближе к целям\nруководства, но мало чувства общности", 660, 660, "y", 630, 100),
], edges=[E("root", "tl"), E("root", "ar"), E("root", "so"), E("root", "rh"),
          E("tl", "same"), E("ar", "same"), E("so", "fire"), E("rh", "fire")])

# own: shared foundation of Staff work
D["ch01-staff-work"] = dict(items=[
    N("root", "Общая основа работы\nStaff-инженера", 500, 0, "n", 300, 100),
    N("dir", "Технические\nрешения и курс", 0, 200, "p", 220, 110),
    N("men", "Менторство\nи спонсорство", 270, 200, "g", 220, 110),
    N("view", "Инженерный взгляд\nв важных\nрешениях", 540, 200, "y", 220, 110),
    N("exp", "Исследование\n(exploration)", 810, 200, "pu", 220, 110),
    N("glue", "Glue work:\nнужная, но\nневидимая работа", 1080, 200, "db", 220, 110),
    T("Код, проекты и связи остаются, но становятся вспомогательной работой.\nОбратная связь приходит через недели, месяцы и годы.", 0, 350, 20, "#495057"),
], edges=[E("root", "dir"), E("root", "men"), E("root", "view"), E("root", "exp"), E("root", "glue")])

# own: hill-climbing vs exploration
D["ch01-hill-climbing"] = dict(items=[
    T("Hill-climbing: шаг за шагом к ближайшей вершине", 0, -50, 22, "#1971c2"),
    N("look", "Осмотреться\nвокруг", 0, 0, "p", 230, 110),
    N("step", "Шагнуть к самой\nвысокой точке рядом", 330, 0, "p", 250, 110),
    N("peak", "Вершина своей\nгоры", 680, 0, "g", 230, 110),
    N("fog", "Туман: выше есть\nдругая гора,\nно её не видно", 1010, 0, "r", 250, 110),
    T("повторять, пока есть куда подняться", 0, 125, 18),
    N("explore", "Exploration: двое-трое доверенных людей\nс широкими навыками, ресурсы\nи проверка через несколько месяцев", 680, 280, "pu", 580, 120),
], edges=[E("look", "step"), E("step", "peak"), E("peak", "fog"), E("fog", "explore", "выход")])

if __name__ == "__main__":
    run_all(D)
