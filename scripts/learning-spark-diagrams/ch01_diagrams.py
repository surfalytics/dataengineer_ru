#!/usr/bin/env python3
"""Chapter 1 (Introduction to Apache Spark) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 1-1 + own: MapReduce writes to disk between steps, Spark keeps intermediate results in memory
D["ch01-mr-vs-spark"] = dict(items=[
    T("Hadoop MapReduce: между шагами всё пишется на диск", 0, -50, 22, "#e03131"),
    N("m1", "Данные\nна диске", 0, 0, "db", 220, 100),
    N("m2", "map", 280, 0, "p", 220, 100),
    N("m3", "Промежуточный\nрезультат\nна диске", 560, 0, "r", 220, 100),
    N("m4", "reduce", 840, 0, "p", 220, 100),
    N("m5", "Результат\nна диске", 1120, 0, "db", 220, 100),
    T("Spark: промежуточные результаты остаются в памяти", 0, 190, 22, "#2f9e44"),
    N("s1", "Данные\nна диске", 0, 240, "db", 220, 100),
    N("s2", "map", 280, 240, "p", 220, 100),
    N("s3", "Промежуточный\nрезультат\nв памяти", 560, 240, "g", 220, 100),
    N("s4", "reduce", 840, 240, "p", 220, 100),
    N("s5", "Результат", 1120, 240, "g", 220, 100),
], edges=[E("m1", "m2"), E("m2", "m3"), E("m3", "m4"), E("m4", "m5"),
          E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "s5")])

# Fig 1-3: components as a unified stack
D["ch01-stack"] = dict(items=[
    N("lang", "Языки: Scala, Java, Python, SQL, R", 0, 0, "n", 1200, 90),
    N("sql", "Spark SQL\nструктурированные данные", 0, 190, "p", 270, 110),
    N("st", "Structured Streaming\nпотоки в реальном времени", 310, 190, "pu", 270, 110),
    N("ml", "MLlib\nмашинное обучение", 620, 190, "g", 270, 110),
    N("gx", "GraphX\nграфы", 930, 190, "y", 270, 110),
    N("core", "Ядро Spark: DAG, планировщик, отказоустойчивость", 0, 400, "q", 1200, 100),
    N("src", "Источники: HDFS, S3, Kafka, Cassandra, RDBMS и другие", 0, 600, "db", 1200, 90),
], edges=[E("lang", "sql"), E("lang", "st"), E("lang", "ml"), E("lang", "gx"),
          E("sql", "core"), E("st", "core"), E("ml", "core"), E("gx", "core"),
          E("core", "src")])

# Fig 1-4: driver, cluster manager, executors
D["ch01-architecture"] = dict(items=[
    N("drv", "Driver\nSparkSession\nстроит DAG, раздаёт tasks", 0, 250, "p", 320, 130),
    N("cm", "Cluster manager\nвыдаёт CPU и память", 480, 0, "y", 320, 110),
    N("e1", "Executor 1\nвыполняет tasks\nхранит данные в памяти", 960, 130, "g", 340, 120),
    N("e2", "Executor 2\nвыполняет tasks\nхранит данные в памяти", 960, 310, "g", 340, 120),
    N("e3", "Executor 3\nвыполняет tasks\nхранит данные в памяти", 960, 490, "g", 340, 120),
    T("Узлы кластера (worker nodes)", 960, 90, 18, "#2f9e44"),
], edges=[E("drv", "cm", "1. ресурсы"), E("cm", "e1", "2. запуск"),
          E("drv", "e1", "3. tasks"), E("drv", "e2", "3. tasks"), E("drv", "e3", "3. tasks")])

# Fig 1-5, 1-6: partitions, one task per core
D["ch01-partitions"] = dict(items=[
    T("Данные в HDFS или облачном хранилище, разрезанные на partition", 0, -50, 20, "#0c8599"),
    N("p1", "partition 1", 0, 0, "db", 270, 90),
    N("p2", "partition 2", 310, 0, "db", 270, 90),
    N("p3", "partition 3", 620, 0, "db", 270, 90),
    N("p4", "partition 4", 930, 0, "db", 270, 90),
    Z("Executor A", -20, 220, 620, 230),
    Z("Executor B", 600, 220, 620, 230),
    N("c1", "Ядро 1\ntask 1", 0, 300, "g", 270, 100),
    N("c2", "Ядро 2\ntask 2", 310, 300, "g", 270, 100),
    N("c3", "Ядро 1\ntask 3", 620, 300, "g", 270, 100),
    N("c4", "Ядро 2\ntask 4", 930, 300, "g", 270, 100),
    T("Одно ядро берёт одну partition: tasks работают параллельно", 0, 480, 20, "#495057"),
], edges=[E("p1", "c1"), E("p2", "c2"), E("p3", "c3"), E("p4", "c4")])

if __name__ == "__main__":
    run_all(D)
