---
title: "Max active tasks и Pool"
prev: {"label":"Что такое Pool и зачем нужны слоты?","link":"/interview/questions/airflow/pools/"}
next: {"label":"Что произойдёт с пропущенными интервалами?","link":"/interview/questions/airflow/scheduling/"}
editUrl: false
---

**`max_active_tasks`** — параметр DAG, ограничивающий число одновременно работающих экземпляров задач. **Pool** задаёт бюджет для выбранного ресурса, которым могут пользоваться задачи из нескольких DAG. Учитываются оба ограничения.

| Настройка | Что ограничивает |
| --- | --- |
| `max_active_tasks`, по умолчанию из `[core] max_active_tasks_per_dag` | В Airflow **2.11** считают работающие задачи по всем активным запускам одного DAG. В **3.4** лимит действует в пределах каждого отдельного DAG Run. |
| `max_active_runs` | Сколько запусков одного DAG может быть активно одновременно. Один запуск может содержать много задач. |
| `pool` и `pool_slots` | Сколько слотов могут вместе занять назначенные в пул задачи из любых DAG. |

**Пример.** У DAG два активных запуска, `max_active_tasks=4`. В 2.11 они делят четыре места. В 3.4 каждый запуск может занять до четырёх, итого до восьми при наличии ресурсов. Если все выгрузки используют один пул на три слота и берут по одному слоту, одновременно к источнику пойдут максимум три. [Конфигурация 2.11](https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#max-active-tasks-per-dag) · [Конфигурация 3.4](https://airflow.apache.org/docs/apache-airflow/3.4.0/configurations-ref.html#max-active-tasks-per-dag) · [Пулы](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/pools.html)
