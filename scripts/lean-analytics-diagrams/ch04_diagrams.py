#!/usr/bin/env python3
"""Chapter 4 (data-driven vs data-informed) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: humans do inspiration, machines do validation (Omniture case)
D["ch04-human-machine"] = dict(items=[
    T("Люди придумывают, машины проверяют", 0, -50, 22, "#1971c2"),
    N("idea", "Человек:\nидеи и варианты\n(куратор подбирает\nкартинки)", 0, 0, "pu", 270, 130),
    N("test", "Машина:\nтестирует варианты,\nищет лучший CTR", 470, 0, "p", 270, 130),
    N("res", "Результат:\nлучший вариант\nиз предложенных", 940, 0, "g", 270, 130),
    N("check", "Человек:\nсмотрит на общую картину:\nбренд, клиенты, видение", 470, 300, "y", 330, 130),
], edges=[E("idea", "test", "варианты"), E("test", "res", "цифры"),
          E("res", "check"), E("check", "idea", "новые идеи", dashed=True)])

# own: local maximum, tricycle vs four wheels
D["ch04-local-maximum"] = dict(items=[
    Z("Оптимизация по данным: внутри известной системы", -20, -60, 860, 230),
    N("v1", "3 колеса:\nвариант 1", 0, 0, "n", 220, 100),
    N("v2", "3 колеса:\nвариант 2", 300, 0, "n", 220, 100),
    N("tri", "Трицикл:\nлучший из трёх колёс\n(локальный максимум)", 580, 0, "p", 240, 120),
    N("car", "4 колеса:\nновая система,\nкуда устойчивее", 580, 330, "g", 240, 120),
    T("Шаг, которого данные\nне сделают: человек\nменяет саму задачу", 120, 330, 20, "#9c36b5"),
], edges=[E("v1", "v2"), E("v2", "tri"), E("tri", "car", "«а если 4 колеса?»", dashed=True)])

# own: Lean Startup as the road to a big vision
D["ch04-lean-vision"] = dict(items=[
    N("start", "Плацдарм:\nпервый рынок\nили сегмент", 0, 0, "n", 240, 110),
    N("lean", "Lean Startup:\nстроить → измерять →\nучиться", 380, 0, "p", 260, 110),
    N("vision", "Большое видение:\nизменить мир,\nа не регион", 780, 0, "g", 260, 110),
    N("learn", "Новые знания о проблеме,\nклиентах и доходе\nрасширяют видение", 380, 260, "y", 300, 110),
], edges=[E("start", "lean"), E("lean", "vision", "путь"),
          E("lean", "learn"), E("learn", "vision", dashed=True)])

if __name__ == "__main__":
    run_all(D)
