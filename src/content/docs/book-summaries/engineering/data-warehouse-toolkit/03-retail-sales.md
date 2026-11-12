---
title: "The Data Warehouse Toolkit, глава 3: Продажи в рознице"
head:
  - tag: title
    content: "Star schema на примере розницы: Kimball | Инжиниринг Данных"
description: "Конспект главы 3 The Data Warehouse Toolkit. Четыре шага проектирования, grain, degenerate dimension, factless fact table, star schema и практика в DuckDB."
sidebar:
  order: 3
  label: "3. Продажи в рознице"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** любую витрину проектируют одинаково. Выберите бизнес-процесс, задайте grain, перечислите dimensions, перечислите facts. Первый пример в книге — касса в магазине.

![Star schema розничных продаж: одна fact-таблица и четыре dimension](/assets/data-warehouse-toolkit/ch03-retail-star.png)

## Четыре шага проектирования

| Шаг | Вопрос | Пример в рознице |
|---|---|---|
| 1. Business process | Какой процесс измеряем? | Продажи на кассе (POS) |
| 2. Grain | Что значит одна строка? | Одна позиция в чеке |
| 3. Dimensions | Кто, что, где, когда, почему? | Дата, товар, магазин, акция |
| 4. Facts | Что мы считаем? | Количество, сумма продажи |

Порядок важен. Grain выбирают до dimensions и facts. Если grain нечёткий, модель сломается.

## Grain

- Лучше всего брать самый детальный (`atomic`) grain. Его можно агрегировать. Обратно детали не вернуть.
- Все facts в таблице должны относиться к одному grain.
- Все dimensions в таблице должны быть верны для этого grain.

## Fact table

Fact table хранит измерения процесса. Это числа, которые мы суммируем или усредняем.

| Тип факта | Можно ли суммировать | Пример |
|---|---|---|
| Additive | По всем dimensions | Сумма продажи, количество |
| Semi-additive | По некоторым dimensions, но не по времени | Остаток на счёте |
| Non-additive | Нельзя. Храните компоненты | Процент маржи, цена за единицу |

- Для процента храните числитель и знаменатель. Считайте отношение в запросе: `sum(a) / sum(b)`.
- `NULL` в факте допустим. Агрегаты его пропускают. `NULL` в foreign key недопустим. Используйте строку «Unknown» в dimension.
- Строки в fact table создаются только при событии. Если акция была, а продаж нет, строки нет. Для вопросов «чего не было» нужен `factless fact table` (см. ниже).

В книге у продажи больше facts: цены за единицу (обычная, скидка, итоговая) и суммы по строке (скидка, выручка, себестоимость, gross profit). Цены за единицу — non-additive. Суммы по строке — additive. Gross margin считаем в запросе: `sum(gross_profit) / sum(sales)`.

## Dimension table

Dimension хранит описание: по чему мы режем и группируем.

- Это широкая и плоская таблица. В ней много текстовых атрибутов.
- Primary key — `surrogate key`. Это целое число без смысла. Ключ из источника (`natural key`) хранится как обычный атрибут.
- Иерархии (товар → бренд → категория) лежат в одной таблице. Это денормализация, она намеренная.

### Date dimension

- Её строят один раз на несколько лет вперёд.
- Атрибуты: день недели, месяц, квартал, праздник, fiscal period.
- Нужна, потому что SQL не знает про ваши праздники и финансовый год.

### Degenerate dimension

Номер чека лежит в fact table. У него нет атрибутов, отдельная таблица не нужна. Такое поле называют `degenerate dimension` (`DD`). По нему группируют строки в «корзину».

### Promotion dimension

- Это `causal dimension`: она описывает, что могло вызвать продажу. Скидка, листовка, выкладка, купон.
- У продаж без акции ключ ведёт на строку «Без акции». `NULL` в ключе не ставим.

## Factless fact table: покрытие акций

Вопрос «какие товары были в акции, но не продавались?» sales fact не отвечает. В нём есть только проданные товары.

- Нужен отдельный `promotion coverage fact table`.
- Ключи: дата, товар, магазин, акция. Grain: товар в акции в магазине в этот день. Строка есть, даже если продаж не было.
- Чисел нет. Иногда добавляют `promotion_count = 1`, чтобы было удобно считать.
- Ответ — разность двух множеств: «было в акции» минус «продавалось».

Такие таблицы встретятся снова: в главе 6 (покрытие клиентов торговыми представителями) и в главе 13 (посещаемость).

## Расширение модели

Star schema легко расширять. Старые запросы не ломаются:

- новая dimension, если у неё одно значение на строку fact (например, кассир);
- новый атрибут в dimension;
- новый fact на том же grain.

## Ключи

| Ключ | Правило книги |
|---|---|
| Surrogate key dimension | Целое число без смысла. Защищает от изменений в источнике и нужен для SCD Type 2 |
| Natural key | Ключ из источника. Хранится как атрибут |
| Durable (supernatural) key | Свой постоянный ключ сущности. Не меняется, даже если источник сменил свой ключ |
| Smart key даты | `20241225` допустим для date dimension. Удобно для партиций |
| Degenerate dimension | Surrogate key не нужен. Номер чека и так уникален |
| Fact table surrogate key | Необязателен. Полезен для ETL: перезапуск загрузки, обновления |

## Star и snowflake

| Схема | Что это | Вывод книги |
|---|---|---|
| Star | Dimension плоские, одна join до fact | Рекомендуется |
| Snowflake | Dimension нормализованы в подтаблицы | Обычно не нужна. Сложнее для людей, экономия места мала |

- Dimension много меньше fact. Экономия на нормализации незаметна.
- Исключение: общие подтаблицы-`outrigger`, если их правда нужно переиспользовать. Пример: календарь открытия магазина в `dim_store`.
- Обратная ошибка — `centipede fact table`: десятки foreign keys, по одному на каждый уровень иерархии (товар, бренд, категория отдельно). Иерархию держим внутри одной dimension.

## Ключевые термины

| Термин | Значение |
|---|---|
| Grain | Что означает одна строка fact table |
| Fact | Числовое измерение процесса |
| Dimension | Описательный контекст |
| Surrogate key | Служебный ключ dimension |
| Degenerate dimension | Идентификатор в fact table без своей таблицы |
| Star schema | Fact в центре, плоские dimensions вокруг |

## Что это значит на практике

- Начинайте с вопроса «что такое одна строка?». Запишите ответ одним предложением.
- В `dbt` fact — это таблица `fct_*`, dimension — `dim_*`. Тесты `unique` и `relationships` проверяют grain и ключи.
- Не кладите проценты в fact. Храните суммы и считайте отношение в BI.
- Если нужно несколько единиц измерения (штуки и коробки), храните коэффициент конверсии прямо в fact. Так советует книга в главе 6.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём star schema

```sql
CREATE TABLE dim_date AS
SELECT
    strftime(d, '%Y%m%d')::INT AS date_key,
    d AS full_date,
    monthname(d) AS month_name,
    dayname(d) AS day_name,
    (month(d) = 12 AND day(d) = 25) AS is_holiday
FROM generate_series(DATE '2024-12-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_product AS
SELECT * FROM (VALUES
    (1, 'SKU-100', 'Молоко 1л',   'Дары полей', 'Молочные'),
    (2, 'SKU-200', 'Йогурт',      'Дары полей', 'Молочные'),
    (3, 'SKU-300', 'Хлеб белый',  'Пекарь',     'Выпечка'),
    (4, 'SKU-400', 'Багет',       'Пекарь',     'Выпечка'),
    (5, 'SKU-500', 'Кофе 250г',   'Бодрое утро','Бакалея')
) t(product_key, sku, product_name, brand, category);

CREATE TABLE dim_store AS
SELECT * FROM (VALUES
    (1, 'Магазин №1', 'Москва',  'Центр'),
    (2, 'Магазин №2', 'Казань',  'Поволжье')
) t(store_key, store_name, city, region);

CREATE TABLE dim_promotion AS
SELECT * FROM (VALUES
    (0, 'Без акции',        'none'),
    (1, 'Скидка 20%',       'discount'),
    (2, 'Новый год',        'seasonal')
) t(promotion_key, promotion_name, promo_type);

-- grain: одна позиция в чеке. В чеке 3 позиции, у чека одна дата и один магазин
CREATE TABLE fact_retail_sales AS
WITH lines AS (
    SELECT i,
           (i // 3) % 31   AS day_no,
           1 + (i * 7) % 5 AS product_key,
           1 + (i // 3) % 2 AS store_key
    FROM range(0, 300) t(i)
), promo AS (
    SELECT *,
           CASE WHEN day_no >= 19 AND product_key IN (1, 2, 5) THEN 2  -- Новый год: 20–31 декабря
                WHEN day_no < 10  AND product_key = 3          THEN 1  -- скидка 20%: 1–10 декабря
                ELSE 0 END AS promotion_key
    FROM lines
)
SELECT
    strftime(DATE '2024-12-01' + day_no::INT, '%Y%m%d')::INT AS date_key,
    product_key,
    store_key,
    promotion_key,
    'T' || lpad((i // 3)::VARCHAR, 5, '0') AS ticket_number,
    1 + (i % 4) AS sales_quantity,
    round((1 + (i % 4)) * (20 + 30 * product_key)
          * CASE WHEN promotion_key = 1 THEN 0.8 ELSE 1 END, 2) AS net_sales_amount
FROM promo;
```

### Шаг 2. Проверяем grain и ключи

```sql
-- должно вернуть 0 строк: у каждого foreign key есть пара в dimension
SELECT count(*) AS orphan_rows
FROM fact_retail_sales f
LEFT JOIN dim_product p USING (product_key)
WHERE p.product_key IS NULL;

SELECT count(*) AS rows_in_fact, count(DISTINCT ticket_number) AS tickets
FROM fact_retail_sales;
```

### Задания

**1.** Выручка по категориям. Сначала напишите запрос сами.

<details>
<summary>Решение</summary>

```sql
SELECT p.category, sum(f.net_sales_amount) AS revenue
FROM fact_retail_sales f
JOIN dim_product p USING (product_key)
GROUP BY p.category
ORDER BY revenue DESC;
```
</details>

**2.** Выручка по региону и по бренду. Измените только `GROUP BY` и `JOIN`. Fact не трогайте.

<details>
<summary>Решение</summary>

```sql
SELECT s.region, p.brand, sum(f.net_sales_amount) AS revenue
FROM fact_retail_sales f
JOIN dim_store s USING (store_key)
JOIN dim_product p USING (product_key)
GROUP BY ALL
ORDER BY s.region, revenue DESC;
```
</details>

**3.** Эффект акции. Покажите для каждого типа акции количество строк, выручку и среднюю цену за штуку. Цена — non-additive: считайте её как `sum(сумма) / sum(штуки)`, а не как среднее цен.

<details>
<summary>Решение</summary>

```sql
SELECT pr.promo_type,
       count(*)                                  AS lines,
       sum(f.net_sales_amount)                   AS revenue,
       sum(f.net_sales_amount) / sum(f.sales_quantity) AS avg_price_per_unit
FROM fact_retail_sales f
JOIN dim_promotion pr USING (promotion_key)
GROUP BY pr.promo_type
ORDER BY revenue DESC;
```
</details>

**4.** Средняя «корзина». Используйте degenerate dimension `ticket_number`. Найдите среднюю сумму чека и среднее число позиций.

<details>
<summary>Решение</summary>

```sql
WITH tickets AS (
    SELECT ticket_number,
           count(*)                AS items,
           sum(net_sales_amount)   AS ticket_total
    FROM fact_retail_sales
    GROUP BY ticket_number
)
SELECT avg(ticket_total) AS avg_ticket, avg(items) AS avg_items
FROM tickets;
```
</details>

**5.** Праздники. Сравните выручку 25 декабря и среднюю выручку остальных дней. Для этого нужна `dim_date`.

<details>
<summary>Решение</summary>

```sql
SELECT d.is_holiday,
       count(DISTINCT d.date_key)               AS days,
       sum(f.net_sales_amount)                  AS revenue,
       sum(f.net_sales_amount) / count(DISTINCT d.date_key) AS revenue_per_day
FROM fact_retail_sales f
JOIN dim_date d USING (date_key)
GROUP BY d.is_holiday;
```
</details>

**6.** Factless fact table. Создайте `fact_promotion_coverage`: какие товары были в акции в каждом магазине по дням. Для каждого товара посчитайте пары «магазин × день», когда товар был в акции, но не продавался.

<details>
<summary>Решение</summary>

```sql
-- grain: товар в акции в магазине в этот день. Продажи не важны
CREATE TABLE fact_promotion_coverage AS
SELECT d.date_key, p.product_key, s.store_key, pr.promotion_key
FROM dim_date d
CROSS JOIN dim_store s
CROSS JOIN dim_product p
JOIN dim_promotion pr
  ON (pr.promotion_key = 2 AND d.full_date >= DATE '2024-12-20' AND p.product_key IN (1, 2, 5))
  OR (pr.promotion_key = 1 AND d.full_date <= DATE '2024-12-10' AND p.product_key = 3);

-- было в акции МИНУС продавалось
SELECT p.product_name, pr.promotion_name,
       count(*) AS covered_store_days,
       count(*) FILTER (WHERE NOT EXISTS (
           SELECT 1 FROM fact_retail_sales f
           WHERE f.date_key = c.date_key AND f.product_key = c.product_key
             AND f.store_key = c.store_key AND f.promotion_key = c.promotion_key
       )) AS store_days_without_sales
FROM fact_promotion_coverage c
JOIN dim_product p USING (product_key)
JOIN dim_promotion pr USING (promotion_key)
GROUP BY ALL
ORDER BY p.product_name;
```

В sales fact таких дней не видно: там нет строк с нулём. Только coverage показывает, что товар был в акции.
</details>

## Вопросы для самопроверки

1. Почему grain выбирают до dimensions и facts?
2. Чем additive fact отличается от semi-additive?
3. Зачем в dimension нужен surrogate key, если есть natural key?
4. Когда номер чека лучше оставить в fact, а не выносить в таблицу?
5. Как найти товары, которые были в акции, но не продавались?
