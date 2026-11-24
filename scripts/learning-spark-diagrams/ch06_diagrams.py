#!/usr/bin/env python3
"""Chapter 6 (Spark SQL and Datasets) diagrams. Usage: ch06_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 6-1, 6-2: JVM object <-> encoder <-> Tungsten row
D["ch06-encoders"] = dict(items=[
    N("jvm", "Объект JVM\nMyClass(Int, String, String)\nзаголовок, hashcode, служебные поля\n«abcd» занимает 48 байт", 0, 0, "r", 400, 150),
    N("enc", "Encoder\nбыстро переводит\nв обе стороны", 560, 0, "y", 300, 150),
    N("tun", "Строка Tungsten\nодин сплошной блок off-heap\nчисло | указатели | данные строк", 1020, 0, "g", 460, 150),
    N("gc", "Объекты лежат в куче JVM:\nработает сборщик мусора (GC)", 0, 260, "n", 400, 100),
    N("off", "Доступ по адресу и смещению,\nGC не мешает, места меньше", 1020, 260, "n", 460, 100),
    T("serialize: JVM → Tungsten, deserialize: Tungsten → JVM", 380, -60, 20, "#495057"),
], edges=[E("jvm", "enc", "serialize"), E("enc", "tun", "serialize"),
          E("jvm", "gc", dashed=True, head=False), E("tun", "off", dashed=True, head=False)])

# Fig 6-3: lambda breaks the chain, DSL keeps it inside Tungsten
D["ch06-lambda-vs-dsl"] = dict(items=[
    T("Смесь lambda и DSL: на каждом переходе Spark делает SerDe", 0, -50, 22, "#e03131"),
    N("a1", "filter\nlambda", 0, 0, "r", 200, 90),
    N("a2", "filter\nDSL", 320, 0, "g", 200, 90),
    N("a3", "filter\nlambda", 640, 0, "r", 200, 90),
    N("a4", "filter\nDSL", 960, 0, "g", 200, 90),
    N("a5", "count", 1280, 0, "p", 200, 90),
    T("Только DSL: всё остаётся в формате Tungsten, SerDe не нужен", 0, 190, 22, "#2f9e44"),
    N("b1", "filter\nDSL", 0, 240, "g", 200, 90),
    N("b2", "filter\nDSL", 320, 240, "g", 200, 90),
    N("b3", "filter\nDSL", 640, 240, "g", 200, 90),
    N("b4", "filter\nDSL", 960, 240, "g", 200, 90),
    N("b5", "count", 1280, 240, "p", 200, 90),
], edges=[E("a1", "a2", "SerDe"), E("a2", "a3", "SerDe"), E("a3", "a4", "SerDe"), E("a4", "a5"),
          E("b1", "b2"), E("b2", "b3"), E("b3", "b4"), E("b4", "b5")])

# Own: Catalyst sees DSL, lambda is a black box
D["ch06-catalyst-opaque"] = dict(items=[
    N("d1", "DSL / SQL\ncol(\"usage\") > 900", 0, 0, "g", 300, 100),
    N("d2", "Catalyst видит\nвыражение", 460, 0, "y", 300, 100),
    N("d3", "Оптимизация:\nPushedFilters, меньше чтения", 920, 0, "g", 340, 100),
    N("l1", "lambda / UDF\nu => u.usage > 900", 0, 220, "r", 300, 100),
    N("l2", "Catalyst видит\nчёрный ящик", 460, 220, "y", 300, 100),
    N("l3", "Нет оптимизации,\nкаждую строку надо разобрать в объект", 920, 220, "r", 340, 100),
], edges=[E("d1", "d2"), E("d2", "d3"), E("l1", "l2"), E("l2", "l3")])

if __name__ == "__main__":
    run_all(D)
