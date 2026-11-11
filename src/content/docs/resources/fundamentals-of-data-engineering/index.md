---
title: "Fundamentals of Data Engineering — конспект книги"
head:
  - tag: title
    content: "Fundamentals of Data Engineering: конспект | Инжиниринг Данных"
description: "Конспект книги Fundamentals of Data Engineering на русском. Жизненный цикл данных, архитектура, выбор технологий, разбор всех глав и приложений."
sidebar:
  order: 10
  label: "Fundamentals of Data Engineering"
tags:
  - books
  - data-engineering
---

**Fundamentals of Data Engineering** — книга Joe Reis и Matt Housley (O'Reilly, 2022). Она объясняет профессию data engineer через единую рамку: жизненный цикл данных. В книге 11 глав и 2 приложения в трёх частях. Это конспект на русском с разбором по главам и схемами.

> Это собственный пересказ, а не перевод. За полным текстом и примерами идите в оригинал. Схемы нарисованы заново по содержанию глав.

![Карта книги: три части, главы жизненного цикла и приложения](/assets/fundamentals-of-data-engineering/ch00-book-map.png)

## Зачем нужна эта книга

Книга не учит одному инструменту. Авторы прямо пишут, что такие книги быстро устаревают. Они описывают то, что остаётся стабильным.

- **Единый взгляд на профессию.** Работа data engineer описана целиком: от источника данных до потребителя.
- **Вне привязки к инструментам.** Технологии меняются, этапы жизненного цикла остаются.
- **Жизненный цикл.** Генерация, хранение, приём, трансформация, выдача. Плюс сквозные темы (`undercurrents`): безопасность, управление данными, `DataOps`, архитектура, оркестрация.
- **Архитектура.** Книга объясняет, как собрать компоненты в рабочую систему. Архитектура и выбор технологий разделены.
- **Как выбирать технологии.** Рамка помогает отличать пользу от маркетинга.
- **Язык для разговора с бизнесом.** Вы лучше объясните, что делаете, и поймёте, что нужно потребителям данных.

## Для кого

| Роль | Что получит |
|---|---|
| Software engineer, data scientist, аналитик, который идёт в data engineering | Полную картину профессии и порядок изучения |
| Data engineer, который знает отдельные технологии | Широкий взгляд и общий язык |
| Тимлид, руководитель данных | Понимание, из чего состоит работа команды и на что смотреть |

Авторы ожидают знакомства с SQL, Python и облачными сервисами. Подход в книге cloud-first, но большинство идей работает и без облака.

## Как устроена книга

| Часть | О чём | Главы |
|---|---|---|
| I. Foundation and Building Blocks | Определение профессии, жизненный цикл, архитектура, выбор технологий | 1–4 |
| II. The Data Engineering Lifecycle in Depth | Каждый этап цикла в отдельной главе. Ядро книги | 5–9 |
| III. Security, Privacy, and the Future | Безопасность, приватность, взгляд в будущее | 10–11 |
| Приложения | Сериализация и сжатие, сети в облаке | A, B |

## Как читать

- **Новичок.** Читайте на уровне идей. Незнакомые термины выписывайте и ищите отдельно. Потом перечитайте. Практикуйте SQL и Python на малых данных в облаке и следите за стоимостью.
- **Опытный инженер.** Начните с глав 2–4, затем берите этапы, где у вас пробелы. Главы 10 и 11 и приложения читайте по нужде.
- **Менеджер.** Главы 1–4 и 10. Они дают рамку, архитектуру, выбор технологий и риски.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Что такое data engineering](/resources/fundamentals-of-data-engineering/01-data-engineering-described/) | Определение профессии, зрелость, роли, связь с data science |
| [2. Жизненный цикл](/resources/fundamentals-of-data-engineering/02-data-engineering-lifecycle/) | Пять этапов и сквозные темы |
| [3. Хорошая архитектура данных](/resources/fundamentals-of-data-engineering/03-designing-good-data-architecture/) | Принципы, виды архитектур |
| [4. Выбор технологий](/resources/fundamentals-of-data-engineering/04-choosing-technologies/) | Критерии выбора, стоимость, build или buy |
| [5. Источники данных](/resources/fundamentals-of-data-engineering/05-data-generation-in-source-systems/) | Откуда берутся данные, как с ними работать |
| [6. Хранение](/resources/fundamentals-of-data-engineering/06-storage/) | Системы и абстракции хранения |
| [7. Приём данных](/resources/fundamentals-of-data-engineering/07-ingestion/) | Batch и streaming, способы загрузки |
| [8. Запросы, моделирование, трансформация](/resources/fundamentals-of-data-engineering/08-queries-modeling-and-transformation/) | Как работают запросы, моделирование данных |
| [9. Выдача данных](/resources/fundamentals-of-data-engineering/09-serving-data/) | Analytics, ML, reverse ETL |
| [10. Безопасность и приватность](/resources/fundamentals-of-data-engineering/10-security-and-privacy/) | Защита данных и соблюдение правил |
| [11. Будущее профессии](/resources/fundamentals-of-data-engineering/11-future-of-data-engineering/) | Тенденции и прогнозы авторов |
| [12. Приложения](/resources/fundamentals-of-data-engineering/12-appendices/) | Сериализация, сжатие, сети в облаке |
