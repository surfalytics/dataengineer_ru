---
title: "Learning Spark — конспект книги"
head:
  - tag: title
    content: "Learning Spark: конспект книги об Apache Spark | Инжиниринг Данных"
description: "Конспект книги Learning Spark на русском: DataFrame, Spark SQL, оптимизация, Structured Streaming, Delta Lake, MLlib и MLflow. Разбор 12 глав со схемами."
author: "Jules S. Damji и др."
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - spark
  - data-engineering
---

**Learning Spark, 2nd Edition. Lightning-Fast Data Analytics** — книга Jules S. Damji, Brooke Wenig, Tathagata Das и Denny Lee (O'Reilly, 2020). На момент выхода книги все авторы работали в Databricks, а Tathagata Das был одним из создателей Structured Streaming. Книга учит работать с Apache Spark 3.0 на Python и Scala: от первого `DataFrame` до потоков, `data lake` и машинного обучения. В книге 12 глав.

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.

📥 [Скачать конспект в EPUB](/downloads/learning-spark.epub) — для телефона и электронной книги.

![Карта книги: 12 глав в четырёх блоках — основы, Spark SQL и данные, скорость и потоки, ML и Spark 3.0](/assets/learning-spark/ch00-book-map.png)

Карту читайте сверху вниз и слева направо: каждый блок опирается на предыдущий.

## О чём книга простыми словами

Данных стало больше, чем помещается на одну машину. Hadoop MapReduce решил эту задачу первым, но он писал каждый промежуточный шаг на диск и требовал много кода. Spark держит промежуточные данные в памяти и даёт один движок для SQL, потоков и машинного обучения. Поэтому авторы называют его единым движком аналитики (`unified analytics engine`).

Главная мысль книги — структура. Когда вы пишете запрос через `DataFrame` или SQL, Spark видит, что именно нужно посчитать, и сам строит быстрый план через оптимизатор `Catalyst`. Код с `lambda` и низкоуровневый `RDD` скрывают этот замысел, поэтому оптимизировать их движок не может. Эта идея проходит через все главы: от простых запросов до потоков и ML.

Книга нужна тем, кто обрабатывает большие данные на Spark: инженерам данных, аналитикам и ML-инженерам. Она объясняет не только API, но и то, что происходит внутри: как код превращается в `job`, `stage` и `task`, где возникает `shuffle` и почему запрос тормозит.

## Что нужно знать заранее

- SQL на уровне `SELECT`, `JOIN`, `GROUP BY` и оконных функций. Повторить можно в нашем курсе [SQL](/practice/sql/).
- Python на базовом уровне: функции, списки, словари. Примеры книги есть и на Scala, но мы везде даём PySpark.
- Командную строку и Docker: весь наш код запускается в контейнере. Основы есть в курсе [Базовый минимум Docker](/practice/docker/).
- Для глав 10 и 11 полезно понимать, что такое обучение модели, `train` и `test`.

## Зачем читать

- **Понять устройство Spark.** `Driver`, `executor`, `partition`, `lazy evaluation` и `shuffle` объяснены на простых примерах.
- **Писать быстрый код.** Книга показывает, почему `DataFrame` и SQL быстрее `RDD` и `lambda` и как читать план запроса.
- **Настраивать работу в production.** Память `executor`, число `partition`, кэш, виды `join` и Spark UI.
- **Обрабатывать потоки.** Structured Streaming: окна, `watermark`, `state` и `exactly-once`.
- **Строить lakehouse.** Delta Lake добавляет к файлам озера транзакции, `MERGE` и `time travel`.
- **Обучать модели на больших данных.** MLlib, `Pipeline`, `cross-validation` и MLflow.

## Как устроена книга

Формально книга не делится на части, но главы легко сложить в четыре блока.

| Блок | Главы | О чём |
|---|---|---|
| Основы | 1–3 | История и устройство Spark, установка, `job` и `stage`, `DataFrame`, `Catalyst` |
| Spark SQL и данные | 4–6 | SQL, таблицы и форматы файлов, `UDF`, `JDBC`, BI-инструменты, `Dataset` |
| Скорость, потоки, озеро | 7–9 | Настройка и оптимизация, Structured Streaming, Delta Lake и lakehouse |
| ML и Spark 3.0 | 10–12 | MLlib, MLflow и развёртывание моделей, новое в Spark 3.0 |

Первые три главы дают модель, на которую опирается всё остальное: план запроса, `partition` и `shuffle`. Главы 4–6 показывают, как через этот план читать и писать данные. Затем главы 7–9 учат делать это быстро и надёжно, а последние три переносят тот же подход на машинное обучение и новые возможности движка.

## Главные идеи

| Идея | Где |
|---|---|
| Spark — один движок для SQL, потоков и ML, промежуточные данные он держит в памяти | [Глава 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/) |
| Код только дописывает план, а работа начинается при `action` | [Глава 2](/book-summaries/engineering/learning-spark/02-getting-started/) |
| Структура (`DataFrame`, SQL) даёт `Catalyst` понять запрос и ускорить его | [Глава 3](/book-summaries/engineering/learning-spark/03-structured-apis/) |
| SQL и `DataFrame` API — два способа записать один запрос | [Глава 4](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/) |
| `pandas UDF` работает пачками через Arrow и быстрее обычной Python `UDF` | [Глава 5](/book-summaries/engineering/learning-spark/05-sql-dataframes-external-sources/) |
| `lambda` в `Dataset` скрывает логику от оптимизатора и стоит лишних переводов данных | [Глава 6](/book-summaries/engineering/learning-spark/06-sql-and-datasets/) |
| Скорость зависит от `partition`, кэша и выбора `join`, а причины видны в Spark UI | [Глава 7](/book-summaries/engineering/learning-spark/07-optimizing-and-tuning/) |
| Поток — это таблица, в которую всё время добавляют строки | [Глава 8](/book-summaries/engineering/learning-spark/08-structured-streaming/) |
| `Lakehouse` — это файлы озера плюс `transaction log` | [Глава 9](/book-summaries/engineering/learning-spark/09-reliable-data-lakes/) |
| Модель собирают из `transformer` и `estimator` в один `Pipeline` | [Глава 10](/book-summaries/engineering/learning-spark/10-mllib/) |
| Способ запуска модели выбирают по требованиям к задержке | [Глава 11](/book-summaries/engineering/learning-spark/11-ml-pipelines/) |
| `AQE` и `DPP` ускоряют запросы без правок кода | [Глава 12](/book-summaries/engineering/learning-spark/12-spark-3/) |

## Как читать

| Роль | Путь |
|---|---|
| Новичок | Главы 1–4 подряд, потом 7. Остальное по мере нужды |
| Analytics engineer | Главы 1–5, 7 и 9 |
| Data engineer | Вся книга. Особенно 3, 7, 8 и 9 |
| ML-инженер | Главы 1–3, 5, затем 10–12 |
| Руководитель | Главы 1, 9 и 11: что даёт Spark, lakehouse и путь модели в production |

## Как работать с практикой

Книга написана под Spark 3.0, а мы проверили весь код на Spark 4.3.0 в Docker (примеры Delta Lake — на 4.2.0). Как поставить Spark, описано в главе 1, в разделе [Как установить Spark](/book-summaries/engineering/learning-spark/01-intro-to-spark/#как-установить-spark).

- В каждой главе есть короткие примеры на PySpark с настоящим выводом. Имена и данные в них свои, это не код из книги.
- Полные скрипты лежат в папке `scripts/learning-spark-code/` [репозитория сайта](https://github.com/surfalytics/dataengineer_ru). Там же `Dockerfile` и скрипт `spark-python`, который запускает их в контейнере.
- Примеры с Kafka, внешними базами, Scala и GPU на страницах только показаны: для них нужны внешние сервисы.
- В конце каждой главы есть раздел «Практика в DuckDB»: задания на SQL, которые можно решить без Spark.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Введение в Apache Spark](/book-summaries/engineering/learning-spark/01-intro-to-spark/) | Откуда взялся Spark, из чего он состоит и как распределяет работу |
| [2. Установка Spark и первые шаги](/book-summaries/engineering/learning-spark/02-getting-started/) | Как запустить Spark и как код превращается в `job`, `stage` и `task` |
| [3. Structured API в Spark](/book-summaries/engineering/learning-spark/03-structured-apis/) | Чем `DataFrame` лучше `RDD` и как `Catalyst` строит план |
| [4. Spark SQL и DataFrame: встроенные источники данных](/book-summaries/engineering/learning-spark/04-sql-dataframes-builtin-sources/) | Как работать с таблицами, `view` и форматами Parquet, JSON, CSV, Avro, ORC |
| [5. Spark SQL и DataFrame: внешние источники данных](/book-summaries/engineering/learning-spark/05-sql-dataframes-external-sources/) | Как подключить `UDF`, `JDBC` и BI-инструменты и где взять `join`, окна и `pivot` |
| [6. Spark SQL и Dataset](/book-summaries/engineering/learning-spark/06-sql-and-datasets/) | Что даёт типизированный `Dataset` и сколько стоит его удобство |
| [7. Оптимизация и настройка приложений Spark](/book-summaries/engineering/learning-spark/07-optimizing-and-tuning/) | Как ускорить Spark: настройки, память, кэш, `join` и Spark UI |
| [8. Structured Streaming](/book-summaries/engineering/learning-spark/08-structured-streaming/) | Как обрабатывать поток через `DataFrame`: окна, `watermark`, `state` |
| [9. Надёжный data lake на Spark](/book-summaries/engineering/learning-spark/09-reliable-data-lakes/) | Чем `lakehouse` лучше базы и озера и как с ним работает Delta Lake |
| [10. Машинное обучение с MLlib](/book-summaries/engineering/learning-spark/10-mllib/) | Как собрать `Pipeline`, обучить регрессию и деревья, подобрать гиперпараметры |
| [11. MLflow, развёртывание и масштабирование моделей](/book-summaries/engineering/learning-spark/11-ml-pipelines/) | Как отследить модель в MLflow и выбрать `batch`, `streaming` или `real-time` |
| [12. Эпилог: Apache Spark 3.0](/book-summaries/engineering/learning-spark/12-spark-3/) | Что нового в Spark 3.0: `DPP`, `AQE`, подсказки для `join`, `pandas UDF` |
