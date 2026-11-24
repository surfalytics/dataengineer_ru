#!/usr/bin/env python3
"""Chapter 4 (Spark SQL and DataFrames: built-in data sources) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 4-1 (main): who talks to Spark SQL and which sources it reads
D["ch04-sql-connectors"] = dict(items=[
    T("Кто задаёт запросы", 0, -50, 22, "#1971c2"),
    N("app", "Spark-приложение\nspark.sql() и DataFrame", 0, 0, "p", 290, 100),
    N("cli", "Консоль\nspark-sql", 0, 160, "p", 290, 100),
    N("bi", "BI и клиенты\nTableau, Power BI (JDBC/ODBC)", 0, 320, "p", 290, 100),
    N("sql", "Spark SQL\nодин движок под SQL и DataFrame", 440, 160, "g", 330, 100),
    T("Откуда читает и куда пишет", 920, -50, 22, "#2f9e44"),
    N("files", "Файлы\nParquet, JSON, CSV, Avro, ORC", 920, 0, "y", 330, 100),
    N("tbl", "Таблицы и views\nметаданные в Catalog", 920, 160, "y", 330, 100),
    N("rdbms", "Реляционные БД\nMySQL, PostgreSQL по JDBC", 920, 320, "y", 330, 100),
], edges=[E("app", "sql"), E("cli", "sql"), E("bi", "sql"),
          E("sql", "files"), E("sql", "tbl"), E("sql", "rdbms")])

# Own: DROP TABLE for managed and unmanaged tables
D["ch04-managed-unmanaged"] = dict(items=[
    T("Managed table: Spark хранит и метаданные, и данные", 0, -50, 22, "#1971c2"),
    N("m0", "DROP TABLE\nmanaged_flights", 0, 60, "y", 260, 100),
    N("m1", "Метаданные в Catalog\nудалены", 420, 0, "r", 330, 100),
    N("m2", "Файлы данных в warehouse\nудалены", 420, 150, "r", 330, 100),
    T("Unmanaged table: Spark хранит только метаданные", 0, 330, 22, "#1971c2"),
    N("u0", "DROP TABLE\nunmanaged_flights", 0, 440, "y", 260, 100),
    N("u1", "Метаданные в Catalog\nудалены", 420, 380, "r", 330, 100),
    N("u2", "Ваши файлы данных\nостались на месте", 420, 530, "g", 330, 100),
], edges=[E("m0", "m1"), E("m0", "m2"), E("u0", "u1"), E("u0", "u2")])

# Own: DataFrameReader -> DataFrame -> DataFrameWriter
D["ch04-reader-writer"] = dict(items=[
    N("src", "Источник\nфайлы, таблицы, JDBC", 0, 0, "db", 260, 100),
    N("rd", "DataFrameReader\nspark.read", 400, 0, "p", 260, 100),
    N("df", "DataFrame\nна кластере", 800, 0, "g", 260, 100),
    N("wr", "DataFrameWriter\ndf.write", 1200, 0, "p", 260, 100),
    N("dst", "Приёмник\nфайлы, таблицы", 1600, 0, "db", 260, 100),
    T("format → option → schema → load", 330, 130, 18),
    T("format → option → mode → partitionBy → save", 1070, 130, 18),
], edges=[E("src", "rd"), E("rd", "df"), E("df", "wr"), E("wr", "dst")])

if __name__ == "__main__":
    run_all(D)
