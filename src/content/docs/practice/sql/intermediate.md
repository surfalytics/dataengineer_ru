---
title: "Средний уровень SQL"
description: "Второй уровень курса: агрегаты, GROUP BY, HAVING, CASE, DISTINCT, все виды JOIN, UNION. Задания на DuckDB."
sidebar:
  label: "Средний уровень"
tableOfContents:
  minHeadingLevel: 2
  maxHeadingLevel: 2
tags:
  - sql
  - practice
---

Второй уровень. Вы считаете агрегаты, группируете данные и соединяете таблицы.

Работаем с таблицами Crunchbase, акциями Apple и футболистами. Описание таблиц: [Учебные данные](/practice/sql/datasets/). Нужны знания из уровня [Основы](/practice/sql/basic/).

Решайте сами, без AI. Сначала задание, потом проверка, и только потом решение.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 691 1016" width="691" height="1016" role="img" aria-label="Модель данных среднего уровня">
<path class="erd-view-link" d="M512 486 V526"/>
<path class="erd-view-link" d="M659 670 H673 V284 H659"/>
<path class="erd-link" d="M365 51 H333 V51 H301"/>
<text class="erd-card" x="355" y="46" text-anchor="middle">1</text>
<text class="erd-card" x="311" y="46" text-anchor="middle">N</text>
<path class="erd-link" d="M512 230 V270"/>
<text class="erd-card" x="524" y="243" text-anchor="middle">1</text>
<text class="erd-card" x="524" y="265" text-anchor="middle">N</text>
<path class="erd-link" d="M301 307 H324 V841 H365"/>
<text class="erd-card" x="311" y="302" text-anchor="middle">1</text>
<text class="erd-card" x="355" y="836" text-anchor="middle">N</text>
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="287" height="180" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H295 Q301 14 301 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.crunchbase_acquisitions</text>
<rect class="erd-keyrow" x="15" y="42" width="285" height="18"/>
<text class="erd-col erd-key" x="26" y="55">company_permalink</text>
<text class="erd-type" x="289" y="55" text-anchor="end">text</text>
<text class="erd-col" x="26" y="73">company_name</text>
<text class="erd-type" x="289" y="73" text-anchor="end">text</text>
<text class="erd-col" x="26" y="91">acquirer_name</text>
<text class="erd-type" x="289" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">acquired_at</text>
<text class="erd-type" x="289" y="109" text-anchor="end">text</text>
<text class="erd-col" x="26" y="127">acquired_year</text>
<text class="erd-type" x="289" y="127" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="145">price_amount</text>
<text class="erd-type" x="289" y="145" text-anchor="end">double</text>
<text class="erd-col" x="26" y="163">price_currency_code</text>
<text class="erd-type" x="289" y="163" text-anchor="end">text</text>
<text class="erd-note" x="26" y="181">… ещё 13 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="234" width="287" height="126" rx="6"/>
<path class="erd-head" d="M14 262 V240 Q14 234 20 234 H295 Q301 234 301 240 V262 Z"/>
<text class="erd-title" x="26" y="252">benn.college_football_teams</text>
<text class="erd-col" x="26" y="275">division</text>
<text class="erd-type" x="289" y="275" text-anchor="end">text</text>
<text class="erd-col" x="26" y="293">conference</text>
<text class="erd-type" x="289" y="293" text-anchor="end">text</text>
<rect class="erd-keyrow" x="15" y="298" width="285" height="18"/>
<text class="erd-col erd-key" x="26" y="311">school_name</text>
<text class="erd-type" x="289" y="311" text-anchor="end">text</text>
<text class="erd-col" x="26" y="329">roster_url</text>
<text class="erd-type" x="289" y="329" text-anchor="end">text</text>
<text class="erd-col" x="26" y="347">id</text>
<text class="erd-type" x="289" y="347" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="400" width="287" height="198" rx="6"/>
<path class="erd-head" d="M14 428 V406 Q14 400 20 400 H295 Q301 400 301 406 V428 Z"/>
<text class="erd-title" x="26" y="418">tutorial.aapl_historical_stock_price</text>
<text class="erd-col" x="26" y="441">date</text>
<text class="erd-type" x="289" y="441" text-anchor="end">date</text>
<text class="erd-col" x="26" y="459">year</text>
<text class="erd-type" x="289" y="459" text-anchor="end">int</text>
<text class="erd-col" x="26" y="477">month</text>
<text class="erd-type" x="289" y="477" text-anchor="end">int</text>
<text class="erd-col" x="26" y="495">open</text>
<text class="erd-type" x="289" y="495" text-anchor="end">double</text>
<text class="erd-col" x="26" y="513">high</text>
<text class="erd-type" x="289" y="513" text-anchor="end">double</text>
<text class="erd-col" x="26" y="531">low</text>
<text class="erd-type" x="289" y="531" text-anchor="end">double</text>
<text class="erd-col" x="26" y="549">close</text>
<text class="erd-type" x="289" y="549" text-anchor="end">double</text>
<text class="erd-col" x="26" y="567">volume</text>
<text class="erd-type" x="289" y="567" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="585">id</text>
<text class="erd-type" x="289" y="585" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="14" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 42 V20 Q365 14 371 14 H653 Q659 14 659 20 V42 Z"/>
<text class="erd-title" x="377" y="32">tutorial.crunchbase_companies</text>
<rect class="erd-keyrow" x="366" y="42" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="55">permalink</text>
<text class="erd-type" x="647" y="55" text-anchor="end">text</text>
<text class="erd-col" x="377" y="73">name</text>
<text class="erd-type" x="647" y="73" text-anchor="end">text</text>
<text class="erd-col" x="377" y="91">category_code</text>
<text class="erd-type" x="647" y="91" text-anchor="end">text</text>
<text class="erd-col" x="377" y="109">funding_total_usd</text>
<text class="erd-type" x="647" y="109" text-anchor="end">bigint</text>
<text class="erd-col" x="377" y="127">status</text>
<text class="erd-type" x="647" y="127" text-anchor="end">text</text>
<text class="erd-col" x="377" y="145">country_code</text>
<text class="erd-type" x="647" y="145" text-anchor="end">text</text>
<text class="erd-col" x="377" y="163">state_code</text>
<text class="erd-type" x="647" y="163" text-anchor="end">text</text>
<text class="erd-col" x="377" y="181">founded_at</text>
<text class="erd-type" x="647" y="181" text-anchor="end">text</text>
<text class="erd-col" x="377" y="199">founded_year</text>
<text class="erd-type" x="647" y="199" text-anchor="end">bigint</text>
<text class="erd-note" x="377" y="217">… ещё 8 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="270" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 298 V276 Q365 270 371 270 H653 Q659 270 659 276 V298 Z"/>
<text class="erd-title" x="377" y="288">tutorial.crunchbase_investments</text>
<rect class="erd-keyrow" x="366" y="298" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="311">company_permalink</text>
<text class="erd-type" x="647" y="311" text-anchor="end">text</text>
<text class="erd-col" x="377" y="329">company_name</text>
<text class="erd-type" x="647" y="329" text-anchor="end">text</text>
<text class="erd-col" x="377" y="347">investor_permalink</text>
<text class="erd-type" x="647" y="347" text-anchor="end">text</text>
<text class="erd-col" x="377" y="365">investor_name</text>
<text class="erd-type" x="647" y="365" text-anchor="end">text</text>
<text class="erd-col" x="377" y="383">investor_country_code</text>
<text class="erd-type" x="647" y="383" text-anchor="end">text</text>
<text class="erd-col" x="377" y="401">funding_round_type</text>
<text class="erd-type" x="647" y="401" text-anchor="end">text</text>
<text class="erd-col" x="377" y="419">funded_at</text>
<text class="erd-type" x="647" y="419" text-anchor="end">text</text>
<text class="erd-col" x="377" y="437">funded_year</text>
<text class="erd-type" x="647" y="437" text-anchor="end">bigint</text>
<text class="erd-col" x="377" y="455">raised_amount_usd</text>
<text class="erd-type" x="647" y="455" text-anchor="end">double</text>
<text class="erd-note" x="377" y="473">… ещё 11 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="365" y="526" width="294" height="90" rx="6"/>
<path class="erd-head" d="M365 554 V532 Q365 526 371 526 H653 Q659 526 659 532 V554 Z"/>
<text class="erd-title" x="377" y="544">tutorial.crunchbase_investments_part1</text>
<text class="erd-note" x="377" y="567">Компании A–L</text>
<text class="erd-note" x="377" y="585">Те же столбцы, что у</text>
<text class="erd-note" x="377" y="603">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="365" y="656" width="294" height="90" rx="6"/>
<path class="erd-head" d="M365 684 V662 Q365 656 371 656 H653 Q659 656 659 662 V684 Z"/>
<text class="erd-title" x="377" y="674">tutorial.crunchbase_investments_part2</text>
<text class="erd-note" x="377" y="697">Компании M–Z</text>
<text class="erd-note" x="377" y="715">Те же столбцы, что у</text>
<text class="erd-note" x="377" y="733">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="786" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 814 V792 Q365 786 371 786 H653 Q659 786 659 792 V814 Z"/>
<text class="erd-title" x="377" y="804">benn.college_football_players</text>
<text class="erd-col" x="377" y="827">full_school_name</text>
<text class="erd-type" x="647" y="827" text-anchor="end">text</text>
<rect class="erd-keyrow" x="366" y="832" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="845">school_name</text>
<text class="erd-type" x="647" y="845" text-anchor="end">text</text>
<text class="erd-col" x="377" y="863">player_name</text>
<text class="erd-type" x="647" y="863" text-anchor="end">text</text>
<text class="erd-col" x="377" y="881">position</text>
<text class="erd-type" x="647" y="881" text-anchor="end">text</text>
<text class="erd-col" x="377" y="899">height</text>
<text class="erd-type" x="647" y="899" text-anchor="end">int</text>
<text class="erd-col" x="377" y="917">weight</text>
<text class="erd-type" x="647" y="917" text-anchor="end">int</text>
<text class="erd-col" x="377" y="935">year</text>
<text class="erd-type" x="647" y="935" text-anchor="end">text</text>
<text class="erd-col" x="377" y="953">hometown</text>
<text class="erd-type" x="647" y="953" text-anchor="end">text</text>
<text class="erd-col" x="377" y="971">state</text>
<text class="erd-type" x="647" y="971" text-anchor="end">text</text>
<text class="erd-col" x="377" y="989">id</text>
<text class="erd-type" x="647" y="989" text-anchor="end">int</text>
</g>
</svg>
</div>

**Как читать схему.** Линия — связь для `JOIN`. Подписи `1` и `N` показывают, сколько строк с каждой стороны: у одной компании может быть много покупок и инвестиций. Выделенный столбец — ключ соединения. Пунктир — представление (view): часть данных другой таблицы. Таблицы без линий не связаны с остальными. Показаны главные столбцы широких таблиц. Полный список столбцов: [Учебные данные](/practice/sql/datasets/).
<!-- erd:end -->

## Агрегатные функции

Средний уровень SQL учит считать итоги по данным и соединять таблицы. Первые уроки используют таблицу `tutorial.aapl_historical_stock_price`. Это дневные цены акций Apple за 2000–2014 годы. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

Задачи здесь сложнее, чем на базовом уровне. У многих задач есть несколько верных решений. Решение из курса — это пример, а не единственный ответ.

### Что такое агрегатная функция

Агрегатная функция берёт много строк и возвращает одно значение. Она считает итог по столбцу.

| Функция | Что делает |
|---|---|
| `COUNT` | Считает строки |
| `SUM` | Складывает значения |
| `MIN` | Находит наименьшее значение |
| `MAX` | Находит наибольшее значение |
| `AVG` | Считает среднее |

Это то же самое, что сводная таблица в Excel. Каждой функции посвящён отдельный урок.

### Строки и столбцы

Арифметические операторы работают внутри одной строки:

```sql
SELECT date,
       close - open AS day_change
FROM tutorial.aapl_historical_stock_price
LIMIT 5;
```

Агрегатные функции работают по столбцу, то есть по многим строкам сразу:

```sql
SELECT COUNT(*) AS rows_count,
       MIN(low) AS lowest_price,
       MAX(high) AS highest_price,
       AVG(close) AS avg_close
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт одну строку.

:::note
Агрегатные функции пропускают `NULL`. Подробности — в уроках про [COUNT](/practice/sql/intermediate/#count) и [AVG](/practice/sql/intermediate/#avg).
:::

:::caution
Нельзя смешивать в `SELECT` обычный столбец и агрегатную функцию без `GROUP BY`. Например, `SELECT date, MAX(high)` вернёт ошибку. Это тема урока про [GROUP BY](/practice/sql/intermediate/#group-by).
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите один запрос, который вернёт: число строк в таблице, первую дату и последнюю дату.

**Проверка:** одна строка: 3773 строки, первая дата 2000-01-03, последняя 2014-12-31.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_count,
       MIN(date) AS first_date,
       MAX(date) AS last_date
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 2

Напишите один запрос, который вернёт самую низкую цену `low` и самую высокую цену `high` за всё время.

**Проверка:** минимум 12.72, максимум 705.07.

<details>
<summary>Решение</summary>

```sql
SELECT MIN(low) AS lowest_price,
       MAX(high) AS highest_price
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 3

Напишите запрос, который посчитает общее число проданных акций (`volume`) и среднюю цену закрытия (`close`).

**Проверка:** сумма `volume` — 72665719900.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(volume) AS total_volume,
       AVG(close) AS avg_close
FROM tutorial.aapl_historical_stock_price;
```

</details>

## COUNT

`COUNT` считает строки. Это самая простая агрегатная функция, и результат легко проверить. В этом уроке работаем с `tutorial.aapl_historical_stock_price` и с `tutorial.crunchbase_companies`. Подробнее о таблицах — в [описании данных](/practice/sql/datasets/).

### Считаем все строки

```sql
SELECT COUNT(*)
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт 3773. Это число всех строк. `COUNT(1)` даёт тот же результат. Какой вариант выбрать — дело вкуса.

### Считаем один столбец

`COUNT(столбец)` считает только строки, где значение **не `NULL`**.

```sql
SELECT COUNT(*) AS all_rows,
       COUNT(homepage_url) AS with_homepage
FROM tutorial.crunchbase_companies;
```

| all_rows | with_homepage |
|---|---|
| 66368 | 61310 |

У 5058 компаний сайт не указан. Это строки, где `homepage_url` равен `NULL`.

:::tip
Разница `COUNT(*) - COUNT(столбец)` — быстрый способ узнать, сколько в столбце `NULL`. Это частый шаг при проверке качества данных.
:::

### Не только числа

`COUNT` работает и для текста, и для дат:

```sql
SELECT COUNT(date) AS count_of_date
FROM tutorial.aapl_historical_stock_price;
```

`COUNT` считает непустые строки, а не разные значения. Для разных значений нужен `COUNT(DISTINCT ...)`. Он описан в [уроке про DISTINCT](/practice/sql/intermediate/#distinct).

### Имена столбцов

Без псевдонима столбец называется `count_star()`. Дайте ему понятное имя через `AS`. Пишите строчными буквами и с `_`.

```sql
SELECT COUNT(date) AS "Count Of Date"
FROM tutorial.aapl_historical_stock_price;
```

Если нужны пробелы, берите двойные кавычки. Лучше обойтись без них.

:::note
В DuckDB `COUNT(*)` называется `count_star()` в заголовке результата. В Postgres это `count`. На запрос это не влияет.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который посчитает непустые значения в каждом столбце таблицы `tutorial.aapl_historical_stock_price`: `year`, `month`, `open`, `high`, `low`, `close`, `volume`. По этим числам определите, в каком столбце больше всего `NULL`.

**Проверка:** в каждом столбце 3773. В наших данных `NULL` нет ни в одном столбце.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(year) AS year,
       COUNT(month) AS month,
       COUNT(open) AS open,
       COUNT(high) AS high,
       COUNT(low) AS low,
       COUNT(close) AS close,
       COUNT(volume) AS volume
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 2

В таблице `tutorial.crunchbase_companies` посчитайте компании, у которых заполнено `funding_total_usd`.

**Проверка:** 53583.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(funding_total_usd) AS companies_with_funding
FROM tutorial.crunchbase_companies;
```

</details>

#### Задание 3

Одним запросом посчитайте, сколько в `tutorial.crunchbase_companies` компаний без `category_code`. Не используйте `WHERE`.

**Проверка:** 3148.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) - COUNT(category_code) AS no_category
FROM tutorial.crunchbase_companies;
```

</details>

## SUM

`SUM` складывает все значения числового столбца. Работаем с таблицей `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Сумма по столбцу

```sql
SELECT SUM(volume) AS total_volume
FROM tutorial.aapl_historical_stock_price;
```

Запрос вернёт одно число: сколько всего акций продали за все дни.

Можно считать несколько сумм сразу:

```sql
SELECT SUM(open) AS sum_open,
       SUM(close) AS sum_close
FROM tutorial.aapl_historical_stock_price;
```

### Правила SUM

- `SUM` работает только с числами. Для текста будет ошибка.
- `SUM` пропускает `NULL`. Он не считает их нулями, а просто не берёт в расчёт.
- Если все значения `NULL`, `SUM` вернёт `NULL`, а не 0.

```sql
SELECT SUM(funding_total_usd) AS total_funding
FROM tutorial.crunchbase_companies;
```

У 12785 компаний `funding_total_usd` равен `NULL`. Они в сумме не участвуют.

:::tip
Чтобы получить 0 вместо `NULL`, оберните сумму в `COALESCE(SUM(x), 0)`.
:::

:::caution
`SUM` складывает значения по столбцу. Чтобы сложить два столбца в одной строке, используйте `+`: `open + close`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Посчитайте среднюю цену открытия (`open`) без функции `AVG`. Используйте `SUM`, `COUNT` и деление.

**Проверка:** около 178.30.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(open) / COUNT(open) AS avg_open_price
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 2

Посчитайте, сколько всего инвестиций получили компании со статусом `ipo` в таблице `tutorial.crunchbase_companies`.

**Проверка:** 209961181618.

<details>
<summary>Решение</summary>

```sql
SELECT SUM(funding_total_usd) AS ipo_funding
FROM tutorial.crunchbase_companies
WHERE status = 'ipo';
```

</details>

## MIN и MAX

`MIN` возвращает наименьшее значение столбца. `MAX` возвращает наибольшее. В этом уроке работаем с `tutorial.aapl_historical_stock_price`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

### MIN и MAX для чисел

```sql
SELECT MIN(volume) AS min_volume,
       MAX(volume) AS max_volume
FROM tutorial.aapl_historical_stock_price;
```

Обе функции пропускают `NULL`.

### MIN и MAX не только для чисел

Для текста `MIN` берёт первое значение по алфавиту, `MAX` — последнее. Для дат `MIN` — самая ранняя, `MAX` — самая поздняя.

```sql
SELECT MIN(date) AS first_day,
       MAX(date) AS last_day
FROM tutorial.aapl_historical_stock_price;
```

```sql
SELECT MIN(name) AS first_name,
       MAX(name) AS last_name
FROM tutorial.crunchbase_companies;
```

### Выражения внутри функций

Внутри `MAX` можно считать арифметику по строке. Сначала база считает выражение для каждой строки, потом берёт максимум:

```sql
SELECT MAX(high - low) AS max_day_range
FROM tutorial.aapl_historical_stock_price;
```

:::tip
Чтобы узнать, в какую **дату** случился максимум, одного `MAX` мало. Используйте `ORDER BY ... DESC LIMIT 1`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Каким был самый большой рост цены акции Apple за один день (`close - open`)?

**Проверка:** около 30.76.

<details>
<summary>Решение</summary>

```sql
SELECT MAX(close - open) AS max_day_increase
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 2

Какой была самая низкая цена акции Apple (столбец `low`) за период, который есть в данных?

**Проверка:** 12.72.

<details>
<summary>Решение</summary>

```sql
SELECT MIN(low) AS lowest_price
FROM tutorial.aapl_historical_stock_price;
```

</details>

## AVG

`AVG` считает среднее значение столбца. Работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Среднее по столбцу

```sql
SELECT AVG(high) AS avg_high
FROM tutorial.aapl_historical_stock_price;
```

`AVG` работает только с числами. Для текста будет ошибка.

### AVG и NULL

`AVG` пропускает `NULL`. Он делит сумму на число **непустых** значений. Это важно: `NULL` не равен нулю.

```sql
SELECT AVG(funding_total_usd) AS avg_funding,
       SUM(funding_total_usd) / COUNT(*) AS wrong_avg
FROM tutorial.crunchbase_companies;
```

| avg_funding | wrong_avg |
|---|---|
| 18478604 | 14918922 |

Второе число меньше. Оно делит сумму на все 66368 компаний, в том числе на тех, у кого нет данных.

:::caution
Перед тем как считать среднее, решите: пустое значение — это «неизвестно» или «ноль»? От ответа зависит результат. Если «ноль», используйте `AVG(COALESCE(x, 0))`.
:::

:::tip
`AVG` по столбцу целых чисел в DuckDB возвращает дробное число. В некоторых базах результат округляется до целого. Если сомневаетесь, приведите значение: `AVG(x::DOUBLE)`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который посчитает средний дневной объём торгов (`volume`) акций Apple.

**Проверка:** около 19259400.98.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(volume) AS avg_volume
FROM tutorial.aapl_historical_stock_price;
```

</details>

#### Задание 2

Посчитайте среднюю цену закрытия (`close`) только за 2014 год.

**Проверка:** около 295.40.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(close) AS avg_close_2014
FROM tutorial.aapl_historical_stock_price
WHERE year = 2014;
```

</details>

#### Задание 3

Посчитайте, сколько в среднем денег получили компании в таблице `tutorial.crunchbase_companies`, у которых `funding_total_usd` не `NULL`. Сравните с `AVG(COALESCE(funding_total_usd, 0))`.

**Проверка:** первое число около 18478604, второе около 14918922.

<details>
<summary>Решение</summary>

```sql
SELECT AVG(funding_total_usd) AS avg_known,
       AVG(COALESCE(funding_total_usd, 0)) AS avg_zero
FROM tutorial.crunchbase_companies;
```

</details>

## GROUP BY

`GROUP BY` делит строки на группы и считает агрегат для каждой группы. Без него агрегатная функция даёт один итог на всю таблицу. Здесь работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Итоги по группам

Сколько акций торговали в каждом году:

```sql
SELECT year,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

Запрос вернёт по одной строке на каждый год.

### Несколько столбцов в группе

Можно группировать по нескольким столбцам. Группа — это каждая уникальная пара значений:

```sql
SELECT year,
       month,
       COUNT(*) AS trading_days
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
ORDER BY year, month;
```

Вместо имён столбцов можно писать номера из `SELECT`:

```sql
SELECT year,
       month,
       COUNT(*) AS trading_days
FROM tutorial.aapl_historical_stock_price
GROUP BY 1, 2
ORDER BY 1, 2;
```

:::note
`GROUP BY 1, 2` работает в DuckDB, Postgres и в большинстве баз. Но номера хуже читаются. Если запрос длинный, лучше писать имена.
:::

### Главное правило

Каждый столбец в `SELECT` должен быть либо в `GROUP BY`, либо внутри агрегатной функции.

```sql
-- ошибка: month не в GROUP BY и не в агрегате
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year;
```

:::tip
В DuckDB есть сокращение `GROUP BY ALL`. Оно группирует по всем столбцам `SELECT`, которые не агрегаты. Это удобно, но в других базах не работает.
:::

### Порядок частей запроса

`SELECT` → `FROM` → `WHERE` → `GROUP BY` → `ORDER BY`. `WHERE` фильтрует строки до группировки.

```sql
SELECT status,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE country_code = 'USA'
GROUP BY status
ORDER BY companies DESC;
```

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Посчитайте, сколько всего акций торговали каждый месяц. Отсортируйте результат по времени.

**Проверка:** 180 строк. Первая строка: 2000, 1, 112099800.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
ORDER BY year, month;
```

</details>

#### Задание 2

Напишите запрос, который посчитает среднее дневное изменение цены акции Apple (`close - open`) по годам.

**Проверка:** 15 строк. В 2000 году среднее изменение около -0.115.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       AVG(close - open) AS avg_daily_change
FROM tutorial.aapl_historical_stock_price
GROUP BY 1
ORDER BY 1;
```

</details>

#### Задание 3

Напишите запрос, который найдёт самую низкую и самую высокую цену акции Apple за каждый месяц.

**Проверка:** 180 строк. Первая строка: 2000, 1, 86.5, 121.5.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       MIN(low) AS lowest_price,
       MAX(high) AS highest_price
FROM tutorial.aapl_historical_stock_price
GROUP BY 1, 2
ORDER BY 1, 2;
```

</details>

#### Задание 4

Посчитайте компании в `tutorial.crunchbase_companies` по статусам (`status`). Сначала самый частый статус.

**Проверка:** 4 строки. Первая: `operating`, 53034.

<details>
<summary>Решение</summary>

```sql
SELECT status,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
GROUP BY status
ORDER BY companies DESC;
```

</details>

## HAVING

`HAVING` фильтрует группы после `GROUP BY`. Он нужен, когда условие зависит от агрегата, например «только группы, где больше 1000 строк». Работаем с `tutorial.aapl_historical_stock_price` и `tutorial.crunchbase_companies`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Почему не WHERE

`WHERE` работает до группировки, когда агрегатов ещё нет. Условие с агрегатной функцией в `WHERE` вызовет ошибку.

```sql
-- ошибка: агрегат нельзя использовать в WHERE
SELECT year,
       month,
       MAX(high) AS month_high
FROM tutorial.aapl_historical_stock_price
WHERE MAX(high) > 400
GROUP BY year, month;
```

`HAVING` стоит после `GROUP BY`. Он видит уже посчитанные агрегаты:

```sql
SELECT year,
       month,
       MAX(high) AS month_high
FROM tutorial.aapl_historical_stock_price
GROUP BY year, month
HAVING MAX(high) > 400
ORDER BY year, month;
```

Запрос вернёт 35 месяцев, где цена хотя бы раз поднималась выше 400.

| | WHERE | HAVING |
|---|---|---|
| Когда работает | До `GROUP BY` | После `GROUP BY` |
| Что фильтрует | Строки | Группы |
| Агрегаты в условии | Нельзя | Можно |

### Порядок частей запроса

1. `SELECT`
2. `FROM`
3. `WHERE`
4. `GROUP BY`
5. `HAVING`
6. `ORDER BY`

Пишите части запроса именно в таком порядке.

### WHERE и HAVING вместе

`WHERE` убирает ненужные строки заранее. `HAVING` отбирает группы. Так запрос работает быстрее.

```sql
SELECT category_code,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE country_code = 'USA'
GROUP BY category_code
HAVING COUNT(*) >= 500
ORDER BY companies DESC;
```

:::note
В DuckDB в `HAVING` можно использовать псевдоним: `HAVING companies >= 500`. В Postgres это не работает, нужно повторить выражение: `HAVING COUNT(*) >= 500`.
:::

:::tip
`HAVING` — не единственный способ. Фильтровать итоги можно ещё через подзапрос. О нём будет отдельный урок.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Найдите годы, когда средний дневной объём торгов (`volume`) акций Apple был больше 35 миллионов. Покажите год и среднее значение.

**Проверка:** 2 строки: 2007 и 2008.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       AVG(volume) AS avg_volume
FROM tutorial.aapl_historical_stock_price
GROUP BY year
HAVING AVG(volume) > 35000000
ORDER BY year;
```

</details>

#### Задание 2

Покажите категории (`category_code`) компаний из `tutorial.crunchbase_companies`, в которых не меньше 1000 компаний. Не включайте компании без категории. Отсортируйте от большей категории к меньшей.

**Проверка:** 16 строк. Первая: `biotechnology`, 4468.

<details>
<summary>Решение</summary>

```sql
SELECT category_code,
       COUNT(*) AS companies
FROM tutorial.crunchbase_companies
WHERE category_code IS NOT NULL
GROUP BY category_code
HAVING COUNT(*) >= 1000
ORDER BY companies DESC;
```

</details>

#### Задание 3

Посчитайте суммарный объём торгов по месяцам 2014 года. Оставьте месяцы, где сумма больше 500 миллионов акций.

**Проверка:** 7 строк, с июня по декабрь. Для июня: 853087800.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       SUM(volume) AS volume_sum
FROM tutorial.aapl_historical_stock_price
WHERE year = 2014
GROUP BY year, month
HAVING SUM(volume) > 500000000
ORDER BY month;
```

</details>

## CASE

`CASE` — это условная логика в SQL, аналог `IF/THEN` в Excel. Он нужен, чтобы разложить значения по группам или посчитать «столбцы» по условию. В этом уроке работаем с таблицей `benn.college_football_players`: одна строка на игрока студенческого футбола. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

Столбец `year` — это курс: `FR`, `SO`, `JR`, `SR`.

### Синтаксис CASE

`CASE` состоит из пар `WHEN ... THEN`. Заканчивается словом `END`. Часть `ELSE` необязательна.

```sql
SELECT player_name,
       year,
       CASE WHEN year = 'SR' THEN 'yes'
            ELSE NULL END AS is_a_senior
FROM benn.college_football_players;
```

Как это работает:

- База проверяет условие `year = 'SR'` в каждой строке.
- Если условие верно, в новый столбец попадает `'yes'`.
- Если неверно, срабатывает `ELSE`. Здесь это `NULL`.

Если `ELSE` нет, результат тоже `NULL`. Чтобы вместо `NULL` было слово, напишите его в `ELSE`:

```sql
SELECT player_name,
       year,
       CASE WHEN year = 'SR' THEN 'yes'
            ELSE 'no' END AS is_a_senior
FROM benn.college_football_players;
```

### Несколько условий

Можно добавить много веток `WHEN`. База проверяет их сверху вниз и берёт **первую подходящую**.

```sql
SELECT player_name,
       weight,
       CASE WHEN weight > 250 THEN 'over 250'
            WHEN weight > 200 THEN '201-250'
            WHEN weight > 175 THEN '176-200'
            ELSE '175 or under' END AS weight_group
FROM benn.college_football_players;
```

Условия внутри `WHEN` можно объединять через `AND` и `OR`:

```sql
SELECT player_name,
       weight,
       CASE WHEN weight > 250 AND year = 'FR' THEN 'heavy freshman'
            ELSE 'other' END AS player_type
FROM benn.college_football_players;
```

:::tip
Порядок веток важен. Сначала ставьте более узкие условия. Если поставить `weight > 175` первым, остальные ветки никогда не сработают.
:::

### CASE и агрегаты

Новый столбец из `CASE` можно использовать в `GROUP BY`:

```sql
SELECT CASE WHEN year IN ('FR', 'SO') THEN 'underclass'
            WHEN year IN ('JR', 'SR') THEN 'upperclass'
            ELSE NULL END AS class_group,
       COUNT(1) AS players
FROM benn.college_football_players
GROUP BY 1;
```

### CASE внутри агрегата

Можно положить `CASE` внутрь `COUNT` или `SUM`. Так получаются отдельные столбцы для каждого значения, как в сводной таблице:

```sql
SELECT CASE WHEN year = 'FR' THEN 'FR'
            WHEN year = 'SO' THEN 'SO'
            WHEN year = 'JR' THEN 'JR'
            WHEN year = 'SR' THEN 'SR'
            ELSE 'No Year Data' END AS year_group,
       COUNT(1) AS count
FROM benn.college_football_players
GROUP BY 1;
```

Тот же результат, но курсы идут в столбцах, а не в строках:

```sql
SELECT COUNT(CASE WHEN year = 'FR' THEN 1 ELSE NULL END) AS fr_count,
       COUNT(CASE WHEN year = 'SO' THEN 1 ELSE NULL END) AS so_count,
       COUNT(CASE WHEN year = 'JR' THEN 1 ELSE NULL END) AS jr_count,
       COUNT(CASE WHEN year = 'SR' THEN 1 ELSE NULL END) AS sr_count
FROM benn.college_football_players;
```

`COUNT` не считает `NULL`. Поэтому в счёт попадают только строки, где сработало `WHEN`.

:::note
В DuckDB и Postgres есть короткая запись: `COUNT(*) FILTER (WHERE year = 'FR')`. Она делает то же самое, что `COUNT(CASE ...)`. `CASE` работает во всех базах.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, где есть столбец с пометкой `yes` для игроков из Калифорнии (`state = 'CA'`). Отсортируйте результат так, чтобы такие игроки шли первыми.

**Проверка:** 6935 строк. В начале списка идут 351 строка с `yes`.

<details>
<summary>Решение</summary>

```sql
SELECT player_name,
       state,
       CASE WHEN state = 'CA' THEN 'yes'
            ELSE NULL END AS from_california
FROM benn.college_football_players
ORDER BY 3;
```

</details>

#### Задание 2

Напишите запрос с именами игроков и столбцом, который делит их по росту (`height`, в дюймах) на четыре группы. Границы групп можно выбрать самим: у задачи много верных решений.

**Проверка:** 6935 строк. При границах из решения: `over 74` — 2771, `73-74` — 1654, `71-72` — 1413, `70 or under` — 1097.

<details>
<summary>Решение</summary>

```sql
SELECT player_name,
       height,
       CASE WHEN height > 74 THEN 'over 74'
            WHEN height > 72 AND height <= 74 THEN '73-74'
            WHEN height > 70 AND height <= 72 THEN '71-72'
            ELSE '70 or under' END AS height_group
FROM benn.college_football_players;
```

</details>

#### Задание 3

Выберите все столбцы из `benn.college_football_players` и добавьте столбец, где указано имя игрока, если он на третьем или четвёртом курсе (`JR` или `SR`).

**Проверка:** 6935 строк. Имя заполнено у 2952 игроков, у остальных `NULL`.

<details>
<summary>Решение</summary>

```sql
SELECT *,
       CASE WHEN year IN ('JR', 'SR') THEN player_name ELSE NULL END AS upperclass_player_name
FROM benn.college_football_players;
```

</details>

#### Задание 4

Посчитайте игроков с весом от 300 фунтов и больше по трём регионам: Западное побережье (CA, OR, WA), Техас (TX) и все остальные.

**Проверка:** 3 строки: `West Coast` — 68, `Texas` — 53, `Other` — 657.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN state IN ('CA', 'OR', 'WA') THEN 'West Coast'
            WHEN state = 'TX' THEN 'Texas'
            ELSE 'Other' END AS arbitrary_regional_designation,
       COUNT(1) AS players
FROM benn.college_football_players
WHERE weight >= 300
GROUP BY 1;
```

</details>

#### Задание 5

Напишите запрос, который посчитает суммарный вес игроков из Калифорнии отдельно для младших курсов (`FR`, `SO`) и старших курсов (`JR`, `SR`).

**Проверка:** 2 строки: `underclass` — 49603, `upperclass` — 31766.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN year IN ('FR', 'SO') THEN 'underclass'
            WHEN year IN ('JR', 'SR') THEN 'upperclass'
            ELSE NULL END AS class_group,
       SUM(weight) AS combined_player_weight
FROM benn.college_football_players
WHERE state = 'CA'
GROUP BY 1;
```

</details>

#### Задание 6

Покажите число игроков в каждом штате. Курсы `FR`, `SO`, `JR`, `SR` выведите в отдельных столбцах. Добавьте столбец с общим числом игроков. Штаты с наибольшим числом игроков должны идти первыми.

**Проверка:** первая строка: `TX`, 135, 111, 95, 95, итого 436.

<details>
<summary>Решение</summary>

```sql
SELECT state,
       COUNT(CASE WHEN year = 'FR' THEN 1 ELSE NULL END) AS fr_count,
       COUNT(CASE WHEN year = 'SO' THEN 1 ELSE NULL END) AS so_count,
       COUNT(CASE WHEN year = 'JR' THEN 1 ELSE NULL END) AS jr_count,
       COUNT(CASE WHEN year = 'SR' THEN 1 ELSE NULL END) AS sr_count,
       COUNT(1) AS total_players
FROM benn.college_football_players
GROUP BY state
ORDER BY total_players DESC;
```

</details>

#### Задание 7

Покажите, сколько игроков учатся в школах с названием на буквы от A до M и сколько в школах на буквы от N до Z.

Подсказка: названия в таблице начинаются с заглавной буквы, а `'A' < 'n'` верно для любой заглавной. Приведите название к нижнему регистру через `LOWER`.

**Проверка:** 2 строки: `A-M` — 3817, `N-Z` — 3118.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN LOWER(school_name) < 'n' THEN 'A-M'
            WHEN LOWER(school_name) >= 'n' THEN 'N-Z'
            ELSE NULL END AS school_name_group,
       COUNT(1) AS players
FROM benn.college_football_players
GROUP BY 1
ORDER BY 1;
```

</details>

## DISTINCT

`DISTINCT` убирает повторы. Он нужен, когда надо узнать, какие значения есть в столбце, или посчитать уникальные значения. Работаем с `tutorial.aapl_historical_stock_price`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

### Уникальные значения

```sql
SELECT DISTINCT month
FROM tutorial.aapl_historical_stock_price
ORDER BY month;
```

Запрос вернёт 12 строк, по одной на каждый месяц.

### DISTINCT для нескольких столбцов

`DISTINCT` действует на **всю строку** результата. Он убирает только те строки, которые полностью совпадают.

```sql
SELECT DISTINCT year, month
FROM tutorial.aapl_historical_stock_price
ORDER BY year, month;
```

Запрос вернёт 180 строк: каждая пара «год и месяц» встречается один раз.

:::caution
`DISTINCT(month)` с круглыми скобками работает так же, как `DISTINCT month`. Скобки ничего не меняют. Новички часто думают, что `DISTINCT` применяется только к одному столбцу. Это не так.
:::

### COUNT(DISTINCT ...)

`COUNT(DISTINCT x)` считает уникальные значения:

```sql
SELECT COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price;
```

Результат: 12.

В сочетании с `GROUP BY` можно считать уникальные значения по группам. В следующем примере база считает уникальные месяцы для каждого года.

```sql
SELECT year,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

:::caution
`DISTINCT` на большой таблице работает медленно. Базе нужно сравнить много строк. Если можно обойтись `GROUP BY` или фильтром, лучше так. На собеседовании об этом часто спрашивают.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который вернёт уникальные значения столбца `year` в хронологическом порядке.

**Проверка:** 15 строк, от 2000 до 2014.

<details>
<summary>Решение</summary>

```sql
SELECT DISTINCT year
FROM tutorial.aapl_historical_stock_price
ORDER BY year;
```

</details>

#### Задание 2

Напишите запрос, который посчитает число уникальных значений `month` для каждого года.

**Проверка:** 15 строк. В каждом году 12 месяцев.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price
GROUP BY year
ORDER BY year;
```

</details>

#### Задание 3

Напишите запрос, который отдельно посчитает число уникальных значений `month` и число уникальных значений `year`.

**Проверка:** одна строка: годов 15, месяцев 12.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT year) AS years_count,
       COUNT(DISTINCT month) AS months_count
FROM tutorial.aapl_historical_stock_price;
```

</details>

## JOIN

До сих пор мы работали с одной таблицей. Но данные обычно лежат в нескольких таблицах, и `JOIN` соединяет их. Это главная сила SQL. В этом уроке работаем с таблицами `benn.college_football_players` и `benn.college_football_teams`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Зачем нужны JOIN

Реляционная база хранит разные сущности в разных таблицах. Так данные не повторяются.

- В таблице игроков есть школа игрока, но нет конференции школы.
- В таблице команд есть конференция, но нет игроков.
- Школа (`school_name`) есть в обеих таблицах. Это ключ для связи.

Чтобы узнать, в какой конференции игроки тяжелее всех, нужны обе таблицы.

### Устройство JOIN

```sql
SELECT teams.conference AS conference,
       AVG(players.weight) AS average_weight
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.conference
ORDER BY AVG(players.weight) DESC;
```

Разберём запрос по частям:

| Часть | Что делает |
|---|---|
| `FROM ... players` | Первая (левая) таблица |
| `JOIN ... teams` | Вторая таблица |
| `ON teams.school_name = players.school_name` | Условие: какие строки соединять |
| `GROUP BY`, `ORDER BY` | Как обычно: группируют и сортируют результат |

### Псевдонимы таблиц

Имя `benn.college_football_players` длинное. Дайте таблице короткое имя: напишите его через пробел после имени таблицы.

```sql
SELECT players.player_name,
       players.school_name
FROM benn.college_football_players players
LIMIT 5;
```

После этого столбцы указывают через псевдоним: `players.player_name`. Это то же самое, что `benn.college_football_players.player_name`.

:::tip
Всегда пишите столбцы с псевдонимом таблицы, даже если имя не повторяется. Запрос легче читать. И он не сломается, когда в другой таблице появится столбец с таким же именем.
:::

### JOIN и ON

`ON` говорит базе, как сопоставить строки двух таблиц. Обычно это равенство ключей. Каждая строка слева ищет подходящие строки справа.

```sql
SELECT players.player_name,
       players.school_name,
       teams.conference
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

:::caution
Если забыть `ON`, DuckDB вернёт ошибку. А если условие неверное, получится много лишних строк. Всегда проверяйте число строк после `JOIN`.
:::

Какой именно тип соединения выбрать, расскажут следующие уроки: [INNER JOIN](/practice/sql/intermediate/#inner-join), [LEFT JOIN](/practice/sql/intermediate/#left-join) и другие.

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который вернёт школу, имя игрока, позицию и вес каждого игрока из штата Georgia (`GA`). Отсортируйте по весу от самого тяжёлого к самому лёгкому. Дайте таблице псевдоним и указывайте все столбцы через него.

**Проверка:** 335 строк. Первая строка: Auburn, Brian Barnes, DL, 331.

<details>
<summary>Решение</summary>

```sql
SELECT players.school_name,
       players.player_name,
       players.position,
       players.weight
FROM benn.college_football_players players
WHERE players.state = 'GA'
ORDER BY players.weight DESC;
```

</details>

#### Задание 2

Посчитайте число игроков в каждой конференции. Для этого соедините игроков с командами. Сначала конференция с наибольшим числом игроков.

**Проверка:** первая строка: `Southeastern`, 799.

<details>
<summary>Решение</summary>

```sql
SELECT teams.conference,
       COUNT(*) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.conference
ORDER BY players DESC;
```

</details>

## INNER JOIN

`INNER JOIN` оставляет только строки, у которых нашлась пара в обеих таблицах. Это тип соединения по умолчанию. В уроке работаем с `benn.college_football_players` и `benn.college_football_teams`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Как работает INNER JOIN

Запись `JOIN` и `INNER JOIN` — одно и то же.

```sql
SELECT players.player_name,
       teams.conference
FROM benn.college_football_players players
INNER JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name;
```

Правила:

- Игрок, чьей школы нет в таблице команд, не попадёт в результат.
- Команда, у которой нет игроков, тоже не попадёт.
- Это пересечение двух таблиц.

Если в таблице команд три строки с одним названием школы, каждый игрок этой школы появится три раза. Строки умножаются.

:::caution
Если число строк после `JOIN` стало больше, чем было, значит, ключ в одной из таблиц не уникален. Проверьте это сразу.
:::

В наших данных у каждого игрока есть команда. Поэтому `INNER JOIN` вернёт все 6935 строк.

### Одинаковые имена столбцов

В обеих таблицах есть столбец `school_name`. Если взять `players.*` и `teams.*`, в результате будет два столбца с одним именем. Это неудобно.

```sql
SELECT players.*,
       teams.*
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

Чтобы избежать путаницы, называйте столбцы через `AS`:

```sql
SELECT players.school_name AS players_school_name,
       teams.school_name AS teams_school_name
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

:::note
Если сохранить такой результат в таблицу, DuckDB добавит к повтору суффикс: `school_name_1`. В других базах поведение другое. Лучше всегда задавать псевдонимы.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Напишите запрос, который покажет имена игроков, названия школ и конференции для школ из дивизиона `FBS (Division I-A Teams)`.

**Проверка:** 5089 строк. Среди строк есть: Jamal Sullivan, Alabama, Southeastern.

<details>
<summary>Решение</summary>

```sql
SELECT players.player_name,
       players.school_name,
       teams.conference
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
WHERE teams.division = 'FBS (Division I-A Teams)';
```

</details>

#### Задание 2

Посчитайте игроков в каждом дивизионе.

**Проверка:** 2 строки: `FBS (Division I-A Teams)` — 5089, `FCS (Division I-AA Teams)` — 1846.

<details>
<summary>Решение</summary>

```sql
SELECT teams.division,
       COUNT(*) AS players
FROM benn.college_football_players players
INNER JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.division
ORDER BY teams.division;
```

</details>

## Внешние соединения (OUTER JOIN)

`INNER JOIN` теряет строки без пары. Внешние соединения (`OUTER JOIN`) могут их сохранить. Для таких уроков нужны данные, где пары есть не у всех строк. Мы возьмём данные Crunchbase: каталог стартапов, покупок и инвестиций. Подробнее о таблицах — в [описании данных](/practice/sql/datasets/).

### Виды внешних соединений

| Соединение | Что вернёт |
|---|---|
| `LEFT JOIN` | Все строки левой таблицы. Для строк без пары справа будет `NULL` |
| `RIGHT JOIN` | Все строки правой таблицы. Для строк без пары слева будет `NULL` |
| `FULL OUTER JOIN` | Все строки обеих таблиц |
| `INNER JOIN` | Только строки с парой в обеих таблицах |

Слово `OUTER` можно не писать. `LEFT JOIN` — то же, что `LEFT OUTER JOIN`. `FULL JOIN` — то же, что `FULL OUTER JOIN`.

Уроки дальше разбирают каждый вид отдельно:

- [LEFT JOIN](/practice/sql/intermediate/#left-join)
- [RIGHT JOIN](/practice/sql/intermediate/#right-join)
- [FULL OUTER JOIN](/practice/sql/intermediate/#full-outer-join)

### Данные Crunchbase

Первая таблица — компании. Одна строка на компанию.

```sql
SELECT *
FROM tutorial.crunchbase_companies
LIMIT 5;
```

Столбец `permalink` — уникальный идентификатор компании.

Вторая таблица — покупки компаний. Одна строка на покупку.

```sql
SELECT *
FROM tutorial.crunchbase_acquisitions
LIMIT 5;
```

Связь таблиц:

- `crunchbase_acquisitions.company_permalink` ссылается на `crunchbase_companies.permalink`. Так мы получаем данные о купленной компании.
- `crunchbase_acquisitions.acquirer_permalink` тоже ссылается на `crunchbase_companies.permalink`. Так мы получаем данные о покупателе.

Какой ключ брать, зависит от вопроса: интересует купленная компания или покупатель.

Такая схема встречается часто. Например, в таблице писем есть `sender_email` и `recipient_email`. Оба ссылаются на одну таблицу людей.

:::caution
Данные Crunchbase реальные и неидеальные. В таблице покупок 13027 строк ссылаются на компании, которых нет в `crunchbase_companies`. Поэтому внутреннее соединение теряет много строк. Это нормально для учебных данных, но в работе стоит разбираться, почему так.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Посчитайте строки в таблицах `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` двумя отдельными запросами или одним запросом с двумя подзапросами.

**Проверка:** компаний 66368, покупок 18968.

<details>
<summary>Решение</summary>

```sql
SELECT (SELECT COUNT(*) FROM tutorial.crunchbase_companies) AS companies_rows,
       (SELECT COUNT(*) FROM tutorial.crunchbase_acquisitions) AS acquisitions_rows;
```

</details>

#### Задание 2

Покупатель в таблице покупок указан в `acquirer_permalink`. Соедините `tutorial.crunchbase_acquisitions` с `tutorial.crunchbase_companies` по покупателю (`INNER JOIN`) и посчитайте строки.

**Проверка:** 6935.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS acquisitions_with_known_acquirer
FROM tutorial.crunchbase_acquisitions acquisitions
JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.acquirer_permalink;
```

</details>

#### Задание 3

Теперь повторите соединение из задания 2 как `LEFT JOIN` от таблицы покупок. Сколько строк получилось? Сколько из них без покупателя в таблице компаний?

**Проверка:** всего 18968 строк, из них без пары 12033.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS all_rows,
       COUNT(*) - COUNT(companies.permalink) AS no_acquirer_in_companies
FROM tutorial.crunchbase_acquisitions acquisitions
LEFT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.acquirer_permalink;
```

</details>

## LEFT JOIN

`LEFT JOIN` оставляет все строки левой таблицы, даже если справа нет пары. Для таких строк столбцы правой таблицы заполнены `NULL`. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Сначала INNER JOIN

Посмотрим на обычное соединение компаний и покупок:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1
LIMIT 10;
```

Одна компания может появиться в списке дважды. Так бывает, если у неё две записи о покупке. Обе записи присоединяются к строке компании.

### Тот же запрос как LEFT JOIN

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1
LIMIT 10;
```

Теперь в результате много строк с `NULL` в столбцах `acquisitions_permalink` и `acquired_date`. Это компании, которых никто не купил.

Правило: `LEFT JOIN` возвращает все строки таблицы из `FROM`, независимо от того, есть ли пара в таблице из `LEFT JOIN`.

### Строки без пары

Частый приём: найти строки левой таблицы, у которых нет пары. Для этого фильтруем `NULL` из правой таблицы:

```sql
SELECT companies.permalink,
       companies.name
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE acquisitions.company_permalink IS NULL
LIMIT 10;
```

:::tip
Для проверки пары берите столбец-ключ правой таблицы. Он не бывает `NULL`, если пара есть.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Выполните `INNER JOIN` таблиц `tutorial.crunchbase_acquisitions` и `tutorial.crunchbase_companies`. Вместо списка строк посчитайте непустые значения ключа в каждой таблице.

**Проверка:** обе колонки равны 5941.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(companies.permalink) AS companies_rowcount,
       COUNT(acquisitions.company_permalink) AS acquisitions_rowcount
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>

#### Задание 2

Измените запрос выше на `LEFT JOIN`. Обратите внимание на разницу в результатах.

**Проверка:** `companies_rowcount` — 66562, `acquisitions_rowcount` — 5941.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(companies.permalink) AS companies_rowcount,
       COUNT(acquisitions.company_permalink) AS acquisitions_rowcount
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>

#### Задание 3

Посчитайте по штатам число уникальных компаний и число уникальных купленных компаний. Не включайте строки, где штата нет. Отсортируйте по числу купленных компаний от большего к меньшему.

**Проверка:** первая строка: `CA`, 12900, 1937. Вторая: `MA`, 2542, 396.

<details>
<summary>Решение</summary>

```sql
SELECT companies.state_code,
       COUNT(DISTINCT companies.permalink) AS unique_companies,
       COUNT(DISTINCT acquisitions.company_permalink) AS unique_companies_acquired
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE companies.state_code IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;
```

</details>

## RIGHT JOIN

`RIGHT JOIN` — зеркало `LEFT JOIN`. Он оставляет все строки правой таблицы. Из левой таблицы берутся только строки с парой. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### RIGHT JOIN и LEFT JOIN дают одно и то же

Этот запрос оставляет все компании:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

Поменяйте таблицы местами и замените `LEFT` на `RIGHT`. Результат тот же:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_acquisitions acquisitions
RIGHT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.company_permalink;
```

В обоих запросах все компании сохранены. Меняется только порядок таблиц.

### Какой выбрать

- `RIGHT JOIN` используют редко. Любой запрос можно переписать через `LEFT JOIN`, поменяв таблицы местами.
- Принято всегда писать `LEFT JOIN`. Так запрос легче читать и проверять: главная таблица всегда в `FROM`.
- Технического запрета на `RIGHT JOIN` нет.

Записи `LEFT OUTER JOIN` и `RIGHT OUTER JOIN` — то же самое, что `LEFT JOIN` и `RIGHT JOIN`.

:::tip
Если видите в чужом запросе `RIGHT JOIN`, мысленно поменяйте таблицы местами. Станет проще понять, какие строки сохраняются.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Перепишите запрос из урока про [LEFT JOIN](/practice/sql/intermediate/#left-join), где вы считали все и купленные компании по штатам. Используйте `RIGHT JOIN` вместо `LEFT JOIN`. Результат должен быть таким же.

**Проверка:** первая строка: `CA`, 12900, 1937. Вторая: `MA`, 2542, 396.

<details>
<summary>Решение</summary>

```sql
SELECT companies.state_code,
       COUNT(DISTINCT companies.permalink) AS unique_companies,
       COUNT(DISTINCT acquisitions.company_permalink) AS acquired_companies
FROM tutorial.crunchbase_acquisitions acquisitions
RIGHT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.company_permalink
WHERE companies.state_code IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;
```

</details>

## Фильтр в WHERE или в ON

В запросе с `JOIN` условие можно поставить в `ON` или в `WHERE`. Для `INNER JOIN` результат одинаковый. Для `LEFT JOIN` результат разный. В этом уроке разберём почему. Работаем с `tutorial.crunchbase_companies`, `tutorial.crunchbase_acquisitions` и `tutorial.crunchbase_investments`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Фильтр в ON

Условие в `ON` применяется **до** соединения. Оно работает как `WHERE`, но только для одной таблицы.

Сначала запрос без фильтра:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1;
```

Теперь добавим условие в `ON`. Мы исключаем из правой таблицы покупку компании `1000memories`:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND acquisitions.company_permalink != '/organization/1000memories'
ORDER BY 1;
```

Что видно в результате:

- Компания `1000memories` осталась в левом столбце.
- В столбцах из таблицы покупок для неё стоит `NULL`.
- Строка осталась, потому что `LEFT JOIN` сохраняет левую таблицу.

### Фильтр в WHERE

`WHERE` работает **после** соединения. Он убирает строки целиком, из обеих таблиц.

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE acquisitions.company_permalink != '/organization/1000memories'
   OR acquisitions.company_permalink IS NULL
ORDER BY 1;
```

Теперь компании `1000memories` в результате нет совсем.

Мы добавили `OR ... IS NULL`. Без него `WHERE` убрал бы и все строки с `NULL` справа, то есть всех непроданных компаний. Сравнение с `NULL` никогда не бывает истинным.

| Вариант | Число строк | Что произошло |
|---|---|---|
| Без фильтра | 66562 | Все компании и все покупки |
| Фильтр в `ON` | 66562 | `1000memories` осталась, покупка обнулена |
| Фильтр в `WHERE` | 66561 | `1000memories` пропала |

:::caution
Условие в `WHERE` по столбцу правой таблицы превращает `LEFT JOIN` в `INNER JOIN`. Строки с `NULL` не пройдут фильтр. Если нужно сохранить левую таблицу, ставьте условие в `ON`.
:::

### Практика

Для этих задач мы берём новую таблицу `tutorial.crunchbase_investments`. В ней одна строка на инвестицию. У компании может быть несколько инвестиций. Один инвестор может вложиться в одну компанию несколько раз. Столбец `company_permalink` связан с `permalink` в `tutorial.crunchbase_companies`.

Перед решением изучите таблицу сами: посмотрите строки, посчитайте уникальные значения.

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Покажите название компании, её статус (`status`, из таблицы компаний) и число уникальных инвесторов. Отсортируйте по числу инвесторов от большего к меньшему. Оставьте только компании из штата New York (`NY`).

**Проверка:** 3947 строк. Первая строка: `Fab`, `acquired`, 34 (у `SeatGeek` тоже 34).

<details>
<summary>Решение</summary>

```sql
SELECT companies.name AS company_name,
       companies.status,
       COUNT(DISTINCT investments.investor_name) AS unique_investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
WHERE companies.state_code = 'NY'
GROUP BY 1, 2
ORDER BY 3 DESC;
```

</details>

#### Задание 2

Составьте список инвесторов по числу компаний, в которые они вложились. Добавьте строку для компаний без инвесторов. Отсортируйте от большего числа к меньшему.

**Проверка:** 30189 строк. Первая строка: `No Investors`, 21642. Дальше: `Y Combinator` — 758.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN investments.investor_name IS NULL THEN 'No Investors'
            ELSE investments.investor_name END AS investor,
       COUNT(DISTINCT companies.permalink) AS companies_invested_in
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

## FULL OUTER JOIN

`FULL OUTER JOIN` возвращает все строки обеих таблиц. Совпавшие строки соединяются. Несовпавшие остаются с `NULL` на месте другой таблицы. Он нужен реже других соединений. Чаще всего его используют вместе с агрегатами, чтобы понять, насколько таблицы пересекаются. Работаем с таблицами Crunchbase. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Как работает

Запись `FULL JOIN` и `FULL OUTER JOIN` — одно и то же.

| Строка | Есть слева | Есть справа |
|---|---|---|
| Только слева | да | `NULL` |
| Совпала | да | да |
| Только справа | `NULL` | да |

### Измеряем пересечение

Сколько компаний есть только в таблице компаний, сколько в обеих таблицах и сколько только в таблице покупок:

```sql
SELECT COUNT(CASE WHEN companies.permalink IS NOT NULL AND acquisitions.company_permalink IS NULL
                  THEN companies.permalink ELSE NULL END) AS companies_only,
       COUNT(CASE WHEN companies.permalink IS NOT NULL AND acquisitions.company_permalink IS NOT NULL
                  THEN companies.permalink ELSE NULL END) AS both_tables,
       COUNT(CASE WHEN companies.permalink IS NULL AND acquisitions.company_permalink IS NOT NULL
                  THEN acquisitions.company_permalink ELSE NULL END) AS acquisitions_only
FROM tutorial.crunchbase_companies companies
FULL JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

| companies_only | both_tables | acquisitions_only |
|---|---|---|
| 60621 | 5941 | 13027 |

Обратите внимание: третий столбец считает ключ из таблицы покупок. Если считать `companies.permalink`, получится 0, потому что в таких строках он `NULL`.

В таблице покупок совпала лишь часть строк. В реальной работе стоит посмотреть на несовпавшие строки и понять причину. Возможно, нужны другие данные.

:::tip
Хотите узнать, какие строки есть только в одной таблице? Используйте `FULL JOIN` с условием `WHERE левый_ключ IS NULL OR правый_ключ IS NULL`.
:::

### Практика

Для задачи используется таблица инвестиций Crunchbase. Мы разделили её на две части: `tutorial.crunchbase_investments_part1` и `tutorial.crunchbase_investments_part2`.

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments_part1` через `FULL JOIN`. Посчитайте, сколько строк есть только в компаниях, в обеих таблицах и только в инвестициях. Используйте подход из примера выше.

**Проверка:** `companies_only` — 43618, `both_tables` — 85072, `investments_only` — 1.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(CASE WHEN companies.permalink IS NOT NULL AND investments.company_permalink IS NULL
                  THEN companies.permalink ELSE NULL END) AS companies_only,
       COUNT(CASE WHEN companies.permalink IS NOT NULL AND investments.company_permalink IS NOT NULL
                  THEN companies.permalink ELSE NULL END) AS both_tables,
       COUNT(CASE WHEN companies.permalink IS NULL AND investments.company_permalink IS NOT NULL
                  THEN investments.company_permalink ELSE NULL END) AS investments_only
FROM tutorial.crunchbase_companies companies
FULL JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink;
```

</details>

## UNION

`JOIN` добавляет столбцы из другой таблицы. `UNION` добавляет **строки**. Он ставит результат одного запроса под результатом другого. Работаем с таблицами `tutorial.crunchbase_investments_part1` и `tutorial.crunchbase_investments_part2`. Это две половины таблицы инвестиций Crunchbase: первая содержит компании на буквы от A до L, вторая — от M до Z. Подробнее — в [описании данных](/practice/sql/datasets/).

### UNION

```sql
SELECT *
FROM tutorial.crunchbase_investments_part1

UNION

SELECT *
FROM tutorial.crunchbase_investments_part2;
```

`UNION` убирает полные дубликаты. Если строка из второго запроса точно совпадает со строкой из первого, останется одна.

### UNION ALL

`UNION ALL` оставляет все строки, ничего не убирает.

```sql
SELECT *
FROM tutorial.crunchbase_investments_part1

UNION ALL

SELECT *
FROM tutorial.crunchbase_investments_part2;
```

Проверим на наших данных:

| Запрос | Число строк |
|---|---|
| `UNION ALL` | 168647 |
| `UNION` | 168591 |

Разница в 56 строк — полные дубликаты внутри данных. `UNION` их убрал.

:::tip
`UNION ALL` быстрее: база не ищет дубликаты. Используйте его по умолчанию. `UNION` нужен только если дубликаты точно нужно убрать.
:::

### Правила UNION

- В обоих запросах одинаковое число столбцов.
- Типы данных столбцов совпадают и идут в одном порядке.
- Имена столбцов берутся из первого запроса. Совпадение имён не обязательно, но обычно имена совпадают.

Каждый `SELECT` пишется отдельно. Поэтому можно по-разному фильтровать части:

```sql
SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part1
WHERE company_name ILIKE 'A%'

UNION ALL

SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part2
WHERE company_name ILIKE 'Z%';
```

:::note
`ILIKE` есть в DuckDB и Postgres. Без него используйте `LOWER(company_name) LIKE 'a%'`.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Объедините две таблицы инвестиций через `UNION ALL`, сохранив дубликаты. Из первой таблицы возьмите компании с названием на букву D, из второй — на букву T (без учёта регистра). Оставьте столбцы `company_permalink`, `company_name` и `investor_name`.

В оригинальном курсе брали буквы T и M. В наших данных первая часть содержит A–L, а вторая M–Z. Поэтому мы выбрали D и T.

**Проверка:** 15710 строк (5680 из первой части и 10030 из второй).

<details>
<summary>Решение</summary>

```sql
SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part1
WHERE company_name ILIKE 'D%'

UNION ALL

SELECT company_permalink,
       company_name,
       investor_name
FROM tutorial.crunchbase_investments_part2
WHERE company_name ILIKE 'T%';
```

</details>

#### Задание 2

Напишите запрос с тремя столбцами. Первый — из какой части данные (`investments_part1` или `investments_part2`). Второй — статус компании. Третий — число уникальных инвесторов. Подсказка: понадобится таблица `tutorial.crunchbase_companies` и группировка по статусу и части данных.

**Проверка:** 8 строк (4 статуса на 2 части). Для `investments_part1`: `acquired` — 3955, `closed` — 3060, `ipo` — 1226, `operating` — 16912.

<details>
<summary>Решение</summary>

```sql
SELECT 'investments_part1' AS dataset_name,
       companies.status,
       COUNT(DISTINCT investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1, 2

UNION ALL

SELECT 'investments_part2' AS dataset_name,
       companies.status,
       COUNT(DISTINCT investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part2 investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1, 2
ORDER BY 1, 2;
```

</details>

## JOIN с операторами сравнения

Условие в `ON` необязательно должно быть равенством. Можно использовать `>`, `<`, `>=`, `<=`, `<>`. Так удобно соединять строки по диапазонам, например по датам. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments_part1`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

### Условие сравнения в ON

Посчитаем для каждой компании инвестиции, сделанные позже чем через 5 лет после основания:

```sql
SELECT companies.permalink,
       companies.name,
       companies.status,
       COUNT(investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND investments.funded_year > companies.founded_year + 5
GROUP BY 1, 2, 3;
```

Здесь в `ON` два условия:

- Равенство ключей: `companies.permalink = investments.company_permalink`.
- Сравнение лет: `investments.funded_year > companies.founded_year + 5`.

Присоединяются только те инвестиции, которые подходят под оба условия. Компании без таких инвестиций остаются в результате с нулём.

### То же условие в WHERE

Результат будет другим, если поставить сравнение в `WHERE`:

```sql
SELECT companies.permalink,
       companies.name,
       companies.status,
       COUNT(investments.investor_permalink) AS investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
WHERE investments.funded_year > companies.founded_year + 5
GROUP BY 1, 2, 3;
```

`WHERE` работает после соединения. Он убирает все компании, у которых нет подходящих инвестиций.

| Вариант | Число строк |
|---|---|
| Условие в `ON` | 66368 (все компании) |
| Условие в `WHERE` | 4216 (только компании с подходящими инвестициями) |

Сумма в столбце `investors` в обоих случаях одинакова: 15864. Но в первом запросе есть все компании, а во втором — только часть.

Подробнее об этом — в уроке [Фильтр в WHERE или в ON](/practice/sql/intermediate/#фильтр-в-where-или-в-on).

:::caution
`founded_year` в наших данных иногда «грязный»: есть значения вроде 1015 и 2914. Для учебных запросов это не мешает, но в работе такие значения надо чистить.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments` по ключу и по условию: год инвестиции равен году основания компании (`funded_year = founded_year`). Используйте `INNER JOIN` и посчитайте строки.

**Проверка:** 19197.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS investments_in_founding_year
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
 AND investments.funded_year = companies.founded_year;
```

</details>

#### Задание 2

Посчитайте число строк в запросе из урока, где условие `funded_year > founded_year + 5` стоит в `ON`, и в запросе, где оно стоит в `WHERE`. Используйте `tutorial.crunchbase_investments_part1`. Объясните разницу.

**Проверка:** 66368 и 4216.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_on
FROM (
  SELECT companies.permalink
  FROM tutorial.crunchbase_companies companies
  LEFT JOIN tutorial.crunchbase_investments_part1 investments
    ON companies.permalink = investments.company_permalink
   AND investments.funded_year > companies.founded_year + 5
  GROUP BY companies.permalink
) t;

SELECT COUNT(*) AS rows_where
FROM (
  SELECT companies.permalink
  FROM tutorial.crunchbase_companies companies
  LEFT JOIN tutorial.crunchbase_investments_part1 investments
    ON companies.permalink = investments.company_permalink
  WHERE investments.funded_year > companies.founded_year + 5
  GROUP BY companies.permalink
) t;
```

</details>

#### Задание 3

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` по ключу и по условию: покупка случилась не позже чем через год после основания (`acquired_year <= founded_year + 1`). Посчитайте строки.

**Проверка:** 265.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS quick_acquisitions
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND acquisitions.acquired_year <= companies.founded_year + 1;
```

</details>

## JOIN по нескольким ключам

В `ON` можно связать таблицы сразу по нескольким столбцам. Условия соединяют через `AND`. Это нужно в двух случаях: когда одного ключа мало, чтобы однозначно найти строку, и когда нужно дополнительно проверить данные. Работаем с таблицами Crunchbase. Подробнее — в [описании данных](/practice/sql/datasets/).

### Два условия в ON

```sql
SELECT companies.permalink,
       companies.name,
       investments.company_name,
       investments.company_permalink
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND companies.name = investments.company_name;
```

Здесь строки соединяются, только если совпали и `permalink`, и название компании.

В наших данных результат такой же, как при соединении только по `permalink`: 128690 строк. Название везде совпадает с ключом, поэтому второе условие ничего не отсекает.

### Зачем нужен второй ключ

- **Составной ключ.** Если строку определяют два столбца (например, `год` и `страна`), нужны оба.
- **Проверка данных.** Второе условие убирает ложные совпадения, если ключ в одной из таблиц загрязнён.
- **Скорость.** Иногда лишнее условие помогает базе быстрее найти строки. На маленьких таблицах эффект почти не виден.

:::tip
Если после добавления второго условия число строк уменьшилось, значит, часть строк совпала по первому ключу, но не по второму. Это повод изучить данные.
:::

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Выполните `LEFT JOIN` таблицы `tutorial.crunchbase_companies` с `tutorial.crunchbase_investments_part1` по двум ключам: `permalink = company_permalink` и `name = company_name`. Посчитайте строки результата.

**Проверка:** 128690.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_count
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND companies.name = investments.company_name;
```

</details>

#### Задание 2

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` (`INNER JOIN`) по `permalink = company_permalink` и по категории: `category_code = company_category_code`. Посчитайте строки. Сравните с соединением только по `permalink`.

**Проверка:** с двумя ключами 5784, только по `permalink` 5941. Разница — 157 строк, где категория не совпала.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS two_keys
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND companies.category_code = acquisitions.company_category_code;

SELECT COUNT(*) AS one_key
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>

## Self JOIN

Self JOIN соединяет таблицу саму с собой. Он нужен, когда надо сравнить строки одной таблицы между собой. Например: «компании, которые получили инвестицию из Великобритании после инвестиции из Японии». Работаем с `tutorial.crunchbase_investments_part1`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

### Как это пишется

Особого синтаксиса нет. Одну и ту же таблицу пишем дважды и даём разные псевдонимы:

```sql
SELECT DISTINCT japan_investments.company_name,
       japan_investments.company_permalink
FROM tutorial.crunchbase_investments_part1 japan_investments
JOIN tutorial.crunchbase_investments_part1 gb_investments
  ON japan_investments.company_name = gb_investments.company_name
 AND gb_investments.investor_country_code = 'GBR'
 AND gb_investments.funded_at > japan_investments.funded_at
WHERE japan_investments.investor_country_code = 'JPN'
ORDER BY 1;
```

Как читать запрос:

- `japan_investments` — инвестиции японских инвесторов (фильтр в `WHERE`).
- `gb_investments` — инвестиции британских инвесторов (фильтр в `ON`).
- Строки соединяются по одной и той же компании.
- Условие `gb_investments.funded_at > japan_investments.funded_at` оставляет случаи, когда британская инвестиция была позже японской.

Запрос вернёт 13 компаний. Первая в списке: `Aperto Networks`.

:::note
Мы используем только первую половину таблицы инвестиций. Остальные данные лежат в `tutorial.crunchbase_investments_part2`. Поэтому в результате лишь часть компаний.
:::

:::tip
Даты здесь хранятся строками `YYYY-MM-DD`. Для таких строк сравнение `>` работает правильно: формат сортируется по алфавиту так же, как по времени.
:::

### Другие примеры

Self JOIN нужен не только для дат. Типичные случаи:

- Сотрудники и руководители в одной таблице.
- Пары товаров, которые покупают вместе.
- Цепочки: компания, которую купили, а потом она сама купила другую.

### Что дальше

Вы прошли средний уровень SQL. Дальше идёт продвинутый уровень: типы данных, подзапросы, оконные функции и другое.

### Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

#### Задание 1

Найдите компании, которые получили инвестицию от инвестора из Великобритании (`GBR`) позже, чем от инвестора из США (`USA`). Используйте `tutorial.crunchbase_investments_part1` и соедините компании по `company_permalink`. Посчитайте уникальные компании.

**Проверка:** 372.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT usa_investments.company_permalink) AS companies
FROM tutorial.crunchbase_investments_part1 usa_investments
JOIN tutorial.crunchbase_investments_part1 gb_investments
  ON usa_investments.company_permalink = gb_investments.company_permalink
 AND gb_investments.investor_country_code = 'GBR'
 AND gb_investments.funded_at > usa_investments.funded_at
WHERE usa_investments.investor_country_code = 'USA';
```

</details>

#### Задание 2

Найдите компании, у которых был раунд типа `seed`, а позже раунд типа `venture`. Используйте `tutorial.crunchbase_investments_part1`. Посчитайте уникальные компании.

**Проверка:** 1518.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT seed.company_permalink) AS companies
FROM tutorial.crunchbase_investments_part1 seed
JOIN tutorial.crunchbase_investments_part1 venture
  ON seed.company_permalink = venture.company_permalink
 AND venture.funding_round_type = 'venture'
 AND venture.funded_at > seed.funded_at
WHERE seed.funding_round_type = 'seed';
```

</details>

#### Задание 3

В `tutorial.crunchbase_acquisitions` найдите компании, которых купили, а потом они сами стали покупателями. Для этого соедините таблицу саму с собой: `company_permalink` одной копии должен совпасть с `acquirer_permalink` другой. Посчитайте уникальные такие компании.

**Проверка:** 1345.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT bought.company_permalink) AS companies
FROM tutorial.crunchbase_acquisitions bought
JOIN tutorial.crunchbase_acquisitions bought_others
  ON bought.company_permalink = bought_others.acquirer_permalink;
```

</details>
