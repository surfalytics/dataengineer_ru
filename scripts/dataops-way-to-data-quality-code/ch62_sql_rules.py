"""Проверки доли пропусков и уникальности из главы 62 на четырёх строках DuckDB."""
import duckdb

with duckdb.connect() as connection:
    connection.execute("""
        CREATE TEMP TABLE payments AS
        SELECT * FROM (VALUES (1, 15), (1, 20), (2, NULL), (3, 12)) AS t(vendor_id, amount)
    """)
    null_rate, passes = connection.execute("""
        SELECT avg(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS rate,
               avg(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) < 0.20 AS passes
        FROM payments
    """).fetchone()
    violations = connection.execute("""
        SELECT count(*) FROM (
            SELECT count(*) OVER (PARTITION BY vendor_id) AS occurrences FROM payments
        ) AS measured WHERE occurrences > 1
    """).fetchone()[0]
    print(f"Доля пропусков: {null_rate:.2f}; проверка: {passes}")
    print(f"Строк с повторяющимся идентификатором: {violations}")
