---
title: "TaskFlow API"
prev: {"label":"Как расширить оператор и сохранить запуск родительской задачи?","link":"/interview/questions/airflow/custom-operators/"}
next: {"label":"Когда генерировать DAG из YAML, API или БД?","link":"/interview/questions/airflow/dag-generation/"}
editUrl: false
---

**TaskFlow API** позволяет описать DAG обычными функциями с декораторами. `@dag` описывает граф, `@task` превращает функцию в задачу. В 2.x декораторы обычно импортируют из `airflow.decorators`, в 3.x публичный интерфейс авторов DAG — `airflow.sdk`.

Представим выражение `load(extract())` при построении DAG. Вызов `extract()` создаёт задачу и возвращает **XComArg** — ссылку на будущий результат. Передача этой ссылки в `load` создаёт зависимость. Уже во время запуска `extract` записывает файл и возвращает его путь, а `load` получает этот путь и читает файл.

TaskFlow удобен для цепочек Python-задач и совместим с обычными операторами. Если вернуть большой список строк, он пойдёт через XCom. Для такой задачи лучше вернуть адрес набора данных. [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html) · [XCom](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html)
