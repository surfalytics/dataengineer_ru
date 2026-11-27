---
title: "Что такое RDD и как он восстанавливает данные?"
head:
  - tag: title
    content: "RDD и lineage в Spark | Инжиниринг Данных"
description: "Что означают неизменяемость, партиции и lineage в Spark. Как пересчитывается утерянная партиция и когда пригодится RDD API."
prev: {"label":"Как работает Spark Connect?","link":"/interview/questions/spark/spark-connect/"}
next: {"label":"Что Spark пересчитывает при потере executor?","link":"/interview/questions/spark/executor-loss/"}
tableOfContents: false
editUrl: false
---

**RDD (Resilient Distributed Dataset)** — распределённая неизменяемая коллекция. Spark знает, на какие партиции она разделена, от каких данных зависит каждая партиция и как её вычислить. `map` или `filter` создают новый RDD. Исходный остаётся доступен.

Представь файл с событиями. Сначала читаем строки, потом оставляем ошибки. Если executor потеряет уже вычисленную партицию с ошибками, Spark сможет заново прочитать нужную часть доступного источника и повторить фильтрацию. История этих зависимостей называется **lineage**. После shuffle для восстановления могут понадобиться блоки нескольких предыдущих задач.

В классическом PySpark можно обработать произвольные объекты через `rdd.mapPartitions(...)`. Это пригодится для существующего RDD-кода или собственного алгоритма обработки партиции. Для таблицы заказов удобнее DataFrame: у него есть схема, а Catalyst видит колонки и встроенные выражения и может оптимизировать запрос. [Руководство по RDD](https://spark.apache.org/docs/4.1.1/rdd-programming-guide.html#resilient-distributed-datasets-rdds)
