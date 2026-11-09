---
title: "OR"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "OR в SQL: любое из условий | Инжиниринг Данных"
description: "Как выбрать строки, подходящие под любое из условий, с помощью OR и скобок."
sidebar:
  order: 11
tags:
  - sql
  - practice
---

`OR` оставляет строки, где верно хотя бы одно из условий.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

## Оператор OR

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank = 5 OR artist = 'Gotye';
```

Каждая строка в результате подходит под одно из двух условий. Запрос вернёт 70 строк.

## OR вместе с AND

`AND` и `OR` можно смешивать. Для этого нужны скобки:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND (group_name ILIKE '%macklemore%' OR group_name ILIKE '%timberlake%');
```

Скобки превращают `OR` в одно общее условие. Условие `year = 2013` верно для всех строк результата. А второе условие значит: есть Macklemore или есть Timberlake.

:::caution
Без скобок `AND` сильнее, чем `OR`. Он выполняется первым. Запрос без скобок вернёт другие строки:

```sql
-- ошибка по смыслу: условие по году относится только к первой части
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND group_name ILIKE '%macklemore%'
   OR group_name ILIKE '%timberlake%';
```

Он вернёт Macklemore за 2013 год и Timberlake за все годы. Если смешиваете `AND` и `OR`, всегда ставьте скобки.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт все строки для песен из топ-10, где в составе исполнителей есть Katy Perry или Bon Jovi.

**Проверка:** 8 строк, 5 разных значений `group_name`.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank <= 10
  AND (group_name ILIKE '%katy perry%' OR group_name ILIKE '%bon jovi%');
```

</details>

### Задание 2

Напишите запрос, который вернёт все песни со словом «California» в названии, попавшие в чарт в 1970-х или 1990-х годах.

**Проверка:** 7 строк. Среди них Hotel California.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE song_name LIKE '%California%'
  AND (year BETWEEN 1970 AND 1979 OR year BETWEEN 1990 AND 1999);
```

</details>

### Задание 3

Напишите запрос, который вернёт все записи из топ-100 с участием Dr. Dre до 2001 года или после 2009 года.

**Проверка:** 19 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name ILIKE '%dr. dre%'
  AND (year <= 2000 OR year >= 2010);
```

</details>
