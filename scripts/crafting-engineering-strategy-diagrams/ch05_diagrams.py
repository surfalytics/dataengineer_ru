#!/usr/bin/env python3
"""Chapter 5 (steps to build an engineering strategy) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: main map - five steps, each feeds the next, and the question each step answers
D["ch05-five-steps"] = dict(items=[
    T("Пять шагов: каждый даёт вход следующему", 0, -50, 22, "#1971c2"),
    N("s1", "1. Исследование\n(exploration)", 0, 0, "p", 260, 90),
    N("s2", "2. Диагноз\n(diagnosis)", 340, 0, "p", 260, 90),
    N("s3", "3. Уточнение\n(refinement)", 680, 0, "y", 260, 90),
    N("s4", "4. Политика\n(policy)", 1020, 0, "g", 260, 90),
    N("s5", "5. Operations", 1360, 0, "q", 260, 90),
    N("q1", "Что уже знает отрасль?\nЧужие подходы\nи свежие работы", 0, 190, "n", 260, 110),
    N("q2", "В чём наша проблема?\nКонтекст и причины,\nещё без решений", 340, 190, "n", 260, 110),
    N("q3", "Работает ли идея?\nstrategy testing,\nsystems modeling,\nWardley mapping", 680, 190, "n", 260, 130),
    N("q4", "Какие решения\nи компромиссы мы\nвыбираем?", 1020, 190, "n", 260, 110),
    N("q5", "Как политика станет\nдействующей силой?\nМеханизмы и план", 1360, 190, "n", 260, 110),
    T("Уточнение можно повторять в разных местах стратегии", 340, 350, 20, "#495057"),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "s5"),
          E("s1", "q1", dashed=True, head=False), E("s2", "q2", dashed=True, head=False),
          E("s3", "q3", dashed=True, head=False), E("s4", "q4", dashed=True, head=False),
          E("s5", "q5", dashed=True, head=False)])

# own: objections to the position of refinement and the author's answer
D["ch05-refinement-position"] = dict(items=[
    T("Почему уточнение стоит после диагноза", 0, -50, 22, "#1971c2"),
    N("o1", "Возражение 1\nУточнение нужно\nдо диагноза", 0, 0, "r", 380, 110),
    N("o2", "Возражение 2\nКарта нужна до диагноза,\nмодель после политики", 0, 170, "r", 380, 110),
    N("o3", "Возражение 3\nУточнение — последний шаг,\nшаги замыкаются в цикл", 0, 340, "r", 380, 110),
    N("risk", "Главный риск:\nуточнение\nпропускают совсем", 560, 170, "y", 320, 110),
    N("a1", "Сделать карты и модели\nдешёвыми, чтобы их делало\nбольше людей", 1060, -10, "g", 400, 110),
    N("a2", "Уточнять после диагноза:\nтам меньше несущих\nчастей (load-bearing)", 1060, 170, "g", 400, 110),
    N("a3", "Уточнять можно\nв нескольких местах:\n3 малых или 1 большое", 1060, 350, "g", 400, 110),
], edges=[E("o1", "risk"), E("o2", "risk"), E("o3", "risk"),
          E("risk", "a1"), E("risk", "a2"), E("risk", "a3")])

if __name__ == "__main__":
    run_all(D)
