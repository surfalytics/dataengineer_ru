---
title: "Learning Spark, глава 4: Spark SQL и DataFrame: встроенные источники данных"
head:
  - tag: title
    content: "Spark SQL: таблицы, views, Parquet, JSON, CSV, ORC | Инжиниринг Данных"
description: "Конспект главы 4 Learning Spark на русском. spark.sql, managed и unmanaged таблицы, views, Catalog, DataFrameReader и DataFrameWriter, форматы Parquet, JSON, CSV, Avro, ORC."
sidebar:
  order: 4
  label: "4. Spark SQL и DataFrame: встроенные источники данных"
tags:
  - books
  - spark
---

**Главная мысль:** SQL и `DataFrame` в Spark равны по силе, потому что за обоими стоит один движок. Запрос из `spark.sql()` возвращает `DataFrame`, а любой `DataFrame` можно назвать таблицей и спросить через SQL. Данные приходят из файлов (Parquet, JSON, CSV, Avro, ORC) через единые `DataFrameReader` и `DataFrameWriter`.

## О чём глава

В [главе 3](/book-summaries/engineering/learning-spark/03-structured-apis/) мы увидели, что Spark SQL лежит под `DataFrame` и `Dataset`. Теперь глава показывает, как с ним работать из приложения: запросы, таблицы, `view` и метаданные. Вторая половина — про встроенные источники данных. Темы главы: `spark.sql` рядом с `DataFrame`, таблицы `managed` и `unmanaged`, `view` и `Catalog`, `DataFrameReader` с `DataFrameWriter`, форматы Parquet, JSON, CSV, Avro, ORC, а также картинки и бинарные файлы. Книга показывает Scala и Python, а мы оставляем PySpark. Как установить Spark 4.3 и запустить код, см. в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

![Схема: приложение, консоль и BI-инструменты обращаются к Spark SQL, а он читает файлы, таблицы и реляционные базы](/assets/learning-spark/ch04-sql-connectors.png)

Слева те, кто задаёт вопросы, справа источники данных, а по центру — один движок для всех.

## Spark SQL в приложениях

`SparkSession` (появился в Spark 2.0) — единая точка входа для Structured API. Чтобы выполнить запрос, вызовите `spark.sql("SELECT ...")`. Результат всегда `DataFrame`, поэтому его можно сразу продолжить обычными операциями из главы 3. В `Spark shell` и в notebook переменная `spark` уже есть, а в отдельном приложении сессию строят вручную.

Книга берёт данные об авиарейсах США: больше миллиона записей в CSV. У каждого рейса пять полей:

- `date` — строка вида `02190925`, то есть 19 февраля, 09:25;
- `delay` — задержка вылета в минутах, у ранних рейсов отрицательная;
- `distance` — расстояние в милях;
- `origin` и `destination` — коды аэропортов IATA.

У нас такой файл генерируется в коде: 205 рейсов с фиксированным seed. Сначала читаем CSV и объявляем временный `view`, чтобы к данным можно было писать SQL. Схему задаём строкой `DDL`:

```python
schema = "date STRING, delay INT, distance INT, origin STRING, destination STRING"
df = spark.read.csv(SRC, header=True, schema=schema)
df.createOrReplaceTempView("us_delay_flights_tbl")
inferred = spark.read.csv(SRC, header=True, inferSchema=True)
```

```text
rows: 205
date со схемой: string | date через inferSchema: int
```

В книге авторы читают этот файл с `inferSchema`, хотя для больших файлов сами советуют задавать схему явно. Вывод показывает, чем это опасно: Spark принял `date` за число и потерял бы ведущий ноль в `02190925`.

Запросы такие же, как в MySQL или PostgreSQL: Spark поддерживает SQL:2003. Найдём самые длинные рейсы и рейсы SFO–ORD с задержкой больше двух часов:

```python
spark.sql("""SELECT distance, origin, destination
FROM us_delay_flights_tbl WHERE distance > 1000
ORDER BY distance DESC, origin""").show(3)
spark.sql("""SELECT date, delay, origin, destination
FROM us_delay_flights_tbl
WHERE delay > 120 AND origin = 'SFO' AND destination = 'ORD'
ORDER BY delay DESC, date""").show(3)
```

```text
+--------+------+-----------+
|distance|origin|destination|
+--------+------+-----------+
|    4983|   HNL|        JFK|
|    4983|   HNL|        JFK|
|    4983|   HNL|        JFK|
+--------+------+-----------+
only showing top 3 rows
+--------+-----+------+-----------+
|    date|delay|origin|destination|
+--------+-----+------+-----------+
|02190925| 1638|   SFO|        ORD|
|02190925|  360|   SFO|        ORD|
|03080945|  138|   SFO|        ORD|
+--------+-----+------+-----------+
only showing top 3 rows
```

В книге самые длинные рейсы тоже идут между Гонолулу (HNL) и Нью-Йорком (JFK).

Дальше запрос с `CASE`: подписываем каждый рейс словами `Very Long Delays`, `Long Delays` и так далее. Мы поправили границы: в книге условия `delay > 120 AND delay < 360` пропускают значения ровно 120 и 360, и такие рейсы попадают в `Early`.

> **Пояснение:** в нашем запросе рейс с задержкой ровно 60, 120 или 360 минут попадает в более длинный класс.

```python
spark.sql("""SELECT delay, origin, destination,
CASE
  WHEN delay >= 360 THEN 'Very Long Delays'
  WHEN delay >= 120 THEN 'Long Delays'
  WHEN delay >= 60 THEN 'Short Delays'
  WHEN delay > 0 THEN 'Tolerable Delays'
  WHEN delay = 0 THEN 'No Delays'
  ELSE 'Early'
END AS Flight_Delays
FROM us_delay_flights_tbl""").createOrReplaceTempView("labeled_flights")
spark.sql("""SELECT Flight_Delays, count(*) AS flights FROM labeled_flights
GROUP BY Flight_Delays ORDER BY flights DESC""").show()
```

```text
+----------------+-------+
|   Flight_Delays|flights|
+----------------+-------+
|           Early|     81|
|Tolerable Delays|     66|
|    Short Delays|     40|
|     Long Delays|     13|
|       No Delays|      3|
|Very Long Delays|      2|
+----------------+-------+
```

Первый запрос (самые длинные рейсы) можно написать и на `DataFrame`. Вычисления проходят один путь через Spark SQL и `Catalyst`, поэтому результат один и тот же:

```python
by_df = (df.select("distance", "origin", "destination")
         .where(col("distance") > 1000)
         .orderBy(desc("distance"), "origin", "destination"))
print("SQL и DataFrame дают одно и то же:", by_sql.collect() == by_df.collect())
```

```text
SQL и DataFrame дают одно и то же: True
```

## SQL-таблицы и views

У каждой таблицы есть данные и метаданные: схема, описание, имя таблицы и базы, имена колонок, `partition`, место хранения данных. Метаданные лежат в центральном `metastore`, но своего хранилища для них у Spark нет: по умолчанию он использует Apache Hive metastore в каталоге `/user/hive/warehouse`. Путь меняется настройкой `spark.sql.warehouse.dir`, можно указать локальный или внешний распределённый диск.

### Managed и unmanaged таблицы

Таблицы бывают двух типов, и разница видна при удалении.

- `Managed table`: Spark хранит и метаданные, и данные. Данные лежат в файловой системе: локальной, HDFS или в облачном хранилище вроде Amazon S3. `DROP TABLE` удаляет оба.
- `Unmanaged table`: Spark хранит только метаданные, а данные вы держите сами, например в Cassandra. `DROP TABLE` стирает только метаданные.

![Схема: DROP TABLE для managed таблицы удаляет метаданные и данные, а для unmanaged только метаданные](/assets/learning-spark/ch04-managed-unmanaged.png)

Красным отмечено удалённое: у `unmanaged table` данные остаются на месте, и в этом главное отличие.

### Базы и таблицы

Таблицы живут внутри базы, по умолчанию это база `default`. Создадим свою базу `learn_spark_db` и четыре таблицы: пустую `managed` через SQL, `managed` из `DataFrame` через `saveAsTable`, `unmanaged` через `USING csv OPTIONS (path ...)` и `unmanaged` из `DataFrame` с опцией `path`:

```python
spark.sql("CREATE DATABASE learn_spark_db")
spark.sql("USE learn_spark_db")
spark.sql("""CREATE TABLE managed_empty (date STRING, delay INT, distance INT,
origin STRING, destination STRING)""")
df.write.saveAsTable("managed_flights")
spark.sql("""CREATE TABLE unmanaged_csv (date STRING, delay INT, distance INT,
origin STRING, destination STRING)
USING csv OPTIONS (path '/tmp/ch04_flights_csv', header 'true')""")
df.write.option("path", EXT).saveAsTable("unmanaged_flights")
```

В `Catalog` у каждой таблицы виден её тип:

```text
managed_empty 0
managed_flights 205
unmanaged_csv 205
unmanaged_flights 205
labeled_flights        TEMPORARY  temp=True
managed_empty          MANAGED    temp=False
managed_flights        MANAGED    temp=False
unmanaged_csv          EXTERNAL   temp=False
unmanaged_flights      EXTERNAL   temp=False
us_delay_flights_tbl   TEMPORARY  temp=True
```

Spark называет `unmanaged` таблицы внешними (`EXTERNAL`), а временные `view` получили тип `TEMPORARY`.

### Views

Поверх таблиц Spark создаёт `view`. Данных `view` не хранит: это запрос с именем. Читать `view` можно как таблицу, но таблица переживает остановку приложения, а `view` исчезает вместе с ним. Видов `view` два:

- `Temporary view` виден только в одной `SparkSession`.
- `Global temporary view` виден во всех сессиях одного приложения. Обращаться к нему нужно с префиксом `global_temp.`, потому что Spark кладёт его в базу `global_temp`.

В одном приложении можно держать несколько `SparkSession`, и это удобно, если нужно соединить данные двух сессий с разными настройками Hive metastore.

```python
spark.sql("""CREATE OR REPLACE GLOBAL TEMP VIEW us_origin_airport_SFO_global_tmp_view AS
SELECT date, delay, origin, destination FROM managed_flights WHERE origin = 'SFO'""")
df_jfk = spark.sql("""SELECT date, delay, origin, destination FROM managed_flights
WHERE origin = 'JFK'""")
df_jfk.createOrReplaceTempView("us_origin_airport_JFK_tmp_view")
other = spark.newSession()
```

```text
global: 50
temp: 44
другая сессия, global view: 50
другая сессия, temp view: AnalysisException TABLE_OR_VIEW_NOT_FOUND
```

Вторая сессия видит `global temporary view`, а обычный `temporary view` для неё не существует. Удалить `view` можно командой `DROP VIEW IF EXISTS`.

> **Пояснение:** в книге `view` строится на `us_delay_flights_tbl`, а у нас это временный `view`. Spark 4 не разрешает строить `global temporary view` поверх другого временного `view` и выдаёт ошибку. Поэтому мы взяли таблицу `managed_flights`.

### Catalog и метаданные

Метаданные `managed` и `unmanaged` таблиц собирает `Catalog`, высокоуровневая абстракция Spark SQL. В Spark 2.x у неё появились публичные методы: `spark.catalog.listDatabases()`, `listTables()` и `listColumns("<table>")`, а Spark 3.0 расширил её внешним каталогом (глава 12).

```text
databases: ['default', 'learn_spark_db']
date string True
delay int True
distance int True
origin string True
destination string True
```

Проверим разницу на диске: удалим обе таблицы и посмотрим, остались ли данные.

```python
managed_dir = f"{WH}/learn_spark_db.db/managed_flights"
spark.sql("DROP TABLE managed_flights")
spark.sql("DROP TABLE unmanaged_flights")
```

```text
до DROP: данные managed есть: True | данные unmanaged есть: True
после DROP: данные managed есть: False | данные unmanaged есть: True
в Catalog осталось: ['managed_empty', 'unmanaged_csv']
```

### Кэш и чтение таблицы в DataFrame

Таблицы и `view` можно кэшировать, как `DataFrame`, а в Spark 3.0 к этому добавилась опция `LAZY`: таблица кэшируется при первом использовании, а не сразу. Синтаксис: `CACHE [LAZY] TABLE <table-name>` и `UNCACHE TABLE <table-name>`.

Часто `pipeline` загрузки и ETL наполняет таблицы очищенными данными для приложений ниже по потоку. Прочитать такую таблицу в `DataFrame` можно двумя способами, и они равнозначны: `spark.sql("SELECT * FROM t")` и `spark.table("t")`.

## Источники данных для DataFrame и SQL

Spark SQL даёт единый интерфейс к разным источникам: Data Sources API. Два главных объекта в нём — `DataFrameReader` и `DataFrameWriter`.

![Схема: DataFrameReader читает источник в DataFrame, а DataFrameWriter записывает DataFrame в приёмник](/assets/learning-spark/ch04-reader-writer.png)

Над стрелками показан порядок вызовов. Читаем цепочкой `format`, `option`, `schema`, `load`, а пишем цепочкой `format`, `option`, `mode`, `partitionBy`, `save`.

### DataFrameReader и DataFrameWriter

Объект `DataFrameReader` создать нельзя: его берут у сессии как `spark.read` (статические данные) или `spark.readStream` (потоковые, глава 8). Шаблон такой: `format(...).option("key", "value").schema(...).load()`. Что задают методы:

| Метод | Что задаёт |
|---|---|
| `format()` | Формат: `parquet`, `csv`, `json`, `jdbc`, `orc`, `avro` и другие. Если не указать, будет Parquet или то, что задано в `spark.sql.sources.default` |
| `option()` | Пары ключ-значение: `mode` (`PERMISSIVE`, `FAILFAST`, `DROPMALFORMED`), `inferSchema`, `path`. По умолчанию `PERMISSIVE`. `mode` и `inferSchema` есть только у JSON и CSV |
| `schema()` | Строка `DDL` или `StructType`. Явная схема ускоряет чтение и гарантирует, что данные ей соответствуют |
| `load()` | Путь к данным. Можно опустить, если путь указан в `option("path", ...)` |

`DataFrameWriter` работает наоборот и берётся у самого `DataFrame`: `df.write` или `df.writeStream`. Шаблоны: `format().option().bucketBy().partitionBy().save(path)` и `format().option().sortBy().saveAsTable(table)`. Отличия от чтения: `mode` у записи означает режим записи (`append`, `overwrite`, `ignore`, по умолчанию `errorIfExists`), а ещё есть `bucketBy` (раскладка по бакетам, как в Hive), `partitionBy`, `save` и `saveAsTable`. По умолчанию запись тоже идёт в Parquet.

Посмотрим режимы записи на практике: вторая запись в ту же папку без `mode` падает, `append` дописывает, `ignore` молчит, `overwrite` заменяет:

```python
df.write.format("parquet").mode("append").save(pq)
df.write.format("parquet").mode("ignore").save(pq)
df.write.format("parquet").mode("overwrite").save(pq)
```

```text
по умолчанию: AnalysisException PATH_ALREADY_EXISTS
append: 20
ignore: 20
overwrite: 10
```

### Parquet

Parquet — открытый колоночный формат, который поддерживают многие системы обработки больших данных. Он сжимает данные и быстро отдаёт отдельные колонки, поэтому авторы советуют: после преобразования и очистки сохраняйте `DataFrame` в Parquet для следующих потребителей. Он же формат Spark по умолчанию и основа Delta Lake (глава 9).

Parquet хранится как папка: файлы с данными, служебные файлы вроде `_SUCCESS`, а в конце каждого файла метаданные (версия формата, схема, сведения о колонках). Поэтому схему при чтении указывать не нужно, кроме потоковых источников.

```python
(df.write.format("parquet")
 .mode("overwrite")
 .option("compression", "snappy")
 .save(pq))
parquet_df = spark.read.format("parquet").load(pq)
spark.sql(f"""CREATE OR REPLACE TEMPORARY VIEW us_delay_flights_tbl
USING parquet OPTIONS (path "{pq}")""")
```

```text
['_SUCCESS', 'part-00000-<uuid>-c000.snappy.parquet']
[('DEST_COUNTRY_NAME', 'string'), ('ORIGIN_COUNTRY_NAME', 'string'), ('count', 'int')]
```

Типы вернулись такими же, какими мы их записали. `View` на Parquet создаётся командой `USING parquet OPTIONS (path ...)`. Чтобы получить таблицу, а не файлы, пишите `saveAsTable` вместо `save`: получится `managed table`.

### JSON

JSON популярен тем, что проще XML и легче читается. Spark понимает два режима: в однострочном каждая строка файла — отдельный объект JSON, а в многострочном (`multiLine`) весь файл — один объект. Читается JSON так же, как Parquet: `format("json")`, а `view` создаётся через `USING json`.

```python
print("без multiLine:", spark.read.json(f"{BASE}/multi").columns)
print("с multiLine:", spark.read.option("multiLine", "true").json(f"{BASE}/multi").columns)
```

```text
без multiLine: ['DEST_COUNTRY_NAME', '_corrupt_record', 'count']
с multiLine: ['DEST_COUNTRY_NAME', 'count']
```

Если забыть `multiLine`, то Spark не сможет разобрать файл с массивом на нескольких строках: появится служебная колонка `_corrupt_record`. Опция `compression` работает при записи, а при чтении Spark определяет кодек по расширению файла.

### CSV

CSV распространён почти так же широко, как обычные текстовые файлы: поля разделены запятой, строка — запись. Разделитель можно сменить (`sep`), если запятая встречается в данных. Основные опции: `header` (первая строка с именами), `inferSchema` (по умолчанию `false`), `sep`, `escape`, `multiLine`, `dateFormat`. Но самое важное для надёжности — режим разбора `mode`. Проверим на файле, где в одной строке вместо числа стоит `abc`, а в другой пусто:

```python
for mode in ("PERMISSIVE", "DROPMALFORMED"):
    d = (spark.read.format("csv").schema(schema).option("header", "true")
         .option("mode", mode).option("nullValue", "").load(cs))
```

```text
PERMISSIVE [('Egypt', 'United States', 24), ('Grenada', 'United States', 54), ('Moldova', 'United States', None), ('Senegal', 'United States', None)]
DROPMALFORMED [('Egypt', 'United States', 24), ('Grenada', 'United States', 54), ('Senegal', 'United States', None)]
FAILFAST: FAILED_READ_FILE.NO_HINT
```

Режимы ведут себя так:

- `PERMISSIVE` оставляет испорченное значение пустым (`None`), а остальные поля строки сохраняет.
- `DROPMALFORMED` выбрасывает строку, которую не удалось разобрать.
- `FAILFAST` останавливает чтение с ошибкой.

Пустое поле у Senegal не считается ошибкой: опция `nullValue` с пустой строкой превращает его в `None`.

### Avro

Avro появился как встроенный источник в Spark 2.4. Его используют, например, в Apache Kafka для сериализации сообщений. Плюсы: данные прямо отображаются в JSON, скорость и компактность, поддержка многих языков. Чтение и запись такие же, как у других форматов: `format("avro")`. Из опций важны `avroSchema` (своя схема в JSON, она должна совпасть с данными) и `compression` (по умолчанию `snappy`, ещё `deflate`, `bzip2`, `xz`).

> **Пояснение:** в Spark 4 Avro лежит во внешнем модуле `spark-avro`, и в нашем образе его нет. Без модуля Spark отвечает ошибкой `AVRO_DATA_SOURCE_NOT_ENABLED`. Код ниже показан, но не запускался.

```python
# не запускается: нужен внешний модуль spark-avro, в образе его нет
df = spark.read.format("avro").load("/data/summary-data/avro/*")
df.write.format("avro").mode("overwrite").save("/tmp/data/avro/df_avro")
```

### ORC

ORC — ещё один оптимизированный колоночный формат. В Spark 2.x для него есть векторизованный читатель (`vectorized reader`): он читает блоки строк (часто по 1024) вместо одной строки за раз. Поэтому CPU работает меньше при сканировании, фильтрах, агрегациях и `join`. Его включают две настройки: `spark.sql.orc.impl` равна `native` и `spark.sql.orc.enableVectorizedReader` равна `true`. Чтение и запись обычные:

```python
orc = f"{BASE}/orc"
df.write.format("orc").mode("overwrite").option("compression", "snappy").save(orc)
```

```text
['_SUCCESS', 'part-00000-<uuid>-c000.snappy.orc']
10
```

### Картинки и бинарные файлы

В Spark 2.4 появился источник `image` для TensorFlow, PyTorch и других фреймворков глубокого обучения: загрузка наборов картинок важна для задач компьютерного зрения. Он возвращает колонку `image` (размеры `height`, `width`, число каналов `nChannels`, тип `mode`) и колонку `label`, которую Spark берёт из имени папки. В Spark 3.0 добавили источник `binaryFile`: каждый файл становится одной строкой с колонками `path`, `modificationTime`, `length` и `content` (сырые байты). Опция `pathGlobFilter` выбирает файлы по маске, например `*.jpg`.

Опция `recursiveFileLookup` читает вложенные папки и отключает поиск разбиения по папкам: колонка `label` пропадает. А вот записать `DataFrame` обратно в бинарные файлы нельзя.

```python
images_df = spark.read.format("image").option("dropInvalid", "true").load(imgs)
binary_df = (spark.read.format("binaryFile")
             .option("pathGlobFilter", "*.png")
             .load(imgs))
binary_rec = (spark.read.format("binaryFile")
              .option("pathGlobFilter", "*.png")
              .option("recursiveFileLookup", "true")
              .load(imgs))
```

```text
|height|width|nChannels|mode|label|
|     2|    2|        3|  16|    0|
['path', 'modificationTime', 'length', 'content', 'label']
с recursiveFileLookup: ['path', 'modificationTime', 'length', 'content']
```

Наши четыре картинки PNG 2×2 лежат в папках `label=0` и `label=1`.

## Итоги главы

- `spark.sql()` возвращает `DataFrame`, а SQL и `DataFrame` API дают одинаковый результат, потому что проходят один путь через `Catalyst`.
- Таблица состоит из данных и метаданных, а метаданные хранит `metastore` (по умолчанию Hive).
- У `managed table` `DROP TABLE` удаляет данные и метаданные, у `unmanaged table` только метаданные.
- `View` не хранит данных и исчезает вместе с приложением. `Temporary view` живёт в одной сессии, `global temporary view` виден всем сессиям приложения через `global_temp`.
- `Catalog` отдаёт метаданные баз, таблиц и колонок.
- `DataFrameReader` берут из `spark.read`, `DataFrameWriter` из `df.write`. Оба строятся цепочкой `format`, `option` и так далее.
- Parquet — формат по умолчанию и лучший выбор для хранения очищенных данных: колоночный, сжатый, со схемой внутри.
- Режимы разбора `PERMISSIVE`, `DROPMALFORMED` и `FAILFAST` решают, что делать с плохой строкой в JSON и CSV, а режимы записи `append`, `overwrite`, `ignore`, `errorIfExists` — что делать с уже существующими данными.
- Среди встроенных источников есть Avro, ORC, картинки и бинарные файлы; `binaryFile` не умеет писать обратно.

## Ключевые термины

| Термин | Значение |
|---|---|
| `SparkSession` | Единая точка входа в Spark 2.x и выше; у неё есть `spark.sql`, `spark.read` и `spark.catalog` |
| `metastore` | Хранилище метаданных таблиц; по умолчанию Hive metastore |
| `managed table` | Таблица, у которой Spark хранит и данные, и метаданные |
| `unmanaged table` | Таблица, у которой Spark хранит только метаданные |
| `temporary view` | `View` на одну `SparkSession` |
| `global temporary view` | `View` для всех сессий приложения, префикс `global_temp.` |
| `Catalog` | Высокоуровневый доступ к метаданным баз, таблиц и колонок |
| `DataFrameReader` | Читает данные в `DataFrame`: `spark.read` |
| `DataFrameWriter` | Пишет `DataFrame` в источник: `df.write` |
| Parquet | Открытый колоночный формат; формат Spark по умолчанию |
| ORC | Колоночный формат с векторизованным читателем |
| Avro | Формат для сериализации; много используется в Kafka |
| `mode` | Режим разбора (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`) или режим записи (`append`, `overwrite`, `ignore`, `errorIfExists`) |
| `binaryFile` | Источник, в котором файл становится одной строкой с байтами и метаданными |

## Что это значит на практике

- Храните очищенные данные в Parquet: схема лежит рядом с данными, читать быстро, а Delta Lake строится на нём же.
- Для CSV всегда задавайте схему и `mode`. `inferSchema` может превратить `02190925` в число без ведущего нуля.
- Для загрузки в `pipeline` берите `FAILFAST`, когда плохая строка недопустима, и `PERMISSIVE`, когда плохие данные нужно потом разобрать.
- Не оставляйте режим записи по умолчанию в регулярных задачах: он упадёт на второй запуск. Выбирайте `overwrite` или `append` осознанно.
- Для внешних данных (чужие файлы, `data lake`) создавайте `unmanaged table`: `DROP TABLE` не сотрёт файлы.
- Не стройте `global temporary view` поверх временных `view`: Spark 4 выдаст ошибку.
- Проверяйте типы после чтения через `printSchema()`: так видно, что Spark угадал неверно.

## Практика

Два скрипта главы запускаются в Docker с Spark 4.3.0. Данные генерируются в коде, а вывод выше настоящий.

- [ch04_sql_tables.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch04_sql_tables.py): `spark.sql`, `CASE`, таблицы, `view`, `Catalog`, `DROP`, кэш;
- [ch04_formats.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch04_formats.py): режимы записи, Parquet, JSON, CSV, ORC, `partitionBy`, `image` и `binaryFile`.

Запуск и установку см. в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. DuckDB заменяет здесь Spark SQL: те же `CASE`, `view` и форматы Parquet и CSV на маленькой таблице рейсов.

### Шаг 1. Создаём данные

```sql
CREATE TABLE flights AS
SELECT
    lpad((1 + i % 3)::VARCHAR, 2, '0') || lpad((1 + i * 7 % 28)::VARCHAR, 2, '0') || '0925' AS date,
    (i * 37) % 200 - 20 AS delay,
    [1846, 2586, 337, 740][1 + i % 4] AS distance,
    ['SFO', 'SFO', 'JFK', 'ORD'][1 + i % 4] AS origin,
    ['ORD', 'JFK', 'LAX', 'JFK'][1 + i % 4] AS destination
FROM generate_series(1, 60) t(i);
```

### Шаг 2. Проверяем

Должно быть 60 рейсов.

```sql
SELECT count(*) AS flights, min(delay) AS min_delay, max(delay) AS max_delay FROM flights;
```

### Задания

**1. Классы задержки.** Разбейте рейсы на классы: от 120 минут `Long Delays`, от 60 `Short Delays`, больше 0 `Tolerable Delays`, ровно 0 `No Delays`, остальные `Early`. Посчитайте рейсы в каждом классе, сначала самые частые.

<details><summary>Решение</summary>

```sql
SELECT
    CASE
        WHEN delay >= 120 THEN 'Long Delays'
        WHEN delay >= 60 THEN 'Short Delays'
        WHEN delay > 0 THEN 'Tolerable Delays'
        WHEN delay = 0 THEN 'No Delays'
        ELSE 'Early'
    END AS flight_delays,
    count(*) AS cnt
FROM flights GROUP BY flight_delays ORDER BY cnt DESC, flight_delays;
```

```text
flight_delays     cnt
Long Delays       19
Short Delays      18
Tolerable Delays  18
Early             4
No Delays         1
```

Границы 60 и 120 отнесены к старшему классу, поэтому «дыр» между классами нет.

</details>

**2. View не хранит данные.** Создайте `view` с рейсами из SFO и посчитайте строки. Затем добавьте в таблицу ещё один рейс из SFO и посчитайте строки в `view` снова.

<details><summary>Решение</summary>

```sql
CREATE VIEW sfo_flights AS SELECT date, delay, origin, destination FROM flights WHERE origin = 'SFO';
SELECT count(*) AS view_rows FROM sfo_flights;
INSERT INTO flights VALUES ('0101', 5, 337, 'SFO', 'LAX');
SELECT count(*) AS view_rows_after FROM sfo_flights;
```

```text
view_rows
30

view_rows_after
31
```

`View` хранит только запрос и каждый раз читает таблицу заново, поэтому новая строка сразу видна.

</details>

**3. Parquet и CSV.** Запишите таблицу в Parquet и в CSV и прочитайте обе обратно. Сравните тип колонки `distance`.

<details><summary>Решение</summary>

```sql
COPY flights TO '/tmp/duck_flights.parquet' (FORMAT parquet);
COPY flights TO '/tmp/duck_flights.csv' (HEADER, DELIMITER ',');
SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM read_parquet('/tmp/duck_flights.parquet'))
WHERE column_name = 'distance';
SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM read_csv('/tmp/duck_flights.csv'))
WHERE column_name = 'distance';
```

```text
column_name  column_type
distance     INTEGER

column_name  column_type
distance     BIGINT
```

Parquet хранит схему и возвращает тот `INTEGER`, который мы записали. В CSV типов нет, и DuckDB сам угадал тип `BIGINT`. Так же угадывает типы Spark при `inferSchema`.

</details>

## Вопросы для самопроверки

1. Почему запрос через `spark.sql()` и такой же запрос на `DataFrame` дают одинаковый результат и одинаково быстры?
2. Что останется на диске после `DROP TABLE` у `managed table` и у `unmanaged table`? Когда вы выберете каждую?
3. Чем `temporary view` отличается от `global temporary view` и от таблицы?
4. Что произойдёт при чтении CSV с испорченной строкой в режимах `PERMISSIVE`, `DROPMALFORMED` и `FAILFAST`? Какой режим выберете для `pipeline` и почему?
5. Почему авторы советуют Parquet для хранения очищенных данных и зачем при чтении Parquet не нужна схема?
6. Что меняется при `recursiveFileLookup` в источнике `binaryFile`, и почему так?

Предыдущая: [Structured API в Spark](/book-summaries/engineering/learning-spark/03-structured-apis/). Следующая: [Spark SQL и DataFrame: внешние источники данных](/book-summaries/engineering/learning-spark/05-sql-dataframes-external-sources/).
