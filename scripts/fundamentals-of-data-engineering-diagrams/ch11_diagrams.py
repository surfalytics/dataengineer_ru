#!/usr/bin/env python3
"""Chapter 11 (the future of data engineering) diagrams. Usage: ch11_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Book Fig 11-1 (live data stack) next to the modern data stack
D["ch11-mds-to-live"] = dict(items=[
    Z("Modern data stack: batch, данные ограничены", -20, -60, 1540, 240),
    N("a1", "Приложения\nи SaaS (источники)", 0, 0, "n", 300, 100),
    N("a2", "ELT\nbatch, порциями", 400, 0, "p", 300, 100),
    N("a3", "Cloud data\nwarehouse", 800, 0, "p", 300, 100),
    N("a4", "BI и отчёты:\nчто и когда\nпроизошло", 1200, 0, "q", 300, 110),
    Z("Live data stack: потоки, данные непрерывны", -20, 260, 1540, 530),
    N("b1", "Приложение", 0, 340, "db", 300, 100),
    N("b2", "Streaming\npipeline", 400, 340, "db", 300, 100),
    N("b3", "Real-time OLAP\n(Druid, ClickHouse,\nRockset, Firebolt)", 800, 340, "p", 300, 120),
    N("b4", "ML и автоматические\nдействия в приложении", 400, 580, "g", 300, 110),
    T("Данные и «интеллект» ходят по кругу в реальном времени", 790, 610, 18, "#495057"),
], edges=[E("a1", "a2"), E("a2", "a3"), E("a3", "a4"),
          E("b1", "b2"), E("b2", "b3"), E("b3", "b4"), E("b4", "b1")])

# Cloud-scale data OS analogy
D["ch11-data-os"] = dict(items=[
    Z("Операционная система на одной машине", -20, -60, 1540, 240),
    N("o1", "Приложение", 0, 0, "n", 300, 100),
    N("o2", "Стандартные API", 400, 0, "n", 300, 100),
    N("o3", "Службы ОС\n(WindowServer,\nCoreAudio)", 800, 0, "p", 300, 110),
    N("o4", "Железо:\nэкран и звук", 1200, 0, "n", 300, 100),
    Z("Cloud-scale data OS: облако, много машин", -20, 260, 1540, 450),
    N("c1", "Pipeline или\nприложение данных", 0, 340, "n", 300, 100),
    N("c2", "Data API:\nстандарты пока\nформируются", 400, 340, "y", 300, 110),
    N("c3", "Сервисы: BigQuery,\nSnowflake, Lambda,\nBlob Storage", 800, 340, "p", 300, 110),
    N("c4", "Общий слой: object\nstorage, Parquet и Avro,\nкаталог метаданных", 1200, 340, "g", 300, 120),
    N("c5", "Orchestration:\nзапуск по зависимостям,\nIaC, деплой, lineage", 800, 550, "pu", 300, 110),
], edges=[E("o1", "o2"), E("o2", "o3"), E("o3", "o4"),
          E("c1", "c2"), E("c2", "c3"), E("c3", "c4"), E("c5", "c3")])

# Which trends are solid and which are speculation
D["ch11-trends"] = dict(items=[
    Z("Уже идёт: относительно надёжные прогнозы", -20, -60, 1540, 360),
    N("t1", "Проще инструменты:\nmanaged-сервисы,\nконнекторы", 0, 0, "g", 300, 110),
    N("t2", "Дата-инженеры\nподнимаются выше\nпо уровню задач", 400, 0, "g", 300, 110),
    N("t3", "Enterprisey:\ngovernance, DataOps,\nкачество", 800, 0, "pu", 300, 110),
    N("t4", "Роли размываются:\nsoftware, data и ML", 800, 160, "q", 300, 100),
    Z("Спекуляция: авторы сами не уверены", -20, 340, 1540, 270),
    N("s1", "Live data stack:\nstreaming, real-time\nOLAP, STL", 0, 420, "db", 300, 110),
    N("s2", "Приложения и данные\nсливаются в один стек", 400, 420, "db", 300, 110),
    N("s3", "Приложения и ML:\nкороткий цикл\nобратной связи", 800, 420, "db", 300, 110),
    N("s4", "Инструменты как\nspreadsheet поверх\ncloud OLAP", 1200, 420, "n", 300, 110),
    T("Цикл data engineering lifecycle остаётся при любом исходе", 0, 640, 20, "#495057"),
], edges=[E("t1", "t2"), E("t2", "t3"), E("t2", "t4"),
          E("s1", "s2"), E("s2", "s3")])

# ELT -> STL
D["ch11-stl"] = dict(items=[
    Z("ELT: modern data stack", -20, -60, 1540, 240),
    N("e1", "Источник", 0, 0, "n", 300, 100),
    N("e2", "Extract и load\nbatch, порциями", 400, 0, "p", 300, 100),
    N("e3", "Warehouse:\ntransform внутри\nбазы", 800, 0, "p", 300, 110),
    N("e4", "BI и отчёты", 1200, 0, "q", 300, 100),
    Z("STL: live data stack", -20, 260, 1540, 240),
    N("s1", "Источник\nсобытий", 0, 340, "n", 300, 100),
    N("s2", "Stream:\nнепрерывный\nприём", 400, 340, "db", 300, 110),
    N("s3", "Transform\nв потоке", 800, 340, "db", 300, 100),
    N("s4", "Load: real-time OLAP\nи приложение", 1200, 340, "g", 300, 100),
    T("Batch остаётся для обучения моделей и квартальных отчётов", 0, 540, 20, "#495057"),
], edges=[E("e1", "e2"), E("e2", "e3"), E("e3", "e4"),
          E("s1", "s2"), E("s2", "s3"), E("s3", "s4")])

if __name__ == "__main__":
    run_all(D)
