"""Проверить пять ветвей заказов и смену CASE на примере из главы 30 с SQLite."""
import sqlite3


def main():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE stg_orders(order_id, customer_id, email, order_ts, product_id,
                                region_code, currency_code, order_total, status, updated_at);
        INSERT INTO stg_orders VALUES
            (1, 2, 'buyer@example.com', '2026-07-26', 3,
             'APAC', 'USD', 4182900, 'settled', '2026-07-27 04:15');
        CREATE TABLE products(product_id, sku, category);
        INSERT INTO products VALUES (3, 'sku-3', 'books');
        CREATE TABLE order_lines(order_id, item_id, qty);
        INSERT INTO order_lines VALUES (1, 3, 2);
        CREATE TABLE fx_rates(currency_code, rate_to_usd);
        INSERT INTO fx_rates VALUES ('USD', 1);
        CREATE TABLE revenue_history(daily_revenue NUMERIC);
        INSERT INTO revenue_history VALUES (41829), (41829);

        CREATE VIEW dim_customer AS SELECT customer_id, email, min(order_ts) AS signup_date
          FROM stg_orders GROUP BY customer_id, email;
        CREATE VIEW dim_product AS SELECT p.product_id, p.sku, p.category, count(o.order_id) AS orders
          FROM products p LEFT JOIN stg_orders o USING (product_id) GROUP BY p.product_id, p.sku, p.category;
        CREATE VIEW fct_order_items AS SELECT order_id, item_id, qty FROM stg_orders JOIN order_lines USING (order_id);
        CREATE VIEW fct_order_status AS SELECT order_id, status, updated_at FROM stg_orders;
        CREATE VIEW fct_daily_revenue AS SELECT order_ts, sum(order_total * rate_to_usd) AS order_total
          FROM stg_orders JOIN fx_rates USING (currency_code) WHERE status <> 'cancelled' GROUP BY order_ts;
    """)
    # Контрольный исторический объём клиентов в этом примере равен одной строке.
    checks = (
        "SELECT count(*) NOT BETWEEN 0.8 AND 1.2 FROM dim_customer",
        "SELECT count(*) FROM dim_product WHERE product_id NOT IN (SELECT product_id FROM products)",
        "SELECT count(*) FROM fct_order_items WHERE qty NOT BETWEEN 1 AND 500",
        "SELECT max(updated_at) < datetime('2026-07-27 06:00', '-6 hours') FROM fct_order_status",
    )
    passed = sum(db.execute(sql).fetchone()[0] == 0 for sql in checks)
    failure = db.execute("""
        SELECT SUM(order_total) FROM fct_daily_revenue
        HAVING SUM(order_total) > 3 * (SELECT AVG(daily_revenue) FROM revenue_history)
    """).fetchone()
    print(f"Проверок прошло: {passed}; не прошло: {int(failure is not None)}")
    print(f"Выручка выше порога: {failure[0]}")
    channels = db.execute("""
        SELECT CASE WHEN region_code IN ('NA','EMEA') THEN 'direct' ELSE 'partner' END,
               CASE WHEN region_code IN ('NA','EMEA','APAC') THEN 'direct' ELSE 'partner' END
        FROM stg_orders
    """).fetchone()
    print(f"Канал для APAC: {channels[0]} -> {channels[1]}")
    db.close()


if __name__ == "__main__":
    main()
