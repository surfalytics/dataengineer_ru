---
title: Строим fact table
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Fact table и star schema в DuckDB: пример | Инжиниринг Данных"
description: Строим transaction fact table продаж по шагам. Поиск surrogate key, degenerate dimension, сверка с источником и запросы к star schema в DuckDB.
sidebar:
  order: 7
  label: Строим fact table
tags:
  - data-modelling
  - practice
  - duckdb
---
Измерения готовы. Теперь соберём центр звезды — `fact_sales`. Это **transaction fact table**: одна строка — одно событие.

![Star schema магазина: fact_sales в центре связан с dim_date, dim_customer, dim_product и dim_store](/assets/practice/modeling/star-schema.png)

## Как собирают fact table

Повторим решения из [четырёх шагов](/practice/modeling/four-steps/):

| Решение | Значение |
|---|---|
| Процесс | Клиент покупает товары |
| Grain | Одна позиция в заказе |
| Dimensions | `dim_date`, `dim_customer`, `dim_product`, `dim_store` |
| Degenerate dimension | `order_id`, `line_number` |
| Facts | `quantity`, `gross_amount`, `discount_amount`, `net_amount`, `shipping_amount` |
| Бизнес-правило | Отменённые заказы не входят в продажи |

ETL делает для каждой строки источника три вещи:

1. **Ищет surrogate key.** По natural key из источника находит строку в измерении и берёт её ключ. Это называют **key lookup**.
2. **Считает факты.** `gross_amount = quantity × unit_price`. Доставку распределяет по позициям.
3. **Применяет правила.** Убирает отменённые заказы. Гостям ставит `customer_key = -1`.

## Практика: собираем fact_sales

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Подготовка: база `modeling.duckdb` открыта, измерения созданы в [прошлом уроке](/practice/modeling/dimensions/).

```sql
CREATE OR REPLACE TABLE fact_sales AS
SELECT
    -- ключи измерений (key lookup)
    d.date_key,
    coalesce(c.customer_key, -1) AS customer_key,
    p.product_key,
    s.store_key,
    -- degenerate dimension
    o.order_id,
    i.line_number,
    -- факты
    i.quantity,
    i.quantity * i.unit_price                     AS gross_amount,
    i.discount_amount,
    i.quantity * i.unit_price - i.discount_amount AS net_amount,
    round(o.shipping_cost
          * (i.quantity * i.unit_price - i.discount_amount)
          / sum(i.quantity * i.unit_price - i.discount_amount) OVER (PARTITION BY o.order_id),
          2)                                      AS shipping_amount
FROM src.order_items i
JOIN src.orders      o ON o.order_id    = i.order_id
JOIN dim_date        d ON d.full_date   = o.order_date
JOIN dim_product     p ON p.product_id  = i.product_id
JOIN dim_store       s ON s.store_id    = o.store_id
LEFT JOIN dim_customer c ON c.customer_id = o.customer_id
WHERE o.status <> 'cancelled';

SELECT * FROM fact_sales LIMIT 5;
```

Посмотрите на результат. В таблице только числа. Ни одного названия. Все названия — в измерениях.

## Сверка с источником

Fact table **всегда** сверяют с источником. Три проверки:

```sql
-- 1. Число строк: в факте столько же позиций, сколько в источнике без отмен
SELECT
    (SELECT count(*) FROM fact_sales) AS fact_rows,
    (SELECT count(*) FROM src.order_items i JOIN src.orders o USING (order_id)
     WHERE o.status <> 'cancelled')   AS source_rows;

-- 2. Суммы: выручка и доставка совпадают
SELECT sum(net_amount) AS revenue, sum(shipping_amount) AS shipping
FROM fact_sales;

-- 3. Grain: пара (order_id, line_number) уникальна
SELECT count(*) - count(DISTINCT (order_id, line_number)) AS duplicates
FROM fact_sales;
```

**Проверка:** 3431 строка в обоих случаях. Выручка 25 999 963 — как в [первом уроке](/practice/modeling/why-model/). Доставка 91 371. Дубликатов 0.

Если число строк в факте меньше — какой-то `JOIN` с измерением потерял строки. Обычно это значит: в измерении нет нужного ключа. Если больше — в измерении дубли natural key.

## Запросы к звезде

Все запросы строятся по одному шаблону. Выручка по категориям:

```sql
SELECT p.category_name, sum(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY ALL
ORDER BY revenue DESC;
```

Один `JOIN` вместо трёх. Числа те же, что в первом уроке.

Выручка по месяцам и типу магазина:

```sql
SELECT d.year_month, s.store_type, sum(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_date  d ON d.date_key  = f.date_key
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY ALL
ORDER BY ALL;
```

Каждое измерение подключается одним `JOIN` к факту. Порядок не важен. Нужен атрибут — добавили `JOIN` и колонку в `GROUP BY`.

### Задание 1

Топ-5 товаров по выручке. Покажите название, бренд, количество проданных штук и выручку.

**Проверка:** 5 строк. Первая — Смарт-часы: 232 штуки на 4 852 504.

<details>
<summary>Решение</summary>

```sql
SELECT p.product_name, p.brand,
       sum(f.quantity)   AS quantity,
       sum(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY ALL
ORDER BY revenue DESC
LIMIT 5;
```

Полный результат:

| product_name | brand | quantity | revenue |
|---|---|---|---|
| Смарт-часы | Pulse | 232 | 4 852 504 |
| Кроссовки беговые | Stride | 269 | 2 511 135 |
| Трейловые кроссовки | Stride | 211 | 2 480 731 |
| Наушники беспроводные | Pulse | 207 | 2 149 165 |
| Куртка-ветровка | Stride | 262 | 2 057 425 |

</details>

### Задание 2

Какая доля выручки приходится на гостей в каждом магазине? Онлайн гостей быть не должно.

**Проверка:** 4 строки. Больше всего у ТЦ Авиапарк — 18,0%.

<details>
<summary>Решение</summary>

```sql
SELECT s.store_name,
       round(100 * sum(f.net_amount) FILTER (WHERE f.customer_key = -1)
                 / sum(f.net_amount), 1) AS guest_share_pct
FROM fact_sales f
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY ALL
ORDER BY guest_share_pct DESC;
```

`FILTER` пишет `NULL`, если строк нет. Для онлайна вы увидите `NULL`: гостей там нет. Можно обернуть в `coalesce(..., 0)`.

Полный результат:

| store_name | guest_share_pct |
|---|---|
| ТЦ Авиапарк | 18,0 |
| Невский | 11,9 |
| Казань Молл | 10,3 |
| Онлайн-магазин | NULL |

</details>

### Задание 3. Средний чек

Средний чек — это выручка, делённая на **число заказов**. Номер заказа лежит в факте как degenerate dimension. Посчитайте средний чек по магазинам.

**Проверка:** 4 строки. У онлайн-магазина 856 заказов, средний чек 13 477,7.

<details>
<summary>Решение</summary>

```sql
SELECT s.store_name,
       count(DISTINCT f.order_id)                             AS orders,
       round(sum(f.net_amount) / count(DISTINCT f.order_id), 1) AS avg_check
FROM fact_sales f
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY ALL
ORDER BY s.store_name;
```

Средний чек — non-additive. Его нельзя хранить в факте и складывать. Его считают из двух additive-чисел.

Полный результат:

| store_name | orders | avg_check |
|---|---|---|
| Казань Молл | 268 | 13 226,2 |
| Невский | 339 | 11 417,4 |
| Онлайн-магазин | 856 | 13 477,7 |
| ТЦ Авиапарк | 494 | 14 267,1 |

</details>

### Задание 4

Где выручка в день выше: в будни или в выходные? Нужна средняя выручка **на один день**, а не общая сумма. Будних дней больше.

**Проверка:** будни — 129 318 в день, выходные — 179 190 в день. В выходные продаём на 39% больше.

<details>
<summary>Решение</summary>

```sql
SELECT d.day_type,
       count(DISTINCT d.date_key)                                AS days,
       round(sum(f.net_amount) / count(DISTINCT d.date_key))     AS revenue_per_day
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY ALL;
```

Здесь мы делим на дни, в которые были продажи. Если в какой-то день продаж не было, правильнее делить на число дней из `dim_date`.

</details>

### Задание 5

Выручка по сегменту клиента и типу магазина. Какой сегмент приносит больше онлайн?

**Проверка:** онлайн: «Обычный» — 9 563 665, VIP — 1 973 222. Больше приносит «Обычный»: таких клиентов в 5 раз больше. Офлайн «Гость» — 2 093 640.

<details>
<summary>Решение</summary>

```sql
SELECT s.store_type, c.segment, sum(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_store    s ON s.store_key    = f.store_key
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY ALL
ORDER BY ALL;
```

Сравните с [заданием 3 первого урока](/practice/modeling/why-model/). Там гости были `NULL`. Здесь — понятная подпись «Гость» благодаря unknown member.

</details>

## Итог

- Fact table собирают так: key lookup → расчёт фактов → бизнес-правила.
- Факт сверяют с источником: строки, суммы, уникальность grain.
- Запрос к звезде: факт + нужные измерения + `GROUP BY` по атрибутам.
- Non-additive метрики (средний чек) считают из additive фактов.

**Глубже:** [глава 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) — полный разбор розничной звезды. [Глава 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/) — подсистемы ETL, включая surrogate key pipeline.

Дальше: [Типы fact tables](/practice/modeling/fact-types/).
