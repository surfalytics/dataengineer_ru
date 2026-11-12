---
title: Итоговая практика
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Итоговая практика по dimensional modeling | Инжиниринг Данных"
description: Итоговая практика курса по dimensional modeling. Проектируем и строим fact table возвратов в DuckDB, обновляем bus matrix и отвечаем на вопросы бизнеса.
sidebar:
  order: 12
  label: Итоговая практика
tags:
  - data-modelling
  - practice
  - duckdb
---
Руководитель магазина просит добавить в хранилище **возвраты**. Вопросы бизнеса:

- Какой процент товаров возвращают в каждой категории?
- Почему возвращают обувь?
- Сколько выручки мы теряем на возвратах каждый месяц?

Источник — `src.returns`. Вы пройдёте весь путь: от четырёх шагов до отчёта.

Подготовка: база `modeling.duckdb` открыта, звезда из прошлых уроков построена. Решайте сами, без AI. Открывайте решение, когда ответ готов.

```sql
SELECT * FROM src.returns LIMIT 5;
```

## Шаг 1. Четыре шага

Пройдите [четыре шага Кимбалла](/practice/modeling/four-steps/) для процесса «возврат товара». Запишите grain одним предложением. Какие измерения можно взять готовыми? Какое измерение нужно новое?

<details>
<summary>Ответ</summary>

1. **Процесс:** клиент возвращает товар.
2. **Grain:** одна строка — один возврат одной позиции заказа (`return_id`).
3. **Dimensions:**
   - дата возврата → `dim_date` (conformed);
   - клиент, товар, магазин → `dim_customer`, `dim_product`, `dim_store` (conformed). Берём **те же ключи, что в продаже**. Клиент — версия на момент покупки;
   - причина возврата → **новое** измерение `dim_return_reason`;
   - `order_id`, `line_number` → degenerate dimension. По ним возврат связан с продажей.
4. **Facts:** `returned_quantity`, `refund_amount` (additive), `days_since_sale` (длительность, складывать нельзя, только `avg`).

</details>

## Шаг 2. Измерение причин

Создайте `dim_return_reason`. Добавьте атрибут `reason_group`: «Качество» для «Брак» и «Не совпадает с описанием», «Клиент» для остальных.

**Проверка:** 4 строки, по 2 в каждой группе.

<details>
<summary>Решение</summary>

```sql
CREATE OR REPLACE TABLE dim_return_reason AS
SELECT row_number() OVER (ORDER BY reason) AS reason_key,
       reason,
       CASE WHEN reason IN ('Брак', 'Не совпадает с описанием') THEN 'Качество'
            ELSE 'Клиент' END AS reason_group
FROM (SELECT DISTINCT reason FROM src.returns);

SELECT * FROM dim_return_reason;
```

</details>

## Шаг 3. fact_returns

Постройте `fact_returns`. Подсказки:

- Ключи клиента, товара и магазина возьмите из `fact_sales` по `order_id` + `line_number`. Так возврат получит ту же версию клиента, что и продажа.
- `refund_amount` = вернули штук × цена за штуку после скидки (`net_amount / quantity` из продажи).
- `days_since_sale` = дата возврата − дата продажи.

Сверьте: в факте столько же строк, сколько в `src.returns`.

**Проверка:** 216 строк. Сумма возвратов — 1 407 321.

<details>
<summary>Решение</summary>

```sql
CREATE OR REPLACE TABLE fact_returns AS
SELECT
    strftime(r.return_date, '%Y%m%d')::INT        AS date_key,
    s.customer_key,
    s.product_key,
    s.store_key,
    rr.reason_key,
    r.return_id,
    r.order_id,
    r.line_number,
    r.quantity                                     AS returned_quantity,
    round(r.quantity * s.net_amount / s.quantity, 2) AS refund_amount,
    r.return_date - sd.full_date                   AS days_since_sale
FROM src.returns r
JOIN fact_sales        s  ON s.order_id = r.order_id AND s.line_number = r.line_number
JOIN dim_date          sd ON sd.date_key = s.date_key
JOIN dim_return_reason rr ON rr.reason = r.reason;

SELECT count(*) AS rows, sum(refund_amount) AS refunds FROM fact_returns;
```

Обратите внимание: здесь `JOIN` факта с фактом допустим. Мы не агрегируем, а только **берём ключи** из продажи. У каждого возврата ровно одна строка продажи, поэтому fan-out нет.

</details>

## Шаг 4. Bus matrix

Обновите bus matrix из урока [Conformed dimensions](/practice/modeling/conformed/).

<details>
<summary>Ответ</summary>

| Бизнес-процесс | Дата | Клиент | Товар | Магазин | Причина возврата |
|---|---|---|---|---|---|
| Продажи | ✓ | ✓ | ✓ | ✓ | |
| Остатки | ✓ | | ✓ | ✓ | |
| Выполнение заказа | ✓ ×3 | | | ✓ | |
| Возвраты | ✓ | ✓ | ✓ | ✓ | ✓ |

Возвраты делят с продажами четыре измерения. Значит, их можно сравнивать: drill-across по любому из них.

</details>

## Вопрос 1. Процент возвратов по категориям

Процент возврата = вернули штук / продали штук. Это drill-across: продажи и возвраты агрегируйте отдельно, потом соедините по категории.

**Проверка:** 5 строк. Первая — Обувь: 9,54%.

<details>
<summary>Решение</summary>

```sql
WITH sold AS (
    SELECT p.category_name, sum(f.quantity) AS sold
    FROM fact_sales f JOIN dim_product p USING (product_key)
    GROUP BY ALL
),
returned AS (
    SELECT p.category_name, sum(r.returned_quantity) AS returned
    FROM fact_returns r JOIN dim_product p USING (product_key)
    GROUP BY ALL
)
SELECT category_name, sold, returned,
       round(100 * returned / sold, 2) AS return_rate_pct
FROM sold JOIN returned USING (category_name)
ORDER BY return_rate_pct DESC;
```

Процент — non-additive. Мы считаем его из двух сумм. Строго говоря, возвраты июня относятся и к продажам мая. Для точного анализа считают когорты: возвраты по месяцу **продажи**. Здесь достаточно общего процента за полгода.

Полный результат:

| category_name | sold | returned | return_rate_pct |
|---|---|---|---|
| Обувь | 943 | 90 | 9,54 |
| Одежда | 952 | 66 | 6,93 |
| Электроника | 893 | 38 | 4,26 |
| Аксессуары | 1140 | 38 | 3,33 |
| Снаряжение | 1038 | 28 | 2,70 |

</details>

## Вопрос 2. Почему возвращают обувь

Для категории «Обувь» покажите группу причины, причину, число возвратов и сумму.

**Проверка:** 4 строки. Первая — «Не подошёл размер»: 35 возвратов.

<details>
<summary>Решение</summary>

```sql
SELECT rr.reason_group, rr.reason,
       count(*)             AS returns,
       sum(r.refund_amount) AS refunds
FROM fact_returns r
JOIN dim_product       p  USING (product_key)
JOIN dim_return_reason rr USING (reason_key)
WHERE p.category_name = 'Обувь'
GROUP BY ALL
ORDER BY returns DESC;
```

Полный результат:

| reason_group | reason | returns | refunds |
|---|---|---|---|
| Клиент | Не подошёл размер | 35 | 297 454 |
| Клиент | Передумал | 17 | 117 901 |
| Качество | Брак | 13 | 90 112 |
| Качество | Не совпадает с описанием | 10 | 87 101 |

Почти половина возвратов обуви — размер. Таблица размеров на сайте окупится быстрее, чем смена поставщика.

</details>

## Вопрос 3. Чистая выручка по месяцам

Для каждого месяца: выручка (`fact_sales`), возвраты (`fact_returns`) и чистая выручка = выручка − возвраты. Используйте месяц из `dim_date`. Возвраты относите к месяцу возврата.

**Проверка:** 6 строк. Июнь: возвраты 348 750, чистая выручка 4 838 340.

<details>
<summary>Решение</summary>

```sql
WITH sales AS (
    SELECT d.year_month, sum(f.net_amount) AS revenue
    FROM fact_sales f JOIN dim_date d USING (date_key)
    GROUP BY ALL
),
refunds AS (
    SELECT d.year_month, sum(r.refund_amount) AS refunds
    FROM fact_returns r JOIN dim_date d USING (date_key)
    GROUP BY ALL
)
SELECT year_month, revenue,
       coalesce(refunds, 0)            AS refunds,
       revenue - coalesce(refunds, 0)  AS net_revenue
FROM sales
LEFT JOIN refunds USING (year_month)
ORDER BY year_month;
```

Полный результат:

| year_month | revenue | refunds | net_revenue |
|---|---|---|---|
| 2025-01 | 3 655 248 | 226 821 | 3 428 427 |
| 2025-02 | 3 603 021 | 168 332 | 3 434 689 |
| 2025-03 | 4 066 776 | 235 254 | 3 831 522 |
| 2025-04 | 4 137 647 | 202 824 | 3 934 823 |
| 2025-05 | 5 350 181 | 225 340 | 5 124 841 |
| 2025-06 | 5 187 090 | 348 750 | 4 838 340 |

</details>

## Вопрос 4. Как быстро возвращают

Среднее число дней от покупки до возврата по типу магазина. Где возвращают быстрее?

**Проверка:** онлайн — 10,8 дня, офлайн — 7,3 дня. Онлайн-покупатель сначала ждёт доставку, поэтому срок от покупки дольше.

<details>
<summary>Решение</summary>

```sql
SELECT s.store_type,
       count(*)                          AS returns,
       round(avg(r.days_since_sale), 1)  AS avg_days
FROM fact_returns r
JOIN dim_store s USING (store_key)
GROUP BY ALL
ORDER BY ALL;
```

`days_since_sale` — non-additive факт. Сумма дней ничего не значит. Используем `avg`.

</details>

## Вопрос 5. Возвраты VIP

Сравните процент возврата (в штуках) у VIP и обычных клиентов. Сегмент — **на момент покупки** (Type 2). Гостей не учитывайте.

**Проверка:** Обычный — 5,44%, VIP — 4,55%. VIP-клиенты возвращают реже.

<details>
<summary>Решение</summary>

```sql
WITH sold AS (
    SELECT c.segment, sum(f.quantity) AS sold
    FROM fact_sales f JOIN dim_customer c USING (customer_key)
    WHERE f.customer_key <> -1
    GROUP BY ALL
),
returned AS (
    SELECT c.segment, sum(r.returned_quantity) AS returned
    FROM fact_returns r JOIN dim_customer c USING (customer_key)
    WHERE r.customer_key <> -1
    GROUP BY ALL
)
SELECT segment, sold, returned,
       round(100 * returned / sold, 2) AS return_rate_pct
FROM sold JOIN returned USING (segment)
ORDER BY segment;
```

Ключ клиента в `fact_returns` взят из продажи. Поэтому сегмент — тот, что был при покупке. Если бы мы искали клиента по дате **возврата**, клиент, ставший VIP между покупкой и возвратом, попал бы в другую группу.

</details>

## Что дальше

Вы прошли базовый минимум dimensional modeling:

- отличаете OLTP от OLAP и знаете, зачем нужна звезда;
- проектируете fact table за четыре шага и объявляете grain;
- строите измерения с surrogate key, календарь и unknown member;
- знаете три типа fact tables и factless;
- храните историю через SCD Type 2;
- связываете процессы через conformed dimensions и bus matrix;
- понимаете, где место звезды рядом с Data Vault, OBT и Medallion.

Куда двигаться:

- **Прочитайте Кимбалла.** [Конспект The Data Warehouse Toolkit](/book-summaries/engineering/data-warehouse-toolkit/) — 21 глава с практикой в DuckDB. Главы 6–16 разбирают модели для разных отраслей: банки, телеком, страхование, e-commerce.
- **Перенесите модель в dbt.** Каждая таблица из курса — это одна модель dbt: `SELECT` из источника или других моделей. Добавьте тесты `unique`, `not_null`, `relationships`.
- **Попробуйте на своих данных.** Возьмите любой процесс на работе. Пройдите четыре шага. Нарисуйте bus matrix.
- **Подтяните SQL**, если было трудно: [базовый минимум SQL](/practice/sql/), особенно оконные функции.

<details>
<summary>Ещё книги по моделированию</summary>

- *The Data Warehouse Toolkit* — Ralph Kimball, Margy Ross. Главная книга по теме. 🇬🇧
- *Star Schema: The Complete Reference* — Christopher Adamson. Справочник по каждой детали звезды. 🇬🇧
- *Agile Data Warehouse Design* — Lawrence Corr. Как собирать требования и моделировать вместе с бизнесом (метод BEAM). 🇬🇧
- [Dimensional Modeling 101](https://thedatatoolbox.substack.com/p/dimensional-modeling-101) — короткая статья, на которой основан этот курс. 🇬🇧
- [Kimball Group: Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) — официальный справочник техник. 🇬🇧

</details>
