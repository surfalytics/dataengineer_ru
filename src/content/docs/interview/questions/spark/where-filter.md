---
title: "Чем отличаются where() и filter()?"
head:
  - tag: title
    content: "where() и filter() в Spark | Инжиниринг Данных"
description: "Сравниваем два способа фильтрации одного DataFrame, условие Column, SQL-строку и обработку NULL в PySpark."
prev: {"label":"Job -> Stages -> Task","link":"/interview/questions/spark/execution/"}
next: {"label":"Когда выбрать coalesce(), а когда repartition()?","link":"/interview/questions/spark/repartition-coalesce/"}
tableOfContents: false
editUrl: false
---

**В DataFrame API `where()` — псевдоним `filter()`.** Оба метода возвращают новый DataFrame со строками, у которых условие истинно. Выбор имени не меняет производительность. Оба принимают SQL-выражение строкой или объект Column.

```python
from pyspark.sql import functions as F

paid_sql = orders.where("status = 'paid'")
paid_col = orders.filter(F.col("status") == "paid")
```

В обоих случаях останутся оплаченные заказы. Если `status` равен `NULL`, сравнение даст неопределённый результат, и строка тоже отсеется. Для отбора таких строк есть `F.col("status").isNull()`.

Операция ленивая. Чтобы увидеть фильтр, вызови `paid_col.explain("formatted")`. Чтобы запустить чтение и увидеть строки, вызови `paid_col.show(5)`. [DataFrame.filter](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.filter.html)
