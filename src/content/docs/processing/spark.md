---
title: Apache Spark
description: "Apache Spark для инженеров данных и аналитиков: курсы, видео и практические задания."
sidebar:
  order: 6
tags:
  - spark
  - big-data
---
Apache Spark является самый популярным инструментом среди инженеров данных, аналитиков и инженеров машинного обучения. Его главная задача - это обработка данных. С помощью Spark можно подключаться к любому источнику данных, читать большие данные и обрабатывать их в оперативной памяти с использованием распределенных вычислений (distributed computing).

В зависимости от вашей роли вам необходимо обладать навыками от написания запросов в `PySpark` и `SparkSQL` (реже `Scala`) до развертывания решений Big Data на Apache Spark.

Мы собрали несколько видео и лабораторных работ, которые вам помогут понять, что такое Apache Spark и как им пользоваться. Давайте посмотрим на примеры использования для ролей:

- Дата Инженер:
    - Создание Data Lake или Lake House. Если делаем Lakehouse, то формат таблицы будет по умолчанию `Delta`, но сейчас уже чаще используется `Iceberg`. 
    - Трансформация и обработка данных для ETL/ELT процессов.
    - Потоковая обработка с Apache Spark Streaming
    - Помощь ML-команде в создании ML-решений, например, создание `Feature Store` для предрасчета параметров ML-модели.
- Аналитик и BI-разработчик:
    - Типичные запросы к Data Lake/Lakehouse с использование `SparkSQL`, `PySpark`.
    - Добавиление и модификация ETL jobs (data pipelines)
    - Чтение `source code`, то есть понимание трансформаций данных.

> 🇷🇺 / 🇬🇧 - язык материалов       
> ⭐ - наша рекомендация

Посмотрите видео [Что такое Apache Spark](https://youtu.be/Tl9YzC-dQLI) 🇷🇺 ⭐.

В этом видео вы узнаете:

- Узнаем история Apache Spark
- Посмотрим примеры архитектур с использованием Spark
- Разберемся когда его можно использовать
- Узнаем про основные компоненты
- Узнаем, обозначает термин Unified Analytics

Прежде чем начать работать с Apache Spark, мы должны владеть необходимым минимумом в хотя бы одном из поддерживаемых языков программирования. Один из самых популярных языков - Python.  

> Вы можете ознакомится с ресурсами по самостоятельному обучению [Python на нашем портале](https://dataengineer.ru/coding/2024-11-15-coding.html#python).

Поэтому в этом уроке мы посмотрим, какие команды нам необходимо знать на примере Databricks notebooks. У вас будет замечательная возможно попрактиковаться, и если вдруг вы мало используете Python, то самое время попробовать его, так как дальше он нам очень понадобится.

[Минимум Python для работы со Spark (JUST ENOUGH PYTHON FOR SPARK)](https://youtu.be/ylaby_czbSI) 🇷🇺 ⭐.

В этом видео вы узнаете:

- Что такое Databricks
- Как запустить Community Edition Databricks и какие есть еще варианты для бесплатного Spark
- Переменные и типы данных в Python
- Условия и циклы
- Методы, функции и библиотеки
- Коллекции и классы

Для лабораторной работы вам нужно:

- Создать Databricks Community Edition. Если какие-то проблемы с Databricks, можно все делать на локальном спарке. В следующем уроке покажу, как можно его установить.
- Импортировать Notebooks с примерами для `Just Enougth Python for Spark` - [Репозиторий с кодом](https://github.com/Data-Learn/data-engineering/tree/master/DE-101%20Modules/Module07/DE%20-%20101%20Lab%207.1)
- Выполнить задачки в папке `Labs`

Также вы можете использовать Google Collab или локальный Spark. Для решения Notebooks может подойти Jupyter Notebooks.

Теперь мы можем начать работать с Apache Spark на локальной машине. Посмотрите видео - [Начало работы с Apache Spark](https://youtu.be/FiaZnMMOV-A) 🇷🇺 ⭐. 

В этом видео вы узнаете:

- Скачаем и запустим Apache Spark
- Посмотрим как запустить Spark на Windows
- Посмотрим на Spark UI
- Узнаем про основные компоненты Spark
- Начнем использовать `PySpark`
- Начнем использовать `spark-submit`

Вы можете посмотреть видео про [запуск программы в Apache Spark](https://youtu.be/FiaZnMMOV-A?t=1944) 🇷🇺 ⭐. 

В качестве лабораторной работы вы можете выполнить следующее задание:

1. Ваша задача установить Apache Spark на ваш компьютер и запустить `PySpark`. Этого может хватить вам для изучения Спарка, практически до конца модуля. Так как команды везде очень похожи, а вот интерфейс и конфигурация разные. 
2. Вам нужно взять программу про M&Ms из нашего [репозитория](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/DE%20-%20101%20Lab%207.2/mnmcount.py) и также взять файл с данными в том же репозитории в папке `data`.
3. Запустить Спарк-программу используя `spark-submit` и передать в качестве аргумента месторасположение файла с данными.
4. Вам необходимо взять тот же код про M&Ms, но теперь нужно будет его выполнить в интерактивном режиме. Я это сделал на примере Databricks, если есть доступ к нему, сделайте там, если нет, используйте командную строку или попробуйте вот этот рецепт [Get Started with PySpark and Jupyter Notebook in 3 Minutes](https://medium.com/sicara/get-started-pyspark-jupyter-guide-tutorial-ae2fe84f594f#:~:text=There%20are%20two%20ways%20to%20get%20PySpark%20available,Jupyter%20Notebook%20and%20load%20PySpark%20using%20findSpark%20package)

Мы продолжим [Знакомство с Spark API](https://youtu.be/gg1uip_i2KY) и потренируемся в написании `PySpark`.

В этом видео вы узнаете:

- что такое RDD (Resilient Distributed Datasets)
- что такое DataFrame
- посмотрим на пример синтаксиса Scala vs Python
- типы данных Spark
- схему(schema) dataframe
- колонки (colums) и вычисляемы (expressions) поля dataframe
- основные операции при работе с dataframe (Reader, Wrtiter)
- примеры чтения разных источников и файлов (API, база данных, JSON, Parquet, CSV, TXT)
- различные операции для трансформации, фильтрации и агрегации данных в Spark DataFrame (прям как в SQL)
- Spark SQL, Catalyst Optimizer
- план запроса Spark
- примеры advance Spark функций и ноутбуков в Databticks

В качестве практики попробуйте повторить [Запросы PySpark](https://youtu.be/gg1uip_i2KY?t=2297) использую Spark CLI. Заодно, мы можем познакомиться ближе с Databriks и их курсом - [Обзор курса Databrick - Programming with Apache Spark](https://youtu.be/gg1uip_i2KY?t=3567).

В качестве лабораторной работы, вам нужно будет ответить на вопросы про пожарную службу Сан-Франциско, используя файлик с данными [sf-fire-calls.csv](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/DE%20-%20101%20Lab%207.4/examples/sf-fire-calls.csv)

Вопросы находятся в файлике [sf_fire.py](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/DE%20-%20101%20Lab%207.4/examples/sf_fire.py)

Теперь мы можем изучить [Spark SQL и DataFrame](https://youtu.be/MHt_s0-q_PM).

В этом видео вы узнаете:

- Методы SparkSession для работы с SQL 
- Как создавать таблицы и вьюхи
- Виды таблиц - Managed vs Unmanaged
- Примеры SQL запросов в PySpark
- Кеш в Spark
- Результат SQL-запроса в DataFrame и наоборот
- Пример работы с различными файлами в Spark - Parquet, CSV, JSON, AVRO, ORC
- Пример использования Spark для бинарных файлов и изображений
- Функции и операции Spark
- UNION, JOIN для DataFrame
- Window Functions
- UDF
- Партиционирование данных и оптимизация с командами coalesce, repartition.

В качестве лабораторной работы вам нужно будет выполнить все [запросы](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/DE%20-%20101%20Lab%207.5/examples/) из примеров в CLI и Databricks.

**Книги:**

- [Книга Learnin Spark V2 PDF](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/LearningSpark2.0.pdf) 🇬🇧 ⭐

**Курсы:**

- [Introduction to Big Data with PySpark](https://www.codecademy.com/learn/big-data-pyspark) - курс для ознакомления с библиотекой pyspark. 🇬🇧
- [PySpark on Google Colab 101](https://towardsdatascience.com/pyspark-on-google-colab-101-d31830b238be) 🇬🇧
- [Databricks: Working with SQL at Scale - Spark SQL Tutorial](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/3137082781873852/3704545280501166/1264763342038607/latest.html)
- [Spark SQL Explained with Examples](https://sparkbyexamples.com/spark/spark-sql-explained/)

**Статьи:**

- [Что такое Apache Spark?](https://learn.microsoft.com/ru-ru/dotnet/spark/what-is-spark) 🇷🇺
- [Apache Spark Installation on Windows](https://sparkbyexamples.com/spark/apache-spark-installation-on-windows/) 🇬🇧
- [Install PySpark in Jupyter on Mac using Homebrew](https://sparkbyexamples.com/pyspark/install-pyspark-in-jupyter-on-mac-using-homebrew/) 🇬🇧
- [Get Started with PySpark and Jupyter Notebook in 3 Minutes](https://sparkbyexamples.com/spark/install-apache-spark-on-mac/)
- [Beginners Guide to PySpark](https://towardsdatascience.com/ beginners-guide-to-pyspark-bbe3b553b79f#:~:text=Beginners%20Guide%20to%20PySpark%201%20Setting%20Environment%20in,Values%20...%208%20Querying%20Data%20...%20More%20items) 🇬🇧
- [Welcome to Spark… on Java: Интервью с Евгением Борисовым](https://habr.com/ru/company/jugru/blog/311146/) 🇷🇺
- [Знакомство с Apache Spark](https://habr.com/ru/company/piter/blog/276675/) 🇷🇺
- [Spark local mode: обработка больших файлов на обычном ноутбуке](https://habr.com/ru/post/274705/) 🇷🇺
- [Apache Spark Key Terms, Explained](https://databricks.com/blog/2016/06/22/apache-spark-key-terms-explained.html) 🇬🇧
- [Apache Spark: оптимизация производительности на реальных примерах](https://habr.com/ru/companies/neoflex/articles/578654/) 🇷🇺
- [Практика использования Spark SQL, или Как не наступить на грабли](https://habr.com/ru/companies/sberbank/articles/496310/) 🇷🇺
- [Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/3.2.0/sql-programming-guide.html) 🇬🇧
- [Databricks: Functions](https://docs.databricks.com/sql/language-manual/sql-ref-functions.html) 🇬🇧
- [Databricks: WindowFunctions](https://docs.databricks.com/sql/language-manual/sql-ref-window-functions.html) 🇬🇧


**Вебинары:**

- [ВВЕДЕНИЕ В PYSPARK И SPARKSQL / ОЛЕГ АГАПОВ](https://youtu.be/OfS5o8vz-O8) 🇷🇺 ⭐

