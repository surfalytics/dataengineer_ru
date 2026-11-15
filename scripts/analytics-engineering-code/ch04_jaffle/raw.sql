-- Сырые данные: три таблицы в двух схемах, как jaffle_shop и stripe в книге
CREATE SCHEMA IF NOT EXISTS jaffle_shop;
CREATE SCHEMA IF NOT EXISTS stripe;

CREATE OR REPLACE TABLE jaffle_shop.customers AS
SELECT * FROM (VALUES
  (1, 'Анна', 'Ветрова'), (2, 'Борис', 'Кузнецов'), (3, 'Вера', 'Орлова'),
  (4, 'Глеб', 'Соколов'), (5, 'Дина', 'Морозова'), (6, 'Егор', 'Лебедев'),
  (7, 'Жанна', 'Новикова'), (8, 'Зоя', 'Павлова')
) AS t(id, first_name, last_name);

-- 20 заказов; _etl_loaded_at: загрузка была 16 часов назад
CREATE OR REPLACE TABLE jaffle_shop.orders AS
SELECT i AS id,
       1 + (i * 3) % 8 AS user_id,
       DATE '2024-01-01' + i * 3 AS order_date,
       CASE WHEN i % 7 = 0 THEN 'return_pending'
            WHEN i % 5 = 0 THEN 'returned'
            WHEN i % 9 = 0 THEN 'placed'
            WHEN i % 4 = 0 THEN 'shipped'
            ELSE 'completed' END AS status,
       now() - INTERVAL 16 HOUR AS _etl_loaded_at
FROM (SELECT CAST(range AS INTEGER) AS i FROM range(1, 21));

-- 1-2 платежа на заказ; часть платежей неуспешна (fail)
CREATE OR REPLACE TABLE stripe.payment AS
SELECT row_number() OVER (ORDER BY o.id, p.n) AS id,
       o.id AS orderid,
       CASE (o.id + p.n) % 5 WHEN 0 THEN 'credit_card' WHEN 1 THEN 'paypal'
            WHEN 2 THEN 'gift_card' WHEN 3 THEN 'bank_transfer' ELSE 'coupon' END AS paymentmethod,
       CASE WHEN (o.id * p.n) % 6 = 0 THEN 'fail' ELSE 'success' END AS status,
       (o.id * 7 + p.n * 3) % 25 + 1 AS amount,
       o.order_date AS created
FROM jaffle_shop.orders AS o
CROSS JOIN LATERAL (SELECT unnest(range(1, 2 + o.id % 2)) AS n) AS p;
