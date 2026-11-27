---
title: "Как устроена память executor?"
head:
  - tag: title
    content: "Память executor в Spark | Инжиниринг Данных"
description: "Где находятся execution и storage memory, почему Python workers и direct buffers расходуют память вне heap и что входит в бюджет executor pod."
prev: {"label":"Как устроена память драйвера?","link":"/interview/questions/spark/driver-memory/"}
next: {"label":"Executor упал по OOM. Как найти причину?","link":"/interview/questions/spark/executor-oom/"}
tableOfContents: false
editUrl: false
---

**Executor** выполняет несколько задач в общей JVM. У каждой задачи есть свои рабочие данные, а кеш и broadcast могут использоваться несколькими задачами. На схеме — обычный PySpark executor без отдельно настроенной Spark off-heap memory.

![В executor pod часть JVM heap выделяется под unified memory для execution и storage. Остальная heap содержит другие объекты JVM. Вне heap работают Python workers и используются нативные буферы.](/assets/interview/spark-executor-memory.webp)

**Внутри `spark.executor.memory`.** После служебного резерва часть heap отводится под общую область Spark. По умолчанию `spark.memory.fraction` составляет 0,6 от heap за вычетом 300 МиБ. Внутри этой области execution memory используется для сортировок, агрегатов и JOIN, а storage memory — для хранения блоков, например кеша. Граница между execution и storage подвижна. Остальная heap нужна для пользовательских объектов, метаданных и запаса.

**Вне heap.** Прямые сетевые буферы, нативные библиотеки и процессы Python тоже расходуют память контейнера. На Kubernetes его бюджет складывается из `spark.executor.memory`, `spark.executor.memoryOverhead`, отдельно настроенной `spark.memory.offHeap.size` при включённом off-heap и `spark.executor.pyspark.memory`, если она задана. Без отдельного бюджета Python его расход должен укладываться в overhead.

Например, четыре одновременно работающие Python-задачи могут держать четыре рабочих набора данных. Смотреть только на JVM heap в этот момент недостаточно — сопоставь его с фактической памятью контейнера. [Организация памяти Spark](https://spark.apache.org/docs/4.1.1/tuning.html#memory-management-overview) · [Настройки executor](https://spark.apache.org/docs/4.1.1/configuration.html#application-properties)
