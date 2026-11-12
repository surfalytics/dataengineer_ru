---
title: "The Data Warehouse Toolkit — конспект книги"
head:
  - tag: title
    content: "The Data Warehouse Toolkit: конспект и SQL | Инжиниринг Данных"
description: "Конспект The Data Warehouse Toolkit (Kimball) на русском. Dimensional modeling, star schema, SCD, fact tables, ETL. Схемы и практика на DuckDB для каждой главы."
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**The Data Warehouse Toolkit, 3rd Edition** — книга Ralph Kimball и Margy Ross (Wiley, 2013). Это главный учебник по `dimensional modeling`. В ней 21 глава: приёмы моделирования, 11 отраслевых кейсов, жизненный цикл проекта, ETL и big data. Это конспект на русском. К каждой главе есть схема и практика на DuckDB.

> Это собственный пересказ, а не перевод. За полным текстом идите в оригинал. Схемы и данные для SQL придуманы заново.

## Зачем читать

- Dimensional modeling — основа `dbt`-проектов и BI-витрин. Слои `fct_*` и `dim_*` пришли из этой книги.
- Книга нужна не только data engineer. Analytics engineer и аналитик тоже строят и читают star schema.
- Приёмы работают в любом хранилище: Snowflake, BigQuery, Redshift, DuckDB.
- Книга учит на примерах из отраслей. Вы сравниваете свой случай с готовым.
- Глава 2 — справочник: все приёмы моделирования на нескольких страницах.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| Основы | 1–2 | DW/BI, star schema, все приёмы моделирования |
| Бизнес-процессы | 3–9 | Розница, склад, закупки, заказы, учёт, CRM, HR |
| Отрасли | 10–16 | Финансы, телеком, транспорт, образование, медицина, e-commerce, страхование |
| Проект и ETL | 17–20 | Жизненный цикл, процесс моделирования, 34 подсистемы ETL |
| Big data | 21 | Большие данные и аналитика |

## Главные приёмы моделирования

| Приём | Где разбирается |
|---|---|
| Grain, fact, dimension, star schema | [Глава 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) |
| Slowly changing dimensions (SCD 0–7) | [Глава 2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) |
| Conformed dimensions и bus matrix | Главы 1, 4, 18 |
| Три типа fact table: transaction, snapshot, accumulating | Главы 4, 6 |
| Junk, role-playing, degenerate dimensions | Главы 2, 6 |
| Bridge table для связи many-to-many | Главы 8, 10, 14 |
| Mini-dimension | Главы 8, 10 |
| Factless fact table | Главы 6, 13 |

## Как читать

- **Новичок.** Главы 1–3, затем 4 и 6. После них хватает для первой витрины.
- **Analytics engineer.** Главы 2, 3, 6, 8, 9. Затем 19–20 про загрузку.
- **Data engineer.** Главы 2, 19, 20 и отраслевая глава, близкая к вашей работе.
- **Руководитель.** Главы 1, 17, 18.

## Как работать с практикой

- Установите DuckDB: `brew install duckdb` или откройте [shell.duckdb.org](https://shell.duckdb.org).
- Данные в каждой главе создаются SQL-кодом. Файлы скачивать не нужно.
- Блоки кода идут по порядку. Выполняйте их сверху вниз в одной сессии.
- Сначала решайте задание сами. Потом открывайте решение.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. DW/BI и основы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/01-dw-bi-primer/) | Архитектура DW/BI, Kimball и Inmon, star schema и OLAP |
| [2. Приёмы dimensional modeling](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/) | Справочник приёмов: SCD, виды fact table, conformance |
| [3. Продажи в рознице](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) | Четыре шага проектирования, star schema |
| [4. Склад](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/) | Snapshot, accumulating snapshot, semi-additive |
| [5. Закупки](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/) | Заказы поставщикам, общие dimensions |
| [6. Заказы](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/) | Заголовок и строки, role-playing, pipeline |
| [7. Бухгалтерский учёт](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/) | Главная книга, бюджеты, проводки |
| [8. CRM](/book-summaries/engineering/data-warehouse-toolkit/08-crm/) | Клиент 360, mini-dimension, поведение |
| [9. HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/) | История сотрудников, иерархии, навыки |
| [10. Финансовые услуги](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) | Счета, домохозяйства, bridge |
| [11. Телеком](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/) | Биллинг, звонки, география |
| [12. Транспорт](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/) | Маршруты и сегменты, role-playing |
| [13. Образование](/book-summaries/engineering/data-warehouse-toolkit/13-education/) | Приём, регистрация, посещаемость |
| [14. Медицина](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/) | Диагнозы, bridge с весами |
| [15. E-commerce](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/) | Clickstream, сессии, воронки |
| [16. Страхование](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/) | Полисы, покрытия, убытки |
| [17. Жизненный цикл Kimball](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/) | Этапы DW/BI-проекта |
| [18. Процесс моделирования](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/) | Bus matrix, workshops, проверка grain |
| [19. Подсистемы ETL](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/) | 34 подсистемы ETL |
| [20. Разработка ETL](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/) | Проектирование и запуск ETL |
| [21. Big data](/book-summaries/engineering/data-warehouse-toolkit/21-big-data-analytics/) | Big data и dimensional modeling |
