---
title: "Python, Bash, Kubernetes и Spark"
prev: {"label":"Что стоит передавать через XCom?","link":"/interview/questions/airflow/xcom/"}
next: {"label":"Когда запускать другой DAG, а когда ждать его или внешние данные?","link":"/interview/questions/airflow/dependencies/"}
editUrl: false
---

**Оператор** описывает, что сделает экземпляр задачи. Например, при CeleryExecutor задача может исполняться на Celery-воркере и оттуда запустить отдельный Kubernetes pod.

| Оператор | Что он делает | Пример |
| --- | --- | --- |
| `PythonOperator` или `@task` | Вызывает Python-функцию в окружении исполнения задачи. | Проверить ответ API, посчитать границу выгрузки. |
| `BashOperator` | Запускает shell-команду и отслеживает её завершение. | Вызвать установленную CLI-утилиту. |
| `KubernetesPodOperator` | Через Kubernetes API создаёт pod с выбранным образом, командой и ресурсами. | Запустить Rust-парсер или dlt-загрузчик с собственными зависимостями и несколькими потоками для I/O. |
| `SparkSubmitOperator` / `SparkKubernetesOperator` | Первый вызывает `spark-submit`. Второй работает с ресурсом `SparkApplication` в Kubernetes при установленном Spark Operator. | Передать кластеру Spark задачу трансформации. Вычисления координирует Spark driver, данные обрабатывают Spark executors. |

**Граница ресурсов.** Внешнему pod можно задать собственные CPU и память. Параллелизм внутри контейнера выбирает приложение. В режиме ожидания без deferral задача Airflow при этом продолжает занимать worker slot. `KubernetesPodOperator` можно использовать и без `KubernetesExecutor`.

[PythonOperator](https://airflow.apache.org/docs/apache-airflow-providers-standard/stable/operators/python.html) · [BashOperator](https://airflow.apache.org/docs/apache-airflow-providers-standard/stable/operators/bash.html) · [Операторы Kubernetes](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html) · [Операторы Spark](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/operators.html)
