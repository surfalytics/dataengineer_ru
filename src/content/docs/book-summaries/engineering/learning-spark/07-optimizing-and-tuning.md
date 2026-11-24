---
title: "Learning Spark, глава 7: Оптимизация и настройка приложений Spark"
head:
  - tag: title
    content: "Как настроить и ускорить Spark: память, join, кэш | Инжиниринг Данных"
description: "Конспект главы 7 Learning Spark на русском. Конфигурации Spark, память executor, partition, кэш и persist, broadcast и sort merge join, bucketing, Spark UI."
sidebar:
  order: 7
  label: "7. Оптимизация и настройка приложений Spark"
tags:
  - books
  - spark
---

**Главная мысль:** быстрый Spark — это правильно выбранные настройки, достаточное число `partition`, разумный кэш и join без лишнего `shuffle`. Увидеть, что пошло не так, помогает Spark UI.

## О чём глава

В [прошлой главе](/book-summaries/engineering/learning-spark/06-sql-and-datasets/) мы узнали, как Spark хранит `Dataset` в памяти и сколько это стоит. Теперь вопрос шире: как заставить приложение работать эффективно. Автор берёт самые важные настройки из сотен. Темы: порядок приоритета настроек, настройки для больших нагрузок (`dynamic allocation`, память `executor`, `shuffle`, `partition`), кэш и `persist`, две главные стратегии join и `bucketing`, вкладки Spark UI.

![Схема: настройки Spark берутся из spark-defaults.conf, spark-submit и кода, побеждает самый сильный уровень](/assets/learning-spark/ch07-config-order.png)

Схема читается слева направо: каждый следующий уровень перекрывает предыдущий.

## Настройка Spark

### Как читать и менять настройки

Настройки Spark задают тремя способами:

1. **Файлы в `$SPARK_HOME/conf`.** Если убрать суффикс `.template` у `spark-defaults.conf.template`, `log4j.properties.template` или `spark-env.sh.template`, Spark применит их значения. Это действует на весь кластер.
2. **Параметры `spark-submit`.** Флаг `--conf` задаёт настройки одного приложения, например `--conf spark.sql.shuffle.partitions=5`.
3. **Код приложения.** Через `SparkSession.builder.config(...)` или `spark.conf.set(...)`.

Если одна настройка задана в нескольких местах, побеждает самый сильный уровень. Сначала Spark читает `spark-defaults.conf`, потом `spark-submit`, потом код. Значение из кода перекрывает остальные, значение из командной строки перекрывает файл.

Прочитать текущие значения можно через `spark.conf.getAll`, запрос `SET -v` (только настройки Spark SQL) или вкладку Environment в Spark UI (только чтение). Менять настройку на лету можно не всегда, поэтому проверьте её методом `spark.conf.isModifiable("<имя>")`.

```python
spark = (SparkSession.builder.master("local[2]")
         .config("spark.sql.shuffle.partitions", 5)
         .config("spark.executor.memory", "2g")
         .getOrCreate())
print("shuffle.partitions:", spark.conf.get("spark.sql.shuffle.partitions"))
for key in ["spark.sql.shuffle.partitions", "spark.executor.memory"]:
    print("isModifiable", key, "->", spark.conf.isModifiable(key))
spark.conf.set("spark.sql.shuffle.partitions", 3)
print("после set:", spark.conf.get("spark.sql.shuffle.partitions"))
print("autoBroadcastJoinThreshold:", spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
print("adaptive.enabled:", spark.conf.get("spark.sql.adaptive.enabled"))
```

```text
shuffle.partitions: 5
isModifiable spark.sql.shuffle.partitions -> True
isModifiable spark.executor.memory -> False
после set: 3
autoBroadcastJoinThreshold: 10485760b
adaptive.enabled: true
```

Память `executor` после старта не поменять, а число `shuffle`-`partition` можно.

### Масштабирование для больших нагрузок

Большие нагрузки — это чаще всего batch-задачи на десятки терабайт. Чтобы они не падали, настраивают три компонента: `driver`, `executor` и `shuffle service`. Часть советов взята у компаний вроде Facebook, где Spark обрабатывает терабайты данных.

#### Статическое и динамическое выделение ресурсов

Если задать ресурсы в `spark-submit`, вы ставите потолок. Когда задач станет больше, чем ждали, и они встанут в очередь у `driver`, Spark не сможет взять ещё ресурсов. Режим `dynamic allocation` снимает это ограничение: `driver` сам просит у кластера больше или меньше ресурсов вслед за нагрузкой.

Он полезен там, где нагрузка скачет: в потоках, в интерактивной аналитике с пиками запросов и в общих кластерах (YARN, Mesos, Kubernetes). Но в общем кластере Spark то берёт, то отдаёт ресурсы, и это может мешать соседним приложениям, которым ресурсы нужны в то же время.

```text
spark.dynamicAllocation.enabled true
spark.dynamicAllocation.minExecutors 2
spark.dynamicAllocation.schedulerBacklogTimeout 1m
spark.dynamicAllocation.maxExecutors 20
spark.dynamicAllocation.executorIdleTimeout 2min
```

По умолчанию режим выключен. С этими числами (они для примера) `driver` стартует с двумя `executor`. Если задачи ждут в очереди дольше минуты, он просит ещё один `executor`, до двадцати. Простаивающий две минуты `executor` он останавливает.

#### Память executor и shuffle service

Одного `dynamic allocation` мало: нужно понимать, как `executor` делит память, иначе ему не хватит памяти или его затормозит сборка мусора (`garbage collection`, GC) в JVM. Память задаёт `spark.executor.memory`, и она делится на три части:

![Схема: память executor делится на reserved memory, execution memory и storage memory](/assets/learning-spark/ch07-memory.png)

`Execution` и `storage` могут занимать память друг у друга, а `reserved` остаётся отдельно.

- **Reserved memory:** 300 МБ в запас против ошибок нехватки памяти (OOM).
- **Execution memory:** для `shuffle`, join, сортировок и агрегаций.
- **Storage memory:** для кэша данных и `partition`, полученных из `DataFrame`.

По описанию книги, остаток после 300 МБ делится так: 60% на `execution` и 40% на `storage`. Когда одна часть не занята, Spark отдаёт её другой. Долю задаёт `spark.memory.fraction` (по умолчанию 0,6): подобрать её трудно, зато менять легко.

> **Пояснение:** в документации Spark схема точнее. Под `execution` и `storage` вместе отдают долю `spark.memory.fraction` (0,6) от памяти без 300 МБ. Внутри неё `storage` защищён долей `spark.memory.storageFraction` (0,5), которую `execution` не может отнять.

Во время `map` и `shuffle` Spark пишет файлы `shuffle` на локальный диск и читает их, поэтому ввод-вывод огромный. Настройки по умолчанию для больших задач не подходят. Советы книги дают буферам больше места:

| Настройка | По умолчанию и совет |
|---|---|
| `spark.driver.memory` | 1 ГБ. Увеличивайте, только если `driver` получает много данных (например, из `collect()`) или упирается в память |
| `spark.shuffle.file.buffer` | 32 КБ, советуют 1 МБ: больше буферизации перед записью результатов `map` на диск |
| `spark.file.transferTo` | `true`. Значение `false` заставит Spark передавать файлы через буфер перед записью на диск, и ввода-вывода станет меньше |
| `spark.shuffle.unsafe.file.output.buffer` | 32 КБ. Для больших задач подходит около 1 МБ |
| `spark.io.compression.lz4.blockSize` | 32 КБ, советуют 512 КБ: файлы `shuffle` станут меньше |
| `spark.shuffle.registration.timeout` и `maxAttempts` | 5000 мс и 3 попытки. Советуют 120000 мс и 5 попыток |

Баланс находят экспериментом.

#### Параллелизм и partition

Скорость Spark держится на параллельных `task`. `Partition` — это блок подряд лежащих данных на диске, который можно читать и обрабатывать независимо от других. Spark запускает не больше одного `task` на ядро, и каждый `task` берёт свою `partition`. Поэтому `partition` — неделимая единица параллелизма.

Идеал — `partition` не меньше, чем ядер у `executor`: тогда все ядра заняты.

Откуда берутся `partition`:

- **Из чтения файлов.** Блоки в HDFS и S3 обычно по 128 МБ. Размер `partition` задаёт `spark.sql.files.maxPartitionBytes`, по умолчанию 128 МБ. Если уменьшить его, получится `small file problem`: множество мелких файлов, а с ними лишние операции открытия, закрытия и листинга каталогов, которые на распределённой файловой системе медленные.
- **Из явных вызовов.** Например, `repartition(16)` создаёт 16 `partition` при чтении файла или создании большого `DataFrame`.
- **Из `shuffle`.** Их число задаёт `spark.sql.shuffle.partitions`, по умолчанию 200. Такие `partition` создают широкие преобразования (`wide transformation`), например `groupBy()` и `join()`. Они нагружают сеть и диск: результаты `shuffle` пишутся в `spark.local.directory`, и быстрые SSD там ускорят работу.

Для небольших и потоковых нагрузок 200 слишком много: автор советует снизить значение до числа ядер на `executor` или меньше. Точной формулы нет, число подбирают пробами.

## Кэш и persist

В Spark кэш и `persist` означают одно и то же, но методы дают разный контроль. `cache()` кладёт столько `partition` в память `executor`, сколько влезет. `DataFrame` может быть закэширован частично, а `partition` нет: если из 8 `partition` в память помещаются 4,5, закэшируются только 4. Остальные придётся пересчитывать при каждом обращении, и это замедлит задачу.

В примере книги `DataFrame` на 10 млн строк: первый `count()` заполнил кэш за 5,11 с, второй прочитал его за 0,44 с, почти в 12 раз быстрее. Но кэш готов полностью только после `action`, который проходит по всем строкам, вроде `count()`. После `take(1)` в кэше окажется одна `partition`, потому что Catalyst понимает, что остальные не нужны.

`persist(StorageLevel.LEVEL)` даёт выбор уровня хранения. Данные на диске всегда сериализованы.

| Уровень | Что делает |
|---|---|
| `MEMORY_ONLY` | Объекты только в памяти |
| `MEMORY_ONLY_SER` | Компактные байты в памяти. Чтобы читать, нужна десериализация |
| `MEMORY_AND_DISK` | Объекты в памяти, что не влезло, сериализуется на диск |
| `DISK_ONLY` | Сериализованные данные на диске |
| `OFF_HEAP` | Память вне кучи JVM |
| `MEMORY_AND_DISK_SER` | Как `MEMORY_AND_DISK`, но в памяти данные сериализованы |

У каждого уровня, кроме `OFF_HEAP`, есть вариант с `_2`, например `MEMORY_ONLY_2`: две копии на двух `executor`. Это дорого, но даёт отказоустойчивость и позволяет Spark запустить `task` рядом с одной из копий.

Кэшируют и таблицы или представления командой `CACHE TABLE`: тогда у кэша появляется понятное имя в Spark UI. Снять кэш можно вызовом `unpersist()`.

```python
df = spark.range(1_000_000).toDF("id").withColumn("square", col("id") * col("id"))
df.cache()                           # ленивый: данных в памяти ещё нет
print("count (кладёт в кэш):", df.count())
print("уровень по умолчанию:", df.storageLevel)
df.unpersist()
df.persist(StorageLevel.DISK_ONLY)
print("DISK_ONLY:", df.storageLevel)
```

```text
count (кладёт в кэш): 1000000
уровень по умолчанию: Disk Memory Deserialized 1x Replicated
DISK_ONLY: Disk Serialized 1x Replicated
```

### Когда кэшировать

Кэш помогает, когда большой набор данных читают снова и снова:

- `DataFrame` в итеративном обучении моделей;
- `DataFrame`, к которым часто обращаются в ETL или в `pipeline`.

Кэш не нужен, если `DataFrame` слишком велик для памяти или преобразование дешёвое и редкое. Правило автора: используйте кэш осторожно, потому что сериализация и десериализация тоже стоят ресурсов.

## Семейство join в Spark

Join сливает две таблицы по общему ключу. Spark поддерживает привычные виды: inner, outer, left, right. Все они двигают много данных между `executor`. Такое движение, которое запускают `groupBy()`, `join()`, `agg()` и `sortBy()`, называют `shuffle`.

Стратегий join пять: `broadcast hash join` (BHJ), `shuffle hash join`, `shuffle sort merge join` (SMJ), `broadcast nested loop join` и декартово произведение. Книга разбирает две самые частые: BHJ и SMJ.

### Broadcast hash join

BHJ называют ещё join только на стороне `map`: соединение идёт там, где лежат данные, без обмена между узлами. Он подходит, когда одна таблица маленькая и помещается в память `driver` и `executor`, а вторая большая. `Driver` рассылает маленькую таблицу всем `executor` как `broadcast variable`, и каждый `executor` соединяет её со своей частью большой таблицы. Большого обмена нет.

![Схема: маленькая таблица рассылается всем executor, и join идёт на месте без shuffle](/assets/learning-spark/ch07-broadcast-join.png)

Большие `partition` остаются на своих `executor`, а маленькая таблица едет к ним.

По умолчанию Spark выбирает BHJ, если меньшая таблица меньше 10 МБ. Порог задаёт `spark.sql.autoBroadcastJoinThreshold`. Если памяти хватает, порог можно поднять до 100 МБ и больше. Принудить BHJ можно подсказкой `broadcast()`.

BHJ — самый простой и быстрый join Spark: `shuffle` нет, и после рассылки все данные лежат локально. Но маленькая таблица должна поместиться в память и `driver`, и `executor`. Применяйте его, когда одна таблица заметно меньше другой, нужен только equi-join (соединение по равенству ключей) и вас не пугает расход сети и риск OOM.

Значение `-1` у `spark.sql.autoBroadcastJoinThreshold` отключает BHJ, и Spark всегда выбирает SMJ. Какой join выбран, показывает физический план: `df.explain()` (режимы `simple`, `extended`, `codegen`, `cost`, `formatted`).

### Shuffle sort merge join

SMJ эффективно соединяет две большие таблицы по общему ключу, который можно сортировать и хешировать. Строки с одним ключом из обеих таблиц должны оказаться на одной `partition` одного `executor`, поэтому данные надо обменять между узлами. У алгоритма две фазы: `sort` сортирует каждую таблицу по ключу, а `merge` идёт по ключам обеих таблиц и склеивает строки с совпавшим ключом. Spark включает SMJ по умолчанию (`spark.sql.join.preferSortMergeJoin`).

В примере книги соединяют две таблицы по миллиону строк: пользователей и заказы. План показывает `SortMergeJoin`, а перед каждой стороной стоят `Sort` и `Exchange` (это и есть `shuffle`). `Exchange` дорог: `partition` ходят по сети между `executor`. Spark UI показывает эти шаги в последнем `stage`.

### Как ускорить SMJ: bucketing

Если часто соединять таблицы по одному ключу, `Exchange` можно убрать. Для этого данные заранее сортируют и раскладывают по заданному числу бакетов (`bucketing`): ключ определяет бакет. Spark тогда пропускает `Exchange` и сразу идёт к `WholeStageCodegen`. В книге обе таблицы сохраняют как `managed table` в Parquet с `bucketBy(8, ...)`.

![Схема: без bucketing перед sort merge join нужен Exchange, с bucketing его нет](/assets/learning-spark/ch07-smj-bucketing.png)

Верхняя цепочка ведёт через красный `Exchange`, нижняя без него.

В новом плане `Exchange` нет, а в Spark UI исчез его `stage`. Результат отсортирован по ключам, потому что таблицы сохранены по возрастанию.

```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
j3 = orders.join(users, orders.users_id == users.uid)
print("SMJ  :", plan(j3))
users.write.bucketBy(8, "uid").sortBy("uid").mode("overwrite").saveAsTable("users_b")
orders.write.bucketBy(8, "users_id").sortBy("users_id").mode("overwrite").saveAsTable("orders_b")
j4 = spark.table("orders_b").join(spark.table("users_b"), col("users_id") == col("uid"))
print("bucket:", plan(j4))
```

```text
SMJ  : SortMergeJoin > Sort > Exchange > Sort > Exchange
bucket: SortMergeJoin > Sort > FileScan > Sort > FileScan
```

Наша функция `plan()` печатает только имена операторов физического плана. После `bucketBy` `Exchange` исчез, а `Sort` остался: в маленьком запуске в бакете несколько файлов, и их надо досортировать.

SMJ выгоден, когда:

- ключ обеих больших таблиц можно отсортировать, а строки с одним ключом по хешу собрать в одну `partition`;
- нужен только equi-join;
- хочется избежать `Exchange` и `Sort`, чтобы не гонять большие `shuffle` по сети.

## Spark UI

Spark UI показывает память, `job`, `stage`, `task`, события, логи и метрики на уровне `driver` и отдельных `executor`. `spark-submit` запускает его сам, порт по умолчанию 4040 (на localhost в режиме local).

Основных вкладок шесть. В Spark 3.0 к ним добавилась седьмая, Structured Streaming. Что смотреть на каждой:

| Вкладка | Что показывает и на что смотреть |
|---|---|
| Jobs | `Job`, их длительность и Event Timeline (когда `executor` добавлялись и удалялись). Если `job` долгий, смотрите его `stage` |
| Stages | `Task` каждого `stage`: среднее время, GC, байты `shuffle`. Подробности ниже |
| Executors | Использование диска, памяти и ядер, время GC, объём `shuffle` по каждому `executor`. Помогает проверить расход памяти, когда данные закэшированы |
| Storage | Какие таблицы и `DataFrame` закэшированы и как распределены. Для таблицы с 8 бакетами видны 8 `partition` |
| SQL | Запросы Spark SQL, их `job`, длительность и план. Под каждым оператором (Scan, HashAggregate, Exchange) есть метрики: сколько строк прочитано, сколько байтов записано в `shuffle` |
| Environment | Только чтение: переменные среды, jars, настройки Spark, версия JVM. Сюда смотрят, когда поведение необъяснимо |

На вкладке Stages ищут три признака:

- высокий `Shuffle Read Blocked Time` при чтении с удалённых `executor` намекает на проблемы ввода-вывода;
- высокое время GC значит, что в куче слишком много объектов и `executor` не хватает памяти;
- если максимальное время `task` намного выше медианы, у вас `skew`: данные распределены по `partition` неравномерно.

Отладка через UI — это скорее расследование по следам, чем пошаговая отладка в IDE. Там же лежат логи `driver` и `executor`. Новичка объём информации сначала пугает, но чем чаще вы открываете вкладки, тем быстрее замечаете аномалии.

## Итоги главы

- Настройки Spark задают в файлах, в `spark-submit` и в коде, а при конфликте побеждает код.
- Для больших нагрузок включают `dynamic allocation`, а память `executor` и буферы `shuffle` подбирают под задачу.
- Параллелизм держится на `partition`: их не меньше, чем ядер, а 200 `shuffle`-`partition` по умолчанию подходят не всем.
- Кэш и `persist` ускоряют повторные чтения, но дорогие по памяти и не нужны для дешёвых или огромных данных.
- `Broadcast hash join` не требует `shuffle`, но маленькая таблица должна поместиться в память.
- `Sort merge join` соединяет две большие таблицы, и `bucketing` по ключу join позволяет пропустить `Exchange`.
- Spark UI подсказывает узкие места: долгие `job`, время GC, `skew` в `stage`, лишние `Exchange` в плане.

## Что изменилось к 2026 году

> Это наше дополнение, его нет в книге.

Книга написана под Spark 3.0. В Spark 4.3 многое из этой главы работает сам:

- `AQE` (`adaptive query execution`) включён по умолчанию, а в книге у него `false`. Он сам объединяет мелкие `shuffle`-`partition`, переключает `sort merge join` на `broadcast join` во время работы и делит `skew`-`partition`. Поэтому ручной подбор `spark.sql.shuffle.partitions` нужен реже.
- На Kubernetes `dynamic allocation` требует `shuffle tracking` (`spark.dynamicAllocation.shuffleTracking.enabled`), потому что внешнего `shuffle service` там нет.
- Установка Spark 4.3 описана в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

## Ключевые термины

| Термин | Значение |
|---|---|
| `dynamic allocation` | `Driver` сам просит у кластера больше или меньше `executor` |
| execution memory / storage memory | Память `executor` под `shuffle` и join / под кэш |
| `partition` | Часть данных, которую берёт один `task`. Единица параллелизма |
| `small file problem` | Много мелких файлов: лишний ввод-вывод на открытие и листинг |
| кэш (`cache`, `persist`) | Держим данные в памяти или на диске. `persist` задаёт `StorageLevel` |
| `broadcast hash join` | Маленькую таблицу рассылают на все `executor`. `Shuffle` не нужен |
| `sort merge join` | Сортируем обе таблицы по ключу и сливаем. Нужен `Exchange` |
| `Exchange` | Оператор плана: `shuffle` данных между `executor` |
| `bucketing` | Раскладка таблицы по бакетам ключа. Убирает `Exchange` в join |
| `skew` | Один `task` намного дольше остальных из-за неравных `partition` |

## Что это значит на практике

- Общие настройки держите в `spark-defaults.conf`, а детали меняйте в коде приложения.
- Для батчей с пиками включайте `dynamic allocation` и задавайте `minExecutors` и `maxExecutors`.
- Уменьшайте `spark.sql.shuffle.partitions` для небольших и потоковых задач.
- Кэшируйте только то, что читаете несколько раз и что помещается в память. После работы вызывайте `unpersist()`.
- Если одна из таблиц join меньше 10 МБ, проверьте в `explain()`, что Spark выбрал `broadcast join`.
- Для частых join двух больших таблиц по одному ключу пробуйте `bucketBy` и сравните план до и после.
- После медленной задачи открывайте Spark UI: сначала Stages (GC и `skew`), потом SQL (`Exchange`).

## Практика в PySpark

Три скрипта главы лежат в [`scripts/learning-spark-code/`](https://github.com/surfalytics/dataengineer_ru/tree/main/scripts/learning-spark-code): `ch07_config.py`, `ch07_cache.py` и `ch07_joins.py`. Запуск описан в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

```bash
scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch07_joins.py
```

Блок с `dynamic allocation` не запускается: ему нужен кластер.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. В SQL мы смоделируем `shuffle`-`partition`, `skew` и `bucketing`.

### Шаг 1. Создаём данные

В таблице заказов каждый четвёртый заказ принадлежит одному пользователю с `user_id = 7`.

```sql
CREATE TABLE users AS
SELECT i AS user_id, 'user_' || i AS login
FROM generate_series(1, 1000) t(i);

CREATE TABLE orders AS
SELECT i AS order_id,
       CASE WHEN i % 4 = 0 THEN 7 ELSE 1 + (i * 37) % 1000 END AS user_id,
       10 + i % 50 AS amount
FROM generate_series(1, 20000) t(i);
```

### Шаг 2. Проверяем

Должно быть 1000, 20000 и 0 заказов без пользователя.

```sql
SELECT (SELECT count(*) FROM users) AS users,
       (SELECT count(*) FROM orders) AS orders,
       (SELECT count(*) FROM orders
        WHERE user_id NOT IN (SELECT user_id FROM users)) AS orphans;
```

### Задания

**1. Найдите `skew`.** Разложите заказы по 8 «`shuffle`-`partition`»: номер `partition` равен `hash(user_id) % 8`. Посчитайте строки в каждой и сравните с медианой.

<details><summary>Решение</summary>

```sql
WITH p AS (
  SELECT hash(user_id) % 8 AS part, count(*) AS cnt
  FROM orders GROUP BY part)
SELECT part, cnt, round(cnt / (SELECT median(cnt) FROM p), 1) AS vs_median
FROM p ORDER BY part;
```

```text
part  cnt   vs_median
0     1780  1.0
1     1980  1.1
2     7180  3.9
3     1840  1.0
4     1900  1.0
5     1660  0.9
6     1800  1.0
7     1860  1.0
```

Одна `partition` в 3,9 раза больше медианы, и её `task` будет работать дольше всех. Виноват пользователь 7: у него 5020 заказов, у остальных около 20.

</details>

**2. Join по бакетам.** Соедините `orders` и `users` только внутри одного бакета (`hash(user_id) % 8` с обеих сторон). Сравните число строк с обычным join.

<details><summary>Решение</summary>

```sql
SELECT (SELECT count(*) FROM orders o JOIN users u USING (user_id)) AS full_join,
       (SELECT count(*) FROM orders o JOIN users u
         ON o.user_id = u.user_id
        AND hash(o.user_id) % 8 = hash(u.user_id) % 8) AS bucket_join;
```

```text
full_join  bucket_join
20000      20000
```

Результат тот же: одинаковые ключи всегда попадают в один бакет, поэтому бакеты соединяют по отдельности, без обмена данными.

</details>

**3. Влезет ли в broadcast?** Оцените размер `users` как число строк × (длина `login` + 16 байт на два числа) и посчитайте, сколько таких строк помещается в порог 10 МБ (10 485 760 байт).

<details><summary>Решение</summary>

```sql
SELECT count(*) AS user_rows,
       sum(len(login) + 16) AS bytes_est,
       round(10485760 / (sum(len(login) + 16) / count(*))) AS rows_in_10mb
FROM users;
```

```text
user_rows  bytes_est  rows_in_10mb
1000       23893      438863.0
```

Таблица занимает около 24 КБ, намного меньше порога, так что Spark выберет `broadcast join`. Оценка грубая: в памяти Spark таблица больше.

</details>

## Вопросы для самопроверки

1. Задано `spark.sql.shuffle.partitions=5` в `spark-defaults.conf`, `=10` в `spark-submit` и `=20` в коде. Какое значение сработает и почему?
2. Когда `dynamic allocation` полезен, а когда может навредить?
3. Почему `partition` должно быть не меньше, чем ядер? Чем плохо значение 200 для маленькой задачи?
4. Почему после `df.cache()` и `df.take(1)` кэш неполный? Как заполнить его целиком?
5. Чем `broadcast hash join` отличается от `sort merge join` и когда нужен каждый?
6. Как `bucketing` убирает `Exchange` и почему это ускоряет join?

Предыдущая: [Spark SQL и Dataset](/book-summaries/engineering/learning-spark/06-sql-and-datasets/). Следующая: [Structured Streaming](/book-summaries/engineering/learning-spark/08-structured-streaming/).
