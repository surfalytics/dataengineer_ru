---
title: "HAVING"
description: "Как фильтровать результат группировки с помощью HAVING и чем он отличается от WHERE."
sidebar:
  order: 7
tags:
  - sql
  - practice
---

`HAVING` фильтрует группы после `GROUP BY`. Он нужен, когда условие зависит от агрегата, например «только группы, где больше 1000 строк». Работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`.

## Почему не WHERE

`WHERE` работает до группировки, когда агрегатов ещё нет. Условие с агрегатной функцией в `WHERE` вызовет ошибку.

```sql
-- ошибка: агрегат нельзя использовать в WHERE
SELECT year,
       month,
       MAX(high) AS month_high
FROM tutorial.aapl_historical_stock_price
WHERE MAX(high) > 400
GROUP BY year, month;
```

`HAVING` стоит после `GROUP BY`. Он видит уже посчитанные агрегаты:

```sql
SELECT year,
       month,
       MAX(high) AS month_high
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
HAVING MAX(high) > 400
ORDER BY year, month;
```

Запрос вернёт 35 месяцев, где цена хотя бы раз поднималась выше 400.

| | WHERE | HAVING |
|---|---|---|
| Когда работает | До `GROUP BY` | После `GROUP BY` |
| Что фильтрует | Строки | Группы |
| Агрегаты в условии | Нельзя | Можно |

## Порядок частей запроса

1. `SELECT`
2. `FROM`
3. `WHERE`
4. `GROUP BY`
5. `HAVING`
6. `ORDER BY`

Пишите части запроса именно в таком порядке.

## WHERE и HAVING вместе

`WHERE` убирает ненужные строки заранее. `HAVING` отбирает группы. Так запрос работает быстрее.

```sql
SELECT category_code,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE country_code = 'USA'
GROUP BY category_code
HAVING COUNT(*) >= 500
ORDER BY companies DESC;
```

:::note
В DuckDB в `HAVING` можно использовать псевдоним: `HAVING companies >= 500`. В Postgres это не работает, нужно повторить выражение: `HAVING COUNT(*) >= 500`.
:::

:::tip
`HAVING` — не единственный способ. Фильтровать итоги можно ещё через подзапрос. О нём будет отдельный урок.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Найдите годы, когда средний дневной объём торгов (`volume`) акций Apple был больше 35 миллионов. Покажите год и среднее значение.

**Проверка:** 2 строки: 2007 и 2008.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       AVG(volume) AS avg_volume
FROM tutorial.aapl_historical_stock_price
GROUP BY year
HAVING AVG(volume) > 35000000
ORDER BY year;
```

</details>

### Задание 2

Покажите категории (`category_code`) компаний из `tutorial.crunchbase_companies`, в которых не меньше 1000 компаний. Не включайте компании без категории. Отсортируйте от большей категории к меньшей.

**Проверка:** 16 строк. Первая: `biotechnology`, 4468.

<details>
<summary>Решение</summary>

```sql
SELECT category_code,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE category_code IS NOT NULL
GROUP BY category_code
HAVING COUNT(*) >= 1000
ORDER BY companies DESC;
```

</details>

### Задание 3

Посчитайте суммарный объём торгов по месяцам 2014 года. Оставьте месяцы, где сумма больше 500 миллионов акций.

**Проверка:** 7 строк, с июня по декабрь. Для июня: 853087800.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
WHERE year = 2014
GROUP BY year, month
HAVING SUM(volume) > 500000000
ORDER BY month;
```

</details>
