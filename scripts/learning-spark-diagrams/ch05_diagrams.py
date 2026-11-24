#!/usr/bin/env python3
"""Chapter 5 (Spark SQL and DataFrames: External Data Sources) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own: how clients and external sources connect to Spark SQL (text of the chapter, Figures 5-2..5-8 are Tableau screenshots)
D["ch05-sql-access"] = dict(items=[
    T("Клиенты", 0, -50, 22, "#1971c2"),
    T("Spark", 480, -50, 22, "#1971c2"),
    T("Внешние источники", 1180, -50, 22, "#0c8599"),
    N("bee", "Beeline\n(консоль)", 0, 0, "n", 260, 100),
    N("tab", "Tableau, Power BI\n(BI-инструменты)", 0, 160, "n", 260, 100),
    N("cli", "spark-sql\n(консоль Spark)", 0, 420, "n", 260, 100),
    N("sts", "Thrift JDBC/ODBC\nserver", 480, 80, "y", 280, 120),
    N("sql", "Spark SQL\nSparkSession\nDataFrame, UDF", 480, 340, "p", 280, 180),
    N("jdbc", "JDBC: PostgreSQL,\nMySQL, MS SQL Server", 1180, 0, "db", 300, 110),
    N("cos", "Azure Cosmos DB", 1180, 190, "db", 300, 100),
    N("oth", "Cassandra, Snowflake,\nMongoDB", 1180, 370, "db", 300, 110),
], edges=[E("bee", "sts", "JDBC"), E("tab", "sts", "ODBC"), E("sts", "sql"),
          E("cli", "sql", "напрямую"),
          E("sql", "jdbc", "connector"), E("sql", "cos", "connector"), E("sql", "oth", "connector")])

# Own: how JDBC partitioned read splits the table into parallel queries
D["ch05-jdbc-partitions"] = dict(items=[
    T("numPartitions = 4, lowerBound = 2000, upperBound = 4000: шаг (stride) равен 500", 0, -50, 20, "#495057"),
    N("db", "Таблица orders\nво внешней БД\n\nпартиционная колонка\norder_id", 0, 120, "db", 300, 280),
    N("t1", "task 1: order_id < 2500", 520, 0, "g", 360, 90),
    N("t2", "task 2: от 2500 до 3000", 520, 140, "g", 360, 90),
    N("t3", "task 3: от 3000 до 3500", 520, 280, "g", 360, 90),
    N("t4", "task 4: order_id >= 3500", 520, 420, "g", 360, 90),
    N("p1", "partition 1", 1100, 0, "p", 240, 90),
    N("p2", "partition 2", 1100, 140, "p", 240, 90),
    N("p3", "partition 3", 1100, 280, "p", 240, 90),
    N("p4", "partition 4", 1100, 420, "p", 240, 90),
    T("4 запроса идут параллельно, по одному JDBC-соединению на запрос", 0, 560, 20, "#e03131"),
], edges=[E("db", "t1"), E("db", "t2"), E("db", "t3"), E("db", "t4"),
          E("t1", "p1"), E("t2", "p2"), E("t3", "p3"), E("t4", "p4")])

# Own: row-by-row Python UDF vs vectorized pandas UDF
D["ch05-pandas-udf"] = dict(items=[
    T("Обычная Python UDF: данные идут по одной строке", 0, -50, 22, "#e03131"),
    N("a1", "JVM\n(строки Spark)", 0, 0, "p", 260, 100),
    N("a2", "pickle:\nсериализация\nкаждой строки", 440, 0, "r", 280, 100),
    N("a3", "Python worker\nфункция на\nодном значении", 860, 0, "y", 280, 100),
    T("pandas UDF: данные идут пачками в формате Arrow", 0, 190, 22, "#2f9e44"),
    N("b1", "JVM\n(строки Spark)", 0, 240, "p", 260, 100),
    N("b2", "Arrow:\nколоночная пачка\nбез pickle", 440, 240, "g", 280, 100),
    N("b3", "Python worker\nфункция на\npandas.Series", 860, 240, "y", 280, 100),
], edges=[E("a1", "a2", "медленно"), E("a2", "a3"),
          E("b1", "b2", "быстро"), E("b2", "b3")])

if __name__ == "__main__":
    run_all(D)
