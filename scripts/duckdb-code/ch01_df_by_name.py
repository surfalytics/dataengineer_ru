import duckdb
import pandas as pd

employees = pd.DataFrame({"employee_id": [1, 2, 3, 4],
                          "department": ["HR", "Engineering", "Marketing", "Engineering"]})
sales = pd.DataFrame({"employee_id": [1, 2, 1, 3, 4], "sale_amount": [200, 500, 150, 300, 700]})

# employees и sales - это переменные Python. В SQL их видно по имени.
print(duckdb.sql("""
    SELECT e.department, SUM(s.sale_amount) AS total_sales
    FROM employees e LEFT JOIN sales s ON e.employee_id = s.employee_id
    GROUP BY e.department ORDER BY e.department
""").df().to_string(index=False))
