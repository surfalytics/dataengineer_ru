---
title: "Как работает Dynamic Partition Pruning (DPP)?"
head:
  - tag: title
    content: "Dynamic Partition Pruning в Spark | Инжиниринг Данных"
description: "Как Spark отсекает партиции таблицы фактов по результату фильтрации справочника и где искать динамический фильтр в плане."
prev: {"label":"Что такое Column Pruning?","link":"/interview/questions/spark/column-pruning/"}
next: {"label":"Что такое UDF и почему для Catalyst это «чёрный ящик»?","link":"/interview/questions/spark/udf/"}
tableOfContents: false
editUrl: false
---

**Dynamic Partition Pruning (DPP)** позволяет пропустить партиции большой таблицы, когда нужные ключи становятся известны только при выполнении запроса.

Представь таблицу продаж `sales`, физически разбитую по `region_id`, и справочник `regions`. В запросе задано название страны. Номера регионов этой страны заранее не перечислены.

```sql
SELECT s.order_id, s.amount
FROM sales s
JOIN regions r ON s.region_id = r.region_id
WHERE r.country = 'Армения'
```

Spark фильтрует справочник и получает нужные `region_id`. Если планировщик применил DPP, источник продаж пропускает партиции остальных регионов ещё при чтении. Spark может переиспользовать broadcast справочника. При условии `WHERE s.region_id = 7` ключ известен заранее и достаточно статического отсечения.

Проверь физический план. Для файлового источника ищи `dynamicpruningexpression` в `PartitionFilters` узла чтения `sales`. Для этого примера важно, что ключ соединения совпадает с колонкой физического партиционирования. Сам по себе JOIN применения DPP не гарантирует. [Настройки Spark SQL](https://spark.apache.org/docs/4.1.1/configuration.html#runtime-sql-configuration)
