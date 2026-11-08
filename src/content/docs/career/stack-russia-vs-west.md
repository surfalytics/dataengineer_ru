---
title: "Стек данных: РФ и Запад"
description: "Какие инструменты данных используют в России и на Западе. Типовые архитектуры, общая база и что учить под каждый рынок."
sidebar:
  order: 4
  label: Стек РФ vs Запад
tags:
  - career
---

Инструменты для работы с данными в России и на Западе сильно отличаются. Поэтому сначала решите, на какой рынок вы хотите работать. Потом учите стек этого рынка.

- **Россия:** open source, свои серверы (on-prem), Kubernetes. Главные слова: Greenplum, ClickHouse, Hadoop, Spark, Airflow, Superset.
- **Запад** (США, Европа, Азия, Австралия): облако и платные сервисы (SaaS). Главные слова: Snowflake, Databricks, BigQuery, dbt, Power BI, Tableau, AWS, Azure.

Если вы смотрите на валютную удаленку, читайте также [Валютная удаленка и работа за границей](/career/foreign-work/).

:::note
Страница собрана в ноябре 2026 года. Источники: вакансии крупных компаний, статьи на Хабре и инженерных блогах, опросы. Список в конце страницы. Это типичная картина, а не правило для каждой компании.
:::

## Типичная архитектура в РФ

![Типичный стек данных в РФ](/assets/career/stack-russia.png)

Что важно знать:

- **Все свое.** Компании держат данные на своих серверах. Облако есть (Yandex Cloud, VK Cloud, Selectel, Cloud.ru), но крупный бизнес ему мало доверяет. По опросу 2024 года 80% компаний держат BI на своих серверах.
- **Greenplum и его форки.** Главное MPP-хранилище. В 2024 году Broadcom закрыл код Greenplum. Теперь компании используют форки: Arenadata DB, Greengage, Cloudberry.
- **ClickHouse почти везде.** Обычно для витрин и быстрых отчетов. Иногда это главное хранилище.
- **Hadoop еще жив.** HDFS + Hive + Spark есть в банках, телекоме, ритейле (МТС, Альфа, X5, Ozon). Но новые платформы строят на S3 (Ceph, MinIO).
- **Trino + Iceberg — главный тренд.** Avito, Лемана ПРО, Ozon уже на Trino. Облака продают managed Trino.
- **Vertica.** Вендор ушел из РФ, но Vertica все еще стоит в Ozon и Avito. Они с нее уходят.
- **Свои платформы.** Яндекс использует YTsaurus. Сбер — SberData Platform. Эти навыки плохо переносятся в другие компании.
- **BI.** В IT-компаниях это Superset и DataLens. В enterprise и госсекторе — российские вендоры: Visiology, Luxms, Форсайт, FineBI. После 2022 года доля российских BI выросла с 9% до 68%. Power BI и Tableau почти ушли, иногда остаются как legacy.
- **Git.** GitLab CE на своих серверах. GitLab ушел из РФ в 2022 году. Часть компаний переходит на GitFlic.
- **Загрузка.** Kafka и Debezium (CDC). В банках и госкомпаниях часто Apache NiFi.
- **dbt** встречается (Lamoda, Aviasales, Лемана), но это пока не стандарт. Чаще пишут SQL и Python в Airflow.

## Типичная архитектура на Западе

![Типичный стек данных на Западе](/assets/career/stack-west.png)

Что важно знать:

- **Облако — норма.** AWS, потом Azure, потом GCP. Своих серверов почти нет.
- **Платят за готовое.** Компании покупают SaaS, чтобы не держать свою команду админов. Fivetran загружает данные, Snowflake хранит, dbt трансформирует, Looker показывает.
- **Snowflake и Databricks — лидеры.** В вакансиях: Snowflake 31%, Databricks 29%, BigQuery 14%, Redshift 12%.
- **dbt — стандарт** для Analytics Engineer. Для Data Engineer он в 24% вакансий. dbt Core встречается намного чаще, чем платный dbt Cloud. Самая частая пара: Snowflake + dbt Core, который запускают из Airflow.
- **Airflow — главный оркестратор.** 47% команд. Dagster около 6%, Prefect около 1%. Часто это managed Airflow: MWAA (AWS) или Composer (GCP).
- **Европа — это Azure и Power BI.** В Великобритании Azure в вакансиях встречается чаще, чем AWS. Power BI в 4 раза чаще, чем Tableau. Быстро растет Microsoft Fabric.
- **Databricks — все в одном.** Spark, Delta Lake, ноутбуки, оркестрация (Jobs), SQL-хранилище, каталог (Unity Catalog), ML и даже дашборды. Основа открытая: Spark, Delta и MLflow — open source. Одна команда может закрыть всю платформу без других вендоров.
- **BI.** Power BI, Tableau, Looker — основа. Sigma, Omni, Hex — новые и модные, но их мало в вакансиях.
- **Git.** GitHub и GitHub Actions. Инфраструктура как код: Terraform.

## Тип компании на Западе решает стек

На Западе нет одного стека. Он зависит от типа компании.

| Тип компании | Типичный стек | Почему |
|---|---|---|
| **Enterprise, «Microsoft shop»** (банки, страхование, ритейл, производство) | Azure, ADLS, Databricks или Fabric (lakehouse), Azure Data Factory, Power BI, Azure DevOps | Давний договор с Microsoft. Уже есть Office 365, Active Directory, SQL Server. Проще взять все у одного вендора. |
| **Стартап** | GCP + BigQuery + dbt + Looker, или AWS + Redshift + dbt + Airflow | Быстрый старт, кредиты от облаков для стартапов, мало админов. |
| **Средняя tech/SaaS компания** | Snowflake + dbt Core + Fivetran или Airbyte + Airflow или Dagster + Tableau, Looker или Sigma | «Modern data stack»: лучший инструмент на каждый слой. |
| **Big tech** (Netflix, Uber, Meta, Airbnb) | Свои платформы: Spark, Trino, Iceberg/Hudi на S3, свои оркестраторы | Огромные объемы. Готовые SaaS дороги и не масштабируются. |

Совет: если цель — Европа и крупный enterprise, учите Azure + Databricks + Power BI. Если цель — стартапы и tech, учите Snowflake или BigQuery + dbt + Airflow.

:::tip[Важно]
Big tech на Западе тоже не работает на Snowflake. Netflix, Uber, Airbnb, Meta, Stripe используют Spark, Trino и Iceberg на S3. Это похоже на российский подход. Стек «Snowflake + dbt + Fivetran» — это в основном средние компании и Европа.
:::

## Сравнение по слоям

| Слой | РФ | Запад |
|---|---|---|
| Где живет платформа | Свои серверы, Kubernetes | AWS, Azure, GCP |
| Источники | PostgreSQL, MySQL, Oracle (legacy), 1С | PostgreSQL, MySQL, SaaS (Salesforce, Stripe, HubSpot) |
| Загрузка | Kafka, Debezium, NiFi, Python | Fivetran, Airbyte, Azure Data Factory, Kafka/Confluent, Kinesis |
| Озеро | HDFS, S3 (Ceph, MinIO) | S3, ADLS, GCS |
| Формат таблиц | Hive, Iceberg (растет) | Iceberg, Delta |
| Обработка | Spark, Trino | Spark (Databricks, EMR), Trino, Flink |
| Хранилище | Greenplum / Arenadata DB, ClickHouse, Vertica | Snowflake, Databricks, BigQuery, Redshift, Fabric |
| Трансформации | SQL, Python, иногда dbt-core | dbt Core (чаще), dbt Cloud, Spark SQL |
| Оркестрация | Airflow | Airflow (часто managed), Dagster |
| BI | Superset, DataLens, Visiology, Luxms, Форсайт | Power BI, Tableau, Looker, Sigma, Omni |
| Git и CI/CD | GitLab CE self-hosted, GitFlic | GitHub, GitHub Actions, Terraform |
| Ноутбуки и IDE | Jupyter, DBeaver, DataSphere | Jupyter, Databricks notebooks, Hex |

## Разница в навыках

Отличаются не только названия инструментов. Отличается работа.

| | РФ | Запад |
|---|---|---|
| Что вы делаете | Поднимаете и настраиваете open source сами | Настраиваете готовые сервисы и пишете код поверх них |
| Важные навыки | Linux, Docker, Kubernetes, тюнинг Greenplum и ClickHouse, Hadoop | IAM и доступы, стоимость облака, Terraform, SaaS-коннекторы |
| Главная боль | Железо, обновления, отказоустойчивость | Счет за облако, зоопарк вендоров |
| Чем ценен инженер | Знает внутренности систем | Быстро строит решение из готовых блоков |

## Общая база: учите это в первую очередь

Эти навыки нужны на обоих рынках. С ними легко перейти с одного стека на другой.

- **SQL.** Главный навык везде.
- **Python.** Скрипты, загрузка данных, Spark.
- **Моделирование данных.** Kimball, Data Vault, слои хранилища. Не зависит от инструмента.
- **Spark.** Есть и в РФ, и на Западе.
- **Airflow.** Самый частый оркестратор на обоих рынках.
- **Kafka.** Стандарт для стриминга везде.
- **Trino + Iceberg.** Растут на обоих рынках.
- **Git, Docker, CI/CD.** Нужны всем.
- **dbt.** Стандарт на Западе и набирает популярность в РФ.

## Что учить под конкретный рынок

### Если хотите работать в РФ

1. ClickHouse. Он есть почти в каждой вакансии.
2. Greenplum (Arenadata DB). Как устроено MPP, дистрибуция, партиции.
3. Hadoop-экосистема: HDFS, Hive, Spark на YARN.
4. Kubernetes и Linux на базовом уровне.
5. Superset или DataLens для BI.
6. GitLab CI.

### Если хотите работать на Западе

1. Одно облако. Для США чаще AWS. Для Европы — Azure.
2. Одно облачное хранилище: Snowflake, Databricks или BigQuery. У всех есть бесплатный trial.
3. dbt. Обязателен для Analytics Engineer.
4. Один BI: Power BI (Европа, enterprise) или Tableau/Looker (США).
5. Terraform на базовом уровне.
6. Английский. На собеседовании он важнее любого инструмента.

:::tip[Совет]
Выпишите 20 вакансий из того рынка, куда хотите попасть. Посчитайте, какие инструменты встречаются чаще всего. Учите их. Это лучше любой статьи, потому что рынок меняется каждый год.
:::

## Как это показать в резюме

- Работаете в РФ и хотите на Запад? Пишите про общую базу: Spark, Airflow, Kafka, SQL, моделирование. Сделайте pet-проект на Snowflake или Databricks и dbt. Это закроет пробел.
- Опыт с Greenplum и ClickHouse ценен на Западе. Это MPP и колоночное хранилище, как Redshift и Snowflake. Объясните это словами, а не названием.
- Не пишите названия, которые никто не знает (YTsaurus, Visiology). Пишите, что это за система: «MPP DWH», «BI-платформа».

## Источники

**Россия:**

- 🇷🇺 [Avito: платформа данных на Trino](https://habr.com/ru/companies/avito/articles/979912/) — Trino, Ceph S3, Hive Metastore, уход с Vertica.
- 🇷🇺 [Лемана ПРО: переход с Greenplum на Trino + Iceberg](https://habr.com/ru/articles/909542) — Trino, Iceberg, S3, Kubernetes, dbt в Airflow.
- 🇷🇺 [DWH Яндекс Пэй](https://habr.com/ru/post/957470) — Greenplum, ClickHouse, Kafka, Debezium, Spark, Airflow, DataLens.
- 🇷🇺 [МТС: Big Data платформа](https://habr.com/ru/companies/ru_mts/articles/768302/) — 8 ПБ Hadoop, переход с Tableau на Superset.
- 🇷🇺 [Arenadata и Sapiens: архитектура хранилища](https://habr.com/ru/articles/839516) — Hadoop, Greenplum, ClickHouse, Superset.
- 🇷🇺 [Опрос о BI в крупных компаниях](https://habr.com/ru/amp/publications/825388) — доля российских BI 68%, 80% on-prem.
- 🇷🇺 [Сбер завершил переход на SberData Platform](https://habr.com/ru/news/851690) — отказ от Teradata.
- 🇷🇺 [Greenplum закрыл код](https://www.comnews.ru/content/233630/2024-06-07/2024-w23/1007/zelenaya-sliva-upala-nezreloy-rossiyskie-subd-baze-greenplum-okazalis-zone-riska) — что это значит для российских СУБД.
- 🇷🇺 [Магнит переходит на GitFlic](https://www.comnews.ru/digital-economy/content/245934/2026-06-22/2026-w26/1012/magnit-vnedryaet-gitflic-rossiyskuyu-alternativu-gitlab)

**Запад:**

- 🇬🇧 ⭐ [Practical Data: 2026 State of Data Engineering](https://joereis.github.io/practical_data_data_eng_survey/) — опрос 1 101 инженера: платформы, оркестрация, AI.
- 🇬🇧 [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/technology/) — облака и базы данных.
- 🇬🇧 [dbt Labs: State of Analytics Engineering 2025](https://www.getdbt.com/blog/state-of-analytics-engineering-2025-summary)
- 🇬🇧 [Анализ 6 877 вакансий Data Engineer (2026)](https://dev.to/gnana_6392e836fd500a957dc/data-engineer-skills-companies-want-in-2026-6877-posting-analysis-44p9) — доли инструментов в вакансиях.
- 🇬🇧 [IT Jobs Watch: Data Engineering в Великобритании](https://www.itjobswatch.co.uk/jobs/uk/data%20engineering.do) — Azure, Databricks, Power BI в вакансиях.
- 🇬🇧 [Netflix: Iceberg и Trino (Trino Summit 2024)](https://trino.io/assets/blog/trino-summit-2024/trino-summit-2024-netflix.pdf)
- 🇬🇧 [Airbnb: обновление хранилища на Spark 3 и Iceberg](https://medium.com/airbnb-engineering/upgrading-data-warehouse-infrastructure-at-airbnb-a4e18f09b6d5)
- 🇬🇧 [Uber: Apache Hudi](https://www.uber.com/blog/apache-hudi-at-uber/)
