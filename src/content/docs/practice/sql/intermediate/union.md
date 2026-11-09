---
title: "UNION"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "UNION и UNION ALL в SQL | Инжиниринг Данных"
description: "Как объединять результаты двух запросов в один список с помощью UNION и UNION ALL."
sidebar:
  order: 17
tags:
  - sql
  - practice
---

`JOIN` добавляет столбцы из другой таблицы. `UNION` добавляет **строки**. Он ставит результат одного запроса под результатом другого. Работаем с таблицами `tutorial.crunchbase_investments_part1` и `tutorial.crunchbase_investments_part2`. Это две половины таблицы инвестиций Crunchbase: первая содержит компании на буквы от A до L, вторая — от M до Z.

## UNION

```sql
SELECT *
FROM tutorial.crunchbase_investments_part1

UNION

SELECT *
FROM tutorial.crunchbase_investments_part2;
```

`UNION` убирает полные дубликаты. Если строка из второго запроса точно совпадает со строкой из первого, останется одна.

## UNION ALL

`UNION ALL` оставляет все строки, ничего не убирает.

```sql
SELECT *
FROM tutorial.crunchbase_investments_part1

UNION ALL

SELECT *
FROM tutorial.crunchbase_investments_part2;
```

Проверим на наших данных:

| Запрос | Число строк |
|---|---|
| `UNION ALL` | 168647 |
| `UNION` | 168591 |

Разница в 56 строк — полные дубликаты внутри данных. `UNION` их убрал.

:::tip
`UNION ALL` быстрее: база не ищет дубликаты. Используйте его по умолчанию. `UNION` нужен только если дубликаты точно нужно убрать.
:::

## Правила UNION

- В обоих запросах одинаковое число столбцов.
- Типы данных столбцов совпадают и идут в одном порядке.
- Имена столбцов берутся из первого запроса. Совпадение имён не обязательно, но обычно имена совпадают.

Каждый `SELECT` пишется отдельно. Поэтому можно по-разному фильтровать части:

```sql
SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part1
WHERE company_name ILIKE 'A%'

UNION ALL

SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part2
WHERE company_name ILIKE 'Z%';
```

:::note
`ILIKE` есть в DuckDB и Postgres. Без него используйте `LOWER(company_name) LIKE 'a%'`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Объедините две таблицы инвестиций через `UNION ALL`, сохранив дубликаты. Из первой таблицы возьмите компании с названием на букву D, из второй — на букву T (без учёта регистра). Оставьте столбцы `company_permalink`, `company_name` и `investor_name`.

В оригинальном курсе брали буквы T и M. В наших данных первая часть содержит A–L, а вторая M–Z. Поэтому мы выбрали D и T.

**Проверка:** 15710 строк (5680 из первой части и 10030 из второй).

<details>
<summary>Решение</summary>

```sql
SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part1
WHERE company_name ILIKE 'D%'

UNION ALL

SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part2
WHERE company_name ILIKE 'T%';
```

</details>

### Задание 2

Напишите запрос с тремя столбцами. Первый — из какой части данные (`investments_part1` или `investments_part2`). Второй — статус компании. Третий — число уникальных инвесторов. Подсказка: понадобится таблица `tutorial.crunchbase_companies` и группировка по статусу и части данных.

**Проверка:** 8 строк (4 статуса на 2 части). Для `investments_part1`: `acquired` — 3955, `closed` — 3060, `ipo` — 1226, `operating` — 16912.

<details>
<summary>Решение</summary>

```sql
SELECT 'investments_part1' AS dataset_name,
       companies.status,
       COUNT(DISTINCT investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1, 2

UNION ALL

SELECT 'investments_part2' AS dataset_name,
       companies.status,
       COUNT(DISTINCT investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part2 investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1, 2
ORDER BY 1, 2;
```

</details>
