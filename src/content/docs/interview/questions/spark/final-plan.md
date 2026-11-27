---
title: "Является ли план запроса конечным?"
head:
  - tag: title
    content: "Начальный и конечный планы Spark SQL | Инжиниринг Данных"
description: "Как увидеть начальный и конечный физические планы одного запроса. Проверяем isFinalPlan до и после действия и находим изменения AQE в Spark UI."
prev: {"label":"Как работает Adaptive Query Execution (AQE)?","link":"/interview/questions/spark/aqe/"}
next: false
tableOfContents: false
editUrl: false
---

**Исходный физический план может измениться во время выполнения.** Если включён AQE, Spark сверяет первоначальные оценки с реальными размерами данных после обмена. Он может выбрать другой способ выполнить оставшуюся работу. Если первоначальный вариант подходит, Spark его сохраняет.

Возьмём DataFrame `totals` с выручкой двух магазинов. Посмотрим план до и после выполнения **того же DataFrame**.

```python
totals.explain("formatted")   # исходный план
rows = totals.collect()       # на драйвер вернутся две строки
totals.explain("formatted")   # план завершённого запроса
```

| Когда смотришь | Что увидишь в этом примере |
| --- | --- |
| До действия | У `AdaptiveSparkPlan` стоит `isFinalPlan=false`. В плане есть `Exchange` на восемь shuffle-партиций. |
| После действия | У `AdaptiveSparkPlan` стоит `isFinalPlan=true`. Можно сравнить `Initial Plan` и `Final Plan`. В конечном плане появился `AQEShuffleRead` с пометкой `coalesced` — Spark объединил чтение партиций. |

У завершённого выполнения план **конечный**. При отключённом AQE адаптивного перепланирования во время запуска не будет. Посмотреть, какие операторы действительно отработали и сколько строк через них прошло, можно во вкладке **SQL** в Spark UI. [Вкладка SQL в Spark UI](https://spark.apache.org/docs/4.1.1/web-ui.html#sql-tab)
