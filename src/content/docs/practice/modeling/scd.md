---
title: Slowly Changing Dimensions
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "SCD Type 1, 2, 3: Slowly Changing Dimensions | Инжиниринг Данных"
description: Что такое Slowly Changing Dimensions, чем отличаются SCD Type 0, 1, 2 и 3, как построить SCD2 с valid_from и valid_to и связать его с фактами в DuckDB.
sidebar:
  order: 9
  label: SCD
tags:
  - data-modelling
  - practice
  - duckdb
---
Атрибуты измерений меняются. Клиент переезжает. Товар переводят в другую категорию. Магазин меняет регион. Меняются они **медленно**: редко и непредсказуемо. Отсюда название — **Slowly Changing Dimensions (SCD)**.

Вопрос: клиент из Санкт-Петербурга переехал в Казань. Его покупки за январь — это выручка Петербурга или Казани?

Правильный ответ зависит от вопроса бизнеса. SCD — набор способов, как хранить изменения, чтобы ответить правильно.

## Типы SCD

![Четыре способа обработать переезд клиента 79: Type 0 ничего не меняет, Type 1 перезаписывает, Type 2 добавляет строку, Type 3 добавляет колонку](/assets/practice/modeling/scd-types.png)

| Тип | Что делаем | История | Когда использовать |
|---|---|---|---|
| **Type 0** | Ничего. Значение не меняется никогда | Только исходное значение | Дата регистрации, дата рождения |
| **Type 1** | Перезаписываем старое значение | Нет | Исправление опечаток. Атрибуты, история которых не важна: email, телефон |
| **Type 2** | Добавляем новую строку-версию | Полная | Атрибуты, по которым анализируют прошлое: город, сегмент, категория |
| **Type 3** | Добавляем колонку `previous_...` | Только одно прошлое значение | Переходный период: «старый и новый регион» после реорганизации |

Есть и другие типы. Их используют реже:

- **Type 4 (mini-dimension).** Часто меняющиеся атрибуты (возрастная группа, уровень дохода) выносят в отдельное маленькое измерение. Иначе Type 2 создаст слишком много версий.
- **Type 6 (1 + 2 + 3).** Type 2, но в каждой версии есть ещё колонка `current_city` с текущим значением (Type 1). Позволяет смотреть и «как было», и «как сейчас».

Тип выбирают **для каждого атрибута**, а не для всей таблицы. В одном `dim_customer` email может быть Type 1, город — Type 2, дата регистрации — Type 0.

## Как устроен Type 2

Каждая версия — отдельная строка со своим surrogate key. Плюс служебные колонки:

| Колонка | Смысл |
|---|---|
| `customer_key` | Surrogate key **версии**. Уникален |
| `customer_id` | Natural key. Одинаковый у всех версий клиента |
| `valid_from` | С какой даты версия действует (включительно) |
| `valid_to` | До какой даты (не включительно). У текущей версии — `9999-12-31` |
| `is_current` | `true` у текущей версии. Для удобства фильтра |

Клиент 82 за полгода изменился дважды: стал VIP, потом переехал. В Type 2 у него три строки:

| customer_key | customer_id | city | segment | valid_from | valid_to | is_current |
|---|---|---|---|---|---|---|
| 93 | 82 | Москва | Обычный | 2024-11-19 | 2025-02-04 | false |
| 94 | 82 | Москва | VIP | 2025-02-04 | 2025-05-06 | false |
| 95 | 82 | Санкт-Петербург | VIP | 2025-05-06 | 9999-12-31 | true |

### Point-in-time lookup

Fact table должен ссылаться на версию, которая действовала **в момент события**. Поэтому key lookup ищет не только по `customer_id`, но и по дате:

```text
ON c.customer_id = o.customer_id
AND o.order_date >= c.valid_from
AND o.order_date <  c.valid_to
```

Покупка 82-го клиента 10 марта получит ключ 94 (Москва, VIP). Покупка 1 июня — ключ 95 (Санкт-Петербург). Факт **навсегда** запоминает контекст события.

Интервал «включительно — не включительно» (`>=` и `<`) нужен, чтобы дата смены попала ровно в одну версию.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Подготовка: база `modeling.duckdb` открыта, `fact_sales` создан.

Источник `src.customers` — клиенты на 1 января. `src.customer_changes` — журнал изменений за полгода. Это похоже на CDC (Change Data Capture): поток изменений из базы-источника.

```sql
SELECT * FROM src.customer_changes WHERE customer_id = 82;
```

### Type 1: только текущее состояние

Применяем к каждому клиенту **последнее** изменение. Старые значения теряются.

```sql
CREATE OR REPLACE TABLE dim_customer_type1 AS
WITH last_change AS (
    SELECT * FROM src.customer_changes
    QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY changed_at DESC) = 1
)
SELECT c.customer_id, c.customer_name,
       coalesce(l.city, c.city)       AS city,
       coalesce(l.segment, c.segment) AS segment
FROM src.customers c
LEFT JOIN last_change l ON l.customer_id = c.customer_id;

SELECT * FROM dim_customer_type1 WHERE customer_id = 82;
```

`QUALIFY` — фильтр по результату оконной функции. Он есть в DuckDB, Snowflake, BigQuery.

### Type 2: все версии

Собираем версии: исходное состояние плюс каждое изменение. `valid_to` — это `valid_from` следующей версии. Функция `lead()` берёт значение из следующей строки.

```sql
CREATE OR REPLACE TABLE dim_customer AS
WITH versions AS (
    -- версия 1: состояние на 1 января, действует с даты регистрации
    SELECT customer_id, city, segment, signup_date AS valid_from
    FROM src.customers
    UNION ALL
    -- следующие версии: из журнала изменений
    SELECT customer_id, city, segment, changed_at
    FROM src.customer_changes
),
ranged AS (
    SELECT *,
           lead(valid_from, 1, DATE '9999-12-31')
               OVER (PARTITION BY customer_id ORDER BY valid_from) AS valid_to
    FROM versions
)
SELECT
    row_number() OVER (ORDER BY r.customer_id, r.valid_from) AS customer_key,
    r.customer_id,
    c.customer_name,                 -- Type 1: берём текущее
    c.email,                         -- Type 1
    r.city,                          -- Type 2
    r.segment,                       -- Type 2
    c.signup_date,                   -- Type 0
    year(c.signup_date) AS signup_year,
    CASE WHEN year(c.signup_date) = 2024 THEN 'Новый' ELSE 'Давний' END AS tenure_group,
    r.valid_from,
    r.valid_to,
    r.valid_to = DATE '9999-12-31' AS is_current
FROM ranged r
JOIN src.customers c ON c.customer_id = r.customer_id
UNION ALL
SELECT -1, NULL, 'Гость', NULL, 'Неизвестно', 'Гость', NULL, NULL, 'Неизвестно',
       DATE '1900-01-01', DATE '9999-12-31', true;

SELECT customer_key, customer_id, city, segment, valid_from, valid_to, is_current
FROM dim_customer
WHERE customer_id = 82
ORDER BY valid_from;
```

### Пересобираем fact_sales

Ключи клиентов изменились. Пересоберём факт с **point-in-time lookup**. Остальное — как в уроке [Строим fact table](/practice/modeling/fact-sales/).

```sql
CREATE OR REPLACE TABLE fact_sales AS
SELECT
    d.date_key,
    coalesce(c.customer_key, -1) AS customer_key,
    p.product_key,
    s.store_key,
    o.order_id,
    i.line_number,
    i.quantity,
    i.quantity * i.unit_price                     AS gross_amount,
    i.discount_amount,
    i.quantity * i.unit_price - i.discount_amount AS net_amount,
    round(o.shipping_cost
          * (i.quantity * i.unit_price - i.discount_amount)
          / sum(i.quantity * i.unit_price - i.discount_amount) OVER (PARTITION BY o.order_id),
          2)                                      AS shipping_amount
FROM src.order_items i
JOIN src.orders      o ON o.order_id    = i.order_id
JOIN dim_date        d ON d.full_date   = o.order_date
JOIN dim_product     p ON p.product_id  = i.product_id
JOIN dim_store       s ON s.store_id    = o.store_id
LEFT JOIN dim_customer c
       ON c.customer_id = o.customer_id
      AND o.order_date >= c.valid_from
      AND o.order_date <  c.valid_to
WHERE o.status <> 'cancelled';

SELECT count(*) AS rows, sum(net_amount) AS revenue FROM fact_sales;
```

**Проверка:** снова 3431 строка и 25 999 963. Если строк стало больше — интервалы версий пересекаются. Если появились лишние `-1` — есть дыры между версиями.

### Задание 1

Сколько строк в новом `dim_customer`? У скольких клиентов больше одной версии?

**Проверка:** 331 строка (300 + 30 изменений + гость). У 25 клиентов больше одной версии.

<details>
<summary>Решение</summary>

```sql
SELECT count(*) AS rows FROM dim_customer;

SELECT count(*) AS customers_with_history
FROM (
    SELECT customer_id FROM dim_customer
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
    HAVING count(*) > 1
);
```

</details>

### Задание 2

Проверьте качество Type 2: у каждого клиента ровно одна текущая версия, и интервалы не пересекаются.

**Проверка:** оба запроса возвращают 0 строк.

<details>
<summary>Решение</summary>

```sql
-- ровно одна текущая версия
SELECT customer_id, count(*) FILTER (WHERE is_current) AS current_versions
FROM dim_customer
GROUP BY customer_id
HAVING count(*) FILTER (WHERE is_current) <> 1;

-- конец версии = начало следующей (нет дыр и пересечений)
SELECT *
FROM (
    SELECT customer_id, valid_to,
           lead(valid_from) OVER (PARTITION BY customer_id ORDER BY valid_from) AS next_from
    FROM dim_customer
)
WHERE next_from IS NOT NULL AND next_from <> valid_to;
```

</details>

### Задание 3. Как было и как сейчас

Посчитайте выручку по **городу клиента** двумя способами:

1. **Как было** (Type 2): город на момент покупки. Используйте `fact_sales` + `dim_customer`.
2. **Как сейчас** (Type 1): текущий город. Соедините версию клиента с `dim_customer_type1` по `customer_id`.

Гостей не учитывайте. В каком городе разница больше всего?

**Проверка:** 5 строк. Москва: как было — 10 180 196, как сейчас — 9 987 949.

<details>
<summary>Решение</summary>

```sql
WITH as_was AS (
    SELECT c.city, sum(f.net_amount) AS revenue
    FROM fact_sales f
    JOIN dim_customer c ON c.customer_key = f.customer_key
    WHERE f.customer_key <> -1
    GROUP BY ALL
),
as_is AS (
    SELECT t1.city, sum(f.net_amount) AS revenue
    FROM fact_sales f
    JOIN dim_customer       c  ON c.customer_key = f.customer_key
    JOIN dim_customer_type1 t1 ON t1.customer_id = c.customer_id
    GROUP BY ALL
)
SELECT w.city, w.revenue AS as_was, i.revenue AS as_is, i.revenue - w.revenue AS diff
FROM as_was w
JOIN as_is i USING (city)
ORDER BY diff DESC;
```

Обратите внимание: «как сейчас» тоже можно получить из Type 2. Нужно только знать текущую версию каждого клиента. Это и делает Type 6.

Полный результат:

| city | as_was | as_is | diff |
|---|---|---|---|
| Новосибирск | 941 016 | 1 117 136 | 176 120 |
| Казань | 4 457 492 | 4 574 761 | 117 269 |
| Екатеринбург | 2 191 258 | 2 260 092 | 68 834 |
| Санкт-Петербург | 6 136 361 | 5 966 385 | −169 976 |
| Москва | 10 180 196 | 9 987 949 | −192 247 |

Москва «теряет» 192 тысячи в версии «как сейчас», а Новосибирск «получает» 176 тысяч. Клиенты уехали и забрали с собой историю покупок. Это неправда: покупки были сделаны в Москве. Для такого отчёта нужен Type 2.

</details>

### Задание 4. Type 6

Добавьте в `dim_customer` колонку `current_city` — текущий город клиента в **каждой** его версии. Это Type 6. Потом посчитайте выручку по `current_city` без `dim_customer_type1`.

**Проверка:** числа совпадают с колонкой `as_is` из задания 3.

<details>
<summary>Решение</summary>

```sql
CREATE OR REPLACE TABLE dim_customer AS
SELECT *,
       last_value(city) OVER (
           PARTITION BY customer_id ORDER BY valid_from
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS current_city
FROM dim_customer
ORDER BY customer_key;

SELECT c.current_city, sum(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
WHERE f.customer_key <> -1
GROUP BY ALL
ORDER BY revenue DESC;
```

У гостя одна строка с `customer_id = NULL`. Для него `current_city` = «Неизвестно».

Запрос `SELECT * ... FROM dim_customer` нельзя запускать дважды: колонка `current_city` появится второй раз. В реальном проекте измерение пересобирают целиком из источника, как мы делали выше.

</details>

### Задание 5. Type 3

Для текущих версий клиентов покажите `city` и `previous_city` (город из предыдущей версии). Сколько текущих клиентов переехали за полгода?

**Проверка:** 22 клиента. У остальных 3 из 25 последнее изменение — переход в VIP. Город в последней версии не менялся, поэтому `previous_city = city`.

<details>
<summary>Решение</summary>

```sql
WITH t3 AS (
    SELECT customer_id, city, is_current,
           lag(city) OVER (PARTITION BY customer_id ORDER BY valid_from) AS previous_city
    FROM dim_customer
)
SELECT count(*) AS moved
FROM t3
WHERE is_current AND previous_city IS NOT NULL AND previous_city <> city;
```

Это упрощение: если клиент 74 переехал дважды, Type 3 помнит только последний переезд.

</details>

## Итог

- Type 1 перезаписывает. Type 2 добавляет версии. Type 3 добавляет колонку. Type 6 — Type 2 плюс текущее значение.
- Тип выбирают для каждого атрибута отдельно.
- В Type 2 key lookup ищет версию по дате события. Факт запоминает контекст навсегда.
- Проверяйте Type 2: одна текущая версия, нет дыр и пересечений.

<details>
<summary>SCD в dbt</summary>

В dbt Type 2 строят через **snapshots**. dbt сам добавляет колонки `dbt_valid_from`, `dbt_valid_to` и сравнивает новое состояние источника с прошлым.

```yaml
snapshots:
  - name: customers_snapshot
    relation: source('shop', 'customers')
    config:
      unique_key: customer_id
      strategy: check
      check_cols: [city, segment]
```

Важно: snapshot видит только то состояние, которое было **в момент запуска**. Если клиент изменился дважды между запусками, промежуточная версия потеряется. Журнал изменений (CDC) надёжнее.

</details>

**Глубже:** [глава 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/) — все типы SCD от 0 до 7 с примерами. [Глава 2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) — короткий справочник по SCD. [Глава 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/) — измерение клиента в CRM.

Дальше: [Conformed dimensions и bus matrix](/practice/modeling/conformed/).
