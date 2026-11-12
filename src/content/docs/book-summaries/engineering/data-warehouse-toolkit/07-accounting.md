---
title: "The Data Warehouse Toolkit, глава 7: Бухгалтерия"
head:
  - tag: title
    content: "Главная книга, бюджет и star schema: Kimball | Инжиниринг Данных"
description: "Конспект главы 7 The Data Warehouse Toolkit: журнал проводок, снимки главной книги, план счетов, бюджет, ragged hierarchy и bridge table. Практика в DuckDB."
sidebar:
  order: 7
  label: "7. Бухгалтерия"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** главную книгу (general ledger, G/L) моделируют двумя fact table. Журнал проводок хранит каждое событие. Снимок на конец периода хранит остатки. Бюджет лежит в отдельной таблице с более крупным grain.

![Star schema главной книги: журнал проводок, снимок остатков и бюджет с общими dimensions](/assets/data-warehouse-toolkit/ch07-gl-star.png)

## Две модели главной книги

| Модель | Grain | Для чего |
|---|---|---|
| Journal (transaction fact) | Одна проводка (строка журнала) | Детали и drill down до источника |
| Periodic snapshot | Один период x самый детальный счёт | Остатки, баланс, быстрые отчёты |

- Снимок можно построить из журнала. Но его считают заранее: закрытие периода (`period close`) фиксирует результат.
- В журнале есть номер проводки. Это `degenerate dimension`.
- Снимок и журнал делят одни dimensions: дата, счёт, организация, ledger.
- Для каждой проводки нужен тип: дебет или кредит. Часто это две колонки или одна сумма со знаком.

## План счетов (chart of accounts)

План счетов — это основа dimension `account`.

- Номер счёта часто «умный»: 1000-1999 активы, 2000-2999 обязательства. Это `intelligent key`.
- В dimension не заставляйте людей фильтровать по первой цифре. Добавьте атрибуты: `account_type`, `account_group`, `normal_balance`.
- Cost center даёт rollup в отдел и подразделение. Это отдельная dimension `organization`.
- Если ledger несколько (местный, налоговый, управленческий), добавьте dimension `ledger`. Или храните их отдельными фактами.
- Для нескольких фискальных календарей в `date` держите несколько наборов атрибутов: `fiscal_year`, `fiscal_period`, `calendar_month`.

## Остатки: semi-additive и year-to-date

| Вопрос | Правило |
|---|---|
| Остаток на счёте | Semi-additive. Суммируйте по счетам, не по времени |
| Year-to-date (YTD) | Не храните в fact. Считайте window-функцией |
| Оборот за период | Additive. Суммируйте по любым dimensions |

- YTD в fact опасен. Две даты в запросе дают двойной счёт.
- Для периодов фискального года пригодится атрибут `fiscal_period` в `date`.

## Бюджет

Бюджет планируют не так детально, как проводят. Часто: месяц x отдел x группа счетов.

- Это другой grain. Бюджет — отдельная fact table.
- Dimensions бюджета — «сжатые» версии dimensions факта. Они должны быть conformed: те же ключи и значения.
- Сравнивайте план и факт на общем grain. Сначала агрегируйте актуальные данные до уровня бюджета. Потом делайте `JOIN`.
- Готовый запрос «план против факта» можно положить в consolidated fact table. Это вторичная таблица. Основа остаётся в двух процессах.

![Цепочка бюджетирования: бюджет, обязательства, платежи, проводки и отчёт план против факта](/assets/data-warehouse-toolkit/ch07-budget-chain.png)

Цепочка в книге: budget, commitment, payment, actual. Каждый шаг — свой бизнес-процесс и своя fact table. Общие dimensions связывают их.

## Иерархии организации

| Тип иерархии | Решение |
|---|---|
| Fixed depth (всегда N уровней) | Колонки в dimension: `division`, `department`, `cost_center` |
| Slightly ragged (до 3-4 уровней, разной глубины) | Те же колонки. Пустые уровни повторяют родителя |
| Ragged, глубина неизвестна | `bridge table` с парами «предок - потомок» |

- Bridge содержит: `parent_key`, `child_key`, `depth`, `is_top`, `is_leaf`. Ещё в ней есть пара «узел - сам себе» с глубиной 0.
- Fact привязан к узлу. В запросе join идёт fact -> bridge -> dimension. Так считается итог узла со всеми потомками.
- Если владение долевое, в bridge добавляют `ownership_pct` (weighting factor). Сумма долей по ребёнку = 100%.
- Если иерархия меняется во времени, в bridge добавляют `effective_date` и `expiration_date`.
- Альтернатива bridge: в `dim` хранят путь строкой (`/1/3/7/`) и ищут `LIKE`. Это проще, но менее гибко.
- Рекурсивный `parent_key` в самой dimension удобен для источника. В BI он не работает: `SQL` не умеет сворачивать дерево без `recursive CTE`.

## Ключевые термины

| Термин | Значение |
|---|---|
| General ledger | Главная книга: все проводки и счета |
| Chart of accounts | План счетов: основа dimension `account` |
| Journal entry | Проводка. Одна строка = одно событие |
| Periodic snapshot | Остатки на конец периода |
| Period close | Закрытие периода: после него цифры фиксируют |
| Bridge table | Таблица связей для иерархии или many-to-many |
| Consolidated fact | Fact, объединяющий метрики нескольких процессов на общем grain |

## Что это значит на практике

- Журнал загружайте как есть, на atomic grain. Снимок стройте из него моделью `dbt`, а не вручную.
- Проверьте баланс: сумма дебетов равна сумме кредитов. Это первый тест на загрузку.
- Не клейте YTD в fact. Пусть BI считает.
- Для плана и факта на разном grain всегда агрегируйте до общего уровня. Иначе сумма бюджета удвоится.
- Для иерархий дерево раскрывайте один раз при загрузке (`recursive CTE`) и храните в bridge.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём журнал, снимок, бюджет и иерархию

```sql
-- дата: календарный и фискальный (год с апреля) месяц
CREATE TABLE dim_date AS
SELECT
    strftime(d, '%Y%m%d')::INT AS date_key,
    d AS full_date,
    month(d) AS cal_month,
    CASE WHEN month(d) >= 4 THEN year(d) + 1 ELSE year(d) END AS fiscal_year,
    (month(d) + 8) % 12 + 1 AS fiscal_period
FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_account AS
SELECT * FROM (VALUES
    (1, 1000, 'Касса',            'Asset',   'Cash',       'D'),
    (2, 1200, 'Дебиторка',        'Asset',   'Receivable', 'D'),
    (3, 4000, 'Выручка',          'Income',  'Revenue',    'C'),
    (4, 5000, 'Зарплата',         'Expense', 'Payroll',    'D'),
    (5, 5200, 'Маркетинг',        'Expense', 'Marketing',  'D')
) t(account_key, account_number, account_name, account_type, account_group, normal_balance);

-- ragged иерархия: у узлов разная глубина
CREATE TABLE dim_org AS
SELECT * FROM (VALUES
    (1, 'Группа',          NULL, 'Головной офис'),
    (2, 'Продажи',         1,    'Продажи'),
    (3, 'Маркетинг',       1,    'Маркетинг'),
    (4, 'Продажи Москва',  2,    'Продажи'),
    (5, 'Продажи Казань',  2,    'Продажи'),
    (6, 'Казань розница',  5,    'Продажи')
) t(org_key, org_name, parent_key, department);

-- grain: одна строка проводки. Каждая запись (entry) = две строки: дебет и кредит
CREATE TABLE fact_gl_journal AS
WITH e AS (
    SELECT i,
           1 + (i // 3) % 12 AS m,
           i % 3 AS kind,
           [4, 6, 3, 5][1 + i % 4] AS org_key,
           1000 + (i % 7) * 100 AS amount
    FROM range(0, 360) t(i)
)
SELECT 'JE-' || lpad(i::VARCHAR, 5, '0') AS journal_entry_id,
       strftime(make_date(2024, m, 1 + i % 28), '%Y%m%d')::INT AS date_key,
       account_key, org_key,
       debit AS debit_amount, credit AS credit_amount
FROM e,
     LATERAL (VALUES
        -- выручка: дебет дебиторка, кредит выручка
        (CASE kind WHEN 0 THEN 2 WHEN 1 THEN 4 ELSE 5 END, amount, 0),
        (CASE kind WHEN 0 THEN 3 ELSE 1 END,               0, amount)
     ) l(account_key, debit, credit);

-- snapshot: один период x счёт x организация. Сетка плотная: строки есть и без движения
CREATE TABLE fact_gl_snapshot AS
WITH grid AS (
    SELECT 202400 + m AS month_key, a.account_key, o.org_key
    FROM range(1, 13) t(m), dim_account a, dim_org o
),
net AS (
    SELECT (date_key // 100) AS month_key, account_key, org_key,
           sum(debit_amount - credit_amount) AS period_net_amount
    FROM fact_gl_journal
    GROUP BY ALL
)
SELECT g.month_key, g.account_key, g.org_key,
       coalesce(n.period_net_amount, 0) AS period_net_amount,
       sum(coalesce(n.period_net_amount, 0)) OVER (
           PARTITION BY g.account_key, g.org_key ORDER BY g.month_key
       ) AS ending_balance
FROM grid g
LEFT JOIN net n USING (month_key, account_key, org_key);

-- бюджет: месяц x отдел x счёт. Это более крупный grain
CREATE TABLE fact_budget AS
SELECT 202400 + m AS month_key, dep.department, a.account_key,
       CASE a.account_key WHEN 3 THEN 14000 WHEN 4 THEN 13000 ELSE 12000 END / 2 AS budget_amount
FROM range(1, 13) t(m)
CROSS JOIN (VALUES ('Продажи'), ('Маркетинг')) dep(department)
CROSS JOIN (VALUES (3), (4), (5)) a(account_key);

-- bridge: пары предок - потомок, глубина считается рекурсивно
CREATE TABLE bridge_org AS
WITH RECURSIVE r AS (
    SELECT org_key AS parent_key, org_key AS child_key, 0 AS depth FROM dim_org
    UNION ALL
    SELECT r.parent_key, o.org_key, r.depth + 1
    FROM r JOIN dim_org o ON o.parent_key = r.child_key
)
SELECT * FROM r;
```

### Шаг 2. Проверяем баланс

```sql
-- должно быть 0: дебеты равны кредитам
SELECT sum(debit_amount) - sum(credit_amount) AS imbalance FROM fact_gl_journal;

SELECT count(*) AS lines, count(DISTINCT journal_entry_id) AS entries FROM fact_gl_journal;
```

### Задания

**1.** Результат по типам счетов. Покажите дебеты, кредиты и сальдо для каждого `account_type`.

<details>
<summary>Решение</summary>

```sql
SELECT a.account_type,
       sum(j.debit_amount)  AS debit,
       sum(j.credit_amount) AS credit,
       sum(j.debit_amount - j.credit_amount) AS net_debit
FROM fact_gl_journal j
JOIN dim_account a USING (account_key)
GROUP BY a.account_type
ORDER BY a.account_type;
```
</details>

**2.** Остаток кассы на конец каждого месяца. Это semi-additive fact: суммируйте по организациям, но не по месяцам.

<details>
<summary>Решение</summary>

```sql
SELECT month_key, sum(ending_balance) AS cash_balance
FROM fact_gl_snapshot
WHERE account_key = 1
GROUP BY month_key
ORDER BY month_key;
```

В учебных данных касса только расходуется, поэтому баланс отрицательный. Сумма по организациям верна. Сумма по месяцам не имеет смысла.

Снимок плотный: строки есть и там, где проводок не было. Иначе сумма по организациям за месяц будет неполной.
</details>

**3.** Year-to-date без хранения. Посчитайте выручку по месяцам и накопленную выручку с начала фискального года (апрель) с помощью window-функции.

<details>
<summary>Решение</summary>

```sql
WITH m AS (
    SELECT d.fiscal_year, d.fiscal_period, d.cal_month,
           sum(j.credit_amount - j.debit_amount) AS revenue
    FROM fact_gl_journal j
    JOIN dim_date d USING (date_key)
    WHERE j.account_key = 3
    GROUP BY ALL
)
SELECT fiscal_year, fiscal_period, cal_month, revenue,
       sum(revenue) OVER (PARTITION BY fiscal_year ORDER BY fiscal_period) AS revenue_ytd
FROM m
ORDER BY fiscal_year, fiscal_period;
```
</details>

**4.** План против факта. Бюджет лежит на grain «месяц x отдел x счёт». Сначала агрегируйте факт до этого grain. Потом сделайте `JOIN`.

<details>
<summary>Решение</summary>

```sql
WITH actual AS (
    SELECT (j.date_key // 100) AS month_key, o.department, j.account_key,
           sum(CASE WHEN a.normal_balance = 'C'
                    THEN j.credit_amount - j.debit_amount
                    ELSE j.debit_amount - j.credit_amount END) AS actual_amount
    FROM fact_gl_journal j
    JOIN dim_org o USING (org_key)
    JOIN dim_account a USING (account_key)
    WHERE j.account_key IN (3, 4, 5)
    GROUP BY ALL
)
SELECT b.department, a.account_name,
       sum(b.budget_amount) AS budget,
       sum(coalesce(x.actual_amount, 0)) AS actual,
       sum(coalesce(x.actual_amount, 0)) - sum(b.budget_amount) AS variance
FROM fact_budget b
JOIN dim_account a USING (account_key)
LEFT JOIN actual x USING (month_key, department, account_key)
GROUP BY b.department, a.account_name
ORDER BY b.department, a.account_name;
```

Если соединить факт и бюджет без агрегации, бюджет повторится для каждой проводки.
</details>

**5.** Ragged иерархия. Посчитайте расходы по каждому узлу `dim_org` вместе с потомками. Используйте `bridge_org`.

<details>
<summary>Решение</summary>

```sql
SELECT p.org_name, sum(j.debit_amount - j.credit_amount) AS expense_incl_children
FROM bridge_org b
JOIN dim_org p ON p.org_key = b.parent_key
JOIN fact_gl_journal j ON j.org_key = b.child_key
WHERE j.account_key IN (4, 5)
GROUP BY p.org_name, b.parent_key
ORDER BY b.parent_key;
```

Строка «Группа» должна дать сумму всех расходов. Проверьте это.
</details>

## Вопросы для самопроверки

1. Чем журнал проводок отличается от снимка? Когда нужны оба?
2. Почему year-to-date не хранят в fact table?
3. Как сравнить бюджет и факт, если у них разный grain?
4. Когда для иерархии нужна bridge table, а не колонки в dimension?
