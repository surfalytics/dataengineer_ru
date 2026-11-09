---
title: "Сводные таблицы (PIVOT)"
description: "Как превращать строки в колонки и колонки в строки в SQL: через CASE и UNION ALL и через PIVOT и UNPIVOT в DuckDB."
sidebar:
  order: 8
next:
  label: "Базовый минимум CLI"
tags:
  - sql
  - practice
---

Pivot (сводная таблица) разворачивает данные. Строки превращаются в колонки или колонки в строки. Первое нужно для отчёта и графика. Второе нужно, чтобы данные удобно считались.

В уроке работаем с таблицами `benn.college_football_players`, `benn.college_football_teams` и `tutorial.worldwide_earthquakes`.

## Строки в колонки

Задача: показать для каждой конференции число игроков по курсам (`FR`, `SO`, `JR`, `SR`). Результат должен быть такой:

| conference | fr | so | jr | sr |
|---|---|---|---|---|
| Atlantic Coast | 215 | 175 | 172 | 143 |

Начните с агрегации. Сколько игроков каждого курса в каждой конференции:

```sql
SELECT teams.conference AS conference,
       players.year,
       COUNT(1) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1, 2
ORDER BY 1, 2;
```

Положите этот запрос в подзапрос. Сначала проверьте, что `SELECT * FROM (...) sub` даёт те же строки. Так проще найти ошибку. `ORDER BY` из подзапроса уберите: внешний запрос всё равно сортирует.

Каждый столбец результата — отдельное выражение в `SELECT`. Для каждого курса пишем `SUM(CASE ...)`:

```sql
SELECT conference,
       SUM(CASE WHEN year = 'FR' THEN players ELSE NULL END) AS fr,
       SUM(CASE WHEN year = 'SO' THEN players ELSE NULL END) AS so,
       SUM(CASE WHEN year = 'JR' THEN players ELSE NULL END) AS jr,
       SUM(CASE WHEN year = 'SR' THEN players ELSE NULL END) AS sr
FROM (
      SELECT teams.conference AS conference,
             players.year,
             COUNT(1) AS players
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 1;
```

Как это работает: `CASE` оставляет число только в нужной колонке. В остальных колонках будет `NULL`. `SUM` игнорирует `NULL`. `GROUP BY` собирает строки конференции в одну.

Добавим колонку «всего игроков» и отсортируем по ней:

```sql
SELECT conference,
       SUM(players) AS total_players,
       SUM(CASE WHEN year = 'FR' THEN players ELSE NULL END) AS fr,
       SUM(CASE WHEN year = 'SO' THEN players ELSE NULL END) AS so,
       SUM(CASE WHEN year = 'JR' THEN players ELSE NULL END) AS jr,
       SUM(CASE WHEN year = 'SR' THEN players ELSE NULL END) AS sr
FROM (
      SELECT teams.conference AS conference,
             players.year,
             COUNT(1) AS players
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

Этот способ работает в любой базе. Его знают на собеседованиях.

## Колонки в строки

Многие таблицы в интернете сделаны для чтения, а не для анализа. Например, таблица `tutorial.worldwide_earthquakes`: число землетрясений по силе и годам.

```sql
SELECT *
FROM tutorial.worldwide_earthquakes;
```

Колонки называются `year_2000`, `year_2001` и так далее. Чтобы посчитать, например, среднее по годам, лучше иметь три колонки: `magnitude`, `year`, `number_of_earthquakes`.

Шаг 1. Составьте список годов. Можно написать его руками через `UNION ALL`:

```sql
SELECT year
FROM (
      SELECT 2000 AS year
      UNION ALL SELECT 2001
      UNION ALL SELECT 2002
      UNION ALL SELECT 2003
      UNION ALL SELECT 2004
      UNION ALL SELECT 2005
      UNION ALL SELECT 2006
      UNION ALL SELECT 2007
      UNION ALL SELECT 2008
      UNION ALL SELECT 2009
      UNION ALL SELECT 2010
      UNION ALL SELECT 2011
      UNION ALL SELECT 2012
     ) AS v;
```

Шаг 2. Соедините список с таблицей через `CROSS JOIN`. Каждая строка размножится 13 раз. Выберите нужную колонку через `CASE`:

```sql
SELECT years.year,
       earthquakes.magnitude,
       CASE years.year
            WHEN 2000 THEN year_2000
            WHEN 2001 THEN year_2001
            WHEN 2002 THEN year_2002
            WHEN 2003 THEN year_2003
            WHEN 2004 THEN year_2004
            WHEN 2005 THEN year_2005
            WHEN 2006 THEN year_2006
            WHEN 2007 THEN year_2007
            WHEN 2008 THEN year_2008
            WHEN 2009 THEN year_2009
            WHEN 2010 THEN year_2010
            WHEN 2011 THEN year_2011
            WHEN 2012 THEN year_2012
            ELSE NULL
       END AS number_of_earthquakes
FROM tutorial.worldwide_earthquakes AS earthquakes
CROSS JOIN (
      SELECT 2000 AS year
      UNION ALL SELECT 2001
      UNION ALL SELECT 2002
      UNION ALL SELECT 2003
      UNION ALL SELECT 2004
      UNION ALL SELECT 2005
      UNION ALL SELECT 2006
      UNION ALL SELECT 2007
      UNION ALL SELECT 2008
      UNION ALL SELECT 2009
      UNION ALL SELECT 2010
      UNION ALL SELECT 2011
      UNION ALL SELECT 2012
     ) AS years
ORDER BY 1, 2;
```

Результат: 6 уровней силы × 13 лет = 78 строк.

## Бонус: PIVOT и UNPIVOT в DuckDB

В DuckDB есть готовые команды `PIVOT` и `UNPIVOT`. Они делают то же, что запросы выше, но намного короче.

`PIVOT` из строк в колонки:

```sql
PIVOT (
      SELECT teams.conference,
             players.year
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
     )
ON year IN ('FR', 'SO', 'JR', 'SR')
USING COUNT(*)
GROUP BY conference
ORDER BY conference;
```

Части команды:

- `ON year` — значения какой колонки станут колонками;
- `IN (...)` — какие именно значения (необязательно);
- `USING COUNT(*)` — что считать в ячейках;
- `GROUP BY conference` — что остаётся строками.

`UNPIVOT` из колонок в строки:

```sql
UNPIVOT tutorial.worldwide_earthquakes
ON COLUMNS('year_*')
INTO NAME year VALUE number_of_earthquakes;
```

`COLUMNS('year_*')` берёт все колонки, имя которых начинается с `year_`. В колонке `year` останутся значения вроде `year_2000`. Чтобы получить число, уберите префикс:

```sql
SELECT magnitude,
       REPLACE(year, 'year_', '')::INTEGER AS year,
       number_of_earthquakes
FROM (
      UNPIVOT tutorial.worldwide_earthquakes
      ON COLUMNS('year_*')
      INTO NAME year VALUE number_of_earthquakes
     )
ORDER BY 2, 1;
```

:::note
В Postgres нет команд `PIVOT` и `UNPIVOT`. Там используют `SUM(CASE ...)` для строк в колонки и `CROSS JOIN` с `UNION ALL` или `LATERAL (VALUES ...)` для колонок в строки. SQL Server, Oracle и Snowflake имеют свои версии `PIVOT`.
:::

:::caution
В обычном `PIVOT` нужно знать список значений. Если значение добавится позже, при ручном способе колонка не появится сама. Проверяйте список.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

В этом уроке не было задач в оригинале. Ниже три задачи на тему.

### Задание 1

Для каждого дивизиона (`division` в `benn.college_football_teams`) посчитайте игроков по курсам `FR`, `SO`, `JR`, `SR`. Используйте `SUM(CASE ...)` или `COUNT(CASE ...)` без `PIVOT`. Добавьте колонку `total_players`.

**Проверка:** 2 строки. `FBS (Division I-A Teams)` и `FCS (Division I-AA Teams)`. Сумма `total_players` по двум строкам — 6935.

<details>
<summary>Решение</summary>

```sql
SELECT teams.division,
       COUNT(*) AS total_players,
       COUNT(CASE WHEN players.year = 'FR' THEN 1 END) AS fr,
       COUNT(CASE WHEN players.year = 'SO' THEN 1 END) AS so,
       COUNT(CASE WHEN players.year = 'JR' THEN 1 END) AS jr,
       COUNT(CASE WHEN players.year = 'SR' THEN 1 END) AS sr
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1
ORDER BY 1;
```

</details>

### Задание 2

Превратите `tutorial.worldwide_earthquakes` в длинный вид с колонками `magnitude`, `year`, `number_of_earthquakes`. Используйте `UNPIVOT`. Потом посчитайте сумму землетрясений силой `7.0 to 7.9` за все годы.

**Проверка:** длинная таблица содержит 78 строк. Сумма для `7.0 to 7.9` — 186.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(number_of_earthquakes) AS total
FROM (
      UNPIVOT tutorial.worldwide_earthquakes
      ON COLUMNS('year_*')
      INTO NAME year VALUE number_of_earthquakes
     )
WHERE magnitude = '7.0 to 7.9';
```

</details>

### Задание 3

В `benn.sample_event_table` посчитайте события за март 2014. Строки — `event_name`, колонки — `device`. Используйте `PIVOT` из DuckDB. Устройства выберите автоматически, без `IN`.

**Проверка:** 6 строк (по числу типов событий) и 5 колонок: `event_name` и 4 устройства. Сумма всех ячеек — 171551.

<details>
<summary>Решение</summary>

```sql
PIVOT (
      SELECT event_name,
             device
      FROM benn.sample_event_table
      WHERE event_date >= '2014-03-01'
        AND event_date < '2014-04-01'
     )
ON device
USING COUNT(*)
GROUP BY event_name
ORDER BY event_name;
```

</details>
