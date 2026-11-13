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

**Главная мысль:** `ETL` — «скрытая часть айсберга» проекта хранилища. Сложности спрятаны в источниках, поэтому работа занимает больше времени, чем ждут. Авторы делят её на 10 шагов и разделяют историческую загрузку (её можно останавливать и проверять руками) и инкрементальную (она идёт сама).

## О чём глава

[Глава 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/) перечислила 34 подсистемы ETL. Эта глава показывает порядок работ по шагам. Совет подходит и для ETL tool, и для ручного кода.

- План, спецификация, sandbox.
- Историческая загрузка dimensions и facts.
- Инкремент, агрегаты, автоматизация.
- Real-time и цена низкой latency.

![Инкрементальный ETL: staging, quality screens, dimensions SCD 1 и 2, surrogate key pipeline, fact table, audit и обновление high-water mark](/assets/data-warehouse-toolkit/ch20-incremental-etl.png)

Схема читается сверху вниз: от источника к fact table. `High-water mark` и `delete + insert` взяты из практики, в главе их нет.

## Обзор процесса ETL

| Шаги | Что делаем |
|---|---|
| 1–4 | План: схема, ETL tool, стратегии, детали по таблицам |
| 5–6 | Историческая загрузка: dimensions, потом facts |
| 7–8 | Инкрементальная загрузка: dimensions, потом facts |
| 9–10 | Агрегаты и OLAP, работа и автоматизация |

Перед дизайном нужны логическая модель, черновик архитектуры и черновик `source-to-target mapping` (какая колонка источника в какую колонку хранилища идёт). Ещё нужно узнать, какую нагрузку extract может дать источникам, и выбрать, где выполнять преобразования: на источнике, на целевой системе или на отдельной платформе.

## План ETL

План не зависит от технологии. Но ETL tool книга советует выбрать до детального плана, чтобы не переделывать работу.

### Шаг 1. Схема высокого уровня

Начните с простой схемы: источники слева, цели справа. В примере книги источник — 30-летняя COBOL-система коммунальной компании. На схеме записаны открытые вопросы, например: старых типов счётчиков нет ни в одной системе. Схему часто обновляют и ведут в двух версиях: простой для внешних людей и подробной для команды.

### Шаг 2. Выбор ETL tool

`ETL tool` читает разные источники, умеет lookup и join, пишет в разные цели и управляет потоком задач. Авторы считают его отраслевой best practice, даже если источники реляционные, а разработчики сильные. Графический инструмент сам себя документирует, а ручная система часто становится «непроходимой кашей». Он также даёт metadata, version control, готовый fuzzy matching и fail-over. Но в первой фазе он не окупится: порог входа высокий. Выгода приходит позже, при изменениях. В итогах главы авторы повторяют: коммерческий инструмент лучше библиотеки скриптов, потому что ETL годами поддерживают разные люди.

### Шаг 3. Default strategies

`Default strategies` — общие правила для частых задач. Нужно решить:

- **Extract:** файл, поток или чтение логов. Для SQL лучше родные драйверы, чем ODBC.
- **Архив:** сырые данные хранят минимум месяц.
- **Качество:** проверяйте dimensions и особенно facts в ETL, а не ждите жалоб пользователей.
- **SCD:** как менять атрибуты dimension со временем (slowly changing dimensions).
- **Доступность:** когда готов каждый источник и в каком порядке идут задачи.
- **Audit:** каждая строка помечена информацией о загрузке.
- **Staging:** где лежит staging area.

### Шаг 4. Детализация по целевым таблицам

Для каждой таблицы описывают преобразования, заканчивают mapping и делают profiling.

- **Чистые иерархии.** Надёжнее всего иерархии, которые источник хранит в нормализованных таблицах с FK между уровнями. Иерархию из Excel нужно вычистить или признать, что это не иерархия.
- **Схема таблицы.** В примере книги файл с 13 месячными колонками разворачивают в строки по месяцам. Потом по очереди ищут `surrogate key` (технический ключ dimension) клиента, счётчика, географии и даты.
- **Порядок.** Dimensions обрабатывают раньше lookup в fact. Зависимости между самими dimensions тоже выясняют: вокруг них строится порядок задач.

## Спецификация ETL

В один документ собирают mappings, отчёты profiling, физический дизайн и общие стратегии. Для каждой таблицы пишут раздел на 2–10 страниц: структуру, объёмы истории и инкремента, частоту загрузки, источник и profiling (min, max, число distinct, доля `NULL`), способ extract, правила SCD и late arriving data (данных, пришедших позже срока), логику преобразований (лучше pseudo code), зависимости и оценку сложности. Такой документ тяжело поддерживать. Реалистичный минимум — схема потока на одной странице, модель, mappings и пять страниц описания. Книга считает, что этого уже больше, чем у большинства команд.

## Sandbox: копия источника

Данные источника нужно изучать глубоко. Если источник загружен и нет reporting-копии, DBA могут сделать статичный снимок базы. Тогда можно исследовать данные, не боясь тяжёлого запроса. Лучше делать полную копию, подмножество — только при очень больших объёмах.

## Историческая загрузка

Иногда один код делает и историю, и инкремент, но чаще процессы разные. Часть логики можно использовать повторно.

### Шаг 5. Dimensions: исторические данные

Начинайте с простых dimensions, где все атрибуты type 1 (перезапись). Потом делайте dimensions с атрибутами type 2.

**Преобразования.** Даже простой dimension нужно чистить:

- привести типы и заменить `NULL` значениями по умолчанию: `NULL` мешает в запросах;
- объединить источники: общего ключа обычно нет, поэтому имена и адреса разбирают на части и ищут совпадения fuzzy logic (`IBM` и `International Business Machines`);
- расшифровать коды через таблицу в staging, а для неизвестного кода задать текст по умолчанию;
- проверить связи many-to-one: у товара одна модель. Для этого `GROUP BY` по товару с `HAVING count(DISTINCT model) > 1`. Snowflake-копия иерархии в staging тоже защищает, но проверять лучше заранее.

**Surrogate keys.** Когда в dimension одна строка на объект, назначают целые ключи по порядку (помогает `sequence`). Key map «production key → surrogate key» держат в staging: он нужен при загрузке facts.

**Загрузка.** Даже небольшой dimension грузят bulk-загрузчиком. Книга советует: выключить логирование, но оставить точки перезапуска; отсортировать файл по первичному индексу; делать большинство преобразований в ETL tool, а не в загрузчике: иначе он может уйти в медленный построчный режим; делать `TRUNCATE TABLE` перед полной перезаливкой.

**История type 2.** Бизнес хочет историю за прошлые годы, а не с даты запуска. Восстановить её трудно, иногда невозможно, а обычный SQL тут плохо подходит: нужен курсор или процедурный язык. В конце ставят даты окончания без разрывов. Для дат с точностью до дня конец старой версии — день перед началом новой. Для точности до минуты или секунды конец равен началу следующей строки.

**Date dimension.** Одна строка на день, от самой старой транзакции. Обычно его строят руками в электронной таблице, как и другие небольшие dimensions, например сценарий Actual и Budget. Их утверждает бизнес.

### Шаг 6. Facts: историческая загрузка

Главная проблема — объём: история иногда в тысячи раз больше инкремента. Зато таблица ещё не в production, и загрузка на несколько дней допустима.

- **Extract.** Берите только полезные для бизнеса строки и сразу копите итоги и количества строк.
- **Audit statistics.** Count и sum сравнивают между источником и хранилищем. Числа должны сходиться с операционными отчётами: это даёт хранилищу доверие. Если не сходятся, разницу объясняют.
- **Преобразования.** Facts обычно чистые. Типичные шаги: `NULL`, pivot и unpivot, предрасчёт производных мер.
- **`NULL`.** Если «нет значения» закодировано числом вроде `-1`, замените его настоящим `NULL`: в `sum` и `avg` он ведёт себя правильно. FK-колонки в fact всегда `NOT NULL`.
- **Содержимое.** Все факты одного `grain` (смысл одной строки): годовой итог в дневной таблице убирают или переносят в aggregate table. Производные меры, например net profit, часто считают во view или `OLAP cube` (многомерном кубе), а не хранят.

**Surrogate key pipeline.** Это последняя операция перед загрузкой. Входящая строка уже выглядит как целевая, но с `natural key` (ключом источника). Pipeline меняет их на surrogate keys и обрабатывает нарушения ссылочной целостности (RI). Dimensions к этому моменту готовы. В истории нарушения RI разбирают вручную: загрузку останавливают и чинят dimension или фильтр extract. Для type 2 в lookup нужен `BETWEEN` по датам версии. При небольшом объёме хватает одного join staging-таблицы со всеми dimensions. Для сотен гигабайт это тяжело, и тогда type 1 и type 2 обрабатывают отдельно.

**Audit key.** Строка fact часто хранит ключ `audit dimension`: версию ETL и индикатор качества (проверки пройдены или были проблемы). Ключ добавляют до или после pipeline.

**Загрузка fact.** Ускоряют bulk loader и партиционированная таблица, лучше с параллельной загрузкой партиций. Порядок: отключить FK и индексы, загрузить, построить индексы и склеить партиции, проверить уникальный индекс на surrogate key, включить FK.

## Инкрементальная загрузка

Главная трудность — найти новые, изменённые и удалённые строки. Дальше правила почти те же, что в истории. Но кроме вставок появляются обновления, а они в хранилище дорогие.

### Шаг 7. Dimensions: инкремент

**Extract.** Часто проще взять снимок dimension целиком и найти изменения при преобразовании. Если источник хранит тип изменения, берите только изменённые строки.

**Новые и изменённые строки.** Если владельцы источника не отдают изменения, ETL сравнивает сам:

- новую строку находят lookup по natural key (в dimension это обычный атрибут). Нет совпадения — вставка;
- для type 2 дата начала — день появления объекта (при ночной загрузке обычно вчера), дата конца — самая далёкая дата, не `NULL`: сравнение с `NULL` даёт ошибку или Unknown;
- изменения ищут сравнением колонок. Для больших dimensions это медленно, поэтому добавляют колонки `hash_type1` и `hash_type2` с hash атрибутов и сравнивают одну короткую строку. Другой вариант — `EXCEPT`;
- строки, удалённые в источнике, из dimension обычно не удаляют: на них ссылаются facts.

**Обработка изменений.** Если изменение законное, применяют SCD.

| Изменение | Что делает ETL |
|---|---|
| Type 1 | Перезаписывает значение, обычно во всех строках объекта |
| Type 2 | Закрывает текущую строку и добавляет новую с новым surrogate key: начало — вчера, флаг текущей — true |
| Type 3 | Меняет структуру таблицы, поэтому ETL редко это автоматизирует (см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)) |

### Шаг 8. Facts: инкремент

Fact tables слишком велики, чтобы заменить их за одно окно загрузки, поэтому грузят только новые и изменённые строки. Историческая загрузка может быть не полностью автоматической, а инкрементальная — должна.

1. **Extract и checkpoint качества.** Копию сырых данных сразу пишут в staging и считают метрики качества. Staging служит архивом для аудита и точкой перезапуска.
2. **Surrogate key pipeline.** Он похож на исторический, но нарушения RI обрабатываются автоматически. Lookup идёт по view с текущими версиями dimension. Варианты для строки без ключа:

| Политика | Оценка книги |
|---|---|
| Остановить загрузку | Редко полезно, хотя во многих ETL tools это по умолчанию |
| Отбросить строку | Подходит, если отсутствие dimension значит «эти данные не нужны» |
| Записать в error table | Нужен процесс разбора. Для финансов не подходит: там нужны все строки |
| Inferred member | Самый привлекательный вариант. На лету создают dummy-строку dimension: известен только natural key, остальное по умолчанию. Позже её исправляют как type 1 |
| Один unknown member | Не рекомендуется: все неизвестные ключи сливаются в одну строку |

3. **Late arriving facts.** Загрузка идёт после полуночи и берёт вчерашние транзакции, но часть данных приходит позже. Если все dimensions type 1, проблем нет. Если есть type 2, fact надо связать с версией на момент события: lookup использует даты начала и конца версии.
4. **Загрузка.** Fast load обычно требует пустой или неиндексированной таблицы, поэтому в инкременте часто быстрее обычный insert. Если инкремент идёт в пустую партицию, fast load подходит. Дневные партиции (365 в год) потом объединяют в недельные или месячные.
5. **Snapshot facts.** Transaction fact только растёт вставками. `Periodic snapshot` грузят в конце месяца, а текущий месяц иногда пересчитывают каждый день: с месячными партициями это просто. `Accumulating snapshot` следит за коротким процессом, например за выполнением заказа: строку обновляют много раз. Он дорогой в поддержке, но намного меньше других таблиц.

#### Ускорение цикла загрузки

Первый способ — обрабатывать только изменённые данные. Есть и другие:

- **Грузить чаще.** Ночная загрузка в 30 раз меньше месячной. Если ночью слишком дорого, часть чистки делают днём в staging, а после полуночи остаётся финал: проверки, ключи, загрузка.
- **Параллельность.** Запускайте независимые задачи вместе или дайте базе выполнять шаг параллельно. Но наивная схема может быть медленнее последовательной: процессы конкурируют за сеть, I/O и память.
- **Parallel structures.** Два сервера: один грузит, второй отвечает на запросы, а раз в день они за несколько минут меняются дисками. Дешевле: грузить в offline-партицию или таблицу и быстро переключать.

### Шаг 9. Агрегаты и OLAP

`Aggregate table` — результат большого агрегирующего запроса, сохранённый как таблица. Проблема возникает, когда fact не успевает обработаться в окно загрузки. Месячный агрегат для текущего месяца надо обновлять или пересоздавать. Изменение атрибута type 1 затрагивает все агрегаты и OLAP cubes по нему: ETL должен «вынуть» facts из старой группы и переложить в новую. Агрегаты должны совпадать с деталями, иначе запросы вернут разные результаты.

### Шаг 10. Работа и автоматизация

Идеал — режим `lights-out`: загрузка без людей. Достичь его трудно, но можно приблизиться.

- **Расписание.** ETL tool запускает задачу по времени, а следующую — после успеха предыдущей. Можно ждать события (файл, запись в базе) или вызвать job скриптом.
- **Предсказуемые ошибки.** Обработку ошибок закладывают с самого начала. Ранний fact или `NULL` в обязательной колонке ETL исправляет сам и продолжает.
- **Непредсказуемые ошибки.** Это испорченные данные или отключение питания. Книга советует иметь в fact одну колонку-surrogate key, которую присваивают по порядку новым строкам. Упавшую загрузку продолжают с надёжной точки или откатывают по непрерывному диапазону ключей.

## Real-time

Real-time требуют всё чаще. Авторы советуют сначала выяснить настоящие требования бизнеса.

### Triage: три класса задержки

Вопрос «нужен real-time?» бесполезен: почти все ответят «да». Поэтому книга делит запросы на три класса.

- **Instantaneous:** экран показывает истинное состояние источника в каждый момент. Обычно это `EII` (enterprise information integration): запросы идут прямо в источник, поэтому они должны быть простыми. Пример книги: статус запасов, когда менеджер сразу обещает товар клиенту.
- **Intra-day:** данные обновляются много раз в день, но могут отставать, как биржевые котировки с задержкой до 15 минут. Это micro-batch. Для частого extract нужен поток изменений: очередь сообщений, журнал транзакций или триггеры.
- **Daily:** данные на конец прошлого рабочего дня, после сверки в источнике. Это самый простой вариант. Если пользователи требуют быстрее, объясните компромиссы.

| | Daily | Intra-day | Instantaneous |
|---|---|---|---|
| Данные | Reconciled, полные транзакции | Provisional, отдельные транзакции | Provisional, фрагменты |
| Проверки | Column, structure, business rule | Column, structure | Только column |
| Итоги | Финальные | Исправляют ночью | Могут измениться ночью |

Правило книги: чем ниже latency, тем меньше проверок качества.

### Компромиссы архитектуры

Цели не меняются: качество, compliance, backup и архив нужны и в real-time. Поэтому компромиссы жёсткие.

- **Очередь или лог вместо batch-файла.** Batch-файл чистый: завершённые транзакции и разрешённые FK. В очереди данные сырые: возможны неполные транзакции и неразрешённые ключи. Раз в сутки их исправляет параллельный batch-поток.
- **Меньше quality screens.** Остаются column screens и простые lookup. `Structure screens` и `business rule screens` смотрят несколько полей или таблиц, и на них нет времени.
- **Facts со старыми dimensions.** Событие приходит раньше своего контекста. Тогда берут старую копию dimension, а если её нет, пустую. Позже dimension обновляют, а пользователи знают, что пока он описывает fact неточно.
- **Без staging.** Так работают некоторые системы, особенно EII. Тогда с руководством надо обсудить, кто отвечает за backup, восстановление, архив и compliance.

### Real-time partitions

Чтобы история шла до текущего момента, строят `real-time partition`: отдельную часть fact table, лучше всего настоящую партицию по дате события. Требования к ней:

- она содержит всю активность после последней загрузки;
- у неё тот же grain, что у основного fact;
- индексов почти нет, чтобы данные вливались непрерывно;
- она лежит в памяти, поэтому запросы быстрые и без индексов.

Она подходит для transaction и periodic snapshot. Для accumulating snapshot авторам она не потребовалась.

- **Transaction:** партиция хранит транзакции с полуночи. Пример: 10 миллионов транзакций в день по 40 байт — это 400 МБ в день и около 150 ГБ в год. Основная таблица большая, а дневной срез лежит в памяти.
- **Periodic snapshot:** партиция хранит текущий месяц и обновляется непрерывно. Пример: банк с 15 миллионами счетов, за 36 месяцев 540 миллионов строк. Партиция месяца занимает 480 МБ. В последний день месяца её присоединяют к основной таблице и начинают заново.

## Итоги главы

- ETL занимает больше времени, чем ждут: проблемы спрятаны в источниках. Работа идёт по 10 шагам: план, история, инкремент, агрегаты и автоматизация.
- Авторы советуют коммерческий ETL tool вместо скриптов, но он окупается не в первой фазе.
- Историческую загрузку можно останавливать и проверять, поэтому проблемы RI и разрывы дат type 2 исправляют там.
- В fact `NULL` допустим в мерах, но не в FK, а все строки должны иметь один `grain`.
- Surrogate key pipeline — последний шаг перед загрузкой, и для type 2 в нём нужен `BETWEEN`.
- Инкремент автоматический: нарушения RI решает inferred member, late arriving facts получают версию на дату события.
- Чем ниже latency, тем меньше проверок качества, поэтому бизнес участвует в выборе компромисса.

## Ключевые термины

| Термин | Значение |
|---|---|
| Default strategies | Общие правила ETL для всех таблиц |
| Key map | Таблица в staging: production key → surrogate key |
| Audit statistics | Count и sum, сверяемые между источником и хранилищем |
| Inferred member | Dummy-строка dimension для неизвестного natural key |
| Real-time partition | Часть fact для свежих данных: без индексов, в памяти |

## Что это значит на практике

> **Пояснение:** `high-water mark` (HWM, граница последней загруженной записи) и `idempotent load` (повторный запуск даёт тот же результат) — приёмы практики. В этой главе книги их нет, но практика ниже их использует.

- Храните HWM в таблице управления и обновляйте его только после успешной загрузки.
- Берите HWM из данных (`max(modified_at)` из staging), а не из часов. Иначе будут пропуски и дубли.
- Делайте загрузку idempotent: удалите строки по бизнес-ключу и вставьте заново. В `dbt` это стратегия `delete+insert` или `merge` для incremental.
- Для каждой загрузки сравнивайте count и sum источника и хранилища.
- Не теряйте строки без ключа. Книга советует inferred member (пример в практике [главы 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)). Практика ниже для простоты берёт unknown member.
- Для late arriving facts ищите версию dimension по дате события, а не текущую. Строки, удалённые в источнике, не удаляйте из dimension.
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

Заказ 5 теперь указывает на клиента «Мария». Для такого исправления в fact нужен natural key заказа в staging или в источнике. Поэтому хранение сырых данных важно. Это и есть минус unknown member: ключи в fact приходится переписывать. С inferred member строка fact сразу получила бы свой ключ, а позже обновилась бы только строка dimension.
</details>

## Вопросы для самопроверки

1. Почему историческую и инкрементальную загрузку часто пишут как два разных процесса? Чем отличаются требования к автоматизации?
2. Какие политики есть для строки fact без совпадения в dimension? Почему книга выбирает inferred member, а не один unknown member?
3. Когда в lookup нужен `BETWEEN`? Что случится с late arriving fact, если искать только текущую версию dimension?
4. Почему при низкой latency данные менее качественные? Какие проверки отпадают первыми?
5. Почему HWM лучше брать из данных, а не из времени запуска?
6. Что значит idempotent load и как `DELETE` перед `INSERT` его обеспечивает?

Предыдущая: [Глава 19. ETL subsystems](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/). Следующая: [Глава 21. Big Data](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/).
