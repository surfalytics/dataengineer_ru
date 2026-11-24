# Glossary: Learning Spark, 2nd Edition

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| unified analytics engine | единый движок аналитики (`unified analytics engine`) | унифицированный аналитический движок | Один движок для SQL, streaming, ML и графов. Так книга называет Spark |
| data pipeline | `pipeline` | пайплайн | Цепочка шагов, которая двигает и меняет данные |
| driver | `driver` | драйвер | Процесс с `SparkSession`. Строит план и раздаёт работу `executor` |
| executor | `executor` | исполнитель, экзекьютор | Процесс на узле. Выполняет `task` и держит данные |
| job | `job` | джоб | Результат одного `action`. Делится на `stage` |
| stage | `stage` | стадия, этап | Часть `job` между двумя `shuffle` |
| task | `task` | таск | Одна единица работы на одной `partition`. Идёт на одном ядре `executor` |
| DAG | `DAG` | даг | Граф шагов, который Spark строит из кода |
| DataFrame | `DataFrame` | датафрейм, дата-фрейм | Распределённая таблица с именованными колонками |
| Dataset | `Dataset` | датасет | Типизированный API для Scala и Java. Не путать с набором данных |
| partition | `partition` | партиция | Часть данных, которую берёт один `task`. Не путать с `partitioning` на диске |
| repartition / coalesce | `repartition` / `coalesce` | репартиция | Изменить число `partition`. `coalesce` без `shuffle` |
| transformation | `transformation` | трансформация без пояснения | Шаг, который не запускает работу. Например `filter` |
| action | `action` | экшен, действие | Шаг, который запускает работу. Например `count`, `show` |
| lazy evaluation | `lazy evaluation` (ленивое вычисление) | отложенное вычисление, ленивая оценка | План строится сразу, выполняется при `action` |
| narrow / wide transformation | `narrow` / `wide transformation` | узкая / широкая | `Narrow` не двигает данные между `partition`. `Wide` вызывает `shuffle` |
| lineage | `lineage` | линидж | История шагов, из которых Spark пересчитает потерянную `partition` |
| shuffle | `shuffle` | шафл, перемешивание | Перенос данных между узлами по ключу. Самая дорогая операция |
| fault tolerance | отказоустойчивость | устойчивость к ошибкам | Spark пересчитывает потерянное по `lineage` |
| schema inference | `schema inference` (вывод схемы) | угадывание схемы | Spark сам читает данные и выводит типы. Медленно и ненадёжно |
| schema on read | `schema on read` | — | Схема применяется при чтении, а не при записи |
| Catalyst optimizer | `Catalyst` | оптимизатор катализатор | Оптимизатор запросов Spark SQL |
| predicate pushdown | `predicate pushdown` | проталкивание предикатов | Фильтр ближе к источнику. Читаем меньше данных |
| UDF | `UDF` (`user-defined function`) | юдф | Своя функция, которую вызывают из SQL или `DataFrame` |
| pandas UDF | `pandas UDF` | — | `UDF` на Python, которая работает с `pandas` и `Arrow` пачками |
| temporary view | `temporary view` | временное представление | Живёт, пока живёт `SparkSession`. Читается из SQL |
| managed table | `managed table` | управляемая таблица | Spark хранит и данные, и метаданные. `DROP` удаляет оба |
| unmanaged table | `unmanaged table` | неуправляемая таблица, внешняя таблица | Spark хранит только метаданные. `DROP` не трогает данные |
| bucketing | `bucketing` | бакетирование | Раскладка таблицы по `bucket` по hash ключа. Помогает избежать `shuffle` при join |
| broadcast join | `broadcast join` | — | Маленькую таблицу копируют на все `executor`. `Shuffle` не нужен |
| skew | `skew` | перекос данных | Один ключ несёт много данных. Один `task` тормозит всех |
| cache / persist | кэш (`cache`, `persist`) | кеш, кешировать | Держим результат в памяти или на диске. `persist` задаёт уровень хранения |
| broadcast variable | `broadcast variable` | широковещательная переменная | Копия значения на каждом `executor` |
| adaptive query execution | `AQE` (`adaptive query execution`) | адаптивное выполнение | Spark меняет план по статистике во время работы |
| stream | потоковая обработка (`stream`) | стриминг | Данные приходят без конца |
| Structured Streaming | `Structured Streaming` | структурированный стриминг | Потоковый движок на `DataFrame`. Название продукта |
| micro-batch | `micro-batch` | микробатч, микро-пакет | Маленькая порция данных, которую Spark обрабатывает за раз |
| trigger | `trigger` | триггер без пояснения | Правило: как часто запускать `micro-batch` |
| source / sink | `source` / `sink` | сорс, синк | Откуда поток читают и куда пишут |
| stateful / stateless | `stateful` / `stateless` | — | С памятью между `micro-batch` и без неё |
| event time / processing time | `event time` / `processing time` | — | Когда событие случилось и когда его обработали |
| watermark | `watermark` | вотермарк, водяной знак | Порог: насколько позже события ещё принимаем. Старое состояние удаляем |
| late data | `late data` | запоздавшие данные без пояснения | События, которые пришли позже `watermark` |
| checkpoint | `checkpoint` | чекпоинт, контрольная точка | Сохранённая позиция и состояние запроса. Нужен для восстановления |
| exactly-once | `exactly-once` | ровно-один-раз | Эффект ровно один раз, даже при повторах |
| data lake | `data lake` | озеро данных | Хранилище файлов любого формата |
| lakehouse | `lakehouse` | озерохранилище | Файлы озера плюс таблицы и транзакции |
| transaction log | `transaction log` | журнал транзакций, delta log | Журнал изменений таблицы Delta Lake |
| time travel | `time travel` | путешествие во времени | Чтение таблицы на прошлый момент |
| upsert / merge | `MERGE` / `upsert` | апсерт, мёрдж | Вставка или обновление по ключу |
| schema enforcement / evolution | `schema enforcement` / `schema evolution` | принудительная схема, эволюция схемы | Запись с чужой схемой отклоняют / схему меняют явно |
| estimator / transformer | `estimator` / `transformer` | оценщик, трансформер без пояснения | `Estimator` учится на данных (`fit`). `Transformer` меняет `DataFrame` (`transform`) |
| ML pipeline | `ML pipeline` | пайплайн | Цепочка `transformer` и `estimator` для ML |
| feature engineering | `feature engineering` | инжиниринг признаков | Подготовка признаков для модели |
| cross-validation | `cross-validation` (кросс-валидация) | перекрёстная проверка | Данные делят на части и по очереди проверяют модель |
| RDD (Resilient Distributed Dataset) | `RDD` | — | Базовая структура Spark. На ней построены `DataFrame` и `Dataset` |
| Spark SQL / MLlib / GraphX | `Spark SQL`, `MLlib`, `GraphX` | — | Названия компонентов, пишем как в книге |
| SparkSession | `SparkSession` | — | Единая точка входа в Spark 2.x |
| cluster manager | cluster manager | менеджер кластера | Выдаёт ресурсы узлов. Standalone, YARN, Mesos, Kubernetes. Без backticks, как в таблицах книги |
| Tungsten | Tungsten | — | Физический движок, whole-stage code generation. Название продукта |
| data locality | data locality | локальность данных | Task идёт к ближайшей partition |
| deployment mode | режим развёртывания | — | local, standalone, YARN client/cluster, Kubernetes |
| continuous applications | `continuous applications` | — | Название модели из книги: один pipeline для потоков и статических данных |
| gang scheduler | gang scheduler | — | Планировщик для распределённого deep learning (Project Hydrogen) |
| local mode | `local mode` | локальный режим | Вся обработка на одной машине. Для учёбы и прототипов |
| Spark shell | shell | — | Интерактивная оболочка: `pyspark`, `spark-shell`, `spark-sql`, `sparkR` |
| Spark UI | Spark UI | — | Веб-интерфейс на порту 4040: `job`, `stage`, `task` |
| spark-submit | `spark-submit` | — | Скрипт запуска приложения из `bin` |
| application | application | приложение Spark без пояснения | Программа на Spark: `driver` и `executor`. В тексте можно писать «приложение» |
| immutability | неизменяемость (`immutability`) | иммутабельность | `DataFrame` не меняется, `transformation` даёт новый |
| accumulator | накопитель (`accumulator`) | аккумулятор | Счётчик, который обновляют `task` |
| sbt | `sbt` | — | Инструмент сборки Scala-проектов, `build.sbt` |
| Structured APIs | `Structured API` | структурированные API | `DataFrame`, `Dataset` и SQL. В заголовке: «Structured API в Spark» |
| schema | схема (`schema`) | — | Имена колонок и их типы |
| DSL (domain-specific language) | `DSL` | — | Набор операторов `select`, `filter`, `groupBy`. Они говорят, что считать |
| DDL string | `DDL`-строка | — | Схема строкой: `author STRING, pages INT` |
| Row | `Row` | строка-объект | Общий объект строки: упорядоченный набор полей |
| Column | `Column` | — | Объект колонки. `col("x")` возвращает `Column` |
| projection | `projection` | проекция без пояснения | `select`: оставить только нужные колонки |
| DataFrameReader / DataFrameWriter | `DataFrameReader` / `DataFrameWriter` | — | Интерфейсы чтения и записи |
| Parquet | Parquet | паркет | Колоночный формат. Хранит схему в метаданных |
| case class | `case class` | — | Класс Scala, по нему строят `Dataset[T]` |
| encoder | `encoder` | кодировщик | Превращает JVM-объект в бинарный формат Spark и обратно |
| type safety | проверка типов (`type safety`) | типобезопасность | Ошибки типов ловит компилятор |
| Catalyst phases | `Analysis`, `Logical optimization`, `Physical planning`, `Code generation` | физическое планирование | Четыре фазы Catalyst, названия как в книге |
| Catalog | `Catalog` | — | Внутренний список таблиц, колонок, типов и функций |
| whole-stage code generation | `whole-stage code generation` | — | Весь `stage` склеивается в одну функцию |
| cost-based optimizer (CBO) | `CBO` | — | Выбирает план по оценке стоимости |
| metastore | `metastore` | метахранилище | Центральное хранилище метаданных таблиц. По умолчанию Hive metastore |
| global temporary view | `global temporary view` | глобальное временное представление | View для всех `SparkSession` приложения. Читается через `global_temp` |
| Data Sources API | Data Sources API | — | Единый интерфейс чтения и записи встроенных источников |
| Parquet / Avro / ORC | Parquet, Avro, ORC | — | Названия форматов, без backticks |
| parse mode | `mode` (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`) | — | Что делать с плохими строками при чтении |
| save mode | `mode` (`append`, `overwrite`, `ignore`, `errorifexists`) | — | Что делать, если данные уже есть при записи |
| vectorized reader | векторизованный reader | — | Читает блоки строк (около 1024) за раз |
| columnar format | колоночный формат | столбцовый | Данные хранятся по колонкам |
| Thrift JDBC/ODBC server (STS) | `Thrift server` | — | Сервер, через который Beeline и BI-инструменты ходят в Spark SQL по JDBC и ODBC |
| Beeline | `Beeline` | — | Консольный JDBC-клиент. Название утилиты |
| JDBC | `JDBC` | — | Стандарт подключения к базам из Java |
| JDBC driver (jar базы) | `jar` базы, «библиотека базы» | драйвер | Слово «драйвер» занято: `driver` — это процесс Spark |
| pandas UDF / vectorized UDF | `pandas UDF` | векторная UDF без пояснения | Принимает `pandas.Series`, данные идут пачками через Arrow |
| Apache Arrow | Arrow | — | Колоночный формат обмена между JVM и Python |
| higher-order function | `higher-order function` | — | Функция, которая принимает лямбду. `transform`, `filter`, `exists`, `reduce` |
| window function | оконная функция (`window function`) | — | Считает по окну строк и возвращает значение для каждой строки |
| pivot | `pivot` | поворот | Значения колонки становятся заголовками колонок |
| stride | `stride` | — | Шаг между границами соседних запросов при JDBC-чтении |
| numPartitions / partitionColumn / lowerBound / upperBound | `numPartitions`, `partitionColumn`, `lowerBound`, `upperBound` | — | Свойства параллельного JDBC-чтения |
| classpath | `classpath` | — | Список jar, которые видит JVM |
| serialization / deserialization (SerDe) | `SerDe` | — | Объект в байты и обратно |
| case class / JavaBean | `case class`, `JavaBean` | кейс-класс | Класс, который задаёт схему `Dataset` |
| DSL | `DSL` | — | Операторы `DataFrame` (`filter`, `select`), понятные Catalyst |
| lambda | `lambda` (в тексте «лямбда») | — | Анонимная функция, непрозрачная для Catalyst |
| off-heap | `off-heap` | внекучевая | Память вне кучи JVM |
| garbage collection | `GC` (сборщик мусора) | — | Очистка памяти JVM |
| dynamic allocation | `dynamic allocation` | динамическая аллокация | `Driver` сам просит у кластера больше или меньше `executor` |
| execution memory / storage memory | execution memory / storage memory | — | Память `executor` под `shuffle`, join, сортировки / под кэш. Без backticks, как в таблицах книги |
| reserved memory | reserved memory | — | 300 МБ в запас против OOM |
| garbage collection (GC) | `garbage collection` (GC) | сборка мусора без пояснения | Сборка мусора в JVM. Высокое время GC значит нехватку памяти |
| small file problem | `small file problem` | проблема мелких файлов | Много мелких файлов: лишний ввод-вывод на открытие и листинг |
| StorageLevel | `StorageLevel` | уровень хранения без пояснения | Параметр `persist`: память, диск, сериализация, число копий |
| broadcast hash join (BHJ) | `broadcast hash join` (BHJ) | — | Маленькую таблицу рассылают всем `executor`. `Shuffle` не нужен |
| sort merge join (SMJ) | `sort merge join` (SMJ) | сортирующее слияние | Сортируем обе таблицы по ключу и сливаем. Нужен `Exchange` |
| Exchange | `Exchange` | — | Оператор физического плана: `shuffle` данных между `executor` |
| equi-join | equi-join | — | Join по равенству ключей |
| record-at-a-time | `record-at-a-time` | запись за записью без пояснения | Традиционная модель: узел получает одну запись, обрабатывает, передаёт дальше |
| DStreams (Spark Streaming) | `DStream` | дистрим | Старый потоковый API Spark на базе `RDD` |
| unbounded table | `unbounded table` (бесконечная таблица) | безграничная таблица | Модель: поток = таблица, в которую всё время добавляют строки |
| result table | `result table` | таблица результата | Итог запроса на момент T |
| incrementalization | `incrementalization` (инкрементализация) | — | Spark сам превращает batch-запрос в запрос, который обновляет итог по новым данным |
| output mode | `output mode` (режим вывода) | выходной режим | `append`, `update`, `complete` |
| state | `state` | состояние без пояснения | Промежуточные итоги между `micro-batch` |
| stateless / stateful transformation | `stateless` / `stateful` | — | См. glossary.md; здесь для операций |
| replayable source | `replayable source` | воспроизводимый источник | Источник, из которого можно перечитать тот же диапазон данных |
| idempotent sink | `idempotent sink` | идемпотентный синк | Sink, который игнорирует повторную запись того же `micro-batch` |
| offset | `offset` | — | Позиция записи в Kafka |
| foreachBatch / foreach | `foreachBatch` / `foreach` | — | Методы записи в произвольное хранилище |
| tumbling window | `tumbling window` | кувыркающееся окно | Окно без пересечений, например по 5 минут |
| sliding window | `sliding window` | скользящее окно без англ. | Окна с шагом меньше длины, события попадают в несколько окон |
| watermark delay | `watermark delay` | задержка watermark | Насколько `watermark` отстаёт от максимального `event time` |
| stream-static join / stream-stream join | `stream-static join` / `stream-stream join` | — | Join потока со статичной таблицей / с другим потоком |
| timeout (state) | `timeout` | таймаут без пояснения | Срок, после которого `state` ключа считается устаревшим |
| scheduler pool | `scheduler pool` | пул планировщика | Раздельная очередь `task` для запроса, чтобы запросы делили ресурсы честно |
| managed / unmanaged stateful operations | управляемые / неуправляемые `stateful` операции | — | Spark сам чистит `state` / вы чистите сами |
| Kafka | Kafka | — | Название продукта |
| ACID | `ACID` | — | Атомарность, согласованность, изолированность, долговечность транзакции |
| OLTP / OLAP | `OLTP` / `OLAP` | — | Много мелких быстрых операций / сложные аналитические запросы |
| Delta Lake, Apache Hudi, Apache Iceberg | Delta Lake, Apache Hudi, Apache Iceberg | — | Названия проектов, без backticks |
| CDC | `CDC` (change data capture) | — | Перенос изменений строк из OLTP-таблицы в аналитическую |
| SCD | `SCD` | — | Медленно меняющиеся измерения |
| snapshot isolation | `snapshot isolation` | — | Читатель видит снимок таблицы на момент версии |
| data silo | `data silos` | — | Изолированные хранилища для разных данных |
| GDPR | GDPR | — | Закон ЕС о защите данных |
| label | метка (`label`) | лейбл, целевая переменная без пояснения | Значение, которое модель учится предсказывать |
| feature | признак (`feature`) | фича | Колонка входных данных |
| train / test | `train` / `test` | тренировочный набор | Обучающая и тестовая части данных |
| supervised / unsupervised learning | обучение с учителем / без учителя (`supervised learning`) | — | Есть метки / нет меток |
| classification / regression | классификация / регрессия | — | Метка дискретная / непрерывная |
| hyperparameter | `hyperparameter` | гиперпараметр без backticks | Настройка модели до обучения. Не учится |
| overfitting | переобучение | оверфиттинг | Модель запомнила шум обучающих данных |
| one-hot encoding | `one-hot encoding` (OHE) | — | Для каждой категории своя бинарная колонка |
| RMSE / R2 | `RMSE`, `R2` | — | Метрики регрессии |
| baseline | `baseline` | базовая линия | Простой прогноз для сравнения (среднее по train) |
| decision tree | `decision tree` | дерево решений без backticks | Цепочка правил if-then-else |
| random forest | `random forest` | случайный лес | Ансамбль деревьев |
| bootstrap / bagging | `bootstrap`, `bagging` | бутстрап | Выборка с возвращением и агрегация ответов |
| fold | `fold` | фолд | Одна из k частей train в cross-validation |
| split (tree) | `split` | сплит без пояснения | Разбиение узла дерева по признаку |
| ensemble | ансамбль | — | Много моделей, ответы объединяют |
| pipeline stage | шаг (`Pipeline`) | стадия | «Стадия» занята: `stage` — это часть `job` в Spark |
| MLflow | MLflow | — | Название продукта, без backticks |
| tracking / run / experiment | `Tracking`, `run`, `experiment` | запуск эксперимента без `run | `Tracking` — компонент. `run` — один запуск обучения. `experiment` — группа `run` |
| artifact | `artifact` | артефакт | Файл, который `run` сохраняет: график, CSV, модель |
| Model Registry | Model Registry, `Registry` | реестр моделей | Версии модели, статусы (staging, production, archived), alias |
| model stage | статус модели (`staging`, `production`, `archived`) | стадия модели | Слово «стадия» занято термином `stage` Spark |
| model drift | `model drift` | дрейф модели без `model drift | Качество падает, потому что данные изменились |
| inference | `inference` | инференс | Применение обученной модели к данным |
| batch / streaming / real-time deployment | `batch`, `streaming`, `real-time` | реалтайм | Три режима запуска модели по задержке |
| ONNX | ONNX | — | Открытый формат обмена моделями |
| SparkTrials | `SparkTrials` | — | Класс Hyperopt для параллельных испытаний |
| Koalas / pyspark.pandas | Koalas, `pyspark.pandas` | коалас | `pandas` API поверх Spark. С Spark 3.2 в PySpark как `pyspark.pandas` |
| dynamic partition pruning (DPP) | `DPP` (dynamic partition pruning) | динамическое отсечение партиций | Фильтр по измерению вставляется в scan факта |
| fact table / dimension table | `fact table` / `dimension table` | таблица фактов / измерений без пояснения | Факт разбит на `partition`, измерение нет |
| build relation | `build relation` | — | Hash table из результата фильтра по измерению |
| materialization point | `materialization point` | — | Граница `stage` (`shuffle`, broadcast), где `AQE` пересматривает план |
| join hint | подсказка для `join` (`/*+ MERGE(a, b) */`) | — | MERGE, BROADCAST, SHUFFLE_HASH, SHUFFLE_REPLICATE_NL |
| DataSourceV2 / Catalog API | `DataSourceV2`, `Catalog API` | — | Экспериментальные API каталогов и источников |
| Project Hydrogen | `Project Hydrogen` | — | Инициатива: barrier execution, GPU, обмен данными |
| barrier execution | `barrier execution` | — | Режим, где все `task` стартуют вместе |
| type hints | type hints | подсказки типов | Аннотации Python для `pandas UDF` |
| cogroup | `cogroup` | — | Две группы с общим ключом для `applyInPandas` |
| view | `view` | представление | Запрос с именем. Данных не хранит |
| write mode | режим записи (`mode`) | — | `append`, `overwrite`, `ignore`, `errorIfExists` |
| partitionBy | `partitionBy` | партиционирование | Раскладывает файлы по папкам `колонка=значение` |
| Parquet / ORC / Avro | Parquet / ORC / Avro | — | Названия форматов, без backticks |
