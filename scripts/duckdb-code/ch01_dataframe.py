"""Глава 1. DuckDB читает pandas DataFrame по имени переменной. Копировать данные не нужно."""
import duckdb
import pandas as pd

employees = pd.DataFrame({
    "employee_id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "David"],
    "age": [30, 35, 28, 40],
    "department": ["HR", "Engineering", "Marketing", "Engineering"],
})
sales = pd.DataFrame({
    "sale_id": [101, 102, 103, 104, 105],
    "employee_id": [1, 2, 1, 3, 4],
    "sale_amount": [200, 500, 150, 300, 700],
    "sale_date": ["2023-01-01", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-07"],
})

conn = duckdb.connect()

# В SQL просто пишем employees и sales. Это имена Python-переменных.
print("Итоги по отделам:")
print(conn.execute("""
    SELECT
        e.department,
        SUM(s.sale_amount)             AS total_sales,
        AVG(s.sale_amount)             AS avg_sale,
        COUNT(DISTINCT e.employee_id)  AS number_of_employees
    FROM employees e
    LEFT JOIN sales s ON e.employee_id = s.employee_id
    GROUP BY e.department
    ORDER BY e.department
""").df().to_string(index=False))

print("\nЛучшая продажа каждого сотрудника:")
print(conn.execute("""
    SELECT e.department, e.name AS employee, MAX(s.sale_amount) AS top_sale_amount
    FROM employees e
    LEFT JOIN sales s ON e.employee_id = s.employee_id
    GROUP BY e.department, e.name
    ORDER BY top_sale_amount DESC, e.name
""").df().to_string(index=False))

# Ловушка книги: AVG(sale_amount) - это средняя ПРОДАЖА, а не средняя на сотрудника.
print("\nСредняя продажа и средняя выручка на сотрудника (это разные числа):")
print(conn.execute("""
    SELECT
        e.department,
        AVG(s.sale_amount)                              AS avg_per_sale,
        SUM(s.sale_amount) / COUNT(DISTINCT e.employee_id) AS avg_per_employee
    FROM employees e
    LEFT JOIN sales s ON e.employee_id = s.employee_id
    GROUP BY e.department
    ORDER BY e.department
""").df().to_string(index=False))

# Результат запроса можно сразу вернуть в pandas
df = duckdb.sql("SELECT department, COUNT(*) AS n FROM employees GROUP BY department ORDER BY department").df()
print("\nТип результата:", type(df).__name__)
