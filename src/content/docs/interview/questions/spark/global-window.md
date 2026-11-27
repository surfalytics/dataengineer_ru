---
title: "Почему окно без partitionBy() может стать узким местом?"
head:
  - tag: title
    content: "Окна без partitionBy() в Spark | Инжиниринг Данных"
description: "Как глобальное окно row_number собирает строки в одной партиции, как увидеть Exchange SinglePartition и когда добавление ключа изменяет результат."
prev: {"label":"Когда выбрать coalesce(), а когда repartition()?","link":"/interview/questions/spark/repartition-coalesce/"}
next: {"label":"Что такое Catalyst и как он работает с DataFrame API?","link":"/interview/questions/spark/catalyst/"}
tableOfContents: false
editUrl: false
---

**Без `Window.partitionBy(...)` все строки для окна принадлежат одной группе.** Например, чтобы присвоить каждому заказу сквозной номер по времени, Spark должен сопоставить его место с заказами из других партиций. Для обычного глобального `row_number()` оконный оператор обрабатывает весь вход в одной задаче. Предыдущие стадии по-прежнему могут выполняться параллельно.

```python
from pyspark.sql import Window, functions as F

by_time = Window.orderBy("created_at", "order_id")
ranked = orders.withColumn("position", F.row_number().over(by_time))
ranked.explain("formatted")
```

В плане для распределённого входа ищи `Exchange SinglePartition`, затем `Sort` и `Window`. На больших данных одна задача долго сортирует строки, может писать временные данные на диск или исчерпать память. Это риск, а не обязательное падение.

Если нужен **номер заказа внутри магазина**, окно можно определить как `Window.partitionBy("shop_id").orderBy("created_at", "order_id")`. Тогда счёт начинается заново для каждого магазина, и разные магазины можно обрабатывать параллельно. Если нужен **общий** номер по всей таблице, такое изменение даст другой ответ. Если нужны только десять самых ранних заказов, достаточно `orderBy("created_at", "order_id").limit(10)`. [Оконные функции Spark SQL](https://spark.apache.org/docs/4.1.1/sql-ref-syntax-qry-select-window.html)
