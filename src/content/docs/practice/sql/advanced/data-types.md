---
title: Типы данных
description: Какие типы данных бывают в SQL и как менять тип колонки с помощью CAST и оператора ::.
sidebar:
  order: 1
tags:
  - sql
  - practice
---

Это первый урок продвинутого уровня. Дальше будут типы данных, даты, строки, подзапросы, оконные функции, скорость запросов и сводные таблицы.

Работаем так же, как раньше: сначала смотрите данные через `SELECT * ... LIMIT 10`, потом пишете запрос. Все примеры используют данные Crunchbase и других таблиц из [описания данных](/practice/sql/datasets/). В этом уроке берём `tutorial.crunchbase_companies_clean_date`.

Тема урока: у каждой колонки есть тип. Тип решает, какие функции работают. Если тип не тот, запрос упадёт. Тогда тип нужно поменять прямо в запросе.

## Основные типы

| Тип | Что хранит | Пример |
|---|---|---|
| `VARCHAR` | Текст любой длины | `'software'` |
| `INTEGER`, `BIGINT` | Целые числа | `42` |
| `DOUBLE` | Дробные числа | `37.78` |
| `DECIMAL(p, s)` | Точные дробные числа (деньги) | `19.99` |
| `BOOLEAN` | `TRUE` или `FALSE` | `TRUE` |
| `DATE` | Дата | `2014-03-01` |
| `TIMESTAMP` | Дата и время | `2014-03-01 13:45:00` |

Посмотреть типы таблицы можно так:

```sql
DESCRIBE tutorial.crunchbase_companies_clean_date;
```

Тип одного значения покажет `typeof`:

```sql
SELECT typeof(funding_total_usd) AS funding_type,
       typeof(founded_at_clean) AS founded_type
FROM tutorial.crunchbase_companies_clean_date
LIMIT 1;
```

Здесь `funding_total_usd` это `BIGINT`, а `founded_at_clean` это `VARCHAR`. Дата хранится как текст.

## Почему тип важен

- `COUNT` работает с любым типом.
- `SUM` и `AVG` работают только с числами.
- Дату в виде текста нельзя сложить с интервалом без приведения типа.

Пример ошибки. Колонка `founded_at_clean` это текст:

```sql
-- ошибка
SELECT SUM(founded_at_clean)
FROM tutorial.crunchbase_companies_clean_date;
```

:::caution
Число с запятой или знаком валюты (`'1,000'`, `'$5'`) база не считает числом. Это текст. Сначала уберите лишние символы через `REPLACE`, потом меняйте тип.
:::

## Как поменять тип: CAST и ::

Есть два способа. Результат одинаковый.

```sql
SELECT CAST(funding_total_usd AS VARCHAR) AS funding_total_usd_string,
       founded_at_clean::VARCHAR AS founded_at_string
FROM tutorial.crunchbase_companies_clean_date;
```

- `CAST(значение AS тип)` — стандарт SQL. Работает везде.
- `значение::тип` — короткая запись. Работает в DuckDB и Postgres.

Можно менять тип и в другую сторону. Все значения колонки должны подходить к новому типу:

```sql
SELECT permalink,
       founded_at_clean::DATE AS founded_date
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

## TRY_CAST

Если одно значение не подходит, `CAST` роняет весь запрос. `TRY_CAST` вместо ошибки вернёт `NULL`:

```sql
SELECT TRY_CAST('1,000' AS INTEGER) AS bad_value,
       TRY_CAST('1000' AS INTEGER) AS good_value;
```

:::tip
`TRY_CAST` удобен, когда в колонке с числами есть мусор. Потом посчитайте, сколько `NULL` получилось. Так вы поймёте, сколько данных грязные.
:::

:::note
Деление в DuckDB: `7 / 2` даёт `3.5`. В Postgres `7 / 2` даёт `3`, потому что оба числа целые. Целое деление в DuckDB пишется `7 // 2`. Если переносите запрос из Postgres, проверьте деление.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

В таблице `tutorial.crunchbase_companies_clean_date` приведите `funding_total_usd` к тексту. Посчитайте компании, у которых в записи 9 и больше цифр.

**Проверка:** 1666.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
WHERE LENGTH(CAST(funding_total_usd AS VARCHAR)) >= 9;
```

</details>

### Задание 2

Приведите `founded_at_clean` к типу `DATE`. Посчитайте компании, основанные в 2010 году. Используйте сравнение дат, а не колонку `founded_year`.

**Проверка:** 4253.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean::DATE >= '2010-01-01'
  AND founded_at_clean::DATE < '2011-01-01';
```

</details>

### Задание 3

В таблице `tutorial.sf_crime_incidents_2014_01` номер инцидента `incidnt_num` это число. Превратите его в текст и возьмите первые 2 символа. Посчитайте, сколько инцидентов на каждое значение. Покажите сначала самое частое.

**Проверка:** 3 строки. Первая: `14` — 11879 инцидентов.

<details>
<summary>Решение</summary>

```sql
SELECT LEFT(incidnt_num::VARCHAR, 2) AS prefix,
       COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
GROUP BY 1
ORDER BY 2 DESC;
```

</details>
