# Код к конспекту DuckDB: Up and Running

Запуск из корня репозитория: `python3 -I scripts/duckdb-code/<файл>.py`. Зависимости: `requirements.txt` (в venv).
Страницы собираются командой `python3 scripts/duckdb-code/embed.py <шаблон.md> <страница.md>`.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | База, таблица, агрегаты, JOIN, файл и память | ch01_quick_look.py | ok (вывод одинаков при 6 запусках `python3 -I`) |
| 1 | DuckDB читает pandas DataFrame по имени | ch01_dataframe.py | ok (6 запусков) |
| 1 | pandas и DuckDB дают одинаковый ответ на CSV | ch01_flights_check.py | ok (6 запусков) |
| 1 | Время и память pandas против DuckDB, 5,8 млн строк | ch01_speed_memory.py | ok, но вывод меняется от запуска к запуску (замер времени и памяти) |
| 1 | План запроса: projection и filter pushdown | ch01_explain.py | ok (6 запусков) |
| 1 | SQL-блоки страницы | 01-getting-started.md | ok (`check_sql.py` печатает OK, 18 блоков) |
| 2 | CSV: типы, all_varchar, COPY со схемой, ошибка типа, register, экспорт | ch02_csv_load.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 2 | Parquet и CSV: размер файлов, схема внутри Parquet (1 млн строк) | ch02_parquet_size.py | ok (6 запусков). Размеры файлов могут чуть отличаться в других версиях DuckDB |
| 2 | Excel: `OGR_XLSX_HEADERS` AUTO и FORCE через `spatial` | ch02_excel_header.py | ok (6 запусков). Нужна сеть для `INSTALL spatial` |
| 2 | MySQL: цикл `INSERT` и `ATTACH` | - | не запускали: нужен сервер MySQL |
| 2 | SQL-блоки страницы | 02-importing-data.md | ok (`check_sql.py` печатает OK, 5 блоков) |
| 3 | EXPORT DATABASE / IMPORT DATABASE в консоли duckdb | ch03_export.py | ok (6 запусков `python3 -I`, нужен `duckdb` CLI в PATH; проверено на 1.4.3) |
| 3 | LEFT и INNER JOIN на схеме магазина | ch03_joins.py | ok (6 запусков, duckdb 1.4.3) |
| 3 | SQL-блоки практики на странице | check_sql.py | ok (5 блоков) |
| 4 | Polars: select, filter, SQLContext | ch04_polars_basics.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 4 | Lazy: scan_csv, read_csv, read_csv().lazy(), планы | ch04_lazy.py | ok (8 запусков). CSV строится в коде. Порядок условий в плане Polars не фиксирован, поэтому скрипт его не печатает |
| 4 | DuckDB читает Polars DataFrame, describe, order, aggregate | ch04_duckdb_polars.py | ok (6 запусков) |
| 4 | DuckDBPyRelation: table, insert, join, filter, aggregate, project, limit | ch04_relation.py | ok (6 запусков) |
| 4 | Короткий пример страницы: DuckDB по имени переменной | ch04_df_by_name.py | ok (6 запусков) |
| 4 | Короткий пример страницы: LazyFrame и план | ch04_snippet_lazy.py | ok (8 запусков) |
| 4 | Решения заданий | ch04_practice.py | ok (6 запусков) |
| 4 | SQL-блок практики | 04-polars.md | ok (`check_sql.py`) |
| 5 | spatial: ST_Point, ST_DWithin, ST_Distance, 3 ближайших к Майами | ch05_spatial.py | ok (6 запусков `python3 -I`, вывод одинаков; нужен INSTALL spatial, то есть сеть при первом запуске) |
| 5 | EDA: число против доли, отмены, слоты времени, проверка кодов (6000 придуманных рейсов) | ch05_flights_eda.py | ok (6 запусков, вывод одинаков) |
| 5 | SQL-блоки практики | 05-eda-spatial.md | ok (`check_sql.py` печатает OK, 6 блоков) |
| 5 | folium, leafmap, GeoDataFrame, matplotlib из книги | - | не запускали: карты и графики нужен Jupyter, на странице только описаны |
| 6 | Полный разбор: read_json_auto, records, read_json, struct, unnest, список и маска файлов, COPY | ch06_json.py | ok (6 запусков `python3 -I`, разные PYTHONHASHSEED, вывод одинаков; временная папка нормализована) |
| 6 | Страница: struct и unnest | ch06_snippet_nested.py | ok (6 запусков) |
| 6 | Страница: два файла с разным типом поля, COPY TO | ch06_snippet_files.py | ok (6 запусков) |
| 6 | SQL-блоки практики | 06-json.md | ok (`check_sql.py`) |
| 7 | %sql, %%sql --save --no-execute, %sqlcmd tables, %sqlplot bar через IPython (200 придуманных строк в CSV) | ch07_jupysql.py | ok (6 запусков `python3 -I` в venv, вывод одинаков; jupysql 0.11.1, duckdb 1.4.3, pandas 2.3.3; браузер Jupyter не нужен) |
| 7 | SQL-блоки практики | 07-jupysql.md | ok (`check_sql.py` печатает OK, 6 блоков) |
| 7 | MySQL: DATABASE_URL, connections.ini, keyring | - | не запускали: нужен сервер MySQL, на странице только описаны |
| 8 | Сколько байт скачивается по HTTP: CSV и Parquet, локальный сервер с Range | ch08_range_demo.py | ok (6 запусков `python3 -I`, вывод одинаков). Нужна сеть только для `INSTALL httpfs` |
| 8 | Примеры книги на GitHub и Hugging Face (CSV, Parquet, hf://, glob, CREATE SECRET с фальшивым токеном) | ch08_remote_real.py | ok (6 запусков, вывод одинаков). Нужен интернет. Данные чужие: вывод изменится, если их поменяют |
| 8 | Закрытый датасет: `CONFIG` с настоящим токеном и `CREDENTIAL_CHAIN` | - | не запускали: нужен личный токен Hugging Face |
| 8 | SQL-блоки практики страницы | 08-remote-data.md | ok (`check_sql.py` печатает OK, 4 блока) |
| 9 | Имитация MotherDuck: вторая база в памяти, hybrid-запрос, запрос в стиле prompt_sql на придуманных данных | ch09_cloud_sim.py | ok (6 запусков `python3 -I` с разным PYTHONHASHSEED, вывод одинаков; duckdb 1.4.3) |
| 9 | SQL-блоки практики | 09-motherduck.md | ok (`check_sql.py` печатает OK, 4 блока) |
| 9 | ATTACH 'md:', share, prompt_sql, prompt_query, CLI, hybrid с flights.csv | - | не запускали: нужен аккаунт и токен MotherDuck |
