"""Глава 1. Быстрый взгляд на DuckDB: база, таблица, вставка, запросы, агрегаты, JOIN."""
import os
import tempfile

import duckdb

# 1. База в файле. Данные переживут закрытие соединения.
path = os.path.join(tempfile.mkdtemp(), "my_duckdb_database.db")
conn = duckdb.connect(path)

conn.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        age INTEGER,
        department VARCHAR
    )
""")
print("Таблицы в базе:")
print(conn.execute("SHOW TABLES").df().to_string(index=False))

# 2. Вставка строк (четыре строки)
conn.execute("""
    INSERT INTO employees VALUES
        (1, 'Alice',   30, 'HR'),
        (2, 'Bob',     35, 'Engineering'),
        (3, 'Charlie', 28, 'Marketing'),
        (4, 'David',   40, 'Engineering')
""")
print("\nВсе сотрудники:")
print(conn.execute("SELECT * FROM employees").df().to_string(index=False))

# 3. Агрегаты
print("\nСколько людей в каждом отделе:")
print(conn.execute("""
    SELECT department, COUNT(*) AS employee_count
    FROM employees
    GROUP BY department
    ORDER BY department
""").df().to_string(index=False))

print("\nСредний возраст по компании:")
print(conn.execute("SELECT AVG(age) AS average_age FROM employees").df().to_string(index=False))

print("\nСамый старший в каждом отделе (возраст):")
print(conn.execute("""
    SELECT department, MAX(age) AS oldest_age
    FROM employees
    GROUP BY department
    ORDER BY department
""").df().to_string(index=False))

print("\nСредний возраст по отделам:")
print(conn.execute("""
    SELECT department, AVG(age) AS average_age
    FROM employees
    GROUP BY department
    ORDER BY department
""").df().to_string(index=False))

# 4. Файл переживает перезапуск, база в памяти - нет
conn.close()
conn = duckdb.connect(path)
n = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
print(f"\nПосле переоткрытия файла в таблице {n} строки.")
conn.close()

mem = duckdb.connect(":memory:")
mem.execute("CREATE TABLE t (x INTEGER)")
mem.close()
mem = duckdb.connect(":memory:")
print("Таблиц в новой базе в памяти:", len(mem.execute("SHOW TABLES").fetchall()))

# 5. JOIN двух таблиц
conn = duckdb.connect()
conn.execute("CREATE TABLE orders (order_id INTEGER, customer_id INTEGER, amount FLOAT)")
conn.execute("INSERT INTO orders VALUES (1, 1, 100.0), (2, 2, 200.0), (3, 1, 150.0)")
conn.execute("CREATE TABLE customers (customer_id INTEGER, name VARCHAR)")
conn.execute("INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob')")

print("\nJOIN: суммы по каждому заказу:")
print(conn.execute("""
    SELECT customers.customer_id, customers.name, orders.amount
    FROM orders
    JOIN customers ON orders.customer_id = customers.customer_id
    ORDER BY customers.customer_id, orders.order_id
""").df().to_string(index=False))

print("\nJOIN + SUM: всего потратил каждый клиент:")
print(conn.execute("""
    SELECT customers.customer_id, customers.name, SUM(orders.amount) AS total_spent
    FROM orders
    JOIN customers ON orders.customer_id = customers.customer_id
    GROUP BY customers.customer_id, customers.name
    ORDER BY customers.customer_id
""").df().to_string(index=False))
