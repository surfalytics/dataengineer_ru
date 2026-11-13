import duckdb
import polars as pl

cars = pl.DataFrame({
    "model":   ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox", "Golf", "Hawk"],
    "year":    [1982, 1966, 1994, 1964, 1975, 2000, 1974, 2007],
    "company": ["A", "A", "A", "B", "B", "B", "C", "C"],
})

# cars - переменная Python. DuckDB находит её по имени (через Apache Arrow).
rel = duckdb.sql("""
    SELECT company, count(*) AS models, min(year) AS first_year
    FROM cars GROUP BY company ORDER BY company
""")
print(type(rel).__name__)   # DuckDBPyRelation
print(rel.pl())             # результат обратно в Polars
