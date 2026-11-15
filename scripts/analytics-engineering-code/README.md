# Код к конспекту Analytics Engineering with SQL and dbt

Вместо BigQuery из книги везде DuckDB (`dbt-duckdb`). Данные генерирует сам код. Платных API нет.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.
Python-скрипты запускаются с `python3 -I`, детерминизм проверяет `python3 -I scripts/book-tools/same_output.py <скрипт.py>`.

## Глава 1

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | Example 1-1: ETL на хранимой процедуре, наш вариант на DuckDB (temp table, UPDATE, INSERT) | на странице, блок `sql` | ok: `check_sql.py` OK (DuckDB CLI), вывод настоящий |
| 1 | Практика в DuckDB: raw_orders, stg_orders, выручка, проверка уникальности | на странице, блоки `sql` | ok: `check_sql.py` OK |
| 1 | Example 1-2: DAG Airflow из двух задач, обновлён под Airflow 3 | ch01_simple_dag.py | ok: DagBag без ошибок (Airflow 3.1.0, Python 3.12 venv) |
| 1 | Проверка DAG через DagBag | ch01_check_dag.py | ok (same_output x6 из venv с `apache-airflow==3.1.0`), зависимости: `requirements-ch01-airflow.txt` |
| 1 | Example 1-3: dbt-модель total_revenue (`config`, `ref`) на seed orders.csv | ch01_dbt/, ch01_dbt_run.sh | ok: `dbt seed` + `dbt run`, dbt-core 1.12.7, dbt-duckdb 1.11.1; результат 500.0 / 5, зависимости: `requirements-ch01-dbt.txt` |

## Глава 2

Проверка: `python3 scripts/kimball-diagrams/check_sql.py <page>` → OK; `python3 -I scripts/analytics-engineering-code/ch02_check_dbt.py` → OK (same x6).

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 2 | Физическая модель (пример 2-1), DDL под DuckDB | sql-блок на странице | ok (check_sql.py) |
| 2 | Нормализация 1NF-3NF (примеры 2-2…2-5) | таблица в тексте, без кода | ok: заменены таблицей шагов |
| 2 | Star schema + LEFT JOIN/COALESCE (примеры 2-6…2-9) | sql-блок на странице | ok |
| 2 | Snowflake DDL (примеры 2-10, 2-11) | Mermaid-схема ch02-snowflake | ok: без кода |
| 2 | Data Vault hub + satellite (примеры 2-12…2-14), по стандарту DV 2.0 | sql-блок на странице | ok |
| 2 | dbt: ref() orders/customers (пример 2-15) | описан в тексте | ok: без кода, ref() показан в int-модели |
| 2 | dbt: stg_books, int_book_authors, mart_book_authors (примеры 2-16…2-18) | jinja-блоки, ch02_check_dbt.py | ok: рендер ref/source, запуск в DuckDB |
| 2 | dbt: singular test, generic test (примеры 2-19…2-21), современный синтаксис | jinja + yaml, ch02_check_dbt.py | ok: SQL тестов запускается (singular: 1 строка — книга 106 без автора, так задумано в данных; generic: 0). YAML проверен в настоящем проекте dbt-duckdb (dbt 1.12.7) при проверке кода, 2026-11 |
| 2 | NPS-модель с документацией (пример 2-22) | sql-блок на странице | ok |
| 2 | dbt docs generate, dbt run --full-refresh (2-23, текст) | bash-блоки | не запускались: нужен проект dbt с адаптером |
| 2 | Разбиение запроса на CTE (примеры 2-24, 2-25) | sql-блок на странице | ok |
| 2 | Практика в DuckDB: staging, intermediate, mart, проверка grain | sql-блоки | ok |

## Глава 3

Запуск: `python3.13 -m venv .venv && .venv/bin/pip install -r requirements-ch03.txt && .venv/bin/python -I ch03_<name>.py`

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 3 | SQL главы (DDL, DML, JOIN, view, CTE, оконные функции, практика) | блоки `sql` на странице `03-sql-for-analytics.md`, проверка `scripts/kimball-diagrams/check_sql.py` | ok (DuckDB CLI 1.4.3) |
| 3 | DuckDB над pandas DataFrame (примеры 3-52 ... 3-58) | `ch03_duckdb_pandas.py` | ok |
| 3 | SQL над Polars: DuckDB и `pl.SQLContext` (3-61 ... 3-66) | `ch03_polars_sql.py` | ok (в книге `reverse=True`, сейчас `descending=True`) |
| 3 | FastAPI + DuckDB endpoint (3-50) | `ch03_fastapi.py` | ok (TestClient вместо сервера) |
| 3 | FugueSQL на движках pandas и duckdb (3-73) | `ch03_fugue.py` | ok (Spark не запускали; нужен duckdb 1.1.3) |
| 3 | dask-sql: CREATE MODEL, PREDICT, EXPERIMENT (3-74 ... 3-83) | — | не переносили: экспериментальная библиотека, на странице только таблица команд |

## Глава 4

Запуск: `uv venv --python 3.13 scripts/analytics-engineering-code/.venv && uv pip install --python scripts/analytics-engineering-code/.venv/bin/python -r scripts/analytics-engineering-code/requirements-ch04.txt`, затем `bash scripts/analytics-engineering-code/ch04_run.sh`.
Вместо BigQuery из книги используется DuckDB (`dbt-duckdb`). Данные генерирует `ch04_jaffle/raw.sql`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 4 | 4-1, 4-2: публичные таблицы Jaffle Shop | ch04_jaffle/raw.sql | ok (свои данные, та же структура) |
| 4 | 4-3, 4-4, 4-11: структура проекта и YAML | ch04_jaffle/ | ok |
| 4 | 4-5, 4-13, 4-14, 4-19: dbt_project.yml | ch04_jaffle/dbt_project.yml | ok |
| 4 | 4-6: packages.yml | на странице | ok: dbt deps проверен отдельно для Hub и Git, в проект не входит (нужна сеть) |
| 4 | 4-7: profiles.yml | ch04_jaffle/profiles.yml | ok (DuckDB вместо BigQuery) |
| 4 | 4-8 … 4-10, 4-22: staging-модели | ch04_jaffle/models/staging/ | ok |
| 4 | 4-12: config() в файле модели | на странице | ok: проверен во временной модели |
| 4 | 4-15, 4-24: YAML моделей с тестами | ch04_jaffle/models/staging/jaffle_shop/_jaffle_shop_models.yml | ok (data_tests, с return_pending) |
| 4 | 4-16 … 4-18: intermediate и mart | ch04_jaffle/models/intermediate/, marts/core/ | ok |
| 4 | 4-20, 4-21, 4-23, 4-26: sources, freshness, тесты sources | ch04_jaffle/models/staging/*/_*_sources.yml | ok (WARN freshness ожидаем) |
| 4 | 4-25, 4-27: singular tests | ch04_jaffle/tests/ | ok |
| 4 | 4-28, 4-30: analyses | ch04_jaffle/analyses/ | ok |
| 4 | 4-29: seed | ch04_jaffle/seeds/seed_customer_range_per_paid_amount.csv | ok (полуоткрытые интервалы) |
| 4 | 4-31, 4-32: документация, doc block | ch04_jaffle/models/marts/core/_core_models.yml, _core_docs.md | ok (dbt docs generate проходит) |
| 4 | 4-33 … 4-38: selection syntax | — | ok: проверено через dbt ls |
| 4 | Практика в DuckDB | страница | ok: check_sql.py OK (7 blocks) |

## Глава 5

Проект `ch05_dbt/` — маленький jaffle_shop на `dbt-duckdb`. Данные создаёт `ch05_run.py` (`VALUES`), внешних сервисов нет.
Venv: `python3.13 -m venv <venv> && <venv>/bin/pip install -r scripts/analytics-engineering-code/requirements-ch05.txt`.
Запуск: `<venv>/bin/python -I scripts/analytics-engineering-code/ch05_run.py`. Первый запуск делает `dbt deps` (нужна сеть).
Скрипт делает два прогона `dbt build`, печатает таблицы, скомпилированный SQL и ответы MetricFlow. Блоки вывода на странице взяты из него.
SQL-блоки «Практики в DuckDB» проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 5 | Materialization в YAML: ephemeral, incremental, view (5-1) | ch05_dbt/models/staging/_jaffle_shop_models.yml | ok |
| 5 | Ephemeral-модель превращается в CTE (рис. 5-4) | ch05_dbt/models/marts/dim_customers.sql | ok |
| 5 | Incremental-модель с is_incremental() и merge (5-2) | ch05_dbt/models/staging/stg_jaffle_shop_orders.sql | ok |
| 5 | Materialized view / dynamic table (5-3, 5-4) | — | не запускается: DuckDB не поддерживает, только YAML на странице |
| 5 | Snapshot со стратегией timestamp (5-5) | ch05_dbt/snapshots/snap_order_status_transition.sql | ok |
| 5 | Jinja: цикл по типам оплаты (5-7) | ch05_dbt/models/intermediate/int_payment_type_amount_per_order.sql | ok |
| 5 | Macro sum_two_values (5-8 .. 5-10) | ch05_dbt/macros/sum_two_values.sql | ok |
| 5 | Macro get_column_values, get_payment_types (5-11 .. 5-15) | ch05_dbt/macros/get_distinct_by_column.sql | ok |
| 5 | Macro limit_dataset_if_not_deploy_env (5-6, 5-16, 5-17) | ch05_dbt/macros/limit_dataset_if_not_deploy_env.sql, models/marts/fct_orders.sql | ok |
| 5 | dbt_utils: packages.yml, date_spine, safe_divide (5-18 .. 5-21) | ch05_dbt/packages.yml, models/utils/metricflow_time_spine.sql, models/marts/fct_orders_cash_share.sql | ok |
| 5 | Semantic model и метрики, mf query (5-22 .. 5-24) | ch05_dbt/models/marts/_core_models.yml | ok |
| 5 | Практика в DuckDB: merge, SCD2, pivot | страница главы | ok (check_sql.py) |

## Глава 6

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 6 | 6-1...6-3: DDL операционной базы (MySQL) | SQL-блок на странице, диалект DuckDB | ok (check_sql.py) |
| 6 | 6-4...6-8: ETL MySQL → BigQuery (pandas, pandas_gbq) | `ch06_etl.py`: SQLite → SQLite, только стандартная библиотека | ok, same x6 |
| 6 | 6-10, 6-16, 6-21, 6-24, 6-28: YAML dbt | `ch06_dbt/` (sources, packages, `_omnichannel_marts.yml`), запуск `ch06_run.sh` | ok (dbt build на DuckDB: PASS=15). Из `source` убрана строка `database`. Предупреждение dbt 1.12: аргументы generic-теста надо класть в `arguments` |
| 6 | 6-11...6-23: модели dbt (Jinja) | `ch06_dbt/models/` (блоки страницы + остальные staging, dim, fct) | ok (dbt build на DuckDB). `dim_date`: макрос `dbt_date` падает на DuckDB (`to_char`), в файле SQL-аналог; в блок `fct_purchase_history` добавлен опущенный CTE |
| 6 | 6-25...6-27: singular-тесты | `ch06_dbt/tests/assert_mtr_length_of_stay_is_positive.sql` | ok (PASS в dbt build) |
| 6 | 6-29...6-32: аналитические запросы | Практика в DuckDB (шаг 4, задания 1-2) | ok (check_sql.py) |
