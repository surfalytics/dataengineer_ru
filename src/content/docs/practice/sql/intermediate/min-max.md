---
title: MIN и MAX
description: Как находить наименьшее и наибольшее значение с помощью MIN и MAX, в том числе для текста и дат.
sidebar:
  order: 4
tags:
  - sql
  - practice
---

`MIN` возвращает наименьшее значение столбца. `MAX` возвращает наибольшее. В этом уроке работаем с `tutorial.aapl_historical_stock_price`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

## MIN и MAX для чисел

```sql
SELECT MIN(volume) AS min_volume,
       MAX(volume) AS max_volume
FROM tutorial.aapl_historical_stock_price;
```

Обе функции пропускают `NULL`.

## MIN и MAX не только для чисел

Для текста `MIN` берёт первое значение по алфавиту, `MAX` — последнее. Для дат `MIN` — самая ранняя, `MAX` — самая поздняя.

```sql
SELECT MIN(date) AS first_day,
       MAX(date) AS last_day
FROM tutorial.aapl_historical_stock_price;
```

```sql
SELECT MIN(name) AS first_name,
       MAX(name) AS last_name
FROM tutorial.crunchbase_companies;
```

## Выражения внутри функций

Внутри `MAX` можно считать арифметику по строке. Сначала база считает выражение для каждой строки, потом берёт максимум:

```sql
SELECT MAX(high - low) AS max_day_range
FROM tutorial.aapl_historical_stock_price;
```

:::tip
Чтобы узнать, в какую **дату** случился максимум, одного `MAX` мало. Используйте `ORDER BY ... DESC LIMIT 1`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Каким был самый большой рост цены акции Apple за один день (`close - open`)?

**Проверка:** около 30.76.

<details>
<summary>Решение</summary>

```sql
SELECT MAX(close - open) AS max_day_increase
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 2

Какой была самая низкая цена акции Apple (столбец `low`) за период, который есть в данных?

**Проверка:** 12.72.

<details>
<summary>Решение</summary>

```sql
SELECT MIN(low) AS lowest_price
FROM tutorial.aapl_historical_stock_price;
```

</details>
