---
title: "Чем cache() отличается от persist()?"
head:
  - tag: title
    content: "cache() и persist() в Spark | Инжиниринг Данных"
description: "Какие данные кешируют DataFrame и RDD, как выбрать уровень хранения и когда появляются первые сохранённые партиции."
prev: {"label":"Что такое Broadcast Variable?","link":"/interview/questions/spark/broadcast-variable/"}
next: {"label":"Почему повторный Action снова вычисляет DataFrame?","link":"/interview/questions/spark/repeated-actions/"}
tableOfContents: false
editUrl: false
---

**`cache()` — короткая форма `persist()` с уровнем хранения по умолчанию.** Оба вызова помечают данные для повторного использования. Партиция попадает в кеш, когда действие впервые её вычислит. Например, `show(5)` может заполнить только часть кеша.

| Что кешируем в PySpark | Уровень по умолчанию |
| --- | --- |
| DataFrame | `MEMORY_AND_DISK_DESER`. Блоки хранятся в памяти, а для тех, которым там не хватило места, допускается диск. |
| RDD | `MEMORY_ONLY`. Утраченный блок при необходимости вычисляется заново по lineage. Python-объекты в PySpark RDD при хранении сериализуются. |

`persist()` нужен, когда хочешь задать другой уровень, например `df.persist(StorageLevel.DISK_ONLY)`. Полезный случай — дорогой JOIN, результат которого читают два следующих отчёта. Первый отчёт заполняет кеш по мере чтения, второй может взять уже вычисленные блоки.

Во вкладке **Storage** смотри, сколько партиций сохранено и сколько места занято в памяти и на диске. В плане повторного запроса ищи `InMemoryTableScan`. [DataFrame.persist](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.persist.html) · [Хранение RDD](https://spark.apache.org/docs/4.1.1/rdd-programming-guide.html#rdd-persistence)
