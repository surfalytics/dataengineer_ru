---
title: "The Data Warehouse Toolkit — конспект книги"
head:
  - tag: title
    content: "The Data Warehouse Toolkit: конспект и SQL | Инжиниринг Данных"
description: "Конспект The Data Warehouse Toolkit (Kimball) на русском: dimensional modeling, star schema, SCD, bus matrix, ETL. Краткое содержание всех 21 глав."
author: "Ralph Kimball, Margy Ross"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling**, 3rd Edition — книга Ralph Kimball и Margy Ross (Wiley, 2013). Это главный учебник по `dimensional modeling`: как проектировать хранилище данных (DW/BI) так, чтобы бизнес его понимал, а запросы работали быстро. В книге 21 глава. Авторы опираются на более чем 60 лет опыта в реальных проектах.

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал. Схемы и данные для SQL придуманы заново.

![Карта книги: пять частей и главные темы каждой](/assets/data-warehouse-toolkit/book-map.png)

Схема показывает порядок чтения. Сначала основы и словарь. Потом одни и те же приёмы на примерах бизнеса и отраслей. Затем проект и ETL. В конце big data.

## О чём книга простыми словами

В компании есть два мира данных. Операционные системы (касса, заказы, CRM) записывают данные. Они работают с одной записью за раз и обычно хранят только текущее состояние. DW/BI-система читает данные. Аналитик спрашивает сразу про сотни тысяч записей и хочет видеть историю. Авторы критикуют «хранилища», которые просто копируют операционную базу на другой сервер. Такая копия не решает задачу аналитика.

Решение книги — `dimensional model`. В ней два вида таблиц. `Fact table` хранит измерения бизнес-процесса: сумму продажи, количество, длительность. `Dimension table` хранит описание: кто, что, где, когда, почему. Схема похожа на звезду, поэтому её называют `star schema`. Данные те же, что в нормализованной модели (3NF). Но форма проще для человека и быстрее для базы.

Главная модель мышления такая. Один бизнес-процесс — одна `fact table` на самом детальном `grain`. К ней подключены общие `dimension` (`conformed dimensions`). Из таких звёзд хранилище растёт по частям и не превращается в хаос. Проектирование идёт в четыре шага: процесс, `grain`, `dimensions`, `facts`. Остальная книга — это примеры: как тот же подход работает в рознице, банке, больнице, страховании и на сайте.

Ещё одна мысль авторов: DW/BI — это про бизнес, а не про технологию. Они сравнивают менеджера DW/BI с главным редактором журнала. Его задача — служить читателям, то есть бизнес-пользователям. Успех — когда бизнес реально пользуется системой. Поэтому, как пишут авторы, нужно быть наполовину DBA и наполовину MBA.

## Что нужно знать заранее

- SQL: `JOIN`, `GROUP BY`, агрегаты. Если нужно освежить, пройдите [практику по SQL](/practice/sql/).
- Что такое хранилище данных и чем оно отличается от операционной базы: [Хранилища данных](/processing/dw/).
- Первичный и внешний ключ, нормализация (3NF). Достаточно понимать, что таблицы связаны через ключи.
- Нужен мягкий вход перед книгой? Пройдите [базовый минимум Dimensional Modeling](/practice/modeling/): 11 уроков на данных одного магазина.

## Зачем читать

- Dimensional modeling — основа `dbt`-проектов и BI-витрин. Слои `fct_*` и `dim_*` пришли из этой книги.
- Книга нужна не только data engineer. Analytics engineer и аналитик тоже строят и читают star schema.
- Приёмы работают в любом хранилище: Snowflake, BigQuery, Redshift, DuckDB.
- Книга учит на примерах из отраслей. Вы сравниваете свой случай с готовым.
- Глава 2 — справочник: все приёмы моделирования на нескольких страницах.
- Книга говорит и о процессе: как собрать требования, провести workshop, построить ETL из 34 подсистем.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| Основы | 1–2 | Цели DW/BI, архитектура, star schema, справочник всех приёмов |
| Бизнес-процессы | 3–9 | Розница, склад, закупки, заказы, учёт, CRM, HR |
| Отрасли | 10–16 | Финансы, телеком, транспорт, образование, медицина, e-commerce, страхование |
| Проект и ETL | 17–20 | Жизненный цикл, процесс моделирования, 34 подсистемы ETL, разработка ETL |
| Big data | 21 | Big data рядом с хранилищем, лучшие практики |

Часть 1 даёт словарь. Части 2 и 3 — это один набор приёмов на разных примерах. В каждой главе появляются два-три новых приёма, а старые повторяются. Глава 16 собирает почти все приёмы в одном кейсе. Часть 4 переходит от таблиц к работе: как вести проект, моделировать с бизнесом и загружать данные. Часть 5 показывает, что те же идеи работают и для больших данных.

> **Пояснение:** книга вышла в 2013 году. Это наше дополнение, его нет в книге. Идеи dimensional modeling не устарели. Но глава 21 описывает Hadoop и MapReduce, а сегодня на их месте чаще облачные хранилища и lakehouse. ETL из глав 19–20 теперь часто делают как ELT: данные сначала грузят в хранилище, потом преобразуют внутри него, например в `dbt`. 34 подсистемы ETL остаются хорошим чек-листом.

## Краткое содержание

### Часть 1. Основы

**[Глава 1. DW/BI и основы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/)**

- Авторы начинают с целей, а не с технологий. Хранилище должно быть простым и быстрым, давать согласованные цифры, переживать изменения и защищать данные. Главное — чтобы бизнес принял систему.
- Менеджер DW/BI похож на главного редактора журнала: он думает о читателях, а не о печатном станке.
- Dimensional model — это `fact table` плюс `dimension table`. Та же модель в виде куба называется `OLAP cube`. Модель 3NF хороша для операций, но для BI она слишком сложная.
- В архитектуре Kimball четыре части: источники, ETL system (back room), presentation area и BI applications (front room). Данные в presentation area должны быть dimensional, atomic, по бизнес-процессам и на общих dimensions.
- Альтернативы: независимые data marts (цифры разных отделов не сходятся), hub-and-spoke Inmon (центральное хранилище в 3NF) и гибрид. Dimensional modeling подходит для любой из них.
- Авторы разбирают пять мифов: «только для summary», «только для отдела», «не масштабируется», «только для предсказуемых запросов», «нельзя интегрировать». На каждый есть ответ. Например, fact table с миллиардами строк — обычное дело.

**[Глава 2. Приёмы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/)**

- Это «официальный» справочник всех приёмов. Авторы не ждут, что вы прочтёте его подряд. У каждого приёма есть ссылка на главу с примером.
- Приёмы идут по группам: основы (требования, четыре шага, `grain`), fact tables, dimension tables, conformed dimensions и bus matrix, SCD типов 0–7, иерархии, сложные приёмы для facts и dimensions, особые схемы.
- Особые схемы: supertype и subtype для разных продуктов, real-time fact tables, error event schema.
- Модель начинается с требований бизнеса и реальности данных. Её строят на совместных workshops с бизнесом.

### Часть 2. Бизнес-процессы

**[Глава 3. Продажи в рознице](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/)**

- Первый кейс: касса в сети продуктовых магазинов. Четыре шага: процесс, `grain`, `dimensions`, `facts`. Grain — одна строка чека.
- Facts бывают additive, semi-additive и non-additive. Проценты и цены за единицу не суммируют. Храните компоненты и считайте отношение в запросе.
- Dimensions делают широкими и плоскими. Иерархия товар → бренд → категория лежит в одной таблице. Календарь — отдельная `date dimension` с флагами: выходной, праздник, конец месяца.
- Особые случаи: `degenerate dimension` (номер чека без своей таблицы), `factless fact table` (какие товары были в акции) и строка «unknown» вместо `NULL` во внешнем ключе.
- Ключ dimension — `surrogate key`, а не ключ из источника. Не нормализуйте dimensions в snowflake без причины. Не делайте слишком много dimensions в одной fact table (`centipede`).

**[Глава 4. Склад](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)**

- У компании есть цепочка создания стоимости (`value chain`): закупка, приёмка, склад, магазин, продажа. Каждому шагу — своя звезда.
- Склад описывают тремя видами fact table. `Periodic snapshot` — остаток на конец периода. Он `semi-additive`: по времени остатки не суммируют. `Transaction` — каждое движение товара. `Accumulating snapshot` — путь партии по вехам, с лагами между ними.
- `Bus matrix` — главный план хранилища. Строки — бизнес-процессы, столбцы — общие dimensions. Типичные ошибки: строки по отделам, строки по отчётам, слишком общие столбцы вроде «человек», отдельный столбец для каждого уровня иерархии.
- `Conformed dimension` — одна и та же dimension для разных fact tables: одинаковые ключи, названия и значения. Бывает и урезанная версия (`shrunken`). Благодаря ей работает `drilling across`: сравнение показателей разных процессов.
- Согласование — задача управления данными (data governance). У каждой общей dimension нужен владелец. Это не мешает agile: вы строите по одному процессу, но на общих dimensions.

**[Глава 5. Закупки](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)**

- В закупках много событий: заявка, заказ поставщику, уведомление об отгрузке, приёмка, оплата. Бизнес видит эти события как разные процессы, у них разные источники и разные dimensions. Поэтому авторы выбирают отдельные fact tables, а не одну смешанную. Конвейер закупок дополняет `accumulating snapshot`.
- Главная часть главы — slowly changing dimensions (SCD): как хранить изменения атрибутов.
  - Type 0: оставить исходное значение.
  - Type 1: перезаписать. История теряется.
  - Type 2: добавить новую строку с новым `surrogate key` и датами действия. Это самый частый способ хранить историю.
  - Type 3: добавить столбец с предыдущим значением.
  - Type 4: вынести быстро меняющиеся атрибуты в `mini-dimension`.
  - Types 5, 6 и 7: гибриды. Они дают и историческое, и текущее значение атрибута.

**[Глава 6. Заказы](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)**

- Заказ, отгрузка и счёт часто становятся первым проектом хранилища. Grain заказа — одна строка заказа (`order line`).
- `Role-playing dimension`: одна таблица дат играет роли даты заказа, даты отгрузки и даты счёта. `Junk dimension` собирает мелкие флаги в одну таблицу. `Degenerate dimension` хранит номер заказа в fact table.
- Авторы показывают два плохих шаблона для «заголовок + строки». В первом заголовок копируют в огромную dimension, почти такую же большую, как fact table. Во втором заголовок и строки лежат в двух fact tables, и их приходится соединять. Правильно: перенести ключи заголовка в строки и распределить (`allocate`) суммы заголовка по строкам.
- Несколько валют: храните сумму в местной и в корпоративной валюте. Несколько единиц измерения: кладите коэффициенты пересчёта в fact table, а не в dimension. Так пользователь не ошибётся, а изменение коэффициента со временем учтётся.
- Счёт добавляет факты прибыли и убытков (P&L), но авторы предупреждают о спорных распределениях затрат. `Audit dimension` фиксирует, как строка попала в хранилище.
- `Accumulating snapshot` заказа показывает конвейер: заказ → отгрузка → счёт, с лагами между датами.

**[Глава 7. Бухгалтерский учёт](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/)**

- Главная книга (general ledger) хранится в двух видах: `periodic snapshot` остатков на закрытие периода и `transaction` проводок. Есть план счетов (`chart of accounts`) и несколько финансовых календарей.
- Итоги с начала года (YTD) не храните в fact table. Они не соответствуют `grain` и дают завышенные суммы. Считайте их в BI-слое.
- Бюджет проходит цепочку: бюджет → обязательства → платежи. Для бюджета берут grain «чистое изменение» (`net change`), а не снимки итогов. Отклонение от бюджета удобно держать в `consolidated fact table`.
- Иерархии бывают трёх видов: фиксированной глубины, слегка переменной и произвольной (`ragged`). Для произвольной глубины авторы советуют `bridge table`. Альтернатива — `pathstring`.
- OLAP хорошо подходит для финансового анализа. Пакетные финансовые решения нужно подключать через `conformed dimensions`.

**[Глава 8. CRM](/book-summaries/engineering/data-warehouse-toolkit/08-crm/)**

- Центр главы — `customer dimension`. Она включает разобранные имя и адрес (с учётом разных стран), даты, сегменты, оценки и агрегированные факты как атрибуты.
- Атрибуты с малым числом значений выносят в `outrigger`. Редкие и разнородные атрибуты (name-value) и связи «много ко многим» решает `bridge table`.
- Сложное поведение клиентов описывают так: `behavior study group` (когорта), `step dimension` для последовательности шагов, `timespan fact table` и индикаторы в fact table (удовлетворённость, аномалия).
- Единого клиента получают двумя путями: через MDM в источнике или в ETL, возможно с частичным согласованием. Не соединяйте две fact tables напрямую: сначала агрегируйте их отдельно.
- Глава заканчивается напоминанием о сложностях, когда данные нужны с очень малой задержкой.

**[Глава 9. HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/)**

- В HR сама `employee dimension` отвечает на много вопросов. История профиля хранится как `Type 2`, с точными временными метками и причиной изменения.
- Ежемесячный снимок численности (`headcount snapshot`) — основная fact table. Есть и события: приём, увольнение.
- Иерархия «сотрудник → руководитель» рекурсивная. Для подъёма и спуска по ней нужен `bridge`.
- Навыки сотрудника — атрибут с несколькими значениями. Его решают через `bridge table` или строку с ключевыми словами. Ответы опросов хранят как факты, а текстовые комментарии — отдельно.
- Авторы взвешивают плюсы и минусы готовых моделей и пакетных решений для HR.

### Часть 3. Отрасли

**[Глава 10. Финансовые услуги](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/)**

- Кейс — розничный банк. Начальный grain: один счёт в месяц. С двумя dimensions (месяц и счёт) модель слишком бедная. Нужна `dimension triage`: найти ещё dimensions (филиал, продукт, домохозяйство).
- Счёт и клиент связаны как «много ко многим». Это решает `bridge table` с весами (`weighting factor`). `Household dimension` объединяет клиентов в домохозяйство.
- В одной fact table может быть несколько `mini-dimensions`, например демография и риск-профиль клиента.
- `Dynamic value banding`: числовые факты разбивают на диапазоны через отдельную таблицу границ.
- У разных продуктов разные метрики. Решение: `supertype` fact table с общими метриками и `subtype` схемы для каждой линии бизнеса. Ещё один приём — `hot swappable dimensions`.

**[Глава 11. Телеком](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/)**

- Эта глава — не проектирование с нуля, а ревью черновой схемы биллинга. Авторы дают правила ревью: правильные участники, фасилитатор, два дня без отвлечений, домашнее задание, заметки.
- Типичные ошибки: неясный или смешанный `grain` (счёт против строки услуги), dimension почти такого же размера, как fact table, и временные «корзины» вместо `date dimension`.
- Другие ошибки: нет `surrogate keys`, нет описаний кодов, нет обязательства по conformity. Модель стоит пересматривать каждые 12–24 месяца.
- В конце главы — общая абстрактная dimension для географических данных. Её можно использовать в разных процессах.

**[Глава 12. Транспорт](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/)**

- Кейс — авиакомпания. Данные лежат на нескольких grain: сегмент полёта и весь маршрут пассажира. Для каждого grain своя fact table.
- Аэропорты вылета и прилёта — `role-playing dimensions`. Иногда связанные dimensions объединяют (класс обслуживания, пара городов), но авторы называют это исключением.
- Приёмы работают и для грузов, и для travel-сервисов, например для отелей.
- Даты и время: календари для разных стран держат как `outriggers`. Для нескольких часовых поясов храните и местное время, и стандартное (UTC), в отдельных dimensions даты и времени суток.

**[Глава 13. Образование](/book-summaries/engineering/data-warehouse-toolkit/13-education/)**

- `Accumulating snapshot` отслеживает путь абитуриента по этапам приёма. Тот же приём подходит для заявок на гранты.
- `Factless fact table` фиксирует событие без чисел: кто пришёл на день открытых дверей, кто записался на курс, кто был на занятии.
- Чтобы увидеть то, чего не случилось, авторы называют три пути: таблица покрытия (например, все помещения и все часовые блоки), явные строки со значением 0 и OLAP-куб.
- Для подсчёта в factless fact table добавляют искусственную метрику, равную 1.

**[Глава 14. Медицина](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/)**

- `Accumulating snapshot` ведёт счёт и оплату страховой претензии. В нём несколько ролей даты и врача.
- Диагнозов у пациента несколько, поэтому нужна `bridge table`. Весов в ней обычно нет, потому что трудно задать правила. Часто достаточно отметки «основной».
- Разные виды начислений описывают через `supertype` и `subtype`.
- В электронных медицинских картах измерения разнородные и редкие. Для них нужна `measure type dimension`. Комментарии и изображения хранят отдельно.
- Использование оборудования и помещений — это `transaction` или `periodic snapshot`. Данные в медицине часто меняют задним числом, и об этом надо помнить в ETL.

**[Глава 15. E-commerce](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/)**

- Clickstream — это лог событий на сайте. Сложно определить источник визита, границы сессии и самого посетителя.
- Новые dimensions: `page`, `event`, `session`, `referral`. Fact tables строят на двух grain: сессия и событие страницы. Для порядка шагов есть `step dimension`.
- Google Analytics авторы считают внешним хранилищем про ваш сайт. Его данные можно подключать к общей модели.
- Clickstream нужно связать с остальным бизнесом через `conformed dimensions`. Прибыльность веб-канала считают, если правильно разнести затраты на продажи.

**[Глава 16. Страхование](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/)**

- Последний кейс собирает почти все приёмы книги для страховой компании. Сначала по требованиям рисуют bus matrix, потом строят модели.
- Для полисов и претензий есть три вида схем: `transaction`, `periodic snapshot` (премии) и `accumulating snapshot` (жизнь претензии). Их дополняют consolidated fact table для полисов и претензий и factless fact table для аварий.
- Применяются role-playing, SCD, `mini-dimensions` для быстро меняющихся атрибутов, `bridge`, `degenerate`, `audit` и `junk` dimensions, а также supertype и subtype.
- В конце — десять типичных ошибок моделирования. Среди них: текстовые атрибуты в fact table, экономия на описаниях, ключи источника вместо `surrogate keys`, нет объявленного `grain`, проектирование по отчёту и отсутствие conformed dimensions.

### Часть 4. Проект и ETL

**[Глава 17. Жизненный цикл Kimball](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/)**

- Глава — краткий курс по проекту DW/BI от идеи до сопровождения. Она нужна не только менеджерам: всей команде полезно видеть общую картину.
- Старт — планирование проекта: готовность организации, границы и обоснование, команда, план. Затем сбор требований через интервью, ориентированные на данные, и приоритеты по ценности для бизнеса и реализуемости.
- Дальше идут три параллельные дорожки. Технологическая: архитектура и выбор продуктов. Данных: dimensional modeling, физический дизайн (индексы, агрегаты, OLAP) и ETL. BI-приложений: спецификация и разработка.
- В конце — развёртывание, поддержка и рост. Авторы перечисляют и частые ошибки проекта.

**[Глава 18. Процесс моделирования](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/)**

- Модель рождается в серии workshops с бизнесом и владельцами данных (data stewards). Перед стартом: собрать участников, изучить требования, подготовить инструменты (modeling tool, data profiling) и правила имён.
- Сначала рисуют общую схему «пузырями» (bubble chart) из bus matrix. Потом детально описывают dimensions и facts, выбирают технику SCD и документируют таблицы.
- Затем модель проверяют: ИТ-ревью, группа ключевых пользователей, более широкая бизнес-аудитория. Авторы называют ориентир: три–четыре недели на один бизнес-процесс.
- Названия столбцов — скорее политика, чем техника. Их нужно согласовать со всей организацией.

**[Глава 19. Подсистемы ETL](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)**

- ETL съедает непропорционально много сил. Авторы против подхода «зависит от ситуации» и выделяют 34 подсистемы, которые нужны почти в каждом хранилище.
- Сначала собирают требования: бизнес-потребности, комплаенс, качество данных, безопасность, интеграция, задержка, архивы и lineage, интерфейсы BI, навыки команды.
- Подсистемы в четырёх группах.
  - Extract (1–3): data profiling, change data capture, extract system.
  - Cleaning и conforming (4–8): очистка, error event schema, audit dimension, дедупликация, conforming.
  - Delivery (9–21): SCD manager, генератор `surrogate key`, иерархии, специальные dimensions, загрузчики fact tables, surrogate key pipeline, bridge, поздние данные, агрегаты, OLAP-кубы.
  - Management (22–34): планировщик, backup, restart, версии, мониторинг, lineage, эскалация проблем, параллелизм, безопасность, комплаенс, metadata.
- Для change data capture авторы описывают пять способов: audit columns, timed extracts, full diff compare, чтение логов БД и мониторинг очереди сообщений.

**[Глава 20. Разработка ETL](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/)**

- Глава — план из десяти шагов. Планирование: общая схема, выбор ETL-инструмента, стратегии по умолчанию, детализация по каждой целевой таблице.
- Затем разовая историческая загрузка: сначала dimensions, потом fact tables. И затем инкрементальная загрузка: dimensions, fact tables, агрегаты и OLAP, автоматизация работы.
- Историческая и инкрементальная загрузки сильно различаются. Авторы советуют держать их отдельно.
- Лучше брать коммерческий ETL-инструмент, чем набор скриптов, даже если он дорогой. ETL-система живёт долго, её передают другим людям.
- Real-time: по мере снижения задержки падает качество данных. Бизнес должен участвовать в этом компромиссе. Авторы описывают приёмы: заменить файлы потоком, ограничить проверки качества, грузить факты вместе с dimensions, убрать staging, держать real-time partition.

### Часть 5. Big data

**[Глава 21. Big data](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/)**

- Big data — это не только размер. Это структурированные, полуструктурированные и неструктурированные данные в разных форматах. Многие из них нельзя анализировать SQL-подобным языком. Авторы считают это сменой парадигмы.
- Две архитектуры: расширенная реляционная СУБД и MapReduce/Hadoop. Первая сильна индексированными выборками и транзакциями, вторая — полными сканами и сложными структурами. Авторы ждут, что они будут сосуществовать.
- Практики управления: стройте среду вокруг аналитики, не создавайте «наследие» слишком рано, растите из результатов песочницы, начинайте с простых приложений.
- Практики архитектуры: «шоссе данных» из кэшей с разной задержкой, извлечение фактов из сырых данных, качество данных, потоковая обработка, прототипы в частном облаке.
- Практики моделирования: думайте dimensionally, соединяйте источники через `conformed dimensions`, используйте `durable surrogate keys` и SCD, объявляйте структуру данных при анализе.
- Практики governance: «big data governance» отдельно не существует. Сначала приведите данные к dimensions, потом применяйте governance. Приватность — самый важный взгляд на управление.

## Главные идеи

| Идея | Глава |
|---|---|
| Четыре шага: процесс, `grain`, dimensions, facts | [3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) |
| Atomic `grain`: детали хранятся всегда, summary только дополняет | [1](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/), [3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) |
| Три типа fact table: transaction, periodic snapshot, accumulating snapshot | [4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/), [6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/) |
| Bus matrix и conformed dimensions: как соединять звёзды | [4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/), [18](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/) |
| Slowly changing dimensions (SCD 0–7) | [5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/), [2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) |
| Junk, role-playing, degenerate dimensions | [3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/), [6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/) |
| Bridge table для связи «много ко многим» и иерархий | [7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/), [8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/), [10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/), [14](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/) |
| Mini-dimension для быстро меняющихся атрибутов | [5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/), [8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/), [10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) |
| Factless fact table: событие и покрытие | [3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/), [13](/book-summaries/engineering/data-warehouse-toolkit/13-education/) |
| Supertype и subtype для разных продуктов | [10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/), [14](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/), [16](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/) |
| Ревью модели и список типичных ошибок | [11](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/), [16](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/) |
| 34 подсистемы ETL и 10 шагов разработки | [19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/), [20](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/) |
| Dimensional подход для big data | [21](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/) |

## Как читать

- **Новичок.** Главы 1–3, затем 4 и 6. После них хватает для первой витрины.
- **Analytics engineer.** Главы 2, 3, 6, 8, 9. Затем 19–20 про загрузку.
- **Data engineer.** Главы 2, 19, 20 и отраслевая глава, близкая к вашей работе.
- **Руководитель.** Главы 1, 17, 18.

## Как работать с практикой

- Установите DuckDB: `brew install duckdb` или откройте [shell.duckdb.org](https://shell.duckdb.org).
- Данные в каждой главе создаются SQL-кодом. Файлы скачивать не нужно.
- Блоки кода идут по порядку. Выполняйте их сверху вниз в одной сессии.
- Сначала решайте задание сами. Потом открывайте решение.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. DW/BI и основы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/) | Архитектура DW/BI, Kimball и Inmon, star schema и OLAP |
| [2. Приёмы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) | Справочник приёмов: SCD, виды fact table, conformance |
| [3. Продажи в рознице](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) | Четыре шага проектирования, star schema |
| [4. Склад](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/) | Snapshot, accumulating snapshot, semi-additive |
| [5. Закупки](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/) | Заказы поставщикам, SCD типов 0–7 |
| [6. Заказы](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/) | Заголовок и строки, role-playing, pipeline |
| [7. Бухгалтерский учёт](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/) | Главная книга, бюджеты, иерархии |
| [8. CRM](/book-summaries/engineering/data-warehouse-toolkit/08-crm/) | Клиент 360, mini-dimension, поведение |
| [9. HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/) | История сотрудников, иерархии, навыки |
| [10. Финансовые услуги](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) | Счета, домохозяйства, bridge |
| [11. Телеком](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/) | Ревью модели, биллинг, география |
| [12. Транспорт](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/) | Маршруты и сегменты, role-playing, часовые пояса |
| [13. Образование](/book-summaries/engineering/data-warehouse-toolkit/13-education/) | Приём, регистрация, посещаемость |
| [14. Медицина](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/) | Диагнозы, bridge с весами |
| [15. E-commerce](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/) | Clickstream, сессии, воронки |
| [16. Страхование](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/) | Полисы, покрытия, убытки |
| [17. Жизненный цикл Kimball](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/) | Этапы DW/BI-проекта |
| [18. Процесс моделирования](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/) | Bus matrix, workshops, проверка grain |
| [19. Подсистемы ETL](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/) | 34 подсистемы ETL |
| [20. Разработка ETL](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/) | Проектирование и запуск ETL |
| [21. Big data](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/) | Big data и dimensional modeling |
