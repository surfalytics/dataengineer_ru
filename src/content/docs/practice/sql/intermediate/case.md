---
title: CASE
description: Как писать условную логику if/then в SQL с помощью CASE, в том числе внутри агрегатных функций.
sidebar:
  order: 8
tags:
  - sql
  - practice
---

`CASE` — это условная логика в SQL, аналог `IF/THEN` в Excel. Он нужен, чтобы разложить значения по группам или посчитать «столбцы» по условию. В этом уроке работаем с таблицей `benn.college_football_players`: одна строка на игрока студенческого футбола. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

Столбец `year` — это курс: `FR`, `SO`, `JR`, `SR`.

## Синтаксис CASE

`CASE` состоит из пар `WHEN ... THEN`. Заканчивается словом `END`. Часть `ELSE` необязательна.

```sql
SELECT player_name,
       year,
       CASE WHEN year = 'SR' THEN 'yes'
            ELSE NULL END AS is_a_senior
FROM benn.college_football_players;
```

Как это работает:

- База проверяет условие `year = 'SR'` в каждой строке.
- Если условие верно, в новый столбец попадает `'yes'`.
- Если неверно, срабатывает `ELSE`. Здесь это `NULL`.

Если `ELSE` нет, результат тоже `NULL`. Чтобы вместо `NULL` было слово, напишите его в `ELSE`:

```sql
SELECT player_name,
       year,
       CASE WHEN year = 'SR' THEN 'yes'
            ELSE 'no' END AS is_a_senior
FROM benn.college_football_players;
```

## Несколько условий

Можно добавить много веток `WHEN`. База проверяет их сверху вниз и берёт **первую подходящую**.

```sql
SELECT player_name,
       weight,
       CASE WHEN weight > 250 THEN 'over 250'
            WHEN weight > 200 THEN '201-250'
            WHEN weight > 175 THEN '176-200'
            ELSE '175 or under' END AS weight_group
FROM benn.college_football_players;
```

Условия внутри `WHEN` можно объединять через `AND` и `OR`:

```sql
SELECT player_name,
       weight,
       CASE WHEN weight > 250 AND year = 'FR' THEN 'heavy freshman'
            ELSE 'other' END AS player_type
FROM benn.college_football_players;
```

:::tip
Порядок веток важен. Сначала ставьте более узкие условия. Если поставить `weight > 175` первым, остальные ветки никогда не сработают.
:::

## CASE и агрегаты

Новый столбец из `CASE` можно использовать в `GROUP BY`:

```sql
SELECT CASE WHEN year IN ('FR', 'SO') THEN 'underclass'
            WHEN year IN ('JR', 'SR') THEN 'upperclass'
            ELSE NULL END AS class_group,
       COUNT(1) AS players
FROM benn.college_football_players
GROUP BY 1;
```

## CASE внутри агрегата

Можно положить `CASE` внутрь `COUNT` или `SUM`. Так получаются отдельные столбцы для каждого значения, как в сводной таблице:

```sql
SELECT CASE WHEN year = 'FR' THEN 'FR'
            WHEN year = 'SO' THEN 'SO'
            WHEN year = 'JR' THEN 'JR'
            WHEN year = 'SR' THEN 'SR'
            ELSE 'No Year Data' END AS year_group,
       COUNT(1) AS count
FROM benn.college_football_players
GROUP BY 1;
```

Тот же результат, но курсы идут в столбцах, а не в строках:

```sql
SELECT COUNT(CASE WHEN year = 'FR' THEN 1 ELSE NULL END) AS fr_count,
       COUNT(CASE WHEN year = 'SO' THEN 1 ELSE NULL END) AS so_count,
       COUNT(CASE WHEN year = 'JR' THEN 1 ELSE NULL END) AS jr_count,
       COUNT(CASE WHEN year = 'SR' THEN 1 ELSE NULL END) AS sr_count
FROM benn.college_football_players;
```

`COUNT` не считает `NULL`. Поэтому в счёт попадают только строки, где сработало `WHEN`.

:::note
В DuckDB и Postgres есть короткая запись: `COUNT(*) FILTER (WHERE year = 'FR')`. Она делает то же самое, что `COUNT(CASE ...)`. `CASE` работает во всех базах.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, где есть столбец с пометкой `yes` для игроков из Калифорнии (`state = 'CA'`). Отсортируйте результат так, чтобы такие игроки шли первыми.

**Проверка:** 6935 строк. В начале списка идут 351 строка с `yes`.

<details>
<summary>Решение</summary>

```sql
SELECT player_name,
       state,
       CASE WHEN state = 'CA' THEN 'yes'
            ELSE NULL END AS from_california
FROM benn.college_football_players
ORDER BY 3;
```

</details>

### Задание 2

Напишите запрос с именами игроков и столбцом, который делит их по росту (`height`, в дюймах) на четыре группы. Границы групп можно выбрать самим: у задачи много верных решений.

**Проверка:** 6935 строк. При границах из решения: `over 74` — 2771, `73-74` — 1654, `71-72` — 1413, `70 or under` — 1097.

<details>
<summary>Решение</summary>

```sql
SELECT player_name,
       height,
       CASE WHEN height > 74 THEN 'over 74'
            WHEN height > 72 AND height <= 74 THEN '73-74'
            WHEN height > 70 AND height <= 72 THEN '71-72'
            ELSE '70 or under' END AS height_group
FROM benn.college_football_players;
```

</details>

### Задание 3

Выберите все столбцы из `benn.college_football_players` и добавьте столбец, где указано имя игрока, если он на третьем или четвёртом курсе (`JR` или `SR`).

**Проверка:** 6935 строк. Имя заполнено у 2952 игроков, у остальных `NULL`.

<details>
<summary>Решение</summary>

```sql
SELECT *,
       CASE WHEN year IN ('JR', 'SR') THEN player_name ELSE NULL END AS upperclass_player_name
FROM benn.college_football_players;
```

</details>

### Задание 4

Посчитайте игроков с весом от 300 фунтов и больше по трём регионам: Западное побережье (CA, OR, WA), Техас (TX) и все остальные.

**Проверка:** 3 строки: `West Coast` — 68, `Texas` — 53, `Other` — 657.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN state IN ('CA', 'OR', 'WA') THEN 'West Coast'
            WHEN state = 'TX' THEN 'Texas'
            ELSE 'Other' END AS arbitrary_regional_designation,
       COUNT(1) AS players
FROM benn.college_football_players
WHERE weight >= 300
GROUP BY 1;
```

</details>

### Задание 5

Напишите запрос, который посчитает суммарный вес игроков из Калифорнии отдельно для младших курсов (`FR`, `SO`) и старших курсов (`JR`, `SR`).

**Проверка:** 2 строки: `underclass` — 49603, `upperclass` — 31766.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN year IN ('FR', 'SO') THEN 'underclass'
            WHEN year IN ('JR', 'SR') THEN 'upperclass'
            ELSE NULL END AS class_group,
       SUM(weight) AS combined_player_weight
FROM benn.college_football_players
WHERE state = 'CA'
GROUP BY 1;
```

</details>

### Задание 6

Покажите число игроков в каждом штате. Курсы `FR`, `SO`, `JR`, `SR` выведите в отдельных столбцах. Добавьте столбец с общим числом игроков. Штаты с наибольшим числом игроков должны идти первыми.

**Проверка:** первая строка: `TX`, 135, 111, 95, 95, итого 436.

<details>
<summary>Решение</summary>

```sql
SELECT state,
       COUNT(CASE WHEN year = 'FR' THEN 1 ELSE NULL END) AS fr_count,
       COUNT(CASE WHEN year = 'SO' THEN 1 ELSE NULL END) AS so_count,
       COUNT(CASE WHEN year = 'JR' THEN 1 ELSE NULL END) AS jr_count,
       COUNT(CASE WHEN year = 'SR' THEN 1 ELSE NULL END) AS sr_count,
       COUNT(1) AS total_players
FROM benn.college_football_players
GROUP BY state
ORDER BY total_players DESC;
```

</details>

### Задание 7

Покажите, сколько игроков учатся в школах с названием на буквы от A до M и сколько в школах на буквы от N до Z.

Подсказка: названия в таблице начинаются с заглавной буквы, а `'A' < 'n'` верно для любой заглавной. Приведите название к нижнему регистру через `LOWER`.

**Проверка:** 2 строки: `A-M` — 3817, `N-Z` — 3118.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN LOWER(school_name) < 'n' THEN 'A-M'
            WHEN LOWER(school_name) >= 'n' THEN 'N-Z'
            ELSE NULL END AS school_name_group,
       COUNT(1) AS players
FROM benn.college_football_players
GROUP BY 1
ORDER BY 1;
```

</details>
