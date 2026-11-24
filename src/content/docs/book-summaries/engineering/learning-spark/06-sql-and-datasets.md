---
title: "Learning Spark, глава 6: Spark SQL и Dataset"
head:
  - tag: title
    content: "Spark Dataset, encoder и цена lambda | Инжиниринг Данных"
description: "Конспект главы 6 Learning Spark на русском. Типизированный Dataset, encoder, формат Tungsten, SerDe и почему DSL быстрее lambda."
sidebar:
  order: 6
  label: "6. Spark SQL и Dataset"
tags:
  - books
  - spark
---

**Главная мысль:** `Dataset` — это типизированный API для Scala и Java. Он удобен, но за удобство приходится платить: данные приходится переводить между внутренним форматом Spark и объектами JVM. Чем меньше таких переводов, тем быстрее запрос.

## О чём глава

В [главах 4 и 5](/book-summaries/engineering/learning-spark/05-sql-dataframes-external-sources/) мы работали с `DataFrame`. Теперь авторы разбирают устройство `Dataset` и цену его удобства.

![Схема: выражение DSL понятно Catalyst и оптимизируется, а lambda остаётся для него чёрным ящиком](/assets/learning-spark/ch06-catalyst-opaque.png)

Выражение Spark оптимизирует, а внутрь lambda-функции заглянуть не может.

## Единый API для Java и Scala

Строго типизированы только Scala и Java, поэтому Python и R работают лишь с `DataFrame` без типов. `Dataset` — это типизированные объекты предметной области. Их обрабатывают параллельно функциями или операторами `DSL` (`filter`, `select`, `groupBy`), знакомыми по `DataFrame`. Интерфейс у Scala и Java общий, поэтому Java-разработчики больше не отстают от Scala: любое будущее изменение `groupBy()`, `map()` или `filter()` будет одинаковым в обоих языках.

> **Пояснение:** в PySpark 4.3 типизированного `Dataset` нет. Scala и Java здесь описаны текстом, а запускаемый код написан на PySpark. Установку Spark 4.3 описывает [глава 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

## Case class и JavaBean

Чтобы получить `Dataset[T]` в Scala, нужен `case class`: он описывает объект и служит схемой. Книга берёт JSON с блогерами и объявляет `case class Bloggers(...)`. Затем файл читают с `.as[Bloggers]`, и каждая строка получает тип `Bloggers`. В Java то же делают класс `JavaBean` и явный `encoder`: `Encoders.bean(Bloggers.class)`.

Поэтому здесь нужна подготовка: заранее знать имена и типы всех колонок. В `DataFrame` Spark может вывести схему сам, а в `Dataset` типы задают заранее, и класс должен совпадать со схемой данных.

## Работа с Dataset

### Тестовые данные

Авторы создают 1000 объектов `Usage` с полями `uid`, `uname` (случайное имя) и `usage` (минуты использования сервиса) через `spark.createDataset(data)`. В Scala `encoder` подставляется сам, в Java его указывают явно.

### Функции высшего порядка

Объекты `Dataset` преобразуют функциями `map()`, `reduce()`, `filter()`, `select()`, `aggregate()`. Это функции высшего порядка (`higher-order functions`): они принимают `lambda`, замыкания или обычные функции.

Например, `filter()` оставляет пользователей с `usage` больше 900 минут. Условие передают лямбдой (`d => d.usage > 900`) или именованной функцией. В Java для этого есть `FilterFunction<T>`.

`map()` может вернуть и вычисленное значение. Книга считает стоимость: при `usage > 750` минута стоит 0,15, иначе 0,50. Но тогда результат — одна колонка `value`, и не видно, к какому пользователю относится цена. Чтобы связать цену с пользователем, создают класс `UsageCost` с полем `cost`, и `map()` возвращает его. В Java для этого нужны `MapFunction<T>` и ещё один `encoder`.

Плюсы функционального стиля: поля читаются через точку, часть ошибок видна при компиляции. Но он не обязателен: те же `filter` и `map` пишут на `DSL` или в SQL, например `dsUsage.filter("usage > 900")`. Функции высшего порядка работают и с `DataFrame`, потому что это `Dataset[Row]`.

### Из DataFrame в Dataset

Для строгой проверки типов превращают `DataFrame` в `Dataset`: `df.as[SomeCaseClass]`. Чтение JSON возвращает `Dataset[Row]`, а `.as[Bloggers]` включает `encoder`, который переводит данные из внутреннего формата Spark в объекты `Bloggers`.

### Те же шаги на PySpark

В Python типов нет, поэтому повторяем шаги книги на `DataFrame`. Скрипт: `scripts/learning-spark-code/ch06_dataset_costs.py`.

```python
r = random.Random(42)
data = [(i, f"user-{i:04d}", r.randrange(1000)) for i in range(1000)]
ds_usage = spark.createDataFrame(data, "uid INT, uname STRING, usage INT")

ds_usage.filter(col("usage") > 900).orderBy(desc("usage"), "uid").show(3)

# аналог map() с UsageCost: новая колонка cost, остальные остаются
cost = when(col("usage") > 750, col("usage") * 0.15).otherwise(col("usage") * 0.50)
ds_usage.withColumn("cost", cost).orderBy("uid").show(3)
```

Вывод (Spark 4.3.0):

```text
+---+---------+-----+
|uid|    uname|usage|
+---+---------+-----+
|625|user-0625|  999|
|616|user-0616|  997|
| 66|user-0066|  996|
+---+---------+-----+

+---+---------+-----+-----+
|uid|    uname|usage| cost|
+---+---------+-----+-----+
|  0|user-0000|  654|327.0|
|  1|user-0001|  114| 57.0|
|  2|user-0002|   25| 12.5|
+---+---------+-----+-----+
```

## Память для Dataset и DataFrame

Скорость Spark зависит от работы с памятью. Подход менялся в три шага:

| Версия | Как хранились данные |
|---|---|
| Spark 1.0 | Java-объекты на основе `RDD`. Сериализация дорогая, данные лежат в куче JVM, и большие наборы зависят от сборщика мусора (`GC`) |
| Spark 1.x, Tungsten | Строковый формат вне кучи (`off-heap`) со смещениями и указателями. `GC` почти не мешает |
| Spark 2.x, Tungsten второго поколения | Кодогенерация на весь `stage` (`whole-stage code generation`) и векторная колоночная раскладка. Расчёт на кэши CPU и `SIMD` |

## Encoder

`Encoder` переводит данные из формата Tungsten в объекты JVM и обратно, включая примитивы. Для примитивов, `case class` и `JavaBean` Spark создаёт `encoder` сам. Они заметно быстрее сериализации Java и Kryo.

### Формат Spark и объекты Java

У объектов Java большие накладные расходы: заголовок, hashcode, служебные данные. Даже строка «abcd» занимает 48 байт, а не 4. Поэтому Spark хранит данные одним сплошным блоком вне кучи, а объект создаёт `encoder` по запросу.

![Схема: encoder переводит объект JVM в строку Tungsten и обратно](/assets/learning-spark/ch06-encoders.png)

Слева — раздутый объект JVM, справа — компактная строка Tungsten.

### Сериализация и десериализация (SerDe)

Отправитель кодирует объект в байты (сериализация), получатель собирает объект (десериализация). Эту пару называют `SerDe`. Сериализатор Java медленный, потому что объекты раздуты. `Encoder` быстрее по трём причинам:

- Формат Tungsten компактен и лежит вне кучи.
- Сериализация идёт по памяти простой арифметикой адресов и смещений.
- Десериализацию не тормозят паузы `GC`.

## Цена Dataset

Когда `Dataset` попадает в `filter()`, `map()` или `flatMap()` с лямбдой, Spark десериализует данные из Tungsten в объект JVM. Цена мала, но на больших данных и многих запросах она накапливается.

Есть и вторая проблема. Лямбда анонимна: Catalyst не знает, что внутри, и не оптимизирует запрос. В PySpark так же ведёт себя `UDF`. Проверим на Parquet-файле.

```python
@udf(BooleanType())
def over_900(u):  # Catalyst не видит, что внутри
    return u > 900

dsl = df.filter(col("usage") > 900)
fun = df.filter(over_900(col("usage")))
```

Из плана `explain()` печатаем нужные строки:

```text
== plan: DSL
PushedFilters: [IsNotNull(usage), GreaterThan(usage,900)]
== plan: UDF
вызов Python UDF: да
PushedFilters: []
== same result: 102 102
```

Результат одинаков. Но фильтр-выражение Spark передал в источник (`PushedFilters`), а фильтр с `UDF` — нет.

### Как снизить цену

Две стратегии:

1. Писать выражения `DSL` и не злоупотреблять анонимными лямбдами.
2. Строить цепочки так, чтобы `SerDe` было как можно меньше.

В примере книги `Dataset` типа `Person` проходит четыре фильтра: дата рождения, зарплата выше 80 000, фамилия на «J», имя на «D». Если лямбды чередуются с `DSL`, то на каждом переходе от лямбды к выражению Spark делает `SerDe` для `Person`.

![Схема: цепочка из lambda и DSL платит за SerDe на каждом переходе, цепочка из одного DSL остаётся в формате Tungsten](/assets/learning-spark/ch06-lambda-vs-dsl.png)

Сверху — три `SerDe`, снизу — ни одного.

В хорошем варианте все фильтры написаны на `DSL` (`year($"birthDate")`, `$"salary" > 80000`, `startsWith`), и `SerDe` не нужен. Разницу во времени авторы показали в ноутбуке к главе в GitHub-репозитории книги.

## Итоги главы

- Scala и Java делят один типизированный API `Dataset`, а Python и R работают только с `DataFrame`.
- Для `Dataset[T]` нужны `case class` или `JavaBean`, и типы задают заранее.
- Память Spark развивалась от Java-объектов в куче к формату Tungsten вне кучи.
- `Encoder` быстро переводит данные между Tungsten и объектами JVM и быстрее сериализации Java и Kryo.
- Лямбда заставляет десериализовать данные и непрозрачна для Catalyst, поэтому лучше писать `DSL`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Dataset` | Типизированная распределённая коллекция для Scala и Java |
| `encoder` | Переводит данные между форматом Tungsten и объектами JVM |
| Tungsten | Внутренний бинарный формат и физический движок Spark |
| `SerDe` | Сериализация и десериализация: объект в байты и обратно |
| `DSL` | Операторы `DataFrame`, понятные Catalyst |
| `off-heap` | Память вне кучи JVM, `GC` её не трогает |

## Что это значит на практике

- Если условие можно записать выражением (`col("x") > 1`), не пишите лямбду или `UDF`.
- Смотрите `explain()`: `PushedFilters` показывает, что фильтр ушёл в источник.
- Если лямбда нужна, не чередуйте её с `DSL`: каждый переход стоит `SerDe`.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём данные

```sql
CREATE TABLE usage AS
SELECT i AS uid,
       'user-' || lpad(i::VARCHAR, 4, '0') AS uname,
       (i * 7919) % 1000 AS usage
FROM generate_series(0, 999) t(i);
```

### Шаг 2. Проверяем

Должно быть 1000 строк и максимум 999.

```sql
SELECT count(*) AS rows_cnt, max(usage) AS max_usage FROM usage;
```

### Задания

1. Выберите трёх пользователей с самым большим `usage` выше 900 (при равенстве сортируйте по `uid`).
2. Добавьте колонку `cost`: 0,15 за минуту при `usage > 750`, иначе 0,50. Покажите первых трёх по `uid`.
3. Сколько пользователей на тарифе `special` и `regular` и какова стоимость каждого тарифа?

<details><summary>Решение</summary>

```sql
-- 1
SELECT * FROM usage WHERE usage > 900 ORDER BY usage DESC, uid LIMIT 3;
-- 2
SELECT uid, uname, usage,
       CASE WHEN usage > 750 THEN usage * 0.15 ELSE usage * 0.50 END AS cost
FROM usage ORDER BY uid LIMIT 3;
-- 3
SELECT CASE WHEN usage > 750 THEN 'special' ELSE 'regular' END AS tariff,
       count(*) AS users,
       round(sum(CASE WHEN usage > 750 THEN usage * 0.15 ELSE usage * 0.50 END), 2) AS total_cost
FROM usage GROUP BY tariff ORDER BY tariff;
```

В первом запросе — `uid` 321, 642 и 963. Во втором у `uid` 1 `cost` равен 137,85. В третьем — 751 пользователь `regular` на 140 812,50 и 249 пользователей `special` на 32 681,25.

</details>

## Вопросы для самопроверки

1. Почему `Dataset` есть только в Scala и Java?
2. Почему строка «abcd» в JVM занимает 48 байт и как Tungsten решает эту проблему?
3. Что делает `encoder` и чем он лучше сериализации Java?
4. Когда лямбда в `filter()` дороже выражения `DSL` и почему?
5. Как переписать цепочку из лямбд и `DSL`, чтобы убрать лишний `SerDe`?

Предыдущая: [Spark SQL и DataFrame: внешние источники данных](/book-summaries/engineering/learning-spark/05-sql-dataframes-external-sources/). Следующая: [Оптимизация и настройка приложений Spark](/book-summaries/engineering/learning-spark/07-optimizing-and-tuning/).
