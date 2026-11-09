---
title: "IN"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "IN в SQL: фильтр по списку значений | Инжиниринг Данных"
description: "Как отфильтровать строки по списку значений с помощью IN. Примеры и задачи на DuckDB."
sidebar:
  order: 7
tags:
  - sql
  - practice
---

`IN` оставляет строки, где значение совпадает с одним из значений в списке. Это короткая замена цепочке `OR`.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

## Оператор IN

Песни, которые заняли 1, 2 или 3 место:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank IN (1, 2, 3);
```

Для текста значения берут в одинарные кавычки. Значения в списке разделяют запятой:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE artist IN ('Taylor Swift', 'Usher', 'Ludacris');
```

`IN` ищет точное совпадение. Для частичного совпадения нужен [LIKE](/practice/sql/basic/like/).

:::tip
`IN (1, 2, 3)` — то же самое, что `year_rank = 1 OR year_rank = 2 OR year_rank = 3`. Но короче и легче читать.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет все записи про Elvis Presley и MC Hammer.

Подсказка: MC Hammer в таблице записан иначе. Посмотрите, какие значения есть в `group_name`, например через `WHERE group_name ILIKE '%hammer%'`. Нужны значения `MC Hammer` и `Hammer`.

**Проверка:** 35 строк, 3 разных значения `group_name`.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name IN ('MC Hammer', 'Hammer', 'Elvis Presley');
```

</details>
