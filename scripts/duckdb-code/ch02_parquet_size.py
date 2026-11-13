import os
import tempfile

import duckdb

tmp = tempfile.mkdtemp()
con = duckdb.connect()
con.sql("""
    CREATE TABLE flights AS
    SELECT i AS flight_id,
           ['SU','S7','DP','U6'][1 + i % 4] AS carrier,
           CAST(hash(i) % 120 AS INTEGER) - 20 AS arr_delay,
           'route ' || (i % 50) AS route
    FROM range(1000000) t(i)
""")
con.sql(f"COPY flights TO '{tmp}/flights.csv' (HEADER)")
con.sql(f"COPY flights TO '{tmp}/flights.parquet' (FORMAT PARQUET)")
print("CSV, МБ:    ", round(os.path.getsize(f"{tmp}/flights.csv") / 1e6, 1))
print("Parquet, МБ:", round(os.path.getsize(f"{tmp}/flights.parquet") / 1e6, 1))
# схема лежит внутри файла
print(con.sql(f"SELECT name, type FROM parquet_schema('{tmp}/flights.parquet') WHERE name <> 'duckdb_schema'").fetchall())
