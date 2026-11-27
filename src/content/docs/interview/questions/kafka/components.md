---
title: "Какие основные компоненты есть в Kafka и как проходит сообщение?"
head:
  - tag: title
    content: "Основные компоненты Kafka | Инжиниринг Данных"
description: "Как событие проходит от producer через topic, partition и broker до consumer и какую роль при чтении играет consumer group."
prev: {"label":"Что такое Apache Kafka и зачем она нужна?","link":"/interview/questions/kafka/what-is-kafka/"}
next: {"label":"Что такое topic и partition в Kafka?","link":"/interview/questions/kafka/partitions/"}
tableOfContents: false
editUrl: false
---

**Producer** создаёт событие и отправляет его в topic.

**Topic** — логическое имя потока событий, например `orders`.

Topic разделён на **partitions**. Внутри partition события записываются в конец упорядоченного журнала.

**Broker** — сервер Kafka, который хранит partitions и обслуживает запросы producers и consumers. Несколько brokers образуют cluster.

**Consumer** читает события из partitions. Consumers одного приложения обычно объединяются в **consumer group**, чтобы разделить partitions и обрабатывать данные параллельно.

Упрощённый путь выглядит так: `Producer → Topic Partition на Broker → Consumer`. Kafka сохраняет событие в partition, присваивает ему offset, а consumer запрашивает данные начиная с нужного offset.
