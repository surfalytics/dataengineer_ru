"""Глава 3: SQL над Polars DataFrame: через DuckDB и через pl.SQLContext (примеры 3-61 ... 3-66)."""
import duckdb
import polars as pl

df = pl.DataFrame({
    "title": ["SQL для начинающих", "Python для анализа", "dbt на практике", "Основы Spark"],
    "author": ["Иванова", "Петров", "Сидорова", "Козлов"],
    "price": [30.0, 45.0, 50.0, 40.0],
    "units_sold": [1000, 800, 1200, 600],
})

# 1. API самого Polars: сортировка по убыванию (в книге reverse=True, сейчас descending=True)
print(df.sort("units_sold", descending=True).select(["title", "units_sold"]).head(2))

# 2. DuckDB читает Polars DataFrame и отдаёт результат обратно в Polars
con = duckdb.connect()
con.register("books", df)
print(con.execute("SELECT title, units_sold FROM books WHERE units_sold > 700 ORDER BY units_sold").pl())
con.close()

# 3. Встроенный SQL в Polars: контекст, регистрация, запрос
ctx = pl.SQLContext()
ctx.register("books", df)
res = ctx.execute("SELECT author, price FROM books WHERE price >= 45 ORDER BY price").collect()
print(res)
