---
title: "The Data Warehouse Toolkit, глава 8: CRM"
head:
  - tag: title
    content: "Customer dimension, SCD и bridge: Kimball CRM | Инжиниринг Данных"
description: "Конспект главы 8 The Data Warehouse Toolkit: customer dimension, SCD type 2, mini-dimension, behavior tags, bridge table и cohort. Практика в DuckDB."
sidebar:
  order: 8
  label: "8. CRM"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в CRM главная таблица — широкая customer dimension. Она хранит историю изменений, описывает клиента сотнями атрибутов и связана с facts разных процессов. Быстро меняющиеся атрибуты выносят в mini-dimension. Много значений на клиента хранят в bridge table.

![Star schema CRM: заказы, customer dimension с историей, mini-dimension, bridge с тегами поведения](/assets/data-warehouse-toolkit/ch08-crm-star.png)

## Операционный и аналитический CRM

| Тип | Задача |
|---|---|
| Operational CRM | Обслужить клиента: заказ, звонок, письмо |
| Analytic CRM | Понять клиента: сегменты, отток, ценность |

- Аналитический CRM нужен единый взгляд на клиента. Данные приходят из многих систем.
- Для этого нужны очистка, дедупликация и правила `survivorship`: какой источник главнее для каждого поля.
- Одному реальному клиенту соответствует один `durable key`. Он не меняется при слиянии и новых версиях.

## Customer dimension

- Это самая большая и важная dimension. Часто 100 и более атрибутов.
- Имя и адрес разбирайте на части: имя, фамилия, улица, город, индекс. Тогда работает дедупликация и поиск.
- Для международных клиентов нужны страна, формат адреса и язык.
- Для компаний (B2B) добавляют иерархию: головная компания, филиал.
- Даты (первая покупка, регистрация) — внешние ключи на dimension `date`. Для «не было» используйте строку Unknown.
- Низкокардинальные наборы флагов можно вынести в `outrigger`. Не делайте это без причины.

### Измеренные показатели как атрибуты

- Часто нужен «сколько клиент потратил за всё время». Это fact.
- Для фильтров и групп храните его в виде банда: «до 1 000», «1 000-10 000», «выше».
- Значение берут из fact, считают при загрузке и кладут в dimension. Это `aggregated facts as dimension attributes`.
- Банд удобен для `GROUP BY`. Точное число храните отдельно, если оно нужно.

## История изменений

| Приём | Когда |
|---|---|
| SCD type 1 | Исправление ошибок. История не нужна |
| SCD type 2 | Нужна история. Новая строка и новый surrogate key |
| Mini-dimension (type 4) | Атрибуты меняются часто: доход, возраст, частота покупок |
| Type 5/6 | Нужен и «тогда», и «сейчас» вместе |

- В SCD2 держите `effective_date`, `expiration_date` и `is_current`. Точные даты нужны, чтобы привязать fact к нужной версии.
- Версия строки привязывается к fact при загрузке: по дате события.
- Аналитики часто хотят «текущую» картину. Тогда в dimension хранят и исторический, и текущий атрибут (type 6).
- Mini-dimension — это набор диапазонов (банды). Одна строка = одна комбинация. Fact хранит `demo_key` на момент события. Так история профиля не раздувает customer dimension.
- Для счёта «сколько клиентов» используйте `durable key`, а не surrogate key. Иначе клиент считается дважды.

## Много значений на клиента

- У клиента может быть много интересов, тегов, продуктов. Это many-to-many.
- Решение: `bridge table` между клиентом и dimension значений.
- Для сумм добавьте `weighting_factor`. Сумма весов по клиенту равна 1. Тогда выручка не задваивается.
- Для редких атрибутов (много колонок, мало заполнено) хранят пары «имя - значение» в bridge или в одной строке текста с тегами.
- Для сложного поведения (десятки тегов) книга советует короткий текст с тегами, например `|promo|online|`. Он быстрый, но поиск по нему менее удобен.

## Сложное поведение

| Приём | Идея |
|---|---|
| Behavior study group (cohort) | Отберите клиентов по критерию, сохраните их список, потом изучайте отдельно |
| Step dimension | Шаг в последовательности (визит 1, 2, 3). Отвечает на вопрос «на каком шаге ушёл» |
| Abnormal scenario tag | Отметка в fact («возврат», «ошибка»). Лучше в маленькой dimension, чем флаг |
| Drill across | Не соединяйте две fact table. Считайте каждую отдельно и объединяйте результаты по общей dimension |

- Не делайте `JOIN` fact-to-fact. Размножатся строки. Считайте каждый fact до уровня общих dimensions.
- Cohort (группа исследования) — таблица `customer_id` + метка. Её используют как фильтр.

## Ключевые термины

| Термин | Значение |
|---|---|
| Durable key | Постоянный ключ клиента для всех версий |
| SCD type 2 | Новая строка для каждой версии атрибутов |
| Mini-dimension | Отдельная dimension для быстро меняющихся банд |
| Bridge table | Связь many-to-many между dimension и значениями |
| Weighting factor | Доля, чтобы суммы не задваивались |
| Survivorship | Правило выбора значения при слиянии источников |

## Что это значит на практике

- В `dbt` SCD2 делают через `snapshot`. Он сохраняет `dbt_valid_from` и `dbt_valid_to`.
- Не кладите возраст и доход в customer dimension. Используйте банды в mini-dimension.
- При подсчёте клиентов используйте `count(DISTINCT customer_id)`, не `customer_key`.
- Всегда проверяйте веса bridge: `sum(weight) = 1` для каждого клиента.
- Для клиента без тегов добавляйте строку «Без тега». Иначе он пропадёт из отчёта.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём customer dimension, mini-dimension и bridge

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d AS full_date
FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

-- SCD type 2: у клиентов 101 и 102 есть история
CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1, 101, 'Анна',   'Москва', 'Standard', DATE '2024-01-01', DATE '2024-06-30', FALSE),
    (2, 101, 'Анна',   'Казань', 'Standard', DATE '2024-07-01', DATE '9999-12-31', TRUE),
    (3, 102, 'Борис',  'Москва', 'Standard', DATE '2024-01-01', DATE '2024-03-31', FALSE),
    (4, 102, 'Борис',  'Москва', 'Premium',  DATE '2024-04-01', DATE '9999-12-31', TRUE),
    (5, 103, 'Вера',   'Казань', 'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (6, 104, 'Глеб',   'Тверь',  'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (7, 105, 'Дина',   'Москва', 'Premium',  DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (8, 106, 'Егор',   'Тверь',  'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE)
) t(customer_key, customer_id, customer_name, city, segment, effective_date, expiration_date, is_current);

-- mini-dimension: банды вместо точных значений
CREATE TABLE dim_demographics AS
SELECT * FROM (VALUES
    (1, 'до 50 тыс',     '18-30', 'редко'),
    (2, '50-100 тыс',    '31-45', 'регулярно'),
    (3, 'выше 100 тыс',  '46+',   'часто')
) t(demo_key, income_band, age_band, purchase_frequency_band);

CREATE TABLE dim_tag AS
SELECT * FROM (VALUES
    (0, 'Без тега'),
    (1, 'Любит акции'),
    (2, 'Покупает онлайн'),
    (3, 'Семья')
) t(tag_key, tag_name);

-- bridge: сумма weighting_factor по клиенту равна 1
CREATE TABLE bridge_customer_tag AS
SELECT * FROM (VALUES
    (101, 1, 0.5), (101, 2, 0.5),
    (102, 2, 1.0),
    (103, 1, 1.0/3), (103, 2, 1.0/3), (103, 3, 1.0/3),
    (104, 3, 1.0),
    (105, 1, 1.0),
    (106, 0, 1.0)
) t(customer_id, tag_key, weighting_factor);

-- grain: один заказ. Версия клиента выбирается по дате заказа
CREATE TABLE fact_orders AS
WITH o AS (
    SELECT i,
           101 + i % 6 AS customer_id,
           DATE '2024-01-01' + ((i * 7) % 360)::INT AS order_date,
           50 + (i * 13) % 200 AS order_amount
    FROM range(0, 120) t(i)
)
SELECT 'O-' || lpad(o.i::VARCHAR, 4, '0') AS order_number,
       c.customer_key,
       1 + ((o.customer_id - 101) + (o.order_date >= DATE '2024-04-01')::INT) % 3 AS demo_key,
       strftime(o.order_date, '%Y%m%d')::INT AS date_key,
       o.order_amount
FROM o
JOIN dim_customer c
  ON c.customer_id = o.customer_id
 AND o.order_date BETWEEN c.effective_date AND c.expiration_date;
```

### Шаг 2. Проверяем SCD2 и bridge

```sql
-- должно вернуть 120: каждый заказ нашёл ровно одну версию клиента
SELECT count(*) AS orders, count(DISTINCT order_number) AS distinct_orders FROM fact_orders;

-- веса bridge: у каждого клиента сумма равна 1
SELECT customer_id, round(sum(weighting_factor), 6) AS total_weight
FROM bridge_customer_tag GROUP BY customer_id ORDER BY customer_id;
```

### Задания

**1.** Выручка по городам «как было» и «как сейчас». Исторический город берут из версии, привязанной к заказу. Текущий — из строки с `is_current`.

<details>
<summary>Решение</summary>

```sql
SELECT c.city AS city_at_order, cur.city AS city_now, sum(f.order_amount) AS revenue
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
JOIN dim_customer cur ON cur.customer_id = c.customer_id AND cur.is_current
WHERE c.customer_id = 101
GROUP BY ALL
ORDER BY city_at_order;
```

У клиента 101 заказы разделились на два города. Если взять только текущий город, вся выручка уйдёт в Казань.
</details>

**2.** Сколько клиентов? Сравните `count(DISTINCT customer_key)` и `count(DISTINCT customer_id)`.

<details>
<summary>Решение</summary>

```sql
SELECT count(DISTINCT f.customer_key) AS by_surrogate_key,
       count(DISTINCT c.customer_id)  AS by_durable_key
FROM fact_orders f
JOIN dim_customer c USING (customer_key);
```

Surrogate key даёт 8. Это версии. Реальных клиентов 6.
</details>

**3.** Mini-dimension. Покажите средний заказ по `income_band`. Затем покажите, как клиент 101 переходит между бандами после апреля.

<details>
<summary>Решение</summary>

```sql
SELECT d.income_band, count(*) AS orders, round(avg(f.order_amount), 1) AS avg_order
FROM fact_orders f
JOIN dim_demographics d USING (demo_key)
GROUP BY d.income_band
ORDER BY d.income_band;

SELECT (f.date_key >= 20240401) AS after_april, d.income_band, count(*) AS orders
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
JOIN dim_demographics d USING (demo_key)
WHERE c.customer_id = 101
GROUP BY ALL
ORDER BY after_april;
```
</details>

**4.** Bridge. Посчитайте выручку по тегам с `weighting_factor`. Проверьте, что сумма равна общей выручке.

<details>
<summary>Решение</summary>

```sql
WITH rev AS (
    SELECT c.customer_id, sum(f.order_amount) AS revenue
    FROM fact_orders f
    JOIN dim_customer c USING (customer_key)
    GROUP BY c.customer_id
)
SELECT t.tag_name,
       round(sum(r.revenue * b.weighting_factor), 2) AS weighted_revenue,
       sum(r.revenue)                                AS unweighted_revenue
FROM rev r
JOIN bridge_customer_tag b USING (customer_id)
JOIN dim_tag t USING (tag_key)
GROUP BY t.tag_name
ORDER BY weighted_revenue DESC;
```

Сумма `weighted_revenue` равна общей выручке. Сумма `unweighted_revenue` больше: клиенты с несколькими тегами посчитаны много раз.
</details>

**5.** Банд расходов как атрибут. Посчитайте общие расходы клиента и присвойте банд («до 2 000», «2 000-3 000», «выше»). Затем посчитайте клиентов в каждом банде.

<details>
<summary>Решение</summary>

```sql
WITH spend AS (
    SELECT c.customer_id, sum(f.order_amount) AS lifetime_spend
    FROM fact_orders f
    JOIN dim_customer c USING (customer_key)
    GROUP BY c.customer_id
)
SELECT CASE WHEN lifetime_spend < 2000 THEN '1. до 2 000'
            WHEN lifetime_spend < 3000 THEN '2. 2 000-3 000'
            ELSE '3. выше 3 000' END AS spend_band,
       count(*) AS customers
FROM spend
GROUP BY ALL
ORDER BY spend_band;
```

Подберите границы по своим данным. Идея в том, что банд считается при загрузке и хранится как атрибут.
</details>

## Вопросы для самопроверки

1. Когда достаточно SCD type 1, а когда нужен type 2?
2. Зачем нужна mini-dimension? Что хранит fact?
3. Для чего `weighting_factor` в bridge table?
4. Почему нельзя соединять две fact table напрямую?
