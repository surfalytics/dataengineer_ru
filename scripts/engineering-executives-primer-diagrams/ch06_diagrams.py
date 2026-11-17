#!/usr/bin/env python3
"""Chapter 6 (measuring engineering organizations) diagrams. Usage: ch06_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Main: four buckets for yourself, four kinds of stakeholders
D["ch06-measure-map"] = dict(items=[
    T("Измеряем для себя", 0, -50, 22, "#1971c2"),
    T("Измеряем для других", 760, -50, 22, "#2f9e44"),
    N("plan", "Plan\nкакие проекты выбрать;\nпроекты и их эффект", 0, 0, "p", 330, 110),
    N("op", "Operate\nкачество исполнения:\nинциденты, задержка, cost to serve", 0, 150, "p", 330, 110),
    N("opt", "Optimize\nпродуктивность:\nlead time, deploy frequency, опрос", 0, 300, "y", 330, 110),
    N("ins", "Inspire\nсписок прорывов,\nкоторые стали «очевидными»", 0, 450, "pu", 330, 110),
    N("sp", "Стратегические коллеги\nProduct, Design, Sales", 760, 0, "g", 360, 110),
    N("ceo", "CEO и board\nцели и прогресс\nпо ним", 760, 150, "g", 360, 110),
    N("fin", "Finance\nheadcount, вендоры,\ncapitalization", 760, 300, "n", 360, 110),
    N("tac", "Тактические коллеги\nSupport, Legal:\nих конкретные числа", 760, 450, "n", 360, 110),
], edges=[E("plan", "sp", "reuse"), E("plan", "ceo"), E("op", "ceo", "reuse"),
          E("opt", "ceo", "не показывать", dashed=True)])

# Three rules for sequencing
D["ch06-sequencing"] = dict(items=[
    N("start", "Новая метрика\nв списке", 0, 100, "n", 230, 100),
    N("q1", "Трудно\nизмерить?", 330, 85, "y", 260, 130, "diamond"),
    N("easy", "Лёгкая метрика:\nберём, даже неточную.\nЭто строит доверие", 760, 0, "g", 320, 110),
    N("q2", "Изменит ли\nданные решение?", 330, 330, "y", 260, 130, "diamond"),
    N("proxy", "Берём простой\nproxy вместо трудной", 0, 345, "n", 230, 100),
    N("hard", "Трудная метрика:\nберём, потому что\nона влияет на решения", 760, 330, "g", 320, 110),
    N("one", "Правило 3:\nодна новая\nметрика за раз", 1200, 165, "p", 240, 120),
], edges=[E("start", "q1"), E("q1", "easy", "нет"), E("q1", "q2", "да"),
          E("q2", "proxy", "нет"), E("q2", "hard", "да"),
          E("easy", "one"), E("hard", "one")])

# Loop for building confidence in data
D["ch06-data-confidence"] = dict(items=[
    N("s1", "1. Смотрим данные\nраз в неделю: месяц,\nквартал, год, цель", 0, 0, "p", 300, 120),
    N("s2", "2. Держим гипотезу:\nпочему данные\nменяются", 380, 0, "p", 300, 120),
    N("s3", "3. Данные идут\nпротив гипотезы?", 760, 0, "y", 300, 120),
    N("s4", "4. Копаем, пока\nне объясним, почему\nмы ошиблись", 760, 230, "r", 300, 120),
    N("s5", "5. Уточняем гипотезу\nи сами метрики", 380, 230, "g", 300, 120),
    N("i1", "Коллеги с другим\nвзглядом", 1230, 20, "pu", 290, 90),
    N("i2", "Срезы: регион,\nязык, сегмент", 1230, 175, "pu", 290, 90),
    N("i3", "Ощущения людей:\nсовпадают с цифрами?", 1230, 330, "pu", 290, 90),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4", "да"), E("s4", "s5"),
          E("s5", "s1", "следующий цикл"),
          E("i1", "s4", dashed=True), E("i2", "s4", dashed=True), E("i3", "s4", dashed=True)])

if __name__ == "__main__":
    run_all(D)
