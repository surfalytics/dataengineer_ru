---
title: "Data Pipelines with Apache Airflow — конспект книги"
head:
  - tag: title
    content: "Apache Airflow: конспект книги Data Pipelines | Инжиниринг Данных"
description: "Конспект книги Data Pipelines with Apache Airflow на русском: DAG, расписания, assets, операторы, тесты, production и безопасность. Разбор 17 глав со схемами."
author: "Julian de Ruiter и др."
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - airflow
  - data-engineering
---

**Data Pipelines with Apache Airflow, 2nd edition. Orchestration for data and AI** — книга Julian de Ruiter, Ismael Cabral, Kris Geusebroek, Daniel van der Ende и Bas Harenslak (Manning, 2026). Она учит строить и запускать pipelines в Apache Airflow 3. В книге 17 глав в четырёх частях: основы, расширение Airflow, два проекта и работа в production.

> Это собственный пересказ, а не перевод. За полным текстом и кодом идите в оригинал. Схемы нарисованы заново по содержанию глав.

## Зачем читать

- **Основы без воды.** DAG, tasks, operators, расписания и перезапуск после сбоя.
- **Новое в Airflow 3.** Assets, DAG versioning, deferrable operators, изменения в `catchup`.
- **Идемпотентность и атомарность.** Как писать tasks, которые можно безопасно повторить.
- **Своя логика.** Hooks, operators и sensors, тесты и запуск задач в контейнерах.
- **Production.** Executors, метрики, безопасность и варианты развёртывания.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| 1. Getting started | 1–6 | Что такое Airflow, первый DAG, расписания по времени и по данным, templating, зависимости |
| 2. Beyond the basics | 7–11 | Внешние события, связь с системами, свои operators, тесты, контейнеры |
| 3. Airflow in practice | 12–14 | Best practices и два проекта: транспорт NYC и GenAI с RAG |
| 4. Airflow in production | 15–17 | Эксплуатация, безопасность, развёртывание |

## Главные идеи

| Идея | Где |
|---|---|
| Pipeline это граф небольших задач | [Глава 1](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/) |
| Расписание через `data interval`, а не «время запуска» | [Глава 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/) |
| Связь DAG через `asset`, а не через общий cron | [Глава 4](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/) |
| Task должна быть атомарной и идемпотентной | [Глава 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/), [глава 12](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/) |
| Airflow оркестрирует, тяжёлую работу делают другие системы | [Глава 8](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/) |
| Код DAG лёгкий: его парсят постоянно | [Глава 12](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/) |
| Production: executor, метрики, секреты, развёртывание | [Главы 15–17](/book-summaries/engineering/data-pipelines-with-apache-airflow/15-operating-in-production/) |

## Как читать

| Роль | Путь |
|---|---|
| Новичок | Главы 1–6 подряд. Потом 12 |
| Analytics engineer | Главы 1–3, 5, 6, 12 |
| Data engineer | Вся книга. Особенно 4, 7–9, 12, 15 |
| Platform engineer | Главы 11, 15, 16, 17 |
| Руководитель | Главы 1, 12, 15, 17 |

## Как работать с примерами

- В главах есть короткие примеры на Python. Имена в них свои, это не код из книги.
- Все примеры проверены на Airflow 3.4. DAG без внешних систем проходят `airflow dags test`. Hooks, operators и triggers проверены в pytest с mock.
- Примеры с Docker, Kubernetes, Kafka, S3 и HTTP только загружаются. Для запуска нужны эти сервисы.
- Проверку можно повторить: `scripts/airflow-book-check/check.sh` в [репозитории сайта](https://github.com/surfalytics/dataengineer_ru).

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Знакомство с Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/) | Pipeline как граф, компоненты Airflow, когда его выбирать |
| [2. Анатомия DAG](/book-summaries/engineering/data-pipelines-with-apache-airflow/02-anatomy-of-dag/) | Первый DAG, tasks и operators, перезапуск, DAG versioning |
| [3. Расписания по времени](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/) | Trigger и data interval timetables, backfill, идемпотентность |
| [4. Asset-aware scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/) | Producer и consumer DAG, события assets |
| [5. Templating и контекст](/book-summaries/engineering/data-pipelines-with-apache-airflow/05-templating-context/) | Jinja, `context`, шаблоны в operators |
| [6. Зависимости задач](/book-summaries/engineering/data-pipelines-with-apache-airflow/06-task-dependencies/) | Ветки, условия, trigger rules, XCom, Taskflow API |
| [7. Внешние события](/book-summaries/engineering/data-pipelines-with-apache-airflow/07-triggering-external-input/) | Sensors, REST API, сообщения |
| [8. Внешние системы](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/) | ML pipeline, A-to-B operators |
| [9. Свои operators](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/) | Hooks, operators, sensors, deferrable |
| [10. Тестирование](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/) | DAG integrity test, unit tests, mock, CI/CD |
| [11. Задачи в контейнерах](/book-summaries/engineering/data-pipelines-with-apache-airflow/11-tasks-in-containers/) | DockerOperator, KubernetesPodOperator |
| [12. Best practices](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/) | Чистый код, идемпотентность, dynamic task mapping |
| [13. Проект: транспорт NYC](/book-summaries/engineering/data-pipelines-with-apache-airflow/13-project-nyc-transport/) | Свой operator, raw и processed слои |
| [14. Проект: GenAI и рецепты](/book-summaries/engineering/data-pipelines-with-apache-airflow/14-project-genai-family-traditions/) | RAG, векторная база, Weaviate |
| [15. Airflow в production](/book-summaries/engineering/data-pipelines-with-apache-airflow/15-operating-in-production/) | Executors, логи, метрики, алерты |
| [16. Безопасность](/book-summaries/engineering/data-pipelines-with-apache-airflow/16-securing-airflow/) | RBAC, Fernet, secrets backend, HTTPS |
| [17. Развёртывание](/book-summaries/engineering/data-pipelines-with-apache-airflow/17-deployment-options/) | Managed сервисы, Helm Chart, доставка DAG |
