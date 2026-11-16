#!/usr/bin/env python3
"""DDIA 2nd ed., chapter 1 (trade-offs in data systems architecture) diagrams.
Usage: python3 scripts/ddia-diagrams/ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 1-1 (extended with data lake and reverse ETL): operational -> ETL -> analytical. Main diagram.
D["ch01-operational-analytical"] = dict(items=[
    Z("Операционные системы (OLTP)", -30, -60, 300, 650),
    N("s1", "Сайт и заказы\n(своя БД)", 0, 0, "p", 240, 100),
    N("s2", "Кассы\nв магазинах", 0, 140, "p", 240, 100),
    N("s3", "Склад\nи запасы", 0, 280, "p", 240, 100),
    N("s4", "SaaS: CRM,\nрассылки (API)", 0, 420, "n", 240, 100),
    N("etl", "ETL / pipeline\nextract → transform\n→ load", 400, 170, "y", 260, 140),
    Z("Аналитические системы (OLAP)", 780, -60, 680, 520),
    N("lake", "Data lake\nсырые файлы\nлюбого формата", 810, 0, "db", 260, 110),
    N("dw", "Хранилище данных\n(data warehouse)\nSQL, схема для анализа", 810, 300, "db", 260, 120),
    N("ds", "Data scientists\nML, NLP, Python,\nSpark", 1170, 0, "pu", 250, 110),
    N("ba", "Бизнес-аналитики\nBI, отчёты,\nдашборды", 1170, 300, "g", 250, 120),
    N("rev", "Reverse ETL: модели и\nрезультаты анализа\nидут обратно в продукт", 810, 560, "q", 300, 110),
], edges=[E("s1", "etl"), E("s2", "etl"), E("s3", "etl"), E("s4", "etl"),
          E("etl", "lake"), E("etl", "dw"), E("lake", "dw", "иногда", dashed=True),
          E("lake", "ds"), E("dw", "ba"), E("dw", "rev", dashed=True), E("rev", "s4", dashed=True)])

# Fig 1-2: spectrum of outsourcing software and its operation
D["ch01-build-vs-buy"] = dict(items=[
    T("Кто пишет ПО и кто его запускает", 0, -60, 22, "#1971c2"),
    N("own", "Своё ПО\nпишем сами,\nзапускаем сами", 0, 0, "p", 300, 120),
    N("self", "Готовое ПО, self-hosting\nopen source или коммерческое;\nсвой сервер или VM (IaaS)", 420, 0, "y", 340, 120),
    N("cloud", "Облачный сервис, SaaS\nпишет и запускает вендор;\nдоступ через веб или API", 880, 0, "g", 340, 120),
    N("w1", "Пишем: мы\nЗапускаем: мы", 0, 200, "n", 300, 90),
    N("w2", "Пишем: вендор\nЗапускаем: мы", 420, 200, "n", 340, 90),
    N("w3", "Пишем: вендор\nЗапускаем: вендор", 880, 200, "n", 340, 90),
    T("← больше контроля и настройки", 0, 330, 20, "#495057"),
    T("меньше работы по эксплуатации →", 900, 330, 20, "#495057"),
], edges=[E("own", "self"), E("self", "cloud"),
          E("own", "w1", head=False), E("self", "w2", head=False), E("cloud", "w3", head=False)])

# own: separation of storage and compute
D["ch01-storage-compute"] = dict(items=[
    Z("Традиционно: один сервер", -30, -60, 340, 470),
    N("cpu", "CPU и RAM\nвычисления", 0, 0, "p", 280, 100),
    N("disk", "Локальные диски\n+ RAID\nдолгое хранение", 0, 240, "db", 280, 120),
    Z("Cloud native: хранение отдельно", 380, -60, 980, 470),
    N("v1", "VM 1: вычисления\nлокальный диск —\nтолько кэш", 410, 0, "p", 280, 110),
    N("v2", "VM 2: вычисления\nлокальный диск —\nтолько кэш", 740, 0, "p", 280, 110),
    N("v3", "VM 3: вычисления\nлокальный диск —\nтолько кэш", 1070, 0, "p", 280, 110),
    N("s3", "Object storage (S3)\nбольшие блоки данных,\nданные на многих машинах", 410, 240, "db", 610, 120),
    N("meta", "Отдельный сервис\nдля мелких значений", 1070, 240, "n", 280, 120),
], edges=[E("cpu", "disk", "шина"), E("v1", "s3", "сеть"), E("v2", "s3", "сеть"),
          E("v3", "meta", "сеть"), E("v3", "s3")])

if __name__ == "__main__":
    run_all(D)
