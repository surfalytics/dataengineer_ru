---
title: "The Data Warehouse Toolkit, глава 20: Разработка ETL"
head:
  - tag: title
    content: "Разработка ETL: инкрементальная загрузка | Инжиниринг Данных"
description: "Конспект главы 20 The Data Warehouse Toolkit. 10 шагов разработки ETL: план, исторические загрузки, инкрементальная обработка, real-time и практика в DuckDB."
sidebar:
  order: 20
  label: "20. Разработка ETL"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** ETL разрабатывают по шагам. Сначала план и стратегии. Потом историческая загрузка dimensions и facts. Потом инкрементальная загрузка, которая работает без людей и безопасно перезапускается.

![Инкрементальный ETL: high-water mark, staging, screens, dimensions, surrogate key pipeline, fact table, audit](/assets/data-warehouse-toolkit/ch20-incremental-etl.png)

## 10 шагов

| Шаг | Что делаем |
|---|---|
| 1. High-level plan | Схема: источники, цели, потоки данных |
| 2. Выбор ETL tool | Решаем до детального плана. Иначе придётся переделывать |
| 3. Default strategies | Общие правила для всех таблиц |
| 4. Drill down по таблицам | Детальный план для каждой целевой таблицы |
| 5. Историческая загрузка dimensions | Чистка, ключи, загрузка |
| 6. Историческая загрузка facts | Большой объём, surrogate key pipeline |
| 7. Инкрементальные dimensions | Новые и изменённые строки, SCD |
| 8. Инкрементальные facts | Автоматическая загрузка, late arriving |
| 9. Агрегаты и OLAP | Пересчёт после загрузки |
| 10. Работа и автоматизация | Расписание, обработка ошибок, lights-out |

## Шаги 1-4. План

- Перед дизайном ETL должны быть готовы логическая модель, план архитектуры и черновой source-to-target mapping.
- Подумайте, где будет работать преобразование: на источнике, на целевой системе или на отдельной платформе. И какую нагрузку можно создать на источник.
- Начните с простой схемы: источники слева, цели справа.
- **Default strategies** — общие ответы на вопросы:
  - как извлекаем данные;
  - как проверяем качество;
  - как находим изменения (CDC);
  - как выдаём surrogate keys;
  - как применяем SCD;
  - как обрабатываем ошибки и поздние данные.
- Для каждой целевой таблицы дальше пишут отдельный план: источники, правила, порядок загрузки. Dimensions грузятся раньше facts.

## Шаг 5. Историческая загрузка dimensions

Dimension с одним источником — самый простой случай. Но даже он требует чистки.

| Задача | Пример |
|---|---|
| Простые преобразования | Тип данных, регистр, пробелы, пустые значения |
| Объединение источников | Клиенты из CRM и из биллинга |
| Расшифровка кодов | `M` в «Мужской» |
| Проверка связей «многие к одному» | Один бренд — одна категория. Иначе иерархия сломана |
| Присвоение surrogate keys | Сначала тестовая загрузка, потом полная |
| Загрузка | Строка Unknown в каждый dimension |

Date dimension и другие статические dimensions строят один раз. Бизнес должен их утвердить.

## Шаг 6. Историческая загрузка facts

- Извлекайте только те строки, которые попадают в фильтры проекта. Не берите всё подряд.
- Считайте audit statistics: число строк, суммы. Потом их сверят.
- Уберите лишние нагрузки: перед загрузкой можно удалить индексы и вернуть после.
- Surrogate key pipeline — главный шаг. Natural keys из источника заменяются на surrogate keys.
- Pipeline лучше держать в памяти. Dimensions небольшие, а fact огромный.
- Для больших таблиц загружайте по партициям и в параллель.
- Для строк без совпадения: unknown member или запись в error table.

## Шаг 7. Инкрементальные dimensions

- Если можно, берите из источника только изменённые строки. Иначе берите снимок целиком и сравнивайте.
- **Новые строки:** ищем natural key в dimension. Нет — новая строка.
- **Изменённые строки:** сравниваем колонки или hash type 1 и hash type 2.
- Тип 1 меняет значение на месте. Тип 2 закрывает версию и добавляет новую.
- Удаление в источнике не значит удаление в dimension. На эту строку ссылаются факты.
- Дата начала новой версии — день, когда изменение стало известно. Дата окончания текущей — дальняя дата.

## Шаг 8. Инкрементальные facts

Инкрементальная загрузка должна быть полностью автоматической.

1. **Extract и checkpoint качества.** Сырые данные пишут в staging. Это архив и точка перезапуска. Тут же считают метрики качества.
2. **Transformations и surrogate key pipeline.** Для строк без ключа нужна автоматическая политика:

| Политика | Когда подходит |
|---|---|
| Остановить загрузку | Почти никогда |
| Отбросить строку | Если пропуск означает «данные не нужны» |
| Записать в error table | Хорошо, но нужен процесс разбора |
| Unknown member | Простой вариант |
| Inferred member | Лучший вариант, если dimension придёт позже |

3. **Late arriving facts.** Загрузка идёт после полуночи, но данные могут быть старше. Для type 2 dimension берите версию на дату события.
4. **Загрузка.** Обновления делайте как delete и insert. Это быстрее, чем много `UPDATE`.
5. **Snapshot facts.** Periodic snapshot грузят целиком в новую партицию. Accumulating snapshot обновляют.

Если загрузка не успевает, есть три пути:

- грузить чаще, маленькими порциями;
- обрабатывать данные параллельно (параллельные потоки или партиции);
- разделять структуры, чтобы работа шла без конфликтов.

## Шаги 9-10. Агрегаты и работа системы

- Агрегаты и OLAP пересчитывают после загрузки facts. Если нужно, обновляют только изменившиеся периоды.
- ETL должен работать без людей:
  - расписание задач с зависимостями;
  - автоматическая обработка предсказуемых ошибок (ранний факт, `NULL` в поле);
  - понятные действия при непредсказуемых ошибках;
  - уведомления и точки перезапуска.
- Все метрики операций пишите в таблицы. Это основа для мониторинга и reconciliation.

## Real-time

Сначала выясните, что именно просит бизнес: «real-time» часто значит «раз в час». Книга делит запросы на три класса.

| | Daily | Intra-day | Instantaneous |
|---|---|---|---|
| Способ | Batch ETL | Micro-batch | Streaming |
| Данные | Reconciled | Provisional | Provisional |
| Проверки качества | Column, structure, business rule | Column и structure | Только column |
| Итоговые числа | Финальные | Исправляются ночью | Могут меняться |

Правило: чем ниже latency, тем меньше проверок качества. Низкая задержка даёт более грязные данные.

Компромиссы при real-time:

- заменить batch-файлы потоком;
- ограничить quality screens простыми проверками;
- загружать facts вместе с dimensions;
- убрать staging (тогда пропадает архив);
- добавить real-time partition в presentation area. Ночью она заменяется финальными данными.

## Ключевые термины

| Термин | Значение |
|---|---|
| High-water mark | Граница последней загруженной записи. Следующий запуск берёт всё новее |
| Idempotent load | Повторный запуск даёт тот же результат |
| Reconciliation | Сверка счётчиков и сумм между источником и хранилищем |
| Surrogate key pipeline | Замена natural keys на surrogate keys в fact |
| Inferred member | Заглушка в dimension для раннего факта |
| Late arriving fact | Событие, которое пришло позже срока |
| Real-time partition | Временная часть fact для свежих данных |
| Lights-out | Работа ETL без участия человека |

## Что это значит на практике

- Храните HWM в таблице управления. Обновляйте его только после успешной загрузки.
- Берите HWM из данных (`max(modified_at)` из staging), а не из часов. Иначе пропуски и дубли.
- Делайте загрузку idempotent: удалите строки по бизнес-ключу и вставьте заново. Тогда любой перезапуск безопасен. В `dbt` это стратегия `delete+insert` или `merge` для incremental.
- Пишите счётчики каждой загрузки в audit-таблицу. Сверяйте источник и хранилище.
- Не теряйте строки без ключа. Отправляйте их на unknown member и пишите событие в error table.
- Не обещайте real-time без уточнения. Спросите, какое решение принимается и как быстро.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Решения тоже запускайте по порядку: каждое использует результат предыдущего.

### Шаг 1. Источник, dimension и таблицы управления

```sql
CREATE TABLE src_customer AS
SELECT * FROM (VALUES
    ('C1', 'Иван', 'Москва'),
    ('C2', 'Анна', 'Казань'),
    ('C3', 'Олег', 'Самара')
) t(customer_id, name, city);

CREATE TABLE src_orders (
    order_id INT, customer_id VARCHAR, order_date DATE,
    amount DECIMAL(12,2), modified_at TIMESTAMP);

INSERT INTO src_orders VALUES
    (1, 'C1', DATE '2024-05-01', 100.00, TIMESTAMP '2024-05-01 10:00:00'),
    (2, 'C2', DATE '2024-05-01',  50.00, TIMESTAMP '2024-05-01 11:00:00'),
    (3, 'C3', DATE '2024-05-02',  70.00, TIMESTAMP '2024-05-02 09:00:00');

-- dimension со строкой Unknown (ключ 0)
CREATE TABLE dim_customer AS
SELECT 0 AS customer_key, NULL::VARCHAR AS customer_id, 'Unknown' AS name, 'Unknown' AS city
UNION ALL
SELECT row_number() OVER (ORDER BY customer_id), customer_id, name, city FROM src_customer;

-- таблицы управления и аудита
CREATE TABLE etl_control AS
SELECT 'orders' AS table_name, TIMESTAMP '1900-01-01' AS high_water_mark, 0 AS last_batch_id;

CREATE TABLE etl_batch_log (
    batch_id INT, table_name VARCHAR, rows_extracted INT,
    rows_loaded INT, rows_unknown_member INT, new_hwm TIMESTAMP);

CREATE TABLE error_event (batch_id INT, order_id INT, reason VARCHAR);

-- grain: один заказ
CREATE TABLE fact_orders (
    order_id INT, customer_key INT, order_date DATE, amount DECIMAL(12,2), batch_id INT);
```

### Задания

**1.** Историческая загрузка. Загрузите все заказы в `fact_orders` через surrogate key lookup. Запишите строку в `etl_batch_log`. Сдвиньте high-water mark на максимальное `modified_at`.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE stg_orders AS
SELECT * FROM src_orders
WHERE modified_at > (SELECT high_water_mark FROM etl_control WHERE table_name = 'orders');

INSERT INTO fact_orders
SELECT s.order_id, coalesce(d.customer_key, 0), s.order_date, s.amount,
       (SELECT last_batch_id + 1 FROM etl_control)
FROM stg_orders s
LEFT JOIN dim_customer d ON d.customer_id = s.customer_id;

INSERT INTO etl_batch_log
SELECT c.last_batch_id + 1, 'orders',
       (SELECT count(*) FROM stg_orders),
       (SELECT count(*) FROM fact_orders WHERE batch_id = c.last_batch_id + 1),
       (SELECT count(*) FROM fact_orders WHERE batch_id = c.last_batch_id + 1 AND customer_key = 0),
       (SELECT max(modified_at) FROM stg_orders)
FROM etl_control c;

UPDATE etl_control
SET high_water_mark = (SELECT max(modified_at) FROM stg_orders),
    last_batch_id = last_batch_id + 1;

SELECT * FROM etl_control;
SELECT * FROM etl_batch_log;
```

HWM стал `2024-05-02 09:00:00`. В fact три строки.
</details>

**2.** Инкрементальная загрузка. В источнике на следующий день: заказ 2 исправлен (сумма 55), появились заказ 4 и заказ 5. У заказа 5 клиент `C9` ещё не известен. Загрузите только новое. Для заказа 2 удалите старую версию и вставьте новую. Клиента, которого нет в dimension, отправьте на unknown member и запишите событие в `error_event`.

<details>
<summary>Решение</summary>

```sql
-- изменения в источнике (источник правят на месте)
UPDATE src_orders
SET amount = 55.00, modified_at = TIMESTAMP '2024-05-03 08:00:00'
WHERE order_id = 2;

INSERT INTO src_orders VALUES
    (4, 'C1', DATE '2024-05-03', 120.00, TIMESTAMP '2024-05-03 09:00:00'),
    (5, 'C9', DATE '2024-05-03',  30.00, TIMESTAMP '2024-05-03 10:00:00');

-- 1) staging: только строки новее HWM
CREATE OR REPLACE TABLE stg_orders AS
SELECT * FROM src_orders
WHERE modified_at > (SELECT high_water_mark FROM etl_control WHERE table_name = 'orders');

-- 2) очистка прошлой попытки этого batch и старых версий заказов
DELETE FROM fact_orders WHERE order_id IN (SELECT order_id FROM stg_orders);
DELETE FROM error_event WHERE batch_id = (SELECT last_batch_id + 1 FROM etl_control);

-- 3) события качества
INSERT INTO error_event
SELECT (SELECT last_batch_id + 1 FROM etl_control), s.order_id, 'клиент не найден в dim_customer'
FROM stg_orders s
LEFT JOIN dim_customer d ON d.customer_id = s.customer_id
WHERE d.customer_key IS NULL;

-- 4) fact через surrogate key pipeline
INSERT INTO fact_orders
SELECT s.order_id, coalesce(d.customer_key, 0), s.order_date, s.amount,
       (SELECT last_batch_id + 1 FROM etl_control)
FROM stg_orders s
LEFT JOIN dim_customer d ON d.customer_id = s.customer_id;

-- 5) audit и HWM
DELETE FROM etl_batch_log WHERE batch_id = (SELECT last_batch_id + 1 FROM etl_control);
INSERT INTO etl_batch_log
SELECT c.last_batch_id + 1, 'orders',
       (SELECT count(*) FROM stg_orders),
       (SELECT count(*) FROM fact_orders WHERE batch_id = c.last_batch_id + 1),
       (SELECT count(*) FROM fact_orders WHERE batch_id = c.last_batch_id + 1 AND customer_key = 0),
       (SELECT max(modified_at) FROM stg_orders)
FROM etl_control c;

UPDATE etl_control
SET high_water_mark = (SELECT max(modified_at) FROM stg_orders),
    last_batch_id = last_batch_id + 1
WHERE EXISTS (SELECT 1 FROM stg_orders);

SELECT * FROM fact_orders ORDER BY order_id;
SELECT * FROM etl_batch_log ORDER BY batch_id;
SELECT * FROM error_event;
```

В batch 2 попали три строки: 2, 4 и 5. Fact содержит пять заказов. Заказ 2 имеет сумму 55, дубля нет. Заказ 5 получил ключ 0.
</details>

**3.** Idempotent re-run. Представьте, что загрузка упала после записи в fact, но до обновления HWM. Повторите шаги загрузки fact для тех же данных в `stg_orders`. Покажите, что число строк не изменилось. Потом покажите, что обычный `INSERT` без `DELETE` создал бы дубли.

<details>
<summary>Решение</summary>

```sql
SELECT count(*) AS rows_before FROM fact_orders;

-- повтор: delete по ключу и insert
DELETE FROM fact_orders WHERE order_id IN (SELECT order_id FROM stg_orders);
INSERT INTO fact_orders
SELECT s.order_id, coalesce(d.customer_key, 0), s.order_date, s.amount,
       (SELECT last_batch_id FROM etl_control)
FROM stg_orders s
LEFT JOIN dim_customer d ON d.customer_id = s.customer_id;

SELECT count(*) AS rows_after, count(DISTINCT order_id) AS distinct_orders FROM fact_orders;

-- что было бы без DELETE: проверка на дубли в grain
SELECT count(*) AS rows_if_plain_insert
FROM (
    SELECT order_id FROM fact_orders
    UNION ALL
    SELECT order_id FROM stg_orders
);
```

Было 5 строк, осталось 5. Без `DELETE` стало бы 8 строк, и три заказа дублировались бы.
</details>

**4.** Reconciliation. Сверьте источник и fact: число строк, сумму и построчные расхождения. Затем сверьте `etl_batch_log` с fact.

<details>
<summary>Решение</summary>

```sql
-- итоги источника и хранилища
SELECT 'source' AS side, count(*) AS rows_cnt, sum(amount) AS total FROM src_orders
UNION ALL
SELECT 'fact', count(*), sum(amount) FROM fact_orders;

-- построчные расхождения (должно вернуть 0 строк)
SELECT coalesce(s.order_id, f.order_id) AS order_id, s.amount AS src_amount, f.amount AS fact_amount
FROM src_orders s
FULL OUTER JOIN fact_orders f USING (order_id)
WHERE s.order_id IS NULL OR f.order_id IS NULL OR s.amount <> f.amount;

-- журнал и фактическое число строк по batch
SELECT l.batch_id, l.rows_loaded,
       (SELECT count(*) FROM fact_orders f WHERE f.batch_id = l.batch_id) AS rows_in_fact
FROM etl_batch_log l
ORDER BY l.batch_id;
```

Расхождений нет: 5 строк, сумма 375.00. Но `rows_in_fact` для batch 1 равно 2, а в журнале 3. Заказ 2 из batch 1 был перезаписан в batch 2. Это нормально. Журнал отражает то, что загрузили тогда. Для сверки с источником используйте итоги.
</details>

**5.** Late arriving dimension. В источнике появился клиент `C9`. Добавьте его в `dim_customer` и исправьте строки fact, которые указывали на unknown member.

<details>
<summary>Решение</summary>

```sql
INSERT INTO src_customer VALUES ('C9', 'Мария', 'Омск');

INSERT INTO dim_customer
SELECT (SELECT max(customer_key) FROM dim_customer) + row_number() OVER (ORDER BY customer_id),
       customer_id, name, city
FROM src_customer
WHERE customer_id NOT IN (SELECT customer_id FROM dim_customer WHERE customer_id IS NOT NULL);

-- нужно знать исходный natural key: берём его из источника
UPDATE fact_orders f
SET customer_key = d.customer_key
FROM src_orders s, dim_customer d
WHERE f.customer_key = 0
  AND s.order_id = f.order_id
  AND d.customer_id = s.customer_id;

SELECT f.order_id, f.customer_key, d.name, d.city
FROM fact_orders f
JOIN dim_customer d USING (customer_key)
ORDER BY f.order_id;
```

Заказ 5 теперь указывает на клиента «Мария». Для такого исправления в fact нужен natural key заказа в staging или в источнике. Поэтому хранение сырых данных важно.
</details>

## Вопросы для самопроверки

1. Почему HWM лучше брать из данных, а не из времени запуска?
2. Что значит idempotent load и как `DELETE` перед `INSERT` его обеспечивает?
3. Какие политики есть для строки fact без совпадения в dimension? Какую выбрать?
4. Почему при низкой latency данные менее качественные?
5. Зачем нужна reconciliation, если загрузка завершилась без ошибок?
