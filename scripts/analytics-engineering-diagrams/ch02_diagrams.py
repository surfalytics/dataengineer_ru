#!/usr/bin/env python3
"""Chapter 2 (data modeling for analytics) Excalidraw diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all).
ER diagrams of this chapter are Mermaid: ch02_mermaid.sh + src/ch02-*.mmd."""
from excb import N, E, Z, T, run_all

D = {}

# own (main): from business understanding to a physical model
D["ch02-modeling-phases"] = dict(items=[
    N("b0", "Понимание\nбизнеса", 0, 0, "n"),
    N("c1", "Концептуальная\nмодель", 310, 0, "p"),
    N("c2", "Логическая\nмодель", 620, 0, "p"),
    N("c3", "Физическая\nмодель", 930, 0, "p"),
    N("r0", "Интервью, документы,\nфакты простыми\nфразами", 0, 170, "y", 250, 110),
    N("r1", "ERD: сущности,\nатрибуты, связи,\nкардинальность", 310, 170, "y", 250, 110),
    N("r2", "Таблицы, первичные\nи внешние ключи,\nнормализация", 620, 170, "y", 250, 110),
    N("r3", "DDL под СУБД:\nтипы, ограничения,\nиндексы", 930, 170, "y", 250, 110),
], edges=[E("b0", "c1"), E("c1", "c2"), E("c2", "c3"),
          E("b0", "r0", dashed=True), E("c1", "r1", dashed=True), E("c2", "r2", dashed=True), E("c3", "r3", dashed=True)])

# Fig 2-5: dbt modularity, models reused across layers
D["ch02-dbt-layers"] = dict(items=[
    Z("Сырые таблицы", -25, -70, 300, 460),
    Z("Staging: view", 305, -70, 300, 460),
    Z("Intermediate: ephemeral", 635, -70, 300, 460),
    Z("Marts: table", 965, -70, 300, 460),
    N("r1", "raw_books", 0, 0, "n", 250, 90), N("r2", "raw_authors", 0, 140, "n", 250, 90),
    N("r3", "raw_sales", 0, 280, "n", 250, 90),
    N("s1", "stg_books", 330, 0, "p", 250, 90), N("s2", "stg_authors", 330, 140, "p", 250, 90),
    N("s3", "stg_sales", 330, 280, "p", 250, 90),
    N("i1", "int_book_authors", 660, 70, "pu", 250, 90), N("i2", "int_book_sales", 660, 210, "pu", 250, 90),
    N("m1", "mart_book_authors", 990, 70, "g", 250, 90), N("m2", "mart_genre_sales", 990, 210, "g", 250, 90),
    T("source(): только сырые таблицы.  ref(): все связи между моделями", 0, 420, 18),
], edges=[E("r1", "s1"), E("r2", "s2"), E("r3", "s3"),
          E("s1", "i1"), E("s2", "i1"), E("s1", "i2"), E("s3", "i2"),
          E("i1", "m1"), E("i2", "m2")])

# Fig 2-6: medallion architecture in a lakehouse, dbt between layers
D["ch02-medallion"] = dict(items=[
    Z("Lakehouse: Delta Lake, Iceberg или Hudi на облачном хранилище", 270, -60, 1280, 380),
    N("src1", "Batch-данные", 0, 40, "n", 220, 90), N("src2", "Потоковые\nданные", 0, 180, "n", 220, 90),
    N("pipe", "Pipeline\nзагрузки", 300, 110, "g", 200, 90),
    N("br", "Bronze:\nсырые копии", 580, 110, "q", 240, 90),
    N("sv", "Silver:\nочищенные сущности", 930, 110, "n", 240, 90),
    N("gd", "Gold:\nответы бизнесу", 1280, 110, "y", 240, 90),
    T("как в источнике\n+ метаданные загрузки", 590, 225, 16),
    T("чистка, дедупликация;\n3NF, star или Data Vault", 940, 225, 16),
    T("агрегаты\nдля BI и ML", 1290, 225, 16),
    N("u1", "Аналитика\nна SQL", 1620, 0, "p", 240, 90),
    N("u2", "Визуализация", 1620, 110, "p", 240, 90),
    N("u3", "Machine learning", 1620, 220, "p", 240, 90),
], edges=[E("src1", "pipe"), E("src2", "pipe"), E("pipe", "br"), E("br", "sv", "dbt"), E("sv", "gd", "dbt"),
          E("gd", "u1"), E("gd", "u2"), E("gd", "u3")])

if __name__ == "__main__":
    run_all(D)
