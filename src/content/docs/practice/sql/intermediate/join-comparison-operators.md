---
title: "JOIN с операторами сравнения"
description: "Как использовать в ON не только равенство, но и операторы сравнения, и чем это отличается от фильтра в WHERE."
sidebar:
  order: 18
tags:
  - sql
  - practice
---

Условие в `ON` необязательно должно быть равенством. Можно использовать `>`, `<`, `>=`, `<=`, `<>`. Так удобно соединять строки по диапазонам, например по датам. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments_part1`.

## Условие сравнения в ON

Посчитаем для каждой компании инвестиции, сделанные позже чем через 5 лет после основания:

```sql
SELECT companies.permalink,
       companies.name,
       companies.status,
       COUNT(investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND investments.funded_year > companies.founded_year + 5
GROUP BY 1, 2, 3;
```

Здесь в `ON` два условия:

- Равенство ключей: `companies.permalink = investments.company_permalink`.
- Сравнение лет: `investments.funded_year > companies.founded_year + 5`.

Присоединяются только те инвестиции, которые подходят под оба условия. Компании без таких инвестиций остаются в результате с нулём.

## То же условие в WHERE

Результат будет другим, если поставить сравнение в `WHERE`:

```sql
SELECT companies.permalink,
       companies.name,
       companies.status,
       COUNT(investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
WHERE investments.funded_year > companies.founded_year + 5
GROUP BY 1, 2, 3;
```

`WHERE` работает после соединения. Он убирает все компании, у которых нет подходящих инвестиций.

| Вариант | Число строк |
|---|---|
| Условие в `ON` | 66368 (все компании) |
| Условие в `WHERE` | 4216 (только компании с подходящими инвестициями) |

Сумма в столбце `investors` в обоих случаях одинакова: 15864. Но в первом запросе есть все компании, а во втором — только часть.

Подробнее об этом — в уроке [Фильтр в WHERE или в ON](/practice/sql/intermediate/joins-where-vs-on/).

:::caution
`founded_year` в наших данных иногда «грязный»: есть значения вроде 1015 и 2914. Для учебных запросов это не мешает, но в работе такие значения надо чистить.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments` по ключу и по условию: год инвестиции равен году основания компании (`funded_year = founded_year`). Используйте `INNER JOIN` и посчитайте строки.

**Проверка:** 19197.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS investments_in_founding_year
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
 AND investments.funded_year = companies.founded_year;
```

</details>

### Задание 2

Посчитайте число строк в запросе из урока, где условие `funded_year > founded_year + 5` стоит в `ON`, и в запросе, где оно стоит в `WHERE`. Используйте `tutorial.crunchbase_investments_part1`. Объясните разницу.

**Проверка:** 66368 и 4216.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_on
FROM (
  SELECT companies.permalink
  FROM tutorial.crunchbase_companies companies
  LEFT JOIN tutorial.crunchbase_investments_part1 investments
    ON companies.permalink = investments.company_permalink
   AND investments.funded_year > companies.founded_year + 5
  GROUP BY companies.permalink
) t;

SELECT COUNT(*) AS rows_where
FROM (
  SELECT companies.permalink
  FROM tutorial.crunchbase_companies companies
  LEFT JOIN tutorial.crunchbase_investments_part1 investments
    ON companies.permalink = investments.company_permalink
  WHERE investments.funded_year > companies.founded_year + 5
  GROUP BY companies.permalink
) t;
```

</details>

### Задание 3

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` по ключу и по условию: покупка случилась не позже чем через год после основания (`acquired_year <= founded_year + 1`). Посчитайте строки.

**Проверка:** 265.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS quick_acquisitions
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND acquisitions.acquired_year <= companies.founded_year + 1;
```

</details>
