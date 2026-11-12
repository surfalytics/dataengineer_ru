---
title: "The Data Warehouse Toolkit, глава 16: Страхование"
head:
  - tag: title
    content: "Страхование: policy, premium, claims, Kimball | Инжиниринг Данных"
description: "Конспект главы 16 The Data Warehouse Toolkit. Транзакции полиса, premium snapshot, written и earned premium, claims и практика в DuckDB."
sidebar:
  order: 16
  label: "16. Страхование"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в страховании клиент платит заранее, а выручка зарабатывается по месяцам. Поэтому суммировать транзакции полиса нельзя. Нужны две fact-таблицы: транзакции (что произошло) и ежемесячный snapshot (сколько заработано). Для убытков добавляют третью: accumulating snapshot по claim.

![Star schema страхования: транзакции полиса, premium snapshot, claim и общие dimensions](/assets/data-warehouse-toolkit/ch16-insurance-star.png)

## Цепочка создания ценности

Три основных процесса:

1. Выдать полис.
2. Получить премию.
3. Обработать claim (убыток).

Данные есть, но они разбросаны по системам автомобильных, домашних и других продуктов. Один клиент встречается в них много раз. Задача: собрать общие dimensions.

| Процесс | Строка в bus matrix |
|---|---|
| Транзакции полиса | Создание, изменение, отмена покрытия |
| Premium snapshot | Состояние полиса по месяцам |
| Транзакции claim | Резерв, платежи, задачи, закрытие |

Общие dimensions: дата, policyholder, покрытие (coverage), застрахованный объект (covered item), сотрудник, полис. Для claim добавляются claimant, third-party payee и claim.

Не вносите в bus matrix все детали на первом шаге. Сначала высокий уровень, потом по каждой fact-таблице: grain и меры.

## Транзакции полиса

Grain: одна транзакция полиса. Покрытие — это продукт страховщика. Покрытие применяется к объекту: дому или автомобилю.

| Часть | Что внутри |
|---|---|
| Dimensions | Дата транзакции, дата вступления в силу, policyholder, сотрудник, покрытие, объект, тип транзакции, audit |
| Degenerate dimension | Номер полиса |
| Fact | Сумма транзакции. Смысл зависит от типа |

### Две даты

- Дата транзакции — когда запись попала в систему.
- Дата вступления в силу (effective date) — когда изменение действует по закону.

Это две роли одной `dim_date`. Названия колонок должны отличаться.

### Policyholder и SCD

Типы SCD из главы 5 применяются прямо:

| Атрибут | Тип | Почему |
|---|---|---|
| Дата рождения | Type 1 | Изменения — исправления ошибки |
| ZIP-код | Type 2 | Участвует в расчёте риска. Нужна история |
| Сегмент клиента | Type 3 | Старая классификация нужна временно, после массового пересмотра |

Если dimension больше миллиона строк, часто меняющиеся атрибуты выносят в `mini-dimension` (type 4). То же для covered item: он обычно ещё больше, чем policyholder.

### Multivalued dimensions

- Коммерческий клиент имеет несколько отраслевых кодов (SIC, NAICS). Решение: bridge table с `weighting_factor`, если доли известны.
- У автомобильного полиса несколько водителей. Bridge с весом по доле премии. С датами начала и конца он превращается в factless fact об изменении связей.

### Остальные dimensions

- Тип транзакции — маленькая dimension (до 50 строк). Всё равно отдельная таблица.
- Audit dimension хранит происхождение строки: время загрузки, источник.
- Если у полиса есть собственные атрибуты (общий класс риска), появляется `dim_policy`. Тогда номер полиса уже не degenerate.

### Supertype и subtype

У домашних и автомобильных полисов свои атрибуты: марка машины или площадь дома. Решение:

- Общая fact-таблица (supertype) остаётся одной.
- Для каждой линии бизнеса есть subtype-dimension для покрытия и объекта с особыми атрибутами. Ключи те же.
- Для удобства можно сделать view на supertype fact для одной линии.

### Accumulating snapshot для полиса

Если нужен срок жизни, добавляют accumulating snapshot: одна строка на покрытие и объект. Даты: заявка, расчёт, андеррайтинг, начало, продление, окончание.

## Premium periodic snapshot

Транзакции показывают события, но не отвечают на вопрос «каков статус полиса и сколько выручки заработано в месяце». Для этого нужна вторая таблица.

| | Transaction fact | Premium snapshot |
|---|---|---|
| Grain | Одна транзакция | Полис × покрытие × объект × месяц |
| Время | Дата | Месяц (conformed `dim_month`) |
| Меры | Сумма транзакции | Written premium, earned premium |
| Особые dimensions | Тип транзакции | Status (новый, в силе, отменён) |

![Пример written и earned premium для полиса на год с отменой в марте](/assets/data-warehouse-toolkit/ch16-premium-example.png)

Пример из книги: годовой полис за 600 выписан 1 января.

| Месяц | Written | Earned |
|---|---|---|
| Январь | 600 | 50 |
| Февраль | 0 | 50 |
| Март (отмена 31 марта) | -450 | 50 |

Written — сколько продали. Earned — сколько заработали, потому что покрытие действовало. Правила earned сложные (изменения в середине месяца), поэтому значения берут из учётной системы, а не пересчитывают в BI.

Правила для snapshot:

- Используйте те же dimensions: policyholder, покрытие, объект. Month заменяет date.
- Меры в двух таблицах должны быть conformed: одинаковое имя и определение.
- Не все линии бизнеса имеют одинаковые меры. Для них делают отдельные snapshot-таблицы по линиям (subtype). Иначе половина колонок будет `NULL`.
- Snapshot не заменяет транзакции. Нужны обе таблицы.

## Claims

Claim — главный источник расходов. Поток событий:

1. Заявка. Устанавливают резерв: предварительная оценка убытка.
2. Расследование. Появляются задачи.
3. Платежи: клиенту, врачам, автомастерским. Нужен сотрудник, одобривший платёж.
4. Salvage (остатки имущества) и subrogation (взыскание с виновника) — это возврат денег.
5. Закрытие. Claim может быть открыт повторно.

### Claim transactions

Grain: одна задача или транзакция claim. Новые dimensions:

- Claimant и third-party payee. Часто «грязные»: людей трудно опознать. Платящая сторона иногда сама скрывается.
- Claim profile — это `junk dimension` для кодов с малой кардинальностью (способ обращения, признак катастрофы). Не создавайте огромный claim dimension из всех атрибутов. Высококардинальные поля (адрес, описание) — другое дело.

### Claim accumulating snapshot

Транзакции плохо отвечают на вопросы «чего достиг claim на сегодня». Для этого строят accumulating snapshot. Grain: одна строка на claim.

| Часть | Что внутри |
|---|---|
| Даты | Потеря, открытие, оценка, первый платёж, последний платёж, закрытие |
| Меры | Начальный резерв, текущий резерв, выплачено, salvage, subrogation |
| Lags | Потеря → открытие, открытие → первый платёж, открытие → закрытие |
| Status | Открыт, закрыт, открыт повторно |

Это подходит для процесса с 5–10 понятными вехами. Если процесс непредсказуем, оставьте самые важные даты, а остальное считайте по транзакциям.

### Joint analysis

Убыточность считают как claims / earned premium. Таблицы разного grain соединяют через conformed dimensions и conformed facts. Сначала агрегируйте обе до общего уровня, потом объединяйте (`drill across`).

## Ключевые термины

| Термин | Значение |
|---|---|
| Policy transaction | Любое изменение полиса |
| Written premium | Проданная премия за период |
| Earned premium | Заработанная премия: покрытие действовало |
| Coverage | Покрытие, продукт страховщика |
| Covered item | Застрахованный объект |
| Reserve | Предварительная оценка убытка |
| Salvage, subrogation | Возврат денег по claim |
| Claim profile | Junk dimension с кодами claim |
| Supertype и subtype | Общая схема и расширения для линий бизнеса |

## Что это значит на практике

- Две fact-таблицы для pay-in-advance бизнеса нужны всегда: transaction и snapshot. Это же верно для подписок и гарантий.
- В `dbt` earned premium считайте один раз в модели snapshot и тестируйте суммой по полису.
- Держите `policyholder_id` как durable key. Он нужен, чтобы видеть клиента через все версии SCD type 2.
- Не пытайтесь сложить транзакции в выручку в отчёте. Правила слишком сложные.
- Убыточность считайте после агрегации обеих таблиц до policy или месяца.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Суммы в условных единицах. Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_date AS
SELECT 0 AS date_key, NULL::DATE AS full_date, NULL::INT AS month_key
UNION ALL
SELECT strftime(d, '%Y%m%d')::INT, d::DATE, strftime(d, '%Y%m')::INT
FROM generate_series(DATE '2025-01-01', DATE '2025-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_month AS
SELECT strftime(m, '%Y%m')::INT AS month_key,
       m::DATE AS month_start,
       (m + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE AS month_end,
       monthname(m) AS month_name
FROM generate_series(DATE '2025-01-01', DATE '2025-06-01', INTERVAL 1 MONTH) t(m);

-- SCD type 2: у Анны сменился ZIP-код 1 марта
CREATE TABLE dim_policyholder AS
SELECT * FROM (VALUES
    (1, 'H1', 'Анна',  '101000', DATE '2024-01-01', DATE '2025-02-28'),
    (2, 'H1', 'Анна',  '420000', DATE '2025-03-01', DATE '9999-12-31'),
    (3, 'H2', 'Борис', '190000', DATE '2024-01-01', DATE '9999-12-31'),
    (4, 'H3', 'Вера',  '630000', DATE '2024-01-01', DATE '9999-12-31')
) t(policyholder_key, policyholder_id, policyholder_name, zip_code, valid_from, valid_to);

CREATE TABLE dim_coverage AS
SELECT * FROM (VALUES
    (1, 'Auto liability', 'Auto'),
    (2, 'Home fire',      'Home'),
    (3, 'Auto collision', 'Auto'),
    (4, 'Home theft',     'Home')
) t(coverage_key, coverage_name, line_of_business);

CREATE TABLE dim_covered_item AS
SELECT * FROM (VALUES
    (1, 'Toyota Camry 2020'),
    (2, 'Дом, Казань'),
    (3, 'Mazda 3 2022'),
    (4, 'Квартира, Казань')
) t(covered_item_key, item_description);

CREATE TABLE dim_transaction_type AS
SELECT * FROM (VALUES (1, 'New business'), (2, 'Endorsement'), (3, 'Cancellation')) t(txn_type_key, txn_type);

-- полисы: каждый на 12 месяцев от начала
CREATE TABLE stg_policy AS
SELECT * FROM (VALUES
    ('P-100', 'H1', 1, 1, DATE '2025-01-01'),
    ('P-101', 'H2', 2, 2, DATE '2025-02-01'),
    ('P-102', 'H3', 3, 3, DATE '2025-01-15'),
    ('P-103', 'H1', 4, 4, DATE '2025-03-10')
) t(policy_number, holder_id, coverage_key, covered_item_key, term_start);

-- транзакции: дата записи, дата вступления в силу, сумма
CREATE TABLE stg_policy_txn AS
SELECT * FROM (VALUES
    (1, 'P-100', 1, DATE '2025-01-01', DATE '2025-01-01',  600),
    (2, 'P-100', 3, DATE '2025-03-31', DATE '2025-03-31', -450),
    (3, 'P-101', 1, DATE '2025-02-01', DATE '2025-02-01', 1200),
    (4, 'P-101', 2, DATE '2025-04-05', DATE '2025-04-01',  100),
    (5, 'P-102', 1, DATE '2025-01-15', DATE '2025-01-15',  480),
    (6, 'P-103', 1, DATE '2025-03-10', DATE '2025-03-10',  360)
) t(txn_id, policy_number, txn_type_key, txn_date, effective_date, amount);

-- grain: одна транзакция полиса. Две роли даты
CREATE TABLE fact_policy_transaction AS
SELECT
    t.txn_id,
    dt.date_key AS transaction_date_key,
    de.date_key AS effective_date_key,
    h.policyholder_key,
    p.coverage_key,
    p.covered_item_key,
    t.txn_type_key,
    t.policy_number,
    t.amount AS policy_transaction_amount
FROM stg_policy_txn t
JOIN stg_policy p USING (policy_number)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND t.txn_date BETWEEN h.valid_from AND h.valid_to
JOIN dim_date dt ON dt.full_date = t.txn_date
JOIN dim_date de ON de.full_date = t.effective_date;

-- grain: полис x покрытие x объект x месяц
-- earned: сумма транзакции делится поровну на месяцы от даты вступления до конца срока
CREATE TABLE fact_premium_snapshot AS
WITH spread AS (
    SELECT t.txn_id, t.policy_number, t.amount,
           date_trunc('month', t.effective_date + INTERVAL 1 DAY)::DATE   AS from_month,
           (date_trunc('month', p.term_start) + INTERVAL 11 MONTH)::DATE  AS to_month
    FROM stg_policy_txn t
    JOIN stg_policy p USING (policy_number)
), earned AS (
    SELECT s.policy_number, m.month_key,
           sum(s.amount / (date_diff('month', s.from_month, s.to_month) + 1)) AS earned_premium
    FROM spread s
    JOIN dim_month m ON m.month_start BETWEEN s.from_month AND s.to_month
    GROUP BY ALL
), written AS (
    SELECT t.policy_number, d.month_key, sum(t.amount) AS written_premium
    FROM stg_policy_txn t
    JOIN dim_date d ON d.full_date = t.txn_date
    GROUP BY ALL
)
SELECT
    p.policy_number,
    m.month_key,
    h.policyholder_key,
    p.coverage_key,
    p.covered_item_key,
    CASE WHEN EXISTS (SELECT 1 FROM stg_policy_txn c
                      WHERE c.policy_number = p.policy_number AND c.txn_type_key = 3
                        AND c.effective_date <= m.month_end)
         THEN 'Cancelled' ELSE 'In force' END AS policy_status,
    coalesce(w.written_premium, 0)          AS written_premium,
    round(coalesce(e.earned_premium, 0), 2) AS earned_premium
FROM stg_policy p
JOIN dim_month m ON m.month_start >= date_trunc('month', p.term_start)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND m.month_end BETWEEN h.valid_from AND h.valid_to
LEFT JOIN earned  e ON e.policy_number = p.policy_number AND e.month_key = m.month_key
LEFT JOIN written w ON w.policy_number = p.policy_number AND w.month_key = m.month_key;

-- claims: дата потери и поток транзакций
CREATE TABLE stg_claim AS
SELECT * FROM (VALUES
    ('C1', 'P-100', DATE '2025-02-10'),
    ('C2', 'P-101', DATE '2025-04-12'),
    ('C3', 'P-102', DATE '2025-05-02'),
    ('C4', 'P-103', DATE '2025-05-20')
) t(claim_id, policy_number, loss_date);

CREATE TABLE stg_claim_txn AS
SELECT * FROM (VALUES
    ('C1', DATE '2025-02-11', 'open',    0),
    ('C1', DATE '2025-02-11', 'reserve', 300),
    ('C1', DATE '2025-03-01', 'payment', 100),
    ('C1', DATE '2025-03-20', 'payment', 120),
    ('C1', DATE '2025-04-02', 'close',   0),
    ('C2', DATE '2025-04-13', 'open',    0),
    ('C2', DATE '2025-04-13', 'reserve', 2000),
    ('C2', DATE '2025-05-10', 'payment', 400),
    ('C2', DATE '2025-05-20', 'salvage', 50),
    ('C3', DATE '2025-05-03', 'open',    0),
    ('C3', DATE '2025-05-03', 'reserve', 200),
    ('C3', DATE '2025-05-15', 'payment', 190),
    ('C3', DATE '2025-05-20', 'close',   0),
    ('C4', DATE '2025-05-21', 'open',    0),
    ('C4', DATE '2025-05-21', 'reserve', 100)
) t(claim_id, txn_date, txn_type, amount);

-- accumulating snapshot: одна строка на claim, строка обновляется при новых событиях
CREATE TABLE fact_claim AS
SELECT
    c.claim_id,
    c.policy_number,
    p.coverage_key,
    p.covered_item_key,
    h.policyholder_key,
    c.loss_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'open')    AS open_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'payment') AS first_payment_date,
    max(t.txn_date) FILTER (WHERE t.txn_type = 'payment') AS last_payment_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'close')   AS closed_date,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'reserve'), 0) AS original_reserve,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'payment'), 0) AS paid_to_date,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'salvage'), 0) AS salvage_collected,
    count(*) AS transaction_count,
    CASE WHEN min(t.txn_date) FILTER (WHERE t.txn_type = 'close') IS NULL THEN 'Open' ELSE 'Closed' END AS claim_status
FROM stg_claim c
JOIN stg_policy p USING (policy_number)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND c.loss_date BETWEEN h.valid_from AND h.valid_to
JOIN stg_claim_txn t USING (claim_id)
GROUP BY ALL;
```

### Шаг 2. Проверяем

```sql
-- у P-100 за три месяца written и earned равны: 150 = 150
SELECT policy_number, sum(written_premium) AS written, sum(earned_premium) AS earned
FROM fact_premium_snapshot
WHERE policy_number = 'P-100'
GROUP BY policy_number;

-- 4 claim. Сумма transaction_count равна 15 строкам источника
SELECT count(*) AS claims, sum(transaction_count) AS source_rows FROM fact_claim;
```

### Задания

**1.** Written и earned по месяцам. Покажите оба показателя для всех полисов. Почему они разные в марте и апреле?

<details>
<summary>Решение</summary>

```sql
SELECT m.month_name,
       sum(s.written_premium) AS written,
       sum(s.earned_premium)  AS earned
FROM fact_premium_snapshot s
JOIN dim_month m USING (month_key)
GROUP BY m.month_key, m.month_name
ORDER BY m.month_key;
```

В марте written меньше из-за отмены P-100 (-450). Earned при этом не падает резко: полис действовал весь месяц. Отмена влияет на earned только со следующего месяца.
</details>

**2.** Earned по линиям бизнеса. Покажите earned premium по месяцам для Auto и Home. Транзакции этого не дают: нужно распределение по времени.

<details>
<summary>Решение</summary>

```sql
SELECT m.month_name, c.line_of_business, sum(s.earned_premium) AS earned
FROM fact_premium_snapshot s
JOIN dim_month m USING (month_key)
JOIN dim_coverage c USING (coverage_key)
GROUP BY m.month_key, m.month_name, c.line_of_business
ORDER BY m.month_key, c.line_of_business;
```
</details>

**3.** SCD type 2. Покажите earned premium по ZIP-коду policyholder. Полис P-100 должен делиться между двумя ZIP: старый до февраля, новый с марта. Затем сверьте итог с суммой по всем полисам.

<details>
<summary>Решение</summary>

```sql
SELECT h.zip_code, h.policyholder_name,
       sum(s.earned_premium) AS earned
FROM fact_premium_snapshot s
JOIN dim_policyholder h USING (policyholder_key)
GROUP BY h.zip_code, h.policyholder_name
ORDER BY h.policyholder_name, h.zip_code;

SELECT sum(earned_premium) AS total_earned FROM fact_premium_snapshot;
```

Итого earned равно 1 040. Анна появляется в двух строках: 101000 за январь и февраль, 420000 с марта.
</details>

**4.** Claim как accumulating snapshot. Посчитайте lag от потери до открытия, от открытия до первого платежа и до закрытия в днях. Найдите открытые claims, где ещё не было платежей, на 2025-06-30.

<details>
<summary>Решение</summary>

```sql
SELECT claim_id, claim_status,
       date_diff('day', loss_date, open_date)           AS loss_to_open,
       date_diff('day', open_date, first_payment_date)  AS open_to_first_payment,
       date_diff('day', open_date, closed_date)         AS open_to_closed,
       paid_to_date
FROM fact_claim
ORDER BY claim_id;

-- открыты и нет платежей
SELECT claim_id, original_reserve,
       date_diff('day', open_date, DATE '2025-06-30') AS days_open
FROM fact_claim
WHERE claim_status = 'Open' AND first_payment_date IS NULL;
```

Claim C4 открыт 40 дней без платежей. У открытых claim lag закрытия равен `NULL`. Это нормально: события ещё не было.
</details>

**5.** Убыточность. Посчитайте loss ratio по линиям бизнеса: выплаты по claims делённые на earned premium. Сначала агрегируйте каждую таблицу до policy, потом соединяйте. Попробуйте и неправильный вариант: прямой join двух fact-таблиц.

<details>
<summary>Решение</summary>

```sql
-- правильно: drill across через общий уровень (policy)
WITH premium AS (
    SELECT policy_number, coverage_key, sum(earned_premium) AS earned
    FROM fact_premium_snapshot
    GROUP BY ALL
), claims AS (
    SELECT policy_number, sum(paid_to_date) AS paid
    FROM fact_claim
    GROUP BY policy_number
)
SELECT c.line_of_business,
       sum(p.earned)                       AS earned_premium,
       coalesce(sum(cl.paid), 0)           AS paid_claims,
       round(coalesce(sum(cl.paid), 0) / sum(p.earned), 2) AS loss_ratio
FROM premium p
JOIN dim_coverage c USING (coverage_key)
LEFT JOIN claims cl USING (policy_number)
GROUP BY c.line_of_business
ORDER BY c.line_of_business;

-- неправильно: прямой join строк snapshot и claim. Выплаты считаются много раз
SELECT sum(cl.paid_to_date) AS paid_wrong
FROM fact_premium_snapshot s
JOIN fact_claim cl USING (policy_number);
```

Правильные выплаты равны 710. Неправильный join размножает claim на число месяцев полиса, и сумма сильно больше.
</details>

## Вопросы для самопроверки

1. Почему для страхования нужны и transaction fact, и monthly snapshot?
2. Чем written premium отличается от earned premium? Приведите пример с отменой.
3. Как SCD type 2 для ZIP-кода влияет на отчёт по snapshot?
4. Какие lags и даты хранит claim accumulating snapshot?
