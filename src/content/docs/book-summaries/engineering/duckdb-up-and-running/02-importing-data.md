---
title: "DuckDB: Up and Running, глава 2: Импорт данных"
head:
  - tag: title
    content: "Как загрузить CSV, Parquet, Excel и MySQL в DuckDB | Инжиниринг Данных"
description: "Конспект главы 2 DuckDB: Up and Running на русском. read_csv_auto, COPY, Parquet, Excel через spatial, MySQL через ATTACH, экспорт данных."
sidebar:
  order: 2
  label: "2. Импорт данных"
tags:
  - books
  - duckdb
  - sql
---

**Главная мысль:** DuckDB читает данные из многих источников: CSV, Parquet, Excel, MySQL. Для каждого есть простая функция или команда. Для больших файлов лучше `COPY` и Parquet.

## Создание базы

| Способ | Что получится |
|---|---|
| `duckdb.connect()` или `':memory:'` | База в памяти. Пропадает после закрытия |
| `duckdb.connect('mydb.duckdb')` | Файл на диске. Расширение любое |
| `read_only=True` | Только чтение. Нужно, если несколько процессов открывают один файл |

Для базы в памяти режим `read_only=True` не имеет смысла: в неё нельзя ничего записать.

## CSV

Книга берёт набор данных о рейсах США за 2015 год. В нём три файла: авиакомпании, аэропорты, рейсы. В конспекте мы используем свои данные.

### Загрузка

| Способ | Пример | Когда |
|---|---|---|
| `CREATE TABLE ... AS SELECT * FROM read_csv_auto('f.csv')` | Самый простой путь | Быстрый старт |
| `FROM 'f.csv'` | `SELECT` и функцию можно опустить | Короткая запись |
| `CREATE TABLE` + `COPY t FROM 'f.csv'` | Сначала схема, потом данные | Нужен контроль типов. Лучшая скорость на больших файлах |
| `read_csv('f.csv', names=[...])` | Свои имена столбцов | Нет заголовка |
| `all_varchar=true` | Все столбцы как строки | Типы определяются неверно |
| `LIMIT n` | Только часть файла | Проба на большом файле |

- `read_csv_auto` сам определяет разделитель, заголовок и типы. Если заголовка нет, столбцы называются `column0`, `column1`.
- В `COPY` число столбцов в файле и таблице должно совпасть. Значения должны приводиться к типам таблицы.
- Если таблица уже есть, `CREATE TABLE` упадёт с ошибкой. Используйте `DROP TABLE IF EXISTS` или `CREATE OR REPLACE TABLE`.
- Автор отмечает: `read_csv_auto` иногда принимает строку-заголовок за данные. Поведение может меняться между версиями. Проверяйте результат.

### Регистрация и экспорт

- В Python метод `register()` делает DataFrame видимым в SQL как виртуальную таблицу. Копии данных нет.
- Экспорт: `COPY (SELECT ...) TO 'out.csv' (HEADER, DELIMITER ',')`. Можно сразу выбрать часть строк и столбцов.
- Файл можно копировать в другой файл через `COPY (SELECT ... FROM 'in.csv' LIMIT 10) TO ...`, не создавая таблицу.

## Parquet

`Parquet` — колоночный формат файла. Схема лежит внутри файла. Данные сжимаются лучше, чем в CSV. Читать нужные столбцы быстро.

| Задача | Команда |
|---|---|
| Прочитать | `SELECT * FROM read_parquet('f.parquet')` |
| Загрузить в новую таблицу | `CREATE TABLE t AS SELECT * FROM read_parquet(...)` |
| Добавить в существующую | `INSERT INTO t SELECT * FROM read_parquet(...)` или `COPY t FROM 'f.parquet' (FORMAT PARQUET)` |
| Записать | `COPY t TO 'f.parquet' (FORMAT PARQUET)` |

В книге Parquet-файл делают через pandas и `fastparquet`. В DuckDB это не нужно: `COPY ... TO ... (FORMAT PARQUET)` пишет Parquet сам.

## Excel

- В книге Excel читают через расширение `spatial`: `INSTALL spatial; LOAD spatial;`, затем `st_read('file.xlsx', layer='sheet')`.
- Имя листа задаёт параметр `layer`.
- Первая строка листа по умолчанию становится заголовком, если похожа на него. Переменная `OGR_XLSX_HEADERS` управляет этим: `DISABLE`, `FORCE`, `AUTO`.
- Без заголовка столбцы называются `Field1`, `Field2`. Свои имена: создайте таблицу с нужными столбцами и сделайте `INSERT INTO ... SELECT * FROM st_read(...)`. `COPY` с Excel не работает.
- Типы определяет `OGR_XLSX_FIELD_TYPES`. Значение `STRING` делает все столбцы строками.
- Экспорт: `COPY t TO 'f.xlsx' WITH (FORMAT GDAL, DRIVER 'xlsx')`. Существующий файл вызовет ошибку. Даты и время нужно привести к `VARCHAR`.
- Пароль на файле не поддерживается. Снимите его заранее.

> Расширение ставят один раз командой `INSTALL`. Потом его подключают командой `LOAD`. В новых версиях DuckDB есть отдельное расширение `excel` с функцией `read_xlsx`. Это наше замечание, его нет в книге. Проверьте документацию своей версии.

## MySQL

Два пути:

| Путь | Как | Плюсы |
|---|---|---|
| Вручную | Python-коннектор читает строки из MySQL, вы делаете `INSERT` в DuckDB | Полный контроль схемы и преобразований |
| Расширение `mysql` | `INSTALL mysql; LOAD mysql; ATTACH '...' AS mysqldb (TYPE MYSQL)` | Проще и быстрее. Таблицы видны прямо в DuckDB |

Автор советует расширение для частой работы. Ручной путь нужен, если расширение недоступно или нужны преобразования. Построчный `INSERT` для больших данных медленный.

Не храните пароль в коде. Берите его из переменной окружения или менеджера секретов.

## Ключевые термины

| Термин | Значение |
|---|---|
| `read_csv_auto` | Чтение CSV с автоопределением схемы |
| `COPY` | Быстрая загрузка и выгрузка файлов |
| `Parquet` | Колоночный формат с схемой внутри |
| `register()` | Показать DataFrame как таблицу в SQL |
| `ATTACH` | Подключить внешнюю или другую базу |
| `Extension` | Модуль, который добавляет возможности DuckDB |

## Что это значит на практике

- Для сырых выгрузок используйте Parquet, не CSV. Он меньше и быстрее.
- Большой CSV грузите через `COPY` с явной схемой. Так ошибки типов видны сразу.
- Автоопределение типов удобно для разведки. В пайплайне задавайте схему сами.
- `ATTACH` к MySQL или Postgres позволяет делать `ELT` без отдельного инструмента копирования.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Файлы пишутся в `/tmp`. В браузерной версии пути другие, лучше использовать терминал.

### Шаг 1. Готовим файлы

```sql
COPY (
    SELECT * FROM (VALUES
        ('SVO', 'Шереметьево', 'Москва',  'RU'),
        ('LED', 'Пулково',     'Санкт-Петербург', 'RU'),
        ('KZN', 'Казань',      'Казань',  'RU'),
        ('AER', 'Сочи',        'Сочи',    'RU')
    ) t(iata_code, airport, city, country)
) TO '/tmp/duck_ch2_airports.csv' (HEADER, DELIMITER ',');

-- файл без заголовка
COPY (
    SELECT * FROM (VALUES ('SU', 'Аэрофлот'), ('S7', 'S7 Airlines'), ('DP', 'Победа')) t(a, b)
) TO '/tmp/duck_ch2_airlines.csv' (HEADER false, DELIMITER ',');
```

### Шаг 2. Загружаем и проверяем

```sql
CREATE OR REPLACE TABLE airports AS
SELECT * FROM read_csv_auto('/tmp/duck_ch2_airports.csv');

-- у файла без заголовка задаём имена сами
CREATE OR REPLACE TABLE airlines AS
SELECT * FROM read_csv('/tmp/duck_ch2_airlines.csv',
                       header = false,
                       names = ['carrier_code', 'carrier_name']);

SHOW TABLES;

SELECT count(*) AS airports_rows FROM airports;   -- 4
SELECT * FROM airlines ORDER BY carrier_code;
```

### Задания

**1.** Сохраните таблицу `airports` в Parquet. Прочитайте файл и посчитайте строки.

<details>
<summary>Решение</summary>

```sql
COPY airports TO '/tmp/duck_ch2_airports.parquet' (FORMAT PARQUET);

SELECT count(*) AS n FROM read_parquet('/tmp/duck_ch2_airports.parquet');
```

Результат: 4. Схема пришла из файла, указывать типы не пришлось.

</details>

**2.** Создайте таблицу `airports_copy` с явной схемой. Загрузите в неё CSV через `COPY`.

<details>
<summary>Решение</summary>

```sql
CREATE OR REPLACE TABLE airports_copy (
    iata_code VARCHAR,
    airport   VARCHAR,
    city      VARCHAR,
    country   VARCHAR
);

COPY airports_copy FROM '/tmp/duck_ch2_airports.csv' (HEADER);

SELECT count(*) AS n FROM airports_copy;
```

Результат: 4. Столбцы файла совпали со схемой таблицы.

</details>

**3.** Выгрузите в новый CSV только столбцы `iata_code` и `city`, и только российские аэропорты на букву «С».

<details>
<summary>Решение</summary>

```sql
COPY (
    SELECT iata_code, city
    FROM airports
    WHERE country = 'RU' AND city LIKE 'С%'
    ORDER BY iata_code
) TO '/tmp/duck_ch2_subset.csv' (HEADER, DELIMITER ',');

SELECT * FROM read_csv_auto('/tmp/duck_ch2_subset.csv');
```

Две строки: AER (Сочи) и LED (Санкт-Петербург).

</details>

## Вопросы для самопроверки

1. Чем `read_csv_auto` отличается от `read_csv` с параметрами?
2. Когда лучше использовать `COPY`, а не `CREATE TABLE AS SELECT`?
3. Почему Parquet лучше CSV для аналитики?
4. Какие два способа загрузить данные из MySQL описывает автор? Что выбрать для частой работы?

Предыдущая: [Глава 1. Старт с DuckDB](/book-summaries/engineering/duckdb-up-and-running/01-getting-started/). Следующая: [Глава 3. Основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/).
