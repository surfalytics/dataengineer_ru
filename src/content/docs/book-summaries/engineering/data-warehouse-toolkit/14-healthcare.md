---
title: "The Data Warehouse Toolkit, глава 14: Здравоохранение"
head:
  - tag: title
    content: "Bridge table для диагнозов, claims: Kimball | Инжиниринг Данных"
description: "Конспект главы 14 The Data Warehouse Toolkit. Claims как accumulating snapshot, bridge для диагнозов, measurement type dimension и практика в DuckDB."
sidebar:
  order: 14
  label: "14. Здравоохранение"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в здравоохранении у одного события часто много значений одной dimension: у визита несколько диагнозов. Для них нужен `bridge table`. Счёт на лечение (claim) проходит этапы с датами, поэтому его хранят как `accumulating snapshot`, где одна `dim_date` играет несколько ролей.

## О чём глава

[Глава 13](/book-summaries/engineering/data-warehouse-toolkit/13-education/) показала `accumulating snapshot` на приёме студентов. Глава 14 применяет его к медицинским счетам и добавляет приёмы для диагнозов, анализов, текста и изображений.

Основные темы:

- bus matrix и общие dimensions;
- claims как `accumulating snapshot`, даты в ролях;
- диагнозы: `multivalued dimension` и `bridge table`;
- `supertype` и `subtype` для счетов;
- анализы, текст и изображения из электронных записей;
- койки и оборудование, запоздавшие данные.

![Схема star schema для claim line: fact-таблица, даты в разных ролях, bridge для диагнозов и пациент с историей версий](/assets/data-warehouse-toolkit/ch14-claims-star.png)

В центре стоит `fact_claim_line`: вокруг него даты в четырёх ролях, пациент с версиями, врач, процедура и диагнозы через bridge. Схема упрощена: в книге у claim восемь дат.

## Кейс здравоохранения и bus matrix

Организации хотят лучше лечить и работать эффективнее, поэтому им нужно связать клинические и административные данные из разных систем. Фрагмент `bus matrix` делит процессы на три группы: клинические события (визиты, процедуры, лекарства, анализы), счета и выручка (счета стационара и поликлиники, claims, оплаты, списания) и операционные события (койки, помещения, материалы, расписание персонала).

Данные о пациенте бывают двух видов. Административные — это счета от врача, клиники, больницы или лаборатории. Клиническая карта шире: услуги, анализы, рецепты, заметки и назначения врача. Плательщики (`payer`, то есть страховые) исторически анализировали данные лучше провайдеров (больниц, клиник, врачей), потому что claims лучше структурированы. Но в claims нет подробной клинической картины, поэтому страховые всё чаще работают с провайдерами, а их задачи сближаются.

Правила `conformed dimension` (общая dimension для всех процессов) те же, что в других отраслях. Самая важная — пациент: книга считает 360-degree view из [главы 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/) для пациента ещё важнее, и к нему стремятся электронные медицинские записи (`EMR`, `EHR`). Среди других общих dimensions: дата, ответственная сторона (`responsible party`), работодатель, план страхования, плательщик, врач, процедура, диагноз, учреждение.

Одни dimensions собрать трудно, другие проще, чем кажется:

- **Пациент — трудный случай.** В США нет надёжного национального номера и единого идентификатора пациента для всех учреждений. Закон `HIPAA` строго защищает конфиденциальность данных.
- **Диагнозы и процедуры — проще.** Их содержание задают страховые и государство: диагнозы кодирует `ICD`, процедуры — `HCPCS` на основе `CPT`, у стоматологов есть `CDT`.

Операционные процессы книга не разбирает заново: приёмы те же, что в главах про [HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/), [склад](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/) и [закупки](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/).

## Claims: счета и оплаты

Биллинговой службе нужны выставленные суммы по всем dimensions, доля неполученных оплат, срок оплаты и статус неоплаченных claims.

### Выбор grain

Как в [главе 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/), есть три варианта `grain`:

- `transaction`: каждый счёт и каждая оплата. Нужен рядом как дополнение;
- `periodic snapshot`: не подходит. Он хорош для долгих рядов (банковские счета, страховые полисы), но не для коротких процессов вроде заказов и claims;
- `accumulating snapshot`: подходит, книга выбирает его.

Одна строка fact — одна строка медицинского счёта (`claim line`). Она хранит историю от создания до текущего состояния и обновляется при каждом изменении. Стандартный сценарий включает восемь дат: лечение; счёт первичной страховой, вторичной страховой и ответственной стороне; последняя оплата каждой из трёх сторон; нулевой баланс.

![Этапы claim: лечение, счета трём сторонам, последние оплаты и нулевой баланс как даты одной строки fact](/assets/data-warehouse-toolkit/ch14-claim-workflow.png)

Необычные случаи (несколько оплат на строку, одна оплата на несколько claims) snapshot не описывает. Для них рядом нужны transaction-таблицы. Задача snapshot — поставить каждый claim в стандартную рамку.

В строке есть dimensions (пациент, ответственная сторона, врач и его организация, процедура, учреждение, основной диагноз, две страховые, работодатель) и `master bill ID` как `degenerate dimension`: номер счёта прямо в fact. Facts: выставленная сумма, оплаты трёх сторон, общая оплата и остаток (вычисляются), коллекшн, списание. Есть и lags: число дней от счёта до первой оплаты и до нулевого баланса.

Строка появляется при первых счетах. Пока часть этапов не наступила, date keys не могут быть `NULL`: они указывают на строку `dim_date` «To Be Determined». Дальше строку обновляют при каждой оплате. Это усложняет работу DBA: когда строки перестают меняться, реорганизация таблицы освобождает место. Партиции по дате лечения сохраняются хорошо, потому что эта дата не меняется.

## Role-playing dimensions: даты и не только

Восемь foreign keys к датам нельзя соединять с одним экземпляром `dim_date`. Книга советует создать восемь view над одной таблицей и переименовать в них колонки, чтобы BI показывал понятные названия.

> **Пояснение:** при одном экземпляре SQL потребовал бы, чтобы все этапы пришлись на один день. Вместо view можно взять alias, как в задании 3 ниже.

Роли бывают и у других dimensions: первичная и вторичная страховая, а также врач (направивший, лечащий, консультирующий).

## Multivalued dimension: диагнозы

В момент процедуры у пациента один или несколько диагнозов, и организации хотят хранить их все вместе с финансовыми данными. Три колонки `diagnosis_1..3` не подходят: диагнозы не независимые роли, их бывает больше трёх (до 20 у пожилого пациента в больнице), а BI-запрос не знает, какую колонку фильтровать.

Решение: в fact лежит `diagnosis_group_key`, он соединён many-to-many с `bridge table`, где по строке на каждый диагноз в группе. Bridge ведёт к `dim_diagnosis`. Если модельный инструмент требует связь FK → PK, между fact и bridge вставляют таблицу `diagnosis_group`.

Новую группу на каждый визит не создают: строк станет астрономически много, а многие группы совпадут. В `ETL` набор диагнозов ищут в таблице групп и создают новую группу, только если готовой нет (см. [главу 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)). Если группа меняется за время лечения, в bridge добавляют даты начала и конца ([глава 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/)).

### Веса: нужны ли они

В [главе 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) `weighting factor` распределял метрики по строкам bridge. Для диагнозов вклад каждого почти невозможно определить, кроме основного. Поэтому анализ отвечает на вопросы о влиянии: «Какова общая сумма счетов по процедурам с застойной сердечной недостаточностью?» Это `impact analysis`, он считает суммы повторно. Книга советует: если бизнес не согласен с правилом весов, их не добавляют.

## Supertype и subtype для счетов

Счета стационара (`facility charges`) и врачей в клинике (`professional charges`) разные, как в паре `supertype` и `subtype` из [главы 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/). Для больницы схему claim расширяют:

- врач в двух ролях, `admitting` и `attending`, с организацией для каждой;
- две группы диагнозов: при поступлении (известна сразу) и при выписке (известна позже);
- для сложной операции (пересадка сердца) в fact лежит главный врач, остальных команда связывает через group key и bridge.

## Электронные медицинские записи

Организации переходят с бумаги на электронные записи, и это сильно влияет на DW/BI. Данные трудны из-за огромной вариативности и объёма: числа, текст, изображения. Неструктурированные данные разобраны в [главе 21](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/); книга считает записи классическим случаем для big data.

## Measurement type dimension: sparse facts

Колонка на каждый анализ даёт много `NULL`. Книга предлагает `measurement type dimension`: она описывает, что значит строка fact, и хранит единицу измерения и ограничения аддитивности. В fact остаётся одна колонка `observed_value`.

Плюс: новый тип измерения — это новая строка в dimension, а `NULL` нет. Минусы: `grain` растёт до «одна строка на измерение», и 10 чисел дают 10 строк; сравнить два числа из одного события можно только по двум строкам; все числа лежат в одной колонке, и несовместимые легко смешать. Для очень разреженных данных (клиническая лаборатория) это разумно. Когда данные плотные, возвращаются к обычным колонкам. `OLAP cubes` (кубы) проще считают между типами.

> **Пояснение:** в практике ниже в `dim_measurement_type` есть ещё нормальный диапазон. Это наше дополнение.

## Свободный текст

Заметки врача аналитически слабы, но пользователи не отдают их. В fact текст не кладут: он тратит место и замедляет обычные запросы. Называть его `degenerate dimension` неправильно: так называют номера операционных документов. Выбор зависит от кардинальности. Если почти у каждого события свой текст, он становится атрибутом transaction-dimension. Если многие события без комментария или с повторами, нужна отдельная dimension комментариев с FK в fact. Запросы с текстом и метриками работают медленно, поэтому текст обычно открывают после селективных фильтров.

## Изображения

Изображение хранят как имя JPEG-файла в fact или как blob в базе. Файл открывают другие программы, но хранилище файлов нужно держать синхронным с fact.

## Использование коек и оборудования

Как в [главе 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/), есть три варианта:

- `periodic snapshot`: статус каждой койки в регулярные моменты (в полночь, в начале смены). Это `factless fact table`, fact без числовых метрик;
- `transaction fact table`: строка на каждое движение койки (занята, освобождена). Для операционных статусов больше: до операции, после, простой;
- `timespan fact table` ([глава 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/)): строки с началом и концом состояния, если изменения редкие (койки в реабилитации).

## Retroactive changes: запоздавшие данные

Обычно описания (пациент, врач, плательщик) меняются как `SCD`. Но в здравоохранении часто приходят запоздавшие данные: процедура недельной давности или профиль, обновлённый задним числом. Чем позже запись, тем сложнее `ETL` ([глава 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)). Книга пишет, что это, возможно, основной режим загрузки, а не редкий выброс.

## Итоги главы

- Здравоохранение связывает клинические и административные данные, главная общая dimension — пациент.
- Claim line хранят как `accumulating snapshot`, а восемь дат — это роли одной `dim_date`.
- Необычные оплаты хранят в transaction-таблицах рядом.
- Диагнозы — это `multivalued dimension` через `bridge table`, а не через несколько колонок. Группы используют повторно.
- `Weighting factor` для диагнозов почти нельзя обосновать, поэтому анализ идёт как `impact analysis`.
- `Measurement type dimension` подходит для очень разреженных данных. Для плотных возвращаются к колонкам.
- Текст не кладут в fact: нужна comments dimension или атрибут transaction-dimension.
- Запоздавшие данные здесь обычный режим, и ETL должен принимать их как норму.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Claim line` | Одна строка медицинского счёта |
| `Accumulating snapshot` | Строка с историей процесса, её обновляют на каждом этапе |
| `Role-playing dimension` | Одна dimension в нескольких ролях, например восемь дат |
| `Multivalued dimension` | У события несколько значений dimension, например диагнозы |
| `Bridge table` | Связь many-to-many: строка на каждое значение в группе |
| `Weighting factor` | Доля метрики для строки bridge |
| `Impact analysis` | Отчёт без весов: каждое значение получает всю сумму |
| `Measurement type dimension` | Dimension с описанием измерения: единица, аддитивность |

## Что это значит на практике

- Начните с вопроса: «Что такое одна строка fact?» Для claims это одна строка счёта, а не визит.
- Не допускайте `NULL` в date keys: заведите строку «To Be Determined» в `dim_date`.
- Для ролей дат создавайте view. Рядом со snapshot держите transaction-таблицу оплат.
- Проверяйте `sum(weighting_factor)` по группе: должна быть 1. Отчёт без весов подписывайте как «impact».
- В ETL ищите готовую группу диагнозов, не создавайте новую на каждый визит.
- Не кладите текст врача в fact. Проверьте, как часто приходят запоздавшие данные.
- SCD type 2 в `dim_patient` показывает профиль на момент лечения. Для «текущего профиля» нужен `durable key` (см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)).
- В `dbt` accumulating snapshot — это incremental-модель с `merge` по id строки счёта.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_date AS
SELECT 0 AS date_key, NULL::DATE AS full_date
UNION ALL
SELECT strftime(d, '%Y%m%d')::INT, d::DATE
FROM generate_series(DATE '2025-01-01', DATE '2025-06-30', INTERVAL 1 DAY) t(d);

CREATE MACRO date_key_or_unknown(d) AS coalesce(strftime(d, '%Y%m%d')::INT, 0);

-- SCD type 2: patient_id это durable key, patient_key это surrogate key версии
CREATE TABLE dim_patient AS
SELECT * FROM (VALUES
    (1, 'P1', 'Анна',  'Москва', 'Basic',   DATE '2024-01-01', DATE '2025-03-14', false),
    (2, 'P1', 'Анна',  'Казань', 'Basic',   DATE '2025-03-15', DATE '9999-12-31', true),
    (3, 'P2', 'Борис', 'Москва', 'Basic',   DATE '2024-01-01', DATE '9999-12-31', true),
    (4, 'P3', 'Вера',  'Самара', 'Basic',   DATE '2024-01-01', DATE '2025-04-30', false),
    (5, 'P3', 'Вера',  'Самара', 'Premium', DATE '2025-05-01', DATE '9999-12-31', true)
) t(patient_key, patient_id, patient_name, city, plan, valid_from, valid_to, is_current);

CREATE TABLE dim_physician AS
SELECT * FROM (VALUES
    (1, 'Д-р Смирнов', 'Cardiology'),
    (2, 'Д-р Орлова',  'Endocrinology'),
    (3, 'Д-р Кузнецов','General')
) t(physician_key, physician_name, specialty);

CREATE TABLE dim_procedure AS
SELECT * FROM (VALUES
    (1, 'Consultation',     'Evaluation'),
    (2, 'ECG',              'Diagnostics'),
    (3, 'Blood test',       'Lab'),
    (4, 'Echocardiography', 'Diagnostics')
) t(procedure_key, procedure_name, category);

CREATE TABLE dim_diagnosis AS
SELECT * FROM (VALUES
    (1, 'I50.9', 'Heart failure'),
    (2, 'I10',   'Hypertension'),
    (3, 'E11.9', 'Type 2 diabetes'),
    (4, 'N18',   'Chronic kidney disease'),
    (5, 'J45',   'Asthma')
) t(diagnosis_key, icd_code, diagnosis_name);

-- bridge: группа диагнозов; вес группы суммируется в 1
CREATE TABLE bridge_diagnosis_group AS
SELECT * FROM (VALUES
    (1, 1, 0.6, true),
    (1, 2, 0.4, false),
    (2, 3, 1.0, true),
    (3, 3, 0.5, true),
    (3, 2, 0.3, false),
    (3, 4, 0.2, false),
    (4, 5, 1.0, true)
) t(diagnosis_group_key, diagnosis_key, weighting_factor, is_primary);

-- источник: claim lines (NULL = события ещё не было)
CREATE TABLE stg_claim_line AS
SELECT * FROM (VALUES
    (1, 1, 1, 1, 1, DATE '2025-02-10', 200, DATE '2025-02-12', 160, DATE '2025-02-28',  40, DATE '2025-03-10'),
    (2, 1, 1, 2, 1, DATE '2025-02-10', 300, DATE '2025-02-12', 240, DATE '2025-02-28',  60, DATE '2025-03-20'),
    (3, 2, 1, 4, 1, DATE '2025-04-02', 500, DATE '2025-04-04', 400, DATE '2025-04-25',   0, NULL),
    (4, 3, 2, 3, 2, DATE '2025-03-01', 120, DATE '2025-03-03',  96, DATE '2025-03-20',  24, DATE '2025-04-01'),
    (5, 3, 2, 1, 3, DATE '2025-04-15', 220, DATE '2025-04-17', NULL, NULL,               0, NULL),
    (6, 4, 3, 1, 4, DATE '2025-03-20',  90, DATE '2025-03-22',  72, DATE '2025-04-05',  18, DATE '2025-04-20'),
    (7, 5, 3, 1, 4, DATE '2025-05-10',  90, DATE '2025-05-12',  90, DATE '2025-05-30',   0, DATE '2025-05-30'),
    (8, 3, 2, 2, 3, DATE '2025-05-05', 350, DATE '2025-05-07', 280, DATE '2025-05-27',   0, NULL)
) t(claim_line_id, patient_key, physician_key, procedure_key, diagnosis_group_key,
    treatment_date, billed_amount, primary_bill_date, primary_paid_amount, primary_pay_date,
    responsible_paid_amount, zero_balance_date);

-- grain: одна строка счёта (claim line). Неизвестные даты = ключ 0
CREATE TABLE fact_claim_line AS
SELECT
    claim_line_id, patient_key, physician_key, procedure_key, diagnosis_group_key,
    date_key_or_unknown(treatment_date)    AS treatment_date_key,
    date_key_or_unknown(primary_bill_date) AS primary_bill_date_key,
    date_key_or_unknown(primary_pay_date)  AS primary_pay_date_key,
    date_key_or_unknown(zero_balance_date) AS zero_balance_date_key,
    billed_amount,
    coalesce(primary_paid_amount, 0)    AS primary_paid_amount,
    responsible_paid_amount,
    billed_amount - coalesce(primary_paid_amount, 0) - responsible_paid_amount AS unpaid_balance
FROM stg_claim_line;

-- sparse facts: одна строка на одно измерение
CREATE TABLE dim_measurement_type AS
SELECT * FROM (VALUES
    (1, 'Hemoglobin', 'g/dL',  12.0, 16.0),
    (2, 'Glucose',    'mg/dL', 70.0, 100.0),
    (3, 'LDL',        'mg/dL',  0.0, 130.0)
) t(measurement_type_key, measurement_name, unit, normal_low, normal_high);

CREATE TABLE fact_lab_result AS
SELECT * FROM (VALUES
    ('E1', 1, 20250210, 1, 13.1), ('E1', 1, 20250210, 2,  98.0),
    ('E2', 3, 20250301, 1, 14.2), ('E2', 3, 20250301, 2, 160.0), ('E2', 3, 20250301, 3, 140.0),
    ('E3', 4, 20250320, 1, 11.0),
    ('E4', 5, 20250510, 2, 110.0), ('E4', 5, 20250510, 3,  90.0)
) t(lab_event_id, patient_key, date_key, measurement_type_key, observed_value);
```

### Шаг 2. Проверяем

```sql
-- веса в каждой группе должны давать 1
SELECT diagnosis_group_key, round(sum(weighting_factor), 2) AS weight_sum
FROM bridge_diagnosis_group
GROUP BY diagnosis_group_key
ORDER BY diagnosis_group_key;

-- 8 claim lines. Общая сумма выставленного равна 1 870
SELECT count(*) AS claim_lines, sum(billed_amount) AS billed FROM fact_claim_line;
```

### Задания

**1.** Выставлено по диагнозам. Сначала без весов (impact), потом с весами. Сравните итоги с общей суммой 1 870.

<details>
<summary>Решение</summary>

```sql
SELECT d.diagnosis_name,
       sum(f.billed_amount)                           AS billed_impact,
       round(sum(f.billed_amount * b.weighting_factor), 2) AS billed_weighted
FROM fact_claim_line f
JOIN bridge_diagnosis_group b USING (diagnosis_group_key)
JOIN dim_diagnosis d USING (diagnosis_key)
GROUP BY d.diagnosis_name
ORDER BY billed_weighted DESC;
```

Итог impact-колонки больше 1 870, потому что одна строка счёта попадает в несколько диагнозов. Итог взвешенной колонки равен 1 870.

Веса здесь учебные. Книга предупреждает: в медицине правило весов почти никогда нельзя обосновать. На практике чаще используют impact-отчёт или только основной диагноз (задание 2).
</details>

**2.** Только основной диагноз. Получите ещё один отчёт без перекоса: используйте `is_primary`. Итог должен быть 1 870.

<details>
<summary>Решение</summary>

```sql
SELECT d.diagnosis_name,
       count(*)             AS claim_lines,
       sum(f.billed_amount) AS billed
FROM fact_claim_line f
JOIN bridge_diagnosis_group b USING (diagnosis_group_key)
JOIN dim_diagnosis d USING (diagnosis_key)
WHERE b.is_primary
GROUP BY d.diagnosis_name
ORDER BY billed DESC;
```
</details>

**3.** Accumulating snapshot. Найдите открытые claim lines (нулевой баланс не наступил). Посчитайте возраст долга на 2025-06-01 и средний срок от счёта до первой оплаты. Используйте role-playing alias для `dim_date`.

<details>
<summary>Решение</summary>

```sql
-- открытые счета и возраст
SELECT f.claim_line_id, f.unpaid_balance,
       DATE '2025-06-01' - b.full_date AS days_since_billing
FROM fact_claim_line f
JOIN dim_date b ON b.date_key = f.primary_bill_date_key
WHERE f.zero_balance_date_key = 0
ORDER BY days_since_billing DESC;

-- средний lag от счёта до оплаты
SELECT round(avg(p.full_date - b.full_date), 1) AS avg_days_bill_to_payment
FROM fact_claim_line f
JOIN dim_date b ON b.date_key = f.primary_bill_date_key
JOIN dim_date p ON p.date_key = f.primary_pay_date_key
WHERE f.primary_pay_date_key <> 0;
```

Строка 5 ещё не оплачена. Её даты оплаты равны 0 (Unknown), и она не входит во второй запрос.
</details>

**4.** SCD type 2. Покажите выставленную сумму по городу пациента на момент лечения. Потом по текущему городу (через durable key `patient_id`). Сравните.

<details>
<summary>Решение</summary>

```sql
-- город на момент лечения (ключ версии в fact)
SELECT p.city AS city_at_treatment, sum(f.billed_amount) AS billed
FROM fact_claim_line f
JOIN dim_patient p USING (patient_key)
GROUP BY p.city
ORDER BY billed DESC;

-- текущий город (durable key)
SELECT cur.city AS current_city, sum(f.billed_amount) AS billed
FROM fact_claim_line f
JOIN dim_patient p   ON p.patient_key = f.patient_key
JOIN dim_patient cur ON cur.patient_id = p.patient_id AND cur.is_current
GROUP BY cur.city
ORDER BY billed DESC;
```

Анна переехала из Москвы в Казань. Первые счета остаются за Москвой в первом отчёте и переходят в Казань во втором.
</details>

**5.** Sparse facts. Покажите результаты анализов, вне нормы (`measurement_type` хранит диапазон). Потом соберите по каждому событию одну строку: колонки для гемоглобина и глюкозы.

<details>
<summary>Решение</summary>

```sql
-- вне нормы
SELECT r.lab_event_id, p.patient_name, m.measurement_name, r.observed_value, m.unit
FROM fact_lab_result r
JOIN dim_measurement_type m USING (measurement_type_key)
JOIN dim_patient p USING (patient_key)
WHERE r.observed_value NOT BETWEEN m.normal_low AND m.normal_high
ORDER BY r.lab_event_id, m.measurement_name;

-- одна строка на событие
SELECT r.lab_event_id,
       max(r.observed_value) FILTER (WHERE m.measurement_name = 'Hemoglobin') AS hemoglobin,
       max(r.observed_value) FILTER (WHERE m.measurement_name = 'Glucose')    AS glucose
FROM fact_lab_result r
JOIN dim_measurement_type m USING (measurement_type_key)
GROUP BY r.lab_event_id
ORDER BY r.lab_event_id;
```

Не складывайте `observed_value` без `measurement_type`. Единицы разные.
</details>

## Вопросы для самопроверки

1. Почему для claims выбрали accumulating snapshot, а не transaction fact или periodic snapshot? Что остаётся за transaction-таблицами?
2. Чем bridge table для диагнозов лучше трёх колонок `diagnosis_1..3`?
3. Когда weighting factor нужен, а когда его лучше не добавлять? Что тогда показывает отчёт?
4. Какие минусы у measurement type dimension? Когда лучше вернуться к обычным колонкам?
5. Почему свободный текст нельзя хранить в fact как degenerate dimension? От чего зависит выбор между comments dimension и transaction-dimension?
6. Почему нельзя соединить все даты claim с одним экземпляром `dim_date`? Как это решить?

Предыдущая: [Глава 13. Образование](/book-summaries/engineering/data-warehouse-toolkit/13-education/). Следующая: [Глава 15. Электронная коммерция](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/).
