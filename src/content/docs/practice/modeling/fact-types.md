---
title: Типы fact tables
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Типы fact table: snapshot, accumulating, factless | Инжиниринг Данных"
description: Transaction, periodic snapshot, accumulating snapshot и factless fact table. Когда какую выбрать, role-playing dimension. Практика в DuckDB.
sidebar:
  order: 8
  label: Типы fact tables
tags:
  - data-modelling
  - practice
  - duckdb
---
`fact_sales` — transaction fact table. Но не каждый процесс — это поток событий. Остаток на складе — это состояние. Доставка заказа — процесс с этапами. Для них нужны другие типы fact tables.

![Три типа fact tables: transaction — строка на событие, periodic snapshot — строка на период, accumulating snapshot — строка на весь процесс](/assets/practice/modeling/fact-types.png)

## Сравнение

| | Transaction | Periodic snapshot | Accumulating snapshot |
|---|---|---|---|
| Одна строка | Событие | Состояние на конец периода | Весь процесс от начала до конца |
| Пример | Позиция в чеке | Остаток товара на конец дня | Заказ: создан → отгружен → доставлен |
| Даты | Одна дата события | Дата снимка | Много дат: по одной на этап |
| Строки меняются? | Нет, только добавляются | Нет, каждый период — новые строки | **Да**, строку обновляют на каждом этапе |
| Факты | Additive | Часто semi-additive (остатки, балансы) | Длительности этапов, счётчики |
| Плотность | Нет события — нет строки | Строка есть всегда, даже если ничего не случилось | Одна строка на процесс |
| Размер | Растёт с числом событий | Растёт предсказуемо: объекты × периоды | Растёт с числом процессов |

Эти типы не заменяют, а **дополняют** друг друга. У склада может быть и transaction (каждое движение товара), и periodic snapshot (остаток на вечер). Остаток можно посчитать из движений, но это долго: нужно сложить всю историю. Snapshot отвечает сразу.

## Periodic snapshot

**Periodic snapshot** фиксирует состояние через равные промежутки: каждый день, неделю, месяц. Примеры: остаток на складе, баланс счёта, число активных подписок.

Главное свойство — факты обычно **semi-additive**. Остатки складывают по товарам и магазинам, но **не по дням**. По времени берут среднее или значение на последний день.

## Accumulating snapshot

**Accumulating snapshot** описывает процесс с понятным началом и концом. Одна строка — один экземпляр процесса: заказ, заявка, страховой случай.

![Accumulating snapshot заказа: три даты-этапа order_date_key, shipped_date_key, delivered_date_key и длительности между ними](/assets/practice/modeling/accumulating-snapshot.png)

Особенности:

- **Много дат.** По одной на каждый этап (milestone).
- **Строку обновляют.** Заказ отгрузили — заполнили `shipped_date_key`. Доставили — `delivered_date_key`. Это единственный тип fact table, где `UPDATE` — норма.
- **Будущие этапы ещё не наступили.** Их дата указывает на строку `-1` «Неизвестно» в `dim_date`.
- **Длительности этапов** — главные факты: сколько дней от заказа до отгрузки.

### Role-playing dimension

В accumulating snapshot три даты. Все три ссылаются на **одну** таблицу `dim_date`. Одно измерение играет несколько ролей: дата заказа, дата отгрузки, дата доставки. Это **role-playing dimension**.

В запросе `dim_date` подключают несколько раз с разными псевдонимами. Часто для удобства делают представления (view): `dim_order_date`, `dim_ship_date`.

## Factless fact table

**Factless fact table** — таблица без чисел. В ней только ключи измерений. Мерой служит **сам факт строки**: `count(*)`.

Два вида:

- **События.** Студент пришёл на занятие. Клиент зашёл на страницу.
- **Покрытие (coverage).** Что **могло** произойти. Например: товар был в наличии в магазине. Это помогает ответить на вопрос «что **не** произошло?»: товар был на полке, но его не купили. Transaction fact этого не покажет: нет продажи — нет строки.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Подготовка: база `modeling.duckdb` открыта, `fact_sales` и измерения созданы.

### Periodic snapshot: fact_inventory_daily

Grain: остаток одного товара в одном магазине на конец одного дня.

```sql
CREATE OR REPLACE TABLE fact_inventory_daily AS
SELECT
    d.date_key,
    s.store_key,
    p.product_key,
    i.quantity_on_hand,
    i.quantity_on_hand * sp.list_price AS stock_value
FROM src.inventory i
JOIN dim_date     d  ON d.full_date   = i.snapshot_date
JOIN dim_store    s  ON s.store_id    = i.store_id
JOIN dim_product  p  ON p.product_id  = i.product_id
JOIN src.products sp ON sp.product_id = i.product_id;

SELECT count(*) FROM fact_inventory_daily;
```

`stock_value` мы считаем по текущей цене. В реальном DWH берут себестоимость на дату снимка.

Остаток на конец месяца по магазинам — берём **последний день**:

```sql
SELECT s.store_name,
       sum(f.quantity_on_hand) AS units,
       sum(f.stock_value)      AS value
FROM fact_inventory_daily f
JOIN dim_store s ON s.store_key = f.store_key
WHERE f.date_key = 20250630
GROUP BY ALL
ORDER BY value DESC;
```

### Задание 1

Средний дневной остаток (в штуках) по категориям за июнь. Помните: сначала сумма за день, потом среднее по дням.

**Проверка:** 5 строк. Первая — Аксессуары: 304,4 штуки в среднем.

<details>
<summary>Решение</summary>

```sql
WITH daily AS (
    SELECT f.date_key, p.category_name, sum(f.quantity_on_hand) AS units
    FROM fact_inventory_daily f
    JOIN dim_product p ON p.product_key = f.product_key
    GROUP BY ALL
)
SELECT category_name, round(avg(units), 1) AS avg_units
FROM daily
GROUP BY ALL
ORDER BY avg_units DESC;
```

Полный результат:

| category_name | avg_units |
|---|---|
| Аксессуары | 304,4 |
| Снаряжение | 268,3 |
| Электроника | 255,6 |
| Обувь | 242,5 |
| Одежда | 238,9 |

</details>

### Задание 2

Сколько раз в июне товар заканчивался в магазине (`quantity_on_hand = 0`)? Покажите по магазинам. Здесь `count(*)` — это «товаро-дни без остатка».

**Проверка:** 4 строки. Больше всего у ТЦ Авиапарк — 17.

<details>
<summary>Решение</summary>

```sql
SELECT s.store_name, count(*) FILTER (WHERE f.quantity_on_hand = 0) AS out_of_stock_days
FROM fact_inventory_daily f
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY ALL
ORDER BY out_of_stock_days DESC;
```

Полный результат:

| store_name | out_of_stock_days |
|---|---|
| ТЦ Авиапарк | 17 |
| Казань Молл | 5 |
| Невский | 3 |
| Онлайн-магазин | 1 |

</details>

### Accumulating snapshot: fact_order_fulfillment

Процесс: выполнение онлайн-заказа. Grain: один онлайн-заказ. Строка показывает текущее состояние заказа на дату загрузки.

```sql
CREATE OR REPLACE TABLE fact_order_fulfillment AS
WITH amounts AS (
    SELECT order_id,
           count(*)                                    AS items_count,
           sum(quantity * unit_price - discount_amount) AS order_amount
    FROM src.order_items
    GROUP BY order_id
)
SELECT
    o.order_id,
    s.store_key,
    strftime(o.order_date, '%Y%m%d')::INT                       AS order_date_key,
    coalesce(strftime(o.shipped_date, '%Y%m%d')::INT, -1)       AS shipped_date_key,
    coalesce(strftime(o.delivered_date, '%Y%m%d')::INT, -1)     AS delivered_date_key,
    o.status,
    a.items_count,
    a.order_amount,
    o.shipping_cost,
    o.shipped_date   - o.order_date   AS days_to_ship,
    o.delivered_date - o.shipped_date AS days_in_transit,
    o.delivered_date - o.order_date   AS days_to_deliver
FROM src.orders o
JOIN dim_store s ON s.store_id = o.store_id
JOIN amounts   a ON a.order_id = o.order_id
WHERE s.store_type = 'Онлайн';

SELECT status, count(*) AS orders
FROM fact_order_fulfillment
GROUP BY ALL
ORDER BY orders DESC;
```

Здесь отменённые заказы **остаются**. Отмена — это тоже исход процесса.

В рабочем DWH эту таблицу не пересобирают целиком, а обновляют: каждый день находят заказы, у которых появилась новая дата, и делают `UPDATE` (или `MERGE`). Заказ со статусом `shipped` завтра станет `delivered`.

Role-playing: подключаем `dim_date` дважды — как дату заказа и как дату доставки:

```sql
SELECT od.month_name                 AS order_month,
       dd.day_name                   AS delivery_day,
       count(*)                      AS orders
FROM fact_order_fulfillment f
JOIN dim_date od ON od.date_key = f.order_date_key
JOIN dim_date dd ON dd.date_key = f.delivered_date_key
WHERE od.month = 6
GROUP BY ALL
ORDER BY orders DESC
LIMIT 5;
```

Первая строка — «Неизвестно». Это заказы июня, которые ещё не доставлены. Без строки `-1` в `dim_date` они бы пропали из отчёта.

### Задание 3

Среднее время от заказа до доставки (в днях) по месяцам заказа. Учитывайте только доставленные заказы. Становится ли доставка быстрее?

**Проверка:** 6 строк. Среднее — от 3,2 до 3,6 дня.

<details>
<summary>Решение</summary>

```sql
SELECT d.month,
       count(*)                       AS delivered,
       round(avg(f.days_to_deliver), 2) AS avg_days
FROM fact_order_fulfillment f
JOIN dim_date d ON d.date_key = f.order_date_key
WHERE f.status = 'delivered'
GROUP BY ALL
ORDER BY d.month;
```

Явного тренда нет. Полный результат:

| month | delivered | avg_days |
|---|---|---|
| 1 | 114 | 3,20 |
| 2 | 102 | 3,24 |
| 3 | 146 | 3,42 |
| 4 | 147 | 3,59 |
| 5 | 188 | 3,29 |
| 6 | 124 | 3,29 |

</details>

### Задание 4

Сколько заказов «в пути» на конец июня: отгружены, но не доставлены? На какую сумму? Заметьте: у них `delivered_date_key = -1`.

**Проверка:** 28 заказов на 363 817 рублей.

<details>
<summary>Решение</summary>

```sql
SELECT count(*) AS in_transit, sum(order_amount) AS amount
FROM fact_order_fulfillment
WHERE shipped_date_key <> -1 AND delivered_date_key = -1;
```

</details>

### Factless: fact_product_in_stock

Покрытие: товар был в наличии в магазине на конец дня. Grain: дата × магазин × товар, только если остаток больше нуля. Чисел нет.

```sql
CREATE OR REPLACE TABLE fact_product_in_stock AS
SELECT date_key, store_key, product_key
FROM fact_inventory_daily
WHERE quantity_on_hand > 0;
```

### Задание 5

Какие товары были в наличии в офлайн-магазине **весь июнь** (30 дней), но **ни разу не продались** там в июне? Это кандидаты на распродажу.

**Проверка:** одна пара: «Невский» — Фитнес-браслет. Он лежал на полке все 30 дней, и никто его не купил.

<details>
<summary>Решение</summary>

```sql
WITH in_stock AS (
    SELECT store_key, product_key, count(*) AS days_in_stock
    FROM fact_product_in_stock
    WHERE date_key BETWEEN 20250601 AND 20250630
    GROUP BY ALL
),
sold AS (
    SELECT DISTINCT store_key, product_key
    FROM fact_sales
    WHERE date_key BETWEEN 20250601 AND 20250630
)
SELECT s.store_name, p.product_name, i.days_in_stock
FROM in_stock i
JOIN dim_store   s ON s.store_key   = i.store_key
JOIN dim_product p ON p.product_key = i.product_key
LEFT JOIN sold x ON x.store_key = i.store_key AND x.product_key = i.product_key
WHERE x.store_key IS NULL
  AND i.days_in_stock = 30
  AND s.store_type = 'Офлайн'
ORDER BY s.store_name, p.product_name;
```

Это главный приём с factless coverage: «было возможно» минус «случилось» = «не случилось».

</details>

## Итог

- Transaction — события. Periodic snapshot — состояние на конец периода. Accumulating snapshot — процесс с этапами.
- Snapshot-факты часто semi-additive: по времени их не складывают.
- Accumulating snapshot обновляют. Ещё не наступившие этапы ссылаются на `-1`.
- Одно измерение даты играет много ролей (role-playing).
- Factless coverage помогает найти то, чего **не** было.

**Глубже:** [глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/) — три модели склада. [Глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/) — accumulating snapshot заказа, role-playing, factless. [Глава 13](/book-summaries/engineering/data-warehouse-toolkit/13-education/) — factless fact tables на примере образования.

Дальше: [Slowly Changing Dimensions](/practice/modeling/scd/).
