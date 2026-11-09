---
title: "DISTINCT"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "DISTINCT в SQL: уникальные значения | Инжиниринг Данных"
description: "Как находить уникальные значения с помощью DISTINCT и COUNT(DISTINCT)."
sidebar:
  order: 9
tags:
  - sql
  - practice
---

`DISTINCT` убирает повторы. Он нужен, когда надо узнать, какие значения есть в столбце, или посчитать уникальные значения. Работаем с `tutorial.aapl_historical_stock_price`.

## Уникальные значения

```sql
SELECT DISTINCT month
FROM tutorial.aapl_historical_stock_price
ORDER BY month;
```

Запрос вернёт 12 строк, по одной на каждый месяц.

## DISTINCT для нескольких столбцов

`DISTINCT` действует на **всю строку** результата. Он убирает только те строки, которые полностью совпадают.

```sql
SELECT DISTINCT year, month
FROM tutorial.aapl_historical_stock_price
ORDER BY year, month;
```

Запрос вернёт 180 строк: каждая пара «год и месяц» встречается один раз.

:::caution
`DISTINCT(month)` с круглыми скобками работает так же, как `DISTINCT month`. Скобки ничего не меняют. Новички часто думают, что `DISTINCT` применяется только к одному столбцу. Это не так.
:::

## COUNT(DISTINCT ...)

`COUNT(DISTINCT x)` считает уникальные значения:

```sql
SELECT COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price;
```

Результат: 12.

В сочетании с `GROUP BY` можно считать уникальные значения по группам. В следующем примере база считает уникальные месяцы для каждого года.

```sql
SELECT year,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

:::caution
`DISTINCT` на большой таблице работает медленно. Базе нужно сравнить много строк. Если можно обойтись `GROUP BY` или фильтром, лучше так. На собеседовании об этом часто спрашивают.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт уникальные значения столбца `year` в хронологическом порядке.

**Проверка:** 15 строк, от 2000 до 2014.

<details>
<summary>Решение</summary>

```sql
SELECT DISTINCT year
FROM tutorial.aapl_historical_stock_price
ORDER BY year;
```

</details>

### Задание 2

Напишите запрос, который посчитает число уникальных значений `month` для каждого года.

**Проверка:** 15 строк. В каждом году 12 месяцев.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

</details>

### Задание 3

Напишите запрос, который отдельно посчитает число уникальных значений `month` и число уникальных значений `year`.

**Проверка:** одна строка: годов 15, месяцев 12.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT year) AS years_count,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price;
```

</details>
