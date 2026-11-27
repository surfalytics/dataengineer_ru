---
title: "Executor упал по OOM. Как найти причину?"
head:
  - tag: title
    content: "Диагностика Executor OOM в Spark | Инжиниринг Данных"
description: "Как различить Java heap space, direct memory, ошибку Python и OOMKilled на Kubernetes и почему увеличение memoryOverhead помогает только в части случаев."
prev: {"label":"Как устроена память executor?","link":"/interview/questions/spark/executor-memory/"}
next: {"label":"В каких случаях драйвер может упасть по памяти?","link":"/interview/questions/spark/driver-oom/"}
tableOfContents: false
editUrl: false
---

**Начни с причины завершения конкретного executor.** В Spark UI найди неудачную стадию, task и Executor ID. Затем открой логи этого executor и события его pod. Сообщение драйвера `ExecutorLostFailure` говорит, кого потеряли, но причины могут быть разными.

| Что нашёл | Что проверить | Что менять по результату |
| --- | --- | --- |
| `OutOfMemoryError: Java heap space` или `GC overhead limit exceeded` | Посмотри пиковое заполнение heap, GC, самые большие shuffle-партиции, кеш и число одновременных задач. | Уменьши объём одной задачи, устрани skew, освободи кеш или сократи число задач на JVM. Если рабочему набору действительно тесно, увеличь `spark.executor.memory`. |
| `OutOfMemoryError: Direct buffer memory` либо Python `MemoryError` | Определи процесс и операцию. Проверь нативные буферы, размеры батчей Arrow, размер группы в pandas UDF и память Python workers. | Уменьши батч или группу там, где это возможно, и параллельность процессов. Проверь лимит direct memory или отдельный бюджет Python, если они заданы. |
| В Kubernetes причина `OOMKilled` | Сверь пик памяти контейнера с его лимитом, временем сбоя и логами. Возможна сумма heap, Python и native даже при свободной части JVM heap. Код 137 без причины завершения сам по себе OOM не доказывает. | Сократи потребителей памяти или увеличь соответствующую часть бюджета контейнера. Проверь, что новый лимит действительно попал в запущенный pod. |

**Почему `spark.executor.memoryOverhead` мог не помочь?** Он увеличивает бюджет контейнера сверх heap. Максимальный размер Java heap от этого не вырастет. Если одна горячая партиция каждый раз валит одну и ту же задачу, больший запас может только отодвинуть падение. Если упал драйвер, изменения настроек executor вообще не затронут проблемный процесс.

Повтори тот же объём данных и сравни Max/Median чтения, GC, spill и число повторов задач. [Диагностика приложений на Kubernetes](https://spark.apache.org/docs/4.1.1/running-on-kubernetes.html#debugging)
