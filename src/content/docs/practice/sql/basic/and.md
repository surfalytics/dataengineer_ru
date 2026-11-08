---
title: AND
description: Как объединить условия фильтра в SQL с помощью AND.
sidebar:
  order: 11
tags:
  - sql
  - practice
---

`AND` оставляет только те строки, где верны оба условия сразу.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

## Оператор AND

Десять лучших песен 2012 года:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2012 AND year_rank <= 10;
```

Условий может быть сколько угодно. Добавим третье: в названии исполнителя есть «feat»:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2012
  AND year_rank <= 10
  AND group_name ILIKE '%feat%';
```

Каждое условие пишите с новой строки. Так длинный `WHERE` легче читать.

:::tip
Чем больше `AND`, тем меньше строк в результате. Каждое условие только сужает выборку.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет все строки для песен из топ-10, где Ludacris входит в состав исполнителей (`group_name`).

**Проверка:** 7 строк, годы с 2004 по 2010.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank <= 10
  AND group_name ILIKE '%ludacris%';
```

</details>
