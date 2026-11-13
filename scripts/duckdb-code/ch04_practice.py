"""Глава 4. Практика: решения трёх заданий страницы."""
import duckdb
import polars as pl

cars = pl.DataFrame({
    "model":   ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox"],
    "year":    [1982, 1994, 2000, 1975, 2007, 1966],
    "company": ["A", "A", "B", "B", "C", "C"],
    "engine":  [2.5, 2.0, 1.5, 2.7, 1.4, 1.8],
})

# Задание 1: Polars, компания A и двигатель больше 2.0
print(cars.filter((pl.col("company") == "A") & (pl.col("engine") > 2.0)).select("model").to_series().to_list())

# Задание 2: SQL по DataFrame, самый ранний год у компании
print(duckdb.sql("SELECT company, min(year) AS first_year FROM cars GROUP BY company ORDER BY company").fetchall())

# Задание 3: методы DuckDBPyRelation
rel = duckdb.sql("SELECT * FROM cars")
print(rel.filter("year > 1980").project("model, year").order("year").limit(2).fetchall())
