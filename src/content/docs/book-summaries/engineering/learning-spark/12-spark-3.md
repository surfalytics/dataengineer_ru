---
title: "Learning Spark, глава 12: Эпилог: Apache Spark 3.0"
head:
  - tag: title
    content: "Что нового в Spark 3.0: DPP, AQE, pandas UDF | Инжиниринг Данных"
description: "Конспект главы 12 Learning Spark на русском. Dynamic partition pruning, Adaptive Query Execution, join hints, Catalog API, GPU, pandas UDF и explain."
sidebar:
  order: 12
  label: "12. Эпилог: Apache Spark 3.0"
tags:
  - books
  - spark
---

**Главная мысль:** Spark 3.0 ускоряет запросы без правок в вашем коде: `DPP` читает меньше данных, а `AQE` исправляет план во время работы. Кроме того, у `pandas UDF` новый синтаксис, а у SQL есть подсказки для всех видов `join`.

## О чём глава

Книга писалась до выхода Spark 3.0 (код проверяли на 3.0.0-preview2), поэтому авторы лишь выбрали самые заметные новинки. Глава продолжает [главу 11](/book-summaries/engineering/learning-spark/11-ml-pipelines/), где мы видели `mapInPandas`.

![Схема: фильтр по таблице измерений попадает в scan факт-таблицы, и Spark читает только нужные partition](/assets/learning-spark/ch12-dpp.png)

Книга показывает Scala и Python, а здесь везде Python (PySpark). Установку Spark 4.3 описывает [глава 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

## Spark Core и Spark SQL

### Dynamic partition pruning

Идея `DPP` — пропустить данные, которые запросу не нужны. Она работает при `join` факт-таблицы (`fact table`), разбитой на `partition`, и неразбитой таблицы измерений (`dimension table`). Фильтр обычно стоит на измерении (например, `Date`), и без `DPP` Spark читает все `partition` факта.

`DPP` вставляет результат фильтра по измерению в scan факта. Если измерение меньше факта, Spark обычно выбирает `broadcast join`, и шаги такие:

1. Из результата фильтра по измерению строится hash table (`build relation`).
2. Она кладётся в `broadcast variable` и рассылается всем `executor`.
3. Каждый `executor` проверяет hash table и узнаёт, какие строки факта читать.
4. Фильтр попадает в scan факта, и читаются только подходящие `partition`.

`DPP` включена по умолчанию, и с ней Spark лучше справляется с запросами по `star schema`. Проверим: факт `sales` разбит по `sale_date`, а `dim_date` хранит признак выходного дня.

```python
q = """SELECT count(*) AS n, sum(s.amount) AS total
       FROM sales s JOIN dim_date d ON s.sale_date = d.sale_date
       WHERE d.is_weekend"""
for flag in ("true", "false"):
    spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", flag)
    text = plan(spark.sql(q))   # plan() ловит вывод df.explain()
    print(f"DPP={flag}: dynamicpruning in plan = {'dynamicpruning' in text}")
```

```text
DPP=true: dynamicpruning in plan = True
DPP=false: dynamicpruning in plan = False
```

Полный скрипт: [`ch12_planning.py`](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch12_planning.py). Результат запроса одинаков (`n = 800`, `total = 2408`), меняется только объём прочитанных файлов.

### Adaptive Query Execution

`AQE` меняет физический план по статистике, собранной на ходу. Он умеет:

- уменьшать число `reducer` после `shuffle`, сливая мелкие `partition`;
- менять стратегию `join`, например `SortMergeJoin` на `BroadcastHashJoin`;
- справляться с перекосом (`skew`) при `join`.

В Spark 3.0 `AQE` включают настройкой `spark.sql.adaptive.enabled=true`. При этом слиянием и перекосом управляют `spark.sql.adaptive.coalescePartitions.enabled` и `spark.sql.adaptive.skewJoin.enabled`, обе по умолчанию `true`.

![Схема: цикл AQE из четырёх шагов, на шаге оптимизации Catalyst возможны три улучшения плана](/assets/learning-spark/ch12-aqe.png)

`Shuffle` или broadcast-обмен разрывают конвейер операций, потому что результат одного `stage` нужен следующему. Такие границы книга называет `materialization point`: в них план можно пересмотреть. Цикл такой: выполнить `stage`, обновить статистику (число `partition`, байты), заново запустить `Catalyst`, получить новый план и повторять до конца запроса.

В Spark 4.3 `AQE` включён по умолчанию. До запуска план содержит `isFinalPlan=false`, а после запуска в нём появляется отметка `coalesced`: мелкие `partition` слиты.

```text
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
до запуска: isFinalPlan=false: True
после запуска: coalesced: True
```

### SQL join hints

Кроме `BROADCAST`, Spark 3.0 добавил подсказки для остальных стратегий `join`. Их пишут в `/*+ ... */`: `MERGE` (`shuffle sort merge join`), `BROADCAST` (`broadcast hash join`), `SHUFFLE_HASH` (`shuffle hash join`, встречается реже) и `SHUFFLE_REPLICATE_NL` (`shuffle-and-replicate nested loop join`). Мы отключили автоматический `broadcast` через `spark.sql.autoBroadcastJoinThreshold=-1` и посмотрели, какой `join` попал в план:

```python
for hint in ("MERGE", "BROADCAST", "SHUFFLE_HASH", "SHUFFLE_REPLICATE_NL"):
    t = plan(spark.sql(f"SELECT /*+ {hint}(a) */ a.key FROM a JOIN b ON a.key = b.key"), "simple")
```

```text
MERGE                  -> SortMergeJoin
BROADCAST              -> BroadcastHashJoin
SHUFFLE_HASH           -> ShuffledHashJoin
SHUFFLE_REPLICATE_NL   -> CartesianProduct
```

### Catalog plugin API и DataSourceV2

Экспериментальный `DataSourceV2` выводит Spark за пределы Hive metastore. Он подключает внешние источники и каталоги, проталкивает фильтры (`predicate pushdown`) в Parquet, Kafka, Delta Lake, Apache Iceberg и другие, а потоковые и пакетные данные читает одними API. А `Catalog API` создаёт, меняет, читает и удаляет таблицы в подключённом каталоге. Каталог подключают в `spark-defaults.conf` (блок не запускается: нужен свой коннектор):

```text
spark.sql.catalog.ndb_catalog com.ndb.ConnectorImpl
spark.sql.catalog.ndb_catalog.option1 value1
```

Дальше таблицы доступны как `SELECT * FROM ndb_catalog.table_1` и через `DataFrameReader`. Авторы предупреждают: API экспериментальные, и в production их использовать нельзя.

### Планировщик с учётом ускорителей

`Project Hydrogen` — инициатива сообщества, которая сближает ИИ и большие данные: `barrier execution`, планирование с учётом ускорителей, быстрый обмен данными. Базовый `barrier` появился в Spark 2.4.0, а в Spark 3.0 добавили планировщик для GPU в режимах standalone, YARN и Kubernetes. Нужны discovery script с адресами GPU, настройки `spark.executor.resource.gpu.amount` и `spark.task.resource.gpu.amount` и код на `RDD` с `BarrierTaskContext`. Авторы помечают эти шаги как экспериментальные, поэтому пример кода из книги мы не запускали.

## Structured Streaming

В Spark UI появилась вкладка Structured Streaming: сводка по завершённым запросам и детали по каждому (скорость входа и обработки, число строк, длительность `batch`). Настройка не нужна: вкладка включена по умолчанию.

## PySpark, pandas UDF и Pandas Function API

Spark 3.0 требует `pandas` 0.23.2 или новее и `PyArrow` 0.12.1 или новее (для `pandas_udf()` и `toPandas()`).

### Новые pandas UDF с type hints

`pandas UDF` переделали на Python type hints: функция сама описывает вход и выход, а тип вычисления (`PandasUDFType.SCALAR`) не нужен. Так код легче проверять статическим анализом.

```python
@pandas_udf("long")
def plus_one(v: pd.Series) -> pd.Series:
    return v + 1

df = spark.range(3)
df.withColumn("plus_one", plus_one("id")).orderBy("id").show()
```

```text
+---+--------+
| id|plus_one|
+---+--------+
|  0|       1|
|  1|       2|
|  2|       3|
+---+--------+
```

### Iterator в pandas UDF

`pandas UDF` часто нужны для распределённого `inference` модели, обученной на одном узле. Но большую модель дорого загружать заново на каждый `batch`. Теперь функция принимает итератор из `pandas.Series` или `pandas.DataFrame`, и модель грузят один раз:

```python
@pandas_udf("long")
def plus_one_iter(batches: Iterator[pd.Series]) -> Iterator[pd.Series]:
    offset = 1  # здесь в реальной задаче загружают модель: один раз на процесс
    for s in batches:
        yield s + offset
```

![Схема: обычная pandas UDF загружает модель на каждый batch, а UDF с Iterator загружает её один раз](/assets/learning-spark/ch12-pandas-iterator.png)

### Новые Pandas Function API

Новые функции применяют код к целому `DataFrame`, а не к отдельным колонкам. Например, `mapInPandas()` (глава 11) берёт итератор `pandas.DataFrame` и возвращает другой итератор. Длина выхода не обязана совпадать с входом, а размер порции задаёт `spark.sql.execution.arrow.maxRecordsPerBatch`.

`applyInPandas()` работает с cogrouped данными: берёт два `pandas.DataFrame` с общим ключом, применяет функцию к каждой паре групп и объединяет результаты в итоговую таблицу. Предупреждение: вся группа `cogroup` загружается в память, поэтому при перекосе или больших группах будет `OOM`.

```python
def asof_join(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    return pd.merge_asof(left, right, on="time", by="id")

(df1.groupby("id").cogroup(df2.groupby("id"))
    .applyInPandas(asof_join, "time int, id int, v1 double, v2 string")
    .orderBy("id", "time").show())
```

```text
+----+---+---+---+
|time| id| v1| v2|
+----+---+---+---+
|1201|  1|1.0|  x|
|1202|  1|3.0|  x|
|1201|  2|2.0|  y|
|1202|  2|4.0|  y|
+----+---+---+---+
```

> **Пояснение:** Spark 4.3 требует для `pandas UDF` `PyArrow` 18 или новее. Код книги не меняется, нужно лишь обновить библиотеку. Скрипт: [`ch12_pandas.py`](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch12_pandas.py).

## Изменения в поведении

Полный список авторы не дают, потому что список получился бы слишком длинным, и отправляют к release notes и migration guides.

- **Языки.** Python ниже 3.6 и Java 8 устарели и дают предупреждения.
- **`unionAll()`.** Метод больше не считается устаревшим: теперь это псевдоним `union()`.
- **`groupByKey()`.** У `Dataset` ключ простого типа раньше назывался `value`, и `count()` давал `(value, count)`. Теперь это `(key, count)`. Старое имя возвращает `spark.sql.legacy.dataset.nameNonStructGroupingKeyAsValue`. Пример книги на Scala.
- **`explain(mode)`.** Планы `Catalyst` показываются в видах `"simple"` (по умолчанию), `"extended"`, `"cost"`, `"codegen"` и `"formatted"`; в SQL есть `EXPLAIN FORMATTED`. Формат `formatted` нумерует узлы и пишет подробности под ними:

```text
== Physical Plan ==
* Filter (2)
+- * Range (1)

(1) Range [codegen id : 1]
Output [1]: [id#73L]
Arguments: Range (0, 10, step=1, splits=Some(2))

(2) Filter [codegen id : 1]
Input [1]: [id#73L]
Condition : (id#73L > 5)
```

## Итоги главы

- `DPP` вставляет фильтр по измерению в scan факта, поэтому читаются только нужные `partition`.
- `AQE` пересматривает план в точках материализации: сливает `partition`, меняет `join` и справляется с перекосом.
- `Catalog API`, `DataSourceV2` и планировщик GPU пока экспериментальные.
- `pandas UDF` используют type hints и итераторы, а `mapInPandas()` и `applyInPandas()` работают с целым `DataFrame`.

## Что изменилось к 2026 году

> Это наше дополнение, его нет в книге.

- `AQE` включён по умолчанию, хотя в Spark 3.0 был выключен.
- `DataSourceV2` и `Catalog API` стали основой для Delta Lake и Apache Iceberg, ярлык «экспериментально» устарел.
- В Spark 4 включён режим ANSI SQL: неверное приведение типа и деление на ноль дают ошибку, а не `NULL`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `DPP` (dynamic partition pruning) | Фильтр по измерению вставляется в scan факта, лишние `partition` не читаются |
| `AQE` (`adaptive query execution`) | Spark меняет план по статистике во время работы |
| `DataSourceV2` | API для внешних источников, приёмников и каталогов |

## Что это значит на практике

- Разбивайте факт по колонке, по которой его соединяют с измерением: тогда сработает `DPP`.
- Если запрос тормозит после `shuffle`, смотрите финальный план в `explain`: там видна работа `AQE`.
- Для `inference` большой модели берите `pandas UDF` с `Iterator`, чтобы не грузить модель на каждый `batch`.
- В `applyInPandas` следите за размером групп: каждая попадает в память целиком.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём данные

```sql
CREATE TABLE sales AS
SELECT i AS order_id, DATE '2026-01-01' + (i % 30)::INT AS sale_date, (i % 7)::INT AS amount
FROM range(3000) t(i);

CREATE TABLE dim_date AS
SELECT DISTINCT sale_date, dayofweek(sale_date) IN (0, 6) AS is_weekend FROM sales;
```

### Шаг 2. Проверяем

```sql
SELECT count(*) AS rows_total, count(DISTINCT sale_date) AS days FROM sales;
```

```text
┌────────────┬───────┐
│ rows_total │ days  │
│   int64    │ int64 │
├────────────┼───────┤
│       3000 │    30 │
└────────────┴───────┘
```

### Задания

**1.** Посчитайте число заказов и сумму `amount` по выходным дням через `JOIN` с `dim_date`.

<details><summary>Решение</summary>

```sql
SELECT count(*) AS n, sum(s.amount) AS total
FROM sales s JOIN dim_date d ON s.sale_date = d.sale_date
WHERE d.is_weekend;
```

```text
┌───────┬────────┐
│   n   │ total  │
│ int64 │ int128 │
├───────┼────────┤
│   800 │   2408 │
└───────┴────────┘
```

Результат совпал со Spark.
</details>

**2.** Сделайте то же без `JOIN`: отфильтруйте факт по датам из измерения. Сколько дат прочитал бы Spark с `DPP`?

<details><summary>Решение</summary>

```sql
SELECT count(*) AS n, sum(amount) AS total
FROM sales
WHERE sale_date IN (SELECT sale_date FROM dim_date WHERE is_weekend);

SELECT count(*) AS days_to_read FROM dim_date WHERE is_weekend;
```

```text
┌───────┬────────┐
│   n   │ total  │
│ int64 │ int128 │
├───────┼────────┤
│   800 │   2408 │
└───────┴────────┘
┌──────────────┐
│ days_to_read │
│    int64     │
├──────────────┤
│            8 │
└──────────────┘
```

Подзапрос играет роль динамического фильтра: из 30 дат читаются 8.
</details>

**3.** Повторите `applyInPandas(asof_join)` одним запросом. В DuckDB есть `ASOF JOIN`.

<details><summary>Решение</summary>

```sql
CREATE TABLE l (time INT, id INT, v1 DOUBLE);
INSERT INTO l VALUES (1201, 1, 1.0), (1201, 2, 2.0), (1202, 1, 3.0), (1202, 2, 4.0);
CREATE TABLE r (time INT, id INT, v2 VARCHAR);
INSERT INTO r VALUES (1201, 1, 'x'), (1201, 2, 'y');

SELECT l.time, l.id, l.v1, r.v2
FROM l ASOF LEFT JOIN r ON l.id = r.id AND l.time >= r.time
ORDER BY l.id, l.time;
```

```text
┌───────┬───────┬────────┬─────────┐
│ time  │  id   │   v1   │   v2    │
│ int32 │ int32 │ double │ varchar │
├───────┼───────┼────────┼─────────┤
│  1201 │     1 │    1.0 │ x       │
│  1202 │     1 │    3.0 │ x       │
│  1201 │     2 │    2.0 │ y       │
│  1202 │     2 │    4.0 │ y       │
└───────┴───────┴────────┴─────────┘
```

К каждой строке `l` берётся последняя строка `r` с тем же `id` и не более поздним временем.
</details>

## Вопросы для самопроверки

1. Почему `DPP` полезен, когда факт разбит на `partition`, а измерение нет?
2. Что такое `materialization point` и почему `AQE` пересматривает план именно там?
3. Почему `pandas UDF` с `Iterator` быстрее для большой модели?
4. Чем опасен `applyInPandas` при `skew`?
5. Зачем `AQE` сливать мелкие `partition` после `shuffle`?

Предыдущая: [MLflow, развёртывание и масштабирование моделей](/book-summaries/engineering/learning-spark/11-ml-pipelines/). Следующая: нет, это последняя глава.
