# Глоссарий: Analytics Engineering with SQL and dbt (Rui Machado, Hélder Russa)

Единые слова для всех глав. Правила: навык `book-summary`, раздел «Translation guide».
Колонка «Как пишем»: термин в обратных кавычках = оставляем английским; обычное слово = пишем по-русски.

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| analytics engineer | `analytics engineer` | аналитический инженер, инженер по аналитике | Моделирует данные в хранилище: SQL, `dbt`, тесты, документация |
| analytics engineering | `analytics engineering` | аналитическая инженерия | Дисциплина между data engineering и анализом данных |
| data engineer | дата-инженер | инженер данных | Строит и поддерживает пайплайны и платформу данных |
| data analyst | аналитик данных | дата-аналитик | Отвечает на бизнес-вопросы с помощью данных |
| data warehouse | хранилище данных (`data warehouse`) | склад данных | Структурированное хранилище для аналитики |
| data lake | `data lake` | озеро данных | Хранилище сырых файлов любого формата |
| data mart | витрина данных (`data mart`) | — | Готовый набор таблиц для одной области бизнеса |
| data mesh | `data mesh` | — | Подход: данными владеют доменные команды |
| data product | `data product` | — | Набор данных, которым управляют как продуктом: владелец, SLA, пользователи |
| data governance | `data governance` | — | Правила владения, доступа, качества и защиты данных |
| data lineage | `lineage` | линидж | Откуда пришли данные и куда пошли: граф зависимостей |
| data quality | качество данных | — | Насколько данные подходят для задач |
| data modeling | моделирование данных | — | Описание, как данные хранятся и связаны |
| data analytics lifecycle | жизненный цикл аналитики (`data analytics lifecycle`) | — | Путь от постановки задачи до мониторинга качества |
| data pipeline | `pipeline` | — | Цепочка шагов, которая переносит и преобразует данные |
| ETL / ELT | `ETL` / `ELT` | — | Extract, Transform, Load в разном порядке |
| legacy process | старый процесс (`legacy`) | — | Подход до `dbt`: ETL-инструменты и хранимые процедуры |
| stored procedure | хранимая процедура | — | SQL-код, который хранится и выполняется в базе |
| ETL tool | ETL-инструмент | — | Программа с визуальным интерфейсом для потоков данных |
| conceptual model | концептуальная модель | — | Первый этап: сущности и связи без деталей |
| logical model | логическая модель | — | Второй этап: атрибуты, ключи, связи |
| physical model | физическая модель | — | Третий этап: таблицы, типы, индексы в конкретной СУБД |
| normalization | нормализация | — | Разбиение таблиц, чтобы убрать дублирование |
| denormalization | денормализация | — | Объединение таблиц ради скорости чтения |
| dimensional modeling | `dimensional modeling` | размерное моделирование | Моделирование по Kimball: факты и измерения |
| star schema | `star schema` | звёздная схема | Таблица фактов в центре, измерения вокруг |
| snowflake schema | `snowflake schema` | снежинка | Звезда, где измерения нормализованы |
| Data Vault | `Data Vault` | — | Моделирование через hub, link, satellite |
| monolith data model | монолитная модель (`monolith`) | — | Одна большая модель вместо модулей |
| fact table | таблица фактов (`fact table`) | факт-таблица | Измеримые события: заказы, продажи |
| dimension table | таблица измерений (`dimension table`) | — | Описание контекста фактов: клиент, товар, дата |
| grain | `grain` | гранулярность, зернистость | Что означает одна строка таблицы фактов |
| surrogate key | `surrogate key` | суррогатный ключ | Искусственный ключ, не связанный с бизнесом |
| primary key | первичный ключ | — | Уникально определяет строку |
| foreign key | внешний ключ | — | Ссылка на ключ другой таблицы |
| modular data model | модульная модель | — | Модель из небольших переиспользуемых частей |
| staging model | `staging`-модель | — | Первый слой: чистка и переименование сырых данных |
| base model | `base`-модель | — | Простейший слой над источником |
| intermediate model | `intermediate`-модель | — | Промежуточные шаги логики между `staging` и `mart` |
| mart model | `mart`-модель | — | Итоговая модель для бизнеса |
| medallion architecture | `medallion architecture` | медальонная архитектура | Слои `bronze`, `silver`, `gold` |
| bronze / silver / gold layer | `bronze` / `silver` / `gold` | бронзовый слой | Сырые / очищенные / готовые к использованию данные |
| CTE | `CTE` | — | Common Table Expression: именованный подзапрос через `WITH` |
| window function | оконная функция | — | Считает по окну строк, не схлопывая их |
| dbt model | `model` | модель dbt | `SELECT`-запрос в файле, который `dbt` превращает в таблицу или `view` |
| materialization | `materialization` | материализация | Способ, как `dbt` сохраняет модель: `view`, `table`, `incremental`, `ephemeral` |
| incremental model | `incremental`-модель | инкрементальная модель | Обрабатывает только новые строки |
| ephemeral model | `ephemeral`-модель | — | Не создаёт объект в базе, встраивается как CTE |
| seed | `seed` | сид | CSV-файл в проекте, который `dbt` загружает как таблицу |
| snapshot | `snapshot` | снимок | Хранит историю изменений строк (как SCD2) |
| source | `source` | источник | Объявленная в YAML исходная таблица |
| macro | `macro` | макрос | Функция на Jinja для повторного SQL-кода |
| Jinja | Jinja | — | Шаблонизатор в `dbt` |
| generic test | `generic test` | общий тест | Готовый переиспользуемый тест: `unique`, `not_null` |
| singular test | `singular test` | — | Тест как отдельный SQL-файл |
| package | пакет (`package`) | — | Готовая библиотека макросов и моделей для `dbt` |
| dbt project | проект `dbt` | — | Папка с моделями, тестами и `dbt_project.yml` |
| dbt Cloud | dbt Cloud | — | Облачный сервис dbt (название продукта) |
| declarative language | декларативный язык | — | Описываем результат, а не шаги |
| version control | контроль версий | — | Хранение истории кода, обычно в `Git` |
| commit | `commit` | коммит | Сохранённая версия изменений в `Git` |
| branch | `branch` | ветка | Отдельная линия изменений в `Git` |
| pull request | `pull request` | — | Запрос на слияние ветки с обзором кода |
| CI/CD | `CI/CD` | — | Непрерывная интеграция и доставка кода |
| deployment | развёртывание (`deploy`) | — | Запуск проекта в рабочей среде |
| job | `job` | задание | Запланированный запуск команд `dbt` в `dbt Cloud` |
| DDL / DML / DCL | `DDL` / `DML` / `DCL` | — | Язык определения / изменения данных / управления доступом |
| DAG | `DAG` | — | Направленный граф зависимостей без циклов: задачи в Airflow, модели в `dbt` |
| data platform engineer | дата-инженер платформы | инженер платформы данных | Строит платформу и загружает сырые данные |
| OLTP | OLTP | — | Рабочая база приложения для транзакций |
| OLAP | OLAP | — | Аналитическая обработка данных |
| BI (business intelligence) | BI | бизнес-аналитика | Часть аналитики данных для бизнес-решений |
| data analytics | аналитика данных (`data analytics`) | — | Создание, визуализация и анализ бизнес-данных |
| schema-on-write / schema-on-read | schema-on-write / schema-on-read | — | Структура задаётся при записи / при чтении |
| on-premises | on-premises (свои серверы) | — | Инфраструктура в своём дата-центре |
| serverless | serverless | — | Сервис без управления серверами |
| data strategy | стратегия данных (`data strategy`) | — | План управления данными: облако, технологии, процессы, люди, правила |
| vendor lock-in | зависимость от поставщика | — | Уйти к другому поставщику дорого |
| data mining | data mining | — | Поиск закономерностей статистикой и ML |
| dashboard | дашборд | — | — |
| orchestration | оркестрация | — | Запуск задач по расписанию и зависимостям (Airflow, Dagster, Prefect) |
| modern data stack | modern data stack | — | Airflow, `dbt`, Looker и облачные хранилища |
| gemba | гемба | — | «Настоящее место», где создаётся ценность |
| source system | исходная система | источник | Глоссарий запрещает «источник» (это `source` в `dbt`), поэтому общий смысл пишем «исходная система» |
| entity | сущность | — | Объект реального мира в модели: книга, автор |
| attribute | атрибут | — | Свойство сущности, потом столбец таблицы |
| entity-relationship diagram | ERD | — | Диаграмма «сущность — связь» |
| cardinality | кардинальность | — | 1:1, 1:N, N:N |
| cross-reference / junction table | таблица связи (`cross-reference table`) | junction-таблица | Таблица для связи «многие ко многим» с составным ключом |
| first / second / third normal form | 1NF / 2NF / 3NF, первая / вторая / третья нормальная форма | — | Шаги нормализации |
| transitive dependency | транзитивная зависимость | — | C зависит от B, B от ключа A |
| hub / link / satellite | `hub` / `link` / `satellite` | хаб, сателлит | Три вида таблиц `Data Vault` |
| business key | бизнес-ключ | — | Идентификатор из самого бизнеса |
| hash key | `hash key` | — | Хеш бизнес-ключа, первичный ключ `hub` в Data Vault 2.0 |
| DRY | DRY (`Don't Repeat Yourself`) | — | Принцип «не повторяйся» |
| idempotency | идемпотентность | — | Повторный запуск даёт тот же результат |
| backfill | `backfill` | — | Пересчёт данных за прошлые периоды |
| query planner | планировщик запросов | — | Часть СУБД, которая строит план выполнения |
| drill-down / roll-up | `drill-down` / `roll-up` | — | Переход к деталям / к общим итогам |
| lakehouse | `lakehouse` | озерохранилище | `data lake` со свойствами хранилища: ACID, схема |
| open table format | открытый формат (Delta Lake, Iceberg, Hudi) | — | Формат таблиц поверх файлов в облаке |
| ACID | ACID | — | Атомарность, согласованность, изоляция, долговечность |
| CDC | CDC (`change data capture`) | — | Захват изменений в исходной системе |
| modularity | модульность | — | Деление модели на независимые части |
| DBMS | СУБД | — | Программа, которая создаёт базу и даёт с ней работать |
| DIKW pyramid | пирамида DIKW | — | Данные, информация, знание, мудрость |
| constraint | ограничение (`constraint`) | констрейнт | Правило для данных: PK, FK, UNIQUE, CHECK, NOT NULL |
| view | `view` | вью, представление | Виртуальная таблица: сохранённый запрос |
| result set | результирующая таблица (result set) | — | То, что вернул запрос |
| join | `JOIN` | джойн | Соединение таблиц |
| soft delete | `soft delete` | — | Пометка строки флагом вместо удаления |
| subquery | подзапрос | — | Запрос внутри запроса |
| NoSQL | `NoSQL` | — | Нереляционные базы |
| distributed SQL | distributed SQL | — | Одна логическая база на многих узлах |
| DataFrame | DataFrame | датафрейм | Таблица в памяти pandas / Polars / Spark |
| lazy evaluation | `lazy evaluation` (ленивое выполнение) | — | Сначала план и оптимизация, потом расчёт |
| endpoint | `endpoint` | — | Адрес API, который отдаёт данные |
| execution engine | движок выполнения (`ExecutionEngine`) | — | Где Fugue выполняет код: pandas, DuckDB, Spark, Dask, Ray |
| exercise (practice heading) | упражнения | задания | «Задание» в глоссарии занято под `job` |
| dbt Core | dbt Core | — | CLI-инструмент dbt с открытым кодом (название продукта) |
| source freshness | `source freshness` | свежесть источника | Проверка возраста сырых данных по полю времени загрузки |
| cascading scope priority | `cascading scope priority` | — | Более конкретная настройка перекрывает общую: проект, затем YAML папки, затем `config()` в модели |
| analysis | `analysis` (папка `analyses/`) | — | SQL-шаблон, который `dbt` компилирует, но не запускает в `dbt run` |
| doc block | `doc block` | — | Именованный фрагмент Markdown для описаний, вызывается через `doc()` |
| selection syntax | `selection syntax` | — | Язык выбора ресурсов для команд: имена, теги, пути, `+` |
| lineage graph | граф `lineage` | — | Граф зависимостей моделей, `dbt` строит его по `ref()` и `source()` |
| ref() / source() | `ref()` / `source()` | — | Функции Jinja: ссылка на модель / на объявленную сырую таблицу |
| threads | `threads` | — | Сколько моделей `dbt` строит параллельно |
| profile / target | `profile` / `target` | — | Профиль подключения в `profiles.yml` / среда внутри профиля (`dev`, `prod`) |
| environment (development / deployment) | среда (development / deployment) | окружение | Где выполняется код: среда разработки или рабочая среда |
| EL tool | EL-инструмент | — | Инструмент, который извлекает и загружает данные без трансформации |
| data platform | платформа данных | — | BigQuery, Snowflake, Databricks, Redshift и другие |
| service account | сервисный аккаунт | — | Технический аккаунт Google Cloud, через который `dbt` подключается к BigQuery |
| persist_docs | `persist_docs` | — | Настройка, которая записывает описания таблиц и колонок в базу |
| data tests (dbt 1.8+) | `data_tests` | — | Новое имя ключа `tests:` в YAML с `dbt` 1.8 |
| table (materialization) | `table` | — | Модель сохраняется как таблица с данными на диске |
| materialized view | `materialized view` | материализованное представление | Хранит результат запроса, платформа сама его обновляет |
| dynamic table | `dynamic table` | динамическая таблица | Аналог `materialized view` в Snowflake |
| incremental strategy | стратегия загрузки (`incremental_strategy`) | — | Как `incremental`-модель пишет новые строки: `merge`, `append`, `insert_overwrite` |
| full refresh | `full refresh` | полное обновление | Пересборка `incremental`-модели с нуля (`--full-refresh`) |
| slowly changing dimension type 2 | `SCD2` | — | Каждая версия строки хранится отдельно, с периодом действия |
| target (dbt) | `target` | — | Профиль подключения, с которым запущен `dbt`: `dev`, `prod`, `deploy` |
| compiled code | скомпилированный SQL | — | SQL после того, как `dbt` подставил Jinja, `ref` и `source` |
| semantic layer | `semantic layer` | семантический слой | Слой с общими определениями метрик над моделями |
| semantic model | `semantic model` | семантическая модель | YAML-описание модели: `entities`, `dimensions`, `measures` |
| entity (semantic layer) | `entity` | — | Ключ (ID), по которому `semantic layer` связывает модели. Обычная «сущность» из моделирования — отдельный термин |
| dimension (semantic layer) | `dimension` | — | Атрибут, по которому режут метрику: дата, статус |
| measure | `measure` | мера | Числовое поле с агрегацией: `sum`, `count_distinct` |
| metric | метрика (`metric`) | — | Показатель для бизнеса, построен на `measure` |
| MetricFlow | MetricFlow | — | Семантический движок `dbt`, строит SQL для метрик |
| date spine | `date spine` | — | Непрерывный ряд дат без пропусков |
| omnichannel | омниканальный | — | Клиент работает с компанией через несколько каналов, компания видит его путь целиком |
| conformed dimension | `conformed dimension` | согласованное измерение | Измерение, общее для нескольких таблиц фактов |
| natural key | `natural key` | естественный ключ, натуральный ключ | Ключ строки из исходной системы (`nk_`) |
| audit columns | служебные колонки (`CREATED_AT`, `UPDATED_AT`) | — | Время создания и изменения строки, нужны для инкрементальной выгрузки |
| information_schema | `information_schema` | — | Служебная схема СУБД с метаданными о таблицах и колонках |
| bounce | отказ (`bounce`) | — | Уход из канала без каких-либо действий |
| bounce rate | доля отказов (`bounce rate`) | — | Доля визитов, которые закончились отказом |
| naming convention | соглашение об именах | — | Префиксы `stg`, `dim`, `fct`, `sk`, `nk`, `mtr`, `dsc`, `dt` |
| ERD | `ERD` | — | Entity-relationship diagram: диаграмма сущностей и связей |
| referential integrity | ссылочная целостность | — | Внешний ключ ссылается только на существующие строки |
| environment (dbt Cloud) | среда (`environment`) | окружение | Набор настроек запуска: development или production |
| business process | бизнес-процесс | — | Операция бизнеса, которую описывает таблица фактов |
| cross-sell / upsell | `cross-sell` / `upsell` | — | Продажа сопутствующих / более дорогих товаров |
