#!/usr/bin/env python3
"""Chapter 2 (Downloading Spark and Getting Started) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own: the three steps of the chapter and the first application
D["ch02-steps"] = dict(items=[
    N("s1", "Шаг 1\nУстановить Spark\n(архив или pip, Docker)", 0, 0, "y", 290, 120),
    N("s2", "Шаг 2\nЗапустить shell\npyspark, spark-sql", 390, 0, "p", 290, 120),
    N("s3", "Шаг 3\nПонять понятия\njob, stage, task", 780, 0, "g", 290, 120),
    N("s4", "Первое приложение\nspark-submit\nmnmcount.py", 1170, 0, "q", 290, 120),
    N("ui", "Spark UI\nlocalhost:4040", 780, 260, "db", 290, 100),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s3", "ui", "смотрим job и stage")])

# Fig 2-3, 2-4, 2-5: application -> job -> stages -> tasks
D["ch02-job-stage-task"] = dict(items=[
    N("app", "Application\ndriver + SparkSession", 0, 130, "p", 280, 110),
    N("job", "Job\nодин action", 380, 130, "y", 240, 110),
    N("st1", "Stage 1\nдо shuffle", 720, 0, "g", 240, 110),
    N("st2", "Stage 2\nпосле shuffle", 720, 280, "g", 240, 110),
    N("t1", "tasks этапа 1\nодна partition на task", 1080, 0, "q", 300, 110),
    N("t2", "tasks этапа 2\nодна partition на task", 1080, 280, "q", 300, 110),
    T("Один task работает на одном ядре executor", 1080, 150, 18, "#495057"),
], edges=[E("app", "job"), E("job", "st1"), E("job", "st2"),
          E("st1", "st2", "shuffle"), E("st1", "t1"), E("st2", "t2")])

# Fig 2-6: lazy transformations and eager action
D["ch02-lazy"] = dict(items=[
    N("f", "Файл", 0, 0, "db", 170, 100),
    N("t1", "read()\nT", 270, 0, "p", 190, 100),
    N("t2", "filter()\nT", 560, 0, "p", 190, 100),
    N("t3", "select()\nT", 850, 0, "p", 190, 100),
    N("a", "count()\nA: запуск", 1140, 0, "r", 220, 100),
    N("res", "Результат", 1140, 220, "g", 220, 100),
    T("T записывается в lineage и не выполняется", 270, 140, 18, "#1971c2"),
], edges=[E("f", "t1"), E("t1", "t2"), E("t2", "t3"), E("t3", "a"), E("a", "res")])

# Fig 2-7: narrow vs wide
D["ch02-narrow-wide"] = dict(items=[
    T("Narrow: filter, select", 0, -60, 22, "#2f9e44"),
    N("a1", "partition 1", 0, 0, "db", 200, 80),
    N("a2", "partition 2", 0, 160, "db", 200, 80),
    N("b1", "partition 1'", 330, 0, "g", 200, 80),
    N("b2", "partition 2'", 330, 160, "g", 200, 80),
    T("Wide: groupBy, orderBy, join", 760, -110, 22, "#e03131"),
    N("c1", "partition 1", 760, -40, "db", 200, 80),
    N("c2", "partition 2", 760, 100, "db", 200, 80),
    N("c3", "partition 3", 760, 240, "db", 200, 80),
    N("d1", "partition A\nключи a-m", 1260, 20, "r", 220, 90),
    N("d2", "partition B\nключи n-z", 1260, 180, "r", 220, 90),
], edges=[E("a1", "b1"), E("a2", "b2"),
          E("c1", "d1"), E("c1", "d2"), E("c2", "d1"), E("c2", "d2"), E("c3", "d1"), E("c3", "d2")])

if __name__ == "__main__":
    run_all(D)
