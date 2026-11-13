"""Глава 1. Скорость и память: pandas против DuckDB на одном CSV.
Каждый способ идёт в отдельном процессе, поэтому память не смешивается.
Числа зависят от машины: они меняются от запуска к запуску."""
import os
import subprocess
import sys
import tempfile
import time

import duckdb
import psutil

ROWS = 5_800_000  # столько строк в flights.csv из книги
AIRLINES = ["AA", "AS", "B6", "DL", "EV", "F9", "HA", "MQ", "NK", "OO", "UA", "US", "VX", "WN"]


def mb():
    return psutil.Process().memory_info().rss / 1024 ** 2


def child(mode, path):
    before = mb()
    t0 = time.perf_counter()
    if mode == "pandas":
        import pandas as pd
        df = pd.read_csv(path)
        res = df.groupby("AIRLINE")["ARRIVAL_DELAY"].mean().reset_index()
    else:
        res = duckdb.sql(f"""
            SELECT AIRLINE, AVG(ARRIVAL_DELAY) AS MEAN_ARRIVAL_DELAY
            FROM read_csv_auto('{path}')
            GROUP BY AIRLINE ORDER BY AIRLINE
        """).df()
    dt = time.perf_counter() - t0
    after = mb()
    print(f"{mode:7s} время: {dt:5.2f} с   память до: {before:7.1f} МБ   после: {after:7.1f} МБ   "
          f"выросла на: {after - before:7.1f} МБ   групп: {len(res)}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        child(sys.argv[1], sys.argv[2])
        sys.exit()
    path = os.path.join(tempfile.mkdtemp(), "flights_big.csv")
    air = "[" + ",".join(f"'{a}'" for a in AIRLINES) + "]"
    duckdb.sql(f"""
        COPY (
            SELECT 2015 AS YEAR, 1 + (i % 12) AS MONTH, 1 + (i % 28) AS DAY,
                   {air}[1 + (i % 14)] AS AIRLINE,
                   100 + CAST(hash(i * 3) % 7000 AS INTEGER) AS FLIGHT_NUMBER,
                   'N' || (hash(i * 5) % 99999) AS TAIL_NUMBER,
                   (hash(i * 11) % 300) AS ORIGIN_CODE,
                   (hash(i * 13) % 300) AS DEST_CODE,
                   (hash(i * 17) % 1400) AS DEPARTURE_TIME,
                   CAST(hash(i * 19) % 120 AS INTEGER) - 10 AS DEPARTURE_DELAY,
                   CASE WHEN hash(i) % 60 = 0 THEN NULL ELSE CAST(hash(i * 7) % 120 AS INTEGER) - 20 END AS ARRIVAL_DELAY,
                   50 + CAST(hash(i * 23) % 2500 AS INTEGER) AS DISTANCE
            FROM range({ROWS}) t(i)
        ) TO '{path}' (HEADER, DELIMITER ',')
    """)
    print(f"Файл: {ROWS:,} строк, {os.path.getsize(path) / 1024 ** 2:.0f} МБ".replace(",", " "), flush=True)
    for mode in ("pandas", "duckdb"):
        subprocess.run([sys.executable, "-I", __file__, mode, path], check=True)
