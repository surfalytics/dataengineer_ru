"""Глава 4. Lazy evaluation: read_csv (eager) и scan_csv (lazy). CSV строим сами, без загрузок."""
import os
import tempfile

import duckdb
import polars as pl

path = os.path.join(tempfile.mkdtemp(), "flights.csv")
# 200 000 строк, 12 колонок. Без случайности: значения считаются из номера строки.
duckdb.sql(f"""
    COPY (
        SELECT
            i AS id,
            1 + i % 12 AS month,
            ['SFO','SEA','LAX','JFK','ORD'][1 + i % 5] AS origin_airport,
            ['SEA','SFO','DEN','BOS','ATL'][1 + (i // 5) % 5] AS destination_airport,
            i % 97 AS delay,
            i % 31 AS c1, i % 37 AS c2, i % 41 AS c3, i % 43 AS c4,
            i % 47 AS c5, i % 53 AS c6, i % 59 AS c7
        FROM range(200000) t(i)
    ) TO '{path}' (HEADER, DELIMITER ',')
""")

def show(plan):
    """Убираем путь файла. Polars сам решает порядок условий в SELECTION, поэтому текст условий не печатаем."""
    out = []
    for line in plan.replace(path, "flights.csv").splitlines():
        out.append("SELECTION: [условия фильтра, порядок выбирает Polars]" if line.startswith("SELECTION") else line)
    return "\n".join(out)


cond = (pl.col("month") == 5) & (pl.col("origin_airport") == "SFO") & (pl.col("destination_airport") == "SEA")

# Lazy: scan_csv ничего не читает, возвращает LazyFrame
q = (
    pl.scan_csv(path)
    .select(["month", "origin_airport", "destination_airport"])
    .filter(cond)
)
print("scan_csv вернул:", type(q).__name__)
print("--- план без оптимизации ---")
print(show(q.explain(optimized=False)))
print("--- план с оптимизацией ---")
print(show(q.explain(optimized=True)))
lazy_df = q.collect()
print("collect():", lazy_df.shape)

# Eager: read_csv читает всё сразу
eager = pl.read_csv(path)
print("read_csv вернул:", type(eager).__name__, eager.shape)

# Explicit lazy: read_csv(...).lazy() - файл уже прочитан, но следующие шаги оптимизируются
q2 = pl.read_csv(path).lazy().select(["month", "origin_airport", "destination_airport"]).filter(cond)
print("результаты совпадают:", q2.collect().equals(lazy_df))
