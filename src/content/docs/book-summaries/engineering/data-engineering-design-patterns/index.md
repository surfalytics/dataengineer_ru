---
title: "Data Engineering Design Patterns — конспект книги"
head:
  - tag: title
    content: "Data Engineering Design Patterns: конспект | Инжиниринг Данных"
description: "Конспект книги Data Engineering Design Patterns на русском. Загрузка, идемпотентность, ошибки, качество, наблюдаемость: 10 глав и около 70 паттернов."
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - data-engineering
  - patterns
---

**Data Engineering Design Patterns: Recipes for Solving the Most Common Data Engineering Problems** — книга Bartosz Konieczny (O'Reilly, 2025). Автор собрал около 70 повторяющихся решений для задач дата-инженера. Книга идёт по жизни проекта: от загрузки данных до наблюдаемости. В ней 10 глав.

> Это собственный пересказ, а не перевод. За полным текстом, кодом и примерами идите в оригинал.

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
