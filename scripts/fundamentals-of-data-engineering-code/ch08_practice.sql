-- Chapter 8 practice. Run: duckdb -bail :memory: < ch08_practice.sql
SELECT count(*) AS строк_в_результате
FROM (SELECT 'this' AS k FROM range(5)) a
JOIN (SELECT 'this' AS k FROM range(10)) b USING (k);

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
  (1, 5, 'Анна',  '10001', DATE '2019-01-04', DATE '9999-01-01'),
  (2, 7, 'Борис', '84101', DATE '2020-05-04', DATE '2021-09-18'),
  (3, 7, 'Борис', '90210', DATE '2021-09-19', DATE '9999-01-01')
) AS t(customer_key, customer_id, name, zip, eff_start, eff_end);

CREATE TABLE fact_orders AS
SELECT * FROM (VALUES
  (100, 5, DATE '2022-03-01', 100.00),
  (101, 7, DATE '2022-03-01',  75.00),
  (102, 7, DATE '2022-03-01',  25.00),
  (103, 7, DATE '2021-06-10',  40.00),
  (104, 5, DATE '2022-03-02',  60.00)
) AS t(order_id, customer_id, order_date, gross_sales);

SELECT count(*) AS orders, sum(gross_sales) AS total FROM fact_orders;

SELECT customer_id, count(*) AS current_rows
FROM dim_customer
WHERE eff_end = DATE '9999-01-01'
GROUP BY customer_id
HAVING count(*) > 1;

SELECT d.zip, count(*) AS orders, sum(f.gross_sales) AS sales
FROM fact_orders f
JOIN dim_customer d
  ON d.customer_id = f.customer_id
 AND f.order_date BETWEEN d.eff_start AND d.eff_end
GROUP BY d.zip
ORDER BY d.zip;

CREATE TABLE orders_log AS
SELECT * FROM (VALUES
  (100, 'new',     TIMESTAMP '2022-03-01 10:00:00', false),
  (100, 'paid',    TIMESTAMP '2022-03-01 10:05:00', false),
  (101, 'new',     TIMESTAMP '2022-03-01 11:00:00', false),
  (101, 'deleted', TIMESTAMP '2022-03-01 12:00:00', true),
  (102, 'new',     TIMESTAMP '2022-03-01 13:00:00', false)
) AS t(order_id, status, updated_at, is_deleted);

SELECT order_id, status
FROM orders_log
QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1
   AND NOT is_deleted
ORDER BY order_id;

CREATE TABLE orders_now (order_id INTEGER PRIMARY KEY, status VARCHAR);
INSERT INTO orders_now VALUES (100, 'new'), (102, 'new');

MERGE INTO orders_now AS t
USING (SELECT * FROM (VALUES (100, 'paid'), (103, 'new')) AS s(order_id, status)) AS s
ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET status = s.status
WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.status);

SELECT * FROM orders_now ORDER BY order_id;

CREATE TABLE events AS
SELECT * FROM (VALUES
  (1, TIMESTAMP '2022-03-01 10:00:00'), (1, TIMESTAMP '2022-03-01 10:02:00'),
  (1, TIMESTAMP '2022-03-01 10:03:30'), (1, TIMESTAMP '2022-03-01 10:20:00'),
  (1, TIMESTAMP '2022-03-01 10:22:00'), (2, TIMESTAMP '2022-03-01 10:01:00')
) AS t(user_id, ts);

WITH marked AS (
  SELECT *, CASE WHEN ts - lag(ts) OVER (PARTITION BY user_id ORDER BY ts) >= INTERVAL 5 MINUTE
                 THEN 1 ELSE 0 END AS new_session
  FROM events
), numbered AS (
  SELECT *, sum(new_session) OVER (PARTITION BY user_id ORDER BY ts) AS session_no
  FROM marked
)
SELECT user_id, session_no, min(ts) AS started, max(ts) AS ended, count(*) AS events
FROM numbered
GROUP BY user_id, session_no
ORDER BY user_id, session_no;

SELECT time_bucket(INTERVAL 10 MINUTE, ts) AS window_start, count(*) AS events
FROM events
GROUP BY window_start
ORDER BY window_start;
