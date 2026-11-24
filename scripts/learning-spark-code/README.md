# Код конспекта Learning Spark, 2nd Edition

Все примеры запускаются в Docker. Книга написана под Spark 3.0, код обновлён под Spark 4.3.0.

## Образы

| Образ | Файл | Что внутри | Для каких глав |
|---|---|---|---|
| `learning-spark:4.3.0` | `Dockerfile`, `requirements.txt` | Python 3.12, Java 17, PySpark 4.3.0, pandas, pyarrow, DuckDB, MLflow | все, кроме Delta Lake |
| `learning-spark:4.2.0-delta` | `Dockerfile.delta`, `requirements-delta.txt` | PySpark 4.2.0 + delta-spark 4.4.1 (Delta пока не поддерживает 4.3) | глава 9 |

Сборка из корня репозитория:

```bash
docker build -t learning-spark:4.3.0 scripts/learning-spark-code
docker build -f scripts/learning-spark-code/Dockerfile.delta -t learning-spark:4.2.0-delta scripts/learning-spark-code
```

## Запуск

```bash
scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch01_spark_sql.py
SPARK_IMAGE=learning-spark:4.2.0-delta scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch09_<name>.py
```

`spark-python` запускает `python3` в контейнере и монтирует репозиторий по тому же пути.
Проверка детерминизма: `python3 -I scripts/book-tools/same_output.py --python scripts/learning-spark-code/spark-python <script.py>`.

## Статус примеров

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | SparkSession, temporary view, SQL по DataFrame (в книге Scala + JSON на S3) | ch01_spark_sql.py | ok (same x6) |
| 1 | MLlib: LogisticRegression fit/transform (в книге `...` и пути S3) | ch01_mllib.py | ok (same x6) |
| 1 | Structured Streaming: word count (в книге socket + Kafka) | ch01_streaming.py | ok (same x6): вместо socket файловый источник, вместо Kafka memory sink |
| 1 | Structured Streaming: sink Kafka | блок на странице | не запускается: нужен брокер Kafka |
| 1 | GraphX joinVertices (Scala) | — | не запускается: Scala, в Python GraphX нет |
| 1 | repartition(8), spark.range(..., 8) | ch01_partitions.py | ok (same x6) |
| 1 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 2 | Shell: read.text, show, count, filter (в книге README.md из папки Spark, Scala + Python) | ch02_shell.py | ok (same x6): свой файл в /tmp вместо README.md |
| 2 | Lazy evaluation (accumulator) и Exchange в плане для narrow и wide | ch02_lazy.py | ok (same x6): пример наш, в книге только схема |
| 2 | M&M count (Example 2-1, Python) | ch02_mnmcount.py | ok (same x6): данные генерируются в /tmp (20 000 строк, seed 42) вместо mnm_dataset.csv |
| 2 | spark-submit mnmcount.py | команда на странице | ok: проверено в learning-spark:4.3.0 и apache/spark:4.3.0-python3 (`spark-submit ch02_mnmcount.py`) |
| 2 | M&M count на Scala (Example 2-2), build.sbt (Example 2-3), sbt clean package | — | не запускается: Scala и sbt, на страницах только PySpark |
| 2 | JavaWordCount через bin/run-example | команда в тексте | не запускается: Java-пример из дистрибутива, не нужен для PySpark |
| 2 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 3 | RDD против DataFrame, схема DDL, expr, withColumn, Row (в книге Scala и Python) | ch03_schema_columns.py | ok (same x6) |
| 3 | SF Fire: схема, CSV, filter, to_timestamp, groupBy, агрегации, Parquet (в книге данные Databricks, здесь 200 строк с seed 42) | ch03_fire_calls.py | ok (same x6) |
| 3 | Catalyst: explain, DataFrame и SQL дают один план, predicate pushdown | ch03_catalyst.py | ok (same x6): AQE выключен, чтобы план не менялся |
| 3 | Dataset, case class, IoT (Scala) | — | не запускается: Dataset[T] есть только в Scala и Java |
| 3 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 4 | spark.sql, CASE, DataFrame API, managed и unmanaged таблицы, views, Catalog, CACHE LAZY (в книге CSV на Databricks, Scala и Python) | ch04_sql_tables.py | ok (same x6): данные генерируются (205 рейсов, seed 42), границы CASE исправлены. Запуск: scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch04_sql_tables.py |
| 4 | DataFrameReader/Writer: Parquet, JSON, CSV (mode), ORC, partitionBy, image, binaryFile | ch04_formats.py | ok (same x6): данные генерируются. Запуск: scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch04_formats.py |
| 4 | Avro read/write | блок на странице | не запускается: в Spark 4 Avro лежит во внешнем модуле spark-avro, образ его не содержит |
| 4 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 5 | SQL UDF `cubed`, проверка null (UDF и CASE WHEN), pandas UDF | ch05_udf.py | ok (same x6) |
| 5 | JDBC: чтение с `numPartitions` и bounds, `query`, запись (вместо PostgreSQL встроенная Derby в памяти) | ch05_jdbc.py | ok (same x6) |
| 5 | explode + collect_list, transform / filter / exists / reduce, встроенные функции массивов и словарей | ch05_hof.py | ok (same x6): для `map_concat` задан `spark.sql.mapKeyDedupPolicy=LAST_WIN` (Spark 4: ошибка DUPLICATED_MAP_KEY) |
| 5 | union, join, window (dense_rank), withColumn / drop / withColumnRenamed, PIVOT на сгенерированных рейсах | ch05_ops.py | ok (same x6) |
| 5 | JDBC PostgreSQL / MySQL / MS SQL Server (блок на странице) | блок `python` на странице | не запускается: нужен сервер БД и jar |
| 5 | Azure Cosmos DB (блок на странице) | блок `python` на странице | не запускается: нужен аккаунт Azure и коннектор |
| 5 | spark-sql, Beeline, Thrift server, Tableau | блоки `text` и `bash` на странице | не запускается: интерактивная консоль, сервер и BI-инструмент |
| 5 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 6 | filter, cost (аналог map с UsageCost), DSL против UDF, explain (в книге Scala/Java Dataset) | ch06_dataset_costs.py | ok (same x6): в PySpark нет типизированного Dataset, показан DataFrame |
| 6 | Dataset, case class, JavaBean, encoder, MapFunction (Scala/Java) | — | не показывается кодом: Scala и Java, на странице описано текстом |
| 6 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 7 | Чтение и изменение настроек: `builder.config`, `conf.get/set`, `isModifiable`, `SET -v` (в книге Scala и spark-submit) | ch07_config.py | ok (same x6). В Spark 4 AQE включён по умолчанию (в книге `false`), размеры печатаются с суффиксом `b` |
| 7 | `cache`, `persist(DISK_ONLY)`, `unpersist`, `CACHE TABLE` (в книге Scala, со временем выполнения) | ch07_cache.py | ok (same x6). Время не печатаем: оно не детерминировано. Цифры 5,11 с и 0,44 с взяты из книги |
| 7 | Broadcast hash join, sort merge join, bucketing, `explain()` (в книге Scala, 1 млн строк) | ch07_joins.py | ok (same x6). `Sort` остаётся и после bucketing: в бакете несколько файлов |
| 7 | `spark.dynamicAllocation.*` | блок на странице | не запускается: нужен кластер (YARN, Kubernetes) |
| 7 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 8 | Word count: источник, режимы update / complete, append (ошибка), restart с тем же checkpoint (в книге socket + console) | ch08_wordcount.py | ok (same x6): вместо socket файловый источник, вместо console foreachBatch |
| 8 | Окна по event time, watermark, режимы update / append, sliding window | ch08_windows.py | ok (same x6) |
| 8 | stream-static join, stream-stream inner и leftOuter с watermark | ch08_joins.py | ok (same x6) |
| 8 | file sink, foreachBatch (две папки, дедупликация по batchId), foreach, StreamingQueryListener | ch08_sinks.py | ok (same x6) |
| 8 | Произвольный state: applyInPandasWithState с event-time timeout (в книге mapGroupsWithState, только Scala) | ch08_state.py | ok (образ с pyarrow 18.1.0) |
| 8 | Kafka source и sink (word count в topic) | блок на странице | не запускается: нужен брокер Kafka |
| 8 | Cassandra через foreachBatch | описание в тексте | не запускается: нужна Cassandra и коннектор; технику foreachBatch показывает ch08_sinks.py |
| 8 | Scala: mapGroupsWithState, flatMapGroupsWithState, StreamingQueryListener | — | не запускается: Scala, на странице только описание |
| 8 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 9 | Delta Lake: Parquet в Delta, поток, schema enforcement, mergeSchema, UPDATE, DELETE, MERGE, insert-only MERGE, history, time travel | ch09_delta.py | ok (same x6): `SPARK_IMAGE=learning-spark:4.2.0-delta scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch09_delta.py` |
| 9 | JDBC чтение из PostgreSQL | блок на странице | не запускается: нужен сервер PostgreSQL |
| 9 | Hudi, Iceberg | — | в книге кода нет |
| 9 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 10 | randomSplit, VectorAssembler, LinearRegression, Pipeline, StringIndexer + OneHotEncoder, RMSE, R2, baseline, save/load PipelineModel (в книге данные Airbnb с Databricks) | ch10_pipeline.py | ok (same x6): данные сгенерированы с seed, запуск `scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch10_pipeline.py` |
| 10 | DecisionTreeRegressor (ошибка maxBins, setMaxBins(40), featureImportances), RandomForestRegressor, ParamGridBuilder, CrossValidator, parallelism, CrossValidator внутри Pipeline | ch10_trees.py | ok (same x6): время работы идёт в stderr, `scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch10_trees.py` |
| 10 | RFormula | блок на странице | не запускается: показан одной строкой, на странице вместо него полный путь StringIndexer + OHE |
| 10 | toDebugString, VectorIndexer, лог-цена | — | не запускаются: в книге только упоминание, в тексте без кода |
| 10 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 11 | MLflow Tracking, `search_runs`, batch `transform`, Model Registry с alias (в книге файловое хранилище и данные Airbnb на DBFS) | ch11_mlflow.py | ok (same x6): SQLite вместо файлового хранилища, синтетические данные |
| 11 | Потоковые прогнозы: `readStream`, `maxFilesPerTrigger`, `foreachBatch` | ch11_stream.py | ok (same x6): `availableNow`, 4 parquet-файла вместо 100 |
| 11 | `mapInPandas` с моделью scikit-learn, `applyInPandas` на группу, `pyspark.pandas` вместо Koalas | ch11_pandas_udf.py | ok (same x6): нужен PyArrow 18+, см. примечание |
| 11 | `mlflow.run(...)` проекта из GitHub, `mlflow ui` | блок на странице | не запускается: нужен репозиторий книги в GitHub и сервер UI |
| 11 | XGBoost: загрузка нативной модели | блок на странице | не запускается: `xgboost` нет в образе, распределённый API есть только в Java и Scala |
| 11 | Joblib со Spark-бэкендом, `GridSearchCV` | блок на странице | не запускается: `joblibspark` нет в образе |
| 11 | Hyperopt `fmin` + `SparkTrials` | блок на странице | не запускается: `hyperopt` нет в образе |
| 11 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |
| 12 | DPP: dynamicpruning в плане, AQE (coalesced), join hints, explain formatted | ch12_planning.py | ok (same x6) |
| 12 | pandas UDF с type hints, Iterator, mapInPandas, applyInPandas, unionAll | ch12_pandas.py | ok (same x4, PYTHONHASHSEED 1-4) |
| 12 | Catalog plugin: spark-defaults.conf | блок на странице | не запускается: нужен свой коннектор |
| 12 | GPU scheduler: discovery script, BarrierTaskContext (Scala) | — | не запускается: нужны GPU и Scala |
| 12 | DuckDB practice (SQL) | блоки `sql` на странице | ok (check_sql.py) |

Примечания:

- `pandas UDF`, `mapInPandas`, `applyInPandas` и `pyspark.pandas` в Spark 4.3 требуют `pyarrow` 18 или новее. В `requirements.txt` стоит `pyarrow==18.1.0`.
- Сообщения Spark идут в stderr. Вывод в stdout одинаковый при любом hash seed.
