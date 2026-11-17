#!/usr/bin/env python3
"""Chapter 8 (stories, part 3) diagrams. Usage: ch08_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

CW, GAP = 290, 40  # column width and gap
X = [i * (CW + GAP) for i in range(4)]
P = ("jo", "da", "dm", "st")

# own: map of the four stories (main diagram of the chapter)
D["ch08-four-stories"] = dict(items=[
    N("root", "Четыре истории: пути разные,\nработа Staff+ похожая", 340, 0, "n", 440, 100),
    N("jo", "Джой Эберц\nSplit\nSenior Staff-инженер", X[0], 240, "p", CW, 110),
    N("da", "Дамиан Шенкельман\nAuth0\nPrincipal-инженер", X[1], 240, "pu", CW, 110),
    N("dm", "Дмитрий Петрашко\nStripe\nStaff-инженер, TA", X[2], 240, "y", CW, 110),
    N("st", "Стивен Ван\nSamsara\nStaff-инженер", X[3], 240, "db", CW, 110),
    N("jo2", "Box 8 лет, 1,5 года\nменеджмента,\nпотом Staff", X[0], 430, "n", CW, 110),
    N("da2", "Пятый инженер,\nдиректор по инженерии,\nпотом Principal", X[1], 430, "n", CW, 110),
    N("dm2", "PhD, проект Sorbet,\nдва повышения\nв Stripe", X[2], 430, "n", CW, 110),
    N("st2", "Ранний вход,\nуровень при вводе\nлестницы", X[3], 430, "n", CW, 110),
    N("jo3", "Architect:\nвидение для backend,\nbackend chapter", X[0], 620, "n", CW, 110),
    N("da3", "Architect:\nстратегия и\nгруппа DNA", X[1], 620, "n", CW, 110),
    N("dm3", "Right Hand (TA),\nраньше Solver\n(Sorbet)", X[2], 620, "n", CW, 110),
    N("st3", "Между Solver\nи техлидом\n(его слова)", X[3], 620, "n", CW, 110),
    N("jo4", "Усиливайте сильные\nстороны. Пишите\npromotion packet заранее", X[0], 810, "g", CW, 130),
    N("da4", "Записывайте\nи повторяйте.\nБудьте терпеливы", X[1], 810, "g", CW, 130),
    N("dm4", "Договоритесь о целевом\nэффекте и допустимых\nкомпромиссах", X[2], 810, "g", CW, 130),
    N("st4", "Много говорите.\nНе выгорайте:\nменяйте через других", X[3], 810, "g", CW, 130),
    T("путь\nк уровню", X[0] - 190, 460, 16),
    T("архетип\n(наша оценка)", X[0] - 190, 650, 16),
    T("главный\nсовет", X[0] - 190, 850, 16),
    T("Заранее заданного Staff project не было ни у кого", 300, 990, 20, "#495057"),
], edges=[E("root", p) for p in P]
  + [E(p, p + "2") for p in P]
  + [E(p + "2", p + "3") for p in P]
  + [E(p + "3", p + "4") for p in P])

# own: how Damian replaced rumors with a strategy (nemawashi)
D["ch08-nemawashi"] = dict(items=[
    N("rumor", "Слухи и неясность:\nкоманды боятся решать", 190, 0, "r", 400, 100),
    N("talk", "Дамиан говорит с людьми,\nзаписывает проблемы\nи связывает их", 190, 180, "n", 400, 110),
    Z("Сейчас", -30, 370, 400, 520),
    N("dna", "Группа DNA:\n3 Principal и 3 ротируемых\nStaff или Senior", 0, 430, "p", 340, 120),
    N("guide", "Guidelines и список\n«одобренных» технологий:\nкоманды решают сами", 0, 620, "g", 340, 120),
    N("rfc", "Исключения: ревью\nчерез RFC", 0, 810, "g", 340, 80),
    Z("Надолго", 410, 370, 440, 960),
    N("topics", "Список тем, по которым\nкомпании нужны решения", 440, 430, "p", 380, 100),
    N("slides", "Две презентации:\nкороткая для руководства,\nподробная для инженеров", 440, 610, "p", 380, 120),
    N("nema", "Nemawashi: тихие разговоры\nс VP, руководителями,\nколлегами до встречи", 440, 810, "y", 380, 120),
    N("meet", "Общая встреча:\nобсуждают компромиссы\nи принимают решения", 440, 1010, "p", 380, 120),
    N("log", "Decision log:\nрешения и письменно\nназначенные владельцы", 440, 1210, "g", 380, 110),
], edges=[E("rumor", "talk"), E("talk", "dna"), E("talk", "topics"),
          E("dna", "guide"), E("guide", "rfc"),
          E("topics", "slides"), E("slides", "nema"), E("nema", "meet"), E("meet", "log")])

if __name__ == "__main__":
    run_all(D)
