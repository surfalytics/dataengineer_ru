---
title: "Подзапросы"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Подзапросы в SQL: примеры и задачи | Инжиниринг Данных"
description: "Как писать вложенные запросы: подзапрос в FROM, в WHERE, подзапросы в JOIN и в UNION."
sidebar:
  order: 5
tags:
  - sql
  - practice
---

Подзапрос (вложенный запрос) — это запрос внутри другого запроса. Он нужен, когда задачу нельзя решить за один шаг. Например: сначала посчитать суммы, потом усреднить их.

Работаем с таблицами `tutorial.sf_crime_incidents_2014_01`, `tutorial.sf_crime_incidents_cleandate` и таблицами Crunchbase.

## Основы

Самое простое место для подзапроса — `FROM`:

```sql
SELECT sub.*
FROM (
      SELECT *
      FROM tutorial.sf_crime_incidents_2014_01
      WHERE day_of_week = 'Friday'
     ) sub
WHERE sub.resolution = 'NONE';
```

Как это работает:

1. База выполняет внутренний запрос в скобках.
2. Результат становится временной таблицей `sub`.
3. Внешний запрос работает с `sub`.

Правила:

- Внутренний запрос должен работать сам по себе. Проверьте его отдельно.
- Подзапрос в `FROM` нужно назвать (`sub`).
- Делайте отступы. Читатель должен видеть, где подзапрос.

:::note
В Postgres у подзапроса в `FROM` тоже обязателен псевдоним. В DuckDB он необязателен, но лучше всегда писать его.
:::

## Агрегация в несколько шагов

Нужно среднее число инцидентов в день для каждой категории. Это два шага:

1. Посчитать инциденты по дням и категориям.
2. Усреднить по дням.

```sql
SELECT sub.category,
       AVG(sub.incidents) AS avg_incidents_per_day
FROM (
      SELECT cleaned_date::DATE AS day,
             category,
             COUNT(*) AS incidents
      FROM tutorial.sf_crime_incidents_cleandate
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

Один `GROUP BY` здесь не поможет. Нельзя написать `AVG(COUNT(*))`.

## Подзапрос в условии

Подзапрос можно поставить в `WHERE`. Есть два вида.

Подзапрос возвращает одно значение:

```sql
SELECT COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
WHERE category = (
      SELECT category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      ORDER BY COUNT(*) DESC
      LIMIT 1
     );
```

Подзапрос возвращает список. Тогда используйте `IN`:

```sql
SELECT *
FROM tutorial.sf_crime_incidents_2014_01
WHERE category IN (
      SELECT category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      HAVING COUNT(*) < 5
     );
```

:::caution
Если подзапрос с `=` вернёт больше одной строки, будет ошибка. Для списка всегда пишите `IN`.
:::

## JOIN с подзапросом

Сначала сожмите данные подзапросом, потом присоедините. Так JOIN работает быстрее. Покажем каждый инцидент и общее число инцидентов его категории:

```sql
SELECT incidents.incidnt_num,
       incidents.category,
       sub.total_in_category
FROM tutorial.sf_crime_incidents_2014_01 incidents
JOIN (
      SELECT category,
             COUNT(*) AS total_in_category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
     ) sub
  ON sub.category = incidents.category;
```

## Подзапросы и UNION

В Crunchbase данные об инвестициях разделены на две таблицы. `UNION ALL` собирает их вместе. Подзапрос даёт общий результат для дальнейшей работы:

```sql
SELECT COUNT(*) AS rows_total
FROM (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) sub;
```

:::tip
Подзапрос в `FROM` можно заменить на `WITH` (CTE). Это то же самое, но читается лучше. Пример: `WITH sub AS (SELECT ...) SELECT * FROM sub;`
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Выберите все аресты по ордеру (`descript = 'WARRANT ARREST'`) из `tutorial.sf_crime_incidents_2014_01`. Оберните запрос внешним запросом, который покажет только нераскрытые инциденты (`resolution = 'NONE'`).

**Проверка:** 16 строк.

<details>
<summary>Решение</summary>

```sql
SELECT sub.*
FROM (
      SELECT *
      FROM tutorial.sf_crime_incidents_2014_01
      WHERE descript = 'WARRANT ARREST'
     ) sub
WHERE sub.resolution = 'NONE';
```

</details>

### Задание 2

Покажите среднее число инцидентов для каждой категории. Подсказка: используйте `tutorial.sf_crime_incidents_cleandate`. Данные охватывают один месяц, поэтому считайте среднее в день, а не в месяц.

**Проверка:** 32 строки. Первая: `LARCENY/THEFT` — около 94.39.

<details>
<summary>Решение</summary>

```sql
SELECT sub.category,
       AVG(sub.incidents) AS avg_incidents_per_day
FROM (
      SELECT cleaned_date::DATE AS day,
             category,
             COUNT(*) AS incidents
      FROM tutorial.sf_crime_incidents_cleandate
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

### Задание 3

Покажите все строки из трёх категорий с наименьшим числом инцидентов. Добавьте колонку с общим числом инцидентов категории.

**Проверка:** 4 строки. Категории: `BAD CHECKS` (1), `BRIBERY` (1) и `EXTORTION` (2).

<details>
<summary>Решение</summary>

```sql
SELECT incidents.*,
       sub.count AS total_incidents_in_category
FROM tutorial.sf_crime_incidents_2014_01 incidents
JOIN (
      SELECT category,
             COUNT(*) AS count
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      ORDER BY 2
      LIMIT 3
     ) sub
  ON sub.category = incidents.category;
```

</details>

### Задание 4

Посчитайте, сколько компаний основано и сколько куплено по кварталам, начиная с Q1 2012 и до Q4 2015 включительно. Сделайте два отдельных запроса с агрегацией, потом соедините их. Таблицы: `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`.

**Проверка:** 16 строк. Первая: `2012-Q1` — основано 3581, куплено 445. Последняя: `2015-Q4` — основано 48, куплено 926.

<details>
<summary>Решение</summary>

```sql
SELECT COALESCE(companies.quarter, acquisitions.quarter) AS quarter,
       companies.companies_founded,
       acquisitions.companies_acquired
FROM (
      SELECT founded_quarter AS quarter,
             COUNT(permalink) AS companies_founded
      FROM tutorial.crunchbase_companies
      WHERE founded_year BETWEEN 2012 AND 2015
      GROUP BY 1
     ) companies
FULL JOIN (
      SELECT acquired_quarter AS quarter,
             COUNT(DISTINCT company_permalink) AS companies_acquired
      FROM tutorial.crunchbase_acquisitions
      WHERE acquired_year BETWEEN 2012 AND 2015
      GROUP BY 1
     ) acquisitions
  ON companies.quarter = acquisitions.quarter
ORDER BY 1;
```

</details>

:::note
Мы ограничили годы значением 2015. В данных есть неверные даты, например `2041-Q3` и `3201-Q4`. Это ошибки источника.
:::

### Задание 5

Объедините две таблицы инвестиций (`crunchbase_investments_part1` и `crunchbase_investments_part2`). Составьте рейтинг инвесторов по общему числу инвестиций.

**Проверка:** 30190 строк (одна из них с `NULL` вместо имени). Первая: `Sequoia Capital` — 1033.

<details>
<summary>Решение</summary>

```sql
SELECT investor_name,
       COUNT(*) AS investments
FROM (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) sub
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>

### Задание 6

Сделайте то же, что в задании 5, но только для компаний, которые ещё работают. Подсказка: статус хранится в `tutorial.crunchbase_companies` (`status = 'operating'`).

**Проверка:** 26257 строк (одна из них с `NULL` вместо имени). Первая: `Wayra` — 877.

<details>
<summary>Решение</summary>

```sql
SELECT investments.investor_name,
       COUNT(*) AS investments
FROM tutorial.crunchbase_companies companies
JOIN (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) investments
  ON investments.company_permalink = companies.permalink
WHERE companies.status = 'operating'
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>
