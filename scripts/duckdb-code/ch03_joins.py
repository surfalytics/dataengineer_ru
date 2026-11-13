"""Глава 3. LEFT и INNER JOIN на схеме магазина: товар без заказов и порядок таблиц."""
import duckdb

con = duckdb.connect()
con.execute("""
CREATE TABLE products (product_id INTEGER PRIMARY KEY, title VARCHAR NOT NULL, price DECIMAL(10, 2));
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL,
                     FOREIGN KEY (product_id) REFERENCES products(product_id));
INSERT INTO products VALUES (1, 'Ноутбук', 900.00), (2, 'Мышь', 20.00), (3, 'Книга SQL', 35.00), (4, 'Лампа', 40.00);
INSERT INTO orders VALUES (1, 1), (2, 2), (3, 3), (4, 3), (5, 1), (6, 3);
""")


def show(title, sql):
    print(title)
    for row in con.execute(sql).fetchall():
        print("  ", row)


show("INNER JOIN: только товары с заказами", """
    SELECT p.title, count(o.order_id) AS orders_cnt
    FROM products p INNER JOIN orders o ON o.product_id = p.product_id
    GROUP BY p.title ORDER BY p.title""")
show("LEFT JOIN: все товары, у лампы заказов 0", """
    SELECT p.title, count(o.order_id) AS orders_cnt
    FROM products p LEFT JOIN orders o ON o.product_id = p.product_id
    GROUP BY p.title ORDER BY p.title""")
show("Таблицы в другом порядке: orders LEFT JOIN products (лампы нет)", """
    SELECT p.title, count(*) AS orders_cnt
    FROM orders o LEFT JOIN products p ON o.product_id = p.product_id
    GROUP BY p.title ORDER BY p.title""")
