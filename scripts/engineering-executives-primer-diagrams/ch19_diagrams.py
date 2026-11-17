#!/usr/bin/env python3
"""Chapter 19 (engineering processes) diagrams. Usage: ch19_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

tops = [
    ("Early Startup\nдо 30-50 человек", "p"),
    ("Baseline\nот 50 человек", "g"),
    ("Specialized\nEngineering Roles\nот 200 инженеров", "p"),
    ("Company\nEmbedded Roles\nинженерия очень большая", "p"),
    ("Business Unit Local\nнесколько бизнес-юнитов", "p"),
]
descs = [
    "Основатель или\nруководитель функции\nделает всё сам",
    "People ведёт процессы\nкомпании, инженеры и\nменеджеры ведут свои",
    "TPM или Engineering\nOperations ведут\nпроцессы инженерии",
    "People и Recruiting\nвыделяют людей\nпод инженерию",
    "У каждого юнита\nсвоя инженерия,\nобщего руководителя нет",
]
items = []
for i, ((t, k), d) in enumerate(zip(tops, descs)):
    items.append(N(f"t{i}", t, i * 380, 0, k, 300, 130))
    items.append(N(f"d{i}", d, i * 380, 230, "n", 300, 130))
items.append(T("Компании проходят паттерны в этом порядке. Без особой причины автор советует Baseline", 0, 400, 20, "#495057"))
D["ch19-five-patterns"] = dict(items=items,
    edges=[E(f"t{i}", f"t{i+1}") for i in range(4)] + [E(f"t{i}", f"d{i}") for i in range(5)])

D["ch19-baseline-tweaks"] = dict(items=[
    N("top", "Baseline, меньше 100 инженеров:\nхочется сменить паттерн", 380, 0, "r", 340, 110),
    N("a", "1. Ротация\nшесть месяцев на процесс,\nдвое с разным стартом", 0, 220, "p", 340, 130),
    N("b", "2. Интерес\nincident review + планирование,\nspec review + стратегия", 380, 220, "y", 340, 130),
    N("c", "3. Признание\nповышения ценят эту работу,\nназывать людей на all-hands", 760, 220, "g", 340, 130),
    N("res", "Baseline работает дольше,\nчем ожидаешь", 380, 440, "g", 340, 100),
], edges=[E("top", "a"), E("top", "b"), E("top", "c"), E("a", "res"), E("b", "res"), E("c", "res")])

D["ch19-budget-traps"] = dict(items=[
    N("top", "Предложение: нанять TPM\nили Engineering Operations", 380, 0, "p", 340, 110),
    N("a", "Нет роста компании:\nразговор про «больше\nменьшими силами»", 0, 220, "r", 340, 130),
    N("b", "Доли портфеля, например\nG&A 20%, S&M 30%, R&D 50%:\nколлеги теряют свой G&A", 380, 220, "r", 340, 130),
    N("c", "Бюджет в headcount:\n3 TPM выглядят дороже\n2 Staff-инженеров,\nхотя это не так", 760, 220, "r", 340, 130),
    N("res", "Совет автора: оставайтесь на Baseline,\nпока выручка или headcount\nне растут заметно", 330, 440, "g", 440, 120),
], edges=[E("top", "a"), E("top", "b"), E("top", "c"), E("a", "res"), E("b", "res"), E("c", "res")])

if __name__ == "__main__":
    run_all(D)
