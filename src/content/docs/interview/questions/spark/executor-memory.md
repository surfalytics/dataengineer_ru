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

**Внутри `spark.executor.memory`.** Сначала Spark исключает из расчёта служебный резерв 300 МиБ. На схеме он входит в область за пределами Unified memory. По умолчанию под Unified memory выделяется 60 % оставшейся heap (`spark.memory.fraction=0.6`). Внутри этой области execution memory используется для сортировок, агрегатов и JOIN, а storage memory — для хранения блоков, например кеша. Обе области могут занимать свободное место. Когда execution нужна память, она может вытеснить кеш до защищённого порога storage. По умолчанию `spark.memory.storageFraction=0.5` защищает занятые кешем блоки в пределах половины **unified memory**. Storage не может вытеснять данные, уже занятые execution. Остальная heap нужна для пользовательских объектов, метаданных и запаса.

**Вне heap.** Прямые сетевые буферы, нативные библиотеки и процессы Python тоже расходуют память контейнера. На Kubernetes его бюджет складывается из `spark.executor.memory`, `spark.executor.memoryOverhead`, отдельно настроенной `spark.memory.offHeap.size` при включённом off-heap и `spark.executor.pyspark.memory`, если она задана. Без отдельного бюджета Python его расход должен укладываться в overhead.

Для PySpark-приложения, отправленного в Kubernetes как Python-задача, Spark по умолчанию рассчитывает overhead как **40 %** размера heap, для JVM-приложения — **10 %**. Стандартный минимум — **384 МиБ**. Это запас для контейнера, а не измеренная доля Python. Явное значение `spark.executor.memoryOverhead` заменяет расчёт по коэффициенту. [Настройки памяти в Kubernetes](https://spark.apache.org/docs/4.1.1/running-on-kubernetes.html#spark-properties)

Например, четыре одновременно работающие Python-задачи могут держать четыре рабочих набора данных. Смотреть только на JVM heap в этот момент недостаточно — сопоставь его с фактической памятью контейнера. [Организация памяти Spark](https://spark.apache.org/docs/4.1.1/tuning.html#memory-management-overview) · [Настройки executor](https://spark.apache.org/docs/4.1.1/configuration.html#application-properties)
