---
title: "ORDER BY"
description: "Как сортировать результат запроса с помощью ORDER BY и как писать комментарии в SQL."
sidebar:
  order: 13
next:
  label: "Средний уровень SQL"
tags:
  - sql
  - practice
---

`ORDER BY` сортирует результат по одному или нескольким столбцам. Без него порядок строк не гарантирован.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

## Сортировка по одному столбцу

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY artist;
```

Строки идут по алфавиту, от A до Z. Это порядок по возрастанию. Он работает по умолчанию. Для чисел это от меньшего к большему.

Чтобы отсортировать в обратном порядке, добавьте `DESC`:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
ORDER BY year_rank DESC;
```

`ORDER BY` пишут после `WHERE`. Если есть `LIMIT`, то `ORDER BY` идёт перед ним.

## Сортировка по нескольким столбцам

Столбцы перечисляют через запятую. Сначала сортировка по первому. Если значения равны, то по второму:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
ORDER BY year_rank, artist;
```

`DESC` действует только на тот столбец, после которого стоит:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY year DESC, year_rank;
```

Здесь год идёт от нового к старому, а место внутри года — от 1 к 100.

:::tip
В `ORDER BY` можно указать номер столбца из `SELECT`: `ORDER BY 1, 2`. Это быстро, но в рабочих запросах лучше писать имена.
:::

:::note
`NULL` в DuckDB по умолчанию идут последними при сортировке по возрастанию. Изменить порядок: `NULLS FIRST` или `NULLS LAST`. В Postgres `NULL` при `ASC` тоже идут последними.
:::

## Комментарии

Комментарий — это текст, который база игнорирует. Он нужен людям.

Однострочный комментарий начинается с `--`:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013 -- нужный год
  AND year_rank <= 10; -- только топ-10
```

Многострочный комментарий — между `/*` и `*/`:

```sql
/* Топ-10 за 2013 год.
   Запрос нужен для проверки. */
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank <= 10;
```

Хороший комментарий объясняет, зачем это сделано, а не пересказывает код.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт все строки за 2012 год. Отсортируйте их по названию песни от Z до A.

**Проверка:** 131 строка. Первая строка — песня «Young, Wild & Free».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2012
ORDER BY song_name DESC;
```

</details>

### Задание 2

Напишите запрос, который вернёт все строки за 2010 год. Отсортируйте их по месту в чарте. Внутри каждой песни отсортируйте исполнителей по алфавиту.

**Проверка:** 147 строк. Первая строка — Tik Tok, Kesha.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2010
ORDER BY year_rank, artist;
```

</details>

### Задание 3

Напишите запрос, который покажет все строки, где T-Pain входит в состав исполнителей. Отсортируйте их по месту в чарте от худшего к лучшему (от 100 к 1).

**Проверка:** 54 строки. Первая строка: 2008 год, место 100, «She Got It».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name ILIKE '%t-pain%'
ORDER BY year_rank DESC;
```

</details>

### Задание 4

Напишите запрос, который вернёт песни на местах с 10 по 20 включительно в 1993, 2003 или 2013 году. Отсортируйте результат по году и месту. Оставьте комментарий на каждой строке `WHERE`, который объясняет, что эта строка делает.

**Проверка:** 48 строк. Первая строка: 1993 год, место 10, «Informer».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year IN (1993, 2003, 2013)  -- нужные годы
  AND year_rank BETWEEN 10 AND 20 -- места с 10 по 20
ORDER BY year, year_rank;
```

</details>
