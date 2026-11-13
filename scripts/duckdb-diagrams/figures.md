| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | 1-1 | Обычный путь: загрузить в сервер БД, потом запрос | ch01-traditional-vs-duckdb.png (верхняя полоса) | redrawn |
| 1 | 1-2 | С DuckDB запрос идёт прямо над файлом | ch01-traditional-vs-duckdb.png (нижняя полоса) | redrawn |
| 1 | 1-3 | DuckDB работает над pandas DataFrame | ch01-dataframe-flow.png | redrawn |
| 1 | 1-4 .. 1-15 | Скриншоты результатов в Jupyter (SHOW TABLES, SELECT, агрегаты, JOIN, DataFrame) | настоящий вывод скриптов ch01_quick_look.py, ch01_dataframe.py | skipped: скриншоты таблиц, заменены реальным выводом кода |
| 1 | 1-16 | Скриншот: средняя задержка по авиакомпаниям | вывод ch01_flights_check.py | skipped: скриншот таблицы, заменён реальным выводом |
| 1 | (свои) | Карта главы | ch01-chapter-map.png | own |
| 1 | (свои) | Хронология DuckDB | ch01-timeline.png | own |
| 1 | (свои) | Где стоит DuckDB: SQLite, DuckDB, Spark | ch01-where-duckdb.png | own |
| 1 | (свои) | Строки и столбцы | ch01-row-vs-column.png | own |
| 1 | (свои) | Путь запроса внутри DuckDB | ch01-query-pipeline.png | own |
| 1 | (свои) | Время и память pandas против DuckDB (числа автора) | ch01-speed-memory.png | own |
| 2 | 2-1 .. 2-8 | Скриншоты: число строк, SHOW TABLES, содержимое таблиц, DataFrame airlines, ошибка заголовка | настоящий вывод ch02_csv_load.py | skipped: скриншоты таблиц, заменены реальным выводом |
| 2 | 2-9 .. 2-11 | DataFrame: хранение по строкам и по столбцам (CSV и Parquet) | ch02-csv-vs-parquet.png | redrawn |
| 2 | 2-12 .. 2-14 | Tad показывает Parquet, содержимое таблицы airports | - | skipped: скриншоты |
| 2 | 2-15 .. 2-18 | Excel: два листа, результаты st_read, заголовки | вывод ch02_excel_header.py | skipped: скриншоты, заменены реальным выводом |
| 2 | 2-19, 2-20 | Таблица airlines в MySQL и в DuckDB | ch02-mysql-ways.png (два пути) | skipped: скриншоты; два пути нарисованы свои |
| 2 | (свои) | Источники данных DuckDB | ch02-import-sources.png | own |
| 2 | (свои) | Три способа загрузить CSV | ch02-csv-ways.png | own |
| 2 | (свои) | Размер CSV и Parquet (наш замер 21,7 и 5,0 МБ) | ch02-csv-vs-parquet.png | own |
| 2 | (свои) | MySQL: вручную и через ATTACH | ch02-mysql-ways.png | own |
| 3 | 3-1 | Страница загрузки DuckDB CLI | - | skipped: скриншот сайта |
| 3 | 3-2 | Папка после EXPORT DATABASE и её файлы | ch03-cli-map.png (правая часть) | redrawn |
| 3 | 3-3 | Схема таблиц мини-библиотеки | ch03-shop-er.png (наша схема магазина, Mermaid, `src/ch03-shop-er.mmd`) | redrawn |
| 3 | 3-4 | LEFT JOIN | ch03-joins.png | redrawn |
| 3 | 3-5 | RIGHT JOIN | ch03-joins.png | redrawn |
| 3 | 3-6 | INNER JOIN | ch03-joins.png | redrawn |
| 3 | 3-7 | FULL JOIN | ch03-joins.png | redrawn |
| 3 | 3-8 | Три вложенных SELECT | ch03-nested-query.png | redrawn |
| 3 | own | Консоль: память и файл, .open, ATTACH, EXPORT/IMPORT | ch03-cli-map.png | own |
| 4 | 4-1 .. 4-8 | Скриншоты Polars DataFrame и результатов select, filter, SQL | настоящий вывод ch04_polars_basics.py | skipped: скриншоты таблиц |
| 4 | 4-9, 4-12 | Загрузка большого CSV в pandas, результат collect() | вывод ch04_snippet_lazy.py | skipped: скриншоты |
| 4 | 4-10, 4-11 | Оптимизированный и неоптимизированный план запроса | ch04-lazy-plan.png | redrawn |
| 4 | 4-13 .. 4-18 | Скриншоты результатов duckdb.sql, describe, order, GROUP BY | вывод ch04_duckdb_polars.py, ch04_df_by_name.py | skipped: скриншоты таблиц |
| 4 | 4-19 .. 4-24 | Скриншоты join, filter, aggregate, project, limit | вывод ch04_relation.py | skipped: скриншоты таблиц |
| 4 | (свои) | Polars и DuckDB вместе (главная схема) | ch04-polars-duckdb.png | own |
| 4 | (свои) | eager, implicit lazy, explicit lazy | ch04-lazy-modes.png | own |
| 4 | (свои) | Методы DuckDBPyRelation и аналоги в SQL | ch04-relation-sql.png | own |
| 5 | 5-1 | Три таблицы в базе (SHOW TABLES) | - | skipped: скриншот таблицы |
| 5 | 5-2, 5-3 | Карта США в folium, выбор плиток | - | skipped: скриншоты интерактивной карты, описаны текстом |
| 5 | 5-4 .. 5-6 | Аэропорты на карте: CircleMarker, Marker со значком | - | skipped: скриншоты карты |
| 5 | 5-7 | DataFrame со столбцом geometry | - | skipped: скриншот таблицы |
| 5 | 5-8, 5-9 | explore() по GeoDataFrame, клик по маркеру | - | skipped: скриншоты карты |
| 5 | 5-10 .. 5-15 | Ближайшие аэропорты к Майами | ch05-nearest-airports.png + вывод ch05_spatial.py | redrawn |
| 5 | 5-16 .. 5-20 | Аэропорты по штатам и городам (таблицы) | - | skipped: скриншоты таблиц |
| 5 | 5-21 .. 5-24 | Pie и bar chart аэропортов по штатам | - | skipped: графики, описаны текстом |
| 5 | 5-25 .. 5-30 | Рейсы по маршрутам, отмены Delta | - | skipped: скриншоты таблиц, числа автора в тексте |
| 5 | 5-31 .. 5-34 | Отмены по авиакомпаниям (таблица, bar, pie) | вывод ch05_flights_eda.py, блок 2 | skipped: скриншоты, заменены реальным выводом |
| 5 | 5-35 .. 5-39 | Рейсы по дням недели, проверка кодов | вывод ch05_flights_eda.py, блок 4 | skipped: скриншоты, заменены реальным выводом |
| 5 | 5-40 .. 5-42 | Задержки по слотам времени | вывод ch05_flights_eda.py, блок 3 | skipped: скриншоты, заменены реальным выводом |
| 5 | 5-43 .. 5-47 | Задержки и вовремя прилетевшие по авиакомпаниям | ch05-count-vs-share.png + вывод ch05_flights_eda.py, блок 1 | redrawn (на наших данных) |
| 5 | (свои) | Схема главы | ch05-eda-flow.png | own |
| 5 | (свои) | Слоты времени | ch05-timeslots.png | own, не использована на странице |
| 6 | 6-1, 6-2, 6-3 | read_json_auto: таблица, records=false, выбор полей | ch06-three-ways.png (общий выбор способа) | redrawn (идея), скриншоты таблиц skipped: таблицы пересказаны текстом и выводом |
| 6 | 6-4, 6-5 | read_json с format и columns, NDJSON | ch06-formats.png | redrawn |
| 6 | 6-6, 6-7, 6-8 | вложенный объект: struct и выбор ключей | ch06-nested-flow.png | redrawn |
| 6 | 6-9, 6-10, 6-11 | массив в ключе: unnest | ch06-nested-flow.png | redrawn |
| 6 | 6-12 | результат загрузки двух файлов | вывод кода на странице | skipped: показан реальным выводом |
| 6 | 6-13, 6-14 | COPY FROM, таблица people | ch06-three-ways.png | skipped: скриншоты таблиц |
| 7 | 7-1, 7-2 | Путь через DataFrame и путь через JupySQL и DuckDB | ch07-jupysql-flow.png | redrawn |
| 7 | 7-3, 7-4 | %load_ext sql, справка %sql? | - | skipped: скриншоты ячеек |
| 7 | 7-5 .. 7-11 | Результаты запросов, %sqlcmd tables/columns/profile, snippets | ch07-magics.png (карта команд) | redrawn: карта команд вместо скриншотов таблиц |
| 7 | 7-12 .. 7-26 | Histogram, box plot, pie, bar, настройка цветов, Titanic по возрасту | ch07-plots.png | redrawn: выбор графика по вопросу, сами графики не копируем |
| 7 | 7-27 .. 7-33 | getpass, DATABASE_URL, .ini, keyring, список подключений | ch07-connect-ways.png | redrawn: три способа хранить доступ |
| 8 | 8-1 .. 8-9 | GitHub Raw, DataFrame с CSV и Parquet, схема, столбцы, avg, count | реальный вывод ch08_remote_real.py | skipped: скриншоты таблиц |
| 8 | 8-10 .. 8-13, 8-15 .. 8-23 | Страницы Hugging Face, DataFrame с результатами | реальный вывод ch08_remote_real.py | skipped: скриншоты |
| 8 | 8-14 | Как собрать путь hf:// | ch08-hf-path.png | redrawn |
| 8 | 8-24 .. 8-33 | Аккаунт, новый датасет, загрузка файла, токен на сайте Hugging Face | - | skipped: скриншоты интерфейса |
| 8 | 8-34 | Закрытый датасет в DataFrame | - | skipped: скриншот |
| 8 | (свои) | httpfs и три вида удалённых источников | ch08-remote-sources.png | own |
| 8 | (свои) | Сколько байт скачивается: CSV и Parquet (наш замер) | ch08-remote-bytes.png | own |
| 8 | (свои) | CONFIG и CREDENTIAL_CHAIN | ch08-auth.png | own |
| 9 | 9-1, 9-2, 9-3 | Главная страница, вход, веб-интерфейс | ch09-architecture.png (по смыслу: ваша машина и облако) | redrawn: общая схема вместо скриншотов |
| 9 | 9-4 | Два тарифа | - | skipped: скриншот, цены в таблице текста |
| 9 | 9-5, 9-6 | Базы my_db и sample_data, права | ch09-hierarchy.png | redrawn |
| 9 | 9-7 .. 9-14, 9-25 | Add Data, ячейки, схема Titanic | ch09-hierarchy.png | skipped: скриншоты UI, идея в схеме иерархии |
| 9 | 9-15 .. 9-24 | Создание, список, изменение и удаление share | ch09-share.png | redrawn |
| 9 | 9-26, 9-27 | Detach и список Detached databases | - | skipped: скриншоты, описаны текстом |
| 9 | 9-28 .. 9-35 | Запрос и статистика колонок | - | skipped: скриншоты, описаны текстом |
| 9 | 9-36 .. 9-39 | prompt_sql, prompt_query, prompt_explain | - | skipped: скриншоты, вывод описан текстом |
| 9 | 9-40 .. 9-42 | Подтверждение входа из CLI | - | skipped: скриншоты, шаги описаны текстом |
| 9 | 9-43, 9-44 | Таблицы в вебе после CLI | - | skipped: скриншоты |
| 9 | (свой) | Hybrid-запрос | ch09-hybrid.png | redrawn: своя схема |
