---
title: "Что такое Catalyst и как он работает с DataFrame API?"
head:
  - tag: title
    content: "Оптимизатор Catalyst в SQL и DataFrame API | Инжиниринг Данных"
description: "Как Catalyst оптимизирует запросы SQL и DataFrame API в Spark. Сравниваем два способа посчитать выручку по магазинам и прослеживаем путь до физического плана."
prev: {"label":"Job -> Stages -> Task","link":"/interview/questions/spark/execution/"}
next: {"label":"Кто строит логический план запроса?","link":"/interview/questions/spark/logical-plan/"}
tableOfContents: false
editUrl: false
---

**Catalyst — оптимизатор Spark SQL. Он работает и с SQL-запросами, и с DataFrame API.** Когда ты пишешь `filter()`, `groupBy()` и `agg()` в PySpark, Spark собирает эти операции в логический план. Catalyst оптимизирует его на драйвере точно так же, как план запроса, написанного на SQL. [Spark SQL и DataFrames](https://spark.apache.org/docs/4.1.1/sql-programming-guide.html)

Допустим, таблица `orders` хранится в Parquet. Нужна выручка по каждому магазину за оплаченные заказы.

```sql
SELECT shop_id, SUM(amount) AS revenue
FROM orders
WHERE status = 'paid'
GROUP BY shop_id
```

Тот же расчёт через DataFrame API в PySpark выглядит так.

```python
from pyspark.sql import functions as F

totals = (
    spark.table("orders")
    .filter(F.col("status") == "paid")
    .groupBy("shop_id")
    .agg(F.sum("amount").alias("revenue"))
)
```

В первом случае исходный логический план строит SQL-парсер, во втором — вызовы DataFrame API. Дальше оба плана проходят через один анализатор, оптимизатор и физический планировщик.

| Что решает Spark | На примере заказов |
| --- | --- |
| Можно ли выполнить такой запрос к этой таблице? | Анализатор находит `orders`, проверяет имена колонок и тип `amount` для `SUM`. |
| Какие операции можно упростить? | После фильтрации по `status` для подсчёта нужны только `shop_id` и `amount`. Остальные колонки можно отбросить. |
| Как выполнить расчёт на кластере? | Планировщик выбирает операторы для чтения Parquet, подсчёта частичных сумм и обмена данными между партициями. |

**Логический план** описывает, что посчитать. **Физический план** показывает, какими операциями Spark это сделает. Оба видны в выводе `EXPLAIN EXTENDED`. [Документация Spark SQL](https://spark.apache.org/docs/4.1.1/sql-ref-syntax-qry-explain.html)
