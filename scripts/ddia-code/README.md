# Код к конспекту DDIA (2-е издание)

Запуск из корня репозитория. SQL — DuckDB CLI: `duckdb < scripts/ddia-code/<файл>.sql`. Python — только стандартная библиотека: `python3 -I scripts/ddia-code/<файл>.py`.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.
Вывод на странице вставляет `python3 scripts/ddia-code/embed.py <шаблон.md> <страница.md>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | В главе нет кода | — | ok (нечего запускать) |
| 2 | Домашняя лента: запрос при чтении и fan-out при записи (DuckDB) | ch02_timeline.sql | ok: `duckdb < ch02_timeline.sql`, вывод на странице реальный |
| 2 | Среднее, p50–p999 и почему нельзя усреднять перцентили (DuckDB) | ch02_percentiles.sql | ok: `duckdb < ch02_percentiles.sql`, детерминирован (одинаковый вывод дважды) |
| 3 | `join` users и regions (Example: нормализация) | страница, блок sql | ok |
| 3 | Миграция `ALTER TABLE` + `split_part` | страница, блок sql | ok |
| 3 | Акулы по месяцам, `date_trunc` | страница, блок sql | ok |
| 3 | Граф в таблицах + рекурсивный CTE (Example 3-3, 3-6) | страница, блок sql | ok (в DuckDB нужны скобки: `(properties->>'name') = ...`) |
| 3 | Практика: журнал событий, view статусов, свободные места, PIVOT | страница, блоки sql | ok |
| 3 | MongoDB, Cypher, Turtle, SPARQL, Datalog, GraphQL, JS | страница, без запуска | не запускается: нужны MongoDB, Neo4j, triple store; показаны как иллюстрация синтаксиса |
| 3 | Лента X (запрос с `current_user`) | страница, блок text | не запускается: псевдо-SQL из книги |
| 4 | Простейшая база на bash (`db_set`, `db_get`) | `ch04_simple_db.sh` | ok (bash, вывод на странице совпадает) |
| 4 | Example 4-1 (продажи фруктов и конфет по дням недели) | — | не в коде: описан словами, идея показана в «Практика в DuckDB» |
| 4 | Запрос ресторанов по широте и долготе | — | не в коде: описан словами |
| 4 | DuckDB: compaction, bitmap AND, серии после сортировки | на странице, блоки `sql` | ok (`check_sql.py` OK, DuckDB 1.4.3) |
| 5 | Запись из примера 5-2 в JSON, MessagePack, Protocol Buffers, Avro: 81, 66, 33, 32 байта, как в книге | ch05_encodings.py | ok |
| 5 | `varint` и `zigzag`; ID больше 2^53 теряет точность в `double` | ch05_encodings.py | ok |
| 5 | Avro: перевод из схемы писателя в схему читателя; потеря неизвестного поля (рисунок 5-1) | ch05_compatibility.py | ok |
| 5 | Схема Avro в JSON (на странице) | — | ok: разобрана `fastavro`, кодирует запись в те же 32 байта |
| 5 | Схема Protocol Buffers | — | на странице таблицей, не кодом: `protoc` не установлен; размер 33 байта проверен своим кодировщиком |
| 5 | Пример 5-1 JSON Schema, 5-3 OpenAPI, 5-4 FastAPI, 5-5 Temporal | — | пересказаны текстом: нужны `fastapi`, сервер Temporal; не основная мысль главы |
| 6 | Номера версий и siblings на одной реплике (корзина, Figure 6-15) | ch06_cart_versions.py | ok (stdlib, same x6) |
| 7 | Сколько ключей переезжает: `hash mod N` против фиксированного числа `shard` (в книге кода нет, пример наш) | ch07_rebalance.py | ok (python3 -I, только stdlib, same x6) |
| 8 | Атомарный `UPDATE` счётчика (42 → 44) | на странице, блок `sql` | ok (duckdb 1.4.3, check_sql.py OK) |
| 8 | Условная запись по номеру версии (`optimistic locking`), второй `UPDATE` возвращает 0 строк | на странице, блок `sql` | ok (duckdb 1.4.3) |
| 8 | Example 8-1: `SELECT ... FOR UPDATE` в игре | на странице, блок `sql title="PostgreSQL"` | ok (PostgreSQL 14.20; DuckDB не поддерживает `FOR UPDATE`, поэтому check_sql.py его пропускает) |
| 8 | Fig 8-8: `write skew` врачей на `REPEATABLE READ` и `SERIALIZABLE` | ch08_write_skew.sh | ok (PostgreSQL 14.20, две параллельные сессии psql, вывод одинаковый x3) |
| 8 | Example 8-2: бронирование переговорки | — | ok (проверено в PostgreSQL 14.20), на странице пересказано текстом |
| 8 | Практика: правила видимости MVCC и идемпотентный `ledger` | на странице, блоки `sql` | ok (duckdb 1.4.3, check_sql.py OK) |
| 9 | Цикл с lease из раздела «Паузы процессов» и fencing token: пауза 40 с, запись зомби без проверки и с проверкой token | ch09_lease_pause.py | ok (python3 -I, стандартная библиотека, same x6) |
| 10 | — | — | ok: в главе нет кода. Операции `read`, `write`, `CAS` показаны как нотация, а не как программа |
| 11 | Топ-5 страниц по логу: цепочка Unix-команд и Python со словарём, сравнение результатов | ch11_top_urls.py | ok (same x6) |
| 11 | Практика в DuckDB: GROUP BY как MapReduce, sort-merge join событий и пользователей, раздача ключей по reducer | на странице, `check_sql.py` | ok |
| 12 | Timeline как join posts и follows (запрос из книги, PostgreSQL `array_agg` заменён на DuckDB `list`) | на странице, блок `sql` в разделе «Table–table join» | ok (`check_sql.py`) |
| 12 | Практика: tumbling window по event time и processing time, session window, log compaction через `QUALIFY` | на странице, раздел «Практика в DuckDB» | ok (`check_sql.py`, DuckDB 1.4.3) |
| 13 | Примеры 13-1 и 13-2: повтор перевода без request_id и с уникальным request_id | ch13_request_id.sql | ok (duckdb 1.4.3, `duckdb < scripts/ddia-code/ch13_request_id.sql`; в DuckDB нет `ALTER TABLE ADD UNIQUE`, ключ задан в `CREATE TABLE`) |
| 14 | В главе нет кода | — | ok: нечего запускать |

## Заметки

- Глава 3: Весь код главы — SQL в DuckDB прямо на странице. Проверка: `python3 scripts/kimball-diagrams/check_sql.py <page.md>` печатает `OK` (9 блоков).
- Глава 5: Только стандартная библиотека Python, без зависимостей. Проверено `same_output.py`: `same x6`.
- Глава 6: Вывод на странице вставлен через `python3 scripts/ddia-code/embed.py <template> <page>` (маркер `{{out: ch06_cart_versions.py}}`).
