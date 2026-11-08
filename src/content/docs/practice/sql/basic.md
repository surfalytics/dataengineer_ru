---
title: "Основы SQL"
description: "Первый уровень курса: SELECT, WHERE, операторы сравнения, LIKE, IN, BETWEEN, IS NULL, AND, OR, NOT, ORDER BY. Задания на DuckDB."
sidebar:
  label: "Основы"
tableOfContents:
  minHeadingLevel: 2
  maxHeadingLevel: 2
tags:
  - sql
  - practice
---

Первый уровень. Вы учитесь выбирать и фильтровать данные из таблицы.

Работаем с таблицами `tutorial.us_housing_units` и `tutorial.billboard_top_100_year_end`. Описание таблиц: [Учебные данные](/practice/sql/datasets/). Не установили DuckDB? Начните с [установки](/practice/sql/setup/).

Идите по урокам по порядку. Каждый урок: пример, потом задания. Решайте сами, без AI.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 625 446" width="625" height="446" role="img" aria-label="Модель данных уровня «Основы»: три таблицы без связей">
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="236" height="162" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H244 Q250 14 250 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.us_housing_units</text>
<text class="erd-col" x="26" y="55">year</text>
<text class="erd-type" x="238" y="55" text-anchor="end">int</text>
<text class="erd-col" x="26" y="73">month</text>
<text class="erd-type" x="238" y="73" text-anchor="end">int</text>
<text class="erd-col" x="26" y="91">month_name</text>
<text class="erd-type" x="238" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">south</text>
<text class="erd-type" x="238" y="109" text-anchor="end">double</text>
<text class="erd-col" x="26" y="127">west</text>
<text class="erd-type" x="238" y="127" text-anchor="end">double</text>
<text class="erd-col" x="26" y="145">midwest</text>
<text class="erd-type" x="238" y="145" text-anchor="end">double</text>
<text class="erd-col" x="26" y="163">northeast</text>
<text class="erd-type" x="238" y="163" text-anchor="end">double</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="216" width="236" height="216" rx="6"/>
<path class="erd-head" d="M14 244 V222 Q14 216 20 216 H244 Q250 216 250 222 V244 Z"/>
<text class="erd-title" x="26" y="234">tutorial.crunchbase_companies</text>
<text class="erd-col" x="26" y="257">permalink</text>
<text class="erd-type" x="238" y="257" text-anchor="end">text</text>
<text class="erd-col" x="26" y="275">name</text>
<text class="erd-type" x="238" y="275" text-anchor="end">text</text>
<text class="erd-col" x="26" y="293">category_code</text>
<text class="erd-type" x="238" y="293" text-anchor="end">text</text>
<text class="erd-col" x="26" y="311">funding_total_usd</text>
<text class="erd-type" x="238" y="311" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="329">status</text>
<text class="erd-type" x="238" y="329" text-anchor="end">text</text>
<text class="erd-col" x="26" y="347">country_code</text>
<text class="erd-type" x="238" y="347" text-anchor="end">text</text>
<text class="erd-col" x="26" y="365">state_code</text>
<text class="erd-type" x="238" y="365" text-anchor="end">text</text>
<text class="erd-col" x="26" y="383">founded_at</text>
<text class="erd-type" x="238" y="383" text-anchor="end">text</text>
<text class="erd-col" x="26" y="401">founded_year</text>
<text class="erd-type" x="238" y="401" text-anchor="end">bigint</text>
<text class="erd-note" x="26" y="419">… ещё 8 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="314" y="14" width="280" height="144" rx="6"/>
<path class="erd-head" d="M314 42 V20 Q314 14 320 14 H587 Q593 14 593 20 V42 Z"/>
<text class="erd-title" x="326" y="32">tutorial.billboard_top_100_year_end</text>
<text class="erd-col" x="326" y="55">year</text>
<text class="erd-type" x="581" y="55" text-anchor="end">int</text>
<text class="erd-col" x="326" y="73">year_rank</text>
<text class="erd-type" x="581" y="73" text-anchor="end">int</text>
<text class="erd-col" x="326" y="91">group_name</text>
<text class="erd-type" x="581" y="91" text-anchor="end">text</text>
<text class="erd-col" x="326" y="109">artist</text>
<text class="erd-type" x="581" y="109" text-anchor="end">text</text>
<text class="erd-col" x="326" y="127">song_name</text>
<text class="erd-type" x="581" y="127" text-anchor="end">text</text>
<text class="erd-col" x="326" y="145">id</text>
<text class="erd-type" x="581" y="145" text-anchor="end">int</text>
</g>
</svg>
</div>

Таблицы этого уровня не связаны друг с другом. Показаны главные столбцы широких таблиц. Полный список столбцов: [Учебные данные](/practice/sql/datasets/).
<!-- erd:end -->

## SELECT и FROM

`SELECT` и `FROM` есть в каждом запросе. `SELECT` говорит, какие столбцы показать. `FROM` говорит, из какой таблицы их взять.

В этом уроке работаем с таблицей `tutorial.us_housing_units` — число построенных домов в США по месяцам и регионам.

### База, схема, таблица

**База данных** — это организованный набор данных. Данные в ней лежат в **таблицах**.

Таблица похожа на лист Excel: есть строки и столбцы. Но правила строже:

- данные всегда разложены по столбцам;
- у каждого столбца есть имя, и оно уникально в таблице;
- в одном столбце все значения одного типа (числа, текст, даты).

Таблицы сгруппированы в **схемы**. Схема — это папка для таблиц. Полное имя таблицы пишут так: `схема.таблица`.

В нашей учебной базе две схемы:

| Схема | Что в ней |
|---|---|
| `tutorial` | Основные таблицы курса: Billboard, дома, Crunchbase, акции Apple и другие |
| `benn` | Таблицы про студенческий футбол и служебные таблицы для кейсов |

Например, `tutorial.us_housing_units` — таблица `us_housing_units` в схеме `tutorial`.

:::tip
Список всех таблиц в DuckDB: команда `.tables`. Столбцы таблицы: `DESCRIBE tutorial.us_housing_units;`.
:::

### SELECT и FROM

Выберем три столбца:

```sql
SELECT year,
       month,
       west
FROM tutorial.us_housing_units;
```

Правила:

- сначала `SELECT`, потом `FROM`, порядок менять нельзя;
- столбцы разделяют запятой;
- после последнего столбца запятой нет.

Запрос вернёт столбцы `year`, `month` и `west`. Строки — все, что есть в таблице.

### Все столбцы: SELECT *

Звёздочка `*` значит «все столбцы»:

```sql
SELECT *
FROM tutorial.us_housing_units;
```

:::caution
В рабочих запросах `*` лучше не использовать. Если в таблицу добавят столбец, результат запроса изменится. Перечисляйте нужные столбцы явно. `*` удобна, чтобы быстро посмотреть на таблицу.
:::

### Что происходит при запуске запроса

База выполняет запрос и возвращает результат — новую таблицу. Исходная таблица при этом не меняется. `SELECT` только читает данные.

Если запустить запрос ещё раз, база снова прочитает таблицу. Если данные в таблице изменились, изменится и результат.

### Как оформлять запрос

SQL не различает регистр ключевых слов и не обращает внимания на переносы строк. Эти два запроса одинаковы:

```sql
select year, month, west from tutorial.us_housing_units;
```

```sql
SELECT year,
       month,
       west
FROM tutorial.us_housing_units;
```

Второй читать проще. Принятые правила:

- ключевые слова (`SELECT`, `FROM`, `WHERE`) — заглавными буквами;
- имена столбцов и таблиц — строчными;
- каждую часть запроса — с новой строки;
- в конце — точка с запятой `;`.

### Имена столбцов: AS

Столбец в результате можно переименовать. Для этого пишут `AS` и новое имя:

```sql
SELECT west AS west_region,
       south AS south_region
FROM tutorial.us_housing_units;
```

Хорошее имя — строчными буквами, слова через подчёркивание: `west_region`.

Если в имени нужны пробелы или заглавные буквы, возьмите его в двойные кавычки:

```sql
SELECT west AS "West Region"
FROM tutorial.us_housing_units;
```

:::note
Двойные кавычки — для имён столбцов и таблиц. Одинарные — для текстовых значений, например `'January'`. Это правило одинаково в DuckDB и Postgres.
:::

### Практика

#### Задание 1

Выберите все столбцы таблицы `tutorial.us_housing_units`, но без `*`. Перечислите каждый столбец.

**Проверка:** 564 строки, 7 столбцов. Первая строка: 1968 год, January, `south` = 34.4.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       month_name,
       south,
       west,
       midwest,
       northeast
FROM tutorial.us_housing_units;
```

</details>

#### Задание 2

Выберите все столбцы таблицы `tutorial.us_housing_units` и переименуйте их так, чтобы каждое слово начиналось с заглавной буквы: `Year`, `Month`, `Month Name` и так далее.

**Проверка:** 7 столбцов, третий называется `Month Name`.

<details>
<summary>Решение</summary>

```sql
SELECT year AS "Year",
       month AS "Month",
       month_name AS "Month Name",
       south AS "South",
       west AS "West",
       midwest AS "Midwest",
       northeast AS "Northeast"
FROM tutorial.us_housing_units;
```

</details>

## LIMIT

`LIMIT` ограничивает число строк, которые вернёт запрос. Это самый простой способ быстро посмотреть на таблицу и не ждать миллион строк.

В этом уроке работаем с таблицей `tutorial.us_housing_units`.

### Как DuckDB показывает результат

Запустите запрос без ограничений:

```sql
SELECT *
FROM tutorial.us_housing_units;
```

В таблице 564 строки. Но DuckDB в терминале покажет только первые и последние 20 строк, а между ними — точки. Внизу будет написано, сколько строк всего.

Это ограничение только вывода. Запрос всё равно прочитал все строки.

:::tip
Показать больше строк: `.maxrows 100`. Подробнее — на странице [установки](/practice/sql/setup/).
:::

### Зачем ограничивать результат

- **Посмотреть на таблицу.** Часто нужно увидеть несколько строк: какие есть столбцы, как выглядят значения.
- **Сэкономить время.** Таблица может содержать миллионы строк. Выводить их все долго и бесполезно.
- **Защита от ошибки.** Легко случайно запустить запрос, который вернёт огромный результат.

### Команда LIMIT

```sql
SELECT *
FROM tutorial.us_housing_units
LIMIT 100;
```

Запрос вернёт 100 строк.

`LIMIT` всегда пишут в самом конце запроса. Порядок частей запроса, которые вы узнаете в этом разделе:

| Порядок | Часть |
|---|---|
| 1 | `SELECT` |
| 2 | `FROM` |
| 3 | `WHERE` |
| 4 | `ORDER BY` |
| 5 | `LIMIT` |

:::caution
Без `ORDER BY` база не обещает порядок строк. `LIMIT 10` вернёт какие-то 10 строк, не обязательно «первые». Чтобы получить, например, 10 самых больших значений, нужен `ORDER BY` — он будет в уроке [ORDER BY](/practice/sql/basic/#order-by).
:::

:::note
В DuckDB, Postgres, MySQL и Snowflake пишут `LIMIT`. В SQL Server вместо него `SELECT TOP 10 ...`. В стандарте SQL есть `FETCH FIRST 10 ROWS ONLY` — DuckDB и Postgres его тоже понимают.
:::

### Практика

#### Задание 1

Напишите запрос к `tutorial.us_housing_units`, который с помощью `LIMIT` вернёт только 15 строк.

**Проверка:** 15 строк, 7 столбцов. DuckDB показывает все 15 строк без точек.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
LIMIT 15;
```

</details>

## WHERE

`WHERE` оставляет в результате только те строки, которые подходят под условие. Это фильтр, как в Excel. Без него запрос возвращает всю таблицу.

В этом уроке работаем с таблицей `tutorial.us_housing_units`.

### Оператор WHERE

Сначала посмотрим на таблицу целиком:

```sql
SELECT *
FROM tutorial.us_housing_units;
```

Теперь оставим только январь:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month = 1;
```

Запрос вернёт 47 строк — по одной на каждый год с 1968 по 2014.

Части запроса всегда идут в таком порядке: `SELECT`, `FROM`, `WHERE`.

### Как работает WHERE

База проверяет условие для каждой строки:

- условие верно — строка попадает в результат;
- условие неверно — строка отбрасывается.

Строка всегда остаётся целой. Фильтр по одному столбцу убирает строку целиком, со всеми её столбцами. Каждая строка — это одно наблюдение, и её данные не перемешиваются с другими строками.

:::note
В Excel можно отсортировать один столбец отдельно от других и испортить данные. В SQL так не получится: строка всегда двигается целиком.
:::

Условие может использовать столбец, которого нет в `SELECT`:

```sql
SELECT year,
       west
FROM tutorial.us_housing_units
WHERE month = 1;
```

В условиях можно использовать не только `=`. Другие операторы сравнения — в следующем уроке, [Операторы сравнения](/practice/sql/basic/#операторы-сравнения).

### Практика

#### Задание 1

Напишите запрос, который вернёт все строки за 1990 год.

**Проверка:** 12 строк. В январе 1990 года `west` = 34.2.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE year = 1990;
```

</details>

#### Задание 2

Напишите запрос, который вернёт только столбцы `year` и `west` для всех строк за июнь (`month` = 6).

**Проверка:** 47 строк, 2 столбца. Для 1968 года `west` = 26.0.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       west
FROM tutorial.us_housing_units
WHERE month = 6;
```

</details>

#### Задание 3

Напишите запрос, который вернёт все строки за 2014 год — последний год в таблице.

**Проверка:** 12 строк. В строке за декабрь `south` = 35.3.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE year = 2014;
```

</details>

## Операторы сравнения

Операторы сравнения — самый простой способ фильтровать данные в `WHERE`. Они сравнивают значение столбца с числом, текстом или другим столбцом.

В этом уроке работаем с таблицей `tutorial.us_housing_units`. Числа в таблице — тысячи домов.

### Операторы для чисел

| Оператор | Значение |
|---|---|
| `=` | равно |
| `<>` или `!=` | не равно |
| `>` | больше |
| `<` | меньше |
| `>=` | больше или равно |
| `<=` | меньше или равно |

Найдём месяцы, когда на западе построили больше 30 тысяч домов:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE west > 30;
```

Запрос вернёт 278 строк. Замените `>` на другие операторы. Попробуйте другие числа. Так вы быстро почувствуете, как они работают.

### Операторы для текста

Сравнивать можно и текст. Текстовое значение пишут в одинарных кавычках:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name = 'January';
```

Операторы `>` и `<` для текста сравнивают значения по алфавиту. Точнее, по коду символов:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name < 'O';
```

:::caution
Регистр важен. В DuckDB все заглавные буквы идут раньше строчных. `'January' < 'o'` — верно, `'September' < 'o'` — тоже верно. Поэтому сравнивайте с заглавной буквой, если значения начинаются с заглавной. Результат зависит от базы и её настроек (collation).
:::

:::tip
Сравнение текста по алфавиту нужно редко. Обычно для текста хватает `=` и `<>`.
:::

### Арифметика в SELECT

В `SELECT` можно считать. Доступны `+`, `-`, `*`, `/` и скобки:

```sql
SELECT year,
       month,
       west + south AS west_south_total
FROM tutorial.us_housing_units;
```

Правила:

- арифметика работает по строкам: каждая строка считается отдельно;
- новому столбцу дайте имя через `AS`;
- порядок действий как в математике, скобки меняют его.

Арифметику можно использовать и в `WHERE`. Здесь сравниваем столбец с суммой двух других:

```sql
SELECT year,
       month,
       west,
       south
FROM tutorial.us_housing_units
WHERE west > south + 10;
```

:::note
В DuckDB `/` делит как дробное число: `5 / 2` даст `2.5`. В Postgres для целых чисел `5 / 2` даст `2`. Целочисленное деление в DuckDB — оператор `//`.
:::

### Практика

#### Задание 1

Выпускал ли регион West больше 50 тысяч домов за один месяц?

**Проверка:** 19 строк. Максимум в столбце `west` — 55.7.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE west > 50;
```

</details>

#### Задание 2

Выпускал ли регион South 20 тысяч домов или меньше за один месяц?

**Проверка:** 5 строк. Минимум в столбце `south` — 17.4.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE south <= 20;
```

</details>

#### Задание 3

Напишите запрос, который покажет только строки, где название месяца — February.

**Проверка:** 47 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name = 'February';
```

</details>

#### Задание 4

Напишите запрос, который покажет только строки, где `month_name` начинается с буквы N или с буквы, которая в алфавите раньше.

**Проверка:** 470 строк, 10 разных месяцев. Нет September и October.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name < 'O';
```

</details>

#### Задание 5

Напишите запрос, который считает сумму всех четырёх регионов в отдельном столбце.

**Проверка:** 564 строки. В первой строке (январь 1968) сумма равна 80.5.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west,
       south,
       midwest,
       northeast,
       west + south + midwest + northeast AS usa_total
FROM tutorial.us_housing_units;
```

</details>

#### Задание 6

Напишите запрос, который вернёт все строки, где в регионе West построили больше домов, чем в Midwest и Northeast вместе.

**Проверка:** 104 строки.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west,
       south,
       midwest,
       northeast
FROM tutorial.us_housing_units
WHERE west > (midwest + northeast);
```

</details>

#### Задание 7

Напишите запрос, который считает, какой процент всех построенных домов США приходится на каждый регион. Верните только годы с 2000 и позже.

Подсказка: должно получиться четыре столбца с процентами.

**Проверка:** 180 строк. Для января 2000: `west_pct` = 24.45, `south_pct` = 52.36 (округление до сотых).

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west / (west + south + midwest + northeast) * 100 AS west_pct,
       south / (west + south + midwest + northeast) * 100 AS south_pct,
       midwest / (west + south + midwest + northeast) * 100 AS midwest_pct,
       northeast / (west + south + midwest + northeast) * 100 AS northeast_pct
FROM tutorial.us_housing_units
WHERE year >= 2000;
```

</details>

## Логические операторы

Чаще всего одного условия мало. Логические операторы помогают собрать из нескольких условий один фильтр. Этот урок — обзор. Каждый оператор разберём отдельно в следующих уроках.

### Операторы

| Оператор | Что делает | Урок |
|---|---|---|
| `LIKE` | ищет значения по шаблону | [LIKE](/practice/sql/basic/#like) |
| `IN` | оставляет значения из списка | [IN](/practice/sql/basic/#in) |
| `BETWEEN` | оставляет значения из диапазона | [BETWEEN](/practice/sql/basic/#between) |
| `IS NULL` | находит пустые значения | [IS NULL](/practice/sql/basic/#is-null) |
| `AND` | оба условия верны | [AND](/practice/sql/basic/#and) |
| `OR` | верно хотя бы одно условие | [OR](/practice/sql/basic/#or) |
| `NOT` | условие неверно | [NOT](/practice/sql/basic/#not) |

### Таблица Billboard

Для этих уроков нужна таблица `tutorial.billboard_top_100_year_end`. В ней итоговые годовые чарты Billboard: 100 лучших песен каждого года, с 1956 по 2013.

Столбцы:

| Столбец | Что в нём |
|---|---|
| `year` | год чарта |
| `year_rank` | место песни в конце года |
| `group_name` | полное имя исполнителя, как в чарте. Для совместных песен — несколько имён |
| `artist` | один исполнитель. У песни с гостями несколько строк |
| `song_name` | название песни |

Посмотрим на таблицу. Пока не думайте об `ORDER BY`, он будет в одном из следующих уроков:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY year DESC, year_rank;
```

Обратите внимание на 2013 год. У песни Macklemore несколько строк, по одной на каждого исполнителя. Поэтому строк в таблице больше, чем 100 на год.

:::tip
Столбец `group_name` — это полное имя, например `Katy Perry featuring Snoop Dogg`. Столбец `artist` — один человек или группа: `Katy Perry`, `Snoop Dogg`. Для поиска по составу чаще берут `group_name` с `LIKE`.
:::

### Практика

#### Задание 1

Напишите запрос, который покажет все строки таблицы `tutorial.billboard_top_100_year_end` за 2013 год.

**Проверка:** 144 строки в 2013 году. Первое место — Thrift Shop.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013;
```

</details>

#### Задание 2

Напишите запрос, который покажет только столбцы `year`, `year_rank` и `song_name` для песен, занявших первое место в 2005 году.

**Проверка:** 1 уникальная песня, год 2005, `year_rank` = 1.

<details>
<summary>Решение</summary>

```sql
SELECT DISTINCT year,
       year_rank,
       song_name
FROM tutorial.billboard_top_100_year_end
WHERE year = 2005
  AND year_rank = 1;
```

</details>

## LIKE

`LIKE` ищет строки, похожие на шаблон. Он нужен, когда вы не знаете точное значение. Например: «все исполнители, чьё имя начинается на Snoop».

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end` — итоговые годовые чарты Billboard.

### Оператор LIKE

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name LIKE 'Snoop%';
```

Запрос вернёт строки, где `group_name` начинается с «Snoop», а дальше идут любые символы.

### Символы шаблона

| Символ | Что значит | Пример | Найдёт |
|---|---|---|---|
| `%` | Любое число любых символов, даже ноль | `'Snoop%'` | Snoop Dogg, Snoop Dogg featuring Pharrell |
| `_` | Ровно один любой символ | `'Dr_ke'` | Drake |

Где стоит `%` — важно:

- `'Snoop%'` — начинается с «Snoop»;
- `'%Snoop'` — заканчивается на «Snoop»;
- `'%Snoop%'` — содержит «Snoop» где угодно.

### Регистр букв: ILIKE

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

### Практика

#### Задание 1

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

#### Задание 2

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

## IN

`IN` оставляет строки, где значение совпадает с одним из значений в списке. Это короткая замена цепочке `OR`.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Оператор IN

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

`IN` ищет точное совпадение. Для частичного совпадения нужен [LIKE](/practice/sql/basic/#like).

:::tip
`IN (1, 2, 3)` — то же самое, что `year_rank = 1 OR year_rank = 2 OR year_rank = 3`. Но короче и легче читать.
:::

### Практика

#### Задание 1

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

## BETWEEN

`BETWEEN` оставляет строки, где значение лежит в диапазоне. Его используют для чисел и дат.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Оператор BETWEEN

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank BETWEEN 5 AND 10;
```

Запрос вернёт 396 строк. `BETWEEN` всегда идёт вместе с [AND](/practice/sql/basic/#and).

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
С датами и временем будьте осторожны. `BETWEEN '2014-01-01' AND '2014-01-31'` не захватит записи от 31 января после полуночи, если в столбце есть время. Подробнее — в уроке [Формат дат и времени](/practice/sql/advanced/#формат-дат-и-времени).
:::

### Практика

#### Задание 1

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

## IS NULL

`IS NULL` находит строки, где в столбце нет данных. Такое значение называют `NULL`.

В этом уроке работаем с таблицей `tutorial.crunchbase_companies` — компании из Crunchbase. В Billboard пустых значений нет, поэтому нужна другая таблица.

### Что такое NULL

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

### Пустая строка и NULL

Иногда пустые значения хранят как пустую строку `''` или как пробелы. Это не `NULL`. Чтобы поймать оба случая:

```sql
SELECT *
FROM tutorial.crunchbase_companies
WHERE category_code IS NULL
   OR TRIM(category_code) = '';
```

`TRIM` убирает пробелы по краям. Подробнее про `NULL` — на странице [Средний уровень](/practice/sql/intermediate/).

### Практика

#### Задание 1

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

## AND

`AND` оставляет только те строки, где верны оба условия сразу.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Оператор AND

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

### Практика

#### Задание 1

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

## OR

`OR` оставляет строки, где верно хотя бы одно из условий.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Оператор OR

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year_rank = 5 OR artist = 'Gotye';
```

Каждая строка в результате подходит под одно из двух условий. Запрос вернёт 70 строк.

### OR вместе с AND

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

### Практика

#### Задание 1

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

#### Задание 2

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

#### Задание 3

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

## NOT

`NOT` ставят перед условием. Тогда в результат попадут строки, где условие неверно.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Оператор NOT

Песни 2013 года, кроме мест 2 и 3:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank NOT BETWEEN 2 AND 3;
```

### NOT и операторы > и <

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

### NOT с LIKE

`NOT` часто ставят перед `LIKE`. Так исключают строки по шаблону:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND group_name NOT ILIKE '%macklemore%';
```

В результате нет Macklemore. Запрос вернёт 138 строк.

### NOT с NULL

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

### Практика

#### Задание 1

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

## ORDER BY

`ORDER BY` сортирует результат по одному или нескольким столбцам. Без него порядок строк не гарантирован.

В этом уроке работаем с таблицей `tutorial.billboard_top_100_year_end`.

### Сортировка по одному столбцу

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY artist;
```

Строки идут по алфавиту, от A до Z. Это порядок по возрастанию. Он работает по умолчанию. Для чисел это от меньшего к большему.

Чтобы отсортировать в обратном порядке, добавьте `DESC`:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
ORDER BY year_rank DESC;
```

`ORDER BY` пишут после `WHERE`. Если есть `LIMIT`, то `ORDER BY` идёт перед ним.

### Сортировка по нескольким столбцам

Столбцы перечисляют через запятую. Сначала сортировка по первому. Если значения равны, то по второму:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
ORDER BY year_rank, artist;
```

`DESC` действует только на тот столбец, после которого стоит:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY year DESC, year_rank;
```

Здесь год идёт от нового к старому, а место внутри года — от 1 к 100.

:::tip
В `ORDER BY` можно указать номер столбца из `SELECT`: `ORDER BY 1, 2`. Это быстро, но в рабочих запросах лучше писать имена.
:::

:::note
`NULL` в DuckDB по умолчанию идут последними при сортировке по возрастанию. Изменить порядок: `NULLS FIRST` или `NULLS LAST`. В Postgres `NULL` при `ASC` тоже идут последними.
:::

### Комментарии

Комментарий — это текст, который база игнорирует. Он нужен людям.

Однострочный комментарий начинается с `--`:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013 -- нужный год
  AND year_rank <= 10; -- только топ-10
```

Многострочный комментарий — между `/*` и `*/`:

```sql
/* Топ-10 за 2013 год.
   Запрос нужен для проверки. */
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013
  AND year_rank <= 10;
```

Хороший комментарий объясняет, зачем это сделано, а не пересказывает код.

### Практика

#### Задание 1

Напишите запрос, который вернёт все строки за 2012 год. Отсортируйте их по названию песни от Z до A.

**Проверка:** 131 строка. Первая строка — песня «Young, Wild & Free».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2012
ORDER BY song_name DESC;
```

</details>

#### Задание 2

Напишите запрос, который вернёт все строки за 2010 год. Отсортируйте их по месту в чарте. Внутри каждой песни отсортируйте исполнителей по алфавиту.

**Проверка:** 147 строк. Первая строка — Tik Tok, Kesha.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2010
ORDER BY year_rank, artist;
```

</details>

#### Задание 3

Напишите запрос, который покажет все строки, где T-Pain входит в состав исполнителей. Отсортируйте их по месту в чарте от худшего к лучшему (от 100 к 1).

**Проверка:** 54 строки. Первая строка: 2008 год, место 100, «She Got It».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE group_name ILIKE '%t-pain%'
ORDER BY year_rank DESC;
```

</details>

#### Задание 4

Напишите запрос, который вернёт песни на местах с 10 по 20 включительно в 1993, 2003 или 2013 году. Отсортируйте результат по году и месту. Оставьте комментарий на каждой строке `WHERE`, который объясняет, что эта строка делает.

**Проверка:** 48 строк. Первая строка: 1993 год, место 10, «Informer».

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year IN (1993, 2003, 2013)  -- нужные годы
  AND year_rank BETWEEN 10 AND 20 -- места с 10 по 20
ORDER BY year, year_rank;
```

</details>
