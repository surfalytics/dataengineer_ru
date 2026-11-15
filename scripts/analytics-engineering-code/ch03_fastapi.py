"""Глава 3: SQL считает, Python отдаёт результат как API (пример 3-50 книги).
Вместо запуска сервера вызываем endpoint через TestClient."""
import duckdb
from fastapi import FastAPI
from fastapi.testclient import TestClient

con = duckdb.connect()
con.execute("""
CREATE TABLE sales AS
SELECT * FROM (VALUES
    ('SQL для начинающих', 'Север', 1000),
    ('Python для анализа', 'Север', 800),
    ('dbt на практике',    'Север', 1200),
    ('Основы Spark',       'Юг',    600)
) AS t(title, publisher, units_sold)
""")

app = FastAPI()

@app.get("/top_books")
def get_top_books():
    rows = con.execute("""
        SELECT title, units_sold
        FROM sales
        WHERE publisher = 'Север'
        ORDER BY units_sold DESC
        LIMIT 2
    """).fetchall()
    return {"top_books": [{"title": t, "units_sold": u} for t, u in rows]}

client = TestClient(app)
r = client.get("/top_books")
print(r.status_code)
print(r.json())
