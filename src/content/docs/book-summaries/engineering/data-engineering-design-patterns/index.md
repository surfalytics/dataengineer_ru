---
title: "Data Engineering Design Patterns — конспект книги"
head:
  - tag: title
    content: "Data Engineering Design Patterns: конспект | Инжиниринг Данных"
description: "Конспект книги Data Engineering Design Patterns на русском. Загрузка, идемпотентность, ошибки, качество, наблюдаемость: 10 глав и около 70 паттернов."
author: "Bartosz Konieczny"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - data-engineering
  - patterns
---

**Data Engineering Design Patterns: Recipes for Solving the Most Common Data Engineering Problems** — книга Bartosz Konieczny (O'Reilly, 2025). Автор собрал около 70 повторяющихся решений для задач дата-инженера. Книга идёт по жизни проекта: от загрузки данных до наблюдаемости. В ней 10 глав.

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.

## О чём книга простыми словами

Дата-инженеры решают одни и те же задачи в каждой компании: загрузить данные, не потерять их при сбое, не задвоить при перезапуске, добавить ценность, защитить, хранить так, чтобы запросы шли быстро, и проверять качество. Обычно каждая команда придумывает решения заново, а у решений нет общих имён. Из-за этого трудно обсуждать дизайн и учиться на чужом опыте.

Konieczny применяет к данным идею design patterns из software engineering. Паттерн - это повторяющееся решение типовой проблемы, у которого есть имя. У него три части: проблема, решение и последствия (цена решения). Паттерны не привязаны к одному продукту: примеры на Spark, Airflow, Kafka, Delta Lake и SQL показывают идею, а не рецепт для одного инструмента.

Главная идея книги: у любого решения есть цена. `Full Loader` прост, но дорог на больших объёмах. `Aligned Fan-In` быстро показывает ошибки, но ждёт самую медленную ветку. Поэтому автор в каждом паттерне описывает, что вы получаете и чем платите.

## Что нужно знать заранее

- Основы SQL: `JOIN`, `GROUP BY`, агрегаты. Подойдёт [раздел SQL](/practice/sql/) и страница [SQL](/processing/sql/).
- Что такое ETL и пайплайн данных: [ETL](/processing/etl/).
- Общее представление о хранилище данных и моделировании: [DW](/processing/dw/), [моделирование данных](/processing/data-modelling/).
- Немного Python и понимание batch и streaming: [Spark](/processing/spark/), [streaming](/processing/streaming/).
- Знать все инструменты из примеров не нужно. Достаточно понимать идею.

## Зачем читать

- **Общий язык.** У решений есть имена: `Full Loader`, `Dead-Letter`, `Windowed Deduplicator`. Командам проще обсуждать дизайн.
- **Готовые решения.** Каждый паттерн описывает проблему, решение и цену решения.
- **Не привязана к одному продукту.** Примеры на Spark, Airflow, Kafka и SQL. Идеи работают и с `dbt`, и с облачными сервисами.
- **Идемпотентность и ошибки.** Две главы о том, как делать пайплайны, которые можно безопасно перезапустить.
- **Качество и наблюдаемость.** Как ловить плохие данные и задержки до того, как их заметит бизнес.

## Как устроена книга

У каждого паттерна три части: Problem, Solution, Consequences. Паттерны сгруппированы в категории внутри главы.

| Часть | Главы | О чём |
|---|---|---|
| Основы | 1 | Что такое паттерны, учебный кейс книги |
| Загрузка и надёжность | 2–4 | Ingestion, обработка ошибок, идемпотентность |
| Работа с данными | 5–6 | Обогащение, агрегация, сессии, порядок, потоки задач |
| Безопасность и хранение | 7–8 | Удаление, доступ, защита данных, партиции, форматы |
| Качество и контроль | 9–10 | Проверки, схемы, наблюдаемость, lineage |

Части идут по пути данных. Сначала данные нужно получить (глава 2), пережить сбои и повторы (3–4), затем добавить ценность и связать пайплайны (5–6). Потом данные нужно защитить и разложить для быстрого чтения (7–8). Последние главы отвечают на вопрос, можно ли им верить и видим ли мы сбои раньше потребителей (9–10).

## Главные идеи

| Идея | Где разбирается |
|---|---|
| Паттерн = проблема, решение, цена решения | [Глава 1](/book-summaries/engineering/data-engineering-design-patterns/01-introduction/) |
| Загружать можно целиком или инкрементально, и у каждого способа свои риски | [Глава 2](/book-summaries/engineering/data-engineering-design-patterns/02-data-ingestion/) |
| Ошибки в данных нужно изолировать, а не ронять весь пайплайн | [Глава 3](/book-summaries/engineering/data-engineering-design-patterns/03-error-management/) |
| Пайплайн должен давать тот же результат при каждом повторе | [Глава 4](/book-summaries/engineering/data-engineering-design-patterns/04-idempotency/) |
| Ценность дают обогащение, агрегация, сессии и порядок | [Глава 5](/book-summaries/engineering/data-engineering-design-patterns/05-data-value/) |
| Границы задач и запусков определяют надёжность потока | [Глава 6](/book-summaries/engineering/data-engineering-design-patterns/06-data-flow/) |
| Безопасность: удаление, минимум прав, шифрование, секреты | [Глава 7](/book-summaries/engineering/data-engineering-design-patterns/07-data-security/) |
| Раскладка данных заменяет вычислительную мощность | [Глава 8](/book-summaries/engineering/data-engineering-design-patterns/08-data-storage/) |
| Качество строится в три слоя: контроль, схема, наблюдение | [Глава 9](/book-summaries/engineering/data-engineering-design-patterns/09-data-quality/) |
| Нужно видеть сбои и происхождение данных, а не только проверять данные | [Глава 10](/book-summaries/engineering/data-engineering-design-patterns/10-data-observability/) |

## Как читать

- **Новичок.** Начните с глав 2 и 4: загрузка и идемпотентность. Это основа любого пайплайна.
- **Analytics engineer.** Главы 4, 5, 8 и 9: перезапуск моделей, обогащение, `denormalization`, проверки качества.
- **Data engineer.** Читайте по порядку. Используйте главы как справочник при дизайне пайплайна.
- **Руководитель.** Главы 1, 3, 9 и 10: надёжность, качество и контроль SLA.

## Разбор по главам

| Глава | О чём |
|---|---|
| [1. Введение](/book-summaries/engineering/data-engineering-design-patterns/01-introduction/) | Что такое паттерны, учебный кейс |
| [2. Загрузка данных](/book-summaries/engineering/data-engineering-design-patterns/02-data-ingestion/) | Full и incremental load, CDC, репликация, compaction |
| [3. Обработка ошибок](/book-summaries/engineering/data-engineering-design-patterns/03-error-management/) | Dead-letter, дубликаты, late data, checkpoint |
| [4. Идемпотентность](/book-summaries/engineering/data-engineering-design-patterns/04-idempotency/) | Overwrite, merge, keyed idempotency, immutable dataset |
| [5. Ценность данных](/book-summaries/engineering/data-engineering-design-patterns/05-data-value/) | Обогащение, агрегация, сессии, порядок |
| [6. Поток данных](/book-summaries/engineering/data-engineering-design-patterns/06-data-flow/) | Sequence, fan-in, fan-out, оркестрация |
| [7. Безопасность](/book-summaries/engineering/data-engineering-design-patterns/07-data-security/) | Удаление данных, доступ, шифрование, секреты |
| [8. Хранение](/book-summaries/engineering/data-engineering-design-patterns/08-data-storage/) | Партиции, bucket, сортировка, normalizer и denormalizer |
| [9. Качество данных](/book-summaries/engineering/data-engineering-design-patterns/09-data-quality/) | Audit-Write-Audit-Publish, схемы, наблюдатели |
| [10. Наблюдаемость](/book-summaries/engineering/data-engineering-design-patterns/10-data-observability/) | Детекторы, lag, SLA, lineage |
