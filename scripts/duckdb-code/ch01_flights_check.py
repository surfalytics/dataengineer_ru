"""Глава 1. Тот же запрос в pandas и в DuckDB даёт тот же ответ.
Данные: 1 млн синтетических рейсов. Файл строится в SQL без случайности (hash), поэтому вывод одинаков при каждом запуске."""
import os
import tempfile

import duckdb
import pandas as pd

csv_path = os.path.join(tempfile.mkdtemp(), "flights_demo.csv")
duckdb.sql("""
    COPY (
        SELECT
            2015 AS YEAR,
            1 + (i % 12) AS MONTH,
            ['AA','DL','UA','WN','B6'][1 + (i % 5)] AS AIRLINE,
            CASE WHEN hash(i) % 50 = 0 THEN NULL            -- отменённый рейс: задержки нет
                 ELSE CAST(hash(i * 7) % 90 AS INTEGER) - 15 + (i % 5) * 2 -- задержка в минутах, может быть < 0
            END AS ARRIVAL_DELAY
        FROM range(1000000) t(i)
    ) TO '{p}' (HEADER, DELIMITER ',')
""".format(p=csv_path))

# pandas: грузим весь файл, потом считаем
df = pd.read_csv(csv_path)
pandas_res = (df.groupby("AIRLINE")["ARRIVAL_DELAY"].mean().reset_index()
                .sort_values("AIRLINE").reset_index(drop=True))

# DuckDB: читаем файл прямо в запросе
duck_res = duckdb.sql(f"""
    SELECT AIRLINE, AVG(ARRIVAL_DELAY) AS MEAN_ARRIVAL_DELAY
    FROM read_csv_auto('{csv_path}')
    GROUP BY AIRLINE
    ORDER BY AIRLINE
""").df()

print("Строк в файле:", len(df))
print("Рейсов без задержки (NULL):", int(df["ARRIVAL_DELAY"].isna().sum()))
print()
print(duck_res.round(3).to_string(index=False))
same = all(abs(a - b) < 1e-9 for a, b in zip(pandas_res["ARRIVAL_DELAY"], duck_res["MEAN_ARRIVAL_DELAY"]))
print("\npandas и DuckDB дали одинаковые средние:", same)
