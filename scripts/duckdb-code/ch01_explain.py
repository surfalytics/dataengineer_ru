"""Глава 1. Проверяем projection и filter pushdown: смотрим план запроса (EXPLAIN) над Parquet."""
import os
import tempfile

import duckdb

path = os.path.join(tempfile.mkdtemp(), "flights_demo.parquet")
duckdb.sql(f"""
    COPY (
        SELECT i AS id,
               ['AA','DL','UA'][1 + (i % 3)] AS airline,
               CAST(hash(i) % 100 AS INTEGER) - 20 AS arr_delay,
               'note ' || i AS note
        FROM range(300000) t(i)
    ) TO '{path}' (FORMAT parquet)
""")


def plan(sql):
    return duckdb.sql("EXPLAIN " + sql).fetchall()[0][1]


print("План 1: нужны два столбца и есть фильтр")
print(plan(f"SELECT airline, avg(arr_delay) FROM '{path}' WHERE arr_delay > 60 GROUP BY airline"))
print()
print("План 2: SELECT * (нужны все столбцы)")
print(plan(f"SELECT * FROM '{path}' WHERE arr_delay > 60"))
