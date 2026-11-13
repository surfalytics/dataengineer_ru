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

**Главная мысль:** `accumulating snapshot` следит за коротким процессом с этапами, например за приёмом абитуриентов: одна строка обновляется на каждом этапе. `factless fact table` хранит события без чисел, например регистрацию на курс. Она помогает считать события и находить то, чего не было.

## О чём глава

[Глава 12](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/) показала несколько fact-таблиц с разным `grain` для одного процесса. Эта глава добавляет два других типа на примере университета. `accumulating snapshot` книга уже использовала для склада ([глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)) и заказов ([глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). `factless fact table` она вводила в [главе 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) для акций.

- Bus matrix университета.
- Воронка приёма и заявок на гранты как `accumulating snapshot`.
- `factless fact table` для событий (приём, регистрация, посещаемость) и для покрытия (помещения).
- Term, студент с изменениями, несколько преподавателей у курса.
- Как анализировать события, которых не было.

![Схема: две factless fact-таблицы (регистрация на курс и посещаемость) с общими dimensions студента, курса и даты, dimension term и bridge для преподавателей](/assets/data-warehouse-toolkit/ch13-registration-attendance.png)

Как читать схему: вверху две таблицы событий со счётчиком, всегда равным 1; они делят dimensions студента и курса, а преподаватели подключены к курсу через bridge.

## Bus matrix университета

Один клиент сказал, что университет похож на небольшую деревню: он ведёт все нужные ей виды бизнеса. Это жильё, столовые, книжный магазин, финансовая помощь, эндаумент, здания, клиника. Раньше образование мало смотрело на выручку и прибыль. Из-за роста расходов и конкуренции теперь так нельзя. Университет хочет понимать, что студенты «покупают» (какие курсы берут в каждый term), каких результатов достигают, и хочет поддерживать связь с ними после выпуска.

| Группа процессов | Примеры |
|---|---|
| Жизненный цикл студента | Приём, финансовая помощь, регистрация на курсы, активности, пожертвования выпускников |
| Финансы | Бюджет, эндаумент, GL, зарплата, закупки |
| Сотрудники | Численность, найм, воронка заявок на гранты, публикации |
| Администрирование | Использование помещений, энергия, заявки на ремонт |

Общие `conformed dimension` матрицы: дата и term, абитуриент (студент, выпускник), сотрудник, курс, подразделение, помещение, счёт.

## Accumulating snapshot fact tables

В главе 4 книга назвала признаки `accumulating snapshot`:

- одна строка хранит всю историю одного экземпляра процесса;
- несколько дат отмечают стандартные этапы;
- факты включают счётчики статусов и длительности между этапами;
- строку обновляют при каждом изменении: меняются и foreign keys, и факты.

### Воронка приёма абитуриентов (Applicant Pipeline)

Абитуриент проходит этапы: запрос, визит в кампус, подача заявки, сбор документов, уведомление о решении, зачисление или выход (withdraw). Аналитики хотят знать, сколько абитуриентов на каждом этапе. Книга сравнивает это с воронкой: запросов много, до конца доходит гораздо меньше. Та же схема подходит для найма и продаж.

`grain` — одна строка на абитуриента. Это самый детальный уровень, который известен при входе в воронку.

![Этапы приёма абитуриента и одна обновляемая строка в fact-таблице](/assets/data-warehouse-toolkit/ch13-applicant-pipeline.png)

Каждая дата этапа — `role-playing dimension`: одна `dim_date` подключена несколько раз под разными ролями. По датам видно темп движения и узкие места. Для этапов, которые ещё не наступили, книга советует default surrogate key.

> **Пояснение:** для этого в `dim_date` держат строку `Unknown`. Тогда foreign key не равен `NULL`, и `inner join` не теряет абитуриентов без этапа.

Dimension абитуриента хранит географию, баллы тестов, школу, предварительный major и источник заявки. Эти срезы помогают приёмной комиссии менять стратегию. Факты — счётчики этапов и решений (admit, waitlist, deny, enroll). Если данные есть, добавляют вероятности подачи заявки и зачисления для прогноза.

### Альтернативные схемы для воронки приёма

`accumulating snapshot` подходит для коротких процессов с чётким началом и концом. Но строки обновляются, поэтому таблица не хранит число абитуриентов на важные даты, например на дату раннего решения. Эти числа проверяют очень внимательно. Книга предлагает хранить snapshots на ключевых датах или построить `transaction fact table` приёма: одна строка на транзакцию абитуриента.

### Воронка заявок на гранты (Research Grant Proposal Pipeline)

Заявка на грант идёт от предварительного предложения до одобрения и получения денег. Можно считать заявки на каждом этапе и долю успешных по преподавателю, подразделению, теме и источнику финансирования.

## Factless fact tables

Обычная fact-таблица имеет от 5 до примерно 20 foreign keys и числовые, желательно аддитивные факты. Числа оправдывают таблицу, а ключи определяют место измерения. У некоторых процессов чисел нет. Тогда fact-таблица состоит только из ключей: это `factless fact table`. Книга показывает два вида: таблицы событий (приём, регистрация, посещаемость) и таблицы покрытия (помещения).

### Admissions events: события приёма

Таблица хранит факт, что абитуриент побывал на мероприятии: ярмарке колледжей, собеседовании с выпускником, ночёвке в кампусе. В fact лежат ключи даты, term зачисления, абитуриента, его статуса, сотрудника комиссии и мероприятия.

### Course registrations: регистрация на курсы

`grain` — одна строка на курс, на который студент записался в term. Числового факта нет, поэтому анализ строится на подсчёте строк. Например: сколько студентов записалось к преподавателю за три года или сколько студентов-инженеров взяли курс по финансам.

### Term dimension

Регистрация имеет `grain` term, а не день. `dim_term` должна быть `conformed` с календарём: каждая дата называет term (`Fall`), term с годом (`Fall 2013`) и учебный год (`2013-2014`). Названия и значения общих атрибутов должны совпадать полностью.

### Student dimension и отслеживание изменений

Dimension студента расширяет dimension абитуриента: к данным приёма добавляются данные кампуса, например проживание, major и курс обучения. Многие хотят следить за изменениями major, курса и завершения учёбы. Книга предлагает два пути из [главы 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/):

- `mini-dimension` (SCD type 4) для часто меняющихся атрибутов;
- SCD type 7, если нужен и профиль на момент регистрации, и срез по текущим данным. В fact два ключа: `surrogate key` (type 2) и `durable key` (view с текущей строкой).

### Artificial count metric: искусственный счётчик

В factless-таблице можно считать любой ключ: `count(term_key)`. SQL считает ключи, а не уникальные значения. Это путает, поэтому дизайнеры добавляют факт `registration_count`, всегда равный 1. Запрос становится понятнее: `sum(registration_count)`. Кроме того, aggregate-таблице нужна настоящая колонка для суммы, а в OLAP-кубе обычно нужен явный счётчик. Если появляется настоящая мера (плата за обучение, оценки), её можно добавить, если она подходит к `grain`. Но тогда таблица уже не factless.

### Несколько преподавателей у курса

У курса с несколькими преподавателями атрибут `multivalued`. Книга предлагает четыре варианта.

| Вариант | Минус |
|---|---|
| Добавить преподавателя в `grain` | Неестественный `grain`, регистрации завышаются |
| `bridge table` с `instructor_group_key` | Риск завысить сумму |
| Имена через разделитель в dimension курса | Нет анализа по характеристикам преподавателей |
| Главный преподаватель как один foreign key | Остальных не видно |

В bridge одна строка на преподавателя, который ведёт курс один, и две строки на команду с общим group key. Если нагрузка поделена чётко, добавляют `weighting_factor` ([глава 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/)).

> **Пояснение:** если веса в группе дают в сумме 1, сумма по преподавателям равна общему числу регистраций. Без весов регистрация курса с двумя преподавателями считается дважды.

### Course registration periodic snapshots

Некоторым пользователям нужны `periodic snapshot` на ключевые даты: предварительная регистрация, начало term, срок отказа от курсов, конец term. Тогда `grain` — одна строка на курс студента в term на дату snapshot.

### Facility utilization: таблица покрытия

Руководству нужно знать, какие помещения используют сильнее всего и падает ли загрузка по пятницам. Это второй вид: таблица покрытия, `coverage`. В fact одна строка на помещение на каждый часовой блок каждого дня недели в term, независимо от того, используют помещение или нет. Статус (`Available` или `Utilized`) хранит отдельная dimension.

> **Пояснение:** другой способ — хранить только события и вычитать их из списка возможных. Так сделана посещаемость в практике ниже.

### Student attendance: посещаемость

`grain` — одна строка на студента, который пришёл на занятие в этот день. Счёт идёт по дате, а не по term. Таблица показывает, какие курсы посещают чаще и у каких посещаемость за term падает меньше.

### Explicit rows: явные строки для того, что не произошло

Чтобы найти записанных студентов, которые не пришли, в fact добавляют строки для пропусков: `attendance_count` равен 1 или 0. Здесь это допустимо. У пропуска те же dimensions, а прогульщиков немного. В других случаях книга называет такой подход нелепым: нельзя добавлять в покупку строки для акционных товаров, которые покупатель не взял.

### OLAP-кубы и то, чего не было

OLAP-кубы хорошо показывают то, чего не было: они справляются с разреженностью и не хранят явные нули. Книга оговаривает, что это верно для не слишком разреженных кубов.

## Другие задачи аналитики университета

Кроме платы за обучение, главные источники дохода — исследовательские гранты и пожертвования выпускников.

- **Гранты.** Это финансовый анализ из [главы 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/) на уровне subledger, с dimensions: источник финансирования, тема, срок и исследователь. Цель — сравнивать бюджет и расходы, избегать излишка и дефицита.
- **Выпускники.** Их понимают как клиентов ([глава 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/)): география, работа, интересы и данные студенческих лет. Это помогает адресовать сообщения. Книга советует записывать в CRM все контакты с выпускниками.

## Итоги главы

- `accumulating snapshot` хранит одну строку на экземпляр процесса, несколько дат этапов и обновляется при каждом изменении.
- Он подходит для коротких процессов с чётким началом и концом, но встречается реже других типов и часто дополняется ими.
- Он не хранит состояние на прошлую дату, поэтому для ключевых дат нужны snapshots или `transaction fact table`.
- Для ещё не наступивших этапов нужен default surrogate key.
- `factless fact table` хранит только ключи и бывает двух видов: событие и покрытие.
- Счётчик, равный 1, делает SQL понятнее и нужен для aggregate-таблиц и OLAP-кубов.
- `dim_term` должна быть `conformed` с `dim_date`.
- Для нескольких преподавателей книга предлагает четыре варианта, среди них bridge с весами.
- То, чего не было, показывают таблица покрытия, явные строки с нулём или OLAP-куб.

## Ключевые термины

| Термин | Значение |
|---|---|
| `accumulating snapshot` | Одна строка на процесс, обновляется по этапам |
| `factless fact table` | Fact-таблица только с ключами, без мер |
| Coverage table | Factless-таблица со всеми возможными событиями |
| `role-playing dimension` | Одна dimension под разными ролями, например даты этапов |
| `bridge table` | Связь many-to-many между fact и dimension |
| `weighting_factor` | Доля метрики, которая относится к строке bridge |

## Что это значит на практике

- Accumulating snapshot в `dbt` — это incremental-модель с `merge`. Ключом служит id процесса.
- Держите в `dim_date` строку «Unknown» (например, с ключом `0`). Тогда `inner join` не теряет строки.
- Для расчёта «чего не было» держите таблицу ожидаемых событий и ищите разницу через `anti join`.
- `count(key)` не считает уникальные значения. Для уникальных студентов нужен `count(distinct student_key)`.
- Решайте заранее: нужен ли вес в bridge, или отчёт показывает «влияние» (impact) с повторным счётом.

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

1. Чем `accumulating snapshot` отличается от `transaction fact table`? Почему он не отвечает на вопрос «сколько заявок было на дату раннего решения» и что для этого добавить?
2. Зачем в `factless fact table` нужен `registration_count = 1`, если он не несёт информации?
3. Как найти студентов, которые записаны на курс, но ни разу не пришли? Когда допустимо хранить явные строки с `attendance_count = 0`, а когда нет?
4. Когда в bridge для преподавателей нужен `weighting_factor`, а когда его лучше не добавлять?
5. Почему `dim_term` должна быть `conformed` с `dim_date`? Что сломается, если названия term в них различаются?
6. Чем таблица покрытия отличается от таблицы событий и когда она нужна?

Предыдущая: [Глава 12. Транспорт](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/). Следующая: [Глава 14. Здравоохранение](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/).
