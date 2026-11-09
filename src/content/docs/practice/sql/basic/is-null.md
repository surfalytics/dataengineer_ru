---
title: "IS NULL"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "IS NULL в SQL: поиск пустых значений | Инжиниринг Данных"
description: "Как найти пустые значения NULL в SQL с помощью IS NULL и IS NOT NULL. Примеры и задачи на DuckDB."
sidebar:
  order: 9
tags:
  - sql
  - practice
---

`IS NULL` находит строки, где в столбце нет данных. Такое значение называют `NULL`.

В этом уроке работаем с таблицей `tutorial.crunchbase_companies` — компании из Crunchbase. В Billboard пустых значений нет, поэтому нужна другая таблица.

## Что такое NULL

`NULL` — это «значения нет». Это не ноль и не пустая строка. В Excel пустая ячейка и ячейка с пробелом почти одинаковы. В SQL разница большая.

Пустые значения найдём так:

```sql
SELECT *
FROM tutorial.crunchbase_companies
WHERE country_code IS NULL;
```

Запрос вернёт 6958 строк.

:::caution
`WHERE country_code = NULL` не работает. Он ничего не вернёт. Любое сравнение с `NULL` даёт не «верно» и не «неверно», а «неизвестно». Строки с таким результатом отбрасываются. Всегда пишите `IS NULL`.
:::

## Пустая строка и NULL

Иногда пустые значения хранят как пустую строку `''` или как пробелы. Это не `NULL`. Чтобы поймать оба случая:

```sql
SELECT *
FROM tutorial.crunchbase_companies
WHERE category_code IS NULL
   OR TRIM(category_code) = '';
```

`TRIM` убирает пробелы по краям. Подробнее про `NULL` — на странице [Средний уровень](/practice/sql/intermediate/).

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет все компании из `tutorial.crunchbase_companies`, у которых `category_code` пустой.

В оригинальном курсе здесь искали пустые `song_name` в Billboard. В нашей таблице таких строк нет.

**Проверка:** 3148 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.crunchbase_companies
WHERE category_code IS NULL;
```

</details>
