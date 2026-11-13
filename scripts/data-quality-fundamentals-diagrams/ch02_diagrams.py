#!/usr/bin/env python3
"""Chapter 2 (building blocks of a reliable data system) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 2-1: data platform, operational vs analytical layers (main diagram)
D["ch02-data-platform"] = dict(items=[
    Z("Операционные данные", -25, -80, 590, 450),
    Z("Слой интеграции", 620, -80, 290, 450),
    Z("Аналитические данные", 950, -80, 600, 450),
    N("s1", "Датчики,\nIoT-потоки", 0, 0, "n", 210, 100),
    N("s2", "Логи приложений\nи транзакций", 0, 130, "n", 210, 100),
    N("s3", "Ответы\nWeb API", 0, 260, "n", 210, 100),
    N("lake", "Data lake", 330, 130, "db", 210, 100),
    N("int", "Интеграция:\nFivetran, Glue,\nMatillion", 660, 115, "pu", 210, 130),
    N("dwh", "Data warehouse", 990, 130, "db", 210, 100),
    N("bi", "Отчёты,\nдашборды, ML", 1300, 130, "g", 210, 100),
    N("o1", "Быстро отвечать на мелкие запросы:\nнизкая latency (OLTP)", 0, 420, "y", 560, 90),
    N("o2", "Считать большие агрегаты:\nвысокая throughput (OLAP)", 990, 420, "y", 520, 90),
], edges=[E("s1", "lake"), E("s2", "lake"), E("s3", "lake"), E("lake", "int"), E("int", "dwh"), E("dwh", "bi")])

# own: warehouse vs lake vs lakehouse
D["ch02-warehouse-vs-lake"] = dict(items=[
    N("h1", "Data warehouse", 260, 0, "db", 400, 90), N("h2", "Data lake", 700, 0, "db", 400, 90),
    N("l1", "Схема", 0, 120, "n", 220, 90), N("a1", "Schema on write:\nструктуру задают при записи", 260, 120, "p", 400, 90),
    N("b1", "Schema on read:\nструктуру выводят при чтении", 700, 120, "p", 400, 90),
    N("l2", "Данные и языки", 0, 240, "n", 220, 90), N("a2", "Таблицы, SQL.\nPython только после выгрузки", 260, 240, "p", 400, 90),
    N("b2", "Любые файлы. SQL, Python,\nSpark, Hadoop", 700, 240, "p", 400, 90),
    N("l3", "Риски качества", 0, 360, "n", 220, 90),
    N("a3", "Жёсткость, плохие данные\nпроскакивают, выгрузка ломается", 260, 360, "r", 400, 90),
    N("b3", "Blind ETL, swampification,\nбольше endpoints", 700, 360, "r", 400, 90),
    N("lh", "Lakehouse: SQL на файлах (Presto, Spark), схема (Parquet),\nACID (Delta Lake, Hudi), managed-сервисы", 260, 540, "g", 840, 100),
], edges=[E("a3", "lh"), E("b3", "lh")])

# own: four steps of pulling metrics from the warehouse
D["ch02-four-steps"] = dict(items=[
    N("s1", "1. Инвентарь\ntables, columns", 0, 0, "p", 250, 100),
    N("s2", "2. Свежесть\nи объём", 300, 0, "p", 250, 100),
    N("s3", "3. История\nзапросов", 600, 0, "p", 250, 100),
    N("s4", "4. Health check\nпо полям", 900, 0, "p", 250, 100),
    N("r1", "Что отслеживать;\nкак меняется схема", 0, 180, "n", 250, 110),
    N("r2", "Строки, байты,\nвремя обновления", 300, 180, "n", 250, 110),
    N("r3", "Кто пишет и читает;\nlineage; стоимость", 600, 180, "n", 250, 110),
    N("r4", "Completeness, zero rate,\nmean, quantiles по часам", 900, 180, "n", 250, 110),
    N("st", "Храним метрики во времени\nи сравниваем с прошлым", 1250, 0, "g", 280, 100),
    N("al", "Алерты и общий UI\nдля root cause analysis", 1250, 180, "g", 280, 110),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "st"), E("st", "al"),
          E("s1", "r1", dashed=True), E("s2", "r2", dashed=True), E("s3", "r3", dashed=True), E("s4", "r4", dashed=True)])

# own: catalog vs discovery
D["ch02-catalog-vs-discovery"] = dict(items=[
    Z("Каталог данных: идеальное состояние, ручная работа", -25, -70, 1480, 230),
    N("c1", "Договориться,\nкакие данные важны", 0, 0, "p", 230, 100),
    N("c2", "Назначить\nвладельцев", 280, 0, "p", 230, 100),
    N("c3", "Заполнить: вручную\nили SQL-парсером", 560, 0, "p", 230, 100),
    N("c4", "Метаданные в БД\n(DataHub, Amundsen)", 840, 0, "db", 230, 100),
    N("c5", "Со временем\nустаревает", 1120, 0, "r", 230, 100),
    Z("Data discovery: текущее состояние, автоматика", -25, 230, 1480, 230),
    N("d1", "Метаданные,\nquery logs, lineage", 0, 300, "q", 230, 100),
    N("d2", "Автоматический\nразбор по доменам", 280, 300, "pu", 230, 100),
    N("d3", "Живая картина:\nкак данные есть сейчас", 560, 300, "g", 230, 100),
    N("d4", "Свежо? Кто использует?\nКакие зависимости?", 840, 300, "g", 230, 100),
    N("d5", "Self-service\nбез отдела поддержки", 1120, 300, "g", 230, 100),
], edges=[E("c1", "c2"), E("c2", "c3"), E("c3", "c4"), E("c4", "c5"),
          E("d1", "d2"), E("d2", "d3"), E("d3", "d4"), E("d4", "d5")])

if __name__ == "__main__":
    run_all(D)
