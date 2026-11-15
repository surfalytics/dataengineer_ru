#!/usr/bin/env python3
"""Chapter 1 (data engineering for the enterprise amid AI disruption) diagrams.
Usage: python3 scripts/redefining-de-ai-diagrams/ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own (main): data engineering is a bridge between operational systems and consumers, with a feedback loop
D["ch01-de-bridge"] = dict(items=[
    N("src", "Операционные\nсистемы\n\nERP, CRM,\nпродукт, SaaS,\nлоги, IoT,\nвнешние данные", -120, 0, "n", 260, 300),
    Z("Инжиниринг данных", 310, -60, 1000, 400),
    N("ing", "Ingestion\nи pipeline", 340, 20, "p", 280, 130),
    N("cln", "Очистка\nи преобразование", 680, 20, "pu", 280, 130),
    N("sto", "Хранение\nи моделирование", 1020, 20, "db", 270, 130),
    N("qa", "Качество, observability, lineage, compliance — на всём пути данных", 340, 210, "g", 950, 100),
    N("cons", "Потребители\n\nBI и дашборды,\nML-модели,\nagentic AI,\nприложения", 1360, 0, "y", 280, 300),
    N("fb1", "Инсайты\nи intelligence", 1360, 420, "q", 280, 100),
    N("fb2", "Решения\nи действия бизнеса", -120, 420, "q", 260, 100),
], edges=[E("src", "ing", "данные"), E("ing", "cln"), E("cln", "sto"), E("sto", "cons"),
          E("cons", "fb1"), E("fb1", "fb2", "обратная связь", dashed=True), E("fb2", "src")])

# own: civic governance branches -> data governance primitives
D["ch01-governance-branches"] = dict(items=[
    T("Сверху — три ветви власти в государстве, снизу — те же функции для данных компании", 0, -45, 22, "#495057"),
    N("leg", "Законодательная:\nпринимает правила", 0, 0, "n", 330, 110),
    N("exe", "Исполнительная:\nследит, чтобы правила\nвыполнялись", 400, 0, "n", 330, 110),
    N("jud", "Судебная:\nрешает, было ли нарушение\nи что за ним следует", 800, 0, "n", 330, 110),
    N("pol", "Политики данных:\nкто и к чему имеет\nдоступ, сколько хранить", 0, 260, "p", 330, 120),
    N("enf", "Исполнение:\nроли, проверки\nв pipeline, маскирование", 400, 260, "p", 330, 120),
    N("aud", "Контроль:\nаудит, lineage,\nразбор инцидентов", 800, 260, "p", 330, 120),
    N("dg", "Data governance — способы выполнять эти три функции для данных", 0, 450, "g", 1130, 90),
], edges=[E("leg", "pol", dashed=True), E("exe", "enf", dashed=True), E("jud", "aud", dashed=True),
          E("pol", "dg", head=False), E("enf", "dg", head=False), E("aud", "dg", head=False)])

# own: platform effect - without a platform each AI use case builds its own pipelines
D["ch01-platform-effect"] = dict(items=[
    Z("Без платформы", 0, 0, 640, 420),
    N("p1", "Свой\npipeline 1", 25, 80, "r", 180, 90),
    N("p2", "Свой\npipeline 2", 230, 80, "r", 180, 90),
    N("p3", "Свой\npipeline 3", 435, 80, "r", 180, 90),
    N("m1", "Модель 1", 25, 250, "y", 180, 80),
    N("m2", "Модель 2", 230, 250, "y", 180, 80),
    N("m3", "Модель 3", 435, 250, "y", 180, 80),
    T("Каждая новая задача стоит\nстолько же, сколько первая", 25, 350, 18, "#e03131"),
    Z("С платформой", 700, 0, 640, 420),
    N("pl", "Общая платформа: проверенные\nдатасеты, признаки, документация", 725, 80, "g", 590, 90),
    N("n1", "Модель 1", 725, 250, "y", 130, 80),
    N("n2", "Модель 2", 878, 250, "y", 130, 80),
    N("n3", "Модель 3", 1031, 250, "y", 130, 80),
    N("nn", "Модель N", 1185, 250, "y", 130, 80),
    T("Цена N-й задачи близка к нулю:\nостаются бизнес-контекст, проверки, governance", 725, 350, 18, "#2f9e44"),
], edges=[E("p1", "m1"), E("p2", "m2"), E("p3", "m3"),
          E("pl", "n1"), E("pl", "n2"), E("pl", "n3"), E("pl", "nn")])

# own: the AI slop cycle and where a human breaks it
D["ch01-slop-cycle"] = dict(items=[
    N("a", "AI быстро пишет\nSQL, схемы,\nтесты, документацию", 0, 0, "p", 300, 110),
    N("b", "Результат выглядит\nверно и проходит\nбазовые проверки", 400, 0, "p", 300, 110),
    N("c", "Команда принимает\nего без смысловой\nпроверки", 800, 0, "r", 300, 110),
    N("d", "Качество кода\nи данных падает:\nрастёт смысловой долг", 800, 340, "r", 300, 110),
    N("e", "Новые AI-инструменты\nучатся на этом коде\nи повторяют ошибки", 0, 340, "r", 300, 110),
    N("h", "Человек разрывает цикл:\nсмысловая проверка,\nquality gates, отметки\n«принято / изменено / отклонено»", 340, 160, "g", 420, 130),
], edges=[E("a", "b"), E("b", "c"), E("c", "d"), E("d", "e"), E("e", "a"),
          E("h", "c", dashed=True)])

if __name__ == "__main__":
    run_all(D)
