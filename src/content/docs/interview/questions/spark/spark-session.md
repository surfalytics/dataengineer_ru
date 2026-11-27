---
title: "Что такое SparkSession?"
head:
  - tag: title
    content: "SparkSession | Инжиниринг Данных"
description: "Как открыть сессию Spark, создать DataFrame, выполнить SQL и получить доступ к SparkContext в классическом PySpark."
prev: {"label":"Как запускается Spark-приложение","link":"/interview/questions/spark/application-launch/"}
next: {"label":"Как работает Spark Connect?","link":"/interview/questions/spark/spark-connect/"}
tableOfContents: false
editUrl: false
---

**SparkSession** — точка входа для работы с таблицами, DataFrame и SQL. В PySpark её обычно называют `spark`. Через одну сессию можно прочитать заказы из Parquet, зарегистрировать их как временное представление и выполнить запрос.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
orders = spark.read.parquet(orders_path)
orders.createOrReplaceTempView("orders")
spark.sql("SELECT COUNT(*) FROM orders").show()
```

В классическом Spark за связь приложения с кластером отвечает **SparkContext**. Он доступен как `spark.sparkContext` и нужен, например, чтобы создать RDD или broadcast-переменную. Для обычного SQL достаточно сессии.

У одного приложения может быть несколько сессий. Вызов `spark.newSession()` создаёт отдельные SQL-настройки и временные представления. При этом сессии используют общий SparkContext, executors и кеш таблиц. [SparkSession](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.html)
