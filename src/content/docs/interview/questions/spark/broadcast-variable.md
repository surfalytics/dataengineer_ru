---
title: "Что такое Broadcast Variable?"
head:
  - tag: title
    content: "Broadcast Variable в Spark | Инжиниринг Данных"
description: "Как раздать доступный только для чтения объект нескольким задачам в классическом PySpark и когда освободить broadcast-переменную."
prev: {"label":"Почему broadcast() может не дать BroadcastHashJoin?","link":"/interview/questions/spark/broadcast-hint-failure/"}
next: {"label":"Чем cache() отличается от persist()?","link":"/interview/questions/spark/cache-persist/"}
tableOfContents: false
editUrl: false
---

**Broadcast Variable** — доступная только для чтения копия объекта, который драйвер распространяет для использования в задачах. Допустим, функции обработки событий регулярно нужен один и тот же маленький словарь кодов. Его можно один раз объявить через `SparkContext.broadcast`, а внутри задач читать из `.value`.

```python
sc = spark.sparkContext
cities = sc.broadcast({1: "Омск", 2: "Пермь"})
try:
    result = sc.parallelize([2, 1, 2]).map(lambda key: cities.value[key]).collect()
finally:
    cities.destroy()
```

Здесь результат маленький: `["Пермь", "Омск", "Пермь"]`. Задачи переиспользуют распространённые данные. В PySpark у процессов Python могут быть отдельные десериализованные копии, что важно для большого словаря. Изменять словарь и ждать, что изменения появятся у других задач, нельзя.

`unpersist()` освобождает копии на executors и допускает повторную рассылку. `destroy()` завершает использование этой переменной. Для соединения двух DataFrame есть отдельный механизм `F.broadcast(shops)`, который подсказывает SQL-планировщику сторону JOIN. [Broadcast Variables](https://spark.apache.org/docs/4.1.1/rdd-programming-guide.html#broadcast-variables)
