---
title: "Executors"
prev: {"label":"Из каких компонентов состоит Airflow 2 и что изменилось в Airflow 3?","link":"/interview/questions/airflow/components/"}
next: {"label":"Что такое Pool и зачем нужны слоты?","link":"/interview/questions/airflow/pools/"}
editUrl: false
---

**Executor** определяет, куда scheduler отправит готовый экземпляр задачи. Один настроенный тип executor может обслуживать много задач и воркеров.

| Executor | Где исполняется задача | Когда подходит |
| --- | --- | --- |
| `LocalExecutor` | В локальном процессе на машине scheduler. Несколько задач могут выполняться параллельно. | Небольшая установка с достаточными ресурсами одного узла. |
| `CeleryExecutor` | Через брокер задача попадает в очередь, которую обслуживают долгоживущие Celery-воркеры. | Поток коротких задач, очереди для разных типов нагрузки, масштабирование числом воркеров и их concurrency. |
| `KubernetesExecutor` | Для экземпляра задачи создаётся отдельный pod. | Нужны изоляция, разные образы или ресурсы задач. Учитывайте время запуска pod и доступную ёмкость кластера. |
| `SequentialExecutor` в Airflow 2.x | Выполняет по одной задаче за раз. | Можно встретить в старой локальной установке. |

Начиная с **2.10** в одном развёртывании можно настроить несколько executors и выбирать их для задач. Например, короткие задачи отправлять в Celery, а задачи с особыми ресурсами — в Kubernetes. На интервью полезно уточнить, какой показатель имеется в виду — типы executors, число Celery-воркеров или количество одновременно работающих подов.

**Что с многопоточностью?** Executor и настройки Airflow ограничивают параллелизм экземпляров задач. Один экземпляр задачи может занимать один слот Airflow и при этом выполнять, например, четыре сетевых запроса через Python `ThreadPoolExecutor`. Их полезное число определяется ресурсами процесса, квотами контейнера и возможностями источника. Отдельный pod удобен, когда нужны другой образ, лимиты или зависимости. [Executors и multi-executor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html) · [CeleryExecutor](https://airflow.apache.org/docs/apache-airflow-providers-celery/stable/celery_executor.html) · [KubernetesExecutor](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/kubernetes_executor.html) · [Пул потоков Python](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
