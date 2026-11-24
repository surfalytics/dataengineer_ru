---
title: "Learning Spark, глава 2: Установка Spark и первые шаги"
head:
  - tag: title
    content: "Как установить Spark и запустить первое приложение | Инжиниринг Данных"
description: "Конспект главы 2 Learning Spark на русском. Установка Spark, shell, job, stage и task, lazy evaluation, Spark UI и первое приложение на PySpark."
sidebar:
  order: 2
  label: "2. Установка Spark и первые шаги"
tags:
  - books
  - spark
---

**Главная мысль:** чтобы начать работать со Spark, нужно поставить его, запустить shell и понять, как код превращается в `job`, `stage` и `task`. Spark ничего не считает, пока не встретит `action`: до этого шаги кода только дописывают план.

## О чём глава

Глава ведёт от нуля до первого приложения. Она продолжает [главу 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/) про `driver`, `executor` и `partition` и готовит [главу 3](/book-summaries/engineering/learning-spark/03-structured-apis/) про Structured API. Все примеры идут в `local mode`: вся обработка выполняется на одной машине. Это удобно для учёбы и малых данных. Для больших данных нужны YARN или Kubernetes.

Темы: установка, папки Spark, shell, понятия приложения, ленивое вычисление, Spark UI и первое приложение.

![Схема: три шага главы и первое приложение](/assets/learning-spark/ch02-steps.png)

Spark UI открывается на третьем шаге: в нём видно `job` и `stage`.

## Шаг 1: скачиваем Spark

Скачайте архив на странице загрузки Spark. В книге выбран вариант «Pre-built for Apache Hadoop 2.7»: в нём есть всё, чтобы запустить Spark на ноутбуке. Если у вас уже стоит Hadoop, выберите сборку под его версию.

Тем, кто пишет только на Python, достаточно `pip install pyspark` (со Spark 2.2). Пакет меньше, потому что в нём нет библиотек для Scala, Java и R. Дополнения ставятся так: `pip install pyspark[sql,ml,mllib]`. Нужна ещё Java 8 или новее и переменная `JAVA_HOME`.

## Папки и файлы Spark

После распаковки архива (`tar -xf`) в папке лежат такие каталоги и файл `README.md` с инструкциями. Книга предполагает Linux или macOS.

| Папка или файл | Что внутри |
|---|---|
| `bin` | Скрипты: shell (`pyspark`, `spark-shell`, `spark-sql`, `sparkR`) и `spark-submit` для запуска приложений |
| `sbin` | Административные скрипты: запуск и остановка компонентов кластера |
| `kubernetes` | Dockerfile для образов Spark в Kubernetes (с версии 2.4) |
| `data` | Входные файлы для MLlib, Structured Streaming и GraphX |
| `examples` | Примеры на Java, Python, R и Scala |

## Шаг 2: запускаем shell

Shell — это интерактивная оболочка, в которой данные анализируют по ходу дела. Spark даёт четыре таких оболочки: `pyspark`, `spark-shell` (Scala), `spark-sql` и `sparkR`. Они умеют подключаться к кластеру и загружать данные в память `executor`, поэтому учиться в них удобно.

Запустите `pyspark` из папки `bin` (после установки через pip достаточно `pyspark`). Shell напечатает версию и сообщит, что `SparkSession` доступна как переменная `spark`. Выходят из shell по `Ctrl-D`.

### Первый пример в local mode

Пример читает текстовый файл как `DataFrame`, показывает часть строк и считает их. Книга берёт `README.md` из папки Spark, а мы создаём свой маленький файл. `orderBy` нужен, чтобы вывод не менялся.

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder.master("local[2]").appName("Ch02Shell")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Готовим небольшой текстовый файл: 12 строк, в 5 из них есть слово Spark
lines = []
for i in range(12):
    lines.append(f"Spark line {i}" if i % 2 == 0 and i < 10 else f"plain line {i}")
with open("/tmp/readme.txt", "w") as f:
    f.write("\n".join(lines) + "\n")

print(spark.version)
strings = spark.read.text("/tmp/readme.txt")          # transformation
strings.orderBy("value").show(4, truncate=False)      # action
print(strings.count())                                # action

# filter() ничего не считает, count() запускает всё
filtered = strings.filter(strings.value.contains("Spark"))
print(filtered.count())
spark.stop()
```

```text
4.3.0
+------------+
|value       |
+------------+
|Spark line 0|
|Spark line 2|
|Spark line 4|
|Spark line 6|
+------------+
only showing top 4 rows
12
5
```

`truncate=False` отключает обрезание длинных строк. Книга показывает тот же код на Scala: синтаксис почти совпадает. Файл читается в `DataFrame` через Structured API, а не в `RDD`: с версии 2.x `RDD` считается низкоуровневым API. Внутри операции раскладываются на `RDD`, но этот код пользователь не видит.

## Шаг 3: понятия приложения Spark

Чтобы понять, что Spark делает с кодом из примера, нужны пять понятий.

| Термин | Значение |
|---|---|
| Application | Пользовательская программа на Spark. Состоит из `driver` и `executor` на кластере |
| `SparkSession` | Точка входа в Spark. В shell её создаёт `driver`, в приложении вы сами |
| `Job` | Параллельное вычисление из нескольких `task`. Появляется в ответ на `action`, например `save()` или `collect()` |
| `Stage` | Часть `job`: набор `task`, зависящий от других таких наборов |
| `Task` | Одна единица работы для одного `executor` |

### Приложение и SparkSession

В центре каждого приложения — программа `driver`, которая создаёт `SparkSession`. В shell `driver` входит в сам shell. Выше всё шло в одной JVM, потому что shell запущен локально. Но его можно подключить и к кластеру: подсказку даёт `pyspark --help`. Тогда компоненты общаются через `driver`, как на [схеме из главы 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

### Job, stage и task

`Driver` превращает ваш код в один или несколько `job`. Каждый `job` он превращает в `DAG` — это и есть план выполнения. Узел `DAG` может быть одним `stage` или несколькими.

`Stage` выделяют по тому, какие операции можно выполнять последовательно, а какие параллельно. Границу проводят там, где данные надо передавать между `executor`. Каждый `stage` состоит из `task`. Один `task` занимает одно ядро и работает с одной `partition`, поэтому `executor` с 16 ядрами обрабатывает 16 `partition` одновременно.

![Схема: application запускает job, job делится на stage, stage состоит из task](/assets/learning-spark/ch02-job-stage-task.png)

Верхний `stage` идёт до обмена данными, нижний — после него.

### Transformations, actions и lazy evaluation

Операции над данными бывают двух видов: `transformation` и `action`. `Transformation` превращает `DataFrame` в новый `DataFrame`, не меняя исходный. Это неизменяемость (`immutability`): `select()` или `filter()` возвращают новый результат.

Все `transformation` вычисляются лениво (`lazy evaluation`, ленивое вычисление). Spark не считает результат сразу, а записывает шаги в `lineage`. По этой записи Spark потом может переставить и объединить шаги и собрать их в `stage`. Вычисление начинается на `action`: он запускает все записанные `transformation`.

![Схема: transformations записываются в lineage, action запускает вычисление](/assets/learning-spark/ch02-lazy.png)

Синие блоки дополняют план, красный `count()` запускает цепочку.

| Transformation | Action |
|---|---|
| `orderBy()`, `groupBy()`, `filter()`, `select()`, `join()` | `show()`, `take()`, `count()`, `collect()`, `save()` |

Ленивость помогает оптимизировать запрос, а запись шагов и неизменяемость дают `fault tolerance` (отказоустойчивость): `DataFrame` между шагами не меняются, а шаги записаны, поэтому после сбоя Spark повторяет `lineage`.

Проверим ленивость. Накопитель (`accumulator`) считает вызовы нашей функции. После `filter()` он равен нулю: работа началась только на `count()`.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import BooleanType

spark = (SparkSession.builder.master("local[2]").appName("Ch02Lazy")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 1. Ленивое вычисление: накопитель считает, сколько раз вызвали нашу функцию
calls = spark.sparkContext.accumulator(0)

def is_even(x):
    calls.add(1)
    return x % 2 == 0

is_even_udf = udf(is_even, BooleanType())

df = spark.range(1000)                                # 1000 строк
filtered = df.filter(is_even_udf(col("id")))          # transformation
print("после filter:", calls.value)
print("строк в результате:", filtered.count())        # action
print("после count:", calls.value)

# 2. Narrow и wide: ищем Exchange (shuffle) в плане
narrow = df.filter("id % 2 = 0")
wide = df.groupBy((col("id") % 3).alias("k")).count()
print("--- filter (narrow)")
narrow.explain()
print("--- groupBy (wide)")
wide.explain()
spark.stop()
```

```text
после filter: 0
строк в результате: 500
после count: 1000
--- filter (narrow)
== Physical Plan ==
*(1) Filter ((id#0L % 2) = 0)
+- *(1) Range (0, 1000, step=1, splits=2)


--- groupBy (wide)
== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- HashAggregate(keys=[_groupingexpression#18L], functions=[count(1)])
   +- Exchange hashpartitioning(_groupingexpression#18L, 200), ENSURE_REQUIREMENTS, [plan_id=83]
      +- HashAggregate(keys=[_groupingexpression#18L], functions=[partial_count(1)])
         +- Project [(id#0L % 3) AS _groupingexpression#18L]
            +- Range (0, 1000, step=1, splits=2)
```

В примере книги то же самое: две `transformation` (`read()`, `filter()`) и один `action` (`count()`). Пока не выполнен `count()`, ничего не происходит. В книге строк со словом Spark 20, у нас 5.

### Narrow и wide transformations

Ленивость позволяет Spark увидеть весь запрос. Он объединяет операции в один `stage` или делит их там, где нужен `shuffle` — обмен данными по кластеру. По типу зависимостей между входными и выходными данными такие операции делятся на два вида.

- `Narrow transformation`: одну выходную `partition` можно вычислить из одной входной. Например, `filter()` работает в пределах одной `partition`, без обмена данными.
- `Wide transformation`: нужны данные из других `partition`, их читают, объединяют и пишут на диск. Например, `groupBy()` и `orderBy()`. Каждая `partition` знает только свою часть итога, поэтому подсчёт после `groupBy()` требует `shuffle`.

![Схема: narrow transformation работает внутри partition, wide требует shuffle между partition](/assets/learning-spark/ch02-narrow-wide.png)

Слева каждая `partition` переходит в свою, справа каждая входная отправляет данные в обе выходные. В плане выше `Exchange` есть только у `groupBy`: это `shuffle`.

## Spark UI

Spark UI — веб-интерфейс, в котором видны `job`, `stage` и `task`. `Driver` запускает его на порту 4040, в `local mode` это `http://localhost:4040`. Там же видны память, работающие `executor` и запросы Spark SQL.

В книге разобран пример из shell. Вкладка «DAG Visualization» показывает один `job` и один `stage`. Блока `Exchange` нет, потому что обмен данными не нужен. В `stage 0` один `task`, а несколько `task` шли бы параллельно. К Spark UI книга вернётся в [главе 7](/book-summaries/engineering/learning-spark/07-optimizing-and-tuning/) как к инструменту отладки.

## Databricks Community Edition

Databricks продаёт управляемую платформу Spark в облаке. Примеры книги можно пробовать и в бесплатной Databricks Community Edition: там есть учебные материалы, ноутбуки на Python, R, Scala и SQL и импорт чужих ноутбуков, в том числе Jupyter.

## Первое самостоятельное приложение

Примеры из дистрибутива запускает `bin/run-example <class> [params]`, например `JavaWordCount README.md`. Подсчёт слов — это «Hello, World» распределённых вычислений. Но этот пример слишком известен, и авторы решают похожую задачу на большем наборе данных.

Одна из авторов учит студентов в разных штатах США и печёт для них печенье с конфетами M&M. Ей нужно знать, какой цвет любят в каждом штате. В файле больше 100 000 строк вида `<state, mnm_color, count>`. Программа считает строки для каждой пары «штат, цвет», а потом отдельно смотрит штат CA. Данные мы генерируем сами: 20 000 строк с фиксированным `seed`, в CA чаще жёлтый.

```python
import csv
import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import count

# Данные: 20 000 строк <State, Color, Count>, фиксированный seed
random.seed(42)
states = ["CA", "WA", "OR", "TX", "CO", "NV", "AZ", "UT", "NM", "WY"]
colors = ["Yellow", "Green", "Brown", "Orange", "Red", "Blue"]
with open("/tmp/mnm_dataset.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["State", "Color", "Count"])
    for _ in range(20000):
        state = random.choice(states)
        weights = [3, 1, 1, 1, 1, 1] if state == "CA" else [1] * 6  # в CA любят Yellow
        w.writerow([state, random.choices(colors, weights)[0], random.randint(1, 100)])

spark = (SparkSession.builder.master("local[2]").appName("PythonMnMCount")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

mnm_df = (spark.read.format("csv")
          .option("header", "true")
          .option("inferSchema", "true")
          .load("/tmp/mnm_dataset.csv"))

count_mnm_df = (mnm_df
                .select("State", "Color", "Count")
                .groupBy("State", "Color")
                .agg(count("Count").alias("Total"))
                .orderBy("Total", "State", "Color", ascending=[False, True, True]))
count_mnm_df.show(n=5, truncate=False)
print("Total Rows = %d" % count_mnm_df.count())

ca_count_mnm_df = (mnm_df
                   .select("State", "Color", "Count")
                   .where(mnm_df.State == "CA")
                   .groupBy("State", "Color")
                   .agg(count("Count").alias("Total"))
                   .orderBy("Total", "Color", ascending=[False, True]))
ca_count_mnm_df.show(n=10, truncate=False)
spark.stop()
```

```text
+-----+------+-----+
|State|Color |Total|
+-----+------+-----+
|CA   |Yellow|748  |
|AZ   |Brown |369  |
|OR   |Green |366  |
|WY   |Orange|366  |
|TX   |Red   |364  |
+-----+------+-----+
only showing top 5 rows
Total Rows = 60
+-----+------+-----+
|State|Color |Total|
+-----+------+-----+
|CA   |Yellow|748  |
|CA   |Red   |265  |
|CA   |Brown |245  |
|CA   |Blue  |240  |
|CA   |Orange|239  |
|CA   |Green |236  |
+-----+------+-----+
```

`SparkSession` создаётся один раз: в одной JVM она может быть только одна. Файл читается как CSV с заголовком, типы колонок выводит `schema inference`. Цепочка `select`, `groupBy`, `agg`, `orderBy` состоит из `transformation`. Вычисление начинается на `show()` и `count()`, потому что это `action`. `RDD` здесь нет совсем: авторы подчёркивают, что код говорит Spark, что делать, а не как. Заметьте: `count("Count")` считает строки, а не складывает конфеты. В книге в CA лидирует жёлтый (1807 строк), у нас тоже, но числа другие.

Приложение запускают так: `$SPARK_HOME/bin/spark-submit mnmcount.py data/mnm_dataset.csv`. Переменная `SPARK_HOME` указывает на папку установки Spark. Чтобы убрать сообщения INFO, книга предлагает правку `log4j.properties`. У нас это делает `setLogLevel`.

### Версия на Scala и сборка через sbt

Книга показывает ту же программу на Scala: API почти совпадают. Python собирать не надо, а Scala надо. Проект описывает `build.sbt` (версии Scala и зависимости от `spark-core` и `spark-sql`), затем `sbt clean package` собирает jar, а `spark-submit --class main.scala.chapter2.MnMcount ...jar data/mnm_dataset.csv` его запускает. Результат такой же, как у Python. На наших страницах только PySpark.

## Итоги главы

- `Local mode` подходит для учёбы и прототипов, для больших данных нужны YARN или Kubernetes.
- В shell `SparkSession` уже есть под именем `spark`, в приложении её создаёте вы.
- Приложение превращается в `job`, `job` делится на `stage`, `stage` состоит из `task`. Один `task` работает на одном ядре с одной `partition`.
- `Transformation` не меняет данные и вычисляется лениво. Работа начинается на `action`.
- `Lineage` и неизменяемость `DataFrame` дают `fault tolerance`: потерянное Spark пересчитывает.
- `Narrow transformation` работает в пределах одной `partition`, `wide transformation` вызывает `shuffle` и делит работу на `stage`.
- Spark UI на порту 4040 показывает `job`, `stage` и `task`.
- Structured API говорят Spark, что делать, а не как. Во всей книге они используются вместо `RDD`.

## Что изменилось к 2026 году

> Это наше дополнение, его нет в книге.

Книга писалась на Spark 3.0.0-preview2, а сейчас последняя стабильная версия — Spark 4.3.0. Как его установить, мы описали в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/#как-установить-spark), поэтому здесь не повторяем. Все примеры этой главы мы запускали в нашем Docker-образе со Spark 4.3.0, например:

```bash
scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch02_mnmcount.py
```

Что ещё поменялось по сравнению с книгой:

- **Логи.** В Spark 4 используется `log4j2`, и шаблон называется `log4j2.properties.template`. Проще вызвать `setLogLevel("WARN")`.
- **Scala.** Spark 4 собран только под Scala 2.13, поэтому в `build.sbt` и в имени jar-файла (`_2.12`) версию надо поменять.

## Ключевые термины

| Термин | Значение |
|---|---|
| `local mode` | Вся обработка идёт на одной машине |
| `SparkSession` | Точка входа в Spark. В shell доступна как `spark` |
| `job` | Результат одного `action`. Делится на `stage` |
| `stage` | Часть `job` между обменами данными |
| `task` | Работа на одной `partition` и одном ядре |
| `DAG` | План выполнения `job` |
| `transformation` | Шаг, который даёт новый `DataFrame` и ничего не считает |
| `action` | Шаг, который запускает вычисление |
| `lazy evaluation` | Шаги записываются и выполняются при `action` |
| `lineage` | Записанная история шагов |
| `narrow` / `wide transformation` | Работает внутри одной `partition` / вызывает `shuffle` |
| `shuffle` | Обмен данными между узлами по ключу |
| `spark-submit` | Скрипт запуска приложения |

## Что это значит на практике

- Сначала проверяйте идею в `pyspark` на малых данных, потом пишите приложение и запускайте его через `spark-submit`.
- Если запрос «ничего не делает», проверьте, был ли `action`. Без него Spark только строит план.
- Следите за `wide transformation`: `groupBy`, `orderBy` и `join` вызывают `shuffle`, а это самая дорогая часть запроса.
- Смотрите план через `explain()` и Spark UI. Слово `Exchange` значит `shuffle`.
- Образ Docker с зафиксированной версией работает одинаково у всей команды, а локальная установка Java и Hadoop отнимает время.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Здесь мы делаем на SQL то же, что делал Spark-код с M&M. Данные создаём в самом SQL.

### Шаг 1. Создаём данные

```sql
CREATE TABLE mnm AS
SELECT
    ['CA','WA','OR','TX','CO'][1 + (i * 7) % 5] AS state,
    ['Yellow','Green','Brown','Red'][1 + (i * i + i // 3) % 4] AS color,
    1 + (i * 13) % 50 AS cnt
FROM generate_series(1, 1000) t(i);
```

### Шаг 2. Проверяем

```sql
SELECT count(*) AS rows, count(DISTINCT state) AS states, count(DISTINCT color) AS colors FROM mnm;
```

```text
┌───────┬────────┬────────┐
│ rows  │ states │ colors │
│ int64 │ int64  │ int64  │
├───────┼────────┼────────┤
│  1000 │      5 │      4 │
└───────┴────────┴────────┘
```

### Задания

**Задание 1.** Найдите пять самых частых пар «штат, цвет». Это аналог `groupBy().agg(count()).orderBy()`.

<details>
<summary>Решение</summary>

```sql
SELECT state, color, count(cnt) AS total
FROM mnm
GROUP BY state, color
ORDER BY total DESC, state, color
LIMIT 5;
```

```text
┌─────────┬─────────┬───────┐
│  state  │  color  │ total │
│ varchar │ varchar │ int64 │
├─────────┼─────────┼───────┤
│ CA      │ Brown   │    68 │
│ OR      │ Yellow  │    68 │
│ CO      │ Brown   │    67 │
│ TX      │ Yellow  │    67 │
│ WA      │ Brown   │    67 │
└─────────┴─────────┴───────┘
```

`GROUP BY` — это `wide transformation`: в Spark здесь был бы `shuffle`.

</details>

**Задание 2.** Посчитайте цвета только для штата CA.

<details>
<summary>Решение</summary>

```sql
SELECT color, count(cnt) AS total
FROM mnm
WHERE state = 'CA'
GROUP BY color
ORDER BY total DESC, color;
```

```text
┌─────────┬───────┐
│  color  │ total │
│ varchar │ int64 │
├─────────┼───────┤
│ Brown   │    68 │
│ Yellow  │    65 │
│ Green   │    34 │
│ Red     │    33 │
└─────────┴───────┘
```

`WHERE` — это `narrow transformation`: каждую строку проверяют отдельно.

</details>

**Задание 3.** `count(cnt)` считает строки, а не конфеты. Покажите для CA число строк и сумму `cnt`.

<details>
<summary>Решение</summary>

```sql
SELECT color, count(cnt) AS rows_n, sum(cnt) AS mnm_sum
FROM mnm
WHERE state = 'CA'
GROUP BY color
ORDER BY color;
```

```text
┌─────────┬────────┬─────────┐
│  color  │ rows_n │ mnm_sum │
│ varchar │ int64  │ int128  │
├─────────┼────────┼─────────┤
│ Brown   │     68 │    1658 │
│ Green   │     34 │     759 │
│ Red     │     33 │     763 │
│ Yellow  │     65 │    1520 │
└─────────┴────────┴─────────┘
```

Если `cnt` — число конфет, то для вопроса «какой цвет любят» нужна `sum`. Она даёт другой порядок цветов.

</details>

## Вопросы для самопроверки

1. Почему `local mode` подходит для учёбы, но не для больших данных?
2. Чем `job`, `stage` и `task` отличаются друг от друга? Что запускает новый `job`, а что проводит границу между `stage`?
3. Почему `filter()` возвращается мгновенно, а `count()` может работать долго?
4. Как `lineage` и неизменяемость `DataFrame` помогают пережить сбой?
5. Почему `groupBy()` — это `wide transformation`, а `filter()` — `narrow`? Как это увидеть в плане запроса?
6. Чем запуск приложения на Python отличается от Scala?

Предыдущая: [Введение в Apache Spark](/book-summaries/engineering/learning-spark/01-intro-to-spark/). Следующая: [Structured API в Spark](/book-summaries/engineering/learning-spark/03-structured-apis/).
