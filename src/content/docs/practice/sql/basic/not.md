---
title: NOT
description: Как исключить строки из результата с помощью NOT.
sidebar:
  order: 13
tags:
  - sql
  - practice
---

`NOT` ставят перед условием. Тогда в результат попадут строки, где условие неверно.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

## Оператор NOT

Песни 2013 года, кроме мест 2 и 3:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank NOT BETWEEN 2 AND 3;
```

## NOT и операторы > и <

С `>` и `<` `NOT` не нужен. Такая запись даст ошибку:

```sql
-- ошибка
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank NOT > 3;
```

Используйте противоположный оператор:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank <= 3;
```

## NOT с LIKE

`NOT` часто ставят перед `LIKE`. Так исключают строки по шаблону:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND group_name NOT ILIKE '%macklemore%';
```

В результате нет Macklemore. Запрос вернёт 138 строк.

## NOT с NULL

Чтобы найти непустые значения, пишут `IS NOT NULL`:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND artist IS NOT NULL;
```

:::caution
`NOT NULL` без `IS` — ошибка. Правильно: `IS NOT NULL`. Ещё одна ловушка: `NOT IN` и `NOT LIKE` не вернут строки, где значение `NULL`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт все строки для песен, попавших в чарт в 2013 году, в названии которых нет буквы «a».

**Проверка:** 68 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE song_name NOT ILIKE '%a%'
  AND year = 2013;
```

</details>
