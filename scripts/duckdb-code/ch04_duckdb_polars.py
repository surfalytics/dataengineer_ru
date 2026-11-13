"""Глава 4. DuckDB запрашивает Polars DataFrame по имени переменной и отдаёт результат обратно."""
import duckdb
import polars as pl

cars = pl.DataFrame({
    "model":      ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox", "Golf", "Hawk"],
    "year":       [1982, 1966, 1994, 1964, 1975, 2000, 1974, 2007],
    "engine_min": [2.5, 1.8, 2.0, 2.3, 2.7, 1.5, 1.0, 1.4],
    "engine_max": [3.5, 2.0, 2.5, 5.0, 5.0, 2.5, 2.0, 2.0],
    "company":    ["A", "A", "A", "B", "B", "B", "C", "C"],
})

# DuckDB находит переменную cars по имени. Нужен pyarrow.
rel = duckdb.sql("SELECT * FROM cars")
print("duckdb.sql вернул:", type(rel).__name__)
print("в Polars:", type(rel.pl()).__name__)

print(rel.describe().pl().select("aggr", "year", "engine_max"))

# Методы DuckDBPyRelation
print(rel.order("year DESC").limit(3).pl().select("model", "year"))
print(rel.aggregate("min(year) AS first_year").fetchall())

# Когда SQL проще: сортировка и группировка
print(duckdb.sql("SELECT company, count(model) AS n FROM cars GROUP BY company ORDER BY company").pl())

# То же в Polars
print(cars.group_by("company", maintain_order=True).agg(pl.col("model").count().alias("n")))
