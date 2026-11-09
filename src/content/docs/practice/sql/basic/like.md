---
title: "LIKE"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "LIKE и ILIKE в SQL: поиск по шаблону | Инжиниринг Данных"
description: "Как искать текст по шаблону с помощью LIKE и ILIKE и символов % и _. Примеры и задачи на DuckDB."
sidebar:
  order: 6
tags:
  - sql
  - practice
---

`LIKE` ищет строки, похожие на шаблон. Он нужен, когда вы не знаете точное значение. Например: «все исполнители, чьё имя начинается на Snoop».

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end` — итоговые годовые чарты Billboard.

## Оператор LIKE

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name LIKE 'Snoop%';
```

Запрос вернёт строки, где `group_name` начинается с «Snoop», а дальше идут любые символы.

## Символы шаблона

| Символ | Что значит | Пример | Найдёт |
|---|---|---|---|
| `%` | Любое число любых символов, даже ноль | `'Snoop%'` | Snoop Dogg, Snoop Dogg featuring Pharrell |
| `_` | Ровно один любой символ | `'Dr_ke'` | Drake |

Где стоит `%` — важно:

- `'Snoop%'` — начинается с «Snoop»;
- `'%Snoop'` — заканчивается на «Snoop»;
- `'%Snoop%'` — содержит «Snoop» где угодно.

## Регистр букв: ILIKE

`LIKE` различает заглавные и строчные буквы. Шаблон `'snoop%'` не найдёт «Snoop Dogg».

`ILIKE` регистр не различает:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name ILIKE 'snoop%';
```

Символ `_` заменяет ровно один символ:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE artist ILIKE 'dr_ke';
```

:::note
`ILIKE` есть в DuckDB, Postgres и Snowflake. В некоторых базах его нет. Универсальный способ: `LOWER(group_name) LIKE 'snoop%'`.
:::

:::caution
`LIKE '%...%'` на большой таблице работает медленно: база проверяет каждую строку. На собеседовании об этом часто спрашивают.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт все строки, где Ludacris входит в состав исполнителей (`group_name`).

**Проверка:** 64 строки.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name ILIKE '%ludacris%';
```

</details>

### Задание 2

Напишите запрос, который вернёт все строки, где первый исполнитель в `group_name` начинается на «DJ».

**Проверка:** 15 строк, 5 разных значений `group_name`.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name LIKE 'DJ%';
```

</details>
