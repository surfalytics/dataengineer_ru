"""Глава 4. Polars: select, filter, SQLContext. Данные - наша таблица машин."""
import polars as pl

cars = pl.DataFrame({
    "model":      ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox", "Golf", "Hawk"],
    "year":       [1982, 1966, 1994, 1964, 1975, 2000, 1974, 2007],
    "engine_min": [2.5, 1.8, 2.0, 2.3, 2.7, 1.5, 1.0, 1.4],
    "engine_max": [3.5, 2.0, 2.5, 5.0, 5.0, 2.5, 2.0, 2.0],
    "awd":        [False, False, True, False, True, True, True, True],
    "company":    ["A", "A", "A", "B", "B", "B", "C", "C"],
})

print(cars)                       # индекса нет, под именем колонки виден тип
print(cars.dtypes)
print(cars.columns)

# select: выбрать колонки. Выражение pl.col(pl.String) берёт все строковые колонки.
print(cars.select(pl.col(pl.String)).columns)

# filter: выбрать строки. Каждое условие в скобках.
print(cars.filter((pl.col("company") == "A") & (pl.col("year") > 1970)).select("model", "year"))
print(cars.filter(pl.col("company").is_in(["A", "C"])).height)

# SQL внутри Polars
ctx = pl.SQLContext(cars=cars)
print(ctx.execute("""
    SELECT company, AVG(engine_min) AS avg_min, AVG(engine_max) AS avg_max
    FROM cars GROUP BY company ORDER BY company
""", eager=True))
