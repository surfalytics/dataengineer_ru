---
title: "The Data Warehouse Toolkit, глава 9: HR"
head:
  - tag: title
    content: "Моделирование HR: SCD, иерархии, skills | Инжиниринг Данных"
description: "Конспект главы 9 The Data Warehouse Toolkit: employee dimension с SCD2, headcount snapshot, иерархия руководителей, bridge для навыков. Практика в DuckDB."
sidebar:
  order: 9
  label: "9. HR"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в HR многое решает одна широкая employee dimension с историей профиля (SCD type 2). Она сама отвечает на вопросы вроде «сколько было сотрудников на дату и какие у них были профили». Численность по месяцам хранит periodic snapshot, а каждый HR-процесс получает свою fact table. Иерархию руководителей и навыки книга раскладывает по `bridge table` или упрощает.

## О чём глава

Глава отвечает на вопрос: как хранить кадровые данные, чтобы видеть историю сотрудника, численность и подчинение. В [главе 8. CRM](/book-summaries/engineering/data-warehouse-toolkit/08-crm/) была широкая customer dimension с историей. Здесь та же идея работает для сотрудников. 

Главные темы:

- employee dimension с историей и граница между dimension и fact;
- headcount `periodic snapshot` и `bus matrix` HR;
- готовые модели вендоров;
- иерархия руководителей и `bridge table`;
- навыки как multivalued атрибут;
- опросы и текстовые комментарии.

![Модель HR для практики: события и снимок численности, employee dimension с историей, bridge для иерархии руководителей и навыков](/assets/data-warehouse-toolkit/ch09-hr-star.png)

Это наша учебная модель для практики ниже, а не рисунок из книги. Обе fact table ссылаются на версию профиля через `employee_key`. Два bridge внизу связаны с сотрудником через постоянный `employee_id`.

## Профиль сотрудника: employee dimension с историей

Авторы предупреждают: после многих глав легко привыкнуть, что всю работу делает fact table с аддитивными числами. В HR иначе. Хорошая employee dimension сама поддерживает много метрик.

Профиль сотрудника в большой компании содержит минимум 100 атрибутов: дату найма, job grade, зарплату, оценки, подразделение, адрес. Людей постоянно нанимают, переводят и повышают. Бизнес хочет точно отслеживать эти изменения.

Первая мысль — `transaction fact table`: строка на каждое изменение профиля. Чисел у них нет, поэтому fact `factless`. Employee dimension ведут как SCD type 2: каждое изменение даёт новую строку. Тогда в fact и в dimension одинаковое число строк. Книга называет это тревожным сигналом: fact table не должна быть такой же большой, как её dimension.

Решение книги — убрать эту fact table и усилить dimension:

- Каждая строка хранит профиль сразу после изменения.
- Тип транзакции становится атрибутом `change_reason`.
- Первичный ключ — `surrogate key`. Идентификатор из HR-системы (`employee_id`) лежит в строке как атрибут. Это `durable key` (книга называет его durable natural key): он общий для всех версий.
- Числовой атрибут, по которому считают суммы, а не только фильтруют, живёт в fact table.

### Точные effective и expiration даты

Две колонки задают период, когда профиль верен. Приём описан в [главе 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/). Если данные грузят чаще раза в сутки, нужны date/time: в 9 утра и в 9 вечера профиль может быть разным.

- У текущей строки expiration стоит в будущем.
- Когда ETL видит новый профиль, он ставит expiration старой строки «чуть раньше» effective новой: на предыдущий день, минуту или секунду.
- Если сотрудник вернулся к прежнему профилю, вставьте новую строку. Не правьте старую: две строки окажутся действующими одновременно.
- `current row indicator` быстро находит последний статус. ETL снимает его со старой строки.

Выберите момент и условие «>= effective и строго < expiration»: получите всех сотрудников и их профили на этот момент.

### Change reason: причина изменения

`change_reason` кладёт метаданные ETL в сами данные. В поле пишут код или название каждого изменившегося атрибута. Вопрос «сколько человек сменили индекс» сводится к `WHERE change_reason LIKE '%ZIP%'`. Если меняется сразу несколько атрибутов, причина multivalued. Книга предлагает строку с разделителями (`|Last Name|ZIP|`) или bridge. Оба приёма разобраны ниже в разделе про навыки.

Источник может записывать изменение микротранзакциями по одному атрибуту. Делать из них отдельные type 2 версии бессмысленно. Лучше свести их в одну «супертранзакцию», например повышение. Найти такие группы трудно, поэтому надёжнее, когда HR-система сама записывает действие целиком.

### Изменения профиля: type 2 или события в fact

Некоторые дизайнеры кладут в type 2 все изменения сотрудника. Для компании в 100 000 человек dimension тогда растёт до миллионов строк. Зато в любую fact table можно класть ключ версии, действовавшей в момент события.

Но маятник можно качнуть слишком далеко. Не заводите версию на каждую оценку, участие в льготах или курс обучения. В этих событиях участвуют свои dimensions: дата, организация, льгота, проверяющий, причина ухода. Поэтому книга советует отдельные fact tables по процессам. Многие из них factless, но по ним считают события и тренды.

Результат события, например grade после повышения, кладут в employee dimension как атрибут. Ошибка — добавлять в неё много внешних ключей на outriggers (проверяющий, льгота, причина ухода). Dimension перегружается.

## Headcount: periodic snapshot численности

Менеджерам нужны регулярные отчёты: число сотрудников, зарплата, дни отпуска, новые сотрудники, повышения. Часть этих чисел трудно получить из одной employee dimension.

Для этого книга предлагает `periodic snapshot`. `Grain` — один сотрудник за один месяц. Dimensions: месяц, сотрудник, организация.

- Ключ сотрудника ведёт на версию, действовавшую в конце последнего дня месяца.
- Меры: число сотрудников, найм, переводы, повышения, зарплата, сверхурочные, дни отпуска (начислено, взято, баланс).

Все меры `additive`, кроме балансов. Баланс отпуска `semi-additive`: его суммируют по другим dimensions, а по месяцам усредняют.

### Bus matrix для HR-процессов

Employee dimension и месячный снимок — только начало. Книга даёт предварительную `bus matrix` (таблицу процессов и общих dimensions) и тип fact table для каждого процесса.

| Тип fact table | HR-процессы из книги |
|---|---|
| `periodic snapshot` | позиции сотрудников, право на льготы |
| `accumulating snapshot` | заявка на вакансию, процесс оценки |
| `transaction fact table` | найм, компенсации, пройденные курсы, увольнение |

Многие процессы, например право на льготы, дают factless fact tables.

> **Пояснение:** в практике ниже мы упрощаем. Найм, повышение, перевод и увольнение лежат в одной `fact_employee_event`. У снимка нет organization dimension: отдел берём из employee dimension.

## Готовые решения и модели от вендоров

К готовой HR-системе часто идёт add-on для DW/BI, а другие вендоры продают стандартные модели данных. Их аргумент: так быстрее и безопаснее, ведь везде одни процессы — найм, льготы, оплата, оценка, увольнение.

Книга признаёт, что общее есть, но у каждого бизнеса свои особенности. Чтобы продукт можно было настроить, вендоры добавляют абстракции: таблицу `party` с ролями и общие названия колонок. Менеджерам вне HR такой словарь звучит как чужой язык.

Второй риск — интеграция. Если dimensions вендорской модели нельзя привести к `conformed dimensions` (общим справочникам компании), модель станет ещё одним изолированным набором данных.

Готовая модель помогает увидеть основные процессы и общие dimensions. Но то же понимание дают несколько недель работы с бизнес-пользователями, и это привяжет их к проекту. Высокая цена не гарантирует качества: в некоторых стандартных моделях есть типичные ошибки dimensional modeling.

## Рекурсивные иерархии сотрудников

Частая характеристика сотрудника — его руководитель. Если нужно только имя, это атрибут employee dimension. Если больше, начинается `recursive hierarchy`: руководитель сам является сотрудником. Книга показывает два способа связи.

| Способ | Как работает | Цена |
|---|---|---|
| Ключ руководителя в fact | Второй ключ на `role-playing dimension`: ту же employee dimension в роли «manager» | Два ключа в каждой fact table, где нужны отчёты по руководителям |
| Ключ руководителя в employee dimension | Ключ лежит в строке сотрудника и ведёт на outrigger в роли «manager» | Риск каскада версий (см. ниже) |

`Role-playing dimension` — одна физическая dimension, которая играет в схеме разные роли под разными названиями. Первый способ связывает сотрудника и руководителя при вставке строки в fact. BI одинаково быстро фильтрует по атрибутам сотрудника или руководителя.

### Отслеживание изменений во встроенном ключе руководителя

Пример. Abby — руководитель Hayden. Если у Hayden сменился руководитель и нужна история, ключ руководителя ведут как type 2, и Hayden получает новую строку.

Теперь Abby остаётся руководителем, но у неё меняется адрес (type 2). У Abby новая строка и новый ключ. Если ключ руководителя у Hayden тоже type 2, новая строка появляется и у него. Пусть Abby — CEO: одно изменение в её профиле размножит строки всех сотрудников.

Книга советует сначала уточнить бизнес-правило: нужна ли история профилей руководителей? Если нет, храните в строке сотрудника `durable key` руководителя и связывайте его с dimension, где только текущие строки руководителей. Ключ type 1 всегда связывает сотрудника с текущим руководителем. История теряется, но это может полностью подойти.

### Подъём и спуск по иерархии руководителей

Ключ в строке сотрудника подходит для связи «многие к одному» с фиксированной глубиной. Для всей цепочки руководителей или всех подчинённых нужны другие приёмы.

- В `OLAP cube` встроенного ключа может хватить: популярные OLAP-продукты умеют parent/child hierarchy переменной глубины.
- В реляционной базе нужен Oracle `CONNECT BY` или `recursive CTE`. Книга считает оба способа почти непригодными для пользователя BI-инструмента.
- Остаётся `bridge table`, как в [главе 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/). В ней одна строка на пару «руководитель — сотрудник в его цепочке» (прямой и косвенный), плюс строка «руководитель сам себе». Ещё в ней хранят число уровней от вершины.

У bridge есть минусы. Её трудно строить, в ней много строк, и запросы могут быть медленными. Для ad hoc запросов в BI она сложна, а чтобы агрегировать вверх, нужно развернуть join. Если руководитель и сотрудник ведутся как type 2, bridge быстро растёт.

Книга предлагает такой выход:

- Кладите в bridge `durable keys` вместо ключей версий.
- Если нужна история подчинения, добавьте даты действия связи. Новые строки тогда появляются при смене подчинения, а не при любом type 2 изменении.
- Такую bridge труднее запрашивать, поэтому авторы советуют спрятать её в готовых BI-приложениях, а прямой доступ дать только power users.
- Подходят и другие приёмы из главы 7, например `pathstring` (путь от вершины одной строкой).

«Серебряной пули» нет, пишут авторы.

> **Пояснение:** в практике ниже bridge строит `recursive CTE` из текущей таблицы `employee_manager` на постоянном `employee_id`, без дат.

## Multivalued skill keyword: навыки сотрудников

Пример: ИТ-отделу нужно добавить в employee dimension навыки: языки, ОС, СУБД. Это ключевые слова сотрудника, и по ним нужен поиск.

Если навыков конечное число, каждый можно сделать атрибутом, например `Linux` со значениями «Linux skills» и «No Linux skills». Такие позиционные атрибуты быстрые и простые. Но подход ломается, когда навыков становится много.

### Skill keyword bridge

Реально у сотрудника непредсказуемое число навыков, и новые появляются регулярно. Это multivalued dimension. Книга показывает две логически равные схемы. Первая — `bridge table`:

- Employee dimension хранит `skill group key`. Одна группа — один набор навыков.
- Все, кто знает Oracle, Unix и SQL, получают один group key. В bridge для него три строки, по одной на навык.
- Bridge связывает группу со skills dimension.

В [главе 14](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/) похожая bridge соединена напрямую с fact table.

### Дилемма AND/OR

OR-запрос («Unix или Linux») прост: одно условие OR по названию навыка. AND-запрос («Unix и Linux») сложен. Условие нужно проверить по двум строкам dimension, а SQL плохо справляется с этим.

Книга решает это через `UNION` и `INTERSECT`: по запросу на навык. `UNION` даёт сотрудников с любым навыком, `INTERSECT` — с обоими. Такой код советуют прятать в специальный интерфейс.

> **Пояснение:** то же даёт `GROUP BY employee_id HAVING count(DISTINCT skill_name) = 2`. Так сделано в практике. Там bridge проще: она связывает сотрудника и навык напрямую, без `skill group key`.

### Skill keyword как текстовая строка

Второй путь убирает many-to-many bridge. В employee dimension (или в outrigger) хранят одну строку со всеми навыками.

- Разделитель, например вертикальную черту, ставят в начале и после каждого навыка: `|Unix|C++|`.
- Если наборы навыков часто повторяются, строки выносят в outrigger. Если нет, строку кладут прямо в dimension.
- Строку приводят к верхнему регистру, чтобы UNIX, Unix и unix совпали: `UPPER` (в книге `UCase`).

Тогда AND и OR пишутся одним `SELECT` одной формы: условия `UPPER(skill_list) LIKE '%|UNIX|%'` соединяют через `OR` или `AND`. Разделитель нужен, чтобы находить точное слово и не получать ложных совпадений.

> **Пояснение:** без разделителей `LIKE '%SQL%'` найдёт и `NoSQL`.

Приём работает в любой реляционной БД. Цена: нельзя посчитать сотрудников по каждому навыку.

## Данные опросов и анкет

HR собирает опросы сотрудников, особенно оценки коллег и руководителей, и считает средний рейтинг оцениваемого и отдела. `Grain` fact table — один вопрос в анкете одного респондента. Dimensions:

- employee в двух ролях: отвечающий и оцениваемый;
- date в двух ролях: дата отправки и дата получения;
- survey: название, тип, цель, год анкеты;
- question: текст и категория вопроса. Один вопрос обычно задают в нескольких опросах;
- response category: например «благоприятный» или «враждебный».

В fact также лежат номер анкеты (`degenerate dimension`) и ответ. Схема подходит и для опросов клиентов.

## Текстовые комментарии

Fact хранит числа, а атрибут dimension берёт значение из дискретного списка. Куда класть замечание руководителя или свободный ответ в опросе? Инженеры хотят выбросить такой текст, но бизнес может потребовать его оставить. Сначала проверьте, что бизнес правда не откажется от текста. Потом посмотрите, можно ли разобрать комментарии на атрибуты, например «похвала» и «жалоба». Обычно нужен и полный текст.

Соблазн — положить текст в fact как ещё один `degenerate dimension`. Книга отвечает: комментарий под это не подходит. Он раздувает fact table.

Книга советует хранить комментарии вне fact table:

- Если комментарии повторяются (хотя бы «No comment») и уникальных меньше, чем событий, заведите `comments dimension` с ключом в fact.
- Если у каждого события свой комментарий, сделайте его атрибутом dimension того же grain, что и транзакция.

Join с такой большой dimension будет медленным. Но читают комментарии после сильной фильтрации, а обычные анализы метрик не несут лишнего веса.

## Итоги главы

- Employee dimension с SCD type 2, точными датами и `change_reason` сама отвечает на многие HR-вопросы.
- Factless fact «изменение профиля» дублирует dimension по числу строк. Книга советует её убрать.
- Оценки, льготы и обучение получают свои fact tables. В dimension остаётся только результат события.
- Headcount `periodic snapshot` имеет grain «сотрудник x месяц». Баланс отпуска semi-additive: по месяцам его усредняют.
- Готовая вендорская модель помогает начать, но приносит абстракции и риск изолированных данных.
- Ключ руководителя как type 2 размножает версии: изменение у CEO затрагивает всех. Выход — `durable key` руководителя или type 1.
- Для иерархии переменной глубины нужна `bridge table`, лучше на durable keys и с датами связи. Простого решения нет.
- Навыки хранят в bridge с `skill group key` или в строке с разделителями. Строка упрощает AND/OR, но не даёт считать по навыкам.
- Комментарии выносят из fact в comments dimension или в атрибут transaction dimension.

## Ключевые термины

| Термин | Значение |
|---|---|
| `durable key` | Постоянный идентификатор сотрудника, общий для всех версий |
| Effective / expiration date | Границы периода, когда версия профиля верна |
| `change_reason` | Атрибут с причиной появления версии |
| Recursive hierarchy | Дерево, где руководитель сам сотрудник |
| Role-playing dimension | Одна dimension в разных ролях: сотрудник, руководитель |
| Bridge table | Таблица связей для иерархии или many-to-many |
| `skill group key` | Ключ набора навыков: одна группа, много строк в bridge |

## Что это значит на практике

- Для as-of запроса («кем он был 15 мая») ищите версию, чей период содержит дату. Для date/time книга пишет «>= effective и < expiration». В практике ниже даты и `BETWEEN`: expiration равен последнему дню версии.
- Не считайте сотрудников по `count(*)` из dimension: версий больше, чем людей. Считайте `count(DISTINCT employee_id)`.
- Fact table грузите с ключом версии на момент события. Bridge строят на `employee_id`.
- Сводите микроизменения источника в одну версию. Не ведите ключ руководителя как type 2 без явного правила.
- Прячьте bridge иерархии за готовым отчётом или представлением.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём employee dimension, события, снимок, bridge

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d AS full_date
FROM generate_series(DATE '2020-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

-- SCD type 2: версия = период с одинаковым профилем. change_reason = почему появилась версия
CREATE TABLE dim_employee AS
SELECT * FROM (VALUES
    (1,  1, 'Анна',  'CEO',              'Руководство', DATE '2020-01-01', DATE '9999-12-31', 'Приём'),
    (2,  2, 'Борис', 'Head of Data',     'Data',        DATE '2022-01-01', DATE '2024-05-31', 'Приём'),
    (3,  2, 'Борис', 'Director of Data', 'Data',        DATE '2024-06-01', DATE '9999-12-31', 'Повышение'),
    (4,  3, 'Вера',  'Head of Sales',    'Sales',       DATE '2021-03-01', DATE '9999-12-31', 'Приём'),
    (5,  4, 'Глеб',  'Analyst',          'Data',        DATE '2023-03-01', DATE '2024-03-31', 'Приём'),
    (6,  4, 'Глеб',  'Senior Analyst',   'Data',        DATE '2024-04-01', DATE '9999-12-31', 'Повышение'),
    (7,  5, 'Дина',  'Engineer',         'Data',        DATE '2023-06-01', DATE '9999-12-31', 'Приём'),
    (8,  6, 'Егор',  'Engineer',         'Data',        DATE '2024-02-01', DATE '2024-08-31', 'Приём'),
    (9,  6, 'Егор',  'Engineer',         'Sales',       DATE '2024-09-01', DATE '9999-12-31', 'Перевод'),
    (10, 7, 'Жанна', 'Sales Manager',    'Sales',       DATE '2022-05-01', DATE '9999-12-31', 'Приём'),
    (11, 8, 'Зина',  'Sales Rep',        'Sales',       DATE '2023-01-01', DATE '2024-09-30', 'Приём')
) t(employee_key, employee_id, employee_name, job_title, department, effective_date, expiration_date, change_reason);

CREATE TABLE dim_event_type AS
SELECT * FROM (VALUES (1,'hire'),(2,'promotion'),(3,'transfer'),(4,'termination')) t(event_type_key, event_type);

-- grain: одно кадровое событие. employee_key = версия после события
CREATE TABLE fact_employee_event AS
SELECT employee_key, strftime(event_date, '%Y%m%d')::INT AS event_date_key, event_type_key, annual_salary
FROM (VALUES
    (1,  DATE '2020-01-01', 1, 300000),
    (2,  DATE '2022-01-01', 1, 150000),
    (3,  DATE '2024-06-01', 2, 200000),
    (4,  DATE '2021-03-01', 1, 140000),
    (5,  DATE '2023-03-01', 1,  80000),
    (6,  DATE '2024-04-01', 2,  95000),
    (7,  DATE '2023-06-01', 1,  90000),
    (8,  DATE '2024-02-01', 1,  85000),
    (9,  DATE '2024-09-01', 3,  85000),
    (10, DATE '2022-05-01', 1,  90000),
    (11, DATE '2023-01-01', 1,  60000),
    (11, DATE '2024-09-30', 4,  60000)
) t(employee_key, event_date, event_type_key, annual_salary);

-- grain: один сотрудник x конец месяца 2024. Берём версию, действующую в этот день
CREATE TABLE fact_headcount_snapshot AS
SELECT strftime(m.month_end, '%Y%m%d')::INT AS month_end_key, e.employee_key, 1 AS headcount
FROM (SELECT last_day(d) AS month_end
      FROM generate_series(DATE '2024-01-01', DATE '2024-12-01', INTERVAL 1 MONTH) t(d)) m
JOIN dim_employee e
  ON m.month_end BETWEEN e.effective_date AND e.expiration_date;

-- иерархия руководителей (текущая) и bridge
CREATE TABLE employee_manager AS
SELECT * FROM (VALUES
    (1, NULL), (2, 1), (3, 1), (4, 2), (5, 2), (6, 4), (7, 3), (8, 3)
) t(employee_id, manager_id);

CREATE TABLE bridge_management AS
WITH RECURSIVE r AS (
    SELECT employee_id AS manager_id, employee_id, 0 AS depth FROM employee_manager
    UNION ALL
    SELECT r.manager_id, em.employee_id, r.depth + 1
    FROM r JOIN employee_manager em ON em.manager_id = r.employee_id
)
SELECT * FROM r;

CREATE TABLE dim_skill AS
SELECT * FROM (VALUES (1,'SQL'),(2,'Python'),(3,'dbt'),(4,'Переговоры'),(5,'Excel')) t(skill_key, skill_name);

CREATE TABLE bridge_employee_skill AS
SELECT * FROM (VALUES
    (2,1),(2,3),(4,1),(4,5),(5,1),(5,2),(5,3),(6,1),(6,2),
    (3,4),(7,4),(7,5),(8,4)
) t(employee_id, skill_key);
```

### Шаг 2. Проверяем

```sql
-- у каждого employee_id версии не пересекаются: должно вернуть 0 строк
SELECT a.employee_id, a.employee_key, b.employee_key AS overlap_with
FROM dim_employee a
JOIN dim_employee b
  ON a.employee_id = b.employee_id AND a.employee_key < b.employee_key
 AND a.effective_date <= b.expiration_date AND b.effective_date <= a.expiration_date;

SELECT count(*) AS versions, count(DISTINCT employee_id) AS employees FROM dim_employee;
```

### Задания

**1.** Численность по месяцам и по отделам. Используйте `fact_headcount_snapshot`. Покажите декабрь и сентябрь.

<details>
<summary>Решение</summary>

```sql
SELECT s.month_end_key, e.department, sum(s.headcount) AS headcount
FROM fact_headcount_snapshot s
JOIN dim_employee e USING (employee_key)
WHERE s.month_end_key IN (20240930, 20241231)
GROUP BY ALL
ORDER BY s.month_end_key, e.department;
```

В сентябре Егор уже в Sales. В декабре нет Зины: она ушла 30 сентября, но в сентябрьский снимок ещё входит.
</details>

**2.** As-of запрос. Кем был каждый сотрудник на 15 мая 2024 года, и кем он стал сейчас? Не используйте `is_current`.

<details>
<summary>Решение</summary>

```sql
SELECT a.employee_name,
       a.job_title AS title_on_may_15,
       a.department AS dept_on_may_15,
       n.job_title AS title_now
FROM dim_employee a
LEFT JOIN dim_employee n
  ON n.employee_id = a.employee_id AND n.expiration_date = DATE '9999-12-31'
WHERE DATE '2024-05-15' BETWEEN a.effective_date AND a.expiration_date
ORDER BY a.employee_name;
```

У Зины `title_now` равен `NULL`: у неё нет текущей версии, она уволилась.
</details>

**3.** Повышения и зарплата. Для каждого повышения покажите новую зарплату и рост в процентах к прошлой зарплате этого сотрудника.

<details>
<summary>Решение</summary>

```sql
SELECT e.employee_name, t.event_type, f.event_date_key, f.annual_salary,
       round(100.0 * (f.annual_salary - lag(f.annual_salary) OVER w)
             / lag(f.annual_salary) OVER w, 1) AS raise_pct
FROM fact_employee_event f
JOIN dim_employee e USING (employee_key)
JOIN dim_event_type t USING (event_type_key)
WINDOW w AS (PARTITION BY e.employee_id ORDER BY f.event_date_key)
QUALIFY t.event_type = 'promotion'
ORDER BY e.employee_name;
```

Окно считается по всем событиям. `QUALIFY` оставляет только повышения. Это даёт процент к предыдущей зарплате.
</details>

**4.** Иерархия. Для каждого руководителя покажите размер команды без него самого. Прямые подчинённые и все уровни отдельно.

<details>
<summary>Решение</summary>

```sql
SELECT m.employee_name AS manager,
       count(*) FILTER (WHERE b.depth = 1) AS direct_reports,
       count(*) FILTER (WHERE b.depth >= 1) AS whole_team
FROM bridge_management b
JOIN (SELECT DISTINCT employee_id, employee_name FROM dim_employee) m
  ON m.employee_id = b.manager_id
GROUP BY m.employee_name
HAVING count(*) FILTER (WHERE b.depth >= 1) > 0
ORDER BY whole_team DESC;
```

У Анны вся команда — 7 человек. Она видит и сотрудников уровнем ниже.
</details>

**5.** Навыки. Найдите сотрудников, у которых есть и SQL, и dbt. Покажите все их навыки одной строкой.

<details>
<summary>Решение</summary>

```sql
SELECT n.employee_name,
       string_agg(s.skill_name, ', ' ORDER BY s.skill_name) AS skills
FROM bridge_employee_skill b
JOIN dim_skill s USING (skill_key)
JOIN (SELECT DISTINCT employee_id, employee_name FROM dim_employee) n USING (employee_id)
WHERE b.employee_id IN (
    SELECT b2.employee_id
    FROM bridge_employee_skill b2
    JOIN dim_skill s2 USING (skill_key)
    WHERE s2.skill_name IN ('SQL', 'dbt')
    GROUP BY b2.employee_id
    HAVING count(DISTINCT s2.skill_name) = 2
)
GROUP BY n.employee_name
ORDER BY n.employee_name;
```
</details>

**6.** Change reason. Сколько изменений профиля каждого типа было в 2024 году? Используйте только `dim_employee`, без fact.

<details>
<summary>Решение</summary>

```sql
SELECT change_reason, count(*) AS changes
FROM dim_employee
WHERE effective_date BETWEEN DATE '2024-01-01' AND DATE '2024-12-31'
GROUP BY change_reason
ORDER BY changes DESC;
```

Два повышения (Борис, Глеб), один приём (Егор), один перевод (Егор). Увольнение Зины видно по `expiration_date`, а не по новой версии.
</details>

## Вопросы для самопроверки

1. Почему у одного сотрудника много строк в employee dimension? Как считать людей, а не версии?
2. Почему книга советует убрать factless fact «изменение профиля»? Когда отдельная fact table для HR-события всё же нужна?
3. Что случится, если ключ руководителя в строке сотрудника ведётся как type 2, а руководитель — CEO? Какие есть два выхода?
4. Зачем нужен bridge для иерархии руководителей, если есть `manager_id`? Почему в bridge лучше использовать durable keys и даты действия связи?
5. Чем headcount snapshot отличается от employee dimension? Как правильно агрегировать баланс отпуска?
6. Как найти сотрудников с двумя навыками сразу? Когда строка с разделителями лучше bridge, а когда хуже?

Предыдущая: [Глава 8. CRM](/book-summaries/engineering/data-warehouse-toolkit/08-crm/). Следующая: [Глава 10. Финансовые услуги](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/).
