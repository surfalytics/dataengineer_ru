---
title: "The Data Warehouse Toolkit, глава 2: Техники Kimball"
head:
  - tag: title
    content: "Техники Kimball: SCD и fact tables | Инжиниринг Данных"
description: "Конспект главы 2 The Data Warehouse Toolkit. Справочник техник: типы fact tables, surrogate key, role-playing, junk dimension, SCD 0-7 и практика в DuckDB."
sidebar:
  order: 2
  label: "2. Техники Kimball"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** глава 2 — официальный каталог приёмов Kimball. Её не читают подряд: к ней возвращаются, когда нужен конкретный приём. Авторы считают техники стандартом: другие книги не расширили их заметно и не спорят с ними.

## О чём глава

[Глава 1](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/) объяснила, зачем нужна dimensional model. Глава 2 отвечает: какие приёмы входят в набор Kimball и когда нужен каждый. Это справочник: у каждой техники в книге есть ссылки на главы с примерами, а кейсы начинаются с розницы ([глава 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/)).

- Основные понятия и базовые техники для `fact table` и `dimension table`.
- Интеграция через `conformed dimensions` и `bus matrix`.
- `SCD` (Type 0–7) и иерархии.
- Продвинутые техники и специальные схемы.

![Четыре типа fact table: transaction, periodic snapshot, accumulating snapshot и factless](/assets/data-warehouse-toolkit/ch02-fact-table-types.png)

Читайте схему сверху вниз: от типа таблицы к тому, что значит строка и как она обновляется.

## Основные понятия

### Требования бизнеса и реальность данных

Сначала команда узнаёт, что нужно бизнесу: на встречах обсуждают KPI, острые проблемы и решения. Эксперты по источникам и data profiling показывают, что возможно.

### Совместные workshops по моделированию

Модель делают вместе с экспертами бизнеса и data governance. Ведёт моделер, но модель складывается на интерактивных workshops. Проектировать её в изоляции от бизнеса нельзя.

### Четыре шага проектирования

Модель определяют четыре решения: выбрать `business process`, объявить `grain`, определить `dimensions` и `facts`. Затем команда с data governance задаёт имена и бизнес-правила.

### Business process

`Business process` — операция организации: принять заказ, обработать страховой иск, записать студента на курс. Процесс порождает метрики, которые становятся facts. Каждый процесс — строка в `bus matrix`.

### Grain

`Grain` — что значит одна строка `fact table`. Это контракт дизайна: его объявляют до выбора dimensions и facts, потому что всё остальное должно ему соответствовать. Авторы советуют начинать с `atomic grain` — самого низкого уровня данных процесса: он выдерживает непредсказуемые запросы. Один grain — одна таблица, смешивать нельзя.

### Dimensions: описательный контекст

`Dimension` отвечает на вопросы «кто, что, где, когда, почему, как» про событие. Её атрибуты нужны для фильтров и группировок; по возможности она даёт одно значение на строку fact. Авторы называют dimensions «душой» хранилища: от них зависит удобство BI.

### Facts: измерения

`Fact` — числовое измерение, результат события процесса. Строка fact table — одно измерение на объявленном grain и отражает физическое событие, а не нужды отчёта. Количество и сумма подходят для продажи, зарплата менеджера магазина нет.

### Star schema и OLAP cube

`Star schema` — dimensional модель в реляционной БД: fact table связана с dimension tables через primary и foreign keys. `OLAP cube` — та же модель в многомерной БД, с доступом через MDX и XMLA вместо SQL.

### Graceful extensions: мягкие расширения

Dimensional модель переживает изменения без правки запросов и без смены их результатов. Можно добавить facts и foreign keys (grain не меняется), добавить атрибуты в dimension или сделать grain более атомарным, сохранив имена колонок.

## Базовые техники для fact table

### Структура fact table

Fact table хранит числовые измерения реального события. Кроме чисел в ней есть foreign key на каждую dimension, а также degenerate dimension keys и метки времени. От будущих отчётов структура не зависит.

### Additive, semi-additive и non-additive facts

- `Additive` fact суммируется по всем dimensions.
- `Semi-additive` суммируется по части: остаток на счёте нельзя суммировать по времени.
- `Non-additive` не суммируется, например ratio. Хранят additive части и делят после суммирования, в BI или кубе.

### NULL в fact tables

`NULL` в числовом факте безопасен: `SUM`, `COUNT`, `MIN`, `MAX` и `AVG` работают правильно. `NULL` в foreign key нельзя, он нарушает referential integrity. Вместо него в dimension заводят строку «неизвестно» или «неприменимо».

### Conformed facts

Если показатель есть в нескольких fact tables, его определение и имя должны совпадать. Если определения разные, имена тоже делают разными, чтобы предупредить пользователей.

### Transaction fact table

Строка — одно событие в точке места и времени. Такие таблицы самые выразительные и дают максимум slice and dice. Строка есть, только если событие было.

### Periodic snapshot

Строка подытоживает период: день, неделю, месяц. Grain — период, а не транзакция. Строка есть за каждый период, даже без активности: facts тогда равны нулю или `NULL`.

### Accumulating snapshot

Строка описывает процесс с началом, шагами и концом, например выполнение заказа. Для каждой вехи есть date key. Строку вставляют при создании и обновляют по ходу процесса: только у этого типа строки регулярно меняются.

### Factless fact table

Событие может не нести чисел: «студент пришёл на занятие» — строка с ключами дня, студента, преподавателя, места и класса. Таблица отвечает и на вопрос «что не случилось»: из coverage table (все возможные события) вычитают activity table.

### Aggregate fact table и OLAP cube

`Aggregate` — простая числовая свёртка atomic fact table, нужная для скорости. BI сам выбирает уровень (`aggregate navigation`): агрегаты работают как индексы и не видны пользователям. Агрегатные кубы строят так же, но пользователи работают с ними напрямую.

### Consolidated fact table

Facts из разных процессов можно объединить в одной таблице, если у них один grain, например план и факт. ETL тяжелее, зато аналитику проще, чем при drill across.

## Базовые техники для dimension table

### Структура dimension table

У dimension один primary key, он встроен как foreign key в fact tables. Обычно это широкая плоская денормализованная таблица. Самые полезные атрибуты — подробные описания, а не коды: по ним фильтруют, они же подписи в отчётах.

### Surrogate keys

`Surrogate key` — анонимное целое число, которое хранилище выдаёт по порядку. Primary key не может быть `natural key` источника: при истории у него много строк, а natural keys разных систем несовместимы. Хранилище владеет ключами всех dimensions; исключение — date dimension.

### Natural, durable и supernatural keys

Natural key создаёт источник, и правила бизнеса могут его менять: номер сотрудника меняется, если тот уволился и вернулся. Поэтому нужен `durable key` (supernatural): постоянный ключ, лучше всего простое целое число. Surrogate keys сотрудника меняются с профилем, durable key нет.

### Drilling down

Drill down — добавить в запрос атрибут dimension в `GROUP BY`. Атрибут может быть из любой dimension, заранее заданные иерархии не нужны.

### Degenerate dimension

`Degenerate dimension` — dimension без содержимого, кроме ключа. Строки счёта наследуют все ключи счёта, а номер счёта остаётся ключом. Его кладут в fact table без отдельной таблицы.

### Denormalized flattened dimensions

Авторы советуют сопротивляться привычке нормализовать. Иерархии many-to-one фиксированной глубины раскладывают в атрибуты одной плоской строки: так проще и быстрее.

### Multiple hierarchies

В одной dimension может быть несколько иерархий. У календаря есть день → неделя → fiscal period и день → месяц → год. Они уживаются в одной таблице.

### Flags and indicators как текст

Криптичные сокращения и флаги true/false дополняют полными словами. Коды со смыслом внутри значения разбивают на части: каждая часть — отдельный атрибут.

### NULL в атрибутах dimension

Вместо `NULL` в атрибутах пишут `Unknown` или `Not Applicable`: базы по-разному группируют и фильтруют по `NULL`.

### Calendar date dimension

Календарь есть почти у каждой fact table: через него ходят по датам, месяцам, fiscal periods и праздникам. Ключ можно сделать осмысленным, `YYYYMMDD`. Для времени суток нужна отдельная dimension.

### Role-playing dimension

Одну физическую dimension можно использовать в fact несколько раз в разных ролях: несколько дат ведут в одну date dimension. Каждый foreign key должен ссылаться на отдельный view, чтобы ссылки были независимыми. Эти view и есть роли.

### Junk dimension

Транзакции дают много мелких флагов с низкой cardinality. Вместо отдельной dimension на каждый создают одну `junk dimension`. Она не обязана быть декартовым произведением значений: нужны только комбинации из источника.

### Snowflake

`Snowflake` получается, если иерархию dimension нормализовать во вторичные таблицы. Авторы советуют его избегать: пользователям сложно, запросы могут замедлиться. 

### Outrigger

`Outrigger` — dimension, на которую ссылается другая dimension, например дата открытия в dimension банковского счёта. Это допустимо, но редко: обычно связь лучше опустить в fact table, где у обеих dimensions свои foreign keys.

## Интеграция через conformed dimensions

### Conformed dimensions

Dimensions `conform`, если у атрибутов одинаковые имена и значения. Тогда данные из разных fact tables собирают в одном отчёте по общему атрибуту — в этом суть интеграции. Dimension определяют один раз с data governance и переиспользуют.

### Shrunken dimensions

`Shrunken dimension` — conformed dimension с частью строк или колонок базовой. Нужна для агрегатов и процессов с крупным grain, например прогноза по месяцу и бренду.

### Drilling across

`Drill across` — отдельные запросы к двум и более fact tables с одинаковыми conformed атрибутами в заголовках строк. Результаты склеивают по этим заголовкам операцией sort-merge. В BI это зовут stitch или multipass query.

### Value chain

`Value chain` — цепочка создания стоимости, естественный поток процессов: для розницы закупка → склад → продажа. У каждого шага свои метрики и grain, поэтому он даёт минимум одну atomic fact table.

### Enterprise data warehouse bus architecture

`Bus architecture` — инкрементальный способ построить корпоративное DW/BI: планирование делят по процессам, а интеграцию дают общие conformed dimensions. Каждая строка `bus matrix` — небольшой agile-проект. Архитектура не зависит от платформы.

### Enterprise data warehouse bus matrix

В `bus matrix` строки — процессы, колонки — dimensions, закрашенная ячейка — связь. Строку читают, чтобы проверить dimensions процесса, колонку — чтобы найти dimension для согласования. Приоритеты расставляют по строкам: внедряют по одной.

### Detailed implementation bus matrix

Здесь строка процесса раскрыта до конкретных fact tables или кубов, с точным grain и списком facts.

### Opportunity/stakeholder matrix

Колонки здесь — бизнес-функции: маркетинг, продажи, финансы. Матрица показывает, кому интересен процесс, то есть кого звать на workshops.

## Slowly changing dimensions: изменения атрибутов

Атрибуты dimension иногда меняются. Способ выбирают для каждого атрибута отдельно.

![Схема выбора типа SCD: Type 0–4 и гибриды Type 5–7](/assets/data-warehouse-toolkit/ch05-scd-types.png)

Type 5–7 — гибриды. Подробно SCD разбирает [глава 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/).

### Type 0: оставить исходное значение

Значение не меняется, и facts всегда группируются по исходному значению. Подходит для атрибутов «original», например исходного кредитного рейтинга, для durable identifiers и большинства атрибутов date dimension.

### Type 1: перезапись

Старое значение заменяют новым, история пропадает. Это просто, но затронутые агрегаты и кубы нужно пересчитать.

### Type 2: новая строка

При изменении добавляют новую строку с новым surrogate key. Он попадает в facts с момента изменения до следующего. Поэтому primary key не может быть natural или durable key. Нужны минимум три колонки: row effective date, row expiration date и current row indicator.

> **Пояснение:** в практике ниже дата окончания равна дате начала следующей версии, а в join стоит `<`.

### Type 3: новая колонка

Старое значение сохраняют в новой колонке, а основную перезаписывают, как в Type 1. Авторы зовут это «alternate reality»: группировать можно по текущему или по прежнему значению. Type 3 нужен редко.

### Type 4: mini-dimension

Быстро меняющиеся атрибуты выносят в `mini-dimension`. Кандидаты — часто используемые атрибуты в dimension на миллионы строк, даже если они меняются редко. У mini-dimension свой primary key, а fact table хранит оба ключа.

### Type 5: mini-dimension и Type 1 outrigger

Type 5 строится на Type 4: в базовую dimension встраивают текущую ссылку Type 1 на mini-dimension. Тогда текущие атрибуты читаются без fact table, а история сохраняется. ETL перезаписывает ссылку при каждой смене.

### Type 6: атрибуты Type 1 в dimension Type 2

Type 6 тоже даёт историю и текущие значения: в dimension Type 2 добавляют колонки с текущими значениями тех же атрибутов (Type 1). Facts группируют по значению на момент события или по текущему. Колонку перезаписывают во всех строках с одним durable key.

### Type 7: две перспективы

Type 7 даёт отчёты «как было» и «как сейчас» на одной dimension. В fact лежат durable key и surrogate key. «Как сейчас»: фильтр по флагу current и join по durable key. «Как было»: join по surrogate key. Это два view.

## Иерархии в dimensions

### Fixed depth positional hierarchies

Цепочка many-to-one, например product → brand → category → department. Если у уровней согласованные имена, их делают отдельными атрибутами: это самый понятный и быстрый вариант. Иначе нужны ragged hierarchies.

### Slightly ragged hierarchies

Число уровней разное, но разброс небольшой: географические иерархии бывают от трёх до шести уровней. Делают атрибуты на максимум уровней и заполняют по правилам бизнеса.

### Ragged hierarchies и bridge table

Иерархии неопределённой глубины трудно моделировать. Рекурсия в SQL и OLAP не умеет подменять иерархию на лету и не поддерживает shared ownership и изменения во времени. Решение — `bridge table` со строкой на каждый возможный путь: тогда хватает обычного SQL.

### Ragged hierarchies и pathstring

Альтернатива — атрибут `pathstring` с закодированным путём от вершины до узла. Многие запросы идут обычным SQL. Минусы: нельзя быстро подменить иерархию, нет shared ownership, смена структуры может потребовать переименовать всё дерево.

## Продвинутые техники для fact table

### Fact table surrogate keys

Surrogate key для fact table полезен, но не обязателен. Его выдаёт ETL. Он служит primary key и идентификатором строки, помогает отменить или продолжить загрузку и заменить update на insert и delete.

### Centipede fact tables

`Centipede` получается, когда каждый уровень иерархии (дата, месяц, квартал, год) делают отдельной dimension и кладут все ключи в fact. Авторы советуют этого избегать и сворачивать такие dimensions до нижнего grain. Так же получается, если вместо junk dimension сделать десятки мелких dimensions.

### Числа: атрибут или fact

Если число нужно в основном для расчётов, это fact. Если оно стабильное и нужно для фильтров и групп, это атрибут dimension (можно с диапазонами, value bands). Классический спорный случай — стандартная цена товара. Иногда нужны оба варианта.

### Lag/duration facts

В accumulating snapshot у каждой вехи есть дата, а пользователям нужны сроки между вехами. Чтобы не считать сотни lag, хранят по одному lag на шаг от начала процесса. Любой lag между шагами — разность двух значений.

### Header/line fact tables

У транзакции есть заголовок и строки (parent/child). В fact table уровня строки кладут все foreign keys и degenerate dimensions заголовка.

### Allocated facts

У header/line бывают facts другого grain, например доставка на весь заказ. Их распределяют по строкам по правилам бизнеса, чтобы резать по всем dimensions. Header-level fact table тогда часто не нужна.

### Profit and loss fact tables

Fact table с уравнением прибыли (выручка − затраты) на grain атомарной выручки даёт прибыльность клиентов, продуктов, акций и каналов. Её трудно строить: затраты нужно распределить на этот grain. Это крупная подсистема ETL и политически острый шаг, нужна поддержка руководства. Поэтому такие таблицы не делают в первую очередь.

### Multiple currency facts

Для каждого финансового fact хранят две колонки: в валюте транзакции и в единой валюте. Вторую считает ETL по утверждённому правилу. Нужна ещё currency dimension.

### Multiple units of measure

Если facts нужны в разных единицах (паллеты, ящики, штуки), их хранят один раз в стандартной единице и держат в строке коэффициенты пересчёта. Для пользователей делают view с нужным коэффициентом.

### Year-to-date facts

Просьба о YTD быстро растёт в «YTD на закрытие периода» и другие варианты. Надёжнее считать YTD в BI или кубе, а не хранить.

### Multipass SQL

BI не должен соединять две fact tables по foreign keys: cardinality такого join не контролируется, ответ будет неверным. Например, отгрузки и возвраты по клиенту и продукту. Нужен drill across: два запроса и sort-merge.

### Timespan tracking в fact tables

В редких случаях в fact добавляют effective date, expiration date и current indicator, как в Type 2. Например, для медленно меняющихся остатков запасов: частый periodic snapshot грузил бы одинаковые строки.

### Late arriving facts

Факт пришёл с опозданием, и текущий контекст dimension ему не подходит. Тогда ищут ключи, которые действовали в момент события.

## Продвинутые техники для dimension

### Dimension-to-dimension joins

Ссылка на outrigger может вызвать взрывной рост базовой dimension: Type 2 изменения в outrigger заставляют делать Type 2 и в базе. Выход — перенести foreign key outrigger в fact table. Связь тогда видна только через fact.

### Multivalued dimensions и bridge table

Обычно dimension даёт одно значение на строку fact, но иногда значений несколько: у пациента бывает несколько диагнозов. Тогда fact ссылается на группу, а `bridge table` хранит строку на каждый диагноз группы.

### Time varying multivalued bridge tables

Bridge может опираться на Type 2 dimensions, например связь банковских счетов и клиентов. Чтобы связи были верными, в bridge добавляют даты начала и конца, а запрос ограничивает bridge моментом времени.

### Behavior tag time series

Кластерный анализ периодически даёт клиентам текстовые behavior tags. Ряд тегов хранят позиционными атрибутами в customer dimension.

### Behavior study groups

Сложное поведение клиентов находят долгим анализом и не встраивают в каждый отчёт. Результат сохраняют в таблице `study group` с durable keys клиентов и используют как фильтр в любой схеме с customer dimension.

### Aggregated facts as dimension attributes

Клиентов часто фильтруют по агрегатам, например «потратили больше суммы за прошлый год». Такие метрики кладут в dimension, часто диапазонами. ETL сложнее, BI проще.

### Dynamic value bands

Отчёт со строками-диапазонами по числовому fact, например баланс «от 0 до $10», «от $10,01 до $25». Границы задают при запросе, а не в ETL. Диапазоны хранят в маленькой value banding dimension с join «больше/меньше» или в `CASE`. Dimension, вероятно, быстрее: `CASE` почти без ограничений сканирует fact table.

### Text comments dimension

Свободные комментарии не хранят в fact как текстовые метрики. Их выносят в comments dimension и ссылаются foreign key.

### Multiple time zones

Для универсального и местного времени в fact ставят два foreign keys на две role-playing date dimensions.

### Measure type dimensions

Если в fact table много редко заполненных facts, можно свести их к одному generic fact и measure type dimension. Авторы обычно не советуют: таблица растёт в среднем во столько раз, сколько колонок заполнено в строке, а расчёты между колонками усложняются. Допустимо при сотнях возможных facts, если на строку подходят единицы.

### Step dimensions

В последовательных процессах, например событиях веб-страниц, на каждый шаг есть строка. Step dimension показывает номер шага и сколько шагов осталось.

### Hot swappable dimensions

Одна fact table работает с разными копиями одной dimension. Пример: котировки акций видят несколько инвесторов, и у каждого свои атрибуты акций.

### Abstract generic dimensions

Модельеры иногда делают одну общую dimension для разных сущностей, например одну `location` вместо атрибутов в store, warehouse и customer. Авторы советуют этого избегать: атрибуты у типов разные, а таблица раздувается. Абстракция уместна в источнике или ETL, но не в модели.

### Audit dimensions

При создании строки fact ETL может создать audit dimension с метаданными: индикаторами качества данных, версией ETL-кода, временем выполнения. Так видно, какая версия ETL создала какие строки, это важно для compliance.

### Late arriving dimensions

Facts иногда приходят раньше контекста dimension. Тогда создают строку-заглушку с natural key и значениями «unknown» и позже обновляют её как Type 1. Если Type 2 атрибут меняют задним числом, вставляют новую строку и перестраивают (restate) связанные facts.

## Специальные схемы

### Supertype и subtype

У банка десятки видов счетов, и одна fact table со всеми facts и атрибутами не получится: они несовместимы. Строят `supertype` fact table с общими facts и общей dimension, а для каждого subtype — свои таблицы. Их ещё зовут core и custom.

### Real-time fact tables

Таким таблицам нужны обновления чаще ночной загрузки. Приёмы зависят от СУБД или куба: например, `hot partition` держат в памяти без агрегатов и индексов.

### Error event schemas

Качество данных проверяют `data quality screens`. Найденную ошибку пишут в специальную схему в ETL back room: error event fact table (grain — одна ошибка) и error event detail fact table (grain — каждая колонка в ошибке).

## Итоги главы

- Модель начинается с четырёх решений: process, grain, dimensions, facts. Grain объявляют первым.
- Три базовых типа fact table — transaction, periodic snapshot и accumulating snapshot. Factless table хранит события без чисел.
- Dimension — широкая плоская таблица с `surrogate key`, а natural key источника на роль primary key не годится.
- Интеграцию дают `conformed dimensions`, а `bus matrix` превращает их в план внедрения по строкам.
- Для изменений атрибутов есть SCD Type 0–7, и тип выбирают для каждого атрибута отдельно.
- Авторы советуют избегать `snowflake`, centipede fact tables и abstract generic dimensions.
- Две fact tables не соединяют напрямую: каждую агрегируют отдельно и объединяют через `drill across`.

## Ключевые термины

| Термин | Значение |
|---|---|
| Surrogate key | Анонимное целое число, primary key dimension |
| Role-playing dimension | Одна dimension в нескольких ролях |
| Junk dimension | Мелкие флаги и коды в одной таблице |
| Conformed dimension | Общая dimension для нескольких fact tables |
| Drill across | Запросы к разным fact tables и склейка по общим атрибутам |
| Bus matrix | Процессы в строках, dimensions в колонках |
| SCD | Способ хранить изменения атрибутов dimension |
| Bridge table | Связь многие-ко-многим или пути в иерархии |

## Что это значит на практике

- Запишите тип SCD для каждого атрибута dimension, а не для всей таблицы.
- В `dbt` Type 2 — это `snapshot` с колонками `dbt_valid_from` и `dbt_valid_to`.
- Не держите флаги в fact: сделайте junk dimension.
- Не храните YTD и проценты: храните additive части, считайте итог в запросе.
- Для каждой роли даты делайте отдельный view: `dim_order_date`, `dim_ship_date`.
- Не оставляйте `NULL` в foreign key: заведите в dimension строку «Unknown».
- Не соединяйте две fact tables одним `JOIN`: агрегируйте каждую и объединяйте по общим атрибутам.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку в одной сессии. Не пропускайте задания: каждое меняет таблицы для следующего.

### Шаг 1. Создаём схему

![Одна dimension дат играет две роли в fact; junk dimension хранит флаги заказа](/assets/data-warehouse-toolkit/ch02-role-playing.png)

```sql
CREATE TABLE dim_date AS
SELECT
    strftime(d, '%Y%m%d')::INT AS date_key,
    d::DATE AS full_date,
    monthname(d) AS month_name
FROM generate_series(DATE '2024-01-01', DATE '2024-06-30', INTERVAL 1 DAY) t(d);

-- SCD: city = Type 2, customer_name = Type 1, segment = Type 3 (prior_segment)
CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1, 'C1', 'Анна Смирнова', 'Москва', 'Retail', NULL::VARCHAR, DATE '2024-01-01', DATE '9999-12-31', true),
    (2, 'C2', 'Борис Иванов',  'Казань', 'Retail', NULL::VARCHAR, DATE '2024-01-01', DATE '9999-12-31', true),
    (3, 'C3', 'Вера Петрова',  'Казань', 'Retail', NULL::VARCHAR, DATE '2024-01-01', DATE '9999-12-31', true)
) t(customer_key, customer_id, customer_name, city, segment, prior_segment,
    row_effective_date, row_expiration_date, is_current);

-- новый срез из источника на 2024-03-01
CREATE TABLE stg_customer AS
SELECT * FROM (VALUES
    ('C1', 'Анна Смирнова',        'Москва', 'Corporate'),  -- segment изменился
    ('C2', 'Борис Иванов',         'Москва', 'Retail'),     -- city изменился
    ('C3', 'Вера Петрова-Сидорова','Казань', 'Retail')      -- имя исправлено
) t(customer_id, customer_name, city, segment);

-- junk dimension: комбинации флагов заказа
CREATE TABLE dim_order_profile AS
SELECT * FROM (VALUES
    (1, 'Карта',    'Сайт',  'Обычный'),
    (2, 'Карта',    'Сайт',  'Срочный'),
    (3, 'Наличные', 'Офлайн','Обычный'),
    (4, 'Наличные', 'Офлайн','Срочный')
) t(profile_key, payment_type, channel, rush_flag);

-- grain: одна строка заказа. Две роли даты: order и ship
CREATE TABLE fact_order_line AS
SELECT
    strftime(order_date, '%Y%m%d')::INT AS order_date_key,
    strftime(ship_date,  '%Y%m%d')::INT AS ship_date_key,
    customer_key, profile_key, order_number, amount
FROM (VALUES
    ('O1', DATE '2024-01-10', DATE '2024-01-12', 1, 1, 100),
    ('O2', DATE '2024-01-15', DATE '2024-01-20', 2, 3, 200),
    ('O3', DATE '2024-02-05', DATE '2024-02-07', 2, 2, 150),
    ('O4', DATE '2024-02-27', DATE '2024-03-02', 3, 1,  80)
) t(order_number, order_date, ship_date, customer_key, profile_key, amount);
```

### Задания

**1.** Type 1. Исправьте имя клиента из `stg_customer`. История не нужна: просто перезапишите значение в текущей строке.

<details>
<summary>Решение</summary>

```sql
UPDATE dim_customer d
SET customer_name = s.customer_name
FROM stg_customer s
WHERE d.customer_id = s.customer_id
  AND d.is_current
  AND d.customer_name <> s.customer_name;

SELECT customer_key, customer_id, customer_name FROM dim_customer ORDER BY 1;
```

Изменилась только строка C3. Ключ остался прежним, поэтому старые факты видят новое имя.
</details>

**2.** Type 2. Клиент C2 переехал. Закройте старую строку датой `2024-03-01` и добавьте новую версию с новым surrogate key.

<details>
<summary>Решение</summary>

```sql
-- 1) закрываем старую версию
UPDATE dim_customer d
SET row_expiration_date = DATE '2024-03-01', is_current = false
FROM stg_customer s
WHERE d.customer_id = s.customer_id
  AND d.is_current
  AND d.city <> s.city;

-- 2) вставляем новую версию для тех, у кого нет текущей строки
INSERT INTO dim_customer
SELECT (SELECT max(customer_key) FROM dim_customer)
         + row_number() OVER (ORDER BY s.customer_id),
       s.customer_id, s.customer_name, s.city, s.segment, NULL::VARCHAR,
       DATE '2024-03-01', DATE '9999-12-31', true
FROM stg_customer s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_customer d
    WHERE d.customer_id = s.customer_id AND d.is_current
);

SELECT customer_key, customer_id, city, row_effective_date, row_expiration_date, is_current
FROM dim_customer ORDER BY customer_id, customer_key;
```

У C2 теперь две строки: Казань (ключ 2, закрыта) и Москва (ключ 4, текущая).
</details>

**3.** Type 3. У клиента C1 сменился segment. Сохраните прошлое значение в колонке `prior_segment`.

<details>
<summary>Решение</summary>

```sql
UPDATE dim_customer d
SET prior_segment = d.segment,
    segment = s.segment
FROM stg_customer s
WHERE d.customer_id = s.customer_id
  AND d.is_current
  AND d.segment <> s.segment;

SELECT customer_id, segment, prior_segment FROM dim_customer WHERE is_current ORDER BY 1;
```
</details>

**4.** Загрузка новых fact. Добавьте три заказа за март и апрель (O5–O7, данные в решении). Для каждого найдите версию клиента, действовавшую на дату заказа. Потом покажите выручку по городам.

<details>
<summary>Решение</summary>

```sql
INSERT INTO fact_order_line
SELECT strftime(o.order_date, '%Y%m%d')::INT,
       strftime(o.ship_date,  '%Y%m%d')::INT,
       c.customer_key, o.profile_key, o.order_number, o.amount
FROM (VALUES
    ('O5', DATE '2024-03-10', DATE '2024-03-12', 'C2', 1, 300),
    ('O6', DATE '2024-04-02', DATE '2024-04-03', 'C2', 4, 120),
    ('O7', DATE '2024-04-08', DATE '2024-04-12', 'C1', 2,  90)
) o(order_number, order_date, ship_date, customer_id, profile_key, amount)
JOIN dim_customer c
  ON c.customer_id = o.customer_id
 AND o.order_date >= c.row_effective_date
 AND o.order_date <  c.row_expiration_date;

SELECT c.city, sum(f.amount) AS revenue
FROM fact_order_line f
JOIN dim_customer c USING (customer_key)
GROUP BY c.city
ORDER BY c.city;
```

Заказы C2 до марта остались за Казанью. Заказы после — за Москвой. Это и есть смысл Type 2.
</details>

**5.** Role-playing и junk dimension. Покажите по месяцу заказа и месяцу отгрузки количество заказов и средний срок отгрузки в днях. Затем посчитайте выручку по типу оплаты и срочности.

<details>
<summary>Решение</summary>

```sql
SELECT od.month_name AS order_month,
       sd.month_name AS ship_month,
       count(*)      AS orders,
       avg(sd.full_date - od.full_date) AS avg_ship_days
FROM fact_order_line f
JOIN dim_date od ON od.date_key = f.order_date_key   -- роль: order date
JOIN dim_date sd ON sd.date_key = f.ship_date_key    -- роль: ship date
GROUP BY ALL
ORDER BY min(od.full_date);

SELECT p.payment_type, p.rush_flag, sum(f.amount) AS revenue
FROM fact_order_line f
JOIN dim_order_profile p USING (profile_key)
GROUP BY ALL
ORDER BY revenue DESC;
```

Заказ O4 сделан в феврале, а отправлен в марте. Одна dimension в двух ролях показывает это.
</details>

## Вопросы для самопроверки

1. Когда выбрать periodic snapshot, а когда transaction fact table?
2. Почему natural key не годится как primary key dimension и зачем нужен durable key?
3. Как выбрать между SCD Type 1, 2 и 3 для атрибута «город клиента»?
4. Зачем junk dimension, если можно оставить флаги в fact, и почему в ней не нужны все возможные комбинации?
5. Почему нельзя соединять две fact tables напрямую и как это решает drill across?
6. Зачем в accumulating snapshot хранить по одному lag на шаг от начала процесса, а не все пары дат?

Предыдущая: [Глава 1. DW/BI и dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/). Следующая: [Глава 3. Продажи в рознице](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/).
