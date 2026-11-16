---
title: "Designing Data-Intensive Applications — конспект книги"
head:
  - tag: title
    content: "Designing Data-Intensive Applications: конспект | Инжиниринг Данных"
description: "Конспект 2-го издания Designing Data-Intensive Applications на русском: хранение, репликация, sharding, транзакции, консенсус, потоки. 14 глав."
author: "Martin Kleppmann, Chris Riccomini"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - data-engineering
  - distributed-systems
---

**Designing Data-Intensive Applications, 2nd Edition** — книга Martin Kleppmann и Chris Riccomini (O'Reilly, 2026). Она объясняет, как базы данных, `message broker` и системы обработки данных устроены внутри и какие компромиссы стоят за каждым из этих решений. Первое издание Kleppmann выпустил в 2017 году. Для второго издания авторы переработали весь текст. Они добавили облачные системы поверх объектного хранилища (`object storage`), векторные индексы, DataFrame, `durable execution`, `sync engine` и GDPR. А главу о пакетной обработке переписали без упора на MapReduce. В книге 14 глав.

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.

📥 [Скачать конспект в EPUB](/downloads/designing-data-intensive-applications.epub) — для телефона и электронной книги.

![Карта книги: 14 глав в трёх блоках — основы одной системы (главы 1–5), распределённые данные (главы 6–10) и производные данные (главы 11–14)](/assets/designing-data-intensive-applications/ch00-book-map.png)

Читайте карту сверху вниз. Сначала книга разбирает одну систему: требования, модели данных, хранение и форматы. Затем она показывает, что меняется, когда данные лежат на многих машинах. В конце авторы собирают из нескольких систем одно приложение и спрашивают, как оно влияет на людей.

## О чём книга простыми словами

Авторы называют приложение data-intensive (`data-intensive`), если его главная трудность — в данных, а не в мощности процессора. Данных может быть много, они могут быть сложными или быстро меняться. Таких приложений сейчас большинство: почти любой сервис хранит данные, ищет по ним, кэширует их и обрабатывает пачками или потоком.

Книга не учит одному продукту. Она разбирает идеи, на которых стоят PostgreSQL, MySQL, Cassandra, Kafka, Spark, Snowflake и десятки других систем. Продукты меняются быстро, а идеи остаются, поэтому знание идей помогает выбрать систему и понять, почему она ведёт себя так, а не иначе.

Главная мысль книги — в архитектуре нет правильного ответа, есть только компромиссы (`trade-off`). Каждое решение что-то даёт и что-то отнимает. Например, репликация повышает отказоустойчивость, но приносит лаг репликации и конфликты. Сильная согласованность упрощает код, но замедляет систему и хуже переносит сбои сети. Задача инженера — знать цену каждого варианта и выбирать её осознанно.

## Что нужно знать заранее

- Базовый SQL: `SELECT`, `JOIN`, `GROUP BY`. Если нужно повторить, начните с раздела [SQL](/processing/sql/).
- Общее понимание, что такое база данных, индекс, сервер и сеть.
- Для практики: DuckDB CLI и Python 3. Код из книги переписан так, что внешние сервисы не нужны.
- Полезно, но не обязательно: [конспект Fundamentals of Data Engineering](/book-summaries/engineering/fundamentals-of-data-engineering/). Он даёт общую карту профессии, а эта книга объясняет, что происходит внутри блоков на этой карте.

## Зачем читать

- **Видеть компромиссы.** Идеальной базы данных нет. После книги вы видите, что система выигрывает и чем за это платит.
- **Понимать распределённые данные.** Репликация, `sharding`, транзакции и консенсус объяснены на примерах, без формул.
- **Знать, почему данные расходятся.** Книга показывает, какие гарантии дают уровни изоляции и модели согласованности на самом деле и где они ломаются.
- **Строить `pipeline` правильно.** Пакетная и потоковая обработка, CDC, `exactly-once` и идемпотентность нужны дата-инженеру каждый день.
- **Задавать поставщику точные вопросы.** Вы сможете спросить, что база гарантирует при сбое узла или разрыве сети, и понять ответ.
- **Думать о людях.** Последняя глава объясняет, как системы данных влияют на приватность и справедливость решений.

## Как устроена книга

Во втором издании нет формального деления на части. Но главы явно идут тремя блоками, как в первом издании, и мы группируем их так же.

| Блок | Главы | О чём |
|---|---|---|
| Основы | 1–5 | Как устроена одна система: требования, модели данных, хранение, кодирование и изменение схем |
| Распределённые данные | 6–10 | Что происходит, когда данные лежат на многих машинах: репликация, `sharding`, транзакции, сбои, консенсус |
| Производные данные | 11–14 | Как из нескольких систем собрать одно приложение: пакетная и потоковая обработка, журнал событий, этика данных |

Блоки опираются друг на друга. Первый блок даёт словарь: задержка (`latency`), `throughput`, B-tree, `LSM-tree`, совместимость схем. Второй блок берёт эти понятия и показывает, как они ломаются, когда машин много и сеть ненадёжна. Третий блок исходит из того, что одной системы не хватает, и объясняет, как держать много систем согласованными через журнал событий (`log`) и производные данные.

## Главные идеи

| Идея | Глава |
|---|---|
| Операционные и аналитические системы решают разные задачи, поэтому данные копируют из одних в другие | [1](/book-summaries/engineering/designing-data-intensive-applications/01-trade-offs-in-architecture/) |
| Скорость описывают перцентилями времени ответа, а не средним | [2](/book-summaries/engineering/designing-data-intensive-applications/02-nonfunctional-requirements/) |
| Модель данных выбирают по типу связей: документы, таблицы или граф | [3](/book-summaries/engineering/designing-data-intensive-applications/03-data-models-and-query-languages/) |
| `LSM-tree` быстрее пишет, B-tree быстрее читает, а аналитике нужно колоночное хранение | [4](/book-summaries/engineering/designing-data-intensive-applications/04-storage-and-retrieval/) |
| Формат данных должен давать совместимость в обе стороны: старый код читает новые данные, новый код читает старые | [5](/book-summaries/engineering/designing-data-intensive-applications/05-encoding-and-evolution/) |
| Вся трудность репликации — в изменениях: лаг, порядок и конфликты параллельных записей | [6](/book-summaries/engineering/designing-data-intensive-applications/06-replication/) |
| Ключ `sharding` решает, будет ли нагрузка ровной и сколько данных переедет при росте кластера | [7](/book-summaries/engineering/designing-data-intensive-applications/07-sharding/) |
| Слабые уровни изоляции пропускают гонки, от всех гонок защищает только `serializability` | [8](/book-summaries/engineering/designing-data-intensive-applications/08-transactions/) |
| Сеть, часы и процессы ненадёжны, поэтому важные решения принимает кворум | [9](/book-summaries/engineering/designing-data-intensive-applications/09-trouble-with-distributed-systems/) |
| `Linearizability`, блокировки и уникальность сводятся к консенсусу | [10](/book-summaries/engineering/designing-data-intensive-applications/10-consistency-and-consensus/) |
| `Batch job` читает неизменяемый вход, поэтому ошибку исправляют перезапуском | [11](/book-summaries/engineering/designing-data-intensive-applications/11-batch-processing/) |
| Лог событий можно перечитать, а состояние системы можно вывести из лога | [12](/book-summaries/engineering/designing-data-intensive-applications/12-stream-processing/) |
| Корректность дают сквозные ID запросов и идемпотентность, а не распределённые транзакции | [13](/book-summaries/engineering/designing-data-intensive-applications/13-philosophy-of-streaming-systems/) |
| Данные о людях — это ответственность: собирайте меньше и удаляйте раньше | [14](/book-summaries/engineering/designing-data-intensive-applications/14-doing-the-right-thing/) |

## Как читать

Книга плотная, поэтому выберите свой путь. На первом проходе читайте «Главную мысль», схемы и «Итоги главы» каждой страницы, а детали оставьте на второй проход.

| Роль | Что читать | Почему |
|---|---|---|
| Новичок | По порядку, главы 1–5, затем 6–8 | Сначала словарь и одна машина, потом распределённые данные. Главы 9 и 10 самые трудные: их лучше читать вторым проходом |
| Analytics engineer | Главы 1, 3, 4, 5, затем 11 и 13 | Модели данных, колоночное хранение, форматы и схемы, пакетная обработка и производные данные |
| Data engineer | Главы 4, 5, 11, 12, 13, затем 6–8 | Хранение, форматы, `pipeline` из пакетов и потоков, CDC, затем репликация, `sharding` и транзакции |
| Руководитель, архитектор | Главы 1, 2, 13 и 14 | Компромиссы архитектуры, требования в числах, как связать системы и за что команда отвечает перед людьми |

Если данные расходятся между системами, читайте главы 6, 8, 10 и 13: они объясняют, откуда берутся расхождения и как их избежать.

## Связь с Fundamentals of Data Engineering

Эти две книги дополняют друг друга.

| | Fundamentals of Data Engineering | Designing Data-Intensive Applications |
|---|---|---|
| Фокус | Жизненный цикл данных и архитектура | Внутреннее устройство систем |
| Вопрос | Что строить и как выбирать технологии | Как это работает и какие есть компромиссы |
| Уровень | Широкий обзор профессии | Глубокий разбор механизмов |

Сначала можно прочитать [конспект Fundamentals of Data Engineering](/book-summaries/engineering/fundamentals-of-data-engineering/): он даёт карту. После этого книга Kleppmann и Riccomini объяснит, что происходит внутри блоков на карте.

## Как работать с практикой

В книге мало кода, но многие идеи легко проверить руками. Поэтому мы добавили примеры, которые запускаются локально и не требуют внешних сервисов.

- **DuckDB.** Главы [3](/book-summaries/engineering/designing-data-intensive-applications/03-data-models-and-query-languages/), [4](/book-summaries/engineering/designing-data-intensive-applications/04-storage-and-retrieval/), [8](/book-summaries/engineering/designing-data-intensive-applications/08-transactions/), [11](/book-summaries/engineering/designing-data-intensive-applications/11-batch-processing/) и [12](/book-summaries/engineering/designing-data-intensive-applications/12-stream-processing/) заканчиваются разделом «Практика в DuckDB». Запустите `duckdb` и выполняйте запросы по порядку: данные создаются прямо в SQL.
- **Python, shell и SQL-файлы.** Код к главам 2, 4–9, 11 и 13 лежит в папке `scripts/ddia-code/` репозитория сайта. Ему нужны только стандартная библиотека Python, shell и DuckDB CLI.
- Вывод на страницах — настоящий, он получен запуском кода. Если ваш вывод отличается, сначала проверьте версию DuckDB.

## Разбор по главам

| Глава | На какой вопрос отвечает |
|---|---|
| [1. Компромиссы в архитектуре систем данных](/book-summaries/engineering/designing-data-intensive-applications/01-trade-offs-in-architecture/) | Чем операционные системы отличаются от аналитических и когда выбирать облако или распределённую систему |
| [2. Нефункциональные требования](/book-summaries/engineering/designing-data-intensive-applications/02-nonfunctional-requirements/) | Как описать в числах скорость, надёжность, масштабируемость и простоту сопровождения |
| [3. Модели данных и языки запросов](/book-summaries/engineering/designing-data-intensive-applications/03-data-models-and-query-languages/) | Когда выбрать реляционную, документную или графовую модель, event sourcing или DataFrame |
| [4. Хранение и извлечение данных](/book-summaries/engineering/designing-data-intensive-applications/04-storage-and-retrieval/) | Как устроены `LSM-tree`, B-tree, колоночное хранение, полнотекстовые и векторные индексы |
| [5. Кодирование данных и изменение схем](/book-summaries/engineering/designing-data-intensive-applications/05-encoding-and-evolution/) | Как JSON, Protocol Buffers и Avro дают совместимость и как данные идут между процессами |
| [6. Репликация](/book-summaries/engineering/designing-data-intensive-applications/06-replication/) | Как работают один `leader`, несколько `leader` и репликация без `leader` и что делать с лагом и конфликтами |
| [7. Sharding](/book-summaries/engineering/designing-data-intensive-applications/07-sharding/) | Как делить данные по ключу или хешу, переносить `shard` и искать по вторичным индексам |
| [8. Транзакции](/book-summaries/engineering/designing-data-intensive-applications/08-transactions/) | Что гарантируют `ACID` и уровни изоляции, как получить `serializability` и как работает `two-phase commit` |
| [9. Проблемы распределённых систем](/book-summaries/engineering/designing-data-intensive-applications/09-trouble-with-distributed-systems/) | Почему сеть, часы и процессы ненадёжны и как узлу принимать решения без полной информации |
| [10. Согласованность и консенсус](/book-summaries/engineering/designing-data-intensive-applications/10-consistency-and-consensus/) | Что такое `linearizability`, как работают `logical clock` и почему многие задачи сводятся к консенсусу |
| [11. Пакетная обработка](/book-summaries/engineering/designing-data-intensive-applications/11-batch-processing/) | Как устроены Unix-инструменты, MapReduce, Spark и `shuffle` и где применяют пакетную обработку |
| [12. Потоковая обработка](/book-summaries/engineering/designing-data-intensive-applications/12-stream-processing/) | Как работают брокеры на основе лога, CDC, окна по времени, `join` в потоках и отказоустойчивость |
| [13. Философия потоковых систем](/book-summaries/engineering/designing-data-intensive-applications/13-philosophy-of-streaming-systems/) | Как собрать приложение из нескольких систем через журнал событий и обеспечить корректность без распределённых транзакций |
| [14. Поступать правильно: этика данных](/book-summaries/engineering/designing-data-intensive-applications/14-doing-the-right-thing/) | Как алгоритмы и сбор данных влияют на людей и что с этим может сделать инженер |

Каждая страница главы содержит главную мысль, схемы, ключевые термины, выводы для практики и вопросы для самопроверки.
