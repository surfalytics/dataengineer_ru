---
title: "Как работает Broadcast JOIN и какие у него ограничения?"
head:
  - tag: title
    content: "Broadcast JOIN и его ограничения в Spark | Инжиниринг Данных"
description: "Что рассылает драйвер, когда broadcast экономит shuffle и чем различаются порог автоматического выбора и предел размера таблицы."
prev: {"label":"Как Spark выбирает стратегию JOIN?","link":"/interview/questions/spark/join-strategies/"}
next: {"label":"Что такое хинты в Spark?","link":"/interview/questions/spark/join-hints/"}
tableOfContents: false
editUrl: false
---

**Broadcast JOIN** нужен, когда к большой таблице надо присоединить маленькую. Например, к миллиарду заказов добавляем город из справочника магазинов. Для соединения по равенству Spark может собрать справочник на драйвере, построить хеш-таблицу и разослать её executors. Задача читает свою партицию заказов и ищет магазин локально. Анимация этого обмена есть на странице [стратегий JOIN](/interview/questions/spark/join-strategies/#broadcasthashjoin).

| Ограничение | Что важно помнить |
| --- | --- |
| Автоматический выбор | По умолчанию `spark.sql.autoBroadcastJoinThreshold` равен **10 МиБ**. Планировщик использует оценку размера после фильтрации и выбора колонок. Размер сжатого Parquet-файла может сильно отличаться от размера хеш-таблицы. |
| Память и время | Справочник собирается на драйвере, а его копия нужна каждому участвующему executor. Даже принудительный `broadcast()` может закончиться OOM или тайм-аутом ожидания рассылки. |
| Предел реализации | В Spark 3.5.x проверка размера отклоняет таблицу от **8 ГиБ**. Начиная с 4.1 предел задаёт `spark.sql.maxBroadcastTableSize` с тем же значением по умолчанию. Есть и отдельная проверка числа строк. |
| Условие и тип JOIN | При `INNER JOIN` подходит любая достаточно маленькая сторона. Хеш-таблицу для `LEFT OUTER` строят только справа, для `RIGHT OUTER` — только слева. С `FULL OUTER` стратегия BroadcastHashJoin недоступна. При соединении без подходящего ключа равенства подсказка broadcast может привести к `BroadcastNestedLoopJoin`. |

В `explain("formatted")` ищи `BroadcastExchange` на рассылаемой стороне и имя оператора JOIN. В Spark UI у выполненного обмена можно посмотреть объём данных и время рассылки. [Настройки Spark SQL](https://spark.apache.org/docs/4.1.1/sql-performance-tuning.html#optimizing-the-join-strategy) · [Проверки размера в Spark 4.1](https://github.com/apache/spark/blob/v4.1.1/sql/core/src/main/scala/org/apache/spark/sql/execution/exchange/BroadcastExchangeExec.scala)
