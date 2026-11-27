---
title: "Чем отличаются at-most-once, at-least-once и exactly-once в Kafka?"
head:
  - tag: title
    content: "Гарантии доставки событий в Kafka | Инжиниринг Данных"
description: "Когда обработка допускает пропуск или повтор события, как в Kafka работает exactly-once и что меняется при записи результата во внешнюю базу."
prev: {"label":"Как в Kafka работают replication, partition leader и ISR?","link":"/interview/questions/kafka/replication/"}
next: {"label":"Как Kafka хранит события и чем retention отличается от log compaction?","link":"/interview/questions/kafka/retention/"}
tableOfContents: false
editUrl: false
---

**At-most-once** означает, что событие обрабатывается не более одного раза, но может быть потеряно. Так получается, если сначала сохранить offset, а потом выполнять обработку.

**At-least-once** означает, что событие не должно потеряться, но может быть обработано повторно. Для этого я сначала выполняю обработку и только потом коммичу offset. Если процесс упадёт между этими действиями, Kafka отдаст событие ещё раз. Это наиболее распространённая модель, поэтому обработчик делают идемпотентным.

**Exactly-once** означает, что результат события должен появиться один раз даже при retry. Для Kafka-to-Kafka обработки Kafka поддерживает idempotent producer и transactions: можно атомарно записать результат и offsets, а consumers читают только подтверждённые записи через `isolation.level=read_committed`.

Если результат пишется во внешнюю базу, одной Kafka transaction недостаточно. Тогда нужны идемпотентная запись, deduplication, transactional outbox или другой способ согласовать внешний side effect с offset.
