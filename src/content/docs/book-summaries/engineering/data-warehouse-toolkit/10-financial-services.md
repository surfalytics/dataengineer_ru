---
title: "The Data Warehouse Toolkit, глава 10: Финансовые услуги"
head:
  - tag: title
    content: "Банк: household, bridge, supertype в DWH | Инжиниринг Данных"
description: "Конспект главы 10 The Data Warehouse Toolkit: снимок счетов, household, bridge с весами, mini-dimension, dynamic banding, supertype. Практика в DuckDB."
sidebar:
  order: 10
  label: "10. Финансовые услуги"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в банке главный процесс — счёт. Счёт принадлежит нескольким клиентам, клиенты живут в household, а продукты разные. Книга решает это так: monthly snapshot счетов, больше dimensions (dimension triage), bridge с весами и разделение на supertype и subtype.

![Модель банка: снимок счетов, mini-dimension профиля, bridge счёт-клиент и household](/assets/data-warehouse-toolkit/ch10-bank-star.png)

## Снимок счетов

- Grain: один счёт x один месяц. Это periodic snapshot.
- Facts: остаток на конец месяца, приход, расход, начисленные проценты, число операций.
- Остаток — `semi-additive`. Его суммируют по счетам, но не по месяцам. По времени берут среднее или последнее значение.
- Операции (transactions) можно хранить отдельным transaction fact. Снимок остаётся главным для остатков и быстрых отчётов.
- Снимок плотный: строка есть, даже если операций не было.

## Dimension triage: не слишком мало dimensions

- Если dimension всего две (месяц и счёт), а всё остальное спрятано в `dim_account`, это ловушка.
- Книга выносит отдельные dimensions: филиал, продукт, главный клиент, статус счёта, household.
- Так пользователю проще: это естественные срезы бизнеса. И `dim_account` (миллионы строк) меньше растёт от SCD2.
- Обычно в модели 5–20 dimensions. Если меньше, проверьте: causal, несколько дат, degenerate, role-playing, status, audit, junk.
- Правило: атрибут, у которого одно значение на строку fact, можно сделать dimension.

## Mini-dimension

Атрибуты, которые меняются каждый месяц (банд остатка, статус активности), не кладут в `dim_account`. Иначе SCD2 даст тысячи версий.

- Mini-dimension хранит все комбинации диапазонов. Это маленькая таблица.
- Fact хранит `profile_key` на конец месяца.
- История профиля видна в fact. Переходы между бандами считаются по соседним месяцам.
- В одной fact может быть несколько mini-dimensions: демография, кредитный риск. Группируйте связанные атрибуты. Не делайте mini-dimension на каждый атрибут.
- Если аналитикам нужно точное значение (score 1–1200), храните его ещё и как fact. Банд — для отчётов, число — для data mining.
- Если клиент связан с fact через bridge, ключ mini-dimension кладут в bridge: `account_key`, `customer_key`, `demographics_key`.

## Dynamic value banding

- Бизнес хочет менять диапазоны (банды) без перезагрузки истории.
- Решение: таблица диапазонов `band_ranges` (`band_name`, `from_amount`, `to_amount`). В книге в ней может быть несколько наборов банд (`band_group`).
- Запрос делает `JOIN` по условию `>= from AND < to`. Банд считается на лету, fact не меняется.
- Минус: запрос читает все строки за период. Помогает колоночная БД. Для постоянных банд лучше mini-dimension.

## Household и many-to-many

| Задача | Решение |
|---|---|
| Счёт принадлежит нескольким клиентам | `bridge_account_customer` |
| Счета одной семьи | Отдельная `dim_household`, `household_key` в fact |
| Доля в сумме не должна задваиваться | `weighting_factor`, сумма на счёт = 1 |

- Household — группа счетов и клиентов с общими финансами (семья, группа компаний). Его определяет отдельный алгоритм.
- Книга кладёт `household_key` в fact, а не в `dim_account`. Связь счёта с household меняется, а SCD2 на 10 млн счетов дорог.
- Отчёт с весами — correctly weighted report. Итог сходится.
- Отчёт без весов — impact report. Совместный счёт попадает к обоим владельцам. Это допустимо, если пользователи понимают задвоение.
- Удобно сделать два view: fact + bridge с весами и без весов.
- Связь счёт-клиент меняется со временем: добавьте в bridge даты действия.

## Supertype и subtype

Разные продукты (чековый счёт, сберегательный, ипотека) имеют общие и особые facts.

| Часть | Что хранит |
|---|---|
| Supertype fact | Общие метрики для всех счетов: остаток, приход, расход |
| Subtype fact | Метрики одного продукта: овердрафт и банкоматы для чекового |

- Общий отчёт идёт по supertype. Сравнение всех продуктов легко.
- Глубокий анализ чековых счетов идёт по subtype. Там нет пустых колонок.
- Subtype fact повторяет общие facts supertype. Тогда аналитику не нужен `JOIN` между ними.
- Dimensions тоже делят. Subtype `dim_checking_account` — shrunken conformed dimension: те же surrogate keys, меньше строк, свои атрибуты.
- Нельзя класть все колонки в одну широкую таблицу: будет много `NULL`.
- Если facts у всех продуктов одинаковые, хватит одной supertype fact. Разные только subtype dimensions.

## Hot swappable dimensions

- Одна fact, несколько версий одной dimension. Пример: брокер даёт клиентам общую таблицу цен акций. У каждого клиента своя `dim_stock` со своими атрибутами.
- Нужную dimension подставляют в запрос. Foreign key constraints для этого обычно отключают.

## Ключевые термины

| Термин | Значение |
|---|---|
| Periodic snapshot | Остатки на конец периода |
| Semi-additive fact | Суммируется не по всем dimensions (не по времени) |
| Mini-dimension | Таблица быстро меняющихся банд |
| Bridge table | Связь many-to-many |
| Weighting factor | Доля, защищающая от двойного счёта |
| Household | Группа клиентов с общими финансами |
| Supertype / subtype | Общая таблица и таблицы особенностей продукта |

## Что это значит на практике

- Остаток никогда не суммируйте по месяцам. Используйте `avg` или значение на последнюю дату.
- Проверяйте веса: `sum(weighting_factor) = 1` для каждого счёта. Это тест `dbt`.
- Банды профиля стройте в mini-dimension при загрузке. Не создавайте новую версию счёта на каждое изменение.
- Для общего отчёта и особых метрик держите два уровня fact table.
- Определение household — бизнес-правило. Зафиксируйте его в документации и в тестах.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём счета, клиентов, bridge и снимки

```sql
CREATE TABLE dim_date AS
SELECT strftime(last_day(d), '%Y%m')::INT AS month_key, last_day(d) AS month_end
FROM generate_series(DATE '2024-01-01', DATE '2024-06-01', INTERVAL 1 MONTH) t(d);

CREATE TABLE dim_household AS
SELECT * FROM (VALUES (1,'Ивановы'),(2,'Петровы'),(3,'Сидоров'),(4,'Кузнецова')) t(household_key, household_name);

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1,'Иван Иванов'),(2,'Мария Иванова'),
    (3,'Пётр Петров'),(4,'Ольга Петрова'),
    (5,'Сергей Сидоров'),(6,'Анна Кузнецова')
) t(customer_key, customer_name);

CREATE TABLE dim_account AS
SELECT * FROM (VALUES
    (1,'40817-001','checking','Центр'),
    (2,'40817-002','savings', 'Центр'),
    (3,'40817-003','checking','Север'),
    (4,'40817-004','savings', 'Север'),
    (5,'40817-005','checking','Север'),
    (6,'40817-006','checking','Центр'),
    (7,'40817-007','savings', 'Центр'),
    (8,'40817-008','checking','Юг')
) t(account_key, account_number, product_type, branch);

-- результат householding-алгоритма: какой household у счёта (staging для ETL)
CREATE TABLE stg_account_household AS
SELECT * FROM (VALUES (1,1),(2,1),(3,2),(4,2),(5,2),(6,3),(7,4),(8,2)) t(account_key, household_key);

-- bridge: сумма весов на счёт равна 1
CREATE TABLE bridge_account_customer AS
SELECT * FROM (VALUES
    (1,1,0.5),(1,2,0.5),
    (2,1,1.0),
    (3,3,1.0),
    (4,3,0.5),(4,4,0.5),
    (5,4,1.0),
    (6,5,1.0),
    (7,6,1.0),
    (8,3,0.5),(8,4,0.5)
) t(account_key, customer_key, weighting_factor);

-- mini-dimension: комбинации банд остатка и активности
CREATE TABLE dim_account_profile AS
SELECT row_number() OVER () AS profile_key, b.balance_band, s.activity_status
FROM (VALUES ('1. до 3 000'),('2. 3 000-8 000'),('3. выше 8 000')) b(balance_band)
CROSS JOIN (VALUES ('active'),('dormant')) s(activity_status);

-- supertype: один счёт x месяц. Общие facts для всех продуктов.
-- household_key лежит в fact: связь счёт-household меняется со временем
CREATE TABLE fact_account_snapshot AS
WITH base AS (
    SELECT a.account_key, h.household_key, d.month_key,
           (a.account_key * 7919 + (d.month_key % 100) * 104729) % 1301 + 200 AS deposit_amount,
           (a.account_key * 6007 + (d.month_key % 100) * 86969) % 1499      AS withdrawal_amount,
           (a.account_key * (d.month_key % 100)) % 5                  AS txn_count,
           1500 * a.account_key                                       AS opening_balance
    FROM dim_account a
    JOIN stg_account_household h USING (account_key)
    CROSS JOIN dim_date d
),
bal AS (
    SELECT *, opening_balance
              + sum(deposit_amount - withdrawal_amount) OVER (PARTITION BY account_key ORDER BY month_key) AS ending_balance
    FROM base
)
SELECT b.month_key, b.account_key, b.household_key, p.profile_key,
       b.ending_balance, b.deposit_amount, b.withdrawal_amount, b.txn_count
FROM bal b
JOIN dim_account_profile p
  ON p.balance_band = CASE WHEN b.ending_balance < 3000 THEN '1. до 3 000'
                           WHEN b.ending_balance < 8000 THEN '2. 3 000-8 000'
                           ELSE '3. выше 8 000' END
 AND p.activity_status = CASE WHEN b.txn_count = 0 THEN 'dormant' ELSE 'active' END;

-- subtype: только чековые счета. Повторяет общие facts и добавляет свои
CREATE TABLE fact_checking_snapshot AS
SELECT s.month_key, s.account_key,
       s.ending_balance, s.deposit_amount, s.withdrawal_amount, s.txn_count,
       CASE WHEN s.ending_balance < 6000 THEN 25 ELSE 0 END AS overdraft_fee,
       s.txn_count * 3 AS atm_withdrawal_count
FROM fact_account_snapshot s
JOIN dim_account a USING (account_key)
WHERE a.product_type = 'checking';

CREATE TABLE band_ranges AS
SELECT * FROM (VALUES
    ('низкий',  0,     3000),
    ('средний', 3000,  8000),
    ('высокий', 8000,  1000000)
) t(band_name, from_amount, to_amount);
```

### Шаг 2. Проверяем

```sql
-- должно вернуть 0 строк: сумма весов каждого счёта равна 1
SELECT account_key, sum(weighting_factor) AS total_weight
FROM bridge_account_customer
GROUP BY account_key
HAVING abs(sum(weighting_factor) - 1) > 1e-9;

SELECT count(*) AS snapshot_rows, count(DISTINCT account_key) AS accounts FROM fact_account_snapshot;
```

### Задания

**1.** Household и bridge. Покажите остаток по household на июнь: `household_key` есть прямо в fact. Затем покажите остаток по клиентам через bridge: с весами и без весов. Сравните итоги с общим остатком.

<details>
<summary>Решение</summary>

```sql
SELECT h.household_name, sum(s.ending_balance) AS household_balance
FROM fact_account_snapshot s
JOIN dim_household h USING (household_key)
WHERE s.month_key = 202406
GROUP BY h.household_name
ORDER BY household_balance DESC;

SELECT c.customer_name,
       sum(s.ending_balance * b.weighting_factor) AS weighted_balance,
       sum(s.ending_balance)                      AS impact_balance
FROM fact_account_snapshot s
JOIN bridge_account_customer b USING (account_key)
JOIN dim_customer c USING (customer_key)
WHERE s.month_key = 202406
GROUP BY c.customer_name
ORDER BY weighted_balance DESC;

SELECT sum(ending_balance) AS total_balance FROM fact_account_snapshot WHERE month_key = 202406;
```

- Сумма по household и сумма `weighted_balance` равны общему остатку.
- Сумма `impact_balance` больше: совместные счета посчитаны у обоих владельцев. Книга называет это impact report. Он полезен («какие деньги затрагивает клиент»), но не для итогов.
</details>

**2.** Semi-additive. Покажите общий остаток банка по месяцам. Потом покажите, что будет, если просуммировать остаток по всем месяцам. Найдите правильное «среднее значение за период».

<details>
<summary>Решение</summary>

```sql
WITH m AS (
    SELECT month_key, sum(ending_balance) AS total_balance
    FROM fact_account_snapshot
    GROUP BY month_key
)
SELECT month_key, total_balance FROM m ORDER BY month_key;

SELECT sum(ending_balance) AS wrong_sum_over_time,
       sum(ending_balance) / count(DISTINCT month_key) AS avg_total_balance
FROM fact_account_snapshot;
```

Сумма по времени бессмысленна: она примерно в 6 раз больше реального остатка. Средний остаток за период считается как сумма, делённая на число месяцев.
</details>

**3.** Mini-dimension. Покажите число счетов в каждом банде остатка в январе и в июне. Затем найдите счета, у которых банд изменился между январём и июнем.

<details>
<summary>Решение</summary>

```sql
SELECT s.month_key, p.balance_band, count(*) AS accounts
FROM fact_account_snapshot s
JOIN dim_account_profile p USING (profile_key)
WHERE s.month_key IN (202401, 202406)
GROUP BY ALL
ORDER BY s.month_key, p.balance_band;

SELECT jan.account_key, pj.balance_band AS band_jan, pn.balance_band AS band_jun
FROM fact_account_snapshot jan
JOIN fact_account_snapshot jun
  ON jun.account_key = jan.account_key AND jun.month_key = 202406
JOIN dim_account_profile pj ON pj.profile_key = jan.profile_key
JOIN dim_account_profile pn ON pn.profile_key = jun.profile_key
WHERE jan.month_key = 202401 AND pj.balance_band <> pn.balance_band
ORDER BY jan.account_key;
```
</details>

**4.** Dynamic banding. Посчитайте число счетов и средний остаток по бандам из `band_ranges` на июнь. Затем измените границы в таблице и повторите запрос.

<details>
<summary>Решение</summary>

```sql
SELECT r.band_name, count(*) AS accounts, round(avg(s.ending_balance), 1) AS avg_balance
FROM fact_account_snapshot s
JOIN band_ranges r
  ON s.ending_balance >= r.from_amount AND s.ending_balance < r.to_amount
WHERE s.month_key = 202406
GROUP BY r.band_name
ORDER BY min(r.from_amount);
```

Fact не менялся. Банды можно менять без перезагрузки.
</details>

**5.** Supertype и subtype. Для чековых счетов покажите по месяцам остаток и комиссию за овердрафт. Используйте только subtype fact, без `JOIN`. Затем проверьте, что остаток чековых счетов на июнь в supertype и subtype совпадает.

<details>
<summary>Решение</summary>

```sql
SELECT month_key,
       count(*)                  AS checking_accounts,
       sum(ending_balance)       AS checking_balance,
       sum(overdraft_fee)        AS overdraft_fees,
       sum(atm_withdrawal_count) AS atm_withdrawals
FROM fact_checking_snapshot
GROUP BY month_key
ORDER BY month_key;

SELECT (SELECT sum(s.ending_balance) FROM fact_account_snapshot s
        JOIN dim_account a USING (account_key) WHERE a.product_type = 'checking' AND s.month_key = 202406) AS supertype_checking_jun,
       (SELECT sum(ending_balance) FROM fact_checking_snapshot WHERE month_key = 202406) AS subtype_checking_jun;
```

Subtype содержит только чековые счета (5 из 8). Он повторяет общие facts. Поэтому аналитик чековых счетов работает с одной таблицей и не соединяет её с supertype.
</details>

## Вопросы для самопроверки

1. Почему остаток на счёте — semi-additive fact?
2. Зачем нужен `weighting_factor` в bridge между счётом и клиентом?
3. Когда выбрать mini-dimension, а когда dynamic banding?
4. Что выигрываем от разделения на supertype и subtype?
