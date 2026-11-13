| English | Как пишем | Пояснение |
|---|---|---|
| in-process database | `in-process` база | База внутри программы, без сервера |
| RDBMS | `RDBMS` (реляционная СУБД) | Таблицы и SQL |
| OLAP | `OLAP` | Аналитические запросы: большие чтения и агрегаты |
| OLTP | `OLTP` | Много коротких операций над строками |
| columnar storage | `columnar storage` (хранение по столбцам) | Данные лежат по столбцам |
| vectorized execution | `vectorized execution` (векторное выполнение) | Обработка порциями строк |
| parallel execution | `parallel execution` | Запрос делится между ядрами |
| late materialization | `late materialization` (отложенная материализация) | Полные строки собираются в конце |
| query planner | `query planner` (планировщик запросов) | Перестраивает запрос перед выполнением |
| predicate pushdown | `predicate pushdown` | Фильтр ближе к источнику |
| join reordering | `join reordering` | Выбор порядка соединения таблиц |
| ELT | `ELT` | Extract, Load, Transform |
| DataFrame | `DataFrame` | Таблица в памяти программы |
| MotherDuck | MotherDuck | Облачный сервис на DuckDB (название продукта) |
| DuckDB Labs | DuckDB Labs | Компания, которая развивает DuckDB |
| read_csv_auto | `read_csv_auto` | Чтение CSV с автоопределением схемы |
| COPY | `COPY` | Быстрая загрузка и выгрузка файлов |
| Parquet | `Parquet` | Колоночный формат со схемой внутри файла |
| register | `register()` | Показать DataFrame как виртуальную таблицу в SQL |
| ATTACH | `ATTACH` | Подключить внешнюю базу |
| extension | расширение (`extension`) | Модуль, который добавляет возможности DuckDB |
| lazy loading | `lazy loading` | Данные поднимаются в память по мере запросов |
| data lake | `data lake` | Хранилище файлов в облаке |
| CLI | `CLI` (консоль `duckdb`) | Программа командной строки |
| dot command | dot-команда | Команда консоли, начинается с точки, не SQL |
| ATTACH / USE | `ATTACH` / `USE` | Подключить базу / сделать активной |
| EXPORT / IMPORT DATABASE | `EXPORT DATABASE` / `IMPORT DATABASE` | Выгрузить базу в папку / загрузить из папки |
| foreign key | `FOREIGN KEY` | Ссылка на ключ другой таблицы |
| CRUD | `CRUD` | Создать, прочитать, обновить, удалить |
| view | `view` | Сохранённый запрос |
| subquery | `subquery` (вложенный запрос) | Запрос внутри запроса |
| inner / left / right / full / cross join | `INNER`, `LEFT`, `RIGHT`, `FULL`, `CROSS JOIN` | Виды соединения таблиц |
| Polars | `Polars` | Библиотека DataFrame на Rust |
| lazy evaluation | `lazy evaluation` (ленивое вычисление) | План строится сразу, выполняется при `collect()` |
| eager execution | eager-режим | Операция выполняется сразу |
| LazyFrame | `LazyFrame` | Объект с планом запроса |
| expression | `expression` (выражение) | `pl.col(...)`, из выражений строят запрос |
| Apache Arrow | `Apache Arrow` | Колоночный формат данных в памяти |
| DuckDBPyRelation | `DuckDBPyRelation` | Объект запроса DuckDB в Python |
| SQLContext | `SQLContext` | Класс Polars для SQL по DataFrame |
| EDA | `EDA` | Первый разведочный анализ данных |
| geospatial analysis | геоанализ (`GIS`-анализ) | Анализ пространственных данных |
| spatial extension | расширение `spatial` | Геофункции DuckDB |
| Point | `Point` | Тип «точка» |
| WKT | `WKT` | Текстовый формат геометрии |
| EPSG:4326 / WGS 84 | `EPSG:4326` | Система координат: широта и долгота |
| GeoDataFrame | `GeoDataFrame` | Таблица GeoPandas с геометрией |
| descriptive analytics | описательная аналитика | Сводка прошлых данных |
| tile | плитки (`tiles`) | Фрагменты, из которых собрана карта |
| nested object | `nested object` | Объект внутри объекта JSON |
| struct | `struct` | Тип DuckDB для объекта с именованными полями |
| NDJSON / newline-delimited | NDJSON | Один JSON-объект на строку файла |
| unnest | `unnest` | Разворачивает массив в строки |
| glob | `glob` | Маска имён файлов: `*`, `**`, `?` |
| JupySQL | JupySQL | Расширение Jupyter для SQL-ячеек |
| magic command | магическая команда (`%sql`, `%%sql`) | Команда ноутбука с `%` или `%%` |
| snippet | `snippet` | Сохранённый именованный запрос, живёт в ноутбуке |
| SQLAlchemy | `SQLAlchemy` | Библиотека Python для работы с реляционными БД |
| bins | корзины (`bins`) | Диапазоны значений на гистограмме |
| outlier | выброс (`outlier`) | Значение, далёкое от остальных |
| keyring | `keyring` | Доступ к хранилищу паролей ОС |
| httpfs | `httpfs` | Расширение для чтения и записи файлов по HTTP(S) и S3 |
| range request | range request | HTTP-запрос части файла |
| Hugging Face | Hugging Face | Площадка с моделями и датасетами для машинного обучения |
| secret | секрет (`CREATE SECRET`) | Сохранённый доступ: токен или ключ |
| CONFIG | `CONFIG` | Токен задан прямо в команде |
| CREDENTIAL_CHAIN | `CREDENTIAL_CHAIN` | DuckDB сам ищет токен в известных местах |
| access token | токен доступа | Ключ для чтения закрытого датасета |
| serverless | serverless | Нет своего сервера |
| compute unit | compute unit (`CU`) | Единица вычислений в тарифе |
| share | `share` | Доступ к снимку базы только для чтения |
| Dual Execution | `Dual Execution` | Запрос идёт частично локально, частично в облаке |
| hybrid query | hybrid-запрос | Запрос по локальным и облачным данным |
| schema | схема (`schema`) | Группа таблиц внутри базы |
