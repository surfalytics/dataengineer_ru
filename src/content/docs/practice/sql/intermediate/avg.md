---
title: "AVG"
description: "Как считать среднее значение с помощью AVG и почему NULL влияет на результат."
sidebar:
  order: 5
tags:
  - sql
  - practice
---

`AVG` считает среднее значение столбца. Работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`.

## Среднее по столбцу

```sql
SELECT AVG(high) AS avg_high
FROM tutorial.aapl_historical_stock_price;
```

`AVG` работает только с числами. Для текста будет ошибка.

## AVG и NULL

`AVG` пропускает `NULL`. Он делит сумму на число **непустых** значений. Это важно: `NULL` не равен нулю.

```sql
SELECT AVG(funding_total_usd) AS avg_funding,
       SUM(funding_total_usd) / COUNT(*) AS wrong_avg
FROM tutorial.crunchbase_companies;
```

| avg_funding | wrong_avg |
|---|---|
| 18478604 | 14918922 |

Второе число меньше. Оно делит сумму на все 66368 компаний, в том числе на тех, у кого нет данных.

:::caution
Перед тем как считать среднее, решите: пустое значение — это «неизвестно» или «ноль»? От ответа зависит результат. Если «ноль», используйте `AVG(COALESCE(x, 0))`.
:::

:::tip
`AVG` по столбцу целых чисел в DuckDB возвращает дробное число. В некоторых базах результат округляется до целого. Если сомневаетесь, приведите значение: `AVG(x::DOUBLE)`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который посчитает средний дневной объём торгов (`volume`) акций Apple.

**Проверка:** около 19259400.98.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(volume) AS avg_volume
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 2

Посчитайте среднюю цену закрытия (`close`) только за 2014 год.

**Проверка:** около 295.40.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(close) AS avg_close_2014
FROM tutorial.aapl_historical_stock_price
WHERE year = 2014;
```

</details>

### Задание 3

Посчитайте, сколько в среднем денег получили компании в таблице `tutorial.crunchbase_companies`, у которых `funding_total_usd` не `NULL`. Сравните с `AVG(COALESCE(funding_total_usd, 0))`.

**Проверка:** первое число около 18478604, второе около 14918922.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(funding_total_usd) AS avg_known,
       AVG(COALESCE(funding_total_usd, 0)) AS avg_zero
FROM tutorial.crunchbase_companies;
```

</details>
