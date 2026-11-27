---
title: "Как работает Dynamic Resource Allocation?"
head:
  - tag: title
    content: "Dynamic Resource Allocation в Spark | Инжиниринг Данных"
description: "Как Spark меняет число executors по очереди задач и по времени простоя, какие границы задать и как сохранить доступ к shuffle-данным."
prev: {"label":"В каких случаях драйвер может упасть по памяти?","link":"/interview/questions/spark/driver-oom/"}
next: {"label":"Почему у Spark в Kubernetes растёт память при длительной загрузке?","link":"/interview/questions/spark/kubernetes-allocation/"}
tableOfContents: false
editUrl: false
---

**Dynamic Resource Allocation**, или динамическое выделение ресурсов, позволяет одному Spark-приложению менять число executors в ходе работы. Если задачи ждут свободных слотов достаточно долго, драйвер запрашивает дополнительные executors. Когда они простаивают, Spark может освободить их. На Kubernetes это появление и удаление executor pods.

| Настройка | Что задаёт |
| --- | --- |
| `spark.dynamicAllocation.enabled` | Включает динамическое выделение executors. |
| `minExecutors`, `initialExecutors`, `maxExecutors` в группе `spark.dynamicAllocation` | Нижнюю, начальную и верхнюю границы пула. При старте Spark учитывает и большее явно заданное `spark.executor.instances`. |
| `schedulerBacklogTimeout`, `executorIdleTimeout` | Сколько ждать при очереди задач до запроса дополнительных ресурсов и сколько простаивать до освобождения. Для executors с кешем есть отдельный `cachedExecutorIdleTimeout`. |

Для сохранности shuffle-данных нужен поддерживаемый механизм. На Kubernetes распространён **shuffle tracking**: Spark отслеживает нужные промежуточные блоки и может удержать создавший их executor. Поэтому число pods не обязано падать до минимума сразу после стадии.

Динамика меняет **число executors**. Количество слотов внутри каждого задают ресурсы executor и одной задачи. Если очередь создаёт единственная горячая партиция, дополнительные pods сами по себе эту задачу не ускорят. [Динамическое выделение ресурсов](https://spark.apache.org/docs/4.1.1/job-scheduling.html#dynamic-resource-allocation)
