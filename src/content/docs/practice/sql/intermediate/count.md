---
title: "COUNT"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "COUNT в SQL: подсчёт строк | Инжиниринг Данных"
description: "Как считать строки с помощью COUNT, чем COUNT(*) отличается от COUNT(столбец) и как NULL влияет на результат."
sidebar:
  order: 2
tags:
  - sql
  - practice
---

`COUNT` считает строки. Это самая простая агрегатная функция, и результат легко проверить. В этом уроке работаем с `tutorial.aapl_historical_stock_price` и с `tutorial.crunchbase_companies`.

## Считаем все строки

```sql
SELECT COUNT(*)
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт 3773. Это число всех строк. `COUNT(1)` даёт тот же результат. Какой вариант выбрать — дело вкуса.

## Считаем один столбец

`COUNT(столбец)` считает только строки, где значение **не `NULL`**.

```sql
SELECT COUNT(*) AS all_rows,
       COUNT(homepage_url) AS with_homepage
FROM tutorial.crunchbase_companies;
```

| all_rows | with_homepage |
|---|---|
| 66368 | 61310 |

У 5058 компаний сайт не указан. Это строки, где `homepage_url` равен `NULL`.

:::tip
Разница `COUNT(*) - COUNT(столбец)` — быстрый способ узнать, сколько в столбце `NULL`. Это частый шаг при проверке качества данных.
:::

## Не только числа

`COUNT` работает и для текста, и для дат:

```sql
SELECT COUNT(date) AS count_of_date
FROM tutorial.aapl_historical_stock_price;
```

`COUNT` считает непустые строки, а не разные значения. Для разных значений нужен `COUNT(DISTINCT ...)`. Он описан в [уроке про DISTINCT](/practice/sql/intermediate/distinct/).

## Имена столбцов

Без псевдонима столбец называется `count_star()`. Дайте ему понятное имя через `AS`. Пишите строчными буквами и с `_`.

```sql
SELECT COUNT(date) AS "Count Of Date"
FROM tutorial.aapl_historical_stock_price;
```

Если нужны пробелы, берите двойные кавычки. Лучше обойтись без них.

:::note
В DuckDB `COUNT(*)` называется `count_star()` в заголовке результата. В Postgres это `count`. На запрос это не влияет.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который посчитает непустые значения в каждом столбце таблицы `tutorial.aapl_historical_stock_price`: `year`, `month`, `open`, `high`, `low`, `close`, `volume`. По этим числам определите, в каком столбце больше всего `NULL`.

**Проверка:** в каждом столбце 3773. В наших данных `NULL` нет ни в одном столбце.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(year) AS year,
       COUNT(month) AS month,
       COUNT(open) AS open,
       COUNT(high) AS high,
       COUNT(low) AS low,
       COUNT(close) AS close,
       COUNT(volume) AS volume
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 2

В таблице `tutorial.crunchbase_companies` посчитайте компании, у которых заполнено `funding_total_usd`.

**Проверка:** 53583.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(funding_total_usd) AS companies_with_funding
FROM tutorial.crunchbase_companies;
```

</details>

### Задание 3

Одним запросом посчитайте, сколько в `tutorial.crunchbase_companies` компаний без `category_code`. Не используйте `WHERE`.

**Проверка:** 3148.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) - COUNT(category_code) AS no_category
FROM tutorial.crunchbase_companies;
```

</details>
