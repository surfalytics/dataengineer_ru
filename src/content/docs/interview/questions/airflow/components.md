---
title: "Компоненты Airflow 2 и 3"
prev: {"label":"Все подтемы Airflow","link":"/interview/questions/airflow/"}
next: {"label":"Кто исполняет задачи и чем различаются executors?","link":"/interview/questions/airflow/executors/"}
editUrl: false
---

Путь задачи удобно проследить от файла до результата. **DAG Processor** читает описание DAG. **Scheduler** решает, какие экземпляры задач готовы. **Executor** передаёт их на исполнение. Выбранный воркер запускает код задачи. Состояния DAG Run и Task Instance сохраняются в **metadata DB**.

| Компонент | Airflow 2.11 | Airflow 3.x |
| --- | --- | --- |
| Интерфейс и API | `webserver` обслуживает UI и REST API. | `api-server` обслуживает UI, публичный REST API и Execution API, через который задачи взаимодействуют с Airflow. |
| Разбор DAG | По умолчанию процессами парсинга управляет scheduler. DAG Processor можно вынести отдельно. | `dag-processor` запускается отдельно, читает DAG из DAG bundles и записывает сериализованные описания. |
| Планирование и исполнение | Scheduler проверяет расписание, зависимости и лимиты. Стратегия executor работает внутри scheduler, сами задачи могут исполняться локально или удалённо. | Разделение сохраняется. Для выполнения задач Task SDK взаимодействует с Airflow через Execution API. |
| Metadata DB | Хранит состояния, описания и служебные метаданные. Компоненты 2.x, включая исполнение задач, могли обращаться к ней напрямую. | По-прежнему хранит метаданные. Коду задач для штатной работы доступ к этой БД не требуется. |
| Triggerer | Обслуживает асинхронные триггеры для отложенных задач. | Та же роль. Нужен, если используются deferrable-операторы или сенсоры. |

Состав **воркеров** зависит от executor. Для Celery нужны воркеры и брокер сообщений, для KubernetesExecutor создаются поды задач. Redis и Kubernetes не являются обязательными частями любого развёртывания. [Архитектура 2.11](https://airflow.apache.org/docs/apache-airflow/2.11.0/core-concepts/overview.html) · [Архитектура 3.x](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html) · [Переход на 3.x](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading_to_airflow3.html)
