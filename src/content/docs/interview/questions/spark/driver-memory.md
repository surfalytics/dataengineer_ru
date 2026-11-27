---
title: "Как устроена память драйвера?"
head:
  - tag: title
    content: "Память драйвера в Spark | Инжиниринг Данных"
description: "Что занимает JVM heap и память вне heap в driver pod PySpark и как оценить ресурсы для планирования, broadcast и локальных результатов."
prev: {"label":"Сколько ресурсов дать драйверу и executors?","link":"/interview/questions/spark/cluster-sizing/"}
next: {"label":"Как устроена память executor?","link":"/interview/questions/spark/executor-memory/"}
tableOfContents: false
editUrl: false
---

В классическом PySpark на Kubernetes в режиме `cluster` в driver pod работают JVM драйвера и Python-процесс приложения. **Лимит контейнера включает больше, чем `spark.driver.memory`.** На схеме показаны основные потребители памяти, площади блоков условны.

![В driver pod JVM heap хранит планы, метаданные задач и результаты. За пределами heap память потребляют Python и нативные структуры JVM.](/assets/interview/spark-driver-memory.webp)

| Где расходуется память | Что там находится |
| --- | --- |
| JVM heap — `spark.driver.memory` | Планы запросов, метаданные заданий и задач, подготовка broadcast, данные при сборе результатов. Для heap важны пики во время этих операций. |
| Вне heap — запас `spark.driver.memoryOverhead` | Нативная память JVM, direct buffers, стеки потоков и отдельный процесс Python. После `toPandas()` именно Python может удерживать основную часть результата. |

Для пробного запуска в `cluster` режиме конфигурация **4 ГиБ heap + 2 ГиБ overhead** даёт драйверному контейнеру бюджет **6 ГиБ**. Это пример расчёта, конкретные значения выбирай по пику памяти контейнера и занятому heap на репрезентативной загрузке. Отдельно проверь момент подготовки самого большого broadcast. Задавай память драйвера при отправке приложения, пока JVM ещё не запущена. [Память драйвера в конфигурации Spark](https://spark.apache.org/docs/4.1.1/configuration.html#application-properties)
