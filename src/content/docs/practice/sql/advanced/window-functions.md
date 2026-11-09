---
title: "Оконные функции"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Оконные функции в SQL: ROW_NUMBER, LAG | Инжиниринг Данных"
description: "Как считать накопительные суммы, ранги, процентили и сравнивать строки с соседними через OVER, PARTITION BY, ROW_NUMBER, RANK, NTILE, LAG и LEAD."
sidebar:
  order: 6
tags:
  - sql
  - practice
---

Оконная функция считает значение по группе связанных строк, но не схлопывает их в одну. Каждая строка остаётся в результате. Это отличие от `GROUP BY`.

Типичные задачи: накопительная сумма, ранг, доля от общей суммы, сравнение с предыдущей строкой. Оконные функции часто спрашивают на собеседованиях.

Работаем с таблицей `tutorial.dc_bikeshare_q1_2012` — поездки Capital Bikeshare в Вашингтоне за первый квартал 2012 года. Одна строка — одна поездка. Поле `rider_type`: `Registered` — подписка, `Casual` — разовый билет.

## Накопительная сумма

```sql
SELECT duration_seconds,
       SUM(duration_seconds) OVER (ORDER BY start_time) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
LIMIT 10;
```

Здесь нет `GROUP BY`. `SUM(...) OVER (...)` читается так: «сумма `duration_seconds` по всем строкам, по порядку `start_time`».

## PARTITION BY

`PARTITION BY` делит строки на группы. Внутри каждой группы окно считается заново:

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, start_time
LIMIT 10;
```

Если убрать `ORDER BY` из `OVER`, то в каждой строке будет сумма всей группы:

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal) AS start_terminal_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

`PARTITION BY` и `ORDER BY` вместе задают «окно».

:::caution
Оконную функцию нельзя писать в `WHERE` и в `GROUP BY`. Если нужно отфильтровать по её результату, оберните запрос в подзапрос.
:::

## COUNT, SUM, AVG

Это обычные агрегаты. С `OVER` они становятся оконными:

```sql
SELECT start_terminal,
       duration_seconds,
       COUNT(*) OVER (PARTITION BY start_terminal) AS rides_in_terminal,
       AVG(duration_seconds) OVER (PARTITION BY start_terminal) AS avg_duration
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

## ROW_NUMBER, RANK, DENSE_RANK

Все три нумеруют строки внутри окна. Разница в том, как они обрабатывают одинаковые значения.

| Функция | Что делает при одинаковых значениях |
|---|---|
| `ROW_NUMBER()` | Всегда разные номера: 1, 2, 3, 4 |
| `RANK()` | Одинаковый номер, потом пропуск: 1, 2, 2, 4 |
| `DENSE_RANK()` | Одинаковый номер, без пропуска: 1, 2, 2, 3 |

```sql
SELECT start_terminal,
       duration_seconds,
       ROW_NUMBER() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS row_num,
       RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank,
       DENSE_RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS dense_rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, duration_seconds DESC
LIMIT 10;
```

## NTILE

`NTILE(n)` делит строки на `n` равных групп. `NTILE(4)` даёт квартили, `NTILE(100)` даёт процентили:

```sql
SELECT duration_seconds,
       NTILE(4) OVER (ORDER BY duration_seconds) AS quartile
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

## LAG и LEAD

`LAG` берёт значение из предыдущей строки. `LEAD` — из следующей:

```sql
SELECT start_terminal,
       start_time,
       duration_seconds,
       LAG(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS previous_duration,
       LEAD(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS next_duration
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, start_time
LIMIT 10;
```

У первой строки группы нет предыдущей. Там будет `NULL`.

## Псевдоним окна

Если одно окно нужно несколько раз, дайте ему имя через `WINDOW`:

```sql
SELECT start_terminal,
       duration_seconds,
       ROW_NUMBER() OVER w AS row_num,
       RANK() OVER w AS rank,
       DENSE_RANK() OVER w AS dense_rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
WINDOW w AS (PARTITION BY start_terminal ORDER BY duration_seconds DESC)
LIMIT 10;
```

`WINDOW` пишется после `WHERE` и `GROUP BY`, перед `ORDER BY`.

## QUALIFY в DuckDB

Чтобы отфильтровать по оконной функции, в других базах нужен подзапрос. В DuckDB есть `QUALIFY`. Он работает как `WHERE`, но для оконных функций:

```sql
SELECT start_terminal,
       start_time,
       duration_seconds,
       RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
QUALIFY rank <= 5
ORDER BY start_terminal, rank;
```

:::note
`QUALIFY` есть в DuckDB, Snowflake и BigQuery. В Postgres его нет. Там пишут подзапрос с `WHERE rank <= 5` (смотрите задание 3).
:::

:::note
Деление `duration_seconds / SUM(...)` в DuckDB даёт дробное число. В Postgres два целых числа дадут целое (обычно `0`). Там нужно привести одно число к `DOUBLE PRECISION` или `NUMERIC`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Измените пример с `PARTITION BY start_terminal` так, чтобы он показывал длительность каждой поездки как процент от общего времени всех поездок с этого `start_terminal`. Берите поездки до 8 января 2012 (`start_time < '2012-01-08'`). Сортируйте по `start_terminal`, потом по проценту от большего к меньшему.

**Проверка:** 20558 строк. Первая: терминал `31000`, `duration_seconds` 3340, сумма по терминалу 12207, около 27.36%.

<details>
<summary>Решение</summary>

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal) AS start_terminal_sum,
       (duration_seconds / SUM(duration_seconds) OVER (PARTITION BY start_terminal)) * 100 AS pct_of_total_time
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY 1, 4 DESC;
```

</details>

### Задание 2

Покажите накопительную сумму длительности поездок по `end_terminal`. Внутри терминала сортируйте длительность от большей к меньшей. Берите поездки до 8 января 2012.

**Проверка:** 20558 строк. Для `end_terminal` 31000 первые строки: 3097 (накопительно 3097), 3069 (накопительно 6166).

<details>
<summary>Решение</summary>

```sql
SELECT end_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY end_terminal ORDER BY duration_seconds DESC) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY end_terminal, duration_seconds DESC;
```

</details>

### Задание 3

Покажите 5 самых долгих поездок с каждого `start_terminal`. Сортируйте по терминалу, внутри — от самой долгой к самой короткой. Берите поездки до 8 января 2012.

**Проверка:** 667 строк (при равных значениях `RANK` может дать больше 5 строк на терминал). Первая: терминал `31000`, `start_time` `2012-01-05 17:25:44`, `trip_time` 3340, ранг 1.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM (
      SELECT start_terminal,
             start_time,
             duration_seconds AS trip_time,
             RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank
      FROM tutorial.dc_bikeshare_q1_2012
      WHERE start_time < '2012-01-08'
     ) sub
WHERE sub.rank <= 5
ORDER BY start_terminal, rank;
```

</details>

### Задание 4

Покажите только длительность поездки и процентиль, в который она попадает. Считайте по всему набору данных, без `PARTITION BY`. Берите поездки до 8 января 2012. Сначала самые долгие.

**Проверка:** 20558 строк. Первая строка: 70005 секунд, процентиль 100.

<details>
<summary>Решение</summary>

```sql
SELECT duration_seconds,
       NTILE(100) OVER (ORDER BY duration_seconds) AS percentile
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY 1 DESC;
```

</details>
