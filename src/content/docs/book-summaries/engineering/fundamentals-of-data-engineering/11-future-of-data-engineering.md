---
title: "Fundamentals of Data Engineering, глава 11: Будущее профессии"
head:
  - tag: title
    content: "Будущее data engineering и live data stack | Инжиниринг Данных"
description: "Конспект главы 11 книги Fundamentals of Data Engineering на русском. Тренды: простые инструменты, cloud data OS, live data stack, роли."
sidebar:
  order: 11
  label: "11. Будущее профессии"
tags:
  - books
  - data-engineering
---

**Главная мысль:** жизненный цикл data engineering останется. Инструменты станут проще, а инженеры перейдут к задачам более высокого уровня. Авторы также ожидают переход от batch к live data stack.

![Эволюция от Modern Data Stack к Live Data Stack](/assets/fundamentals-of-data-engineering/ch11-mds-to-live.png)

Авторы честно называют часть прогнозов спекуляцией. Одни тренды уже заметны, другие только намечаются.

## Профессия не исчезнет

- Простые инструменты снижают порог входа, но не заменяют инженеров.
- Новые способы использовать данные требуют новых систем.
- Data engineers поднимаются выше по уровню задач.

## Меньше сложности, больше простых инструментов

- Технологии big data стали доступны всем: BigQuery, Snowflake, EMR.
- Open source стал managed: Cloud Composer, managed Airflow, managed Kubernetes. Можно начать с managed и перейти на self-managed.
- Готовые коннекторы (Fivetran, Airbyte) освобождают время.
- Конкуренция делает инструменты проще и богаче по функциям.

## Cloud-scale data OS и interoperability

- Сервисы вроде BigQuery, Snowflake и Lambda похожи на службы операционной системы, но работают на многих машинах.
- Следующий шаг: стандартизованные data APIs.
- Object storage станет слоем обмена. Parquet и Avro заменяют CSV и сырой JSON.
- Нужен новый metadata catalog вместо старого Hive Metastore.
- Оркестраторы (Airflow, Dagster, Prefect) станут data-aware: каталог, lineage, IaC и деплой кода.
- Улучшится управление streaming DAG.

## "Enterprisey" data engineering

- Управление, DataOps, governance и качество перестанут быть только делом больших компаний.
- Авторы называют это "enterprisey". Ничего плохого в слове нет: это "скучные", но нужные практики.

## Роли размываются

- Границы между software, data, data science и ML engineering стираются.
- Появится роль между ML и data engineering: автоматизация обучения, мониторинг моделей и данных.
- Software engineers станут глубже знать streaming, pipelines и качество данных. Подход "перебросить через стену" уйдёт.

## От Modern Data Stack к Live Data Stack

| | Modern Data Stack (MDS) | Live Data Stack |
|---|---|---|
| Данные | Bounded, batch | Unbounded, поток |
| Основа | Cloud data warehouse, ELT | Streaming pipelines, real-time OLAP |
| Цель | BI и аналитика: что и когда | Автоматические действия и ML в приложении |
| Примеры | Warehouse, SaaS pipelines | Druid, ClickHouse, Rockset, Firebolt |

- Авторы считают, что MDS это старые практики warehouse в новой упаковке.
- Если действие после отчёта повторяется, его можно автоматизировать на событиях.
- Streaming и real-time OLAP станут основой. Batch ingestion будет редким.
- Ожидается переход от ELT к `STL` (stream, transform, load).
- Data modeling нужно пересмотреть. Определения метрик и семантики появятся ближе к источнику (upstream definitions layer).
- Приложения и data stack сольются. Следите за базами для OLTP и OLAP и за feature stores.
- Приложения и ML будут тесно связаны через короткие циклы обратной связи.

![Тренды: устойчивые и менее определённые](/assets/fundamentals-of-data-engineering/ch11-trends.png)

## Spreadsheets как dark matter

- Таблицы это самая массовая платформа данных. Пользователей сотни миллионов.
- Большая часть аналитики живёт в таблицах и не попадает в современные системы.
- BI не дал такой же интерактивности. Авторы ждут инструменты, сочетающие интерфейс таблицы и мощь cloud OLAP.

## Ключевые термины

| Термин (EN) | Что значит |
|---|---|
| Modern data stack (MDS) | Cloud warehouse, ELT, SaaS pipelines, BI |
| Live data stack | Стек на streaming и real-time OLAP для приложений |
| STL | Stream, transform, load: преобразование в потоке |
| Cloud data OS | Набор облачных сервисов как слой операционной системы |
| Real-time OLAP | База для быстрого приёма и субсекундных запросов |
| Feature store | Хранилище признаков для ML |
| Enterprisey | Больше governance, DataOps и операций |
| Dark matter data | Данные в таблицах вне основных систем |

## Что это значит на практике

- Инвестируйте в основы жизненного цикла. Они переживут смену инструментов.
- Предпочитайте managed сервисы и коннекторы для рутины.
- Опирайтесь на открытые форматы и object storage.
- Изучайте streaming и real-time OLAP, но проверяйте реальную пользу для бизнеса.
- Развивайте знания о ML и о разработке приложений.
- Не забывайте про таблицы: пользователи часто работают именно в них.

## Вопросы для самопроверки

1. Почему авторы считают, что простота инструментов не уберёт профессию?
2. Чем live data stack отличается от modern data stack?
3. Что такое STL и чем оно отличается от ELT?
4. Почему авторы говорят о spreadsheets как о dark matter?

Предыдущая: [Безопасность и приватность](/book-summaries/engineering/fundamentals-of-data-engineering/10-security-and-privacy/). Следующая: [Приложения](/book-summaries/engineering/fundamentals-of-data-engineering/12-appendices/).
