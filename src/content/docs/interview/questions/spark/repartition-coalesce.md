---
title: "Когда выбрать coalesce(), а когда repartition()?"
head:
  - tag: title
    content: "coalesce() и repartition() в Spark | Инжиниринг Данных"
description: "Как уменьшить или увеличить число партиций DataFrame, когда понадобится shuffle и почему одна партиция тормозит запись."
prev: {"label":"Чем отличаются where() и filter()?","link":"/interview/questions/spark/where-filter/"}
next: {"label":"Почему окно без partitionBy() может стать узким местом?","link":"/interview/questions/spark/global-window/"}
tableOfContents: false
editUrl: false
---

После фильтра из 200 партиций осталось мало данных. Если достаточно собрать соседние небольшие порции вместе, подойдёт `coalesce(20)`. Если данные нужно **заново распределить** по задачам или по ключу, используй `repartition()`.

| Вызов DataFrame | Что произойдёт |
| --- | --- |
| `df.coalesce(20)` | Объединит исходные партиции без полного shuffle. Большую партицию на части не разобьёт. Если их было десять, двадцать не получится. |
| `df.repartition(80)` | Перераспределит строки с shuffle. Так можно как увеличить, так и уменьшить число партиций. |
| `df.repartition(80, "shop_id")` | Распределит строки по хешу магазина. Все строки одного магазина попадут в одну партицию. |

`coalesce(1)` перед записью оставляет одну записывающую задачу и может ограничить параллелизм предшествующих узких операций. `repartition(1)` допускает параллельную работу до shuffle, но запись всё равно выполняет одна задача. Один маленький отчёт так записать можно. Годовую выгрузку этим легко замедлить. [DataFrame.coalesce](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.coalesce.html) · [DataFrame.repartition](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.repartition.html)
