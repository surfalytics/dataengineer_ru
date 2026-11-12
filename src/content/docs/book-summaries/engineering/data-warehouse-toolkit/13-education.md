---
title: "The Data Warehouse Toolkit, глава 13: Образование"
head:
  - tag: title
    content: "Accumulating snapshot и factless fact: Kimball | Инжиниринг Данных"
description: "Конспект главы 13 The Data Warehouse Toolkit. Accumulating snapshot для приёма студентов, factless fact table, bridge для преподавателей и практика в DuckDB."
sidebar:
  order: 13
  label: "13. Образование"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** университет — это много небольших процессов. У приёма студентов есть этапы, и для него нужен accumulating snapshot. У регистрации на курс и посещаемости нет чисел, и для них нужен factless fact table. Всё это работает на общих conformed dimensions.

![Registration и attendance: две factless fact-таблицы с общими dimensions и bridge для преподавателей](/assets/data-warehouse-toolkit/ch13-registration-attendance.png)

## Bus matrix университета

Университет похож на много компаний сразу: банк (финансовая помощь), магазин (книги), строитель (здания), фонд (выпускники). Процессы в книге делятся на группы.

| Группа | Примеры процессов |
|---|---|
| Жизненный цикл студента | Приём, финансовая помощь, регистрация на курсы, оценки, активности, пожертвования |
| Финансы | Бюджет, GL, закупки, зарплата |
| Сотрудники | Численность, найм, гранты, публикации |
| Администрирование | Использование помещений, энергия, заявки на ремонт |

Общие dimensions: дата и term, студент, сотрудник, курс, подразделение, помещение, счёт.

## Accumulating snapshot: воронка приёма

Абитуриент проходит этапы. Одна строка в fact — один абитуриент. Строка обновляется при каждом новом этапе.

![Этапы приёма абитуриента и одна обновляемая строка в fact-таблице](/assets/data-warehouse-toolkit/ch13-applicant-pipeline.png)

Свойства accumulating snapshot:

- Одна строка хранит всю историю одного процесса.
- Есть несколько дат: по одной на каждый этап.
- Есть счётчики и длительности между этапами.
- Строки меняются через `UPDATE`. Меняются и foreign keys, и факты.

| Элемент | Как устроен |
|---|---|
| Grain | Один абитуриент |
| Даты | Запрос, визит, заявка, документы собраны, решение, зачисление или отказ |
| Dimensions | Абитуриент, статус заявки, role-playing даты |
| Facts | Счётчики этапов (inquiry count, admit count и так далее), вероятность зачисления |

- Для дат, которые ещё не наступили, нужна «Unknown» строка в `dim_date`. `NULL` в foreign key нельзя.
- Воронка видна сразу: сколько абитуриентов на каждом этапе. По разнице дат видно, где процесс застревает.
- Snapshot не помнит прошлое. Если нужны цифры на дату, например на конец раннего решения, добавьте periodic snapshot или transaction fact.
- Тот же приём работает для грантов: заявка, рассмотрение, одобрение, получение денег.

## Factless fact table

Бывает событие, у которого нет чисел. Fact-таблица состоит только из ключей. Она всё равно полезна: считаем строки.

### Тип 1. Событие

| Событие | Grain |
|---|---|
| Приёмное мероприятие | Один абитуриент на одном мероприятии |
| Регистрация на курс | Один студент на одном курсе в одном term |
| Посещаемость | Один студент на одном занятии |

Для удобства добавляют `registration_count = 1`. Поле не несёт информации, но:

- `sum()` читается проще, чем `count(ключ)`;
- aggregate-таблице нужна настоящая колонка для суммы;
- OLAP-куб требует явный счётчик.

Если появляется настоящая мера (плата, оценка), то таблица уже не factless. Это нормально, если grain тот же.

### Тип 2. Покрытие (coverage)

Событие записывает то, что было. Но иногда нужно знать то, чего не было. Пример: какие помещения не использовались в среду утром?

Решение: строка для каждого помещения на каждый час, независимо от занятости. В таблице есть dimension `utilization_status` (Available, Utilized). Другой вариант — вычитать события из полного списка возможностей.

То же с посещаемостью: «кто записан, но не пришёл». Два варианта:

- Вычесть фактические посещения из ожидаемых (запись × расписание). Так сделано в практике ниже.
- Книга допускает и явные строки для пропусков: `attendance_count` = 1 или 0. Таблица уже не factless. Это работает, потому что у пропуска те же dimensions, а пропусков немного.
- Для продаж так делать нельзя. Строка на каждый некупленный товар со скидкой раздует таблицу.
- OLAP-кубы хорошо показывают «чего не было» без хранения нулей.

## Term dimension

Регистрация имеет grain term, а не день. `dim_term` должна быть conformed с `dim_date`. В календаре каждая дата называет свой term (`Fall 2025`). Названия и значения общих атрибутов должны совпадать буква в букву.

## Студент и изменения

Студент — расширенный абитуриент. Появляются курс, статус обучения, проживание, major, уровень.

| Задача | Решение |
|---|---|
| Нужен профиль на момент регистрации | SCD type 2 |
| Профиль меняется часто (major, класс) | Mini-dimension (type 4) |
| Нужен и исторический, и текущий профиль | Type 7: два ключа в fact, durable key и surrogate key |

## Несколько преподавателей у курса

Курс ведут два преподавателя. На grain регистрации это multivalued dimension. Варианты:

| Вариант | Плюс | Минус |
|---|---|---|
| Изменить grain: студент × курс × преподаватель | Просто | Регистрации считаются дважды |
| Bridge table с `instructor_group_key` | Точно, поддерживает веса | Нужно помнить о перекосе при суммировании |
| Одна строка с именами через запятую | Удобно для подписи | Нет анализа по атрибутам |
| Главный преподаватель в fact | Просто | Теряется остальные |

Если нагрузка делится по правилу, в bridge добавляют `weighting_factor`. Тогда сумма по преподавателям равна общему итогу.

## Ключевые термины

| Термин | Значение |
|---|---|
| Accumulating snapshot | Одна строка на процесс. Обновляется по этапам |
| Factless fact table | Fact-таблица без мер. Только ключи |
| Coverage table | Factless-таблица со всеми возможными событиями. Показывает, чего не было |
| Bridge table | Связь many-to-many между fact и dimension |
| Weighting factor | Доля метрики, которая относится к строке bridge |
| Conformed dimension | Общая dimension с одинаковыми значениями для всех fact |

## Что это значит на практике

- Accumulating snapshot в `dbt` — это incremental-модель с `merge`. Ключом служит id процесса.
- Всегда ставьте дефолтный ключ даты «Unknown» (например, `0`). Тогда inner join не теряет строки.
- Для расчёта «чего не было» держите отдельную таблицу ожидаемых событий. Ищите разницу через `anti join`.
- Bridge опасен. Всегда решайте заранее: нужен ли вес, или отчёт показывает «влияние» (impact) с повторным счётом.
- Не усложняйте. Если в факте есть настоящая мера, добавьте её в ту же таблицу.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
-- dim_date с unknown-строкой и именем term
CREATE TABLE dim_date AS
SELECT 0 AS date_key, NULL::DATE AS full_date, 'Unknown' AS term_name
UNION ALL
SELECT strftime(d, '%Y%m%d')::INT,
       d::DATE,
       CASE WHEN month(d) BETWEEN 9 AND 12 THEN 'Fall 2025'
            WHEN month(d) BETWEEN 1 AND 5  THEN 'Spring 2025'
            ELSE 'Summer 2025' END
FROM generate_series(DATE '2025-01-01', DATE '2025-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_term AS
SELECT * FROM (VALUES
    (1, 'Fall 2025',   '2025-2026'),
    (2, 'Spring 2025', '2024-2025'),
    (3, 'Summer 2025', '2024-2025')
) t(term_key, term_name, academic_year);

CREATE TABLE dim_student AS
SELECT * FROM (VALUES
    (1, 'Анна',    'Data Science', 'Sophomore'),
    (2, 'Борис',   'Economics',    'Junior'),
    (3, 'Вера',    'Data Science', 'Freshman'),
    (4, 'Глеб',    'Math',         'Sophomore'),
    (5, 'Дарья',   'Economics',    'Senior'),
    (6, 'Егор',    'Data Science', 'Junior')
) t(student_key, student_name, major, class_level);

CREATE TABLE dim_instructor AS
SELECT * FROM (VALUES (1, 'Проф. Иванов'), (2, 'Проф. Петрова')) t(instructor_key, instructor_name);

-- bridge: группа 3 это курс с двумя преподавателями, вес 0.5 у каждого
CREATE TABLE bridge_instructor_group AS
SELECT * FROM (VALUES
    (1, 1, 1.0),
    (2, 2, 1.0),
    (3, 1, 0.5),
    (3, 2, 0.5)
) t(instructor_group_key, instructor_key, weighting_factor);

CREATE TABLE dim_course AS
SELECT * FROM (VALUES
    (1, 'SQL basics',    1),
    (2, 'Data modeling', 3),
    (3, 'Statistics',    2)
) t(course_key, course_name, instructor_group_key);

-- factless: одна строка на студента, курс и term
CREATE TABLE fact_course_registration AS
SELECT term_key, student_key, course_key, 1 AS registration_count
FROM (VALUES
    (1, 1, 1), (1, 1, 2),
    (1, 2, 1), (1, 2, 2), (1, 2, 3),
    (1, 3, 1),
    (1, 4, 2), (1, 4, 3),
    (1, 5, 3),
    (1, 6, 1), (1, 6, 2),
    (2, 1, 3), (2, 2, 1)
) t(term_key, student_key, course_key);

-- расписание занятий осенью
CREATE TABLE class_schedule AS
SELECT * FROM (VALUES
    (1, DATE '2025-09-01'), (1, DATE '2025-09-08'),
    (2, DATE '2025-09-02'), (2, DATE '2025-09-09'),
    (3, DATE '2025-09-03'), (3, DATE '2025-09-10')
) t(course_key, class_date);

-- пропуски: студент, курс, дата
CREATE TABLE stg_absence AS
SELECT * FROM (VALUES
    (1, 1, DATE '2025-09-08'),
    (2, 2, DATE '2025-09-09'),
    (2, 3, DATE '2025-09-10'),
    (4, 3, DATE '2025-09-03'),
    (4, 3, DATE '2025-09-10'),
    (6, 1, DATE '2025-09-01')
) t(student_key, course_key, class_date);

-- factless: один студент на одном занятии (если пришёл)
CREATE TABLE fact_attendance AS
SELECT d.date_key, r.student_key, r.course_key, 1 AS attendance_count
FROM fact_course_registration r
JOIN class_schedule cs ON cs.course_key = r.course_key
JOIN dim_date d ON d.full_date = cs.class_date
WHERE r.term_key = 1
  AND NOT EXISTS (
      SELECT 1 FROM stg_absence a
      WHERE a.student_key = r.student_key AND a.course_key = r.course_key AND a.class_date = cs.class_date
  );

-- accumulating snapshot: источник событий
CREATE TABLE stg_applicant_event AS
SELECT * FROM (VALUES
    (1, 'inquiry',        DATE '2025-01-10'), (1, 'visit', DATE '2025-02-05'), (1, 'submitted', DATE '2025-02-20'),
    (1, 'completed',      DATE '2025-03-01'), (1, 'decision_admit', DATE '2025-03-15'), (1, 'enrolled', DATE '2025-04-20'),
    (2, 'inquiry',        DATE '2025-01-12'), (2, 'visit', DATE '2025-02-06'), (2, 'submitted', DATE '2025-02-25'),
    (2, 'completed',      DATE '2025-03-05'), (2, 'decision_deny',  DATE '2025-03-15'),
    (3, 'inquiry',        DATE '2025-01-15'), (3, 'submitted', DATE '2025-02-28'), (3, 'completed', DATE '2025-03-10'),
    (3, 'decision_admit', DATE '2025-03-15'), (3, 'enrolled', DATE '2025-04-10'),
    (4, 'inquiry',        DATE '2025-01-20'), (4, 'visit', DATE '2025-02-10'),
    (5, 'inquiry',        DATE '2025-01-22'), (5, 'visit', DATE '2025-02-12'), (5, 'submitted', DATE '2025-03-01'),
    (5, 'completed',      DATE '2025-03-12'), (5, 'decision_admit', DATE '2025-03-15'),
    (6, 'inquiry',        DATE '2025-02-01'),
    (7, 'inquiry',        DATE '2025-02-03'), (7, 'visit', DATE '2025-03-01'), (7, 'submitted', DATE '2025-03-08'),
    (7, 'completed',      DATE '2025-03-14'),
    (8, 'inquiry',        DATE '2025-02-10'), (8, 'submitted', DATE '2025-03-02'), (8, 'completed', DATE '2025-03-09'),
    (8, 'decision_admit', DATE '2025-03-15')
) t(applicant_key, stage, event_date);

CREATE TABLE dim_application_status AS
SELECT * FROM (VALUES
    (1, 'Inquiry'), (2, 'Submitted'), (3, 'File completed'),
    (4, 'Admitted'), (5, 'Denied'), (6, 'Enrolled')
) t(application_status_key, application_status);

CREATE MACRO date_key_or_unknown(d) AS coalesce(strftime(d, '%Y%m%d')::INT, 0);

-- grain: один абитуриент. Нет события, значит ключ 0 (Unknown)
CREATE TABLE fact_applicant_pipeline AS
SELECT
    applicant_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage = 'inquiry'))   AS inquiry_date_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage = 'visit'))     AS visit_date_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage = 'submitted')) AS submitted_date_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage = 'completed')) AS completed_date_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage LIKE 'decision%')) AS decision_date_key,
    date_key_or_unknown(min(event_date) FILTER (WHERE stage = 'enrolled'))  AS enrolled_date_key,
    CASE WHEN count(*) FILTER (WHERE stage = 'enrolled') > 0       THEN 6
         WHEN count(*) FILTER (WHERE stage = 'decision_deny') > 0  THEN 5
         WHEN count(*) FILTER (WHERE stage = 'decision_admit') > 0 THEN 4
         WHEN count(*) FILTER (WHERE stage = 'completed') > 0      THEN 3
         WHEN count(*) FILTER (WHERE stage = 'submitted') > 0      THEN 2
         ELSE 1 END AS application_status_key
FROM stg_applicant_event
GROUP BY applicant_key;
```

### Шаг 2. Проверяем

```sql
-- 8 абитуриентов, ни одного NULL в ключах дат
SELECT count(*) AS applicants,
       count(*) FILTER (WHERE visit_date_key IS NULL OR decision_date_key IS NULL) AS null_keys
FROM fact_applicant_pipeline;

-- регистраций осенью должно быть 11
SELECT sum(registration_count) AS fall_registrations
FROM fact_course_registration WHERE term_key = 1;

-- conformed: каждая осенняя дата называет term так же, как dim_term
SELECT count(*) AS fall_days FROM dim_date d JOIN dim_term t USING (term_name) WHERE t.term_key = 1;
```

### Задания

**1.** Регистрации осенью по курсам. Покажите, что `count(*)` и `sum(registration_count)` дают одно число. Затем найдите студентов, записанных на два курса и больше.

<details>
<summary>Решение</summary>

```sql
SELECT c.course_name,
       count(*)                    AS rows_count,
       sum(r.registration_count)   AS registrations
FROM fact_course_registration r
JOIN dim_course c USING (course_key)
JOIN dim_term t USING (term_key)
WHERE t.term_name = 'Fall 2025'
GROUP BY c.course_name
ORDER BY registrations DESC;

SELECT s.student_name, count(*) AS courses
FROM fact_course_registration r
JOIN dim_student s USING (student_key)
WHERE r.term_key = 1
GROUP BY s.student_name
HAVING count(*) > 1
ORDER BY courses DESC, s.student_name;
```
</details>

**2.** Регистрации по преподавателям через bridge. Посчитайте два числа: без весов (impact) и с весами. Итог с весами должен равняться 11.

<details>
<summary>Решение</summary>

```sql
SELECT i.instructor_name,
       count(*)                                          AS registrations_impact,
       round(sum(r.registration_count * b.weighting_factor), 2) AS registrations_weighted
FROM fact_course_registration r
JOIN dim_course c USING (course_key)
JOIN bridge_instructor_group b USING (instructor_group_key)
JOIN dim_instructor i USING (instructor_key)
WHERE r.term_key = 1
GROUP BY i.instructor_name
ORDER BY i.instructor_name;
```

Без весов сумма равна 15, а регистраций 11. Курс Data modeling посчитан у двух преподавателей. С весами сумма равна 11.
</details>

**3.** Посещаемость. Для каждого курса найдите ожидаемые занятия (записанные студенты × расписание), фактические и долю посещения. Затем найдите студентов, которые пропустили все занятия курса.

<details>
<summary>Решение</summary>

```sql
WITH expected AS (
    SELECT r.course_key, r.student_key, count(*) AS expected_sessions
    FROM fact_course_registration r
    JOIN class_schedule cs USING (course_key)
    WHERE r.term_key = 1
    GROUP BY ALL
), actual AS (
    SELECT course_key, student_key, sum(attendance_count) AS attended
    FROM fact_attendance
    GROUP BY ALL
)
SELECT c.course_name,
       sum(e.expected_sessions)                     AS expected,
       coalesce(sum(a.attended), 0)                 AS attended,
       round(coalesce(sum(a.attended), 0) / sum(e.expected_sessions), 2) AS attendance_rate
FROM expected e
LEFT JOIN actual a USING (course_key, student_key)
JOIN dim_course c USING (course_key)
GROUP BY c.course_name
ORDER BY attendance_rate;

-- студенты без единого посещения курса (anti join)
SELECT s.student_name, c.course_name
FROM (SELECT DISTINCT student_key, course_key FROM fact_course_registration WHERE term_key = 1) r
LEFT JOIN (SELECT DISTINCT student_key, course_key FROM fact_attendance) a USING (student_key, course_key)
JOIN dim_student s USING (student_key)
JOIN dim_course c USING (course_key)
WHERE a.student_key IS NULL;
```

Глеб пропустил оба занятия по Statistics. Таких строк нет в `fact_attendance`, поэтому их видно только через список ожидаемых занятий.
</details>

**4.** Воронка приёма. Сколько абитуриентов дошло до каждого этапа? Какая средняя задержка в днях от запроса до заявки? Используйте два role-playing alias для `dim_date`.

<details>
<summary>Решение</summary>

```sql
SELECT count(*)                                               AS inquiries,
       count(*) FILTER (WHERE visit_date_key <> 0)            AS visits,
       count(*) FILTER (WHERE submitted_date_key <> 0)        AS submitted,
       count(*) FILTER (WHERE completed_date_key <> 0)        AS completed,
       count(*) FILTER (WHERE decision_date_key <> 0)         AS decided,
       count(*) FILTER (WHERE enrolled_date_key <> 0)         AS enrolled
FROM fact_applicant_pipeline;

SELECT round(avg(ds.full_date - di.full_date), 1) AS avg_days_inquiry_to_submitted
FROM fact_applicant_pipeline f
JOIN dim_date di ON di.date_key = f.inquiry_date_key
JOIN dim_date ds ON ds.date_key = f.submitted_date_key
WHERE f.submitted_date_key <> 0;
```
</details>

**5.** Обновление строки. Абитуриент 7 получил решение о приёме 20 марта 2025. Обновите его строку в accumulating snapshot. Потом покажите статусы всех абитуриентов.

<details>
<summary>Решение</summary>

```sql
INSERT INTO stg_applicant_event VALUES (7, 'decision_admit', DATE '2025-03-20');

UPDATE fact_applicant_pipeline
SET decision_date_key = 20250320,
    application_status_key = 4
WHERE applicant_key = 7;

SELECT s.application_status, count(*) AS applicants
FROM fact_applicant_pipeline f
JOIN dim_application_status s USING (application_status_key)
GROUP BY s.application_status
ORDER BY min(s.application_status_key);
```

Строка не добавилась, а изменилась. Так и работает accumulating snapshot.
</details>

## Вопросы для самопроверки

1. Какие три признака отличают accumulating snapshot от transaction fact?
2. Зачем в factless fact table нужен `registration_count = 1`?
3. Как найти студентов, которые записаны на курс, но ни разу не пришли?
4. Когда в bridge для преподавателей нужен weighting factor, а когда его лучше не добавлять?
