---
title: "Как в Kafka работают replication, partition leader и ISR?"
head:
  - tag: title
    content: "Репликация, leader и ISR в Kafka | Инжиниринг Данных"
description: "Как Kafka выбирает лидера партиции, что означает состав ISR и как replication factor, acks и min.insync.replicas влияют на надёжность записи."
prev: {"label":"Что такое consumer rebalance и когда он происходит?","link":"/interview/questions/kafka/rebalance/"}
next: {"label":"Чем отличаются at-most-once, at-least-once и exactly-once в Kafka?","link":"/interview/questions/kafka/delivery-semantics/"}
tableOfContents: false
editUrl: false
---

Kafka реплицирует данные на уровне partitions. У partition есть одна leader replica и несколько follower replicas на других brokers. Producer пишет в leader, а followers копируют её log.

ISR, или in-sync replicas, — это leader и followers, которые не отстали от неё сверх допустимого предела. Если broker с leader выходит из строя, Kafka может выбрать новую leader из подходящих replicas и продолжить работу.

Replication factor показывает общее число копий partition. Например, factor 3 означает одну leader и ещё две replicas.

Надёжность записи дополнительно задают `acks` и `min.insync.replicas`. При `acks=all` producer ждёт подтверждения от ISR. Если `min.insync.replicas=2`, а в ISR осталось меньше двух replicas, запись завершится ошибкой, а не будет принята с ослабленной надёжностью. Частый production-вариант — replication factor 3, `acks=all` и `min.insync.replicas=2`.
