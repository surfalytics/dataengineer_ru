---
title: "Learning Spark, глава 3: Structured API в Spark"
head:
  - tag: title
    content: "Spark DataFrame, схема и Catalyst: как работает Structured API | Инжиниринг Данных"
description: "Конспект главы 3 Learning Spark на русском. RDD, DataFrame, Dataset, схемы, операции с колонками, оптимизатор Catalyst и Tungsten."
sidebar:
  order: 3
  label: "3. Structured API в Spark"
tags:
  - books
  - spark
---

**Главная мысль:** структура даёт Spark возможность понять, что вы хотите посчитать. Поэтому `DataFrame` и SQL работают быстрее и читаются проще, чем низкоуровневый `RDD`. Оптимизатор `Catalyst` строит план запроса, а Tungsten генерирует компактный код.

## О чём глава

В [главе 2](/book-summaries/engineering/learning-spark/02-getting-started/) мы запускали первые программы и видели `transformation` и `action`. Теперь глава объясняет, откуда в Spark взялась структура и что она даёт. Темы главы: устройство `RDD` и его слабые места, API `DataFrame` (схемы, колонки, типичные операции), API `Dataset`, выбор между ними и движок Spark SQL с `Catalyst` и Tungsten.

![Схема: в RDD Spark видит только непрозрачный код, а в DataFrame видит намерение и строит план](/assets/learning-spark/ch03-opaque-vs-structured.png)

Сверху `RDD`: Spark не знает, что делают `lambda`, поэтому плана нет. Снизу `DataFrame`: операторы показывают намерение, и `Catalyst` может улучшить план.

## Что внутри RDD

`RDD` (`Resilient Distributed Dataset`) — самая простая абстракция Spark. У него три главные части:

- список зависимостей (`dependencies`): как этот `RDD` построен из входных данных;
- набор `partition` с информацией о расположении данных (`locality`);
- функция вычисления `compute`: `Partition => Iterator[T]`.

Зависимости дают отказоустойчивость: потерянный `RDD` Spark пересоздаёт по ним (это `lineage` из главы 1). `Partition` позволяют делить работу между `executor`. Если данные лежат в HDFS, Spark отправляет `task` поближе к данным, и по сети идёт меньше байтов.

Модель простая, но у неё есть слабые места:

- Функция `compute` непрозрачна. Что бы вы ни делали, `join`, `filter` или агрегацию, Spark видит просто `lambda`.
- В Python тип `Iterator[T]` тоже непрозрачен: для Spark это обычный объект.
- Spark не может заглянуть в функцию, поэтому не понимает намерения и не оптимизирует выражение.
- Spark не знает тип `T`. Он не видит, что вы читаете колонку определённого типа. Поэтому он просто сериализует объект в байты, без сжатия.

Из-за этого Spark не может построить эффективный план запроса. Решение авторы видят в структуре.

## Структура в Spark

В Spark 2.x структуру вводят тремя способами:

1. Вычисления выражаются типичными операциями анализа данных: фильтр, выбор колонок, подсчёт, агрегация, среднее, группировка.
2. Эти операции собраны в набор операторов `DSL`. Он доступен как API на Java, Python, Scala, R и SQL. Вы говорите Spark, что считать, а он сам строит эффективный план.
3. Данные раскладываются в таблицу, как в SQL или электронной таблице, со своими типами.

### Какую пользу даёт структура

Кроме скорости и экономии памяти, авторы выделяют четыре выгоды: выразительность, простота, композиция запросов и единообразие. Первые две показывает один пример: сгруппировать людей по имени и посчитать средний возраст. На `RDD` это цепочка `map` и `reduceByKey` с `lambda`:

```python
ages_rdd = (sc.parallelize(pairs)
            .map(lambda x: (x[0], (x[1], 1)))
            .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))
            .map(lambda x: (x[0], x[1][0] / x[1][1])))
```

Этот код трудно читать. Он говорит Spark, как считать, и скрывает намерение. К тому же на Scala такой код выглядел бы совсем иначе, чем на Python. То же самое на `DataFrame`:

```python
data_df = spark.createDataFrame(pairs, ["name", "age"])
data_df.groupBy("name").agg(avg("age")).orderBy("name").show()
```

```text
+------+--------+
|  name|avg(age)|
+------+--------+
|Brooke|    22.5|
| Denny|    31.0|
| Jules|    30.0|
|    TD|    35.0|
+------+--------+
```

Код короче: операторы `DSL` составляют весь запрос целиком. Spark разбирает его, понимает намерение (сгруппировать по имени, усреднить возраст) и оптимизирует порядок операций.

Кто-то скажет, что высокоуровневые операторы ограничивают контроль. Авторы отвечают: вы не заперты в них. В любой момент можно вернуться к `RDD`, хотя вам это почти никогда не нужно.

Единообразие видно в том, что этот же запрос на Scala почти не отличается от кода на Python. Его даёт движок Spark SQL, на котором построены все компоненты Spark. Поэтому и в Structured Streaming, и в `MLlib` вы работаете с теми же `DataFrame` и теми же операциями.

## API DataFrame

Идея `DataFrame` пришла из pandas. Это распределённая таблица в памяти с именованными колонками и схемой, где у каждой колонки свой тип: целое число, строка, массив, `map`, дата, `timestamp` и другие. Для человека он выглядит как таблица. В примере книги это шесть авторов блога с колонками `Id`, `First`, `Last`, `Url`, `Published`, `Hits` и `Campaigns` (список каналов, например `[twitter, LinkedIn]`).

Как мы знаем из главы 2, `DataFrame` неизменяем (`immutable`), а Spark помнит `lineage` всех `transformation`. Если вы меняете имя или тип колонки, получается новый `DataFrame`, а старый остаётся.

### Базовые типы данных

Типы Spark соответствуют типам языков: целые (`ByteType`, `ShortType`, `IntegerType`, `LongType`), `FloatType`, `DoubleType`, `StringType`, `BooleanType` и `DecimalType`. В Python это `int`, `float`, `str`, `bool` и `decimal.Decimal`.

Для сложной аналитики есть составные типы: `BinaryType`, `TimestampType`, `DateType`, `ArrayType`, `MapType`, `StructType` и `StructField`. Важнее таблицы типов то, как они собираются в схему.

### Схемы и создание DataFrame

Схема (`schema`) описывает имена колонок и их типы. Чаще всего она нужна при чтении данных из внешнего источника. Явная схема лучше, чем вывод схемы (`schema inference`, то есть `schema on read`), по трём причинам:

- Spark не тратит силы на угадывание типов.
- Spark не запускает отдельный `job`, чтобы прочитать большую часть файла и определить схему. Для большого файла это дорого и долго.
- Ошибки видны рано: если данные не подходят под схему, это обнаружится сразу.

Авторы советуют всегда задавать схему заранее, когда вы читаете большой файл.

Схему можно описать двумя способами. Первый — программно, через `StructType` и `StructField`. Второй — строкой `DDL`, она проще и читается легче:

```python
schema = "Id INT, First STRING, Last STRING, Hits INT, Campaigns ARRAY<STRING>"
```

Выбирайте любой. Передадим строку `DDL` в `createDataFrame` и вызовем `printSchema()`:

```text
root
 |-- Id: integer (nullable = true)
 |-- First: string (nullable = true)
 |-- Last: string (nullable = true)
 |-- Hits: integer (nullable = true)
 |-- Campaigns: array (nullable = true)
 |    |-- element: string (containsNull = true)
```

Схему можно получить обратно: `blogs_df.schema`. Чтение из JSON в Python выглядит как `spark.read.schema(schema).json(path)`.

### Колонки и выражения

Именованные колонки `DataFrame` похожи на колонки pandas, R или таблицы СУБД: они описывают поле. Колонка — это объект типа `Column` с публичными методами. Над значениями можно писать выражения, например `expr("Hits * 2")` или `expr("Hits > 10000")`: функция `expr()` из `pyspark.sql.functions` разбирает аргумент как выражение.

Документация Spark называет и `col`, и `Column`. Разница простая: `Column` — это объект, а `col()` — встроенная функция, которая его возвращает.

```python
blogs_df.select(expr("Hits * 2").alias("hits_x2")).show(2)
blogs_df.withColumn("Big Hitters", expr("Hits > 10000")).select("Id", "Hits", "Big Hitters").show()
```

```text
+-------+
|hits_x2|
+-------+
|   9070|
|  17816|
+-------+
only showing top 2 rows
+---+-----+-----------+
| Id| Hits|Big Hitters|
+---+-----+-----------+
|  1| 4535|      false|
|  2| 8908|      false|
|  3| 7659|      false|
|  4|10568|       true|
|  5|40578|       true|
|  6|25568|       true|
+---+-----+-----------+
```

Ещё приёмы: `concat` склеивает три колонки в новую (имя, фамилия и номер дают `JulesDamji1`), записи `expr("Hits")`, `col("Hits")` и `"Hits"` равнозначны, а `sort(col("Id").desc())` сортирует по убыванию.

### Row

Колонки не живут сами по себе: каждая входит в строку, а все строки вместе и есть `DataFrame`. В Scala `DataFrame` — это `Dataset[Row]`. Строка (`Row`) — универсальный объект Spark: упорядоченный набор полей. Поля могут быть разных типов. Его можно создать в любом языке и читать поле по индексу с нуля:

```python
row = Row(6, "Reynold", "Xin")
print("row[1] =", row[1])
```

```text
row[1] = Reynold
```

Из списка `Row` можно быстро собрать `DataFrame` для проверки. На практике данные читают из больших файлов со схемой.

### Типичные операции

#### DataFrameReader и DataFrameWriter

Чтение и запись просты. `DataFrameReader` читает данные в `DataFrame` из JSON, CSV, Parquet, Text, Avro, ORC и других форматов, а также из NoSQL, СУБД и потоковых систем вроде Kafka и Kinesis. `DataFrameWriter` пишет обратно.

Книга берёт большой CSV с вызовами пожарной службы Сан-Франциско: около 4,38 млн записей и 28 колонок. Схему лучше задать. Если задавать схему не хочется, Spark выведет её по выборке: опция `samplingRatio` (например `0.001`) дешевле полного чтения.

В нашем коде данные генерируются: 200 вызовов с фиксированным `seed`. Схема задана заранее, а CSV читается так:

```python
fire_df = spark.read.csv(src, header=True, schema=fire_schema)
```

Запись по умолчанию идёт в Parquet: колоночный формат со сжатием `snappy`. Схема сохраняется в метаданных Parquet, поэтому при чтении её вручную задавать не нужно. Результат можно сохранить и как таблицу: `saveAsTable` регистрирует метаданные в Hive metastore. Таблицы Spark (`managed table` и `unmanaged table`) разбираются в [главе 4](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/).

#### Projections и filters

`Projection` — выбор только нужных колонок. В Spark её делает `select()`. Фильтрует `filter()` или `where()`. Так мы оставляем все вызовы, кроме медицинских:

```python
(fire_df.select("CallNumber", "CallType").where(col("CallType") != "Medical Incident")
 .orderBy("CallNumber").show(3))
```

```text
+----------+-----------------+
|CallNumber|         CallType|
+----------+-----------------+
|      1000|           Alarms|
|      1001|Traffic Collision|
|      1002|   Structure Fire|
+----------+-----------------+
only showing top 3 rows
```

Сколько разных типов вызовов? В книге получилось 32. В нашем маленьком наборе их 5:

```python
(fire_df.select("CallType").where(col("CallType").isNotNull())
 .agg(F.countDistinct("CallType").alias("DistinctCallTypes")).show())
```

```text
+-----------------+
|DistinctCallTypes|
+-----------------+
|                5|
+-----------------+
```

#### Переименование, добавление и удаление колонок

В исходных данных у колонок были пробелы (`Incident Number`). Пробелы в именах мешают, особенно при записи в Parquet: он их не принимает. Мы задали новые имена без пробелов в схеме через `StructField`, поэтому при чтении они поменялись все сразу. Отдельную колонку переименовывает `withColumnRenamed()`. Книга меняет `Delay` на `ResponseDelayedinMins` и смотрит задержки больше пяти минут. Новый `DataFrame` не стирает старый: он остаётся с прежним именем.

Часто нужно менять и содержимое или тип колонки. В данных книги `CallDate`, `WatchDate` и `AvailableDtTm` — строки, а не `timestamp`, и по ним неудобно считать по датам. Функции `to_timestamp()` и `to_date()` из `spark.sql.functions` решают задачу:

```python
ts_df = (new_df
         .withColumn("IncidentDate", to_timestamp(col("CallDate"), "MM/dd/yyyy"))
         .drop("CallDate")
         .withColumn("AvailableDtTS", to_timestamp(col("AvailableDtTm"), "MM/dd/yyyy hh:mm:ss a"))
         .drop("AvailableDtTm"))
ts_df.select("CallNumber", "IncidentDate", "AvailableDtTS").orderBy("CallNumber").show(3, False)
```

```text
+----------+-------------------+-------------------+
|CallNumber|IncidentDate       |AvailableDtTS      |
+----------+-------------------+-------------------+
|1000      |2018-02-01 00:00:00|2018-02-01 16:14:00|
|1001      |2018-09-03 00:00:00|2018-09-03 13:01:00|
|1002      |2018-01-18 00:00:00|2018-01-18 12:41:00|
+----------+-------------------+-------------------+
only showing top 3 rows
```

Запрос превращает строку в `timestamp` по заданному формату, добавляет новую колонку через `withColumn()`, удаляет старую через `drop()` и кладёт результат в новый `DataFrame`.

> **Пояснение:** в Spark 4 включён ANSI-режим. Если строка не подходит под формат, `to_timestamp` теперь падает с ошибкой, а не возвращает `NULL`. Для мягкого разбора есть `try_to_timestamp`.

После этого работают `year()`, `month()` и `day()`. Например, `year("IncidentDate")` с `distinct()` покажет, сколько лет данных в таблице (в нашем примере 2016, 2017 и 2018). Остаётся группировка и подсчёт.

#### Агрегации

Вопросы вроде «какие вызовы самые частые» или «из каких районов звонят чаще всего» решают `groupBy()`, `orderBy()` и `count()`. Для большого `DataFrame`, к которому часто обращаются, помогает кэш (`cache`): о нём в следующих главах.

```python
(ts_df.where(col("CallType").isNotNull()).groupBy("CallType").count()
 .orderBy(col("count").desc(), "CallType").show(truncate=False))
```

```text
+-----------------+-----+
|CallType         |count|
+-----------------+-----+
|Medical Incident |54   |
|Alarms           |50   |
|Traffic Collision|25   |
|Outside Fire     |22   |
|Structure Fire   |20   |
+-----------------+-----+
```

В данных книги самый частый тип тоже `Medical Incident`.

> **Предупреждение:** метод `collect()` возвращает все `Row` на `driver`. Для очень большого `DataFrame` это дорого и опасно: можно получить `OOM` (нехватку памяти). В отличие от `count()`, который возвращает одно число, `collect()` забирает всё. Чтобы посмотреть записи, берите `take(n)`.

#### Другие операции

Есть и описательные статистики: `min()`, `max()`, `sum()`, `avg()`. Модуль функций импортируют как `F`, чтобы не конфликтовать со встроенными функциями Python:

```python
ts_df.select(F.sum("NumAlarms").alias("alarms"),
             F.round(F.avg("ResponseDelayedinMins"), 2).alias("avg_delay"),
             F.min("ResponseDelayedinMins").alias("min_delay"),
             F.max("ResponseDelayedinMins").alias("max_delay")).show()
```

```text
+------+---------+---------+---------+
|alarms|avg_delay|min_delay|max_delay|
+------+---------+---------+---------+
|   390|     6.13|      1.0|     12.0|
+------+---------+---------+---------+
```

В данных книги сумма тревог равна 4 403 441, средняя задержка около 3,9 минуты, минимум 0,017, максимум 1 879,6. Для продвинутой статистики есть `describe()`, `approxQuantile()` и другие методы.

#### Сквозной пример

В репозитории книги есть ноутбуки на Python и Scala с полным разбором тех же данных. Они отвечают на вопросы про 2018 год: какие были типы вызовов, в какие месяцы и в каких районах вызовов больше всего, где хуже всего время реакции. Основные шаги мы повторили выше.

## API Dataset

В Spark 2.0 API `DataFrame` и `Dataset` объединили в Structured API с похожим интерфейсом, чтобы разработчик учил один набор API. У `Dataset` два вида API: типизированный и нетипизированный.

![Схема: DataFrame и Dataset стоят над Spark SQL и RDD; в Python и R есть только DataFrame](/assets/learning-spark/ch03-structured-apis.png)

В Scala `DataFrame` — это псевдоним (`alias`) для `Dataset[Row]`, где `Row` — универсальный нетипизированный JVM-объект. Сам `Dataset` — коллекция строго типизированных JVM-объектов (класс Scala или Java). В документации сказано так: `Dataset` — строго типизированная коллекция объектов предметной области, которую можно параллельно преобразовывать функциями или реляционными операциями.

### Типизированные и нетипизированные объекты

`Dataset` есть только в Java и Scala. В Python и R есть только `DataFrame`, потому что эти языки не проверяют типы при компиляции: типы определяются во время выполнения. В Scala и Java типы привязаны к переменным и объектам уже при компиляции.

| Язык | Основная абстракция | Типы |
|---|---|---|
| Scala | `Dataset[T]` и `DataFrame` (псевдоним `Dataset[Row]`) | и типизированный, и нетипизированный |
| Java | `Dataset<T>` | типизированный |
| Python | `DataFrame` | нетипизированный `Row` |
| R | `DataFrame` | нетипизированный `Row` |

`Row` хранит набор значений разных типов, к ним обращаются по индексу. Внутри Spark превращает их в типы вроде `IntegerType`. Например, поле `Int` в `Row` становится `IntegerType`. В Python `row[0]` вернёт `350`, а в Scala есть геттеры `getInt(0)`, `getBoolean(1)`, `getString(2)`. Типизированные объекты — это настоящие объекты Java или Scala в JVM: каждый элемент `Dataset` соответствует объекту.

### Создание Dataset

Как и для `DataFrame`, при создании `Dataset` надо знать схему, то есть типы. Вывод схемы по JSON или CSV возможен, но на больших данных дорог. В Scala схему проще всего задать через `case class`, в Java используют JavaBean (подробности в [главе 6](/book-summaries/engineering/learning-spark/06-sql-and-datasets/)).

Пример книги: показания IoT-устройств в JSON с полями `device_id`, `temp`, `humidity`, `battery_level`, `c02_level`, `cn` (страна) и другими. Для них объявляют `case class DeviceIoTData`, а затем превращают `Dataset[Row]` в `Dataset[DeviceIoTData]` вызовом `.as[DeviceIoTData]`. Этот код только для Scala, в Python его нет.

### Операции Dataset

Над `Dataset` те же `transformation` и `action`, что над `DataFrame`. Отличие в стиле. В `DataFrame` условия фильтра выражаются операторами `DSL`, похожими на SQL и не зависящими от языка. В `Dataset` вы передаёте функцию на языке программы: `ds.filter(d => d.temp > 30 && d.humidity > 70)`. Аргумент `lambda` — объект `DeviceIoTData`, поля берутся через точку, как в обычном классе.

Меньший `Dataset` получается через `filter`, `map` и `.as[DeviceTempByCountry]` или через `select(...).where(...).as[...]`: `select()` по смыслу похож на `map()`. Операции `filter()`, `map()`, `groupBy()`, `select()`, `take()` те же, что у `DataFrame`. Если сравнивать с `RDD`, то `Dataset` даёт похожий интерфейс и проверку типов при компиляции, но удобнее и ближе к объектно-ориентированному коду.

Создание, преобразование, сериализацию и десериализацию JVM-объектов берёт на себя движок Spark SQL. Он же управляет памятью вне кучи Java (`off-heap`) с помощью `encoder`: об этом подробнее в главе 6.

Сквозной пример книги на вымышленных IoT-данных повторяет анализ из примера с пожарной службой. Он ищет устройства с низким зарядом батареи и страны с высоким CO2, считает минимумы и максимумы, группирует по средним значениям.

## DataFrame или Dataset: что выбрать

Часто подойдёт любой API, но иногда один лучше. Правила книги:

- Хотите сказать Spark, что делать, а не как? Берите `DataFrame` или `Dataset`.
- Нужна богатая семантика, высокоуровневые абстракции и операторы `DSL`? `DataFrame` или `Dataset`.
- Нужна строгая проверка типов при компиляции и вас не пугает множество `case class`? Берите `Dataset`.
- Нужны SQL-подобные реляционные преобразования? `DataFrame`.
- Нужна эффективная сериализация Tungsten через `encoder`? `Dataset`.
- Нужны единообразие, оптимизация кода и простота API во всех компонентах? `DataFrame`.
- Вы пишете на R? `DataFrame`. На Python? `DataFrame`, а к `RDD` спускайтесь, когда нужен больший контроль.
- Нужна скорость и экономия памяти? `DataFrame`.

Когда ошибка будет найдена, зависит от API. Книга показывает это на схеме: чем строже API, тем раньше ловится ошибка.

| Ошибка | SQL | DataFrame | Dataset |
|---|---|---|---|
| Синтаксис | при выполнении | при компиляции | при компиляции |
| Анализ (неверное имя колонки) | при выполнении | при выполнении | при компиляции |

SQL узнаёт об ошибке только при запуске запроса. `DataFrame` ловит опечатку в имени метода при компиляции, но неверное имя колонки видно только при выполнении. `Dataset` проверяет и это при компиляции, потому что поля взяты из класса.

### Когда нужен RDD

`RDD` не списан. Его API поддерживается, но вся будущая работа в Spark 2.x и 3.0 идёт вокруг `DataFrame`. `RDD` стоит использовать, если вы:

- используете сторонний пакет, написанный на `RDD`;
- готовы отказаться от оптимизации кода, экономии памяти и скорости `DataFrame` и `Dataset`;
- хотите точно сказать Spark, как выполнять запрос.

Переходить между `DataFrame` и `RDD` можно вызовом `df.rdd`, но это стоит ресурсов, поэтому делайте это только при необходимости. В итоге `DataFrame` и `Dataset` построены поверх `RDD` и при whole-stage code generation превращаются в компактный код `RDD`.

## Spark SQL и движок под ним

Spark SQL принимает запросы ANSI SQL:2003 по структурированным данным со схемой. Со времён Spark 1.3 он вырос в движок, на котором построены многие функции. Помимо SQL-запросов, он:

- объединяет компоненты Spark и даёт абстракцию `DataFrame` и `Dataset` в Java, Scala, Python и R;
- подключается к Hive metastore и таблицам Hive;
- читает и пишет структурированные форматы (JSON, CSV, Text, Avro, Parquet, ORC) и превращает данные во временные таблицы;
- даёт интерактивную оболочку Spark SQL для быстрой разведки;
- служит мостом к внешним инструментам через `JDBC/ODBC`;
- строит оптимизированные планы и компактный код для JVM.

Ядро движка составляют оптимизатор `Catalyst` и проект Tungsten. Вместе они поддерживают `DataFrame`, `Dataset` и SQL. О Tungsten подробнее в главе 6, а пока посмотрим на оптимизатор.

### Оптимизатор Catalyst

`Catalyst` превращает запрос в план выполнения за четыре фазы. Запросы на Python и на SQL проходят одинаковый путь и дают почти одинаковый байт-код. Пример книги: группировка M&M из главы 2.

![Схема: запрос проходит Analysis, Logical optimization, Physical planning и Code generation, затем выполняется на executors](/assets/learning-spark/ch03-catalyst-phases.png)

Слева направо идёт путь запроса. Снизу к фазе Analysis подключён `Catalog`, он нужен для проверки имён.

Увидеть фазы можно методом `explain(True)` у `DataFrame`. В Scala есть ещё `df.queryExecution.logical` и `df.queryExecution.optimizedPlan`. Мы запустили `explain("extended")` для запроса по маленькой таблице цветов M&M. `DataFrame` и SQL дали один физический план (номера вроде `#0` при сравнении убираем). Вывод сокращён:

```text
== Parsed Logical Plan ==
'Sort ['Total DESC NULLS LAST], true
+- Aggregate [State#0, Color#1], [State#0, Color#1, sum(Count#2L) AS Total#3L]
   +- Project [State#0, Color#1, Count#2L]
      +- LogicalRDD [State#0, Color#1, Count#2L], false
...
== Optimized Logical Plan ==
Sort [Total#3L DESC NULLS LAST], true
+- Aggregate [State#0, Color#1], [State#0, Color#1, sum(Count#2L) AS Total#3L]
   +- LogicalRDD [State#0, Color#1, Count#2L], false
...
same physical plan: True
```

В оптимизированном плане лишний `Project` исчез, потому что колонки и так те же. Читать планы авторы учат в главе 7.

Второй пример книги: `join` двух таблиц (`users` и `events`) с фильтром по дате после соединения. После анализа `Catalyst` перестраивает дерево операторов так, как на схеме ниже: фильтр сдвигается под `join`, и соединение получает меньше строк. Это `predicate pushdown`.

![Схема: до оптимизации фильтр стоит после join, после оптимизации Catalyst переносит его до join](/assets/learning-spark/ch03-pushdown.png)

Мы проверили это на маленьких данных. В физическом плане `Filter` уже стоит перед `Exchange` и `join` (так `explain()` показывает порядок: нижние операторы выполняются первыми):

```text
+- *(3) Filter ((isnotnull(date#33) AND (date#33 > 2015-01-01)) AND isnotnull(uid#32L))
   +- *(3) Scan ExistingRDD[uid#32L,date#33]
```

#### Фаза 1: Analysis

Spark SQL строит абстрактное синтаксическое дерево (`AST`) для SQL- или `DataFrame`-запроса. Имена колонок и таблиц разрешаются через внутренний `Catalog`. Это программный интерфейс со списком имён колонок, типов данных, функций, таблиц и баз. Когда все имена найдены, запрос идёт дальше.

#### Фаза 2: Logical optimization

Фаза идёт в два шага. Сначала по правилам `Catalyst` строит несколько планов-деревьев. Затем оптимизатор на основе стоимости (`CBO`) назначает каждому цену. Правила — например, свёртка констант (`constant folding`), `predicate pushdown`, отсечение лишних колонок (`projection pruning`) и упрощение логических выражений. Логический план становится входом для физического.

#### Фаза 3: Physical planning

Для выбранного логического плана Spark SQL строит оптимальный физический план из физических операторов, которые есть в движке выполнения Spark.

#### Фаза 4: Code generation

Последняя фаза создаёт эффективный байт-код Java для каждой машины. Так как данные лежат в памяти, Spark SQL может генерировать код методами компиляторов, то есть ведёт себя как компилятор. Здесь работает Tungsten с whole-stage code generation. Это физическая оптимизация, которая сворачивает весь запрос в одну функцию: убирает вызовы виртуальных функций и держит промежуточные данные в регистрах процессора. Tungsten второго поколения (Spark 2.0) генерирует компактный код `RDD`, что заметно повышает эффективность CPU.


## Итоги главы

- Структура (операторы `DSL`, таблица, типы) позволяет Spark понять намерение и построить эффективный план запроса.
- В `RDD` функция `compute` и тип данных непрозрачны, поэтому Spark не может оптимизировать код и сжимать данные.
- `DataFrame` — это распределённая неизменяемая таблица с именованными колонками и схемой, а в Scala он совпадает с `Dataset[Row]`.
- Схему лучше задавать заранее (программно или строкой `DDL`): так Spark не угадывает типы, не читает файл дважды и рано находит ошибки.
- `DataFrameReader` и `DataFrameWriter` читают и пишут много форматов, а Parquet по умолчанию хранит схему вместе с данными.
- Типичные операции: `select` и `where`, `withColumnRenamed`, `withColumn` и `drop`, `groupBy` с агрегациями. `collect()` на большом `DataFrame` может вызвать `OOM`.
- `Dataset` типизирован и есть только в Scala и Java, а в Python и R работают с `DataFrame`. `RDD` не устарел, но нужен реже.
- `Catalyst` проходит четыре фазы (`Analysis`, `Logical optimization`, `Physical planning`, `Code generation`), а Tungsten собирает код всего `stage` в одну функцию.
- Запрос на любом языке Spark проходит один путь оптимизации и даёт почти одинаковый байт-код.

## Ключевые термины

| Термин | Значение |
|---|---|
| `RDD` | Базовая абстракция Spark: зависимости, `partition` и функция `compute`; для Spark непрозрачна |
| `DataFrame` | Распределённая таблица с именованными колонками и схемой |
| `Dataset` | Типизированная коллекция объектов в Scala и Java |
| `DSL` | Операторы `select`, `filter`, `groupBy`, которые говорят, что считать |
| схема (`schema`) | Имена колонок и их типы; задаётся программно или строкой `DDL` |
| `schema inference` (вывод схемы) | Spark сам читает данные и угадывает типы: дорого и ненадёжно |
| `Row` | Общий объект строки: упорядоченный набор полей разных типов |
| `Column` | Объект колонки; `col("x")` возвращает его |
| `projection` | Выбор нужных колонок через `select()` |
| Parquet | Колоночный формат по умолчанию; хранит схему в метаданных |
| `Catalyst` | Оптимизатор Spark SQL с четырьмя фазами |
| `Catalog` | Внутренний список таблиц, колонок, типов и функций |
| `predicate pushdown` | Фильтр ближе к источнику: читаем и соединяем меньше данных |
| Tungsten | Физический движок: `whole-stage code generation` и работа с памятью |

## Что это значит на практике

- Всегда задавайте схему при чтении больших файлов: так нет лишнего `job` для вывода типов, а ошибки данных видны сразу.
- Пишите `pipeline` на `DataFrame` или SQL, а не на `RDD`: только их `Catalyst` может оптимизировать.
- Строки с датами сразу превращайте в `timestamp` через `to_timestamp` с явным форматом. В Spark 4 неверный формат даст ошибку.
- Не вызывайте `collect()` на больших данных: для просмотра берите `show()`, `take(n)` или `limit`.
- Читайте план через `explain()`: проверьте, что фильтр стоит до `join` и колонки лишние отброшены.
- В Python `Dataset` нет, поэтому типы в `DataFrame` проверяйте схемой и тестами на данных.

## Практика

Три скрипта главы запускаются в Docker с Spark 4.3.0. Данные генерируются в коде, вывод выше настоящий.

- [ch03_schema_columns.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch03_schema_columns.py): схема, колонки, `Row`;
- [ch03_fire_calls.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch03_fire_calls.py): CSV, фильтры, даты, агрегации, Parquet;
- [ch03_catalyst.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch03_catalyst.py): `explain()` и `predicate pushdown`.

Запуск и установку см. в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. DuckDB заменяет здесь Spark SQL: те же идеи (проекция, фильтр, группировка, даты как строки) на маленьких таблицах.

### Шаг 1. Создаём данные

```sql
CREATE TABLE blogs AS SELECT * FROM (VALUES
    (1, 'Jules',     'Damji',   4535,  ['twitter', 'LinkedIn']),
    (2, 'Brooke',    'Wenig',   8908,  ['twitter', 'LinkedIn']),
    (3, 'Denny',     'Lee',     7659,  ['web', 'twitter', 'FB', 'LinkedIn']),
    (4, 'Tathagata', 'Das',     10568, ['twitter', 'FB']),
    (5, 'Matei',     'Zaharia', 40578, ['web', 'twitter', 'FB', 'LinkedIn']),
    (6, 'Reynold',   'Xin',     25568, ['twitter', 'LinkedIn'])
) t(id, first, last, hits, campaigns);

CREATE TABLE calls AS
SELECT
    i AS call_number,
    ['Medical Incident', 'Medical Incident', 'Structure Fire', 'Alarms', 'Traffic Collision'][1 + i % 5] AS call_type,
    strftime(DATE '2018-01-01' + INTERVAL (i * 17 % 400) DAY, '%m/%d/%Y') AS call_date,
    round(1 + (i * 37 % 100) / 10.0, 1) AS delay_min
FROM generate_series(1, 60) t(i);
```

### Шаг 2. Проверяем

Должно быть 6 и 60 строк.

```sql
SELECT (SELECT count(*) FROM blogs) AS blogs, (SELECT count(*) FROM calls) AS calls;
```

### Задания

**1. Новая колонка.** Покажите `id`, `first`, `hits` и колонку `big_hitter` (`hits` больше 10000). Отсортируйте по `id` по убыванию.

<details><summary>Решение</summary>

```sql
SELECT id, first, hits, hits > 10000 AS big_hitter FROM blogs ORDER BY id DESC;
```

```text
id  first      hits   big_hitter
6   Reynold    25568  true
5   Matei      40578  true
4   Tathagata  10568  true
3   Denny      7659   false
2   Brooke     8908   false
1   Jules      4535   false
```

Это `withColumn("Big Hitters", expr("Hits > 10000"))` из главы.

</details>

**2. Группировка.** Посчитайте вызовы каждого типа. Сначала самые частые, при равенстве по имени типа.

<details><summary>Решение</summary>

```sql
SELECT call_type, count(*) AS cnt FROM calls GROUP BY call_type ORDER BY cnt DESC, call_type;
```

```text
call_type          cnt
Medical Incident   24
Alarms             12
Structure Fire     12
Traffic Collision  12
```

Типов вызовов четыре, медицинских вдвое больше остальных.

</details>

**3. Даты из строк.** Даты лежат строками `MM/dd/yyyy`. Разберите их и посчитайте вызовы по годам.

<details><summary>Решение</summary>

```sql
SELECT year(strptime(call_date, '%m/%d/%Y')) AS yr, count(*) AS cnt
FROM calls GROUP BY yr ORDER BY yr;
```

```text
yr    cnt
2018  55
2019  5
```

`strptime` играет роль `to_timestamp`: строка превращается в дату, и из неё можно взять год. Пять вызовов попали в 2019 год, потому что генератор сдвигает дату до 400 дней.

</details>

## Вопросы для самопроверки

1. Почему Spark не может оптимизировать код на `RDD`, но может оптимизировать код на `DataFrame`?
2. Почему схему лучше задавать заранее, а не выводить из данных? Назовите три причины.
3. Чем `Dataset` отличается от `DataFrame` и почему в Python есть только `DataFrame`?
4. Когда ошибка в имени колонки обнаружится при компиляции, а когда при выполнении? От чего это зависит?
5. Когда стоит вернуться к `RDD` и что за это придётся заплатить?
6. Назовите четыре фазы `Catalyst`. Что происходит с фильтром в примере с `join` и зачем?

Предыдущая: [Установка Spark и первые шаги](/book-summaries/engineering/learning-spark/02-getting-started/). Следующая: [Spark SQL и DataFrame: встроенные источники данных](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/).
