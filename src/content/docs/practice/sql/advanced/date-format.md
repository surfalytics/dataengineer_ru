---
title: "Формат дат и времени"
description: "Почему даты пишут год первым, как считать разницу между датами и добавлять интервалы в DuckDB."
sidebar:
  order: 2
tags:
  - sql
  - practice
---

Даты в SQL часто приходят в плохом виде: как текст, в разных форматах. Если не привести их к `DATE` или `TIMESTAMP`, сортировка и расчёты будут неверными.

В этом уроке работаем с таблицами `tutorial.crunchbase_companies_clean_date` и `tutorial.crunchbase_acquisitions_clean_date`.

## Почему год идёт первым

Американский формат `М/Д/ГГ` (например `9/4/14`) удобен человеку. Но как текст он не сортируется по времени. Текст сравнивается по символам слева направо.

```sql
SELECT permalink,
       founded_at
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at IS NOT NULL
ORDER BY founded_at
LIMIT 5;
```

Первыми придут строки, которые начинаются с `1/1/00`. Потом `1/1/01`... Но `1/30/15` будет раньше, чем `2/1/05`. Порядок неверный.

Формат `ГГГГ-ММ-ДД` решает проблему. Текст в этом формате сортируется так же, как даты:

```sql
SELECT permalink,
       founded_at,
       founded_at_clean
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at IS NOT NULL
ORDER BY founded_at_clean
LIMIT 5;
```

:::note
Колонка `founded_at_clean` в нашей базе содержит и странные годы. Например `1015-01-30`. Это ошибка в исходных данных (двузначный год `15` разобран неверно). Такие строки лучше фильтровать.
:::

## Арифметика с датами

Разница двух дат или timestamp — это тип `INTERVAL`. Колонка `founded_at_clean` это текст. Поэтому сначала приведите её к `TIMESTAMP`.

Сколько времени прошло от основания до продажи компании:

```sql
SELECT companies.permalink,
       companies.founded_at_clean,
       acquisitions.acquired_at_cleaned,
       acquisitions.acquired_at_cleaned - companies.founded_at_clean::TIMESTAMP AS time_to_acquisition
FROM tutorial.crunchbase_companies_clean_date companies
JOIN tutorial.crunchbase_acquisitions_clean_date acquisitions
  ON acquisitions.company_permalink = companies.permalink
WHERE companies.founded_at_clean IS NOT NULL;
```

Результат — интервал в днях, например `1336 days`.

## INTERVAL

Интервал можно записать словами: `'1 week'`, `'3 years'`, `'10 seconds'`. Дата плюс интервал даёт новую дату:

```sql
SELECT permalink,
       founded_at_clean,
       founded_at_clean::TIMESTAMP + INTERVAL '1 week' AS plus_one_week
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

## Текущее время

`now()` возвращает текущий момент:

```sql
SELECT permalink,
       founded_at_clean,
       now() - founded_at_clean::TIMESTAMP AS founded_time_ago
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

Результат зависит от дня запуска. Это нормально.

## Полезные функции DuckDB

| Задача | DuckDB | Результат |
|---|---|---|
| Формат даты в текст | `strftime(d, '%d.%m.%Y')` | `05.03.2014` |
| Часть даты | `date_part('year', d)` или `EXTRACT(year FROM d)` | `2014` |
| Разница в днях | `date_diff('day', d1, d2)` | `59` |
| Разница «как у человека» | `age(d2, d1)` | `2 years 1 month 17 days` |
| Начало месяца | `date_trunc('month', d)` | `2014-03-01` |
| Текст в дату | `strptime('03/05/2014', '%m/%d/%Y')` | `2014-03-05` |

```sql
SELECT strftime(DATE '2014-03-05', '%d.%m.%Y') AS formatted,
       date_part('year', DATE '2014-03-05') AS year,
       date_diff('day', DATE '2014-01-01', DATE '2014-03-01') AS days,
       age(DATE '2014-03-01', DATE '2012-01-15') AS human_age,
       date_trunc('month', DATE '2014-03-05') AS month_start;
```

:::note
В Postgres для формата даты используют `TO_CHAR(d, 'DD.MM.YYYY')`. В DuckDB такой функции нет. Используйте `strftime`. Коды формата другие: `%Y` год, `%m` месяц, `%d` день, `%H` час, `%M` минуты.
:::

:::tip
Хотите дату плюс 7 дней? `d::DATE + 7` работает в DuckDB и Postgres. Для месяцев и лет используйте `INTERVAL`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который считает компании, проданные в течение 3, 5 и 10 лет после основания. Каждый срок — в отдельной колонке. Добавьте колонку с общим числом проданных компаний. Группируйте по `category_code`. Берите только компании с датой основания. Покажите сначала категории с самым большим общим числом.

**Проверка:** 331 строка. Первая строка: `software` — 44, 92, 270 и всего 470.

<details>
<summary>Решение</summary>

```sql
SELECT companies.category_code,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '3 years'
                  THEN 1 END) AS acquired_3_yrs,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '5 years'
                  THEN 1 END) AS acquired_5_yrs,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '10 years'
                  THEN 1 END) AS acquired_10_yrs,
       COUNT(1) AS total
FROM tutorial.crunchbase_companies_clean_date companies
JOIN tutorial.crunchbase_acquisitions_clean_date acquisitions
  ON acquisitions.company_permalink = companies.permalink
WHERE companies.founded_at_clean IS NOT NULL
GROUP BY 1
ORDER BY 5 DESC;
```

</details>
