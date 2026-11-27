---
title: "Что такое Column Pruning?"
head:
  - tag: title
    content: "Column Pruning в Spark | Инжиниринг Данных"
description: "Как Catalyst оставляет только нужные колонки и как по ReadSchema проверить, какие поля Spark действительно читает из Parquet."
prev: {"label":"Полный план запроса в Spark","link":"/interview/questions/spark/query-lifecycle/"}
next: {"label":"Как работает Dynamic Partition Pruning (DPP)?","link":"/interview/questions/spark/dynamic-partition-pruning/"}
tableOfContents: false
editUrl: false
---

**Column Pruning** убирает из плана колонки, которые не нужны для результата или промежуточных операций. В Parquet и ORC значения одного столбца лежат отдельно от других. Если в таблице сто полей, для отчёта можно физически прочитать только несколько.

```python
paid = spark.read.parquet(orders_path).where("status = 'paid'").select("amount")
paid.explain("formatted")
```

В результате останется только `amount`, но для проверки условия ещё требуется `status`. Если это обычные колонки Parquet, в `ReadSchema` узла чтения ожидай обе. Остальные 98 полей читать для этого запроса незачем.

Часть плана `PushedFilters` отвечает на другой вопрос: какие условия Spark передал источнику, чтобы пропускать лишние строки или группы строк. В одном запросе могут одновременно сработать и ранняя фильтрация, и выбор нужных колонок. [Чтение Parquet в Spark SQL](https://spark.apache.org/docs/4.1.1/sql-data-sources-parquet.html)
