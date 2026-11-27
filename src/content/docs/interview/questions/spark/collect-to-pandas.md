---
title: "Чем опасны collect() и toPandas()?"
head:
  - tag: title
    content: "collect() и toPandas() в Spark | Инжиниринг Данных"
description: "Куда попадают результаты collect и toPandas в классическом PySpark и Spark Connect и почему Arrow не снимает ограничение памяти."
prev: {"label":"Чем опасен cache() без unpersist()?","link":"/interview/questions/spark/cache-lifetime/"}
next: {"label":"В чём проблема маленьких файлов?","link":"/interview/questions/spark/small-files/"}
tableOfContents: false
editUrl: false
---

**Оба действия собирают весь результат в одном процессе.** В классическом PySpark `collect()` возвращает на драйвер список объектов `Row`, а `toPandas()` строит локальный pandas DataFrame. Ты можешь успешно обработать таблицу на десятках executors и потерять приложение на последнем шаге.

Например, агрегат по десяти магазинам легко посмотреть локально. Если по ошибке собрать все чеки до агрегации, объём станет совсем другим. Размер Parquet на диске плохо предсказывает размер Python-объектов в памяти. Arrow ускоряет передачу при `toPandas()`, но готовый pandas DataFrame всё равно должен поместиться целиком.

- Для просмотра нескольких строк используй `df.show(20)` или `df.limit(20).toPandas()`. Лимит строк не ограничивает размер одного большого поля.
- Для выгрузки всей таблицы записывай её распределённо через `df.write`.
- `spark.driver.maxResultSize` может прервать действие по размеру сериализованных результатов раньше, чем закончится память. Увеличение лимита само по себе памяти не добавляет.

При Spark Connect результат возвращается в клиентский процесс. Даже если сервер справился, локальный Python-клиент тоже может упасть по памяти. [DataFrame.collect](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.collect.html) · [DataFrame.toPandas](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html)
