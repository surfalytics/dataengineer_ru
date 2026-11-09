---
title: "GROUP BY"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "GROUP BY в SQL: группировка и итоги | Инжиниринг Данных"
description: "Как считать итоги по группам с помощью GROUP BY и какие правила нужно помнить."
sidebar:
  order: 6
tags:
  - sql
  - practice
---

`GROUP BY` делит строки на группы и считает агрегат для каждой группы. Без него агрегатная функция даёт один итог на всю таблицу. Здесь работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`.

## Итоги по группам

Сколько акций торговали в каждом году:

```sql
SELECT year,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

Запрос вернёт по одной строке на каждый год.

## Несколько столбцов в группе

Можно группировать по нескольким столбцам. Группа — это каждая уникальная пара значений:

```sql
SELECT year,
       month,
       COUNT(*) AS trading_days
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
ORDER BY year, month;
```

Вместо имён столбцов можно писать номера из `SELECT`:

```sql
SELECT year,
       month,
       COUNT(*) AS trading_days
FROM tutorial.aapl_historical_stock_price
GROUP BY 1, 2
ORDER BY 1, 2;
```

:::note
`GROUP BY 1, 2` работает в DuckDB, Postgres и в большинстве баз. Но номера хуже читаются. Если запрос длинный, лучше писать имена.
:::

## Главное правило

Каждый столбец в `SELECT` должен быть либо в `GROUP BY`, либо внутри агрегатной функции.

```sql
-- ошибка: month не в GROUP BY и не в агрегате
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year;
```

:::tip
В DuckDB есть сокращение `GROUP BY ALL`. Оно группирует по всем столбцам `SELECT`, которые не агрегаты. Это удобно, но в других базах не работает.
:::

## Порядок частей запроса

`SELECT` → `FROM` → `WHERE` → `GROUP BY` → `ORDER BY`. `WHERE` фильтрует строки до группировки.

```sql
SELECT status,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE country_code = 'USA'
GROUP BY status
ORDER BY companies DESC;
```

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Посчитайте, сколько всего акций торговали каждый месяц. Отсортируйте результат по времени.

**Проверка:** 180 строк. Первая строка: 2000, 1, 112099800.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
ORDER BY year, month;
```

</details>

### Задание 2

Напишите запрос, который посчитает среднее дневное изменение цены акции Apple (`close - open`) по годам.

**Проверка:** 15 строк. В 2000 году среднее изменение около -0.115.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       AVG(close - open) AS avg_daily_change
FROM tutorial.aapl_historical_stock_price
GROUP BY 1
ORDER BY 1;
```

</details>

### Задание 3

Напишите запрос, который найдёт самую низкую и самую высокую цену акции Apple за каждый месяц.

**Проверка:** 180 строк. Первая строка: 2000, 1, 86.5, 121.5.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       MIN(low) AS lowest_price,
       MAX(high) AS highest_price
FROM tutorial.aapl_historical_stock_price
GROUP BY 1, 2
ORDER BY 1, 2;
```

</details>

### Задание 4

Посчитайте компании в `tutorial.crunchbase_companies` по статусам (`status`). Сначала самый частый статус.

**Проверка:** 4 строки. Первая: `operating`, 53034.

<details>
<summary>Решение</summary>

```sql
SELECT status,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
GROUP BY status
ORDER BY companies DESC;
```

</details>
