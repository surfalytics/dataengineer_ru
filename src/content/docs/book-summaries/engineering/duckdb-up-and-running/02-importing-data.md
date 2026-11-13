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

**Главная мысль:** на практике данные лежат в разных местах: в CSV, Parquet, Excel и серверных базах. Для каждого источника в DuckDB есть простая функция или команда. Для больших файлов автор советует `COPY` и Parquet.

## О чём глава

Глава отвечает на вопрос: как положить данные в DuckDB и выгрузить обратно? В [главе 1](/book-summaries/engineering/duckdb-up-and-running/01-getting-started/) мы создали первую базу. Теперь идут источники: CSV, Parquet, Excel и MySQL. Датасет книги: рейсы США за 2015 год с Kaggle. Мы строим свои данные.

![Источники данных DuckDB: CSV, Parquet, Excel и MySQL читаются в таблицу, а COPY выгружает обратно в файлы](/assets/duckdb-up-and-running/ch02-import-sources.png)

## Создание базы

Базу создаёт `connect()`. Без аргументов или с `':memory:'` это база в памяти. С именем файла, например `connect(database='mydb.duckdb')`, она хранится на диске. Расширение файла любое.

`read_only=True` работает, только если файл уже есть. Он нужен, когда несколько процессов читают один файл. Автор предупреждает: для базы в памяти этот флаг не ставьте. Она станет неизменяемой.

## CSV

CSV легкий, простой (текст со строками и разделителем) и гибкий (числа, строки, даты). Автор показывает два способа загрузки и экспорт.

![Три способа загрузить CSV: CREATE TABLE AS с автоопределением типов, COPY в таблицу со схемой и register для DataFrame](/assets/duckdb-up-and-running/ch02-csv-ways.png)

### Способ 1: SQL-запрос

Самый простой путь: `CREATE TABLE t AS SELECT * FROM read_csv_auto('f.csv')`. Функция сама находит заголовок и угадывает типы. Без заголовка столбцы называются `column0`, `column1`.

- Повторный `CREATE TABLE` падает. Помогают `DROP TABLE IF EXISTS` и `CREATE OR REPLACE TABLE`.
- `LIMIT` берёт часть большого файла. 
- `.df()` делает DataFrame. Вызывайте его только для просмотра итога: он грузит данные в память.

Второй путь: создать таблицу со своей схемой и выполнить `COPY t FROM 'f.csv'`. Число столбцов должно совпасть, а значения должны приводиться к типам таблицы. Иначе будет ошибка. Это путь для контроля над типами. Для больших файлов `COPY` даёт лучшую скорость. Ещё есть `read_csv('f.csv', names=[...])` для своих имён и `all_varchar=true`, чтобы читать всё как строки.

### Способ 2: register()

`register()` показывает DataFrame в SQL как виртуальную таблицу без копирования. Автор читает файл через `read_csv` с `header=True` и `columns`, потом вызывает `conn.register("airlines", airlines)`.

Зачем `read_csv`, если есть `read_csv_auto`? Если файл оформлен неровно или заголовок похож на данные, `read_csv_auto` принимает его за строку данных. Автор предупреждает: поведение может измениться, пробуйте обе функции.

На DuckDB 1.4.3 наш файл с заголовком из строк `read_csv_auto` прочитал верно, но проверяйте на своей версии.

Наш запуск: типы, ведущие нули, ошибка `COPY`, `register()` и экспорт. Полный код: [ch02_csv_load.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch02_csv_load.py).

```text
[('iata_code', 'VARCHAR'), ('airport', 'VARCHAR'), ('city', 'VARCHAR'), ('zip_code', 'VARCHAR')]
[('00123',), ('00456',), ('00789',)]
[('00123',), ('00456',), ('00789',)]
[(123,), (456,), (789,)]
COPY упал: ConversionException
(3,)
iata_code,city
SVO,Москва
LED,Санкт-Петербург
```

DuckDB сам оставил `zip_code` строкой. Явный `INTEGER` съел нули: `00123` стало `123`. Неподходящий тип дал `ConversionException`: `COPY` упал сразу, это и нужно.

### Экспорт в CSV

`COPY (SELECT ...) TO 'out.csv' (HEADER, DELIMITER ',')`. В скобках любой запрос, поэтому можно взять часть столбцов и строк. Если в `FROM` стоит имя файла, часть одного файла копируется в другой без таблицы.

## Parquet

`Parquet` — открытый колоночный формат Apache. Он самоописывающийся: схема лежит внутри файла. В CSV данные идут по строкам. В Parquet каждый столбец хранится отдельно, с одним типом. Файл легче: похожие данные сжимаются лучше. Нужные столбцы читаются быстро, а это главное для `OLAP`.

![CSV хранит строки подряд, Parquet хранит столбцы отдельно и со схемой внутри; наш замер: 21,7 МБ против 5,0 МБ](/assets/duckdb-up-and-running/ch02-csv-vs-parquet.png)

Автор делает Parquet из CSV через pandas и `fastparquet`. Мы обошлись без них: `COPY ... TO ... (FORMAT PARQUET)` пишет Parquet сам. Наш замер на 1 млн строк ([ch02_parquet_size.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch02_parquet_size.py)):

```python
import os
import tempfile

import duckdb

tmp = tempfile.mkdtemp()
con = duckdb.connect()
con.sql("""
    CREATE TABLE flights AS
    SELECT i AS flight_id,
           ['SU','S7','DP','U6'][1 + i % 4] AS carrier,
           CAST(hash(i) % 120 AS INTEGER) - 20 AS arr_delay,
           'route ' || (i % 50) AS route
    FROM range(1000000) t(i)
""")
con.sql(f"COPY flights TO '{tmp}/flights.csv' (HEADER)")
con.sql(f"COPY flights TO '{tmp}/flights.parquet' (FORMAT PARQUET)")
print("CSV, МБ:    ", round(os.path.getsize(f"{tmp}/flights.csv") / 1e6, 1))
print("Parquet, МБ:", round(os.path.getsize(f"{tmp}/flights.parquet") / 1e6, 1))
# схема лежит внутри файла
print(con.sql(f"SELECT name, type FROM parquet_schema('{tmp}/flights.parquet') WHERE name <> 'duckdb_schema'").fetchall())
```

```text
CSV, МБ:     21.7
Parquet, МБ: 5.0
[('flight_id', 'INT64'), ('carrier', 'BYTE_ARRAY'), ('arr_delay', 'INT32'), ('route', 'BYTE_ARRAY')]
```

### Загрузка и экспорт Parquet

- Читать: `SELECT * FROM read_parquet('f.parquet')`, например `CREATE TABLE t AS ... LIMIT 100`.
- В готовую таблицу: `COPY t FROM 'f.parquet' (FORMAT PARQUET)`.
- Записать: `COPY t TO 'f.parquet' (FORMAT PARQUET)`. Часть строк: `COPY (SELECT ... LIMIT 100) TO ...`.

Parquet — обычный выбор для облачного хранилища, `data lake` и конвейеров машинного обучения.

## Excel

### Загрузка

Нужно расширение `spatial`. Ставят его один раз: `INSTALL spatial`, подключают `LOAD spatial`. Среди других расширений автор называет `httpfs` (HTTP и облако) и `sqlite`.

Лист читает `st_read('f.xlsx', layer='airports')`. Файл с паролем DuckDB не откроет: снимите пароль заранее.

Заголовком становится первая строка листа, если она на него похожа. Этим управляет переменная окружения `OGR_XLSX_HEADERS` (из библиотеки GDAL/OGR): `DISABLE` (заголовка нет, столбцы `Field1`, `Field2`), `FORCE` (первая строка всегда заголовок), `AUTO` (по умолчанию).

Свои имена даёт таблица с нужными столбцами и `INSERT INTO ... SELECT * FROM st_read(...)`. `COPY` с Excel не работает. Автор предупреждает: не вставляйте строки по одной на больших данных. `OGR_XLSX_FIELD_TYPES=STRING` делает все столбцы строками.

Наш запуск ([ch02_excel_header.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch02_excel_header.py)). Нужна сеть для `INSTALL`.

```python
import os
import tempfile

import duckdb

tmp = tempfile.mkdtemp()
xlsx = f"{tmp}/airlines.xlsx"
con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial")
con.sql(f"""
    COPY (SELECT * FROM (VALUES ('SU','Аэрофлот'), ('S7','S7 Airlines')) t(code, name))
    TO '{xlsx}' WITH (FORMAT GDAL, DRIVER 'xlsx')
""")
# AUTO: в файле все значения строки, первая строка считается данными
print(con.sql(f"SELECT * FROM st_read('{xlsx}')").fetchall())
os.environ["OGR_XLSX_HEADERS"] = "FORCE"  # первая строка листа - заголовок
print(con.sql(f"SELECT * FROM st_read('{xlsx}')").fetchall())
```

```text
[('code', 'name'), ('SU', 'Аэрофлот'), ('S7', 'S7 Airlines')]
[('SU', 'Аэрофлот'), ('S7', 'S7 Airlines')]
```

Все значения листа строки, поэтому `AUTO` считает первую строку данными. С `FORCE` она становится заголовком.

> **Пояснение:** в новых версиях есть расширение `excel` с функцией `read_xlsx('f.xlsx', header=true)`. Этого нет в книге. На нашем файле оно дало тот же результат, что `st_read` с `FORCE`.

### Экспорт в Excel

`COPY t TO 'f.xlsx' WITH (FORMAT GDAL, DRIVER 'xlsx')`. Существующий файл вызовет ошибку. Драйвер не пишет даты и время, поэтому приведите их к `VARCHAR`.

## MySQL

Часто данные лежат на сервере БД. Автор показывает два пути.

![Два пути из MySQL в DuckDB: Python-цикл с INSERT и расширение mysql с командой ATTACH](/assets/duckdb-up-and-running/ch02-mysql-ways.png)

**Вручную.** Открыть соединения DuckDB и MySQL (`mysql-connector-python`), выбрать данные, создать в DuckDB таблицу с той же схемой, вставить каждую строку, закрыть соединения.

**Расширение `mysql`.** `INSTALL mysql; LOAD mysql;`, затем `ATTACH 'host=... user=... password=... database=My_DB' AS mysqldb (TYPE MYSQL)` и `USE mysqldb`. Таблицы MySQL видны в DuckDB прямо в запросах.

Правило автора: нужны простота и скорость, берите расширение. Нужны контроль схемы или преобразования, или расширение недоступно, берите ручной путь. Для частой работы лучше расширение.

MySQL-код мы не запускали: нужен сервер. Пароль берите из переменной окружения, не из кода.

## Итоги главы

- Базу создаёт `connect()`: в памяти по умолчанию, в файле при указании имени.
- CSV грузят через `read_csv_auto` или через схему и `COPY`. Для больших файлов лучше `COPY`.
- Parquet хранит столбцы отдельно и схему внутри. Он легче CSV и читается быстрее.
- Excel читается через `spatial` и `st_read`. `COPY` для него не работает.
- Из MySQL данные берут вручную или через `ATTACH`. Для частой работы лучше расширение.

## Ключевые термины

| Термин | Значение |
|---|---|
| `read_csv_auto` | Чтение CSV с автоопределением схемы |
| `COPY` | Быстрая загрузка и выгрузка файлов |
| `Parquet` | Колоночный формат со схемой внутри |
| `register()` | Показать DataFrame как таблицу в SQL |
| `ATTACH` | Подключить внешнюю или другую базу |
| `Extension` | Модуль, который добавляет возможности DuckDB |

## Что это значит на практике

- Для сырых выгрузок используйте Parquet, не CSV. Он меньше и быстрее.
- Большой CSV грузите через `COPY` с явной схемой. Так ошибки типов видны сразу.
- Автоопределение типов удобно для разведки. В пайплайне задавайте схему сами.
- `ATTACH` к MySQL или Postgres позволяет делать `ELT` без отдельного инструмента копирования.
- Коды, номера и индексы с ведущими нулями читайте как `VARCHAR`. Тип `INTEGER` съедает нули.
- Excel лучше сразу превратить в CSV или Parquet.

## Практика в DuckDB

Запустите `duckdb` в терминале. Блоки идут по порядку. Файлы пишутся в `/tmp`.

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

1. Чем `read_csv_auto` отличается от `read_csv` с параметрами? Когда нужна вторая функция?
2. Когда лучше использовать `COPY`, а не `CREATE TABLE AS SELECT`?
3. Почему Parquet лучше CSV для аналитики?
4. Чем `register()` отличается от `CREATE TABLE`?
5. Какие два способа загрузить данные из MySQL описывает автор? Что выбрать для частой работы?

Предыдущая: [Глава 1. Старт с DuckDB](/book-summaries/engineering/duckdb-up-and-running/01-getting-started/). Следующая: [Глава 3. Основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/).
