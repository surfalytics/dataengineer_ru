-- DuckDB. Все таблицы примера временные.
CREATE TEMP TABLE stg_orders (order_id INTEGER, order_date DATE);
INSERT INTO stg_orders VALUES (1, CURRENT_DATE), (2, CURRENT_DATE - 1);
CREATE TEMP TABLE fact_orders AS SELECT * FROM stg_orders WHERE false;

INSERT INTO fact_orders SELECT * FROM stg_orders WHERE order_date >= CURRENT_DATE - 1;
INSERT INTO fact_orders SELECT * FROM stg_orders WHERE order_date >= CURRENT_DATE - 1;
SELECT count(*) AS after_append_twice FROM fact_orders;

BEGIN TRANSACTION;
DELETE FROM fact_orders WHERE order_date >= CURRENT_DATE - 1;
INSERT INTO fact_orders SELECT * FROM stg_orders WHERE order_date >= CURRENT_DATE - 1;
COMMIT;
BEGIN TRANSACTION;
DELETE FROM fact_orders WHERE order_date >= CURRENT_DATE - 1;
INSERT INTO fact_orders SELECT * FROM stg_orders WHERE order_date >= CURRENT_DATE - 1;
COMMIT;
SELECT count(*) AS after_replace_twice FROM fact_orders;
