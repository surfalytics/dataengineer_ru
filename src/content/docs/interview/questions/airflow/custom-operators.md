---
title: "Наследование операторов"
prev: {"label":"Когда запускать другой DAG, а когда ждать его или внешние данные?","link":"/interview/questions/airflow/dependencies/"}
next: {"label":"Как TaskFlow строит зависимости из Python-функций?","link":"/interview/questions/airflow/taskflow/"}
editUrl: false
---

При обычном запуске оператор выполняет работу в **`execute(self, context)`**. Конструктор `__init__` сохраняет параметры. Создание pod и сетевые вызовы выполняйте во время работы задачи. Конструктор может срабатывать при каждом разборе DAG-файла.

Допустим, `KuberSparkOperator` — обёртка вашей команды, которая уже умеет отправлять Spark-задание. В наследнике нужно добавить метку команды и оставить родителю отправку и отслеживание. Если вы переопределяете `execute`, подготовьте метку, затем вызовите **`return super().execute(context)`**. Возврат сохраняет результат родителя. Без делегирования метод наследника может успешно завершиться, хотя Spark-задание никто не отправил.

**Обязателен ли вызов именно в последней строке?** Это зависит от контракта родителя. Если меняются только параметры, можно унаследовать `execute` без изменений. Если нужны действия после родителя, сохраните его результат и верните в конце. Для deferrable-оператора код после `defer` в этом вызове не продолжится — возобновление идёт через указанный метод, часто `execute_complete`.

В официальном Kubernetes provider класс называется `SparkKubernetesOperator`. В его реализации можно посмотреть реальный пример делегирования через `super().execute(context)`. [Создание операторов](https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html) · [Реализация SparkKubernetesOperator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_modules/airflow/providers/cncf/kubernetes/operators/spark_kubernetes.html)
