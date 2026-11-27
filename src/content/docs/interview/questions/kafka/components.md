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

**Producer** — любое приложение, которое записывает события в Kafka. Например, сервис заказов может сам отправить в топик `orders` событие «заказ оплачен».

Другой пример — Debezium в Kafka Connect. Сервис меняет статус заказа в PostgreSQL. Debezium читает изменение из журнала транзакций (WAL) и формирует событие, а встроенный producer Kafka Connect записывает его в Kafka. В этом варианте сервису заказов достаточно обновить строку в базе. [Как работает коннектор Debezium для PostgreSQL](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#how-the-postgresql-connector-works)

**Topic** — логическое имя потока событий, например `orders`.

Topic разделён на **partitions**. Внутри partition события записываются в конец упорядоченного журнала.

**Broker** — сервер Kafka, который хранит partitions и обслуживает запросы producers и consumers. Несколько brokers образуют cluster.

**Consumer** читает события из partitions. Consumers одного приложения обычно объединяются в **consumer group**, чтобы разделить partitions и обрабатывать данные параллельно.

Упрощённый путь выглядит так: `Producer → Topic Partition на Broker → Consumer`. Kafka сохраняет событие в partition, присваивает ему offset, а consumer запрашивает данные начиная с нужного offset.
