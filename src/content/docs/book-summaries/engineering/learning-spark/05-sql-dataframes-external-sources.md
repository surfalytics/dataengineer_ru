---
title: "Learning Spark, глава 5: Spark SQL и DataFrame: внешние источники данных"
head:
  - tag: title
    content: "Spark SQL: UDF, JDBC, Tableau и оконные функции | Инжиниринг Данных"
description: "Конспект главы 5 Learning Spark на русском. UDF и pandas UDF, Thrift server, Beeline, Tableau, JDBC, higher-order функции, join, window и pivot."
sidebar:
  order: 5
  label: "5. Spark SQL и DataFrame: внешние источники данных"
tags:
  - books
  - spark
---

**Главная мысль:** Spark SQL не живёт сам по себе. Он принимает ваши функции (`UDF`), отвечает на запросы из консоли и BI-инструментов и читает чужие базы через `JDBC`. А для массивов, `union`, `join`, оконных функций и `pivot` у него есть готовые средства.

## О чём глава

В [предыдущей главе](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/) мы читали встроенные форматы файлов. Здесь Spark SQL выходит наружу: к своим функциям, к клиентам и к внешним системам. Темы:

- `UDF` и `pandas UDF`;
- запросы из `spark-sql`, Beeline и Tableau;
- чтение и запись во внешние базы: PostgreSQL, MySQL, Azure Cosmos DB, MS SQL Server;
- сложные типы и `higher-order function`;
- частые операции: `union`, `join`, оконные функции, изменение колонок, `pivot`.

Все примеры на Python (PySpark). Версия Spark — 4.3. Как её ставить, написано в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

![Схема: клиенты и внешние источники вокруг Spark SQL](/assets/learning-spark/ch05-sql-access.png)

Слева клиенты, в центре Spark SQL, справа системы, откуда он читает данные.

## Spark SQL и Apache Hive

Spark SQL вырос из проекта Shark. Shark построили на коде Hive поверх Spark, и он стал одним из первых интерактивных SQL-движков на Hadoop: быстрый, как хранилище данных, и масштабируется, как Hive. Сегодняшний Spark SQL код Hive уже не использует.

Spark SQL соединяет реляционную обработку с функциональным API Spark: вы пишете декларативные запросы и из того же кода вызываете сложные аналитические библиотеки, например для машинного обучения. Единая точка входа, начиная со Spark 2.x, — `SparkSession`.

## UDF: свои функции

Встроенных функций в Spark много, но иногда нужна своя. Такую функцию называют `UDF` (`user-defined function`).

### UDF в Spark SQL

Главная польза `UDF` в том, что её видит SQL. Например, дата-сайентист оборачивает ML-модель в `UDF`, а аналитик вызывает её из запроса и не знает, как модель устроена. `UDF` живёт только в сессии: в `metastore` она не сохраняется.

```python
def cubed(s):
    return s * s * s

spark.udf.register("cubed", cubed, LongType())
spark.range(1, 9).createOrReplaceTempView("udf_test")
spark.sql("SELECT id, cubed(id) AS id_cubed FROM udf_test ORDER BY id").show()
```

```text
+---+--------+
| id|id_cubed|
+---+--------+
|  1|       1|
|  2|       8|
|  3|      27|
|  4|      64|
|  5|     125|
|  6|     216|
|  7|     343|
|  8|     512|
+---+--------+
```

### Порядок вычисления и null

Spark SQL (SQL, `DataFrame` и `Dataset`) не гарантирует порядок вычисления частей выражения. В запросе `WHERE s IS NOT NULL AND strlen(s) > 1` проверка на `NULL` может выполниться после `strlen`, и функция упадёт на пустом значении. Есть два способа:

1. Сделать `UDF` безопасной: проверять `None` внутри неё.
2. Вызывать `UDF` внутри `IF` или `CASE WHEN`, где проверка стоит в условии.

```python
def strlen_safe(s):
    return None if s is None else len(s)

spark.udf.register("strlen_safe", strlen_safe, "int")
spark.sql("""
    SELECT s, strlen_safe(s) AS len_in_udf,
           CASE WHEN s IS NOT NULL THEN strlen_safe(s) END AS len_in_case
    FROM test1 ORDER BY s
""").show()
```

```text
+-----+----------+-----------+
|    s|len_in_udf|len_in_case|
+-----+----------+-----------+
| NULL|      NULL|       NULL|
|    a|         1|          1|
|spark|         5|          5|
+-----+----------+-----------+
```

### pandas UDF: быстрее и параллельно

Раньше `UDF` на PySpark работали медленнее, чем на Scala. Причина: данные ходили между JVM и Python, и этот перенос стоил дорого. В Spark 2.3 появились `pandas UDF` (их ещё называют векторными `UDF`). Они передают данные через Apache Arrow и обрабатывают их с помощью pandas. Python читает формат Arrow напрямую, поэтому сериализовать данные (pickle) больше не нужно. И функция работает не со строкой, а с целой `pandas.Series`.

![Схема: обычная Python UDF получает строки по одной через pickle, pandas UDF получает пачки через Arrow](/assets/learning-spark/ch05-pandas-udf.png)

В Spark 3.0 `pandas UDF` разделили на два API:

- **`pandas UDF`.** Spark выводит тип из подсказок типов Python: `Series` в `Series`, `Iterator` в `Iterator`, `Series` в одно значение (`scalar`).
- **`Pandas Function API`.** Локальная функция применяется к `DataFrame` целиком: вход и выход — объекты pandas. Это `map`, `grouped map` и `cogrouped map`.

```python
def cubed_pd(a: pd.Series) -> pd.Series:
    return a * a * a

cubed_udf = pandas_udf(cubed_pd, returnType=LongType())

print(cubed_pd(pd.Series([1, 2, 3])))
spark.range(1, 4).select("id", cubed_udf(col("id")).alias("cubed")).orderBy("id").show()
```

```text
0     1
1     8
2    27
dtype: int64
+---+-----+
| id|cubed|
+---+-----+
|  1|    1|
|  2|    8|
|  3|   27|
+---+-----+
```

Локальный вызов считает всё на `driver`, а вызов через `pandas_udf` запускает настоящие Spark `job`. В Spark UI данные уходят на `executor` пачками Arrow, а шаг `ArrowEvalPython` показывает, что работает `pandas UDF`. Шаги `WholeStageCodegen` — это генерация кода из Project Tungsten. Она заметно экономит CPU.

Для Spark 4.3 нужен `pyarrow` версии 18 или новее, иначе `pandas_udf` выдаст ошибку `UNSUPPORTED_PACKAGE_VERSION`.

## Запросы из консоли, Beeline и Tableau

Запросы к Spark SQL можно отправлять тремя способами: через консоль `spark-sql`, через Beeline и через BI-инструменты вроде Tableau и Power BI.

### Консоль spark-sql

`spark-sql` — удобная консоль для SQL. Она работает с `Hive metastore` в `local mode`, но не обращается к `Thrift JDBC/ODBC server`. Этот сервер (`Spark Thrift Server`, STS) нужен клиентам, которые подключаются по протоколам JDBC и ODBC. Запуск: `./bin/spark-sql` из папки `$SPARK_HOME`. Дальше работают обычные команды:

```text
spark-sql> CREATE TABLE people (name STRING, age int);
spark-sql> INSERT INTO people VALUES ("Michael", NULL);
spark-sql> INSERT INTO people VALUES ("Andy", 30);
spark-sql> INSERT INTO people VALUES ("Samantha", 19);
spark-sql> SELECT name FROM people WHERE age IS NULL;
Michael
```

### Beeline и Thrift server

Beeline — консольный JDBC-клиент для HiveServer2, он знает язык HiveQL. Им же можно запускать запросы Spark SQL: Thrift-сервер Spark соответствует HiveServer2 из Hive 1.2.1. Порядок такой: запустить сервер, подключиться, выполнить запросы, остановить сервер.

```bash
./sbin/start-all.sh            # если driver и worker ещё не запущены
./sbin/start-thriftserver.sh
./bin/beeline
!connect jdbc:hive2://localhost:10000
# ... запросы ...
./sbin/stop-thriftserver.sh
```

По умолчанию Beeline работает без защиты: логин — ваше имя пользователя, пароль пустой.

### Tableau

BI-инструмент подключается к Spark тем же путём, через Thrift-сервер. Автор показывает это на Tableau Desktop 2019.2: нужен Spark ODBC driver версии 1.2.0 или новее. Шаги такие:

1. Запустить Thrift-сервер, как для Beeline.
2. В диалоге Connect выбрать More…, затем Spark SQL.
3. Ввести параметры: сервер `localhost`, порт `10000`, тип `SparkThriftServer`, вход по имени пользователя, SSL выключен.
4. Выбрать схему `default`, перетащить таблицу `people` в рабочую область и нажать Update Now.

После этого запросы, `join` и остальное работают как с любым источником Tableau. Скриншоты диалогов Tableau мы не перерисовываем: схема выше показывает тот же путь.

## Внешние источники данных

### JDBC и базы SQL

Data source API Spark SQL читает данные из других баз по `JDBC`. Результат приходит как `DataFrame`, поэтому вы получаете все плюсы Spark SQL: скорость и соединение с другими источниками. Библиотека базы (`jar`) должна быть в `classpath`: `./bin/spark-shell --driver-class-path $database.jar --jars $database.jar`.

Основные свойства соединения:

| Свойство | Что задаёт |
|---|---|
| `url` | Адрес `JDBC`, например `jdbc:postgresql://localhost/test` |
| `dbtable` | Таблица для чтения или записи |
| `query` | Запрос вместо таблицы. Нельзя задавать вместе с `dbtable` |
| `driver` | Класс библиотеки базы |
| `user`, `password` | Логин и пароль |

#### Почему важно разбивать чтение на partition

Без настроек все данные идут через одно соединение с `driver`. Соединение перегружается, чтение сильно замедляется, а заодно перегружается и источник. Поэтому для больших объёмов задают четыре свойства:

| Свойство | Что задаёт |
|---|---|
| `numPartitions` | Сколько `partition` читать параллельно. Это же максимум одновременных `JDBC`-соединений |
| `partitionColumn` | Колонка, по которой делят данные. Числа, даты или время |
| `lowerBound` | Нижняя граница значений колонки для шага (`stride`) |
| `upperBound` | Верхняя граница для шага |

Пример из книги: `numPartitions` равен 10, границы 1000 и 10000. Шаг получается 1000, и Spark создаёт 10 `partition`. Это то же самое, что 10 запросов `SELECT * FROM table WHERE partitionColumn BETWEEN 1000 AND 2000` и так далее до 10000.

![Схема: таблица во внешней БД делится на четыре запроса по partitionColumn, каждый запрос становится одной partition](/assets/learning-spark/ch05-jdbc-partitions.png)

На схеме `numPartitions` равен 4, границы 2000 и 4000, шаг 500. Каждый запрос идёт по своему соединению и даёт одну `partition`.

Советы автора:

- **Сколько `partition`.** Начните с числа, кратного количеству worker-узлов: при четырёх узлах попробуйте 4 или 8. Но смотрите и на источник. Если у источника есть окно обработки (время, отведённое под пакетные чтения), число параллельных запросов можно поднять до максимума. У OLTP-базы такого окна нет, она обрабатывает данные непрерывно. Там число параллельных запросов снижают, чтобы её не перегрузить.
- **Границы.** Считайте их по реальным минимуму и максимуму колонки. Если значения лежат от 2000 до 4000, а границы 1000 и 10000, всю работу сделают всего два-три запроса из десяти, остальные почти ничего не вернут. Верная настройка — 2000 и 4000.
- **Колонка.** Берите колонку с равномерным распределением, иначе будет `skew`. Если большая часть значений равна 2500, один `task` получит почти всё. Тогда выберите другую колонку или сгенерируйте новую, например `hash` нескольких колонок.

Проверим советы на встроенной базе Derby: сервер ей не нужен. В таблице 2000 заказов с `order_id` от 2000 до 3999.

```python
URL = "jdbc:derby:memory:orders;create=true"
DRIVER = "org.apache.derby.jdbc.EmbeddedDriver"

def read(lower, upper, n):
    return (spark.read.format("jdbc").option("url", URL).option("driver", DRIVER)
            .option("dbtable", "ORDERS").option("partitionColumn", "ORDER_ID")
            .option("lowerBound", lower).option("upperBound", upper)
            .option("numPartitions", n).load())

report("bounds 2000..4000, 10 partitions:", read(2000, 4000, 10))
report("bounds 1000..10000, 10 partitions:", read(1000, 10000, 10))
report("bounds 3000..3500, 2 partitions:", read(3000, 3500, 2))
```

```text
bounds 2000..4000, 10 partitions: [200, 200, 200, 200, 200, 200, 200, 200, 200, 200] всего строк: 2000
bounds 1000..10000, 10 partitions: [800, 900, 300] всего строк: 2000
bounds 3000..3500, 2 partitions: [1250, 750] всего строк: 2000
```

Функция `report` печатает число строк в каждой `partition` (через `spark_partition_id()`) и общее число строк. При верных границах нагрузка ровная, при плохих работают только три `partition` из десяти. Третья строка показывает: границы ничего не отфильтровывают, все 2000 строк прочитаны. Они задают только шаг.

> **Пояснение:** в книге запросы записаны с `BETWEEN`. На деле первый запрос Spark открыт снизу (`< граница`), последний открыт сверху (`>= граница`). Поэтому строки вне границ не теряются.

### PostgreSQL, MySQL и MS SQL Server

Схема для всех трёх одна: скачать `jar` базы с Maven, добавить в `classpath` (`--jars`), прочитать через `format("jdbc")` и записать назад. Меняются только адрес и класс библиотеки. Книга даёт код на Scala и Python, мы оставляем Python.

```python
# не запускается: нужен сервер PostgreSQL
jdbcDF = (spark.read.format("jdbc")
    .option("url", "jdbc:postgresql://[DBSERVER]")
    .option("dbtable", "[SCHEMA].[TABLENAME]")
    .option("user", "[USERNAME]")
    .option("password", "[PASSWORD]")
    .load())

(jdbcDF.write.format("jdbc")
    .option("url", "jdbc:postgresql://[DBSERVER]")
    .option("dbtable", "[SCHEMA].[TABLENAME]")
    .option("user", "[USERNAME]")
    .option("password", "[PASSWORD]")
    .save())
```

Есть и второй способ: `spark.read.jdbc(url, table, properties={...})`. Для других баз отличаются только эти значения:

| База | Адрес `url` | Класс библиотеки |
|---|---|---|
| PostgreSQL | `jdbc:postgresql://[DBSERVER]` | подбирается сам |
| MySQL | `jdbc:mysql://[DBSERVER]:3306/[DATABASE]` | `com.mysql.jdbc.Driver` |
| MS SQL Server | `jdbc:sqlserver://[DBSERVER]:1433;database=[DATABASE]` | `com.microsoft.sqlserver.jdbc.SQLServerDriver` |

### Azure Cosmos DB и другие источники

Для Cosmos DB нужен коннектор `azure-cosmosdb-spark` (в книге версия под Spark 2.4), его подключают через `--jars` или `--packages`. Настройки передают словарём: `Endpoint`, `Masterkey`, `Database`, `Collection`. При чтении задают `query_custom`, чтобы запрос использовал индексы Cosmos DB. При записи включают `Upsert`.

```python
# не запускается: нужен аккаунт Azure Cosmos DB и коннектор
readConfig = {"Endpoint": "https://[ACCOUNT].documents.azure.com:443/",
              "Masterkey": "[MASTER KEY]", "Database": "[DATABASE]",
              "Collection": "[COLLECTION]",
              "query_custom": "SELECT c.colA, c.coln FROM c WHERE c.origin = 'SEA'"}
df = (spark.read.format("com.microsoft.azure.cosmosdb.spark")
      .options(**readConfig).load())
```

Среди других источников книга называет Cassandra, Snowflake и MongoDB.

## Сложные типы и higher-order функции

Сложный тип собран из простых, например массив чисел. Поэтому его хочется менять напрямую, по элементам. Книга показывает два типичных подхода и оба считает дорогими.

**Вариант 1: `explode` и `collect_list`.** Сначала `explode(values)` создаёт строку на каждый элемент, потом элементы собираются обратно:

```text
SELECT id, collect_list(value + 1) AS values
FROM (SELECT id, EXPLODE(values) AS value FROM table) x
GROUP BY id
```

`GROUP BY` вызывает `shuffle`, поэтому порядок элементов в новом массиве может не совпасть со старым. Массив может быть очень длинным, и тогда запрос дорог.

**Вариант 2: `UDF`.** Функция проходит по элементам через `map()` и прибавляет единицу. Порядок сохраняется, и это лучше. Но сериализация и десериализация данных сами по себе дорогие. Зато `UDF` не страдает от нехватки памяти на `executor`, которая бывает у `collect_list` на больших данных.

### Встроенные функции

С Spark 2.4 есть встроенные функции для массивов и словарей (`map`). Они дешевле обоих вариантов. Вот самые частые на примерах:

| Функция | Что делает | Результат |
|---|---|---|
| `array_distinct(array(1, 2, 3, null, 3))` | Убирает повторы | `[1, 2, 3, NULL]` |
| `array_intersect(array(1, 2, 3), array(1, 3, 5))` | Пересечение массивов | `[1, 3]` |
| `array_union(array(1, 2, 3), array(1, 3, 5))` | Объединение без повторов | `[1, 2, 3, 5]` |
| `array_except(array(1, 2, 3), array(1, 3, 5))` | Есть в первом, нет во втором | `[2]` |
| `arrays_overlap(array(1, 2, 3), array(3, 4, 5))` | Есть ли общий элемент | `true` |
| `flatten(array(array(1, 2), array(3, 4)))` | Массив массивов в один | `[1, 2, 3, 4]` |
| `map_concat(map(1, 'a', 2, 'b'), map(2, 'c', 3, 'd'))` | Объединяет словари | `{1 -> a, 2 -> c, 3 -> d}` |
| `element_at(map(1, 'a', 2, 'b'), 2)` | Значение по ключу | `b` |

> **Пояснение:** в Spark 4 ANSI-режим включён по умолчанию. `map_concat` с одним ключом в двух словарях здесь падает с ошибкой `DUPLICATED_MAP_KEY`. Чтобы получить результат из таблицы, мы задали `spark.sql.mapKeyDedupPolicy` равным `LAST_WIN`: побеждает последнее значение.

### Higher-order функции

`Higher-order function` принимает анонимную функцию (лямбду) как аргумент. Так вы меняете элементы массива, не разворачивая его в строки. Возьмём два массива температур:

```python
schema = "id int, celsius array<int>"
data = [(1, [35, 36, 32, 30, 40, 42, 38]), (2, [31, 32, 34, 55, 56])]
spark.createDataFrame(data, schema).createOrReplaceTempView("tC")
```

- `transform(array, функция)` применяет функцию к каждому элементу. Это похоже на `map()`: каждый элемент даёт один новый элемент.
- `filter(array, условие)` оставляет элементы, для которых условие истинно.
- `exists(array, условие)` возвращает `true`, если условие выполнено хотя бы для одного элемента.
- `reduce(array, начало, слияние, финал)` сворачивает массив в одно значение. Функция слияния по очереди добавляет каждый элемент в буфер (накопитель). Финальная функция превращает итоговый буфер в ответ.

```python
spark.sql("""
    SELECT id,
           transform(celsius, t -> ((t * 9) div 5) + 32) AS fahrenheit,
           filter(celsius, t -> t > 38) AS high,
           exists(celsius, t -> t = 38) AS has_38,
           reduce(celsius, 0, (acc, t) -> acc + t,
                  acc -> (acc div size(celsius) * 9 div 5) + 32) AS avg_fahrenheit
    FROM tC ORDER BY id
""").show(truncate=False)
```

```text
+---+-------------------------------+--------+------+--------------+
|id |fahrenheit                     |high    |has_38|avg_fahrenheit|
+---+-------------------------------+--------+------+--------------+
|1  |[95, 96, 89, 86, 104, 107, 100]|[40, 42]|true  |96            |
|2  |[87, 89, 93, 131, 132]         |[55, 56]|false |105           |
+---+-------------------------------+--------+------+--------------+
```

## Частые операции с DataFrame

Операций у `DataFrame` очень много, полный список лежит в документации Spark SQL. Глава разбирает три группы: `union` с `join`, оконные функции и изменение таблицы.

Книга берёт данные о задержках рейсов в США (больше 1,3 млн строк) и справочник аэропортов. Из рейсов делают маленькую таблицу `foo`: три рейса Seattle (SEA) — San Francisco (SFO) за 1 января. Мы генерируем рейсы сами, с фиксированным seed. Таблицы называются так же: `departureDelays`, `airports_na`, `foo`.

> **Пояснение:** в Spark 4 `CAST` строки в число при плохом значении падает с ошибкой, а в Spark 3 давал `NULL`. Книга приводит `delay` и `distance` из строк в `INT` через `CAST`. У нас числа сразу целые, поэтому приведение не нужно.

### Union

`union()` склеивает два `DataFrame` с одинаковой схемой. Строки `foo` взяты из общей таблицы рейсов, поэтому после склейки каждая из них встречается дважды:

```python
bar = delays.union(foo)
bar.createOrReplaceTempView("bar")
spark.sql("""
    SELECT * FROM bar
    WHERE origin = 'SEA' AND destination = 'SFO' AND date LIKE '01010%' AND delay > 0
    ORDER BY date, delay
""").show()
```

```text
+--------+-----+--------+------+-----------+
|    date|delay|distance|origin|destination|
+--------+-----+--------+------+-----------+
|01010710|   31|     590|   SEA|        SFO|
|01010710|   31|     590|   SEA|        SFO|
|01010730|    5|     590|   SEA|        SFO|
|01010730|    5|     590|   SEA|        SFO|
|01010955|  104|     590|   SEA|        SFO|
|01010955|  104|     590|   SEA|        SFO|
+--------+-----+--------+------+-----------+
```

### Join

По умолчанию Spark SQL делает `inner join`. Доступны и другие типы: `cross`, `outer`, `full`, `full_outer`, `left`, `left_outer`, `right`, `right_outer`, `left_semi`, `left_anti`. Соединим `foo` со справочником аэропортов, чтобы получить город и штат отправления:

```python
spark.sql("""
    SELECT a.City, a.State, f.date, f.delay, f.distance, f.destination
    FROM foo f JOIN airports_na a ON a.IATA = f.origin ORDER BY f.date
""").show()
```

```text
+-------+-----+--------+-----+--------+-----------+
|   City|State|    date|delay|distance|destination|
+-------+-----+--------+-----+--------+-----------+
|Seattle|   WA|01010710|   31|     590|        SFO|
|Seattle|   WA|01010730|    5|     590|        SFO|
|Seattle|   WA|01010955|  104|     590|        SFO|
+-------+-----+--------+-----+--------+-----------+
```

### Оконные функции

Оконная функция (window function) берёт значения из группы строк, «окна», и возвращает значение для каждой входной строки. В отличие от `GROUP BY`, строки не схлопываются. Функции в книге делятся на ранжирующие (`rank`, `dense_rank`, `percent_rank`, `ntile`, `row_number`) и аналитические (`cume_dist`, `first_value`, `last_value`, `lag`, `lead`).

Задача: для каждого аэропорта вылета (SEA, SFO, JFK) найти три направления с наибольшей суммой задержек. Без окон пришлось бы запустить три запроса и склеить их через `union`. С `dense_rank()` хватает одного:

```python
spark.sql("""
    SELECT origin, destination, TotalDelays, rank FROM (
        SELECT origin, destination, TotalDelays,
               dense_rank() OVER (PARTITION BY origin ORDER BY TotalDelays DESC) AS rank
        FROM departureDelaysWindow) t
    WHERE rank <= 3 ORDER BY origin, rank
""").show()
```

```text
+------+-----------+-----------+----+
|origin|destination|TotalDelays|rank|
+------+-----------+-----------+----+
|   JFK|        ATL|       4340|   1|
|   JFK|        SFO|       4012|   2|
|   JFK|        LAX|       3934|   3|
|   SEA|        ATL|       4374|   1|
|   SEA|        SFO|       4239|   2|
|   SEA|        JFK|       4237|   3|
|   SFO|        SEA|       4075|   1|
|   SFO|        JFK|       3784|   2|
|   SFO|        LAX|       3757|   3|
+------+-----------+-----------+----+
```

`PARTITION BY origin` делит строки на окна, `ORDER BY` ранжирует внутри окна. (Числа в таблице наши, у книги другие данные.) Автор предупреждает: каждое окно должно уместиться в один `executor`, оно собирается в одну `partition`. Поэтому размер окна нужно ограничивать.

### Изменение DataFrame

`DataFrame` неизменяемый. Любое «изменение» создаёт новый `DataFrame`. Так сделано, чтобы у данных оставался `lineage`: иначе Spark не смог бы пересчитать потерянное. Три приёма:

- `withColumn()` добавляет колонку;
- `drop()` убирает колонку;
- `withColumnRenamed()` меняет имя.

```python
foo2 = foo.withColumn("status", expr("CASE WHEN delay <= 10 THEN 'On-time' ELSE 'Delayed' END"))
foo3 = foo2.drop("delay")
foo4 = foo3.withColumnRenamed("status", "flight_status")
foo4.orderBy("date").show()
```

```text
+--------+--------+------+-----------+-------------+
|    date|distance|origin|destination|flight_status|
+--------+--------+------+-----------+-------------+
|01010710|     590|   SEA|        SFO|      Delayed|
|01010730|     590|   SEA|        SFO|      On-time|
|01010955|     590|   SEA|        SFO|      Delayed|
+--------+--------+------+-----------+-------------+
```

### Pivot

`Pivot` меняет строки и колонки местами: значения одной колонки становятся заголовками колонок. Заодно можно считать агрегаты. Здесь месяцы 1 и 2 превращаются в `JAN` и `FEB`, а для каждого направления из Seattle считаются средняя и максимальная задержка:

```python
spark.sql("""
    SELECT * FROM (
        SELECT destination, CAST(SUBSTRING(date, 0, 2) AS int) AS month, delay
        FROM departureDelays WHERE origin = 'SEA')
    PIVOT (CAST(AVG(delay) AS DECIMAL(4, 2)) AS AvgDelay, MAX(delay) AS MaxDelay
           FOR month IN (1 JAN, 2 FEB))
    ORDER BY destination
""").show()
```

```text
+-----------+------------+------------+------------+------------+
|destination|JAN_AvgDelay|JAN_MaxDelay|FEB_AvgDelay|FEB_MaxDelay|
+-----------+------------+------------+------------+------------+
|        ATL|       53.66|         118|       55.60|         115|
|        DEN|       62.65|         120|       54.11|         118|
|        JFK|       60.53|         120|       55.62|         115|
|        LAX|       68.70|         119|       44.00|         119|
|        ORD|       50.61|         119|       55.81|         118|
|        SFO|       50.50|         118|       56.59|         118|
+-----------+------------+------------+------------+------------+
```

## Итоги главы

- Spark SQL вырос из Shark и Hive, но современный движок код Hive не использует.
- `UDF` регистрируется в сессии и вызывается из SQL. Она не сохраняется в `metastore`.
- Spark SQL не гарантирует порядок вычисления частей выражения, поэтому `null` проверяют внутри `UDF` или в `CASE WHEN`.
- `pandas UDF` работают с пачками через Arrow и pandas, поэтому быстрее обычных Python `UDF`.
- Консоль `spark-sql` работает без Thrift-сервера. Beeline и BI-инструменты, такие как Tableau, подключаются через него по JDBC и ODBC.
- Чтение из JDBC нужно разбивать на `partition` через `numPartitions`, `partitionColumn` и границы. Иначе всё пойдёт через одно соединение.
- Границы нужно брать по реальным значениям колонки, а колонку — с равномерным распределением, иначе будет `skew`.
- Для массивов и словарей лучше встроенные функции и `higher-order function`, чем `explode` с `collect_list` или `UDF`.
- `DataFrame` неизменяем: `withColumn`, `drop` и `withColumnRenamed` возвращают новый `DataFrame`.
- Окно оконной функции должно помещаться в один `executor`, поэтому его размер ограничивают.

## Ключевые термины

| Термин | Значение |
|---|---|
| `UDF` | Своя функция, которую вызывают из SQL или `DataFrame` |
| `pandas UDF` | `UDF` на Python, которая получает `pandas.Series` пачками через Arrow |
| `Thrift server` | Сервер JDBC/ODBC в Spark. Через него подключаются Beeline и BI-инструменты |
| `Beeline` | Консольный JDBC-клиент для запросов к HiveServer2 и Spark Thrift server |
| `JDBC` | Стандарт подключения к базам данных из Java |
| `numPartitions` | Число параллельных запросов и соединений при чтении по JDBC |
| `partitionColumn` | Колонка, по которой делят таблицу на `partition` при чтении |
| `stride` | Шаг между границами соседних запросов |
| `higher-order function` | Функция, которая принимает другую функцию (лямбду) как аргумент |
| `window function` | Оконная функция: считает по группе строк и возвращает значение для каждой строки |
| `pivot` | Разворот значений колонки в заголовки колонок |
| `skew` | Один ключ несёт много данных, один `task` тормозит всех |

## Что это значит на практике

- Если нужна логика на Python, сначала ищите встроенную функцию. Затем `pandas UDF`, и только потом обычную `UDF`.
- Регистрируйте `UDF` на каждую сессию заново: после перезапуска её нет.
- Читая большую таблицу по `JDBC`, всегда задавайте `numPartitions`, `partitionColumn` и границы. Для границ запросите `MIN` и `MAX` колонки.
- Держите `numPartitions` небольшим для живых OLTP-баз и не делите чтение по колонке с перекосом.
- Для данных в массивах используйте `transform`, `filter`, `exists` и `reduce`, а не `explode` с `GROUP BY`.
- Для топ-N в группе берите `dense_rank()` с `PARTITION BY`, а не несколько запросов с `union`.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. DuckDB знает те же идеи: оконные функции, `PIVOT` и функции со списками (`list_transform`, `list_filter`, `list_reduce`).

### Шаг 1. Создаём данные

```sql
CREATE TABLE flights AS SELECT * FROM (VALUES
    ('SEA', 'SFO', 1, 31), ('SEA', 'SFO', 1, 104), ('SEA', 'SFO', 2, 5),
    ('SEA', 'DEN', 1, 20), ('SEA', 'DEN', 2, 40), ('SEA', 'ORD', 1, 10),
    ('SEA', 'LAX', 2, -3), ('SFO', 'LAX', 1, 60), ('SFO', 'LAX', 2, 35),
    ('SFO', 'ORD', 1, 25), ('SFO', 'JFK', 2, 15), ('SFO', 'SEA', 1, 5),
    ('SFO', 'SEA', 2, 8)
) t(origin, destination, month, delay);

CREATE TABLE temps AS SELECT * FROM (VALUES
    (1, [35, 36, 32, 30, 40, 42, 38]),
    (2, [31, 32, 34, 55, 56])
) t(id, celsius);
```

### Шаг 2. Проверяем

Должно быть 13 и 2 строки.

```sql
SELECT count(*) AS flights FROM flights;
SELECT count(*) AS temps FROM temps;
```

### Задания

**1. Для каждого `origin` найдите два направления с наибольшей суммой задержек.**

<details><summary>Решение</summary>

```sql
SELECT origin, destination, total_delay, rnk FROM (
    SELECT origin, destination, sum(delay) AS total_delay,
           dense_rank() OVER (PARTITION BY origin ORDER BY sum(delay) DESC) AS rnk
    FROM flights GROUP BY origin, destination
) WHERE rnk <= 2 ORDER BY origin, rnk;
```

```text
SEA | SFO | 140 | 1
SEA | DEN |  60 | 2
SFO | LAX |  95 | 1
SFO | ORD |  25 | 2
```

Окно строится по `origin`, внутри него направления ранжируются по сумме задержек.

</details>

**2. Покажите для рейсов из SEA среднюю и максимальную задержку по направлениям, с месяцами в колонках.**

<details><summary>Решение</summary>

```sql
PIVOT (SELECT destination, month, delay FROM flights WHERE origin = 'SEA')
ON month USING avg(delay) AS avg_delay, max(delay) AS max_delay
GROUP BY destination ORDER BY destination;
```

```text
DEN | 20.0 | 20   | 40.0 | 40
LAX | NULL | NULL | -3.0 | -3
ORD | 10.0 | 10   | NULL | NULL
SFO | 67.5 | 104  | 5.0  | 5
```

Колонки называются `1_avg_delay`, `1_max_delay`, `2_avg_delay`, `2_max_delay`. Если рейсов в месяце не было, стоит `NULL`.

</details>

**3. Для каждой строки `temps` переведите температуры в Fahrenheit, оставьте значения выше 38 и посчитайте сумму.**

<details><summary>Решение</summary>

```sql
SELECT id,
       list_transform(celsius, t -> t * 9 // 5 + 32) AS fahrenheit,
       list_filter(celsius, t -> t > 38) AS high,
       list_reduce(celsius, (acc, t) -> acc + t) AS total
FROM temps ORDER BY id;
```

```text
1 | [95, 96, 89, 86, 104, 107, 100] | [40, 42] | 253
2 | [87, 89, 93, 131, 132]          | [55, 56] | 208
```

Лямбды работают прямо над списком, без `unnest` и `GROUP BY`.

</details>

## Вопросы для самопроверки

1. Почему `UDF` в Spark SQL нужно делать безопасной к `null`, а не полагаться на `IS NOT NULL` в `WHERE`?
2. Чем `pandas UDF` быстрее обычной Python `UDF`? Что именно экономит Arrow?
3. Чтение из `JDBC` идёт в одну `partition`. Какие четыре свойства это исправят и по какому правилу их выбирать?
4. Границы `lowerBound` и `upperBound` равны 1000 и 10000, а данные лежат в диапазоне 2000–4000. Что произойдёт и как это исправить?
5. Почему `transform()` лучше, чем `explode` вместе с `collect_list`? Когда вместо них нужна `UDF`?
6. Зачем оконной функции окно ограничивают по размеру и что будет, если окно не помещается в один `executor`?

Предыдущая: [Spark SQL и DataFrame: встроенные источники данных](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/). Следующая: [Spark SQL и Dataset](/book-summaries/engineering/learning-spark/06-sql-and-datasets/).
