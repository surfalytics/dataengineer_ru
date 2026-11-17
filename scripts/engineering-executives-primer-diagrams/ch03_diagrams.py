#!/usr/bin/env python3
"""Chapter 3 (Engineering strategy) diagrams. Usage: python3 ch03_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}
BLUE, GREEN = "#1971c2", "#2f9e44"

# ---------- main: three parts of a strategy with the chapter's example ----------
D["ch03-strategy-parts"] = dict(items=[
    T("Strategy по Румельту: три части и пример из главы", 0, -50, 24, BLUE),
    N("dg", "1. Diagnosis\nв чём проблема\nи её причина", 0, 0, "p", 340, 120),
    N("gp", "2. Guiding policies\nправила выбора\nс trade-off", 460, 0, "y", 340, 120),
    N("ca", "3. Coherent actions\nконкретные шаги\nпо этим правилам", 920, 0, "g", 340, 120),
    N("dgx", "Пример:\nтесты нестабильны,\nкаждая третья сборка падает", 0, 230, "n", 340, 130),
    N("gpx", "Пример:\n10% времени продуктовых\nкоманд идёт на developer\nproductivity", 460, 230, "n", 340, 130),
    N("cax", "Пример:\nworking group по\nстабильности тестов", 920, 230, "n", 340, 130),
    T("Без третьей части стратегия ничего не меняет: важны только согласованные действия.", 0, 410, 20, GREEN),
], edges=[E("dg", "gp"), E("gp", "ca"), E("dg", "dgx", dashed=True), E("gp", "gpx", dashed=True), E("ca", "cax", dashed=True)])

# ---------- Fig 3-1: company strategies ----------
D["ch03-company-strategies"] = dict(items=[
    T("Другие стратегии компании, на которых стоит diagnosis", 0, -50, 24, BLUE),
    N("biz", "Стратегия бизнеса\n(часто не записана)", 0, 0, "q", 330, 110),
    N("prod", "Стратегия продукта\n(часто не записана)", 0, 190, "q", 330, 110),
    N("draft", "Ваш приватный черновик:\nсогласован с владельцем,\nне публикуется", 480, 95, "y", 340, 120),
    N("diag", "Diagnosis\nвашей engineering\nstrategy", 970, 95, "g", 300, 120),
], edges=[E("biz", "draft"), E("prod", "draft"), E("draft", "diag")])

# ---------- writing process ----------
W3, H3 = 340, 120
cx = [0, 460, 920]
r = [0, 230, 460]
D["ch03-writing-process"] = dict(items=[
    T("Как engineering executive пишет strategy: порядок шагов", 0, -50, 24, BLUE),
    N("s1", "Решить писать самому.\nАудитория: старшие\nменеджеры и инженеры", cx[0], r[0], "p", W3, H3),
    N("s2", "Список стейкхолдеров.\n3–5 человек в\nstrategy working group", cx[1], r[0], "p", W3, H3),
    N("s3", "Diagnosis: черновик,\nпотом 1:1 с каждым\nиз группы", cx[2], r[0], "y", W3, H3),
    N("s4", "Guiding policies:\nгруппа и 2–3 внешних\nexecutives", cx[2], r[1], "y", W3, H3),
    N("s5", "Всем стейкхолдерам:\nуже общий документ,\nубрать чувствительное", cx[1], r[1], "y", W3, H3),
    N("s6", "Coherent actions:\nправки с группой", cx[0], r[1], "y", W3, H3),
    N("s7", "1:1 с теми, кто\nможет быть против", cx[0], r[2], "q", W3, H3),
    N("s8", "Встреча для всей\nорганизации, отзывы\nоколо недели", cx[1], r[2], "q", W3, H3),
    N("s9", "Финал, анонс,\nпроверка влияния\nчерез 2 месяца", cx[2], r[2], "g", W3, H3),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "s5"), E("s5", "s6"), E("s6", "s7"), E("s7", "s8"), E("s8", "s9")])

# ---------- policies -> altitude check -> actions ----------
D["ch03-policies-to-actions"] = dict(items=[
    T("От diagnosis к действиям: три вопроса, три проверки, три вида шагов", 0, -50, 24, BLUE),
    N("q1", "Как распределяем\nресурсы?", 0, 0, "p", 330, 110),
    N("q2", "Какие правила\nобязательны для всех?", 0, 160, "p", 330, 110),
    N("q3", "Как принимаем\nрешения?", 0, 320, "p", 330, 110),
    N("gp", "Guiding\npolicies", 480, 160, "y", 240, 110),
    N("chk", "Проверка высоты:\napplicable\nenforced\ncreates leverage", 860, 110, "q", 330, 210),
    N("act", "Coherent actions:\nenforcements\nescalations\ntransitions", 1330, 110, "g", 330, 210),
], edges=[E("q1", "gp"), E("q2", "gp"), E("q3", "gp"), E("gp", "chk"), E("chk", "act")])

if __name__ == "__main__":
    run_all(D)
