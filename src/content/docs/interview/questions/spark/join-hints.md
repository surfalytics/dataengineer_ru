---
title: "Что такое хинты в Spark?"
head:
  - tag: title
    content: "Хинты в Spark | Инжиниринг Данных"
description: "Как предложить стратегию соединения или распределение партиций через SQL и DataFrame API и проверить результат в физическом плане."
prev: {"label":"Как работает Broadcast JOIN и какие у него ограничения?","link":"/interview/questions/spark/broadcast-join/"}
next: {"label":"Почему broadcast() может не дать BroadcastHashJoin?","link":"/interview/questions/spark/broadcast-hint-failure/"}
tableOfContents: false
editUrl: false
---

**Хинт (hint)** — подсказка планировщику для конкретного запроса. Например, ты знаешь, что справочник после фильтрации маленький, а статистика в каталоге устарела. Можно предложить Spark разослать справочник.

```sql
SELECT /*+ BROADCAST(s) */ o.order_id, s.city
FROM orders o JOIN shops s ON o.shop_id = s.shop_id
```

В DataFrame API тот же смысл у `orders.join(F.broadcast(shops), "shop_id")`. Хинты `MERGE` и `SHUFFLE_HASH` предлагают другие стратегии соединения. Есть и подсказки для партиций, например `REPARTITION(40)` перед записью.

Если стороны предлагают разные стратегии, приоритет у `BROADCAST`, затем идут `MERGE`, `SHUFFLE_HASH` и `SHUFFLE_REPLICATE_NL`. Планировщик учитывает поддержку типа JOIN: хинт не сделает BroadcastHashJoin доступным для полного внешнего соединения. Проверь оператор в физическом плане, а с включённым AQE загляни и в конечный план во вкладке SQL. [Синтаксис и приоритет хинтов](https://spark.apache.org/docs/4.1.1/sql-ref-syntax-qry-select-hints.html)
