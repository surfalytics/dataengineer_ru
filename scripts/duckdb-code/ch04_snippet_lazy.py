import polars as pl
import duckdb, tempfile, os

path = os.path.join(tempfile.mkdtemp(), "flights.csv")
duckdb.sql(f"""COPY (SELECT i AS id, 1 + i % 12 AS month,
    ['SFO','SEA','LAX','JFK','ORD'][1 + i % 5] AS origin, i % 97 AS delay,
    i % 31 AS c1, i % 37 AS c2, i % 41 AS c3
    FROM range(200000) t(i)) TO '{path}' (HEADER)""")

q = (
    pl.scan_csv(path)                          # ничего не читаем, получаем LazyFrame
    .select(["month", "origin"])
    .filter((pl.col("month") == 5) & (pl.col("origin") == "SFO"))
)
print(type(q).__name__)
for line in q.explain().replace(path, "flights.csv").splitlines():   # оптимизированный план
    print(line if not line.startswith("SELECTION") else "SELECTION: [условия фильтра]")  # Polars сам решает их порядок
print(q.collect().shape)                          # collect() запускает план
