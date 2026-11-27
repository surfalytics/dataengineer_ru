---
title: "Что такое UDF и почему для Catalyst это «чёрный ящик»?"
head:
  - tag: title
    content: "UDF и Catalyst в Spark | Инжиниринг Данных"
description: "Что видит Catalyst в Python UDF, чем такой вызов отличается от встроенных функций и что меняет передача данных через Arrow."
prev: {"label":"Как работает Dynamic Partition Pruning (DPP)?","link":"/interview/questions/spark/dynamic-partition-pruning/"}
next: {"label":"Как Apache Arrow ускоряет Pandas UDF?","link":"/interview/questions/spark/pandas-udf-arrow/"}
tableOfContents: false
editUrl: false
---

**UDF (user-defined function)** — функция, которую разработчик добавил для обработки значения или набора значений. Для обычной Python UDF Spark знает входные колонки и объявленный тип результата. Код внутри функции исполняет Python worker. Catalyst не может раскрыть произвольный Python-код и переписать его как SQL-выражение.

Например, код магазина нужно очистить от пробелов и привести к нижнему регистру. Выражение `F.lower(F.trim("shop_code"))` целиком понятно Spark. Если завернуть те же действия в Python UDF, появится граница между JVM и Python. Данные нужно передать исполнителю Python и получить результат обратно. Фильтры, независимые от UDF, Catalyst по-прежнему может оптимизировать.

В `explain("formatted")` обычную Python UDF часто выдают узлы `BatchEvalPython`, а варианты с Arrow — `ArrowEvalPython`. Pandas UDF обрабатывает данные пачками и может сократить расходы на передачу. Смысл пользовательской функции при этом по-прежнему скрыт от Catalyst. [Пользовательские функции в PySpark](https://spark.apache.org/docs/4.1.1/api/python/user_guide/udfandudtf.html)
