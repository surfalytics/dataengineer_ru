---
title: "Как Apache Arrow ускоряет Pandas UDF?"
head:
  - tag: title
    content: "Apache Arrow и Pandas UDF в Spark | Инжиниринг Данных"
description: "Как колоночный обмен между JVM и Python и обработка pandas Series пачками снижают накладные расходы и когда ускорения можно не получить."
prev: {"label":"Что такое UDF и почему для Catalyst это «чёрный ящик»?","link":"/interview/questions/spark/udf/"}
next: {"label":"Как работает Adaptive Query Execution (AQE)?","link":"/interview/questions/spark/aqe/"}
tableOfContents: false
editUrl: false
---

**Pandas UDF ускоряет обмен данными между JVM и Python и позволяет обработать целую пачку значений одним вызовом.** Допустим, к цене каждого заказа нужно прибавить 10 %.

1. Executor собирает значения колонки в батч Apache Arrow. Колоночный формат позволяет передать типизированные буферы из JVM в Python с меньшими затратами на преобразование множества отдельных объектов.
2. В скалярную Pandas UDF приходит `pandas.Series`. Функция вызывается для батча и умножает всю серию на `1.10` векторной операцией. Возвращается серия той же длины.
3. Результат передаётся обратно в JVM через Arrow, и Spark продолжает обработку следующего батча.

У обычной скалярной Python UDF код функции вызывается для каждого значения, даже если Spark передаёт строки пачками. Arrow сокращает затраты на обмен, а векторная операция устраняет Python-цикл по элементам. Если внутри Pandas UDF снова написать цикл или `Series.apply` с тяжёлой Python-функцией на каждое значение, часть выигрыша пропадёт.

В этом примере встроенное `F.col("price") * 1.10` вообще не требует перехода в Python. Pandas UDF полезнее, когда нужна функция из pandas или NumPy, которую сложно выразить средствами Spark SQL. Проверь в плане `ArrowEvalPython` и сравни время полного действия на одинаковых данных. Памяти Python worker должно хватать на входной батч и временные массивы. [Apache Arrow и Pandas UDF в PySpark](https://spark.apache.org/docs/4.1.1/api/python/tutorial/sql/arrow_pandas.html)
