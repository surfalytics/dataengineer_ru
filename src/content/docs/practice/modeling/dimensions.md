---
title: Таблицы измерений
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Dimension table: surrogate key и dim_date | Инжиниринг Данных"
description: Как построить таблицы измерений для DWH. Surrogate key и natural key, календарь dim_date, unknown member, денормализация. Практика в DuckDB.
sidebar:
  order: 6
  label: Таблицы измерений
tags:
  - data-modelling
  - practice
  - duckdb
---
В этом уроке строим четыре измерения: `dim_date`, `dim_product`, `dim_store`, `dim_customer`. В следующем уроке к ним подключим факт.

## Surrogate key и natural key

У клиента в источнике уже есть ключ — `customer_id`. Это **natural key** (бизнес-ключ). Он пришёл из системы-источника.

В хранилище измерение получает **свой** ключ — **surrogate key**. Это просто номер: 1, 2, 3... Он ничего не значит для бизнеса. Fact table ссылается только на surrogate key.

Зачем второй ключ:

- **Источников несколько.** В CRM клиент 42 — это Иван. В интернет-магазине клиент 42 — это Мария. Surrogate key разводит их.
- **История.** Клиент переехал. В хранилище у него две строки: до и после. У них один `customer_id`, но разные surrogate key. Подробно — в уроке [SCD](/practice/modeling/scd/).
- **Источник меняет ключи.** Новая CRM, миграция, переиспользование номеров. Хранилище от этого не ломается.
- **Специальные строки.** Например, «неизвестный клиент» с ключом `-1`.
- **Скорость.** Целое число — самый быстрый ключ для `JOIN`.

Natural key **остаётся** в измерении обычной колонкой. По нему ETL находит нужную строку.

<details>
<summary>Как генерируют surrogate key на практике</summary>

| Способ | Пример | Где встречается |
|---|---|---|
| Последовательность | `row_number()`, `SEQUENCE`, `IDENTITY` | Классические DWH |
| Хеш от natural key | `md5(source || '|' || customer_id)` | dbt (`dbt_utils.generate_surrogate_key`), Data Vault, облачные DWH |

В уроке используем `row_number()`: так проще читать результат. Хеш удобен, когда таблицы строят параллельно: ключ можно посчитать без обращения к измерению.

</details>

## Измерение даты

Дата есть почти в каждом факте. Но голой даты мало. Бизнес спрашивает: «а в выходные?», «а в праздники?», «по кварталам?», «по финансовому году?».

Поэтому делают отдельную таблицу-календарь `dim_date`. Одна строка — один день. В ней все атрибуты дня, которые нужны отчётам.

Ключ `dim_date` — исключение из правила «ключ ничего не значит». Обычно это число вида `20250131`. Его легко читать и легко получить из даты.

## Unknown member

В источнике у части заказов нет клиента: покупка в магазине без карты. Если в факте оставить `customer_key = NULL`:

- `JOIN` потеряет эти строки, и выручка не сойдётся;
- в отчёте будет пустая строка без подписи.

Решение — специальная строка в измерении: `customer_key = -1`, имя «Гость». Факт ссылается на неё. Так `JOIN` всегда находит пару, а в отчёте видно понятную подпись.

Так же делают для «не применимо» и «ещё не наступило». Например, дата доставки заказа, который ещё в пути.

## Правила для атрибутов

- **Понятный текст, а не коды.** `«Онлайн»`, а не `1`. `«Выходной»`, а не `true`.
- **Без NULL.** Пишите `«Неизвестно»`. NULL плохо группируется и фильтруется в BI.
- **Денормализуйте иерархии.** Категория — колонка в `dim_product`, а не отдельная таблица.
- **Добавляйте производные атрибуты.** Ценовой диапазон, «год регистрации». Аналитику не придётся писать `CASE` в каждом отчёте.

## Практика: строим измерения

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Подготовка: база `modeling.duckdb` открыта.

### dim_date

Календарь на весь 2025 год и строка `-1` для неизвестной даты.

```sql
CREATE OR REPLACE TABLE dim_date AS
WITH holidays(d) AS (
    SELECT unnest([DATE '2025-01-01', DATE '2025-01-02', DATE '2025-01-03', DATE '2025-01-06',
                   DATE '2025-01-07', DATE '2025-01-08', DATE '2025-05-01', DATE '2025-05-02',
                   DATE '2025-05-08', DATE '2025-05-09', DATE '2025-06-12', DATE '2025-06-13',
                   DATE '2025-11-03', DATE '2025-11-04', DATE '2025-12-31'])
),
days AS (
    SELECT d::DATE AS d
    FROM generate_series(DATE '2025-01-01', DATE '2025-12-31', INTERVAL 1 DAY) t(d)
)
SELECT
    strftime(d, '%Y%m%d')::INT AS date_key,
    d                          AS full_date,
    year(d)                    AS year,
    quarter(d)                 AS quarter,
    month(d)                   AS month,
    ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль',
     'Август','Сентябрь','Октябрь','Ноябрь','Декабрь'][month(d)] AS month_name,
    strftime(d, '%Y-%m')       AS year_month,
    isodow(d)                  AS day_of_week,
    ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'][isodow(d)]               AS day_name,
    CASE WHEN isodow(d) >= 6 THEN 'Выходной' ELSE 'Будний' END    AS day_type,
    d IN (SELECT d FROM holidays)                                  AS is_holiday
FROM days
UNION ALL
SELECT -1, NULL, NULL, NULL, NULL, 'Неизвестно', 'Неизвестно', NULL, 'Неизвестно', 'Неизвестно', false;

SELECT * FROM dim_date WHERE date_key IN (20250101, 20250614, -1);
```

### dim_product

Категорию кладём прямо в товар. Добавляем производный атрибут — ценовой диапазон.

```sql
CREATE OR REPLACE TABLE dim_product AS
SELECT
    row_number() OVER (ORDER BY p.product_id) AS product_key,
    p.product_id,
    p.sku,
    p.product_name,
    p.brand,
    c.category_name,
    CASE WHEN p.list_price >= 5000 THEN 'Премиум' ELSE 'Базовый' END AS price_band
FROM src.products p
JOIN src.categories c ON c.category_id = p.category_id;
```

Цену в измерение **не кладём**. Цена продажи — это факт. Текущая цена из справочника меняется и обманет отчёты по прошлым продажам.

### dim_store

```sql
CREATE OR REPLACE TABLE dim_store AS
SELECT
    row_number() OVER (ORDER BY store_id) AS store_key,
    store_id,
    store_name,
    city,
    region,
    CASE store_type WHEN 'online' THEN 'Онлайн' ELSE 'Офлайн' END AS store_type,
    opened_on
FROM src.stores;
```

### dim_customer

Пока берём клиентов как есть, на 1 января. Историю изменений добавим в уроке [SCD](/practice/modeling/scd/). Добавляем строку `-1` для гостей.

```sql
CREATE OR REPLACE TABLE dim_customer AS
SELECT
    row_number() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_name,
    email,
    city,
    segment,
    signup_date,
    year(signup_date) AS signup_year
FROM src.customers
UNION ALL
SELECT -1, NULL, 'Гость', NULL, 'Неизвестно', 'Гость', NULL, NULL;
```

### Задание 1

Проверьте `dim_customer`: сколько в ней строк? Уникален ли `customer_key`? Уникален ли `customer_id` (без строки `-1`)?

**Проверка:** 301 строка (300 клиентов + гость). Оба ключа уникальны.

<details>
<summary>Решение</summary>

```sql
SELECT count(*)                     AS rows,
       count(DISTINCT customer_key) AS unique_keys,
       count(DISTINCT customer_id)  AS unique_ids   -- NULL у гостя не считается
FROM dim_customer;
```

Такую проверку делают после каждой сборки измерения. В dbt это тесты `unique` и `not_null`.

</details>

### Задание 2

Сколько в первом квартале 2025 года выходных дней? Сколько праздников выпало на будни?

**Проверка:** 26 выходных. 6 праздников в будни: 1, 2, 3, 6, 7 и 8 января.

<details>
<summary>Решение</summary>

```sql
SELECT count(*) FILTER (WHERE day_type = 'Выходной')              AS weekends,
       count(*) FILTER (WHERE is_holiday AND day_type = 'Будний') AS weekday_holidays
FROM dim_date
WHERE quarter = 1;
```

</details>

### Задание 3

Сколько товаров в каждой категории и каждом ценовом диапазоне? Заметьте: запрос к измерению без `JOIN`.

**Проверка:** 5 строк. У «Аксессуары»: 4 базовых и 0 премиум-товаров.

<details>
<summary>Решение</summary>

```sql
SELECT category_name,
       count(*) FILTER (WHERE price_band = 'Базовый') AS base,
       count(*) FILTER (WHERE price_band = 'Премиум') AS premium
FROM dim_product
GROUP BY category_name
ORDER BY category_name;
```

Полный результат:

| category_name | Базовый | Премиум |
|---|---|---|
| Аксессуары | 4 | 0 |
| Обувь | 1 | 3 |
| Одежда | 3 | 1 |
| Снаряжение | 3 | 1 |
| Электроника | 1 | 3 |

</details>

### Задание 4

Добавьте в `dim_customer` атрибут `tenure_group`: «Новый», если клиент зарегистрировался в 2024 году, иначе «Давний». Гостю — «Неизвестно». Сколько клиентов в каждой группе?

**Проверка:** Давний — 147, Новый — 153, Неизвестно — 1.

<details>
<summary>Решение</summary>

Пересобираем измерение целиком. Так запрос можно запускать сколько угодно раз.

```sql
CREATE OR REPLACE TABLE dim_customer AS
SELECT
    row_number() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_name,
    email,
    city,
    segment,
    signup_date,
    year(signup_date) AS signup_year,
    CASE WHEN year(signup_date) = 2024 THEN 'Новый' ELSE 'Давний' END AS tenure_group
FROM src.customers
UNION ALL
SELECT -1, NULL, 'Гость', NULL, 'Неизвестно', 'Гость', NULL, NULL, 'Неизвестно';

SELECT tenure_group, count(*) FROM dim_customer GROUP BY ALL ORDER BY ALL;
```

В dbt так и работают: модель — это `SELECT`, и таблица пересобирается целиком при каждом запуске.

</details>

### Задание 5

Почему в факте нельзя просто хранить `customer_id` из источника вместо `customer_key`? Назовите две причины.

<details>
<summary>Ответ</summary>

- У гостя нет `customer_id`. Нужен `-1` и подпись «Гость».
- Когда клиент переедет, у него будет две версии в измерении. `customer_id` одинаковый, и факт не сможет выбрать нужную версию.
- Если появится второй источник клиентов, номера могут совпасть.

</details>

## Итог

- Измерение — широкая денормализованная таблица с понятными атрибутами.
- Факт ссылается на surrogate key. Natural key остаётся в измерении.
- Календарь `dim_date` — отдельное измерение с атрибутами дня.
- Unknown member `-1` защищает от потери строк и пустых подписей.

**Глубже:** [глава 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) — date dimension, product dimension, degenerate dimension. [Глава 2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) — все техники для dimensions.

Дальше: [Строим fact table](/practice/modeling/fact-sales/).
