---
title: "Как работает Spark Connect?"
head:
  - tag: title
    content: "Spark Connect | Инжиниринг Данных"
description: "Где работают клиент и драйвер Spark Connect, как передаётся логический план и куда возвращается результат collect()."
prev: {"label":"Что такое SparkSession?","link":"/interview/questions/spark/spark-session/"}
next: {"label":"Что такое RDD и как он восстанавливает данные?","link":"/interview/questions/spark/rdd/"}
tableOfContents: false
editUrl: false
---

**Spark Connect** позволяет работать с удалённым Spark из ноутбука или приложения. Ты пишешь привычный DataFrame-код на клиенте. Клиент собирает неразрешённый логический план и передаёт его по gRPC серверу рядом с драйвером. Сервер проверяет и оптимизирует план, а задачи выполняются на executors.

```python
spark = SparkSession.builder.remote("sc://spark-host:15002").getOrCreate()
paid = spark.table("orders").where("status = 'paid'")
paid.groupBy("shop_id").count().show()
```

Локальному Python-клиенту для такой работы не нужна собственная JVM с драйвером. Библиотеки и права, нужные для чтения таблицы, должны быть доступны на стороне сервера. Когда вызываешь `collect()` или `toPandas()`, строки передаются клиенту, и большой результат может переполнить память ноутбука.

Через Connect доступны поддерживаемые операции DataFrame и SQL. Классические `spark.sparkContext`, RDD API и прямой доступ к JVM драйвера через `_jvm` здесь недоступны. [Архитектура Spark Connect](https://spark.apache.org/docs/4.1.1/spark-connect-overview.html)
