---
title: SUM
description: Как складывать значения столбца с помощью SUM и как SUM ведёт себя с NULL.
sidebar:
  order: 3
tags:
  - sql
  - practice
---

`SUM` складывает все значения числового столбца. Работаем с таблицей `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

## Сумма по столбцу

```sql
SELECT SUM(volume) AS total_volume
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт одно число: сколько всего акций продали за все дни.

Можно считать несколько сумм сразу:

```sql
SELECT SUM(open) AS sum_open,
       SUM(close) AS sum_close
FROM tutorial.aapl_historical_stock_price;
```

## Правила SUM

- `SUM` работает только с числами. Для текста будет ошибка.
- `SUM` пропускает `NULL`. Он не считает их нулями, а просто не берёт в расчёт.
- Если все значения `NULL`, `SUM` вернёт `NULL`, а не 0.

```sql
SELECT SUM(funding_total_usd) AS total_funding
FROM tutorial.crunchbase_companies;
```

У 12785 компаний `funding_total_usd` равен `NULL`. Они в сумме не участвуют.

:::tip
Чтобы получить 0 вместо `NULL`, оберните сумму в `COALESCE(SUM(x), 0)`.
:::

:::caution
`SUM` складывает значения по столбцу. Чтобы сложить два столбца в одной строке, используйте `+`: `open + close`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Посчитайте среднюю цену открытия (`open`) без функции `AVG`. Используйте `SUM`, `COUNT` и деление.

**Проверка:** около 178.30.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(open) / COUNT(open) AS avg_open_price
FROM tutorial.aapl_historical_stock_price;
```

</details>

### Задание 2

Посчитайте, сколько всего инвестиций получили компании со статусом `ipo` в таблице `tutorial.crunchbase_companies`.

**Проверка:** 209961181618.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(funding_total_usd) AS ipo_funding
FROM tutorial.crunchbase_companies
WHERE status = 'ipo';
```

</details>
