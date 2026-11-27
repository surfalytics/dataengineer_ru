---
title: "Как Kafka хранит события и чем retention отличается от log compaction?"
head:
  - tag: title
    content: "Хранение событий в Apache Kafka | Инжиниринг Данных"
description: "Как Kafka хранит записи в сегментах, чем удаление по сроку хранения отличается от log compaction и для чего нужна запись с пустым значением."
prev: {"label":"Чем отличаются at-most-once, at-least-once и exactly-once в Kafka?","link":"/interview/questions/kafka/delivery-semantics/"}
next: false
tableOfContents: false
editUrl: false
---

Kafka хранит события в append-only logs, разбитых на сегменты. Чтение consumer не удаляет событие, поэтому разные consumer groups могут читать один topic независимо, а старые данные можно переиграть.

При `cleanup.policy=delete` старые сегменты удаляются по времени или ограничению размера. Retention применяется к log, а не к факту обработки конкретным consumer. Поэтому медленный consumer может потерять возможность дочитать данные, если они уже вышли за срок хранения.

При `cleanup.policy=compact` Kafka со временем сохраняет как минимум последнее известное значение для каждого key и удаляет более старые версии этого key. Запись с key и значением `null` используется как tombstone для удаления ключа. Compaction выполняется асинхронно, поэтому старые версии могут некоторое время оставаться в log.

Политики `delete` и `compact` можно применять вместе. `delete` удобна для потока событий с ограниченной историей, compaction — для восстановления актуального состояния по каждому key.
