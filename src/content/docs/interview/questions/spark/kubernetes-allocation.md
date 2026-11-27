---
title: "Почему в одном длинном запуске растёт число pods или расход памяти?"
head:
  - tag: title
    content: "Аллокации в Spark на Kubernetes | Инжиниринг Данных"
description: "Как отделить рост числа executors от роста памяти внутри pod при помесячной загрузке года и как задать пределы CPU и динамического пула."
prev: {"label":"Как работает Dynamic Resource Allocation?","link":"/interview/questions/spark/dynamic-allocation/"}
next: false
tableOfContents: false
editUrl: false
---

Представь один запуск Spark на весь год. Цикл читает январь, записывает его, затем переходит к февралю. К июню кластер заметно вырос. Первым делом выясни, **что именно растёт между месяцами**: число executor pods, число потоков внутри процесса или память уже работающего pod. Для этих случаев нужны разные настройки.

| Что наблюдаешь | Как проверить и чем управлять |
| --- | --- |
| Стало больше executor pods | Сопоставь вкладку Executors с очередью задач и числом живых pods. При динамическом выделении задай `spark.dynamicAllocation.maxExecutors`. Для фиксированного пула отключи динамику и задай `spark.executor.instances`. Проверь также, что месяцы выполняются в одном приложении, по одному Application ID. |
| Pods столько же, но потоки спорят за CPU | `spark.executor.cores` задаёт ядра, по которым Spark планирует задачи. `spark.kubernetes.executor.request.cores` задаёт CPU request для размещения pod, `spark.kubernetes.executor.limit.cores` — потолок CPU контейнера. Библиотеки Python и JVM могут создавать собственные пулы потоков, поэтому проверь число потоков и CPU throttling. |
| Pods столько же, но память от месяца к месяцу растёт | Сравни heap и память контейнера после каждой записи. Проверь забытые кеши, broadcast-переменные, накопленные Python-результаты и растущие планы. Закрывай их жизненный цикл. `maxExecutors` не освободит эти объекты. |

**Откуда берётся ощущение, что Spark видит все CPU Kubernetes?** Планировщик Spark берёт число слотов из ресурсов, назначенных executors. На Kubernetes по умолчанию у executor одно ядро для планирования. Если у контейнера не задан CPU limit, система может позволить процессу использовать больше CPU **своего узла**, чем его request. Сколько процессоров увидит JVM или библиотека, зависит также от cgroups, ограничений контейнера и среды выполнения. Это разные величины.

Например, при потолке **8 executors**, `spark.executor.cores=2` и `spark.task.cpus=1` приложение получит до **16 обычных задач одновременно**, когда все pods запустятся. Если нагрузка требует жёсткого CPU-бюджета, отдельно проверь фактические requests и limits созданных pods. Историю завершённых executor IDs отличай от количества pods, которые живы прямо сейчас. [CPU в Spark на Kubernetes](https://spark.apache.org/docs/4.1.1/running-on-kubernetes.html#spark-properties) · [Настройки динамического пула](https://spark.apache.org/docs/4.1.1/configuration.html#dynamic-allocation)
