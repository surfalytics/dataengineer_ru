---
title: "Чем опасен cache() без unpersist()?"
head:
  - tag: title
    content: "Когда нужен unpersist() в Spark | Инжиниринг Данных"
description: "Что происходит с кешем после записи очередного месяца и как вовремя освободить блоки, память и локальный диск executors."
prev: {"label":"Почему повторный Action снова вычисляет DataFrame?","link":"/interview/questions/spark/repeated-actions/"}
next: {"label":"Чем опасны collect() и toPandas()?","link":"/interview/questions/spark/collect-to-pandas/"}
tableOfContents: false
editUrl: false
---

Допустим, одно Spark-приложение грузит год помесячно. На каждой итерации ты кешируешь результат JOIN, строишь два отчёта и переходишь к следующему месяцу. **Завершение записи не освобождает кеш.** Январские блоки могут оставаться на executors, когда уже начался февраль.

Кеш занимает storage memory. Под давлением памяти Spark может вытеснить часть блоков или сохранить их на диске в зависимости от уровня хранения. Тогда возрастут чтение с диска, пересчёты и длительность задач. Чем больше разных результатов кешируется в одном приложении, тем заметнее эффект. При динамическом выделении ресурсов executors с кешированными блоками также могут дольше оставаться в кластере.

```python
month = orders.where("month_id = '2026-01'").cache()
try:
    write_sales_report(month)
    write_quality_report(month)
finally:
    month.unpersist(blocking=True)
```

Здесь `write_sales_report` и `write_quality_report` — две записи результата. `blocking=True` нужен, если перед следующим месяцем важно дождаться освобождения блоков. Если DataFrame читается всего один раз, сначала попробуй обойтись без кеша. Проверь во вкладке **Storage**, исчезают ли старые блоки по мере обработки года. [DataFrame.unpersist](https://spark.apache.org/docs/4.1.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.unpersist.html)
