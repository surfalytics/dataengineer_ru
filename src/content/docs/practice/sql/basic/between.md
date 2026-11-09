---
title: "BETWEEN"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "BETWEEN в SQL: фильтр по диапазону | Инжиниринг Данных"
description: "Как отфильтровать строки по диапазону значений с помощью BETWEEN. Примеры и задачи на DuckDB."
sidebar:
  order: 8
tags:
  - sql
  - practice
---

`BETWEEN` оставляет строки, где значение лежит в диапазоне. Его используют для чисел и дат.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

## Оператор BETWEEN

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank BETWEEN 5 AND 10;
```

Запрос вернёт 396 строк. `BETWEEN` всегда идёт вместе с [AND](/practice/sql/basic/and/).

Границы входят в диапазон. Значит, места 5 и 10 тоже попадут в результат. Этот запрос делает то же самое:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank >= 5 AND year_rank <= 10;
```

:::tip
Многие предпочитают второй вариант. В нём границы видно сразу. Про `BETWEEN` легко забыть, входят границы или нет.
:::

:::caution
С датами и временем будьте осторожны. `BETWEEN '2014-01-01' AND '2014-01-31'` не захватит записи от 31 января после полуночи, если в столбце есть время. Подробнее — в уроке [Формат дат и времени](/practice/sql/advanced/date-format/).
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет все песни из чарта с 1985 по 1990 год включительно.

**Проверка:** 630 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year BETWEEN 1985 AND 1990;
```

</details>
