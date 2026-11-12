---
title: "The Data Warehouse Toolkit, глава 11: Телеком"
head:
  - tag: title
    content: "Биллинг телеком и design review: Kimball | Инжиниринг Данных"
description: "Конспект главы 11 The Data Warehouse Toolkit: модель биллинга, ревью дизайна, grain, degenerate dimension, surrogate keys и YTD. Практика в DuckDB."
sidebar:
  order: 11
  label: "11. Телеком"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** глава показывает ревью чужой модели. Черновик биллинга телеком-компании содержит типичные ошибки. Книга разбирает их по одной и даёт общий чеклист для design review.

![Исправленная star schema биллинга: одна fact-таблица и пять dimensions](/assets/data-warehouse-toolkit/ch11-billing-star.png)

## Bus matrix и выбор процесса

- Строки матрицы: покупки, инвентарь, активация, продажи, звонки (call detail), биллинг, поддержка, ремонт.
- Общие dimensions: дата, продукт, клиент, rate plan, sales organization, service line, switch, сотрудник.
- Для первой итерации выбрали биллинг. Он даёт выручку по клиентам, каналам продаж и тарифам.
- Звонки (call detail) самые детальные. Но их объём велик, а ценность для старта ниже. Их оставили на потом.
- Главное: выбирайте процесс по ценности для бизнеса и по реалистичности загрузки.

## Чеклист design review

| Проверка | Вопрос |
|---|---|
| Требования и источник | Данные из требований есть в источнике? Данные источника нужны бизнесу? |
| Бизнес-процесс | Модель отражает процесс, а не один отчёт? |
| Grain | Что такое одна строка? Ответ один для всей команды? |
| Единый grain facts | Все facts относятся к этому grain? |
| Dimensions и иерархии | Dimension плоские? Нет лишнего snowflake? Нет centipede (больше ~20 FK в fact)? |
| Строки разных уровней | Нет ли в dimension строк и для продукта, и для бренда с колонкой `level`? Это ведёт к двойному счёту |
| Date dimension | Есть хотя бы одна явная дата? Нет колонок `month_1`...`month_12` вместо строк? |
| Degenerate dimensions | Номер документа лежит в fact, а не в своей огромной dimension? |
| Surrogate keys | Везде ли суррогатные ключи? Исключение — date dimension |
| Описания | Есть понятные названия, не только коды? Они хранятся в таблице, а не в BI-слое? |
| Conformed dimensions | Общие dimensions совпадают с другими процессами? |

- Вопрос «что такое grain?» задавайте первым. Если команда отвечает по-разному, модель сломана.
- Строите на самом детальном grain, который есть для этого процесса.
- Модели лучше пересматривать каждые 12-24 месяца.

## Разбор черновика: что было не так

![Ошибки черновика биллинга и их исправления после ревью](/assets/data-warehouse-toolkit/ch11-design-review.png)

| Ошибка | Исправление |
|---|---|
| Grain «один счёт в месяц», но у счёта много линий | Grain: одна линия (`service line`) на одном счёте |
| `bill dimension` почти такой же большой, как fact | `bill_number` — `degenerate dimension` в fact |
| Дата счёта не связана с dimension | Дата в fact, `date` играет роль `bill date` |
| Sales channel в отдельной таблице (snowflake) | Атрибуты канала внутри `sales organization` |
| Код типа тарифа лежит в fact как текст | Код и описание в `rate plan` |
| Ключи из источника как primary key | `surrogate key` для каждой dimension |
| В fact хранится year-to-date | Убрать. YTD считает запрос или BI |
| Только коды, без названий | Добавить понятные описания |

### Customer, rate plan, sales org и service line

- У service line один клиент, один тариф и одна организация продаж. Можно слить всё в одну dimension.
- Но линий миллионы, а клиентов и тарифов сильно меньше. Поэтому их оставляют отдельными dimensions (по сути mini-dimensions).
- Атрибуты, которые меняются, нужно обрабатывать SCD. Книга оставляет этот вопрос на следующий шаг.

## Принципы, которые стоит запомнить

- **Single grain.** Все additive facts относятся к одному grain. YTD и другие накопленные суммы нарушают это.
- **Нет текстовых facts.** Флаги и коды живут в dimension, там их можно группировать.
- **Dimension плоские.** Иерархия «канал - организация» лежит в одной таблице. Нормализация нужна для OLTP, не для анализа.
- **Одно значение на строку.** Каждая dimension даёт одно значение для строки fact.
- **Даты как роли.** Одна `dim_date` служит как bill date, due date и другие. В запросах используют alias или view.
- **Описания и имена.** Люди читают названия. Коды остаются как атрибуты.
- **Не строить под один отчёт.** Модель должна переживать новые вопросы.

## Что ещё в главе

- Сначала модели по бизнес-процессам. Потом дополнительные: aggregates, accumulating snapshot, consolidated fact, subset fact для безопасности.
- Как проводить ревью: позвать бизнес, назначить ведущего и секретаря, домашнее задание («5 главных проблем»), начать с bus matrix, рисовать примеры строк, закончить итогами и владельцами задач.

### Переделка существующих таблиц

- Новый type 1 атрибут добавить легко. Новый type 2 атрибут с историей — дорого: нужны новые версии строк и пересчёт ключей в fact.
- Переход на conformed dimensions требует перезагрузить fact с новыми ключами.
- View над таблицами немного защищают отчёты, но не полностью.
- Сравните цену и пользу. Варианты: переделать, построить заново, оставить как есть. Хороший момент — миграция источника или смена BI.

## Geographic location dimension

- Соблазн: одна общая таблица всех адресов (клиенты, линии, вышки, офисы) как outrigger ко всем dimensions.
- Книга против этого в presentation area. Адреса из разных dimensions почти не пересекаются. Общая таблица медленнее и сложнее для пользователей.
- Стандартизация адресов — задача ETL. Общая таблица может жить в back room.
- Для пользователей география — атрибуты внутри каждой dimension: город и регион в `dim_customer`, свои в `dim_service_line`.

## Ключевые термины

| Термин | Значение |
|---|---|
| Service line | Телефонный номер, линия связи |
| Rate plan | Тариф |
| Degenerate dimension | Номер счёта в fact без отдельной таблицы |
| Role-playing dimension | Одна dimension в нескольких ролях (bill date, due date) |
| Snowflake | Нормализованная dimension. Обычно не нужна |
| Design review | Структурная проверка модели |

## Что это значит на практике

- Перед ревью выпишите grain одним предложением. Потом сверьте с ним каждую колонку fact.
- Колонки `ytd_*`, `*_flag` в fact — повод для вопроса. Обычно им место в запросе или в dimension.
- В `dbt` тест `relationships` проверяет ключи. Тест `unique` на сочетании ключей проверяет grain.
- Если dimension почти такого же размера, как fact, это признак ошибки. Скорее всего, это degenerate dimension.
- Не отказывайтесь от surrogate keys ради «простоты». Источник меняет коды.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём модель биллинга

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d::DATE AS full_date,
       month(d) AS month_number, year(d) AS year_number
FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1,'Анна','Москва'),(2,'Борис','Москва'),(3,'Вера','Казань'),
    (4,'Глеб','Казань'),(5,'Дина','Тверь'),(6,'Егор','Тверь')
) t(customer_key, customer_name, city);

-- география как атрибуты dimension: город -> регион (без общей location-таблицы)
CREATE TABLE dim_service_line AS
SELECT l AS service_line_key,
       '+7-9' || lpad((l * 1117)::VARCHAR, 3, '0') || '-0000' AS phone_number,
       CASE WHEN l % 3 = 1 THEN '495' WHEN l % 3 = 2 THEN '843' ELSE '482' END AS area_code,
       CASE WHEN l % 3 = 1 THEN 'Москва' WHEN l % 3 = 2 THEN 'Казань' ELSE 'Тверь' END AS city,
       CASE WHEN l % 3 = 1 THEN 'Центр' WHEN l % 3 = 2 THEN 'Поволжье' ELSE 'Центр' END AS region,
       DATE '2022-01-01' + (l * 40)::INT AS activation_date
FROM range(1, 11) t(l);

CREATE TABLE dim_rate_plan AS
SELECT * FROM (VALUES
    (1,'Старт',  'P', 'Предоплата',  300, 30.0),
    (2,'Оптимум','C', 'Контракт',    800, 50.0),
    (3,'Макси',  'C', 'Контракт',   2000, 80.0)
) t(rate_plan_key, plan_name, plan_type_code, plan_type_description, plan_minutes_allowed, monthly_fee);

-- канал продаж внутри sales organization (без snowflake)
CREATE TABLE dim_sales_org AS
SELECT * FROM (VALUES
    (1,'Салон Центр','Розница'),
    (2,'Онлайн-магазин','Онлайн')
) t(sales_org_key, sales_org_name, sales_channel_name);

-- grain: одна линия на одном счёте (месяц)
CREATE TABLE fact_billing AS
WITH x AS (
    SELECT l AS service_line_key, m,
           1 + (l - 1) % 6 AS customer_key,
           1 + l % 3 AS rate_plan_key,
           1 + l % 2 AS sales_org_key,
           make_date(2024, m, 1 + ((1 + (l - 1) % 6) % 3) * 10) AS bill_date,
           100 + (l * 37 + m * 91) % 400 AS total_minutes,
           (l * 13 + m * 7) % 40 AS roam_minutes,
           (l * 53 + m * 17) % 300 AS message_count,
           500 + (l * 211 + m * 97) % 4000 AS data_mb
    FROM range(1, 11) a(l), range(1, 7) b(m)
)
SELECT strftime(bill_date, '%Y%m%d')::INT AS bill_date_key,
       strftime(bill_date + 20, '%Y%m%d')::INT AS due_date_key,
       x.customer_key, x.service_line_key, x.sales_org_key, x.rate_plan_key,
       'B-' || x.customer_key || '-' || lpad(x.m::VARCHAR, 2, '0') AS bill_number,
       x.total_minutes, x.roam_minutes, x.message_count, x.data_mb,
       p.monthly_fee AS month_service_charge,
       round(x.message_count * 0.05, 2) AS message_charge,
       round(x.data_mb * 0.01, 2)       AS data_charge,
       round(x.roam_minutes * 0.5, 2)   AS roaming_charge,
       round((p.monthly_fee + x.message_count * 0.05 + x.data_mb * 0.01 + x.roam_minutes * 0.5) * 0.1, 2) AS taxes
FROM x
JOIN dim_rate_plan p USING (rate_plan_key);
```

### Шаг 2. Проверяем grain

```sql
-- должно вернуть 0 строк: линия встречается один раз на счёте
SELECT bill_number, service_line_key, count(*)
FROM fact_billing
GROUP BY bill_number, service_line_key
HAVING count(*) > 1;

-- 60 строк fact (10 линий x 6 месяцев), но счетов меньше: в счёте несколько линий
SELECT count(*) AS fact_rows, count(DISTINCT bill_number) AS bills FROM fact_billing;
```

### Задания

**1.** Degenerate dimension. Найдите средний счёт: сумму по `bill_number`, число линий и общую сумму. Это заменяет dimension `bill`.

<details>
<summary>Решение</summary>

```sql
WITH bills AS (
    SELECT bill_number,
           count(*) AS lines,
           sum(month_service_charge + message_charge + data_charge + roaming_charge + taxes) AS bill_total
    FROM fact_billing
    GROUP BY bill_number
)
SELECT count(*) AS bills, round(avg(lines), 2) AS avg_lines_per_bill,
       round(avg(bill_total), 2) AS avg_bill_total
FROM bills;
```

Отдельная таблица `bill` не нужна. Номер счёта в fact группирует линии.
</details>

**2.** Выручка по типу тарифа и каналу продаж. Канал лежит в `dim_sales_org`, тип тарифа в `dim_rate_plan`. Нужен один `JOIN` на dimension.

<details>
<summary>Решение</summary>

```sql
SELECT p.plan_type_description, s.sales_channel_name,
       round(sum(f.month_service_charge + f.message_charge + f.data_charge + f.roaming_charge), 2) AS revenue
FROM fact_billing f
JOIN dim_rate_plan p USING (rate_plan_key)
JOIN dim_sales_org s USING (sales_org_key)
GROUP BY ALL
ORDER BY p.plan_type_description, s.sales_channel_name;
```
</details>

**3.** YTD без хранения. Посчитайте выручку по месяцам счёта и накопленный итог с начала года с помощью window-функции.

<details>
<summary>Решение</summary>

```sql
WITH m AS (
    SELECT d.month_number,
           round(sum(f.month_service_charge + f.message_charge + f.data_charge + f.roaming_charge), 2) AS revenue
    FROM fact_billing f
    JOIN dim_date d ON d.date_key = f.bill_date_key
    GROUP BY d.month_number
)
SELECT month_number, revenue,
       round(sum(revenue) OVER (ORDER BY month_number), 2) AS revenue_ytd
FROM m
ORDER BY month_number;
```

Если хранить YTD в fact, сумма по двум датам даст двойной счёт.
</details>

**4.** Role-playing dimension. Используйте `dim_date` дважды: как дату счёта и как срок оплаты. Найдите счета, срок оплаты которых попадает на другой месяц.

<details>
<summary>Решение</summary>

```sql
SELECT bill_number, bd.full_date AS bill_date, dd.full_date AS due_date
FROM fact_billing f
JOIN dim_date bd ON bd.date_key = f.bill_date_key
JOIN dim_date dd ON dd.date_key = f.due_date_key
WHERE bd.month_number <> dd.month_number
GROUP BY ALL
ORDER BY bill_date, bill_number
LIMIT 10;
```

Это одна физическая таблица в двух ролях. В BI делают два view: `dim_bill_date` и `dim_due_date`.
</details>

**5.** Non-additive и география. Посчитайте долю роуминга как `sum(roam)/sum(total)` по региону. Сравните со средним долей по строкам. Почему они различаются?

<details>
<summary>Решение</summary>

```sql
SELECT sl.region, sl.city,
       round(100.0 * sum(f.roam_minutes) / sum(f.total_minutes), 2) AS roam_pct_correct,
       round(100.0 * avg(f.roam_minutes * 1.0 / f.total_minutes), 2) AS roam_pct_avg_of_ratios
FROM fact_billing f
JOIN dim_service_line sl USING (service_line_key)
GROUP BY sl.region, sl.city
ORDER BY sl.region, sl.city;
```

Первое значение взвешено по минутам. Среднее долей даёт одинаковый вес линиям с малым и большим числом минут. Храните компоненты (числитель и знаменатель). Не храните готовый процент.
</details>

## Вопросы для самопроверки

1. Какой вопрос задают первым в design review и почему?
2. Почему `bill_number` лучше хранить как degenerate dimension?
3. Что плохого в year-to-date в fact table?
4. Когда sales channel в отдельной таблице допустим?
