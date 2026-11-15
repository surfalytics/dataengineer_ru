# Рисунки книги Analytics Engineering with SQL and dbt и наши схемы

Статус: `redrawn` — перерисован по-нашему; `own` — своя схема; `skipped: причина` — не рисовали.
Исходные картинки в репозитории не хранятся (авторские права). Excalidraw-схемы собирает `chNN_diagrams.py` через `excb.py`, Mermaid — `chNN_mermaid.sh` из `src/*.mmd`.

## Обзор

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 0 | — (своя) | Карта книги: 6 глав в четырёх блоках | ch00-book-map.png | own |

## Глава 1

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | — (своя) | Три роли вдоль потока данных и аналогия со стройкой | ch01-roles-bridge.png | redrawn (own, main) |
| 1 | — (своя) | BI на OLTP-реплике против BI на хранилище через pipeline | ch01-bi-oltp.png | redrawn (own) |
| 1 | Figure 1-1 | Жизненный цикл аналитики, 6 этапов по кругу | ch01-analytics-lifecycle.png | redrawn |
| 1 | — (своя) | ETL против ELT, место dbt и Airflow | ch01-etl-vs-elt.png | redrawn (own) |

## Глава 2

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 2 | — | Путь от понимания бизнеса к физической модели | ch02-modeling-phases.png (Excalidraw) | own, главная схема |
| 2 | 2-1 | Концептуальная ERD книг (нотация Чена) | ch02-books-logical.png | skipped: объединена с 2-2, сущности и связи те же, описаны в тексте |
| 2 | 2-2 | Логическая ERD: category, books, authors, publishes | ch02-books-logical.png (Mermaid) | redrawn |
| 2 | 2-3 | Star schema: factBookPublish и три измерения | ch02-star-schema.png (Mermaid) | redrawn |
| 2 | 2-4 | Snowflake schema: иерархия местоположения | ch02-snowflake.png (Mermaid) | redrawn |
| 2 | 2-5 | Модульность dbt: переиспользование моделей по слоям | ch02-dbt-layers.png (Excalidraw) | redrawn, с именами моделей из примеров |
| 2 | 2-6 | Medallion architecture в lakehouse и роль dbt | ch02-medallion.png (Excalidraw) | redrawn |

## Глава 3

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 3 | 3-1 | Пирамида DIKW | ch03-dikw.png | redrawn (наши стрелки и примеры) |
| 3 | 3-2 | Категории баз и их типы | — | skipped: список типов, в тексте есть |
| 3 | 3-3 | Пример таблицы со строками и столбцами | — | skipped: скриншот, текст объясняет |
| 3 | 3-4 | Связь таблиц студентов и курсов | — | skipped: связь «многие ко многим» показана кодом DDL; ER-схемы в главе 2 |
| 3 | 3-5 | Языки SQL и их команды | ch03-sql-languages.png | redrawn (главная схема) |
| 3 | 3-6, 3-8, 3-10, 3-12, 3-13 | Диаграммы Венна для JOIN | ch03-joins.png | redrawn: одна сетка «какие строки попадут в результат» |
| 3 | 3-7, 3-9, 3-11 | Результаты JOIN-запросов | — | skipped: скриншоты, на странице реальный вывод DuckDB |
| 3 | 3-14, 3-15, 3-16 | Результаты UPDATE, DELETE, ROW_NUMBER | — | skipped: скриншоты, на странице реальный вывод DuckDB |
| 3 | own | GROUP BY против оконной функции | ch03-groupby-vs-window.png | own |

## Глава 4

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 4 | 4-1 | Место dbt в потоке данных | ch04-dbt-data-flow.png | redrawn |
| 4 | 4-2 | Пример pipeline: объединить таблицы в dbt | ch04-dbt-data-flow.png, ch04-lineage.png | redrawn (объединён) |
| 4 | 4-3 … 4-15 | Настройка dbt Cloud, BigQuery, GitHub | — | skipped: скриншоты интерфейса, шаги описаны списком |
| 4 | 4-16 … 4-28 | Меню и страницы dbt Cloud UI | — | skipped: скриншоты, описаны списком |
| 4 | 4-29, 4-30 | Зоны dbt Cloud IDE, командная строка | — | skipped: скриншоты, пять зон описаны списком |
| 4 | 4-31 | ER-диаграмма Jaffle Shop | ch04-jaffle-erd.png (Mermaid, src/ch04-jaffle-erd.mmd) | redrawn |
| 4 | 4-32 … 4-36 | Логи dbt run, модели в BigQuery | — | skipped: скриншоты |
| 4 | 4-37, 4-39, 4-53 | Lineage fct_orders (без и с sources, в документации) | ch04-lineage.png | redrawn (объединены) |
| 4 | 4-38 | Скомпилированный код с source() | — | skipped: скриншот; на странице реальный вывод dbt compile текстом |
| 4 | 4-40 … 4-45 | Логи freshness и тестов, результаты analyses | — | skipped: скриншоты; на странице реальный вывод текстом |
| 4 | 4-46 … 4-52 | Сайт документации | — | skipped: скриншоты, описаны списком |
| 4 | 4-54 … 4-62 | Commit, PR, среда развёртывания, job, Run History | ch04-deploy-job.png | redrawn (свой вариант по шагам раздела) |
| 4 | — | Каскад настроек (cascading scope priority) | ch04-config-cascade.png | own: в книге рисунка нет |

## Глава 5

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 5 | 5-1 | Lineage dim_customers: source → stg → dim | ch05-materializations.png | redrawn: верхний ряд главной схемы |
| 5 | 5-2 | stg_jaffle_shop_customers как table в BigQuery | ch05-materializations.png | skipped: скриншот BigQuery, идея в главной схеме |
| 5 | 5-3 | stg_jaffle_shop_customers как view в BigQuery | ch05-materializations.png | skipped: скриншот BigQuery, идея в главной схеме |
| 5 | 5-4 | Скомпилированный код с view и с ephemeral | — | skipped: вместо картинки настоящий скомпилированный SQL на странице |
| 5 | 5-5 | Данные stg_jaffle_shop_orders | — | skipped: скриншот данных, на странице наш вывод |
| 5 | 5-6 | Таблица snapshot в BigQuery | — | skipped: скриншот, на странице настоящий вывод snapshot из DuckDB |
| 5 | 5-7 | Лог успешного dbt deps | — | skipped: скриншот лога |
| 5 | — | Как работает incremental merge | ch05-incremental-merge.png | own |
| 5 | — | Цепочка macro: get_column_values → get_payment_types → модель | ch05-macros-reuse.png | own |
| 5 | — | Semantic layer: fct_orders → semantic model → metrics → MetricFlow → SQL | ch05-semantic-layer.png | own |

## Глава 6

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 6 | 6-1 | Концептуальная модель: Customer, Channel, Products, связи Buy и Visit | ch06-operational-erd.png | redrawn: объединён с 6-2 и 6-3 в одну ER-схему (Mermaid), связи Buy/Visit описаны в тексте |
| 6 | 6-2 | Логическая схема: 5 таблиц | ch06-operational-erd.png | redrawn: объединён с 6-3 |
| 6 | 6-3 | Физическая схема в MySQL: типы и ключи | ch06-operational-erd.png | redrawn (Mermaid `erDiagram`) |
| 6 | 6-4 | Архитектура: MySQL → Python → BigQuery → dbt → SQL | ch06-architecture.png | redrawn (Excalidraw), главная схема главы; добавлены слои staging/marts и production-датасет |
| 6 | 6-5 | Star schema: 4 измерения, 2 таблицы фактов | ch06-star-schema.png | redrawn (Mermaid `erDiagram`) |
| 6 | 6-6 | Логи generic-тестов | — | skipped: скриншот лога |
| 6 | 6-7 | Логи singular-тестов | — | skipped: скриншот лога |
| 6 | 6-8 | Страница документации fct_purchase_history | — | skipped: скриншот интерфейса |
| 6 | 6-9 | Создание production environment в dbt Cloud | — | skipped: скриншот интерфейса, шаги описаны в тексте |
| 6 | 6-10 | Лог запуска job | — | skipped: скриншот лога |
| 6 | 6-11 | Модели в BigQuery | — | skipped: скриншот интерфейса |
| 6 | 6-12..6-15 | Результаты аналитических запросов | — | skipped: скриншоты результатов; выводы книги в таблице, наш вывод из DuckDB в практике |
