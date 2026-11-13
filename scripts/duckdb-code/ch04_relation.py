"""Глава 4. Объект DuckDBPyRelation: table, insert, join, filter, aggregate, project, limit."""
import duckdb

conn = duckdb.connect()
conn.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name VARCHAR)")
conn.execute("CREATE TABLE products (product_id INTEGER PRIMARY KEY, product_name VARCHAR)")
conn.execute("CREATE TABLE sales (customer_id INTEGER, product_id INTEGER, qty INTEGER, PRIMARY KEY (customer_id, product_id))")

customers = conn.table("customers")
for row in ([1, "Alice"], [2, "Bob"], [3, "Charlie"]):
    customers.insert(row)
products = conn.table("products")
for row in ([10, "Paperclips"], [20, "Staple"], [30, "Notebook"]):
    products.insert(row)
sales = conn.table("sales")
for row in ([1, 20, 1], [1, 10, 2], [2, 30, 7], [3, 10, 3], [3, 20, 2]):
    sales.insert(row)

result = (
    customers.join(sales, condition="customer_id", how="inner")
    .join(products, condition="product_id", how="inner")
)
print("join:")
print(result.order("customer_id, product_id").pl())

print("filter customer_id = 1:")
print(result.filter("customer_id = 1").order("product_id").pl())

print("aggregate:")
print(result.aggregate('customer_id, max(name) AS name, sum(qty) AS total_qty', "customer_id").order("customer_id").pl())

print("project + limit(3, 2):")
print(result.project("name, qty, product_name").order("name, product_name").limit(3, 2).pl())
