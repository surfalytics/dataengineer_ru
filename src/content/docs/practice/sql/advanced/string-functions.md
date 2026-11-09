---
title: "Строковые функции"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Строковые функции в SQL: TRIM, SUBSTR | Инжиниринг Данных"
description: "Как чистить и разбирать текст в SQL с помощью LEFT, RIGHT, TRIM, SUBSTR, POSITION, CONCAT, UPPER и LOWER."
sidebar:
  order: 4
tags:
  - sql
  - practice
---

Строковые функции вырезают куски текста, убирают лишнее и склеивают значения. Они нужны, когда данные хранятся в неудобном виде. Например, дата в виде текста или две координаты в одной колонке.

В уроке работаем с таблицей `tutorial.sf_crime_incidents_2014_01` — инциденты, о которых сообщила полиция Сан-Франциско в январе 2014 года. Одна строка — один инцидент.

Важные колонки:

- `date` — текст вида `01/01/2014 08:00:00 AM +0000`;
- `time` — текст `HH:MM`;
- `location` — текст вида `(37.78, -122.42)`;
- `lat` и `lon` — те же координаты, но числами.

Начните с просмотра:

```sql
SELECT *
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 10;
```

## LEFT, RIGHT и LENGTH

`LEFT(текст, n)` берёт `n` символов слева. `RIGHT(текст, n)` — справа. `LENGTH(текст)` считает длину.

В колонке `date` первые 10 символов — это дата:

```sql
SELECT incidnt_num,
       date,
       LEFT(date, 10) AS cleaned_date
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Справа — время:

```sql
SELECT incidnt_num,
       date,
       LEFT(date, 10) AS cleaned_date,
       RIGHT(date, 17) AS cleaned_time
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

`RIGHT(date, 17)` работает, потому что длина везде одинаковая (28 символов). Если длина разная, считайте через `LENGTH`:

```sql
SELECT incidnt_num,
       date,
       LEFT(date, 10) AS cleaned_date,
       RIGHT(date, LENGTH(date) - 11) AS cleaned_time
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Функции можно вкладывать. Сначала работает самая внутренняя.

## TRIM

`TRIM` убирает символы с начала или конца текста.

```sql
SELECT location,
       TRIM(BOTH '()' FROM location) AS no_brackets
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Три части:

- `BOTH`, `LEADING` или `TRAILING` — откуда убирать (с обеих сторон, с начала, с конца);
- `'()'` — какие символы убирать (любой из них);
- `FROM location` — из какого текста.

Без параметров `TRIM(text)` убирает пробелы по краям.

## POSITION и STRPOS

Они возвращают номер символа, с которого подстрока начинается. Если подстроки нет, вернётся `0`. Регистр важен.

```sql
SELECT incidnt_num,
       descript,
       POSITION('A' IN descript) AS a_position
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Тот же результат даёт `STRPOS`. Порядок аргументов другой:

```sql
SELECT incidnt_num,
       descript,
       STRPOS(descript, 'A') AS a_position
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

:::note
`POSITION(... IN ...)` и `STRPOS` работают и в DuckDB, и в Postgres. Менять запросы не надо.
:::

Чтобы искать без учёта регистра, приведите текст к одному регистру через `UPPER` или `LOWER`.

## SUBSTR

`SUBSTR(текст, старт, длина)` вырезает кусок из середины. Номера символов начинаются с 1.

```sql
SELECT incidnt_num,
       date,
       SUBSTR(date, 4, 2) AS day
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

## CONCAT и ||

Склеить текст можно двумя способами:

```sql
SELECT incidnt_num,
       day_of_week,
       CONCAT(day_of_week, ' - ', category) AS day_and_category,
       day_of_week || ' - ' || category AS same_with_pipes
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Числа склеиваются с текстом без `CAST`.

:::caution
Если одно из значений `NULL`, то `||` вернёт `NULL`. А `CONCAT` пропустит `NULL` и склеит остальное. Это частая причина пустых результатов.
:::

## UPPER и LOWER

```sql
SELECT category,
       UPPER(category) AS upper_category,
       LOWER(category) AS lower_category
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

## Текст в дату

Дата в нашей таблице в американском формате. Соберём из неё `ГГГГ-ММ-ДД`:

```sql
SELECT incidnt_num,
       date,
       SUBSTR(date, 7, 4) || '-' || LEFT(date, 2) || '-' || SUBSTR(date, 4, 2) AS cleaned_date
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

Текст `ГГГГ-ММ-ДД` легко превратить в дату через `::DATE`. Для timestamp добавьте время `HH:MM:SS`.

:::tip
В DuckDB есть более короткий способ: `strptime(date, '%m/%d/%Y %I:%M:%S %p %z')`. Но разбор через `SUBSTR` показывает, как работают функции. На собеседованиях такие задачи любят.
:::

## Дата в более удобную дату

`DATE_TRUNC` обрезает timestamp до недели, месяца и других периодов. Для этого нужна колонка типа timestamp. В таблице `tutorial.sf_crime_incidents_cleandate` уже есть такая колонка — `cleaned_date`:

```sql
SELECT cleaned_date,
       DATE_TRUNC('week', cleaned_date) AS week_start,
       DATE_TRUNC('month', cleaned_date) AS month_start
FROM tutorial.sf_crime_incidents_cleandate
LIMIT 5;
```

## COALESCE

`COALESCE(a, b, c)` возвращает первое значение, которое не `NULL`. Так заменяют пропуски:

```sql
SELECT incidnt_num,
       descript,
       COALESCE(resolution, 'unknown') AS resolution
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Разделите колонку `location` на широту и долготу. Сравните результат с колонками `lat` и `lon`.

**Проверка:** 11969 строк. В первой строке широта `37.7884521578132`, долгота `-122.420326993863`. Значения совпадают с `lat` и `lon`. Следите за пробелом после запятой.

<details>
<summary>Решение</summary>

```sql
SELECT location,
       TRIM(LEADING '(' FROM LEFT(location, POSITION(',' IN location) - 1)) AS latitude,
       TRIM(TRAILING ')' FROM RIGHT(location, LENGTH(location) - POSITION(',' IN location) - 1)) AS longitude,
       lat,
       lon
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 2

Склейте `lat` и `lon` так, чтобы получилась колонка, равная `location`. Используйте `CONCAT`.

**Проверка:** 11969 строк. Склеенное значение совпадает с `location` во всех строках.

<details>
<summary>Решение</summary>

```sql
SELECT CONCAT('(', lat, ', ', lon, ')') AS concat_location,
       location
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 3

Сделайте ту же колонку, но через `||` вместо `CONCAT`.

**Проверка:** 11969 строк. Результат такой же, как в задании 2.

<details>
<summary>Решение</summary>

```sql
SELECT '(' || lat || ', ' || lon || ')' AS concat_location,
       location
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 4

Сделайте колонку с датой в формате `ГГГГ-ММ-ДД`.

**Проверка:** 11969 строк. В первой строке `2014-01-01`. Все даты между `2014-01-01` и `2014-01-31`.

<details>
<summary>Решение</summary>

```sql
SELECT incidnt_num,
       date,
       SUBSTR(date, 7, 4) || '-' || LEFT(date, 2) || '-' || SUBSTR(date, 4, 2) AS cleaned_date
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 5

Верните `category` так, чтобы первая буква была заглавной, а остальные строчными. Например `LARCENY/THEFT` станет `Larceny/theft`.

**Проверка:** 11969 строк. В первой строке `Larceny/theft`. Всего 32 разных значения.

<details>
<summary>Решение</summary>

```sql
SELECT incidnt_num,
       category,
       UPPER(LEFT(category, 1)) || LOWER(RIGHT(category, LENGTH(category) - 1)) AS category_cleaned
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 6

Соберите настоящий timestamp из колонок `date` и `time`. Добавьте колонку ровно на 1 неделю позже.

**Проверка:** 11969 строк. В первой строке `2014-01-01 00:01:00` и `2014-01-08 00:01:00`.

<details>
<summary>Решение</summary>

```sql
SELECT incidnt_num,
       (SUBSTR(date, 7, 4) || '-' || LEFT(date, 2) || '-' || SUBSTR(date, 4, 2)
        || ' ' || time || ':00')::TIMESTAMP AS ts,
       (SUBSTR(date, 7, 4) || '-' || LEFT(date, 2) || '-' || SUBSTR(date, 4, 2)
        || ' ' || time || ':00')::TIMESTAMP + INTERVAL '1 week' AS ts_plus_week
FROM tutorial.sf_crime_incidents_2014_01;
```

</details>

### Задание 7

Посчитайте инциденты по неделям. Таблица: `tutorial.sf_crime_incidents_cleandate`. Приведите неделю к `DATE`, чтобы убрать часы и минуты.

**Проверка:** 5 строк. Первая: `2013-12-30` — 1861. Последняя: `2014-01-27` — 1799.

<details>
<summary>Решение</summary>

```sql
SELECT DATE_TRUNC('week', cleaned_date)::DATE AS week_beginning,
       COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_cleandate
GROUP BY 1
ORDER BY 1;
```

</details>

### Задание 8

Покажите, сколько времени прошло с каждого инцидента до сейчас. Считайте, что данные в тихоокеанском времени (UTC-8).

**Проверка:** 11969 строк. Колонка `time_ago` — интервал. Результат зависит от даты запуска. Для инцидента `2014-01-01` это больше 4000 дней.

<details>
<summary>Решение</summary>

```sql
SELECT incidnt_num,
       cleaned_date,
       now() AT TIME ZONE 'PST' AS now_pst,
       now() AT TIME ZONE 'PST' - cleaned_date AS time_ago
FROM tutorial.sf_crime_incidents_cleandate;
```

</details>

:::note
В Postgres то же самое пишут `NOW() AT TIME ZONE 'PST'`. В DuckDB это тоже работает. Для переходов на летнее время надёжнее брать название зоны: `'America/Los_Angeles'`.
:::
