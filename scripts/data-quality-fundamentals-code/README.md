# Код к конспекту Data Quality Fundamentals

Только стандартная библиотека Python 3.10+ и DuckDB CLI (для SQL). Платных API нет, внешние сервисы не нужны.
Запуск из корня репозитория: `python3 -I scripts/data-quality-fundamentals-code/<файл>.py`.
Страницы глав собираются из шаблонов в `templates/` командой `python3 scripts/data-quality-fundamentals-code/embed.py <шаблон.md> <страница.md>`. Для глав 2, 3, 4 и 8 перед этим работают вспомогательные скрипты (`*_sqlout.py`, `ch04_build_page.py`, `ch08_sqlrun.py`): они запускают SQL-блоки и подставляют настоящий вывод.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.
Счётчики слов: `wc_book.py` (глава книги) и `wc_page.py` (проза страницы).

## Глава 1

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | SQL: проверки свежести, дублей, пропавших дней, пустых значений; uptime и «пять девяток» (DuckDB) | блоки ```sql в `src/content/docs/book-summaries/engineering/data-quality-fundamentals/01-why-data-quality-matters.md` | ok (`check_sql.py` печатает OK) |

## Глава 2

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 2 | Журнал запросов: lineage, читатели, последнее чтение, лишний доступ | `ch02_query_log.py` | ok (6 запусков с разным `PYTHONHASHSEED`, вывод одинаковый) |
| 2 | Метрики по часам и data downtime в DuckDB (на странице, 8 sql-блоков) | `templates/ch02.tpl.md` + `ch02_sqlout.py` | ok (`check_sql.py` печатает OK, вывод одинаковый при 6 сборках) |
| 2 | Скрипт сборки: подставляет вывод DuckDB в шаблон (`{{sqlout}}`), дальше `embed.py` | `ch02_sqlout.py` | ok |

Сборка страницы: `python3 scripts/data-quality-fundamentals-code/ch02_sqlout.py templates/ch02.tpl.md <tmp.md>`, затем `python3 scripts/data-quality-fundamentals-code/embed.py <tmp.md> <page.md>`.
Примеры из книги на Snowflake SQL (Example 2-1 ... 2-7) и ANTLR на Java (Example 2-8, 2-9) не запускаются без Snowflake и Java. Вместо них: DuckDB-версия метрик и учебный разбор журнала на Python.

## Глава 3

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 3 | Type coercion (`int` и `round`), `Decimal`, время в UTC | `ch03_coercion.py` | ok (6 запусков с `python3 -I`, вывод одинаковый) |
| 3 | Circuit breaker: проверки свежести, объёма, схемы и null | `ch03_circuit_breaker.py` | ok (6 запусков с `python3 -I`, вывод одинаковый) |
| 3 | DuckDB: тесты not_null, unique, accepted_values, relationships, singular; volume, invariants, TRY_CAST | страница главы (блоки `sql`) | ok (`check_sql.py` печатает OK) |
| 3 | Вывод DuckDB на страницу (маркер `{{sqlout}}`) | `ch03_sqlout.py` | ok (сборка: `embed.py`, затем `ch03_sqlout.py`) |
| 3 | Airflow: SLA и `sla_miss_callback`, `SQLCheckOperator` | - | пропущено: нужен Airflow, на странице описано словами |
| 3 | dbt singular и generic тесты, Great Expectations, Deequ (Scala) | - | пропущено: нужны сторонние инструменты; singular-тест повторён на DuckDB |

## Глава 4

Только стандартная библиотека Python и DuckDB CLI. Запуск Python: `python3 -I scripts/data-quality-fundamentals-code/<файл>`.
Страницу собирает `python3 scripts/data-quality-fundamentals-code/ch04_build_page.py` из `templates/ch04.tpl.md`:
скрипт запускает sql-блоки шаблона в одной базе DuckDB, подставляет их вывод, потом `embed.py` подставляет вывод Python.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 4 | precision, recall, F1, F2, F0,5 по порогу детектора свежести; ловушка accuracy | `ch04_fscore.py` | ok (6 запусков, вывод одинаковый) |
| 4 | z-score против детектора с учётом дня недели (seasonality) | `ch04_zscore_seasonality.py` | ok (6 запусков, вывод одинаковый) |
| 4 | Практика DuckDB: данные, свежесть, F-score в SQL, скользящее среднее, schema и lineage | `ch04_practice.sql` (создаётся сборщиком из страницы) | ok (`check_sql.py` печатает OK) |
| 4 | Сборка страницы: вывод sql-блоков и Python в шаблон | `ch04_build_page.py` | ok |

## Глава 5

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 5 | Цена простоя данных, годовая цена плохих данных, допустимый простой по SLO, проверка цифр Blinkist | `ch05_downtime_cost.py` | ok |
| 5 | DuckDB: тесты при загрузке, TTD и TTR с ценой простоя, SLI и SLO по свежести (SQL на странице, проверка `check_sql.py`) | `templates/ch05.tpl.md` | ok |

## Глава 6

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 6 | RCA, шаг 3: сегменты и доля null | `ch06_rca_segments.py` | ok |
| 6 | SLI инцидентов: N, TTD, TTR | `ch06_incident_metrics.py` | ok |
| 6 | Группировка алертов, подавление шума | `ch06_alert_grouping.py` | ok |

## Глава 7

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 7 | Lineage на уровне полей из SQL моделей (парсер DuckDB `json_serialize_sql`, связи select / non-select, запись с хэшем) | `ch07_lineage.py` | ok (6 запусков с `python3 -I`, вывод одинаковый; нужен DuckDB CLI) |
| 7 | Impact analysis, root cause, PII, data debt по графу связей | `ch07_impact.py` | ok (6 запусков с `python3 -I`, вывод одинаковый) |
| 7 | Рекурсивные запросы DuckDB по таблице связей (3 задания) | `templates/ch07.tpl.md`, раздел «Практика в DuckDB» | ok (`check_sql.py` печатает OK; таблица связей равна выводу `ch07_lineage.py`) |

## Глава 8

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 8 | SQL: SLI, часы data downtime и правило сертификации (DuckDB). SQL-блоки лежат в шаблоне страницы, вывод получают запуском блоков | `templates/ch08.tpl.md`, `ch08_sqlrun.py`, `ch08_out_check.py`, `ch08_out_sli.py`, `ch08_out_downtime.py`, `ch08_out_gate.py`, `ch08_out_t1.py`, `ch08_out_t2.py`, `ch08_out_t3.py` | ok (6 запусков с `python3 -I`, вывод одинаков; `check_sql.py` печатает OK) |

## Глава 9

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 9 | Data mesh score: сумма пяти ответов и вывод по порогам 15 и 30 | `ch09_mesh_score.py` | ok (6 запусков `python3 -I`, вывод одинаковый) |
| 9 | Сигналы «пора заниматься качеством»: 50+ таблиц, 30% тушения, рост потребителей (DuckDB, SQL на странице) | `src/content/docs/book-summaries/engineering/data-quality-fundamentals/09-real-world-case-studies.md` | ok (`check_sql.py` OK) |

## Глава 10

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 10 | Часы простоя и цена работы инженеров по формулам главы, три уровня зрелости | `ch10_labor_cost.py` | ok (6 запусков с `python3 -I`, вывод одинаковый) |
