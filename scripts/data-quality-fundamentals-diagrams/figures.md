# Рисунки книги Data Quality Fundamentals и наши схемы

Статус: `redrawn` — перерисован по-нашему; `skipped: причина` — не рисовали.
Исходные картинки в нашем репозитории не хранятся (авторские права). Схемы собирает `chNN_diagrams.py` через `excb.py`.

## Обзор

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| — | Карта книги: 10 глав в четырёх блоках | `ch00-book-map.png` | наша схема (`ch00_diagrams.py`) |

## Глава 1

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | Figure 1-1 | Data mesh: общая инфраструктура, домены с E-T-L, универсальный уровень совместимости | `ch01-data-mesh.png` | redrawn |
| 1 | (наша схема) | Причины роста data downtime: облако, источники, пайплайны, команды, тренды | `ch01-why-downtime-grows.png` | own |
| 1 | (наша схема) | Где ломаются данные по этапам пайплайна | `ch01-pipeline-breaks.png` | own |
| 1 | (наша схема) | DevOps -> DataOps, uptime -> data downtime | `ch01-devops-dataops.png` | own |

## Глава 2

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 2 | Figure 2-1 | Пример платформы данных: операционные источники, data lake, слой интеграции, data warehouse, ELT | `ch02-data-platform.png` | redrawn |
| 2 | Figure 2-2 | Скриншот Snowflake с таблицей метрик качества | - | skipped: скриншот интерфейса, идею даёт текст и наша схема четырёх шагов |
| 2 | Table 2-1 | Пример простого каталога данных (таблица, дашборд, дата, владелец, заметки) | - | skipped: таблица книги не копируем, суть пересказана в тексте |
| 2 | own | Сравнение data warehouse, data lake и lakehouse | `ch02-warehouse-vs-lake.png` | own diagram |
| 2 | own | Четыре шага получения метрик из Snowflake | `ch02-four-steps.png` | own diagram |
| 2 | own | Каталог данных и data discovery | `ch02-catalog-vs-discovery.png` | own diagram |

## Глава 3

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 3 | (нет, наша схема) | Пять шагов пути данных и проверки на каждом шаге | `ch03-pipeline-stages.png` | own (главная схема главы) |
| 3 | (нет, наша схема) | Три источника данных: логи, API, датчики | `ch03-sources.png` | own |
| 3 | Figure 3-1 | AWS Kinesis: producers, поток с shards, consumers | - | skipped: схема продукта AWS, идея (источники, поток, потребители) описана в тексте |
| 3 | Figure 3-2 | Data Doc из Great Expectations с упавшим тестом | - | skipped: скриншот интерфейса |
| 3 | (нет, наша схема) | Поток теста данных: staging, тесты, production или алерт | `ch03-test-gate.png` | own |
| 3 | Figure 3-3 | Circuit breaker между задачами DAG, состояния closed и open | `ch03-circuit-breaker.png` | redrawn (вместе с Figure 3-4) |
| 3 | Figure 3-4 | Circuit breaker в Airflow UI: задачи circuit_breaker между ETL-задачами | `ch03-circuit-breaker.png` | redrawn (общая схема; сам скриншот UI пропущен) |

## Глава 4

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 4 | 4-1 | Сетка known/unknown knowns и unknowns (слова-примеры) | `ch04-monitoring-map.png` | redrawn: своя версия, идея «тесты закрывают known unknowns, мониторинг закрывает unknown unknowns» плюс пять столпов |
| 4 | 4-2 | Строки в день по данным EXOPLANETS (график из ноутбука) | - | skipped: график сгенерированных данных, заменён таблицей вывода в практике DuckDB |
| 4 | 4-3 | Пробелы свежести как высокие значения Y | - | skipped: график, идея в тексте и в выводе SQL |
| 4 | 4-4 | Свежесть с порогом 1 день | `ch04-threshold-fscore.png` | redrawn: колонка T = 1 |
| 4 | 4-5 | Порог 3 дня, два малых пропуска не видны | `ch04-threshold-fscore.png` | redrawn: колонка T = 3 |
| 4 | 4-6 | Порог 7 дней, остаются два самых больших | `ch04-threshold-fscore.png` | redrawn: колонка T = 7 |
| 4 | 4-7 | Нормальное распределение (колокол) | - | skipped: стандартная иллюстрация, объяснена в тексте |
| 4 | 4-8 | Доля null по четырём полям по дням | - | skipped: график, заменён описанием и SQL |
| 4 | 4-9 | Всплески доли null в avg_temp (порог 0,9) | - | skipped: график, идея в тексте и в практике |
| 4 | 4-10 | Доли null выше 90% после фильтра повторов | - | skipped: график, идея в тексте |
| 4 | 4-11 | Разность «доля null минус скользящее среднее» | - | skipped: график, запрос и вывод есть в практике (задание 2) |
| 4 | 4-12 | Граф зависимостей: источник, снимки схемы, потребитель | `ch04-lineage-root-cause.png` | redrawn: с нашими таблицами и историей инцидента |
| 4 | 4-13 | Среднее habitability падает вдвое | - | skipped: график, числа по месяцам в практике (шаг 4) |
| 4 | 4-14 | Доля нулей в habitability растёт | - | skipped: график, идея в тексте и в задании 3 |
| 4 | 4-15 | Строки в день за месяц (повтор 4-2) | - | skipped: повтор |
| 4 | 4-16 | Пробелы свежести (повтор 4-3) | - | skipped: повтор |
| 4 | 4-17 | Дни устаревших данных (повтор) | - | skipped: повтор |
| 4 | 4-18 | Реестр моделей MLflow в процессе data science | - | skipped: скриншот инструмента, суть в одном пункте списка |
| 4 | 4-19 | Окно TensorBoard при обучении | - | skipped: скриншот инструмента |
| 4 | 4-20 | Precision и recall (картинка с обнаруженными и всеми аномалиями) | `ch04-precision-recall.png` | redrawn: матрица ошибок, формулы, F-beta и два крайних детектора |
| 4 | 4-21 | Precision, recall и F1 по порогу | `ch04-threshold-fscore.png` | redrawn: наши числа для порогов 1, 3, 4, 7 |
| 4 | 4-22 | F-score при разных beta | `ch04-threshold-fscore.png` | redrawn частично: числа F2 и F0,5 по порогам выводит `ch04_fscore.py` |

## Глава 5

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 5 | Figure 5-1 | Data pipeline = данные «в production»: источники, data lake, warehouse, BI | `ch05-platform-layers.png` (верхний ряд: источники, ingestion, storage, transformation, BI) | redrawn |
| 5 | Figure 5-2 | Пять столпов data observability | в основном тексте как таблица; также в `ch05-reliability-map.png` | redrawn (таблица и блок на главной схеме) |
| 5 | Figure 5-3 | Дашборд надёжности данных (скриншот Datadog и Grafana) | нет | skipped: скриншот интерфейса, идея описана в тексте (TTD, TTR, SLO) |
| 5 | Figure 5-4 | Шесть связанных слоёв платформы данных | `ch05-platform-layers.png` | redrawn (с акцентом на сквозные слои) |
| 5 | own | Карта главы: три места защиты и три направления работы | `ch05-reliability-map.png` | own |
| 5 | own | Цена простоя: TTD, TTR и две формулы | `ch05-downtime-cost.png` | own |
| 5 | own | SLI, SLO, SLA и три шага внедрения | `ch05-sla-slo-sli.png` | own |

## Глава 6

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 6 | Figure 6-1 | Цикл DevOps из восьми этапов | нет | skipped: восемь этапов перечислены в тексте, схема ничего не добавляет |
| 6 | Figure 6-2 | Цикл надёжности данных: Detect, Resolve, Prevent | `ch06-incident-lifecycle.png` | redrawn: вместе с пятью шагами работы с инцидентом, главная схема главы |
| 6 | Figure 6-3 | Обнаружение инцидента: алерты по свежести, объёму, распределению | нет | skipped: скриншот интерфейса продукта |
| 6 | Figure 6-4 | Anomaly detection в цикле надёжности | нет | skipped: повтор Figure 6-2 с подсветкой этапа |
| 6 | Figure 6-5 | Сквозной lineage при поломке пайплайна | нет | skipped: скриншот; lineage разбирается в главе 7 |
| 6 | Figure 6-6 | Алерт об изменении схемы | нет | skipped: скриншот продукта |
| 6 | Figure 6-7 | Lineage для RCA | `ch06-rca-five-steps.png` | redrawn: шаг 1 учтён в схеме пяти шагов, сам скриншот пропущен |
| 6 | Figure 6-8 | Как создан запрос (шаг 2 RCA) | `ch06-rca-five-steps.png` | redrawn: шаг 2 в схеме пяти шагов, скриншот пропущен |
| 6 | Figure 6-9 | Просмотр запроса после lineage | нет | skipped: скриншот |
| 6 | Figure 6-10 | Доля аномалий null по сегментам (шаг 3 RCA) | нет | skipped: скриншот; идею воспроизводит код `ch06_rca_segments.py` |
| 6 | Figure 6-11 | Среда запуска ETL/ELT (шаг 4 RCA) | `ch06-rca-five-steps.png` | redrawn: шаг 4 в схеме пяти шагов, скриншот пропущен |
| 6 | Figure 6-12 | Логи задач в Airflow | нет | skipped: скриншот |
| 6 | Figure 6-13 | Тесты ловят около 20% неизвестных неизвестных, остальные 80% находят коллеги | нет | skipped: два числа переданы в тексте |
| 6 | Figure 6-14 | Слои надёжности: testing, CI/CD, discovery, observability по этапам пайплайна | `ch06-reliability-stack.png` | redrawn |
| 6 | Figure 6-15 | Децентрализованная data-команда | `ch06-team-structures.png` | redrawn: вместе с Figure 6-16 |
| 6 | Figure 6-16 | Централизованная data-команда | `ch06-team-structures.png` | redrawn |
| 6 | Figure 6-17 | Визуализация использования данных в бизнесе | нет | skipped: скриншот продукта |

## Глава 7

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 7 | Figure 7-1 | Table-level lineage: связи между таблицами хранилища (скриншот интерфейса) | `ch07-lineage-map.png` (своя схема пути от источника до дашборда) | redrawn (идея, не скриншот) |
| 7 | Figure 7-2 | Lineage полей: сотни связей между полями (скриншот-«паутина») | - | skipped: скриншот, идея (связей очень много, UI должен их прятать) есть в тексте |
| 7 | Figure 7-3 | Структура lineage: таблица-приёмник, её поля, таблицы-источники | `ch07-field-level.png`, `ch07-lineage-design.png` | redrawn |
| 7 | Figure 7-4 | Модель: источники, select-поля и non-select поля, колонка приёмника | `ch07-field-level.png` | redrawn |
| 7 | Figure 7-5 | UI: таблица-источник и отчёты-приёмники на уровне колонок (скриншот) | - | skipped: скриншот интерфейса, идея (два крайних слоя) описана в тексте |
| 7 | Figure 7-6 | Платформа данных Fox: десятки технологий | `ch07-fox-platform.png` (упрощённая: слои, observability, пользователи) | redrawn |
| 7 | own | Lineage вверх (root cause) и вниз (impact) | `ch07-lineage-map.png` | own |
| 7 | own | Как строят lineage: SQL, парсер, связи, хранилище, запросы, UI | `ch07-lineage-design.png` | own |

## Глава 8

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 8 | (наша схема) | Карта главы: четыре опоры доверия к данным | ch08-democratizing-map.png | own diagram |
| 8 | Figure 8-1 | Модель зрелости надёжности данных: reactive, proactive, automated, scalable | ch08-maturity-curve.png | redrawn |
| 8 | Figure 8-2 | Типичные пользователи платформы данных (четыре персоны, фото) | - | skipped: портреты персон, идея передана одним предложением в тексте |
| 8 | Figure 8-3 | Рост функциональности во времени: низкое и высокое внутреннее качество | - | skipped: график без данных, результат пересказан в тексте |
| 8 | Figure 8-4 | Blast radius: ущерб растёт от data engineering до публики | ch08-blast-radius.png | redrawn |
| 8 | Figure 8-5 | Data discovery даёт картину данных по доменам в реальном времени | - | skipped: схема доменов, идея описана в тексте и уже нарисована в главе 2 |
| 8 | Figure 8-6 | Дашборд инцидентов (аномалии, изменения схемы, нарушения правил) | - | skipped: скриншот |
| 8 | Figure 8-7 | Теги в каталоге: Certified Gold, owner | - | skipped: скриншот |
| 8 | (наша схема) | Семь шагов data certification | ch08-certification-steps.png | own diagram |
| 8 | Figure 8-8 | Три структуры дата-команды: плюсы и минусы | - | skipped: это таблица, пересобрана как таблица в тексте |
| 8 | Figure 8-9 | Uber Databook | - | skipped: скриншот |
| 8 | Figure 8-10 | Amundsen | - | skipped: скриншот |

## Глава 9

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 9 | 9-1 | Data mesh: источники, инфраструктура как продукт, домены с E-T-L, слой совместимости | `ch01-data-mesh.png` (нарисована в главе 1, на странице главы 9 использована повторно) | redrawn (глава 1) |
| 9 | 9-2 | Первый стек Kolibri: Facebook Analytics, Firebase, GameAnalytics, ad partners | `ch09-kolibri-timeline.png` (колонка 2016) | redrawn (в общей схеме) |
| 9 | 9-3 | Первая «команда данных» Kolibri: один маркетинг-менеджер | `ch09-kolibri-timeline.png` (колонка 2017) | skipped: картинка команды, идея в тексте и на таймлайне |
| 9 | 9-4 | Стек Kolibri в 2017: добавлен AppsFlyer | `ch09-kolibri-timeline.png` (колонка 2017) | redrawn (в общей схеме) |
| 9 | 9-5 | Команда данных в 2018 | `ch09-kolibri-timeline.png` (колонка 2018) | skipped: картинка команды |
| 9 | 9-6 | Облачный стек в 2018: Azure, SQL database, Power BI, Looker | `ch09-kolibri-timeline.png` (колонка 2018) | redrawn (в общей схеме) |
| 9 | 9-7 | Команда данных в 2019 | `ch09-kolibri-timeline.png` (колонка 2019) | skipped: картинка команды |
| 9 | 9-8 | Архитектура 2019: Databricks, Snowflake, Looker | `ch09-kolibri-timeline.png` (колонка 2019) | redrawn (в общей схеме) |
| 9 | 9-9 | Команда данных в 2020: 9 человек | `ch09-kolibri-timeline.png` (колонка 2020) | skipped: картинка команды |
| 9 | 9-10 | Архитектура 2020: Snowflake ELT, dbt, Airflow | `ch09-kolibri-timeline.png` (колонка 2020) | redrawn (в общей схеме) |
| 9 | 9-11 | Команда 2021: доменные команды в продукте и маркетинге | `ch09-kolibri-timeline.png` (колонка 2021) | skipped: картинка команды |
| 9 | 9-12 | Стек 2021: Event hubs, Databricks, Snowflake, dbt, Airflow, Looker, observability | `ch09-kolibri-timeline.png` (колонка 2021) | redrawn (в общей схеме, без деталей потоков) |
| 9 | 9-13 | Lineage без контекста это «красивая картинка» | нет | skipped: скриншот инструмента, идея в тексте |
| 9 | 9-14 | Метаданные как усилитель для компании | нет | skipped: скриншот lineage-графа, идея в тексте |
| 9 | own | Четыре элемента data mesh и что mesh не является | `ch09-mesh-four-elements.png` | own |
| 9 | own | Каталог и data discovery: сравнение | `ch09-catalog-vs-discovery.png` | own |
| 9 | own | Семь сигналов начинать data quality | `ch09-start-signals.png` | own |

## Глава 10

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 10 | (в главе нет рисунков) | Главный план: четыре прогноза, плюс и минус каждого | `ch10-four-predictions.png` | own: нарисован нами |
| 10 | (в главе нет рисунков) | Формулы часов простоя и цены работы инженеров | `ch10-labor-cost.png` | own: нарисован нами |
| 10 | (в главе нет рисунков) | Четыре новые роли и их задачи | `ch10-new-roles.png` | own: нарисован нами |
| 10 | (в главе нет рисунков) | Пять областей автоматизации: боль и решение | `ch10-automation.png` | own: нарисован нами |
