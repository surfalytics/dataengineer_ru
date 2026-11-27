---
title: "Apache Iceberg: The Definitive Guide — конспект книги"
head:
  - tag: title
    content: "Apache Iceberg: конспект книги | Инжиниринг Данных"
description: "Конспект Apache Iceberg: The Definitive Guide: архитектура, движки, эксплуатация и практические сценарии."
author: "Tomer Shiran, Jason Hughes, Alex Merced"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - iceberg
---

**Apache Iceberg: The Definitive Guide** — книга Tomer Shiran, Jason Hughes и Alex Merced, O’Reilly Media, первое издание 2024 года. В 14 главах авторы объясняют устройство формата таблиц Iceberg, его интеграции и эксплуатацию в lakehouse.

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.

📥 [Скачать конспект в EPUB](/downloads/apache-iceberg-the-definitive-guide.epub) — для телефона и электронной книги.

![Три части книги об Apache Iceberg](/assets/apache-iceberg-the-definitive-guide/overview.png)

Карта показывает три части книги: основы, работу движков и применение Iceberg на практике.

## О чём книга простыми словами

Аналитическая таблица в data lake может состоять из множества файлов, которыми пользуются разные движки. Им нужно одинаково определять состав таблицы и безопасно согласовывать изменения. Iceberg задаёт формат метаданных и правила работы с состояниями таблицы.

Книга объясняет, как каталог, метаданные и файлы данных работают вместе, почему это помогает с планированием запросов и как применять формат в Spark, Flink, Dremio и AWS Glue. Далее рассматриваются обслуживание, потоковая обработка, безопасность, миграция и конкретные сценарии.

## Что нужно знать заранее

- Основы SQL: таблицы, фильтры, группировки и изменения данных.
- Представление о файлах, объектном хранилище и пакетной обработке данных.
- Для разделов о потоках полезны базовые знания Spark, Flink или Kafka.

## Зачем читать

- Понять разницу между форматом файла и форматом таблиц.
- Проследить запись и чтение через каталог и дерево метаданных.
- Оценивать компромиссы между размером файлов, разбиением и стоимостью обслуживания.
- Узнать, как использовать состояния таблицы для воспроизводимости и восстановления.
- Подготовиться к выбору каталога, интеграции движка и миграции.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| Основы | 1–5 | Архитектура, операции, производительность и каталоги. |
| Движки | 6–9 | Spark, Dremio, AWS Glue и Flink. |
| Практика | 10–14 | Эксплуатация, потоки, безопасность, миграция и примеры применения. |

Первая часть даёт модель таблицы; вторая показывает интерфейсы движков; третья связывает возможности с повседневными задачами инженера.

## Главные идеи

| Идея | Глава |
|---|---|
| Дерево метаданных связывает состояние таблицы с файлами. | [Архитектура](/book-summaries/engineering/apache-iceberg-the-definitive-guide/02-architecture/) |
| Фиксация публикует подготовленное изменение через каталог. | [Запись и чтение](/book-summaries/engineering/apache-iceberg-the-definitive-guide/03-write-and-read-queries/) |
| Размер файлов и организация данных влияют на затраты чтения. | [Производительность](/book-summaries/engineering/apache-iceberg-the-definitive-guide/04-performance/) |
| Ветки и история помогают проверять и восстанавливать состояния. | [Эксплуатация](/book-summaries/engineering/apache-iceberg-the-definitive-guide/10-production/) |
| Права на файлы и права в движке защищают разные пути доступа. | [Безопасность](/book-summaries/engineering/apache-iceberg-the-definitive-guide/12-governance-and-security/) |

## Как читать

- **Новичку:** главы 1–3, затем выбранный движок и глава 10.
- **Analytics engineer:** главы 1–4, 7, 12 и 14 — таблицы, запросы, доступ и BI.
- **Data engineer:** главы 1–6, затем нужные интеграции и главы 10–14.
- **Руководителю:** главы 1, 5, 12–14 для выбора архитектуры, управления и перехода.

## Как работать с практикой

В главах указаны версии и среда для проверенных примеров. Spark и PyIceberg создают локальные временные таблицы; для других примеров отдельно указаны необходимые сервисы и ограничения. Перед запуском в своей среде проверяйте пути и последствия записи: операции создания, миграции и обслуживания меняют состояние каталога или хранилища.

## Разбор по главам

| Глава | О чём |
|---|---|
| [1. Введение](/book-summaries/engineering/apache-iceberg-the-definitive-guide/01-introduction/) | Зачем lakehouse нужен формат таблиц. |
| [2. Архитектура](/book-summaries/engineering/apache-iceberg-the-definitive-guide/02-architecture/) | Как каталог, метаданные и файлы образуют таблицу. |
| [3. Запись и чтение](/book-summaries/engineering/apache-iceberg-the-definitive-guide/03-write-and-read-queries/) | Как фиксируются изменения и выбираются файлы. |
| [4. Производительность](/book-summaries/engineering/apache-iceberg-the-definitive-guide/04-performance/) | Как размеры файлов, сортировка и разбиение влияют на запросы. |
| [5. Каталоги](/book-summaries/engineering/apache-iceberg-the-definitive-guide/05-catalogs/) | Как выбрать каталог и перенести регистрацию. |
| [6. Apache Spark](/book-summaries/engineering/apache-iceberg-the-definitive-guide/06-apache-spark/) | Как настроить Spark и выполнять операции с таблицами. |
| [7. Dremio](/book-summaries/engineering/apache-iceberg-the-definitive-guide/07-dremio/) | Как работать с Iceberg через SQL Dremio. |
| [8. AWS Glue](/book-summaries/engineering/apache-iceberg-the-definitive-guide/08-aws-glue/) | Как настроить задание Glue и каталог. |
| [9. Apache Flink](/book-summaries/engineering/apache-iceberg-the-definitive-guide/09-apache-flink/) | Как выполнять пакетные и потоковые задания. |
| [10. Эксплуатация](/book-summaries/engineering/apache-iceberg-the-definitive-guide/10-production/) | Как наблюдать метаданные и управлять состояниями. |
| [11. Потоковая обработка](/book-summaries/engineering/apache-iceberg-the-definitive-guide/11-streaming/) | Как читать и записывать потоки с учётом восстановления. |
| [12. Управление и безопасность](/book-summaries/engineering/apache-iceberg-the-definitive-guide/12-governance-and-security/) | Как защищать файлы, представления и каталог. |
| [13. Миграция](/book-summaries/engineering/apache-iceberg-the-definitive-guide/13-migration/) | Как перенести существующие данные и переключить потребителей. |
| [14. Примеры применения](/book-summaries/engineering/apache-iceberg-the-definitive-guide/14-use-cases/) | Как устроить проверку качества, BI и обработку изменений. |
