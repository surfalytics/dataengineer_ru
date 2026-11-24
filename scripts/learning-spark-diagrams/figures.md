# Figures: Learning Spark, 2nd Edition

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | Figure 1-1 | MapReduce пишет промежуточный результат на диск между map и reduce | ch01-mr-vs-spark.png (вместе со Spark в памяти) | redrawn |
| 1 | Figure 1-2 | Экосистема коннекторов Spark | — | skipped: логотипы источников, идея есть в тексте и на ch01-stack.png |
| 1 | Figure 1-3 | Компоненты Spark как единый стек | ch01-stack.png | redrawn |
| 1 | Figure 1-4 | driver, cluster manager, executor | ch01-architecture.png | redrawn |
| 1 | Figure 1-5 | Данные распределены по машинам как partition | ch01-partitions.png | redrawn (вместе с 1-6) |
| 1 | Figure 1-6 | Каждое ядро executor берёт свою partition | ch01-partitions.png | redrawn |
| 1 | Figure 1-7 | Spark на GitHub (скриншот статистики) | — | skipped: скриншот, цифры даны в тексте |
| 2 | Figure 2-1 | Страница загрузки Spark | — | skipped: скриншот, шаги описаны в тексте |
| 2 | Figure 2-2 | Компоненты общаются через driver в кластере | — | skipped: то же, что ch01-architecture.png, на странице ссылка на главу 1 |
| 2 | Figure 2-3 | driver делает из приложения один или несколько job | ch02-job-stage-task.png | redrawn (вместе с 2-4 и 2-5) |
| 2 | Figure 2-4 | job делится на stage | ch02-job-stage-task.png | redrawn |
| 2 | Figure 2-5 | stage делится на task по partition | ch02-job-stage-task.png | redrawn |
| 2 | Figure 2-6 | Lazy transformations и eager action | ch02-lazy.png | redrawn |
| 2 | Figure 2-7 | Narrow и wide transformations | ch02-narrow-wide.png | redrawn |
| 2 | Figure 2-8 | DAG простого примера в Spark UI | — | skipped: скриншот Spark UI, описан в тексте |
| 2 | Figure 2-9 | Детали stage 0 в Spark UI | — | skipped: скриншот Spark UI |
| 2 | Figure 2-10 | Databricks Community Edition | — | skipped: скриншот |
| 2 | Figure 2-11 | Распределение M&M по цветам | — | skipped: декоративная диаграмма с рекламной картинки |
| 2 | (наш) | Три шага главы и Spark UI | ch02-steps.png | drawn (главная схема) |
| 3 | (своя) | RDD для Spark непрозрачен, DataFrame показывает намерение | ch03-opaque-vs-structured.png | redrawn (своя схема) |
| 3 | Figure 3-1 | Structured API: DataFrame и Dataset над Spark SQL и RDD | ch03-structured-apis.png | redrawn |
| 3 | Figure 3-2 | Когда SQL, DataFrame и Dataset ловят ошибки | — | skipped: передана таблицей в тексте |
| 3 | Figure 3-3 | Spark SQL и компоненты вокруг | — | skipped: список в тексте, стек уже на ch01-stack.png |
| 3 | Figure 3-4 | Четыре фазы Catalyst | ch03-catalyst-phases.png | redrawn |
| 3 | Figure 3-5 | Пример преобразования запроса: фильтр ниже join | ch03-pushdown.png | redrawn |
| 4 | Figure 4-1 | Коннекторы и источники данных Spark SQL | ch04-sql-connectors.png | redrawn |
| 4 | — (наша схема) | Managed и unmanaged таблицы: что удаляет DROP TABLE | ch04-managed-unmanaged.png | own |
| 4 | — (наша схема) | DataFrameReader, DataFrame, DataFrameWriter | ch04-reader-writer.png | own |
| 5 | Figure 5-1 | Spark UI: стадии `pandas UDF` (parallelize, mapPartitions, WholeStageCodegen, ArrowEvalPython) | — | skipped: скриншот Spark UI, шаги описаны в тексте |
| 5 | Figures 5-2 – 5-8 | Tableau: диалог Connect, выбор Spark SQL, параметры, схема и таблица `people` | ch05-sql-access.png (общая схема подключения клиентов) | skipped: скриншоты Tableau, путь подключения показан на схеме |
| 5 | own | Клиенты (Beeline, Tableau, spark-sql) и внешние источники вокруг Spark SQL | ch05-sql-access.png | redrawn (наша схема) |
| 5 | own | JDBC: `numPartitions` и границы делят таблицу на параллельные запросы | ch05-jdbc-partitions.png | redrawn (наша схема) |
| 5 | own | Python UDF по строкам и `pandas UDF` пачками через Arrow | ch05-pandas-udf.png | redrawn (наша схема) |
| 6 | Figure 6-1 | Объект MyClass лежит одним блоком off-heap | ch06-encoders.png | redrawn (вместе с 6-2) |
| 6 | Figure 6-2 | Строка Tungsten: указатели и смещения | ch06-encoders.png | redrawn |
| 6 | Figure 6-3 | Цепочка lambda и DSL: SerDe на каждом переходе | ch06-lambda-vs-dsl.png | redrawn (сравнение с цепочкой из одного DSL) |
| 6 | — (наша схема) | Catalyst видит DSL и не видит lambda | ch06-catalyst-opaque.png | own |
| 7 | Figure 7-1 | Вкладка Environment в Spark UI | — | skipped: скриншот, идея описана в таблице вкладок |
| 7 | Figure 7-2 | Память executor: reserved, execution, storage | ch07-memory.png | redrawn |
| 7 | Figure 7-3 | Task, ядра, partition и параллелизм | — | skipped: та же идея нарисована в ch01-partitions.png (глава 1) |
| 7 | Figure 7-4 | Кэш в памяти по 12 partition (Storage) | — | skipped: скриншот Spark UI |
| 7 | Figure 7-5 | Кэш на диске по 12 partition (Storage) | — | skipped: скриншот Spark UI |
| 7 | Figure 7-6 | BHJ: маленькая таблица рассылается всем executor | ch07-broadcast-join.png | redrawn |
| 7 | Figure 7-7, 7-8 | Stages и Exchange до bucketing (Spark UI) | ch07-smj-bucketing.png | redrawn как схема (вместе с 7-9) |
| 7 | Figure 7-9 | После bucketing Exchange не нужен | ch07-smj-bucketing.png | redrawn |
| 7 | Figure 7-10 | Вкладки Spark UI | — | skipped: скриншот, вкладки перечислены в таблице |
| 7 | Figure 7-11 .. 7-18 | Jobs, Stages, Executors, Storage, SQL, Environment | — | skipped: скриншоты Spark UI, смысл в таблице и тексте |
| 7 | (наша) | Порядок приоритета настроек | ch07-config-order.png | drawn: в книге схемы нет |
| 8 | Figure 8-1 | Модель record-at-a-time: граф узлов, одна запись за раз | ch08-micro-batch.png (верхняя часть) | redrawn |
| 8 | Figure 8-2 | Micro-batch: поток режется на порции, каждая порция - набор tasks | ch08-micro-batch.png (нижняя часть) | redrawn |
| 8 | Figure 8-3 | Поток как бесконечная (unbounded) таблица | ch08-unbounded-table.png | redrawn |
| 8 | Figure 8-4 | Модель обработки: входная таблица, запрос, result table, sink, trigger | ch08-unbounded-table.png | redrawn (вместе с 8-3) |
| 8 | Figure 8-5 | Инкрементальное выполнение: цикл активного запроса | ch08-query-loop.png | redrawn |
| 8 | Figure 8-6 | Распределённый state на примере word count | ch08-state.png | redrawn |
| 8 | Figure 8-7 | Событие попадает в tumbling окно по event time | ch08-windows.png | redrawn (вместе с 8-8) |
| 8 | Figure 8-8 | Событие попадает в несколько sliding окон | ch08-windows.png | redrawn |
| 8 | Figure 8-9 | Result table после каждого trigger | — | skipped: те же окна; цифры по батчам даны в нашем коде с реальным выводом |
| 8 | Figure 8-10 | Watermark: максимум event time минус delay, поздние данные | ch08-watermark.png | redrawn |
| 8 | Figure 8-11 | Stream-stream join: оба потока буферизуются как state | ch08-join-state.png | redrawn |
| 8 | Figure 8-12 | Временная шкала показов и кликов и результат join | — | skipped: график с точками, идея в тексте и в нашем коде с выводом |
| 8 | Figure 8-13 | Пороги очистки state из watermark и условия по времени | ch08-join-state.png | redrawn (4 часа и 2 часа в подписях) |
| 9 | — | В главе нет рисунков. | — | skipped: рисунков в книге нет |
| 9 | own | База данных, data lake, lakehouse: свойства и переходы | ch09-evolution.png | redrawn (own) |
| 9 | own | Delta: пакетные и потоковые записи, transaction log, версии, time travel | ch09-delta-log.png | redrawn (own) |
| 9 | own | Schema enforcement и mergeSchema | ch09-schema.png | redrawn (own) |
| 10 | Figure 10-1 | Бинарная классификация (собака или нет) | — | skipped: картинки с собаками, идея в тексте |
| 10 | Figure 10-2 | Мультиклассовая классификация (порода) | — | skipped: то же, идея в тексте |
| 10 | Figure 10-3 | Регрессия: продажи мороженого по температуре | — | skipped: график, идея в тексте |
| 10 | Figure 10-4 | Кластеризация | — | skipped: график точек, идея в тексте |
| 10 | Figure 10-5 | Разбиение на train и test | ch10-cv.png | redrawn (вместе с 10-13) |
| 10 | Figure 10-6 | Линейная регрессия, остатки | — | skipped: график, формула и объяснение в тексте |
| 10 | Figure 10-7, 10-8 | Распределение цены и log-цены | — | skipped: гистограммы данных книги |
| 10 | Figure 10-9 | Decision tree: принять оффер или нет | ch10-tree.png | redrawn |
| 10 | Figure 10-10 | PLANET: распределённые деревья, maxBins | — | skipped: идея объяснена в тексте |
| 10 | Figure 10-11 | Random forest: обучение | ch10-forest.png | redrawn (вместе с 10-12) |
| 10 | Figure 10-12 | Random forest: предсказание | ch10-forest.png | redrawn |
| 10 | Figure 10-13 | k-fold cross-validation | ch10-cv.png | redrawn |
| 10 | (наша) | Transformer, Estimator, Pipeline, PipelineModel | ch10-pipeline.png | own |
| 10 | (наша) | StringIndexer, OneHotEncoder, VectorAssembler, пример Dog/Cat/Fish | ch10-ohe.png | own |
| 11 | Figure 11-1 | Четыре компонента MLflow | ch11-mlflow-components.png (вместе с путём модели: запуск, Tracking, Models, Registry, развёртывание) | redrawn |
| 11 | Figure 11-2 | Tracking server принимает логи из notebook, приложения, облачного job | ch11-mlflow-components.png | redrawn (часть общей схемы) |
| 11 | Figure 11-3 | MLflow UI (скриншот) | — | skipped: скриншот, описан в тексте |
| 11 | Figure 11-4 | Страница запуска random forest (скриншот) | — | skipped: скриншот |
| 11 | Figure 11-5 | Варианты развёртывания MLlib по задержке | ch11-deploy-options.png | redrawn |
| 11 | Figure 11-6 | MLflow Model Registry (скриншот) | — | skipped: скриншот, идея в тексте и в DuckDB-практике |
| 11 | Figure 11-7 | Распределённый подбор гиперпараметров | ch11-hyperparam-search.png | redrawn |
| 12 | Figure 12-1 | Фильтр из измерения попадает в факт-таблицу | ch12-dpp.png | redrawn (вместе с 12-2) |
| 12 | Figure 12-2 | Фильтр в scan факта при broadcast join | ch12-dpp.png | redrawn |
| 12 | Figure 12-3 | AQE пересматривает план во время работы | ch12-aqe.png | redrawn (вместе с 12-4) |
| 12 | Figure 12-4 | План в AQE перестраивается в точках материализации | ch12-aqe.png | redrawn |
| 12 | Figure 12-5 | Иерархия Catalog plugin API | — | skipped: уровни описаны в тексте, эксперимент |
| 12 | Figure 12-6 | Вкладка Structured Streaming, сводка | — | skipped: скриншот UI |
| 12 | Figure 12-7 | Вкладка Structured Streaming, детали | — | skipped: скриншот UI |
| 12 | — (свой) | pandas UDF: модель на каждый batch и один раз с Iterator | ch12-pandas-iterator.png | own |
| 0 | (наша) | Карта книги: 12 глав в четырёх блоках | ch00-book-map.png | drawn (обзор) |
