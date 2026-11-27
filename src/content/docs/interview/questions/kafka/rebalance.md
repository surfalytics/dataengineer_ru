---
title: "Что такое consumer rebalance и когда он происходит?"
head:
  - tag: title
    content: "Ребалансировка consumer group в Kafka | Инжиниринг Данных"
description: "Когда Kafka перераспределяет партиции между участниками группы, что происходит с чтением и почему после rebalance возможна повторная обработка."
prev: {"label":"Что такое offset в Kafka и зачем consumer его коммитит?","link":"/interview/questions/kafka/offsets/"}
next: {"label":"Как в Kafka работают replication, partition leader и ISR?","link":"/interview/questions/kafka/replication/"}
tableOfContents: false
editUrl: false
---

Rebalance — это перераспределение partitions между consumers одной группы.

Он нужен, когда consumer присоединяется к группе, корректно выходит, перестаёт отправлять heartbeat, слишком долго не вызывает `poll()` либо когда меняется набор доступных partitions. Kafka отбирает часть назначений и передаёт их другим участникам.

Rebalance обеспечивает масштабирование и восстановление после отказа, но влияет на обработку. Во время смены назначений часть consumers может временно не читать данные. Если старый consumer не успел корректно завершить работу и закоммитить offsets, после передачи partition возможна повторная обработка.

Поэтому я стараюсь не выполнять долгую блокирующую работу в consumer loop, корректно обрабатывать revoke partitions и коммитить только действительно обработанные записи. Частые rebalances обычно означают проблемы со стабильностью consumers или настройками группы.
