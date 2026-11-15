"""Глава 3: DuckDB выполняет SQL прямо над pandas DataFrame (примеры 3-52 ... 3-58 книги)."""
import duckdb
import pandas as pd

# Маленький DataFrame: SQL видит его по имени переменной
mydf = pd.DataFrame({"a": [1, 2, 3]})
print(duckdb.query("SELECT SUM(a) AS total FROM mydf").to_df())

# Продажи книг (наши данные)
sales_df = pd.DataFrame({
    "title": ["SQL для начинающих", "Python для анализа", "dbt на практике", "Основы Spark"],
    "publisher": ["Север", "Север", "Север", "Юг"],
    "price": [30.0, 45.0, 50.0, 40.0],
    "units_sold": [1000, 800, 1200, 600],
})

con = duckdb.connect()            # база в памяти процесса
con.register("sales", sales_df)   # DataFrame становится таблицей sales

query = """
SELECT SUM(price * units_sold) AS total_revenue
FROM sales
WHERE publisher = 'Север'          -- строки в SQL только в одинарных кавычках
"""
total = con.execute(query).fetchall()[0][0]   # одно число
print("total_revenue:", total)

df_total = con.execute(query).df()            # тот же результат как DataFrame
print(type(df_total).__name__, df_total.shape)
