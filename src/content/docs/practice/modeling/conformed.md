---
title: Conformed dimensions и bus matrix
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Conformed dimensions, bus matrix и drill-across | Инжиниринг Данных"
description: Как связать несколько fact tables через conformed dimensions. Bus matrix, drill-across без двойного счёта, shrunken dimension и агрегаты. Практика в DuckDB.
sidebar:
  order: 10
  label: Conformed dimensions
tags:
  - data-modelling
  - practice
  - duckdb
---
У нас уже три fact table: продажи, остатки, выполнение заказов. Бизнес хочет видеть их **вместе**: «сколько продали и сколько осталось на складе по каждому товару». Это возможно, только если факты используют **одни и те же** измерения.

## Conformed dimension

**Conformed dimension** (согласованное измерение) — измерение, которое одинаково для нескольких fact tables:

- одни и те же ключи;
- одни и те же названия колонок;
- одни и те же значения атрибутов: «Электроника» везде пишется одинаково.

Обычно это **одна физическая таблица**. `dim_product` используют и `fact_sales`, и `fact_inventory_daily`.

![Три fact tables — продажи, остатки, возвраты — используют общие измерения дата, товар, магазин и клиент](/assets/practice/modeling/conformed-dimensions.png)

Что будет без conformed dimensions. Отдел продаж ведёт свой справочник товаров, склад — свой. В продажах категория «Электроника», на складе — «Электроника и гаджеты». Отчёт «продажи и остатки по категориям» не сходится. Начинаются споры, чьи цифры правильные.

Conformed dimensions — главное средство **интеграции** в подходе Кимбалла. Хранилище строят по частям, процесс за процессом. Общие измерения связывают части в одно целое.

### Shrunken dimension

Иногда факт хранится на уровне **крупнее**, чем измерение. Например, план продаж — по месяцам, а не по дням. Тогда делают **shrunken dimension**: уменьшенную копию измерения. `dim_month` из `dim_date`. Его атрибуты (`year`, `month`, `month_name`) — точно такие же, как в `dim_date`. Поэтому отчёты по месяцам сходятся.

### Conformed facts

Факты тоже нужно согласовать. Если «выручка» в одной таблице — до скидки, а в другой — после, их нельзя сравнивать. Одинаковое название — одно определение. Разное определение — разное название: `gross_amount` и `net_amount`.

## Bus matrix

**Bus matrix** — главный документ проектирования хранилища. Строки — бизнес-процессы (будущие fact tables). Колонки — измерения. На пересечении — отметка: этот процесс использует это измерение.

| Бизнес-процесс | Дата | Клиент | Товар | Магазин |
|---|---|---|---|---|
| Продажи (`fact_sales`) | ✓ | ✓ | ✓ | ✓ |
| Остатки (`fact_inventory_daily`) | ✓ | | ✓ | ✓ |
| Выполнение заказа (`fact_order_fulfillment`) | ✓ ×3 | | | ✓ |
| Возвраты (`fact_returns`) | ✓ | ✓ | ✓ | ✓ |

Как читать:

- **По строке** — какие измерения нужны процессу. Это план для одной fact table.
- **По колонке** — какие процессы делят измерение. Чем больше отметок, тем важнее сделать измерение conformed. `dim_date` и `dim_store` нужны всем.
- «✓ ×3» — role-playing: дата заказа, отгрузки и доставки.

Bus matrix помогает планировать. Сначала договариваемся об общих измерениях. Потом строим процессы по одному, в порядке важности для бизнеса.

## Drill-across

**Drill-across** — запрос, который объединяет **несколько fact tables** через conformed dimensions.

Правило: **сначала агрегировать каждый факт отдельно, потом соединять результаты**. Никогда не соединяйте две fact tables напрямую.

![Drill-across: каждая fact table агрегируется по товару отдельно, затем результаты соединяются по product_key](/assets/practice/modeling/drill-across.png)

Почему нельзя соединять факты напрямую. В июне у товара 30 строк остатков и, например, 20 строк продаж. `JOIN` по товару даст 30 × 20 = 600 строк. Каждая продажа посчитается 30 раз. Это **fan-out** (размножение строк).

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Подготовка: база `modeling.duckdb` открыта, все таблицы прошлых уроков созданы.

### Пример: ошибка fan-out

Соединяем продажи и остатки напрямую. Считаем выручку июня по смарт-часам:

```sql
SELECT sum(f.net_amount) AS wrong_revenue
FROM fact_sales f
JOIN fact_inventory_daily i
  ON i.product_key = f.product_key AND i.store_key = f.store_key
JOIN dim_product p ON p.product_key = f.product_key
WHERE p.product_name = 'Смарт-часы'
  AND f.date_key BETWEEN 20250601 AND 20250630;

SELECT sum(f.net_amount) AS right_revenue
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
WHERE p.product_name = 'Смарт-часы'
  AND f.date_key BETWEEN 20250601 AND 20250630;
```

Правильно — 1 211 649. Неправильно — 36 349 470, ровно в 30 раз больше. Каждая продажа соединилась с 30 днями остатков.

### Пример: правильный drill-across

Продажи и средний остаток за июнь по категориям:

```sql
WITH sales AS (
    SELECT p.category_name, sum(f.quantity) AS units_sold
    FROM fact_sales f
    JOIN dim_product p ON p.product_key = f.product_key
    WHERE f.date_key BETWEEN 20250601 AND 20250630
    GROUP BY ALL
),
stock AS (
    SELECT category_name, avg(units) AS avg_stock
    FROM (
        SELECT f.date_key, p.category_name, sum(f.quantity_on_hand) AS units
        FROM fact_inventory_daily f
        JOIN dim_product p ON p.product_key = f.product_key
        GROUP BY ALL
    )
    GROUP BY ALL
)
SELECT category_name, units_sold, round(avg_stock, 1) AS avg_stock
FROM sales
FULL JOIN stock USING (category_name)
ORDER BY category_name;
```

Каждый факт агрегирован до одного уровня — категории. Потом соединили по атрибуту conformed dimension. `FULL JOIN` сохраняет категории, которые есть только в одном из фактов.

### Задание 1. Запас в днях

Для каждого товара посчитайте за июнь:

- `units_sold` — продано штук (все магазины);
- `stock_end` — остаток на 30 июня (все магазины);
- `days_of_cover` — на сколько дней хватит остатка при июньском темпе продаж: `stock_end / (units_sold / 30)`.

Покажите 5 товаров с самым маленьким запасом.

**Проверка:** 5 строк. Первая — Скакалка: запаса хватит на 26,3 дня.

<details>
<summary>Решение</summary>

```sql
WITH sales AS (
    SELECT product_key, sum(quantity) AS units_sold
    FROM fact_sales
    WHERE date_key BETWEEN 20250601 AND 20250630
    GROUP BY ALL
),
stock AS (
    SELECT product_key, sum(quantity_on_hand) AS stock_end
    FROM fact_inventory_daily
    WHERE date_key = 20250630
    GROUP BY ALL
)
SELECT p.product_name, s.units_sold, k.stock_end,
       round(k.stock_end / (s.units_sold / 30), 1) AS days_of_cover
FROM sales s
JOIN stock k       USING (product_key)
JOIN dim_product p USING (product_key)
ORDER BY days_of_cover
LIMIT 5;
```

Полный результат:

| product_name | units_sold | stock_end | days_of_cover |
|---|---|---|---|
| Скакалка | 73 | 64 | 26,3 |
| Трейловые кроссовки | 45 | 44 | 29,3 |
| Куртка-ветровка | 55 | 57 | 31,1 |
| Худи | 46 | 48 | 31,3 |
| Носки | 65 | 69 | 31,8 |

Скакалок хватит меньше чем на месяц. Пора заказывать.

</details>

### Задание 2. Выручка и запасы по магазинам

Для каждого магазина: выручка за июнь и стоимость остатков на 30 июня. Сколько рублей запаса приходится на рубль месячной выручки?

**Проверка:** 4 строки. У ТЦ Авиапарк `stock_per_revenue` меньше 1 — это 0,70.

<details>
<summary>Решение</summary>

```sql
WITH sales AS (
    SELECT store_key, sum(net_amount) AS revenue_june
    FROM fact_sales
    WHERE date_key BETWEEN 20250601 AND 20250630
    GROUP BY ALL
),
stock AS (
    SELECT store_key, sum(stock_value) AS stock_value
    FROM fact_inventory_daily
    WHERE date_key = 20250630
    GROUP BY ALL
)
SELECT s.store_name, x.revenue_june, k.stock_value,
       round(k.stock_value / x.revenue_june, 2) AS stock_per_revenue
FROM sales x
JOIN stock k     USING (store_key)
JOIN dim_store s USING (store_key)
ORDER BY s.store_name;
```

Полный результат:

| store_name | revenue_june | stock_value | stock_per_revenue |
|---|---|---|---|
| Казань Молл | 779 833 | 1 035 540 | 1,33 |
| Невский | 648 653 | 1 188 730 | 1,83 |
| Онлайн-магазин | 2 269 921 | 4 335 690 | 1,91 |
| ТЦ Авиапарк | 1 488 683 | 1 048 580 | 0,70 |

ТЦ Авиапарк продаёт быстрее всех: запаса меньше, чем на месяц продаж. Там же больше всего дней без товара (задание 2 из урока [Типы fact tables](/practice/modeling/fact-types/)).

</details>

### Задание 3. Shrunken dimension и агрегат

1. Создайте `dim_month` из `dim_date`: одна строка на месяц, ключ `month_key` вида `202501`.
2. Создайте агрегат `fact_sales_monthly`: месяц × магазин × категория, сумма выручки и штук.
3. Проверьте: общая выручка в агрегате равна выручке в `fact_sales`.

**Проверка:** в `dim_month` 12 строк. В агрегате 120 строк (6 месяцев × 4 магазина × 5 категорий). Выручка — 25 999 963 в обеих таблицах.

<details>
<summary>Решение</summary>

```sql
CREATE OR REPLACE TABLE dim_month AS
SELECT DISTINCT
    year * 100 + month AS month_key,
    year, quarter, month, month_name, year_month
FROM dim_date
WHERE date_key <> -1
ORDER BY month_key;

CREATE OR REPLACE TABLE fact_sales_monthly AS
SELECT d.year * 100 + d.month AS month_key,
       f.store_key,
       p.category_name,
       sum(f.quantity)   AS quantity,
       sum(f.net_amount) AS net_amount
FROM fact_sales f
JOIN dim_date    d ON d.date_key    = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY ALL;

SELECT (SELECT count(*) FROM dim_month)                   AS months,
       (SELECT count(*) FROM fact_sales_monthly)          AS agg_rows,
       (SELECT sum(net_amount) FROM fact_sales_monthly)   AS agg_revenue,
       (SELECT sum(net_amount) FROM fact_sales)           AS fact_revenue;
```

Атрибуты `dim_month` взяты из `dim_date`. Поэтому отчёт по агрегату и отчёт по детальному факту дадут одинаковые подписи и суммы. Агрегаты ускоряют дашборды. Но детальный факт остаётся: из агрегата нельзя получить выручку по товару.

</details>

### Задание 4

Маркетинг хочет добавить процесс «рассылка писем клиентам»: письмо отправлено, открыто, был клик. Добавьте строку в bus matrix. Какие измерения общие, а какие нужны новые?

<details>
<summary>Ответ</summary>

| Бизнес-процесс | Дата | Клиент | Товар | Магазин | Кампания |
|---|---|---|---|---|---|
| Рассылки (`fact_email_events`) | ✓ | ✓ | ✓ (если письмо про товар) | | ✓ новое |

- **Дата и клиент** — conformed. Используем те же `dim_date` и `dim_customer`. Тогда можно ответить: «покупают ли клиенты после письма?» (drill-across рассылок и продаж по клиенту и дате).
- **Кампания** — новое измерение: название, тема, канал.
- **Магазин** не нужен: письмо не связано с магазином.

</details>

## Итог

- Conformed dimension — одно измерение для многих фактов. Это основа интеграции.
- Bus matrix — карта процессов и общих измерений. С неё начинают проект хранилища.
- Drill-across: агрегируем каждый факт отдельно, потом соединяем. Прямой `JOIN` фактов даёт fan-out.
- Shrunken dimension и агрегаты ускоряют отчёты и остаются согласованными с деталями.

**Глубже:** [глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/) — bus architecture, bus matrix, conformed dimensions и facts. [Глава 18](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/) — как строить bus matrix вместе с бизнесом.

Дальше: [Другие подходы к моделированию](/practice/modeling/other-approaches/).
