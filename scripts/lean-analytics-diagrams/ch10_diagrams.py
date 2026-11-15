#!/usr/bin/env python3
"""Chapter 10 (Model Three: Free Mobile App) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 10-1: unit economics of a free mobile game (our layout, same numbers as the book example)
D["ch10-unit-economics"] = dict(items=[
    N("d", "12 304 загрузки\nза месяц", 420, 0, "p", 340, 90),
    N("l", "11 812 запусков", 420, 200, "p", 340, 90),
    N("e", "3 544 вовлечённых\nигрока", 420, 400, "p", 340, 90),
    N("arpu", "ARPU:\n$3,20 в месяц", 0, 600, "y", 340, 90),
    N("rev", "3 544 × $3,20 = $11 339\nдоход за месяц", 420, 600, "y", 340, 90),
    N("churn", "Churn:\n15% в месяц", 840, 600, "r", 340, 90),
    N("life", "1 / 0,15 = 6,67 месяца — средний срок жизни игрока", 0, 790, "r", 1180, 80),
    N("ltv", "LTV = $3,20 × 6,67\n= $21,33", 0, 970, "y", 340, 90),
    N("coh", "$11 339 × 6,67 = $75 596\nдоход когорты за всё время", 420, 970, "y", 340, 90),
    N("cac", "CAC = $11,21\nна вовлечённого игрока", 420, 1160, "q", 340, 90),
    N("c1", "Вклад игрока:\n$21,33 − $11,21 = $10,12", 0, 1350, "g", 340, 90),
    N("c2", "ROI привлечения:\n$21,33 / $11,21 = 1,9×", 420, 1350, "g", 340, 90),
    N("c3", "Окупаемость CAC:\n$11,21 / $3,20 = 3,5 месяца", 840, 1350, "g", 340, 90),
], edges=[E("d", "l", "96% запускают"), E("l", "e", "30% вовлекаются"), E("e", "rev"),
          E("arpu", "rev"), E("arpu", "life"), E("rev", "life"), E("churn", "life"),
          E("life", "ltv"), E("life", "coh"), E("ltv", "cac"),
          E("cac", "c1"), E("cac", "c2"), E("cac", "c3")])

# Fig 10-2: lifecycle of a mobile app user, everything feeds back to the app store
D["ch10-lifecycle"] = dict(items=[
    N("store", "App store:\nрейтинги, поиск,\nтоп-листы", 500, 0, "q", 300, 120),
    N("down", "Покупка\nи загрузка", 500, 220, "p", 300, 100),
    N("inst", "Установка", 500, 420, "p", 300, 100),
    N("acct", "Создание аккаунта", 500, 620, "p", 300, 100),
    N("play", "Игра: ARPU,\nпокупки в приложении", 500, 820, "g", 300, 100),
    N("dis", "Потеря интереса", 500, 1020, "y", 300, 100),
    N("un", "Удаление:\nchurn, итог LTV", 500, 1220, "r", 300, 100),
    N("rate", "Оценки и отзывы:\nчестные, накрученные,\nза награду", 0, 420, "q", 300, 120),
    N("inv", "Приглашения\nдрузей (virality)", 1000, 420, "pu", 300, 100),
    N("re", "Возвращение\n(reactivation)", 1000, 1020, "p", 300, 100),
], edges=[E("store", "down", "загрузки, выручка"), E("down", "inst"), E("inst", "acct"),
          E("acct", "play", "активация"), E("play", "dis"), E("dis", "un", "churn"),
          E("dis", "re"), E("re", "play", dashed=True),
          E("play", "rate"), E("rate", "store", "отзывы"),
          E("play", "inv"), E("inv", "store", "virality")])

# own: when users leave tells why (Keith Katz)
D["ch10-churn-periods"] = dict(items=[
    N("i", "Установка", 0, 0, "n", 220, 90),
    N("d1", "Churn\nчерез 1 день", 320, 0, "y", 260, 90),
    N("w1", "Churn\nчерез 1 неделю", 680, 0, "y", 260, 90),
    N("m1", "Churn\nчерез 1 месяц", 1040, 0, "y", 260, 90),
    N("r1", "Плохое обучение,\nигра не цепляет", 320, 200, "r", 260, 100),
    N("r2", "Игре не хватает\nглубины", 680, 200, "r", 260, 100),
    N("r3", "Плохо спланированы\nобновления", 1040, 200, "r", 260, 100),
], edges=[E("i", "d1"), E("d1", "w1"), E("w1", "m1"),
          E("d1", "r1", dashed=True), E("w1", "r2", dashed=True), E("m1", "r3", dashed=True)])

if __name__ == "__main__":
    run_all(D)
