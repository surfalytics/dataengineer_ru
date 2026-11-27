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

Проверь физический план. Для файлового источника ищи `dynamicpruningexpression` в `PartitionFilters` узла чтения `sales`. В этом примере `region_id` — ключ JOIN и физическая колонка партиционирования продаж. Фильтр по стране оставляет лишь часть справочника. При стандартной настройке `spark.sql.optimizer.dynamicPartitionPruning.reuseBroadcastOnly=true` Spark ищет в плане broadcast отфильтрованного справочника, который можно переиспользовать для отсечения партиций. Одной оценки «справочник маленький» недостаточно. [Правило DPP для файлового источника](https://github.com/apache/spark/blob/v4.1.1/sql/core/src/main/scala/org/apache/spark/sql/execution/dynamicpruning/PlanDynamicPruningFilters.scala)
