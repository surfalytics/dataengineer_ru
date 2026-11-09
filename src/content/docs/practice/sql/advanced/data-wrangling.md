---
title: "Подготовка данных (data wrangling)"
description: "Что такое data wrangling, какие проблемы бывают в сырых данных и как чистить их средствами SQL."
sidebar:
  order: 3
tags:
  - sql
  - practice
---

Data wrangling (или data munging) — это превращение «сырых» данных в удобный вид. Данные редко приходят чистыми. Их вводят люди, их собирают сайты, их выгружают из Excel. Поэтому аналитик тратит на чистку много времени.

В этом уроке нет новых функций. Мы собираем план: что обычно сломано и чем это чинить. Работаем с таблицами `tutorial.crunchbase_companies_clean_date` и `tutorial.sf_crime_incidents_2014_01`.

## Что обычно сломано

| Проблема | Пример в наших данных | Чем чинить |
|---|---|---|
| Дата хранится как текст | `founded_at = '9/4/14'` | `strptime`, `CAST`, `SUBSTR` |
| Число хранится как текст | `'1,000'` | `REPLACE` + `CAST`, `TRY_CAST` |
| Лишние символы | `location = '(37.78, -122.42)'` | `TRIM`, `REPLACE` |
| Разный регистр и пробелы | `'Software '`, `'SOFTWARE'` | `LOWER`, `TRIM` |
| Несколько значений в одной колонке | `'1200 Block of POLK ST'` | `SUBSTR`, `POSITION`, `LEFT` |
| Пропуски | `category_code IS NULL` | `COALESCE`, `CASE` |
| Дубли | Одна компания в двух строках | `DISTINCT`, `GROUP BY` |

Про функции для строк — в [уроке про строки](/practice/sql/advanced/string-functions/). Про даты — в [уроке про даты](/practice/sql/advanced/date-format/).

## Пример: чистим домен

В колонке `homepage_url` лежит полный адрес. Нам нужен только домен. Уберём `https://`, `http://` и `www.`:

```sql
SELECT homepage_url,
       REPLACE(REPLACE(REPLACE(homepage_url, 'https://', ''), 'http://', ''), 'www.', '') AS domain
FROM tutorial.crunchbase_companies_clean_date
WHERE homepage_url IS NOT NULL
LIMIT 5;
```

Функции вложены друг в друга. Сначала работает самая внутренняя.

## Пример: заполняем пропуски

`COALESCE` берёт первое значение, которое не `NULL`:

```sql
SELECT COALESCE(category_code, 'unknown') AS category,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
GROUP BY 1
ORDER BY 2 DESC
LIMIT 5;
```

## Пример: делим одну колонку на две

Адрес вида `1200 Block of POLK ST` хранит номер дома и улицу вместе. Достанем улицу:

```sql
SELECT address,
       SUBSTR(address, POSITION(' Block of ' IN address) + 10) AS street
FROM tutorial.sf_crime_incidents_2014_01
WHERE POSITION(' Block of ' IN address) > 0
LIMIT 5;
```

:::tip
Чистите данные в два шага. Сначала напишите запрос с `LIMIT 10` и посмотрите результат глазами. Потом уберите `LIMIT`. Так вы быстро найдёте ошибку.
:::

:::caution
Не меняйте смысл данных при чистке. Проверяйте число строк до и после. Если строк стало меньше, вы что-то отфильтровали.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Из `homepage_url` получите домен без `https://`, `http://` и `www.`. Посчитайте, сколько компаний у каждого домена. Покажите сначала самые частые. Пустые адреса пропустите.

**Проверка:** 61127 строк. Первая: `askforoffer.com` — 5 компаний.

<details>
<summary>Решение</summary>

```sql
SELECT REPLACE(REPLACE(REPLACE(homepage_url, 'https://', ''), 'http://', ''), 'www.', '') AS domain,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
WHERE homepage_url IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>

### Задание 2

В таблице `tutorial.sf_crime_incidents_2014_01` возьмите только адреса, где есть текст `Block of`. Достаньте название улицы (всё после `Block of`). Посчитайте инциденты по улицам. Покажите сначала самые частые.

**Проверка:** 833 улицы. Первая: `MARKET ST` — 467.

<details>
<summary>Решение</summary>

```sql
SELECT SUBSTR(address, POSITION(' Block of ' IN address) + 10) AS street,
       COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
WHERE POSITION(' Block of ' IN address) > 0
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>

### Задание 3

В колонке `time` время хранится текстом `HH:MM`. Достаньте час как число. Посчитайте инциденты по часам. Покажите сначала самый загруженный час.

**Проверка:** 24 строки. Первая: час 18 — 761 инцидент.

<details>
<summary>Решение</summary>

```sql
SELECT LEFT(time, 2)::INTEGER AS hour,
       COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>
