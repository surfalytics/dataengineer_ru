---
title: "Агрегатные функции"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Агрегатные функции в SQL: обзор | Инжиниринг Данных"
description: "Введение в средний уровень SQL и обзор агрегатных функций COUNT, SUM, MIN, MAX и AVG."
sidebar:
  order: 1
tags:
  - sql
  - practice
---

Средний уровень SQL учит считать итоги по данным и соединять таблицы. Первые уроки используют таблицу `tutorial.aapl_historical_stock_price`. Это дневные цены акций Apple за 2000–2014 годы.

Задачи здесь сложнее, чем на базовом уровне. У многих задач есть несколько верных решений. Решение из курса — это пример, а не единственный ответ.

## Что такое агрегатная функция

Агрегатная функция берёт много строк и возвращает одно значение. Она считает итог по столбцу.

| Функция | Что делает |
|---|---|
| `COUNT` | Считает строки |
| `SUM` | Складывает значения |
| `MIN` | Находит наименьшее значение |
| `MAX` | Находит наибольшее значение |
| `AVG` | Считает среднее |

Это то же самое, что сводная таблица в Excel. Каждой функции посвящён отдельный урок.

## Строки и столбцы

Арифметические операторы работают внутри одной строки:

```sql
SELECT date,
       close - open AS day_change
FROM tutorial.aapl_historical_stock_price
LIMIT 5;
```

Агрегатные функции работают по столбцу, то есть по многим строкам сразу:

```sql
SELECT COUNT(*) AS rows_count,
       MIN(low) AS lowest_price,
       MAX(high) AS highest_price,
       AVG(close) AS avg_close
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт одну строку.

:::note
Агрегатные функции пропускают `NULL`. Подробности — в уроках про [COUNT](/practice/sql/intermediate/count/) и [AVG](/practice/sql/intermediate/avg/).
:::

:::caution
Нельзя смешивать в `SELECT` обычный столбец и агрегатную функцию без `GROUP BY`. Например, `SELECT date, MAX(high)` вернёт ошибку. Это тема урока про [GROUP BY](/practice/sql/intermediate/group-by/).
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите один запрос, который вернёт: число строк в таблице, первую дату и последнюю дату.

**Проверка:** одна строка: 3773 строки, первая дата 2000-01-03, последняя 2014-12-31.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_count,
       MIN(date) AS first_date,
       MAX(date) AS last_date
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 2

Напишите один запрос, который вернёт самую низкую цену `low` и самую высокую цену `high` за всё время.

**Проверка:** минимум 12.72, максимум 705.07.

<details>
<summary>Решение</summary>

```sql
SELECT MIN(low) AS lowest_price,
       MAX(high) AS highest_price
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 3

Напишите запрос, который посчитает общее число проданных акций (`volume`) и среднюю цену закрытия (`close`).

**Проверка:** сумма `volume` — 72665719900.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(volume) AS total_volume,
       AVG(close) AS avg_close
FROM tutorial.aapl_historical_stock_price;
```

</details>
