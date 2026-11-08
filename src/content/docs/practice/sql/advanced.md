---
title: "Продвинутый SQL"
description: "Четвёртый уровень курса: типы данных, даты, чистка данных, строки, подзапросы, оконные функции, производительность, pivot."
sidebar:
  label: "Продвинутый уровень"
tableOfContents:
  minHeadingLevel: 2
  maxHeadingLevel: 2
tags:
  - sql
  - practice
---

Четвёртый уровень. Вы чистите данные, пишете подзапросы и оконные функции, читаете план запроса.

Нужны знания из уровней [Основы](/practice/sql/basic/) и [Средний уровень](/practice/sql/intermediate/). Описание таблиц: [Учебные данные](/practice/sql/datasets/).

Решайте сами, без AI.

## Типы данных

Это первый урок продвинутого уровня. Дальше будут типы данных, даты, строки, подзапросы, оконные функции, скорость запросов и сводные таблицы.

Работаем так же, как раньше: сначала смотрите данные через `SELECT * ... LIMIT 10`, потом пишете запрос. Все примеры используют данные Crunchbase и других таблиц из [описания данных](/practice/sql/datasets/). В этом уроке берём `tutorial.crunchbase_companies_clean_date`.

Тема урока: у каждой колонки есть тип. Тип решает, какие функции работают. Если тип не тот, запрос упадёт. Тогда тип нужно поменять прямо в запросе.

### Основные типы

| Тип | Что хранит | Пример |
|---|---|---|
| `VARCHAR` | Текст любой длины | `'software'` |
| `INTEGER`, `BIGINT` | Целые числа | `42` |
| `DOUBLE` | Дробные числа | `37.78` |
| `DECIMAL(p, s)` | Точные дробные числа (деньги) | `19.99` |
| `BOOLEAN` | `TRUE` или `FALSE` | `TRUE` |
| `DATE` | Дата | `2014-03-01` |
| `TIMESTAMP` | Дата и время | `2014-03-01 13:45:00` |

Посмотреть типы таблицы можно так:

```sql
DESCRIBE tutorial.crunchbase_companies_clean_date;
```

Тип одного значения покажет `typeof`:

```sql
SELECT typeof(funding_total_usd) AS funding_type,
       typeof(founded_at_clean) AS founded_type
FROM tutorial.crunchbase_companies_clean_date
LIMIT 1;
```

Здесь `funding_total_usd` это `BIGINT`, а `founded_at_clean` это `VARCHAR`. Дата хранится как текст.

### Почему тип важен

- `COUNT` работает с любым типом.
- `SUM` и `AVG` работают только с числами.
- Дату в виде текста нельзя сложить с интервалом без приведения типа.

Пример ошибки. Колонка `founded_at_clean` это текст:

```sql
-- ошибка
SELECT SUM(founded_at_clean)
FROM tutorial.crunchbase_companies_clean_date;
```

:::caution
Число с запятой или знаком валюты (`'1,000'`, `'$5'`) база не считает числом. Это текст. Сначала уберите лишние символы через `REPLACE`, потом меняйте тип.
:::

### Как поменять тип: CAST и ::

Есть два способа. Результат одинаковый.

```sql
SELECT CAST(funding_total_usd AS VARCHAR) AS funding_total_usd_string,
       founded_at_clean::VARCHAR AS founded_at_string
FROM tutorial.crunchbase_companies_clean_date;
```

- `CAST(значение AS тип)` — стандарт SQL. Работает везде.
- `значение::тип` — короткая запись. Работает в DuckDB и Postgres.

Можно менять тип и в другую сторону. Все значения колонки должны подходить к новому типу:

```sql
SELECT permalink,
       founded_at_clean::DATE AS founded_date
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

### TRY_CAST

Если одно значение не подходит, `CAST` роняет весь запрос. `TRY_CAST` вместо ошибки вернёт `NULL`:

```sql
SELECT TRY_CAST('1,000' AS INTEGER) AS bad_value,
       TRY_CAST('1000' AS INTEGER) AS good_value;
```

:::tip
`TRY_CAST` удобен, когда в колонке с числами есть мусор. Потом посчитайте, сколько `NULL` получилось. Так вы поймёте, сколько данных грязные.
:::

:::note
Деление в DuckDB: `7 / 2` даёт `3.5`. В Postgres `7 / 2` даёт `3`, потому что оба числа целые. Целое деление в DuckDB пишется `7 // 2`. Если переносите запрос из Postgres, проверьте деление.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

В таблице `tutorial.crunchbase_companies_clean_date` приведите `funding_total_usd` к тексту. Посчитайте компании, у которых в записи 9 и больше цифр.

**Проверка:** 1666.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
WHERE LENGTH(CAST(funding_total_usd AS VARCHAR)) >= 9;
```

</details>

#### Задание 2

Приведите `founded_at_clean` к типу `DATE`. Посчитайте компании, основанные в 2010 году. Используйте сравнение дат, а не колонку `founded_year`.

**Проверка:** 4253.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean::DATE >= '2010-01-01'
  AND founded_at_clean::DATE < '2011-01-01';
```

</details>

#### Задание 3

В таблице `tutorial.sf_crime_incidents_2014_01` номер инцидента `incidnt_num` это число. Превратите его в текст и возьмите первые 2 символа. Посчитайте, сколько инцидентов на каждое значение. Покажите сначала самое частое.

**Проверка:** 3 строки. Первая: `14` — 11879 инцидентов.

<details>
<summary>Решение</summary>

```sql
SELECT LEFT(incidnt_num::VARCHAR, 2) AS prefix,
       COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

## Формат дат и времени

Даты в SQL часто приходят в плохом виде: как текст, в разных форматах. Если не привести их к `DATE` или `TIMESTAMP`, сортировка и расчёты будут неверными.

В этом уроке работаем с таблицами `tutorial.crunchbase_companies_clean_date` и `tutorial.crunchbase_acquisitions_clean_date`. Подробнее — в [описании данных](/practice/sql/datasets/).

### Почему год идёт первым

Американский формат `М/Д/ГГ` (например `9/4/14`) удобен человеку. Но как текст он не сортируется по времени. Текст сравнивается по символам слева направо.

```sql
SELECT permalink,
       founded_at
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at IS NOT NULL
ORDER BY founded_at
LIMIT 5;
```

Первыми придут строки, которые начинаются с `1/1/00`. Потом `1/1/01`... Но `1/30/15` будет раньше, чем `2/1/05`. Порядок неверный.

Формат `ГГГГ-ММ-ДД` решает проблему. Текст в этом формате сортируется так же, как даты:

```sql
SELECT permalink,
       founded_at,
       founded_at_clean
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at IS NOT NULL
ORDER BY founded_at_clean
LIMIT 5;
```

:::note
Колонка `founded_at_clean` в нашей базе содержит и странные годы. Например `1015-01-30`. Это ошибка в исходных данных (двузначный год `15` разобран неверно). Такие строки лучше фильтровать.
:::

### Арифметика с датами

Разница двух дат или timestamp — это тип `INTERVAL`. Колонка `founded_at_clean` это текст. Поэтому сначала приведите её к `TIMESTAMP`.

Сколько времени прошло от основания до продажи компании:

```sql
SELECT companies.permalink,
       companies.founded_at_clean,
       acquisitions.acquired_at_cleaned,
       acquisitions.acquired_at_cleaned - companies.founded_at_clean::TIMESTAMP AS time_to_acquisition
FROM tutorial.crunchbase_companies_clean_date companies
JOIN tutorial.crunchbase_acquisitions_clean_date acquisitions
  ON acquisitions.company_permalink = companies.permalink
WHERE companies.founded_at_clean IS NOT NULL;
```

Результат — интервал в днях, например `1336 days`.

### INTERVAL

Интервал можно записать словами: `'1 week'`, `'3 years'`, `'10 seconds'`. Дата плюс интервал даёт новую дату:

```sql
SELECT permalink,
       founded_at_clean,
       founded_at_clean::TIMESTAMP + INTERVAL '1 week' AS plus_one_week
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

### Текущее время

`now()` возвращает текущий момент:

```sql
SELECT permalink,
       founded_at_clean,
       now() - founded_at_clean::TIMESTAMP AS founded_time_ago
FROM tutorial.crunchbase_companies_clean_date
WHERE founded_at_clean IS NOT NULL
LIMIT 5;
```

Результат зависит от дня запуска. Это нормально.

### Полезные функции DuckDB

| Задача | DuckDB | Результат |
|---|---|---|
| Формат даты в текст | `strftime(d, '%d.%m.%Y')` | `05.03.2014` |
| Часть даты | `date_part('year', d)` или `EXTRACT(year FROM d)` | `2014` |
| Разница в днях | `date_diff('day', d1, d2)` | `59` |
| Разница «как у человека» | `age(d2, d1)` | `2 years 1 month 17 days` |
| Начало месяца | `date_trunc('month', d)` | `2014-03-01` |
| Текст в дату | `strptime('03/05/2014', '%m/%d/%Y')` | `2014-03-05` |

```sql
SELECT strftime(DATE '2014-03-05', '%d.%m.%Y') AS formatted,
       date_part('year', DATE '2014-03-05') AS year,
       date_diff('day', DATE '2014-01-01', DATE '2014-03-01') AS days,
       age(DATE '2014-03-01', DATE '2012-01-15') AS human_age,
       date_trunc('month', DATE '2014-03-05') AS month_start;
```

:::note
В Postgres для формата даты используют `TO_CHAR(d, 'DD.MM.YYYY')`. В DuckDB такой функции нет. Используйте `strftime`. Коды формата другие: `%Y` год, `%m` месяц, `%d` день, `%H` час, `%M` минуты.
:::

:::tip
Хотите дату плюс 7 дней? `d::DATE + 7` работает в DuckDB и Postgres. Для месяцев и лет используйте `INTERVAL`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который считает компании, проданные в течение 3, 5 и 10 лет после основания. Каждый срок — в отдельной колонке. Добавьте колонку с общим числом проданных компаний. Группируйте по `category_code`. Берите только компании с датой основания. Покажите сначала категории с самым большим общим числом.

**Проверка:** 331 строка. Первая строка: `software` — 44, 92, 270 и всего 470.

<details>
<summary>Решение</summary>

```sql
SELECT companies.category_code,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '3 years'
                  THEN 1 END) AS acquired_3_yrs,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '5 years'
                  THEN 1 END) AS acquired_5_yrs,
       COUNT(CASE WHEN acquisitions.acquired_at_cleaned <= companies.founded_at_clean::TIMESTAMP + INTERVAL '10 years'
                  THEN 1 END) AS acquired_10_yrs,
       COUNT(1) AS total
FROM tutorial.crunchbase_companies_clean_date companies
JOIN tutorial.crunchbase_acquisitions_clean_date acquisitions
  ON acquisitions.company_permalink = companies.permalink
WHERE companies.founded_at_clean IS NOT NULL
GROUP BY 1
ORDER BY 5 DESC;
```

</details>

## Подготовка данных (data wrangling)

Data wrangling (или data munging) — это превращение «сырых» данных в удобный вид. Данные редко приходят чистыми. Их вводят люди, их собирают сайты, их выгружают из Excel. Поэтому аналитик тратит на чистку много времени.

В этом уроке нет новых функций. Мы собираем план: что обычно сломано и чем это чинить. Работаем с таблицами `tutorial.crunchbase_companies_clean_date` и `tutorial.sf_crime_incidents_2014_01`. Подробнее — в [описании данных](/practice/sql/datasets/).

### Что обычно сломано

| Проблема | Пример в наших данных | Чем чинить |
|---|---|---|
| Дата хранится как текст | `founded_at = '9/4/14'` | `strptime`, `CAST`, `SUBSTR` |
| Число хранится как текст | `'1,000'` | `REPLACE` + `CAST`, `TRY_CAST` |
| Лишние символы | `location = '(37.78, -122.42)'` | `TRIM`, `REPLACE` |
| Разный регистр и пробелы | `'Software '`, `'SOFTWARE'` | `LOWER`, `TRIM` |
| Несколько значений в одной колонке | `'1200 Block of POLK ST'` | `SUBSTR`, `POSITION`, `LEFT` |
| Пропуски | `category_code IS NULL` | `COALESCE`, `CASE` |
| Дубли | Одна компания в двух строках | `DISTINCT`, `GROUP BY` |

Про функции для строк — в [уроке про строки](/practice/sql/advanced/#строковые-функции). Про даты — в [уроке про даты](/practice/sql/advanced/#формат-дат-и-времени).

### Пример: чистим домен

В колонке `homepage_url` лежит полный адрес. Нам нужен только домен. Уберём `https://`, `http://` и `www.`:

```sql
SELECT homepage_url,
       REPLACE(REPLACE(REPLACE(homepage_url, 'https://', ''), 'http://', ''), 'www.', '') AS domain
FROM tutorial.crunchbase_companies_clean_date
WHERE homepage_url IS NOT NULL
LIMIT 5;
```

Функции вложены друг в друга. Сначала работает самая внутренняя.

### Пример: заполняем пропуски

`COALESCE` берёт первое значение, которое не `NULL`:

```sql
SELECT COALESCE(category_code, 'unknown') AS category,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies_clean_date
GROUP BY 1
ORDER BY 2 DESC
LIMIT 5;
```

### Пример: делим одну колонку на две

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

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

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

#### Задание 2

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

#### Задание 3

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

## Строковые функции

Строковые функции вырезают куски текста, убирают лишнее и склеивают значения. Они нужны, когда данные хранятся в неудобном виде. Например, дата в виде текста или две координаты в одной колонке.

В уроке работаем с таблицей `tutorial.sf_crime_incidents_2014_01` — инциденты, о которых сообщила полиция Сан-Франциско в январе 2014 года. Одна строка — один инцидент. Подробнее — в [описании данных](/practice/sql/datasets/).

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

### LEFT, RIGHT и LENGTH

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

### TRIM

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

### POSITION и STRPOS

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

### SUBSTR

`SUBSTR(текст, старт, длина)` вырезает кусок из середины. Номера символов начинаются с 1.

```sql
SELECT incidnt_num,
       date,
       SUBSTR(date, 4, 2) AS day
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

### CONCAT и ||

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

### UPPER и LOWER

```sql
SELECT category,
       UPPER(category) AS upper_category,
       LOWER(category) AS lower_category
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

### Текст в дату

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

### Дата в более удобную дату

`DATE_TRUNC` обрезает timestamp до недели, месяца и других периодов. Для этого нужна колонка типа timestamp. В таблице `tutorial.sf_crime_incidents_cleandate` уже есть такая колонка — `cleaned_date`:

```sql
SELECT cleaned_date,
       DATE_TRUNC('week', cleaned_date) AS week_start,
       DATE_TRUNC('month', cleaned_date) AS month_start
FROM tutorial.sf_crime_incidents_cleandate
LIMIT 5;
```

### COALESCE

`COALESCE(a, b, c)` возвращает первое значение, которое не `NULL`. Так заменяют пропуски:

```sql
SELECT incidnt_num,
       descript,
       COALESCE(resolution, 'unknown') AS resolution
FROM tutorial.sf_crime_incidents_2014_01
LIMIT 5;
```

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

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

#### Задание 2

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

#### Задание 3

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

#### Задание 4

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

#### Задание 5

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

#### Задание 6

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

#### Задание 7

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

#### Задание 8

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

## Подзапросы

Подзапрос (вложенный запрос) — это запрос внутри другого запроса. Он нужен, когда задачу нельзя решить за один шаг. Например: сначала посчитать суммы, потом усреднить их.

Работаем с таблицами `tutorial.sf_crime_incidents_2014_01`, `tutorial.sf_crime_incidents_cleandate` и таблицами Crunchbase. Подробнее — в [описании данных](/practice/sql/datasets/).

### Основы

Самое простое место для подзапроса — `FROM`:

```sql
SELECT sub.*
FROM (
      SELECT *
      FROM tutorial.sf_crime_incidents_2014_01
      WHERE day_of_week = 'Friday'
     ) sub
WHERE sub.resolution = 'NONE';
```

Как это работает:

1. База выполняет внутренний запрос в скобках.
2. Результат становится временной таблицей `sub`.
3. Внешний запрос работает с `sub`.

Правила:

- Внутренний запрос должен работать сам по себе. Проверьте его отдельно.
- Подзапрос в `FROM` нужно назвать (`sub`).
- Делайте отступы. Читатель должен видеть, где подзапрос.

:::note
В Postgres у подзапроса в `FROM` тоже обязателен псевдоним. В DuckDB он необязателен, но лучше всегда писать его.
:::

### Агрегация в несколько шагов

Нужно среднее число инцидентов в день для каждой категории. Это два шага:

1. Посчитать инциденты по дням и категориям.
2. Усреднить по дням.

```sql
SELECT sub.category,
       AVG(sub.incidents) AS avg_incidents_per_day
FROM (
      SELECT cleaned_date::DATE AS day,
             category,
             COUNT(*) AS incidents
      FROM tutorial.sf_crime_incidents_cleandate
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

Один `GROUP BY` здесь не поможет. Нельзя написать `AVG(COUNT(*))`.

### Подзапрос в условии

Подзапрос можно поставить в `WHERE`. Есть два вида.

Подзапрос возвращает одно значение:

```sql
SELECT COUNT(*) AS incidents
FROM tutorial.sf_crime_incidents_2014_01
WHERE category = (
      SELECT category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      ORDER BY COUNT(*) DESC
      LIMIT 1
     );
```

Подзапрос возвращает список. Тогда используйте `IN`:

```sql
SELECT *
FROM tutorial.sf_crime_incidents_2014_01
WHERE category IN (
      SELECT category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      HAVING COUNT(*) < 5
     );
```

:::caution
Если подзапрос с `=` вернёт больше одной строки, будет ошибка. Для списка всегда пишите `IN`.
:::

### JOIN с подзапросом

Сначала сожмите данные подзапросом, потом присоедините. Так JOIN работает быстрее. Покажем каждый инцидент и общее число инцидентов его категории:

```sql
SELECT incidents.incidnt_num,
       incidents.category,
       sub.total_in_category
FROM tutorial.sf_crime_incidents_2014_01 incidents
JOIN (
      SELECT category,
             COUNT(*) AS total_in_category
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
     ) sub
  ON sub.category = incidents.category;
```

### Подзапросы и UNION

В Crunchbase данные об инвестициях разделены на две таблицы. `UNION ALL` собирает их вместе. Подзапрос даёт общий результат для дальнейшей работы:

```sql
SELECT COUNT(*) AS rows_total
FROM (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) sub;
```

:::tip
Подзапрос в `FROM` можно заменить на `WITH` (CTE). Это то же самое, но читается лучше. Пример: `WITH sub AS (SELECT ...) SELECT * FROM sub;`
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Выберите все аресты по ордеру (`descript = 'WARRANT ARREST'`) из `tutorial.sf_crime_incidents_2014_01`. Оберните запрос внешним запросом, который покажет только нераскрытые инциденты (`resolution = 'NONE'`).

**Проверка:** 16 строк.

<details>
<summary>Решение</summary>

```sql
SELECT sub.*
FROM (
      SELECT *
      FROM tutorial.sf_crime_incidents_2014_01
      WHERE descript = 'WARRANT ARREST'
     ) sub
WHERE sub.resolution = 'NONE';
```

</details>

#### Задание 2

Покажите среднее число инцидентов для каждой категории. Подсказка: используйте `tutorial.sf_crime_incidents_cleandate`. Данные охватывают один месяц, поэтому считайте среднее в день, а не в месяц.

**Проверка:** 32 строки. Первая: `LARCENY/THEFT` — около 94.39.

<details>
<summary>Решение</summary>

```sql
SELECT sub.category,
       AVG(sub.incidents) AS avg_incidents_per_day
FROM (
      SELECT cleaned_date::DATE AS day,
             category,
             COUNT(*) AS incidents
      FROM tutorial.sf_crime_incidents_cleandate
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

#### Задание 3

Покажите все строки из трёх категорий с наименьшим числом инцидентов. Добавьте колонку с общим числом инцидентов категории.

**Проверка:** 4 строки. Категории: `BAD CHECKS` (1), `BRIBERY` (1) и `EXTORTION` (2).

<details>
<summary>Решение</summary>

```sql
SELECT incidents.*,
       sub.count AS total_incidents_in_category
FROM tutorial.sf_crime_incidents_2014_01 incidents
JOIN (
      SELECT category,
             COUNT(*) AS count
      FROM tutorial.sf_crime_incidents_2014_01
      GROUP BY 1
      ORDER BY 2
      LIMIT 3
     ) sub
  ON sub.category = incidents.category;
```

</details>

#### Задание 4

Посчитайте, сколько компаний основано и сколько куплено по кварталам, начиная с Q1 2012 и до Q4 2015 включительно. Сделайте два отдельных запроса с агрегацией, потом соедините их. Таблицы: `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`.

**Проверка:** 16 строк. Первая: `2012-Q1` — основано 3581, куплено 445. Последняя: `2015-Q4` — основано 48, куплено 926.

<details>
<summary>Решение</summary>

```sql
SELECT COALESCE(companies.quarter, acquisitions.quarter) AS quarter,
       companies.companies_founded,
       acquisitions.companies_acquired
FROM (
      SELECT founded_quarter AS quarter,
             COUNT(permalink) AS companies_founded
      FROM tutorial.crunchbase_companies
      WHERE founded_year BETWEEN 2012 AND 2015
      GROUP BY 1
     ) companies
FULL JOIN (
      SELECT acquired_quarter AS quarter,
             COUNT(DISTINCT company_permalink) AS companies_acquired
      FROM tutorial.crunchbase_acquisitions
      WHERE acquired_year BETWEEN 2012 AND 2015
      GROUP BY 1
     ) acquisitions
  ON companies.quarter = acquisitions.quarter
ORDER BY 1;
```

</details>

:::note
Мы ограничили годы значением 2015. В данных есть неверные даты, например `2041-Q3` и `3201-Q4`. Это ошибки источника.
:::

#### Задание 5

Объедините две таблицы инвестиций (`crunchbase_investments_part1` и `crunchbase_investments_part2`). Составьте рейтинг инвесторов по общему числу инвестиций.

**Проверка:** 30190 строк (одна из них с `NULL` вместо имени). Первая: `Sequoia Capital` — 1033.

<details>
<summary>Решение</summary>

```sql
SELECT investor_name,
       COUNT(*) AS investments
FROM (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) sub
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>

#### Задание 6

Сделайте то же, что в задании 5, но только для компаний, которые ещё работают. Подсказка: статус хранится в `tutorial.crunchbase_companies` (`status = 'operating'`).

**Проверка:** 26257 строк (одна из них с `NULL` вместо имени). Первая: `Wayra` — 877.

<details>
<summary>Решение</summary>

```sql
SELECT investments.investor_name,
       COUNT(*) AS investments
FROM tutorial.crunchbase_companies companies
JOIN (
      SELECT *
      FROM tutorial.crunchbase_investments_part1

      UNION ALL

      SELECT *
      FROM tutorial.crunchbase_investments_part2
     ) investments
  ON investments.company_permalink = companies.permalink
WHERE companies.status = 'operating'
GROUP BY 1
ORDER BY 2 DESC, 1;
```

</details>

## Оконные функции

Оконная функция считает значение по группе связанных строк, но не схлопывает их в одну. Каждая строка остаётся в результате. Это отличие от `GROUP BY`.

Типичные задачи: накопительная сумма, ранг, доля от общей суммы, сравнение с предыдущей строкой. Оконные функции часто спрашивают на собеседованиях.

Работаем с таблицей `tutorial.dc_bikeshare_q1_2012` — поездки Capital Bikeshare в Вашингтоне за первый квартал 2012 года. Одна строка — одна поездка. Поле `rider_type`: `Registered` — подписка, `Casual` — разовый билет. Подробнее — в [описании данных](/practice/sql/datasets/).

### Накопительная сумма

```sql
SELECT duration_seconds,
       SUM(duration_seconds) OVER (ORDER BY start_time) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
LIMIT 10;
```

Здесь нет `GROUP BY`. `SUM(...) OVER (...)` читается так: «сумма `duration_seconds` по всем строкам, по порядку `start_time`».

### PARTITION BY

`PARTITION BY` делит строки на группы. Внутри каждой группы окно считается заново:

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, start_time
LIMIT 10;
```

Если убрать `ORDER BY` из `OVER`, то в каждой строке будет сумма всей группы:

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal) AS start_terminal_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

`PARTITION BY` и `ORDER BY` вместе задают «окно».

:::caution
Оконную функцию нельзя писать в `WHERE` и в `GROUP BY`. Если нужно отфильтровать по её результату, оберните запрос в подзапрос.
:::

### COUNT, SUM, AVG

Это обычные агрегаты. С `OVER` они становятся оконными:

```sql
SELECT start_terminal,
       duration_seconds,
       COUNT(*) OVER (PARTITION BY start_terminal) AS rides_in_terminal,
       AVG(duration_seconds) OVER (PARTITION BY start_terminal) AS avg_duration
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

### ROW_NUMBER, RANK, DENSE_RANK

Все три нумеруют строки внутри окна. Разница в том, как они обрабатывают одинаковые значения.

| Функция | Что делает при одинаковых значениях |
|---|---|
| `ROW_NUMBER()` | Всегда разные номера: 1, 2, 3, 4 |
| `RANK()` | Одинаковый номер, потом пропуск: 1, 2, 2, 4 |
| `DENSE_RANK()` | Одинаковый номер, без пропуска: 1, 2, 2, 3 |

```sql
SELECT start_terminal,
       duration_seconds,
       ROW_NUMBER() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS row_num,
       RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank,
       DENSE_RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS dense_rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, duration_seconds DESC
LIMIT 10;
```

### NTILE

`NTILE(n)` делит строки на `n` равных групп. `NTILE(4)` даёт квартили, `NTILE(100)` даёт процентили:

```sql
SELECT duration_seconds,
       NTILE(4) OVER (ORDER BY duration_seconds) AS quartile
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
LIMIT 10;
```

### LAG и LEAD

`LAG` берёт значение из предыдущей строки. `LEAD` — из следующей:

```sql
SELECT start_terminal,
       start_time,
       duration_seconds,
       LAG(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS previous_duration,
       LEAD(duration_seconds) OVER (PARTITION BY start_terminal ORDER BY start_time) AS next_duration
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY start_terminal, start_time
LIMIT 10;
```

У первой строки группы нет предыдущей. Там будет `NULL`.

### Псевдоним окна

Если одно окно нужно несколько раз, дайте ему имя через `WINDOW`:

```sql
SELECT start_terminal,
       duration_seconds,
       ROW_NUMBER() OVER w AS row_num,
       RANK() OVER w AS rank,
       DENSE_RANK() OVER w AS dense_rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
WINDOW w AS (PARTITION BY start_terminal ORDER BY duration_seconds DESC)
LIMIT 10;
```

`WINDOW` пишется после `WHERE` и `GROUP BY`, перед `ORDER BY`.

### QUALIFY в DuckDB

Чтобы отфильтровать по оконной функции, в других базах нужен подзапрос. В DuckDB есть `QUALIFY`. Он работает как `WHERE`, но для оконных функций:

```sql
SELECT start_terminal,
       start_time,
       duration_seconds,
       RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
QUALIFY rank <= 5
ORDER BY start_terminal, rank;
```

:::note
`QUALIFY` есть в DuckDB, Snowflake и BigQuery. В Postgres его нет. Там пишут подзапрос с `WHERE rank <= 5` (смотрите задание 3).
:::

:::note
Деление `duration_seconds / SUM(...)` в DuckDB даёт дробное число. В Postgres два целых числа дадут целое (обычно `0`). Там нужно привести одно число к `DOUBLE PRECISION` или `NUMERIC`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Измените пример с `PARTITION BY start_terminal` так, чтобы он показывал длительность каждой поездки как процент от общего времени всех поездок с этого `start_terminal`. Берите поездки до 8 января 2012 (`start_time < '2012-01-08'`). Сортируйте по `start_terminal`, потом по проценту от большего к меньшему.

**Проверка:** 20558 строк. Первая: терминал `31000`, `duration_seconds` 3340, сумма по терминалу 12207, около 27.36%.

<details>
<summary>Решение</summary>

```sql
SELECT start_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY start_terminal) AS start_terminal_sum,
       (duration_seconds / SUM(duration_seconds) OVER (PARTITION BY start_terminal)) * 100 AS pct_of_total_time
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY 1, 4 DESC;
```

</details>

#### Задание 2

Покажите накопительную сумму длительности поездок по `end_terminal`. Внутри терминала сортируйте длительность от большей к меньшей. Берите поездки до 8 января 2012.

**Проверка:** 20558 строк. Для `end_terminal` 31000 первые строки: 3097 (накопительно 3097), 3069 (накопительно 6166).

<details>
<summary>Решение</summary>

```sql
SELECT end_terminal,
       duration_seconds,
       SUM(duration_seconds) OVER (PARTITION BY end_terminal ORDER BY duration_seconds DESC) AS running_total
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY end_terminal, duration_seconds DESC;
```

</details>

#### Задание 3

Покажите 5 самых долгих поездок с каждого `start_terminal`. Сортируйте по терминалу, внутри — от самой долгой к самой короткой. Берите поездки до 8 января 2012.

**Проверка:** 667 строк (при равных значениях `RANK` может дать больше 5 строк на терминал). Первая: терминал `31000`, `start_time` `2012-01-05 17:25:44`, `trip_time` 3340, ранг 1.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM (
      SELECT start_terminal,
             start_time,
             duration_seconds AS trip_time,
             RANK() OVER (PARTITION BY start_terminal ORDER BY duration_seconds DESC) AS rank
      FROM tutorial.dc_bikeshare_q1_2012
      WHERE start_time < '2012-01-08'
     ) sub
WHERE sub.rank <= 5
ORDER BY start_terminal, rank;
```

</details>

#### Задание 4

Покажите только длительность поездки и процентиль, в который она попадает. Считайте по всему набору данных, без `PARTITION BY`. Берите поездки до 8 января 2012. Сначала самые долгие.

**Проверка:** 20558 строк. Первая строка: 70005 секунд, процентиль 100.

<details>
<summary>Решение</summary>

```sql
SELECT duration_seconds,
       NTILE(100) OVER (ORDER BY duration_seconds) AS percentile
FROM tutorial.dc_bikeshare_q1_2012
WHERE start_time < '2012-01-08'
ORDER BY 1 DESC;
```

</details>

## Скорость запросов

Быстрый запрос делает меньше работы. Цель настройки скорости: чтобы база обработала меньше строк и сделала меньше вычислений.

В уроке работаем с таблицей `benn.sample_event_table` (1 миллион событий пользователей за первое полугодие 2014) и таблицами `benn.college_football_players` и `benn.college_football_teams`. Подробнее — в [описании данных](/practice/sql/datasets/).

### От чего зависит время запроса

Вы можете влиять на это:

- **Размер таблицы.** Чем больше строк, тем дольше.
- **JOIN.** Если JOIN сильно увеличивает число строк, запрос будет медленным.
- **Агрегации.** Свёртка строк требует больше вычислений, чем простое чтение.

Вы не можете влиять на это:

- другие пользователи, которые запускают запросы в то же время;
- настройки и версия базы.

:::note
DuckDB работает локально и очень быстро на таких объёмах. Разницу в секундах вы не увидите. Поэтому смотрите на план запроса и число обработанных строк. На больших данных в облачных базах разница будет заметна.
:::

### Сначала уменьшите таблицу

Фильтруйте данные как можно раньше. Для временных рядов хорошо работает ограничение по периоду:

```sql
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01';
```

`LIMIT` помогает при исследовании. Достаточно 100 строк, чтобы понять структуру данных:

```sql
SELECT *
FROM benn.sample_event_table
LIMIT 100;
```

#### LIMIT и агрегации

`LIMIT` работает после агрегации. Поэтому он не ускорит такой запрос:

```sql
SELECT COUNT(*)
FROM benn.sample_event_table
LIMIT 100;
```

База всё равно посчитает все строки, а потом покажет одну строку. Чтобы посчитать только по 100 строкам, поставьте `LIMIT` в подзапрос:

```sql
SELECT COUNT(*)
FROM (
      SELECT *
      FROM benn.sample_event_table
      LIMIT 100
     ) sub;
```

:::caution
Так вы меняете результат. Используйте `LIMIT` только чтобы проверить логику. Итоговые цифры считайте на полных данных.
:::

Правило: ограничивайте данные там, где запрос выполняется первым. Это внутренний подзапрос, а не внешний.

### Сделайте JOIN проще

Тот же принцип: уменьшайте таблицы до `JOIN`, а не после. Вот запрос, который присоединяет команды к игрокам:

```sql
SELECT teams.conference AS conference,
       players.school_name,
       COUNT(1) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1, 2;
```

В `benn.college_football_players` 6935 строк. Все они проверяются на совпадение. Сначала сожмите игроков до одной строки на школу. Таких школ 73:

```sql
SELECT players.school_name,
       COUNT(*) AS players
FROM benn.college_football_players players
GROUP BY 1;
```

Теперь `JOIN` обрабатывает 73 строки вместо 6935:

```sql
SELECT teams.conference,
       sub.*
FROM (
      SELECT players.school_name,
             COUNT(*) AS players
      FROM benn.college_football_players players
      GROUP BY 1
     ) sub
JOIN benn.college_football_teams teams
  ON teams.school_name = sub.school_name;
```

:::tip
Сначала добейтесь верного результата. Потом ускоряйте. Быстрый неверный запрос бесполезен.
:::

### EXPLAIN

`EXPLAIN` перед запросом показывает план: в каком порядке база выполнит шаги. Сам запрос не выполняется.

```sql
EXPLAIN
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
LIMIT 100;
```

План DuckDB — это дерево из блоков. Как его читать:

- Читайте снизу вверх. Нижний блок выполняется первым.
- `SEQ_SCAN` — чтение таблицы. Внутри блока строка `Filters` показывает фильтр по датам. Он применяется прямо при чтении.
- `STREAMING_LIMIT` — ограничение `LIMIT 100`. Оно останавливает чтение, когда набрано 100 строк.
- `PROJECTION` — выбор колонок.
- `~N rows` — оценка числа строк. Это только прикидка.
- `HASH_JOIN` и `HASH_GROUP_BY` встречаются в планах с `JOIN` и `GROUP BY`.

:::note
В Postgres `EXPLAIN` выглядит иначе. Это текст со строками `Seq Scan`, `Filter` и числами `cost=...`. Читают его тоже снизу вверх. В DuckDB `cost` нет, есть оценка числа строк.
:::

### EXPLAIN ANALYZE

`EXPLAIN ANALYZE` запускает запрос по-настоящему. Он показывает реальное число строк и время каждого шага:

```sql
EXPLAIN ANALYZE
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
LIMIT 100;
```

Вместо оценки `~N rows` вы увидите точные `N rows` и время в секундах. Обратите внимание на `SEQ_SCAN`. Он прочитал лишь несколько сотен строк, а не миллион. `LIMIT` остановил чтение.

Так работает практика: запустите `EXPLAIN ANALYZE`, найдите самый дорогой шаг, измените запрос, запустите снова и сравните.

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

В этом уроке не было задач в оригинале. Ниже три задачи, которые проверяют тему.

#### Задание 1

Посчитайте число событий в `benn.sample_event_table` за март 2014 по типам событий (`event_name`). Сначала самые частые. Потом добавьте `EXPLAIN` и найдите в плане строку `Filters`.

**Проверка:** 6 строк. Первая: `search_run` — 28937. Сумма по всем строкам — 171551.

<details>
<summary>Решение</summary>

```sql
SELECT event_name,
       COUNT(*) AS events
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

#### Задание 2

Напишите запрос, который показывает конференцию, школу и число игроков. Сначала сожмите игроков по школам в подзапросе, потом присоедините `benn.college_football_teams`. Сначала школы с самым большим числом игроков, потом по алфавиту.

**Проверка:** 73 строки. Первая: `Auburn` (конференция `Southeastern`) — 110 игроков.

<details>
<summary>Решение</summary>

```sql
SELECT teams.conference,
       sub.school_name,
       sub.players
FROM (
      SELECT school_name,
             COUNT(*) AS players
      FROM benn.college_football_players
      GROUP BY 1
     ) sub
JOIN benn.college_football_teams teams
  ON teams.school_name = sub.school_name
ORDER BY sub.players DESC, sub.school_name;
```

</details>

#### Задание 3

Запустите `EXPLAIN ANALYZE` для запроса `SELECT * FROM benn.sample_event_table LIMIT 100`. Посмотрите, сколько строк прочитал `TABLE_SCAN` и сколько строк прошло через `STREAMING_LIMIT`. Сравните с числом строк в таблице.

**Проверка:** через `STREAMING_LIMIT` проходит ровно 100 строк. `TABLE_SCAN` прочитал намного меньше миллиона строк.

<details>
<summary>Решение</summary>

```sql
EXPLAIN ANALYZE
SELECT *
FROM benn.sample_event_table
LIMIT 100;
```

</details>

## Сводные таблицы (PIVOT)

Pivot (сводная таблица) разворачивает данные. Строки превращаются в колонки или колонки в строки. Первое нужно для отчёта и графика. Второе нужно, чтобы данные удобно считались.

В уроке работаем с таблицами `benn.college_football_players`, `benn.college_football_teams` и `tutorial.worldwide_earthquakes`. Подробнее — в [описании данных](/practice/sql/datasets/).

### Строки в колонки

Задача: показать для каждой конференции число игроков по курсам (`FR`, `SO`, `JR`, `SR`). Результат должен быть такой:

| conference | fr | so | jr | sr |
|---|---|---|---|---|
| Atlantic Coast | 215 | 175 | 172 | 143 |

Начните с агрегации. Сколько игроков каждого курса в каждой конференции:

```sql
SELECT teams.conference AS conference,
       players.year,
       COUNT(1) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1, 2
ORDER BY 1, 2;
```

Положите этот запрос в подзапрос. Сначала проверьте, что `SELECT * FROM (...) sub` даёт те же строки. Так проще найти ошибку. `ORDER BY` из подзапроса уберите: внешний запрос всё равно сортирует.

Каждый столбец результата — отдельное выражение в `SELECT`. Для каждого курса пишем `SUM(CASE ...)`:

```sql
SELECT conference,
       SUM(CASE WHEN year = 'FR' THEN players ELSE NULL END) AS fr,
       SUM(CASE WHEN year = 'SO' THEN players ELSE NULL END) AS so,
       SUM(CASE WHEN year = 'JR' THEN players ELSE NULL END) AS jr,
       SUM(CASE WHEN year = 'SR' THEN players ELSE NULL END) AS sr
FROM (
      SELECT teams.conference AS conference,
             players.year,
             COUNT(1) AS players
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 1;
```

Как это работает: `CASE` оставляет число только в нужной колонке. В остальных колонках будет `NULL`. `SUM` игнорирует `NULL`. `GROUP BY` собирает строки конференции в одну.

Добавим колонку «всего игроков» и отсортируем по ней:

```sql
SELECT conference,
       SUM(players) AS total_players,
       SUM(CASE WHEN year = 'FR' THEN players ELSE NULL END) AS fr,
       SUM(CASE WHEN year = 'SO' THEN players ELSE NULL END) AS so,
       SUM(CASE WHEN year = 'JR' THEN players ELSE NULL END) AS jr,
       SUM(CASE WHEN year = 'SR' THEN players ELSE NULL END) AS sr
FROM (
      SELECT teams.conference AS conference,
             players.year,
             COUNT(1) AS players
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
      GROUP BY 1, 2
     ) sub
GROUP BY 1
ORDER BY 2 DESC;
```

Этот способ работает в любой базе. Его знают на собеседованиях.

### Колонки в строки

Многие таблицы в интернете сделаны для чтения, а не для анализа. Например, таблица `tutorial.worldwide_earthquakes`: число землетрясений по силе и годам.

```sql
SELECT *
FROM tutorial.worldwide_earthquakes;
```

Колонки называются `year_2000`, `year_2001` и так далее. Чтобы посчитать, например, среднее по годам, лучше иметь три колонки: `magnitude`, `year`, `number_of_earthquakes`.

Шаг 1. Составьте список годов. Можно написать его руками через `UNION ALL`:

```sql
SELECT year
FROM (
      SELECT 2000 AS year
      UNION ALL SELECT 2001
      UNION ALL SELECT 2002
      UNION ALL SELECT 2003
      UNION ALL SELECT 2004
      UNION ALL SELECT 2005
      UNION ALL SELECT 2006
      UNION ALL SELECT 2007
      UNION ALL SELECT 2008
      UNION ALL SELECT 2009
      UNION ALL SELECT 2010
      UNION ALL SELECT 2011
      UNION ALL SELECT 2012
     ) AS v;
```

Шаг 2. Соедините список с таблицей через `CROSS JOIN`. Каждая строка размножится 13 раз. Выберите нужную колонку через `CASE`:

```sql
SELECT years.year,
       earthquakes.magnitude,
       CASE years.year
            WHEN 2000 THEN year_2000
            WHEN 2001 THEN year_2001
            WHEN 2002 THEN year_2002
            WHEN 2003 THEN year_2003
            WHEN 2004 THEN year_2004
            WHEN 2005 THEN year_2005
            WHEN 2006 THEN year_2006
            WHEN 2007 THEN year_2007
            WHEN 2008 THEN year_2008
            WHEN 2009 THEN year_2009
            WHEN 2010 THEN year_2010
            WHEN 2011 THEN year_2011
            WHEN 2012 THEN year_2012
            ELSE NULL
       END AS number_of_earthquakes
FROM tutorial.worldwide_earthquakes AS earthquakes
CROSS JOIN (
      SELECT 2000 AS year
      UNION ALL SELECT 2001
      UNION ALL SELECT 2002
      UNION ALL SELECT 2003
      UNION ALL SELECT 2004
      UNION ALL SELECT 2005
      UNION ALL SELECT 2006
      UNION ALL SELECT 2007
      UNION ALL SELECT 2008
      UNION ALL SELECT 2009
      UNION ALL SELECT 2010
      UNION ALL SELECT 2011
      UNION ALL SELECT 2012
     ) AS years
ORDER BY 1, 2;
```

Результат: 6 уровней силы × 13 лет = 78 строк.

### Бонус: PIVOT и UNPIVOT в DuckDB

В DuckDB есть готовые команды `PIVOT` и `UNPIVOT`. Они делают то же, что запросы выше, но намного короче.

`PIVOT` из строк в колонки:

```sql
PIVOT (
      SELECT teams.conference,
             players.year
      FROM benn.college_football_players players
      JOIN benn.college_football_teams teams
        ON teams.school_name = players.school_name
     )
ON year IN ('FR', 'SO', 'JR', 'SR')
USING COUNT(*)
GROUP BY conference
ORDER BY conference;
```

Части команды:

- `ON year` — значения какой колонки станут колонками;
- `IN (...)` — какие именно значения (необязательно);
- `USING COUNT(*)` — что считать в ячейках;
- `GROUP BY conference` — что остаётся строками.

`UNPIVOT` из колонок в строки:

```sql
UNPIVOT tutorial.worldwide_earthquakes
ON COLUMNS('year_*')
INTO NAME year VALUE number_of_earthquakes;
```

`COLUMNS('year_*')` берёт все колонки, имя которых начинается с `year_`. В колонке `year` останутся значения вроде `year_2000`. Чтобы получить число, уберите префикс:

```sql
SELECT magnitude,
       REPLACE(year, 'year_', '')::INTEGER AS year,
       number_of_earthquakes
FROM (
      UNPIVOT tutorial.worldwide_earthquakes
      ON COLUMNS('year_*')
      INTO NAME year VALUE number_of_earthquakes
     )
ORDER BY 2, 1;
```

:::note
В Postgres нет команд `PIVOT` и `UNPIVOT`. Там используют `SUM(CASE ...)` для строк в колонки и `CROSS JOIN` с `UNION ALL` или `LATERAL (VALUES ...)` для колонок в строки. SQL Server, Oracle и Snowflake имеют свои версии `PIVOT`.
:::

:::caution
В обычном `PIVOT` нужно знать список значений. Если значение добавится позже, при ручном способе колонка не появится сама. Проверяйте список.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

В этом уроке не было задач в оригинале. Ниже три задачи на тему.

#### Задание 1

Для каждого дивизиона (`division` в `benn.college_football_teams`) посчитайте игроков по курсам `FR`, `SO`, `JR`, `SR`. Используйте `SUM(CASE ...)` или `COUNT(CASE ...)` без `PIVOT`. Добавьте колонку `total_players`.

**Проверка:** 2 строки. `FBS (Division I-A Teams)` и `FCS (Division I-AA Teams)`. Сумма `total_players` по двум строкам — 6935.

<details>
<summary>Решение</summary>

```sql
SELECT teams.division,
       COUNT(*) AS total_players,
       COUNT(CASE WHEN players.year = 'FR' THEN 1 END) AS fr,
       COUNT(CASE WHEN players.year = 'SO' THEN 1 END) AS so,
       COUNT(CASE WHEN players.year = 'JR' THEN 1 END) AS jr,
       COUNT(CASE WHEN players.year = 'SR' THEN 1 END) AS sr
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1
ORDER BY 1;
```

</details>

#### Задание 2

Превратите `tutorial.worldwide_earthquakes` в длинный вид с колонками `magnitude`, `year`, `number_of_earthquakes`. Используйте `UNPIVOT`. Потом посчитайте сумму землетрясений силой `7.0 to 7.9` за все годы.

**Проверка:** длинная таблица содержит 78 строк. Сумма для `7.0 to 7.9` — 186.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(number_of_earthquakes) AS total
FROM (
      UNPIVOT tutorial.worldwide_earthquakes
      ON COLUMNS('year_*')
      INTO NAME year VALUE number_of_earthquakes
     )
WHERE magnitude = '7.0 to 7.9';
```

</details>

#### Задание 3

В `benn.sample_event_table` посчитайте события за март 2014. Строки — `event_name`, колонки — `device`. Используйте `PIVOT` из DuckDB. Устройства выберите автоматически, без `IN`.

**Проверка:** 6 строк (по числу типов событий) и 5 колонок: `event_name` и 4 устройства. Сумма всех ячеек — 171551.

<details>
<summary>Решение</summary>

```sql
PIVOT (
      SELECT event_name,
             device
      FROM benn.sample_event_table
      WHERE event_date >= '2014-03-01'
        AND event_date < '2014-04-01'
     )
ON device
USING COUNT(*)
GROUP BY event_name
ORDER BY event_name;
```

</details>
