-- Сырой слой (в книге - датасет omnichannel_raw в BigQuery). Данные те же, что в «Практике в DuckDB».
-- Колонки created_at и updated_at нужны staging-моделям из книги.
CREATE SCHEMA omnichannel_raw;

CREATE TABLE omnichannel_raw.Channels AS
SELECT channel_id, channel_name,
       TIMESTAMP '2022-01-01 00:00:00' AS created_at, TIMESTAMP '2022-01-01 00:00:00' AS updated_at
FROM (VALUES (1, 'Website'), (2, 'Mobile App'), (3, 'Instagram')) t(channel_id, channel_name);

CREATE TABLE omnichannel_raw.Products AS
SELECT product_sku, product_name, unit_price,
       TIMESTAMP '2022-01-01 00:00:00' AS created_at, TIMESTAMP '2022-01-01 00:00:00' AS updated_at
FROM (VALUES (101, 'Кожаная сумка', 149.99), (102, 'Куртка-бомбер', 129.99),
             (103, 'Кроссовки', 89.99), (104, 'Худи', 59.99), (105, 'Кепка', 19.99))
    t(product_sku, product_name, unit_price);

CREATE TABLE omnichannel_raw.Customers AS
SELECT customer_id, name, email_address,
       TIMESTAMP '2022-01-01 00:00:00' AS created_at, TIMESTAMP '2022-01-01 00:00:00' AS updated_at
FROM (VALUES (1, 'Анна', 'anna@example.com'), (2, 'Иван', 'ivan@example.com'),
             (3, 'Мария', 'maria@example.com'), (4, 'Олег', 'oleg@example.com'),
             (5, 'Елена', 'elena@example.com'))
    t(customer_id, name, email_address);

CREATE TABLE omnichannel_raw.PurchaseHistory AS
SELECT customer_id, product_sku, channel_id, quantity, discount,
       CAST(order_ts AS TIMESTAMP) AS order_date
FROM (VALUES
    (1, 101, 1, 1, 0.10, '2023-04-03 10:15'), (2, 102, 2, 2, 0.00, '2023-05-20 18:40'),
    (3, 103, 3, 1, 0.00, '2023-06-11 12:05'), (1, 104, 2, 3, 0.05, '2023-08-02 09:30'),
    (4, 101, 1, 2, 0.15, '2023-11-24 20:10'), (5, 105, 3, 4, 0.00, '2023-12-01 14:00'),
    (2, 103, 2, 1, 0.00, '2024-01-15 11:45'), (3, 102, 1, 1, 0.20, '2024-02-03 16:20'),
    (5, 104, 1, 2, 0.00, '2024-04-09 13:00'), (4, 103, 3, 2, 0.10, '2024-05-17 19:55'),
    (1, 105, 2, 1, 0.00, '2024-06-30 08:25'), (3, 101, 2, 1, 0.00, '2024-07-04 21:10')
) t(customer_id, product_sku, channel_id, quantity, discount, order_ts);

CREATE TABLE omnichannel_raw.VisitHistory AS
SELECT customer_id, channel_id,
       CAST(visit_ts AS TIMESTAMP) AS visit_timestamp,
       CAST(bounce_ts AS TIMESTAMP) AS bounce_timestamp
FROM (VALUES
    (1, 1, '2023-04-03 10:02', '2023-04-03 10:20'), (2, 2, '2023-05-20 18:31', '2023-05-20 18:44'),
    (3, 3, '2023-06-11 11:58', '2023-06-11 12:03'), (4, 1, '2023-11-24 19:50', '2023-11-24 20:16'),
    (5, 3, '2023-12-01 13:55', '2023-12-01 13:57'), (2, 2, '2024-01-15 11:40', '2024-01-15 11:49'),
    (3, 1, '2024-02-03 16:00', '2024-02-03 16:31'), (1, 2, '2024-06-30 08:20', NULL)
) t(customer_id, channel_id, visit_ts, bounce_ts);
