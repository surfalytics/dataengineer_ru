---
title: "Learning Spark, глава 1: Введение в Apache Spark"
head:
  - tag: title
    content: "Что такое Apache Spark и как он устроен | Инжиниринг Данных"
description: "Конспект главы 1 Learning Spark на русском. История Spark, Hadoop MapReduce, четыре принципа, компоненты, driver, executor и partition."
sidebar:
  order: 1
  label: "1. Введение в Apache Spark"
tags:
  - books
  - spark
---

**Главная мысль:** Apache Spark — это единый движок аналитики (`unified analytics engine`). Один движок обрабатывает SQL, потоки, машинное обучение и графы. Он вырос из проблем Hadoop MapReduce и хранит промежуточные результаты в памяти, а не на диске.

## О чём глава

Глава отвечает на три вопроса: откуда взялся Spark, чем он лучше Hadoop MapReduce и как устроен его кластер. Это первая глава, поэтому она опирается только на [обзор книги](/book-summaries/engineering/learning-spark/). Темы: история Spark, четыре принципа, четыре компонента, архитектура (`driver`, `executor`, `partition`) и пользователи.

![Схема: MapReduce пишет промежуточный результат на диск после каждого шага, а Spark держит его в памяти](/assets/learning-spark/ch01-mr-vs-spark.png)

В верхней цепочке промежуточный результат уходит на диск, в нижней остаётся в памяти.

## Рождение Spark

### Большие данные в Google

Google нужно было индексировать весь интернет, а реляционные базы (RDBMS) и обычный императивный код с таким объёмом не справлялись. Так появились три системы: GFS (отказоустойчивая файловая система на обычных серверах), Bigtable (хранилище структурированных данных поверх GFS) и MapReduce (MR, модель параллельных вычислений).

MR отправляет код (`map` и `reduce`) туда, где лежат данные, а не тащит данные к коду. Поэтому ввод-вывод остаётся на локальных дисках, а сетевой трафик падает. Код Google не открыл, но три статьи вдохновили сообщество, прежде всего Yahoo!.

### Hadoop в Yahoo!

По этим статьям Yahoo! построил HDFS и MapReduce. В 2006 году их передали в Apache Software Foundation (ASF), так появился Apache Hadoop. Но у MapReduce на HDFS были слабые места:

1. Его трудно администрировать. API многословный, а отказоустойчивость хрупкая.
2. Каждая пара шагов MR пишет промежуточный результат на локальный диск. Из-за постоянной записи на диск (disk I/O) большие вычисления MR шли часами и даже днями.
3. Он плохо подходит для машинного обучения, потоков и интерактивного SQL. Для них создавали отдельные системы (Hive, Storm, Impala, Giraph и другие) с разными API, и сложность росла.

Автор напоминает слова Алана Кея: простое должно быть простым, а сложное — возможным. Можно ли сделать Hadoop проще и быстрее?

### Первые годы Spark в AMPLab

Ответили исследователи UC Berkeley, которые раньше имели дело с MapReduce. В 2009 году в RAD Lab (позже AMPLab) они начали проект Spark: проще и быстрее MR, особенно для интерактивных и итеративных задач. Ранние статьи показали ускорение в 10–20 раз, а сегодня, по словам авторов, Spark быстрее MR на много порядков.

Идея такая: взять лучшее из MapReduce, но добавить отказоустойчивость, промежуточные результаты в памяти, простые API на разных языках и единый движок для разных нагрузок. В 2013 году создатели передали Spark в ASF и основали Databricks. Spark 1.0 вышел в мае 2014 года.

## Что такое Apache Spark

Spark — это единый движок для распределённой обработки больших данных, в дата-центре или в облаке. Он держит промежуточные результаты в памяти, поэтому намного быстрее MapReduce. Философия Spark — четыре свойства.

### Скорость

Скорость идёт из трёх источников. Во-первых, Spark использует дешёвые серверы с сотнями гигабайт памяти и многими ядрами. Во-вторых, он строит запрос как `DAG` (граф шагов без циклов), и планировщик раскладывает его на `task`, которые идут параллельно. В-третьих, движок Tungsten генерирует компактный код для всего `stage` (глава 3).

### Простота

В основе лежит простая структура `RDD` (Resilient Distributed Dataset, отказоустойчивый распределённый набор данных), а на ней построены `DataFrame` и `Dataset`. Поэтому модель программирования проста: она состоит из `transformation` (шаг, который описывает вычисление) и `action` (шаг, который его запускает).

### Модульность

Операции доступны на Scala, Java, Python, SQL и R. Библиотеки для SQL, потоков, ML и графов входят в один движок. Поэтому одно приложение делает всё, а отдельные движки для каждой нагрузки не нужны.

### Расширяемость

Spark занимается вычислениями, а не хранением. Hadoop объединял их, а Spark разделяет. Поэтому он читает данные из Hadoop, Cassandra, HBase, Hive, RDBMS, а через расширяемые `DataFrameReader` и `DataFrameWriter` — Kafka, Kinesis и Amazon S3. Кроме того, сторонние пакеты сообщества добавляют коннекторы и мониторинг.

## Единая аналитика

Единство — ядро дизайна Spark. В 2016 году ACM наградила его создателей за статью «Unified Engine for Big Data Processing». Статья говорит, что Spark заменяет отдельные движки для batch, графов, потоков и запросов (Storm, Impala, Dremel, Pregel) одним стеком.

### Компоненты как единый стек

Каждая из четырёх библиотек отделена от ядра. Вы пишете код через API, Spark превращает его в `DAG`, а выполняет его ядро. На каком языке вы пишете, не важно: код превращается в компактный bytecode, который выполняется в JVM на `executor`.

![Схема: языки, четыре библиотеки Spark, ядро и источники данных](/assets/learning-spark/ch01-stack.png)

Все четыре библиотеки стоят над одним ядром, поэтому отдельные кластеры им не нужны.

#### Spark SQL

Модуль читает таблицы RDBMS и файлы (CSV, JSON, Avro, ORC, Parquet) и создаёт постоянные и временные таблицы. SQL можно смешивать с вызовами API на любом языке. Spark SQL соответствует ANSI SQL:2003.

Книга читает JSON с S3 на Scala. Мы повторяем идею на Python: `DataFrame` становится `temporary view`, и к нему идёт SQL-запрос.

```python
"""Глава 1: SparkSession, temporary view и SQL-запрос по DataFrame."""
import os, sys
from pyspark.sql import SparkSession

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("LearnSpark")
         .config("spark.sql.shuffle.partitions", 6)
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Маленькая таблица «коммитеров» вместо JSON на S3
rows = [
    ("Ana", "databricks", "mllib", 14),
    ("Boris", "apple", "mllib", 9),
    ("Chen", "databricks", "sql", 120),
    ("Dina", "google", "mllib", 31),
    ("Egor", "ibm", "mllib", 11),
    ("Farid", "google", "streaming", 50),
]
committers = spark.createDataFrame(rows, ["name", "org", "module", "num_commits"])

# DataFrame превращаем в temporary view: теперь к нему можно писать SQL
committers.createOrReplaceTempView("committers")

results = spark.sql("""
    SELECT name, org, module, num_commits
    FROM committers
    WHERE module = 'mllib' AND num_commits > 10
    ORDER BY num_commits DESC
""")
results.show()

# Тот же запрос через DataFrame API: план и результат одинаковые
same = (committers.filter("module = 'mllib' AND num_commits > 10")
        .orderBy(committers.num_commits.desc()).select("name", "org", "module", "num_commits"))
print("same result:", same.collect() == results.collect())
print("shuffle.partitions =", spark.conf.get("spark.sql.shuffle.partitions"))
spark.stop()
```

```text
+----+----------+------+-----------+
|name|       org|module|num_commits|
+----+----------+------+-----------+
|Dina|    google| mllib|         31|
| Ana|databricks| mllib|         14|
|Egor|       ibm| mllib|         11|
+----+----------+------+-----------+

same result: True
shuffle.partitions = 6
```

> **Пояснение:** `temporary view` живёт, пока живёт `SparkSession`. SQL и вызовы `DataFrame` дают один план, поэтому выводится `same result: True`.

#### MLlib

Это библиотека типовых алгоритмов машинного обучения. С Spark 1.6 у неё два пакета: `spark.mllib` (на `RDD`, только поддержка) и `spark.ml` (на `DataFrame`, туда идут новые функции). Но в книге MLlib — это обе части вместе. Она извлекает признаки, строит `ML pipeline` и сохраняет модели. `Estimator` учится методом `fit` и возвращает `transformer`, а тот применяет модель методом `transform` (главы 10 и 11). Ключевые строки из `scripts/learning-spark-code/ch01_mllib.py`:

```python
lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)  # Estimator
lr_model = lr.fit(training)                                              # Transformer
lr_model.transform(test).select("label", "prediction").orderBy("label").show()
```

```text
+-----+----------+
|label|prediction|
+-----+----------+
|  0.0|       0.0|
|  1.0|       1.0|
+-----+----------+
```

#### Structured Streaming

Structured Streaming появился в Spark 2.0 на движке Spark SQL, а в Spark 2.2 стал готов к production. Он представляет поток данных (`stream`) как таблицу, которая только растёт: новые строки дописываются в конец, а запросы пишутся как к обычной таблице. Движок сам отвечает за отказоустойчивость и поздние данные (`late data`). Модель заменила DStreams (глава 8).

Книга читает сокет и пишет подсчёт слов в Kafka. У нас источник — папка с файлами, а результат — таблица в памяти, поэтому внешние сервисы не нужны.

```python
"""Глава 1: Structured Streaming. Поток как растущая таблица, word count."""
import tempfile, pathlib
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("streaming")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Вместо socket кладём файлы в папку: так поток можно воспроизвести
src = pathlib.Path(tempfile.mkdtemp())
(src / "a.txt").write_text("spark is fast\nspark is unified\n")
(src / "b.txt").write_text("hadoop is slow\n")

lines = spark.readStream.format("text").load(str(src))
words = lines.select(explode(split(lines.value, " ")).alias("word"))
word_counts = words.groupBy("word").count()

query = (word_counts.writeStream.format("memory").queryName("wc")
         .outputMode("complete").trigger(availableNow=True).start())
query.awaitTermination()
spark.sql("SELECT word, count FROM wc ORDER BY count DESC, word").show()
spark.stop()
```

```text
+-------+-----+
|   word|count|
+-------+-----+
|     is|    3|
|  spark|    2|
|   fast|    1|
| hadoop|    1|
|   slow|    1|
|unified|    1|
+-------+-----+
```

Версия книги отличается только `sink` (куда пишем результат):

```python
# не запускается: нужен брокер Kafka
query = (word_counts.writeStream.format("kafka")
         .option("kafka.bootstrap.servers", "localhost:9092")
         .option("topic", "output")
         .option("checkpointLocation", "/tmp/ckpt")
         .outputMode("complete")
         .start())
```

#### GraphX

Библиотека обрабатывает графы (соцсети, маршруты, топология сетей) и даёт алгоритмы PageRank, Connected Components и Triangle Counting. GraphX есть только в Scala и Java, но для Python есть GraphFrames, аналог на `DataFrame`. Пример графа мы не запускаем.

## Распределённое выполнение Spark

Приложение Spark состоит из программы `driver`, которая управляет параллельными операциями в кластере. Через `SparkSession` она обращается к `executor` и cluster manager.

![Схема: driver просит ресурсы у cluster manager, тот запускает executor, а driver раздаёт им task](/assets/learning-spark/ch01-architecture.png)

Читайте схему по номерам. `Driver` просит ресурсы, cluster manager запускает `executor`, и только потом `driver` напрямую раздаёт им `task`.

### Driver и SparkSession

`Driver` создаёт `SparkSession`. Он просит у cluster manager ресурсы для `executor` (это JVM), превращает операции в `DAG` и раздаёт их как `task`.

В Spark 2.0 `SparkSession` стала единой точкой входа. Она поглотила `SparkContext`, `SQLContext`, `HiveContext`, `SparkConf` и `StreamingContext`. Через неё создают `DataFrame` и `Dataset`, читают источники, смотрят метаданные каталога и запускают SQL. В Spark 1.x для каждого модуля создавали отдельный контекст, а в 2.x хватает одной сессии на JVM. Старые контексты остались для совместимости. В Spark shell сессия уже есть в переменной `spark`.

### Cluster manager и executor

Cluster manager выдаёт ресурсы узлов. Spark поддерживает четыре варианта: встроенный standalone, Hadoop YARN, Apache Mesos и Kubernetes.

> **Пояснение:** Mesos объявили устаревшим в Spark 3.2 и убрали в Spark 4.0. Сегодня берут YARN или Kubernetes.

`Executor` запущен на каждом рабочем узле: общается с `driver` и выполняет `task`. Обычно на узле один `executor`.

### Режимы развёртывания

Cluster manager не зависит от места запуска, поэтому Spark запускают в разных средах.

| Режим | `driver` | `executor` | Cluster manager |
|---|---|---|---|
| Local | Одна JVM, например ноутбук | Та же JVM | Тот же хост |
| Standalone | Любой узел | Своя JVM на каждом узле | Любой хост |
| YARN (client) | Клиент, вне кластера | Контейнер NodeManager | Resource Manager и Application Master |
| YARN (cluster) | Вместе с Application Master | Как в client | Как в client |
| Kubernetes | Pod Kubernetes | Свой pod | Kubernetes Master |

### Распределённые данные и partition

Физически данные лежат как `partition` в HDFS или облаке. Spark видит каждую `partition` как `DataFrame` в памяти. По возможности `executor` получает `task` с ближайшей по сети `partition` (data locality). Каждое ядро `executor` берёт свою `partition`, поэтому сеть почти не нужна.

![Схема: четыре partition из хранилища, у каждой своё ядро executor и свой task](/assets/learning-spark/ch01-partitions.png)

Ниже `repartition(8)` делит `DataFrame` на восемь частей, а `spark.range` сразу создаёт 10 000 чисел в восьми `partition`.

```python
"""Глава 1: данные делятся на partition, каждый task берёт одну."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import spark_partition_id

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("partitions")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 10 000 чисел сразу в 8 partition
df = spark.range(0, 10000, 1, 8)
print("range partitions:", df.rdd.getNumPartitions())

# repartition(8) для уже готового DataFrame (в книге так читают большой файл)
log_df = spark.createDataFrame([(i, f"line {i}") for i in range(1000)], ["id", "text"]).repartition(8)
print("repartition partitions:", log_df.rdd.getNumPartitions())

# Сколько строк в каждой partition
df.groupBy(spark_partition_id().alias("partition")).count().orderBy("partition").show()
spark.stop()
```

```text
range partitions: 8
repartition partitions: 8
+---------+-----+
|partition|count|
+---------+-----+
|        0| 1250|
|        1| 1250|
|        2| 1250|
|        3| 1250|
|        4| 1250|
|        5| 1250|
|        6| 1250|
|        7| 1250|
+---------+-----+
```

> **Пояснение:** в книге `repartition(8)` вызывают для большого текстового файла. Мы взяли маленький `DataFrame`, чтобы пример запускался без файлов. Число `partition` под число ядер книга настраивает в главах 3 и 7.

## Опыт разработчика

Цель Spark 2.x — упростить фреймворк и сократить число понятий, которые нужно знать разработчику. Вы описываете, что считать, а не как, поэтому Spark сам выбирает способ (Structured APIs, глава 3). Spark берут data engineer, data scientist и ML engineer, и роли часто совмещаются.

**Data scientist** чистит данные, ищет закономерности и строит модели. Для этого есть MLlib (модели), Spark SQL и Spark shell (интерактивный анализ). Для глубокого обучения Spark 2.4 добавил gang scheduler (проект Hydrogen), а Spark 3.0 умеет выделять GPU в режимах standalone, YARN и Kubernetes.

**Data engineer** строит `pipeline`. Модель машинного обучения не существует сама по себе: она связана с веб-приложением или потоковым движком вроде Kafka, а часто это лишь одна часть общей цепочки обработки данных. Data engineer превращает сырые данные из многих источников в чистые для отчётов и BI. Structured Streaming дал модель `continuous applications` (глава 8): один `pipeline` делает ETL и из потоков, и из статических данных. Spark прячет сложность распределения и отказоустойчивости.

Сценарии: параллельная обработка, интерактивные запросы, обучение моделей, `pipeline` и графы.

## Сообщество

У Spark больше 600 meetup-групп и почти полмиллиона участников. Книга охватывает Spark 2.x и 3.0, код проверен на 3.0-preview2. Код в проект внесли около 1500 разработчиков, на GitHub около 27 000 коммитов.

## Итоги главы

- MapReduce медленный из-за записи промежуточных результатов на диск и не подходит для потоков, ML и SQL.
- Spark хранит промежуточные результаты в памяти и объединяет разные нагрузки в одном движке.
- Spark держится на четырёх свойствах: скорость, простота, модульность, расширяемость.
- Spark SQL, MLlib, Structured Streaming и GraphX стоят над одним ядром.
- `Driver` строит `DAG` и раздаёт `task`, `executor` их выполняет, и каждое ядро берёт одну `partition`.
- `SparkSession` в Spark 2.x заменила прежние контексты, а вычисления отделены от хранения.

## Что изменилось к 2026 году

> Это наше дополнение, его нет в книге.

Книга написана под Spark 3.0. На ноябрь 2026 года последняя стабильная версия — **Spark 4.3.0** (вышла 30 октября 2026). Ветка 3.5 ещё получает исправления, но новые возможности появляются только в 4.x. Главное, что изменилось для установки:

- Spark 4 работает на Java 17, 21 или 25. Java 8 и 11 больше не подходят.
- PySpark 4.3 требует Python 3.11 или новее.
- Spark собран под Scala 2.13. Поддержку Mesos убрали.

### Как установить Spark

Проще всего начать с Docker. Контейнер уже содержит нужные версии Java, Python и Spark, поэтому ничего не надо настраивать на своём компьютере. Если Docker для вас новый, пройдите наш курс [Базовый минимум Docker](/practice/docker/): в нём есть [установка Docker](/practice/docker/setup/) на Windows, macOS и Linux.

Готовый образ от Apache запускает консоль PySpark одной командой:

```bash
docker run -it --rm apache/spark:4.3.0-python3 /opt/spark/bin/pyspark
```

Если нужен Spark без Docker, порядок такой: сначала Java 17 или 21, потом PySpark.

| Система | Как поставить |
|---|---|
| macOS | `brew install apache-spark` ставит Spark 4.3.0 и Java 21. Для Python-проекта: `pip install pyspark==4.3.0` в venv и `export JAVA_HOME=$(brew --prefix openjdk@21)` |
| Linux (Ubuntu, Debian) | `sudo apt install openjdk-17-jdk`, затем `pip install pyspark==4.3.0` в venv |
| Windows | Лучше через WSL 2 (Ubuntu внутри Windows) и шаги для Linux. Без WSL нужны `winutils.exe` и переменная `HADOOP_HOME`, и это частый источник ошибок |

Проверить установку можно так: `python -c "import pyspark; print(pyspark.__version__)"` должен напечатать `4.3.0`. Подробно установку разбирает [глава 2](/book-summaries/engineering/learning-spark/02-getting-started/).

### Как мы запускали код конспекта

Весь код на страницах этого конспекта мы проверили на Spark 4.3.0 в Docker. Образ описан в [Dockerfile](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/Dockerfile): Python 3.12, Java 17 и PySpark 4.3.0. Чтобы повторить примеры, склонируйте репозиторий и выполните из его корня:

```bash
docker build -t learning-spark:4.3.0 scripts/learning-spark-code
scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch01_spark_sql.py
```

Скрипт [`spark-python`](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/spark-python) запускает `python3` внутри контейнера и подключает папку репозитория, поэтому скрипты видят свои файлы.

## Ключевые термины

| Термин | Значение |
|---|---|
| единый движок аналитики (`unified analytics engine`) | Один движок для SQL, потоков, ML и графов |
| `driver` | Процесс с `SparkSession`: строит `DAG`, раздаёт `task` |
| `executor` | Процесс на узле: выполняет `task` |
| `partition` | Часть данных, которую берёт один `task` |
| `DAG` | Граф шагов, который Spark строит из кода |
| `transformation` / `action` | Шаг, который описывает вычисление / запускает его |

## Что это значит на практике

- Пишите `pipeline` на `DataFrame` и SQL: их оптимизирует движок.
- Отлаживайте в режиме local, потом переносите на YARN или Kubernetes.
- Число `partition` задаёт параллелизм: если его мало, ядра простаивают.
- Один движок для batch и потоков — один набор API и один навык для обоих.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём данные

```sql
CREATE TABLE committers AS SELECT * FROM (VALUES
    ('Ana',   'databricks', 'mllib',     14),
    ('Boris', 'apple',      'mllib',      9),
    ('Chen',  'databricks', 'sql',      120),
    ('Dina',  'google',     'mllib',     31),
    ('Egor',  'ibm',        'mllib',     11),
    ('Farid', 'google',     'streaming', 50)
) t(name, org, module, num_commits);

CREATE TABLE lines AS SELECT * FROM (VALUES
    (1, 'spark is fast'),
    (2, 'spark is unified'),
    (3, 'hadoop is slow')
) t(id, line);

CREATE TABLE events AS
SELECT i AS id FROM generate_series(1, 20) t(i);
```

### Шаг 2. Проверяем

Должно быть 6, 3 и 20 строк.

```sql
SELECT (SELECT count(*) FROM committers) AS committers,
       (SELECT count(*) FROM lines) AS lines,
       (SELECT count(*) FROM events) AS events;
```

### Задания

**1. Запрос из Spark SQL.** Найдите коммитеров модуля `mllib` с числом коммитов больше 10.

<details><summary>Решение</summary>

```sql
SELECT name, org, module, num_commits
FROM committers
WHERE module = 'mllib' AND num_commits > 10
ORDER BY num_commits DESC;
```

```text
name  org         module  num_commits
Dina  google      mllib   31
Ana   databricks  mllib   14
Egor  ibm         mllib   11
```

Boris с 9 коммитами отсеян условием `> 10`.

</details>

**2. Partition.** Разделите `events` на 4 «partition» по `id % 4` и посчитайте строки в каждой. Группа — это один `task`.

<details><summary>Решение</summary>

```sql
SELECT id % 4 AS partition, count(*) AS n
FROM events
GROUP BY partition
ORDER BY partition;
```

```text
partition  n
0          5
1          5
2          5
3          5
```

Строки разделились поровну: как в Spark, где каждая из 8 `partition` получила по 1250 строк.

</details>

**3. Растущая таблица.** Посчитайте слова в `lines`, добавьте строку и повторите запрос. Так Structured Streaming видит поток.

<details><summary>Решение</summary>

```sql
SELECT word, count(*) AS n
FROM (SELECT unnest(string_split(line, ' ')) AS word FROM lines)
GROUP BY word
ORDER BY n DESC, word;

INSERT INTO lines VALUES (4, 'spark is everywhere');

SELECT word, count(*) AS n
FROM (SELECT unnest(string_split(line, ' ')) AS word FROM lines)
GROUP BY word
ORDER BY n DESC, word;
```

```text
word     n
is       3
spark    2
fast     1
hadoop   1
slow     1
unified  1

word        n
is          4
spark       3
everywhere  1
fast        1
hadoop      1
slow        1
unified     1
```

Первый результат совпадает с выводом Spark. После вставки `is` стало 4.

</details>

## Вопросы для самопроверки

1. Почему запись на диск замедляет MapReduce и как это решает Spark?
2. Какие четыре свойства лежат в основе Spark?
3. Зачем Spark разделяет хранение и вычисления?
4. Чем `driver` отличается от `executor`? Кто строит `DAG`, а кто выполняет `task`?
5. Зачем нужны `partition` и когда их число становится проблемой?

Предыдущая: [обзор книги](/book-summaries/engineering/learning-spark/). Следующая: [Установка Spark и первые шаги](/book-summaries/engineering/learning-spark/02-getting-started/).
