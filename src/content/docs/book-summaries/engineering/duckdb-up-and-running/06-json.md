---
title: "DuckDB: Up and Running, глава 6: JSON"
head:
  - tag: title
    content: "JSON в DuckDB: read_json_auto и COPY | Инжиниринг Данных"
description: "Конспект главы 6 DuckDB: Up and Running на русском. Типы JSON, read_json_auto, read_json, вложенные объекты, unnest, загрузка по маске, COPY и экспорт."
sidebar:
  order: 6
  label: "6. JSON"
tags:
  - books
  - duckdb
  - sql
  - json
---

**Главная мысль:** DuckDB читает JSON как таблицу. Простые файлы грузит одна функция `read_json_auto()`. Для сложных нужны `read_json()`, `unnest` и обращение к полям по ключу.

## О чём глава

В [главе 2](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/) мы грузили CSV, Parquet, Excel и MySQL. JSON популярен у разработчиков и не имеет жёсткой схемы: ключи и значения каждый задаёт сам. Поэтому ему отведена отдельная глава: три способа загрузки, вложенные данные, несколько файлов, экспорт.

![Три способа загрузки JSON](/assets/duckdb-up-and-running/ch06-three-ways.png)

Начинайте с `read_json_auto()`. Если он ошибся, берите `read_json()`. Для больших простых файлов подходит `COPY`.

## Минимум про JSON

JSON легко читать человеку и разбирать программе. В нём шесть типов:

- `Object` — набор пар ключ-значение в фигурных скобках: `{"id": 1}`.
- `String`, `Number`, `Boolean` и `null` — простые значения.
- `Array` — упорядоченный список в квадратных скобках: `[1, 2, 3]`.

Ключ всегда строка и уникален. Значение может быть любым, в том числе другим объектом (`nested object`). После последней пары запятой нет.

## Три способа загрузки

### read_json_auto()

Функция сама разбирает пары ключ-значение и определяет типы. Массив объектов становится таблицей, ключи становятся колонками. Типы видны в `DESCRIBE`.

- Сохранить результат: `CREATE TABLE t AS FROM 'f.json'`.
- При `records = false` (по умолчанию `true`) объект целиком попадает в одну колонку `json` типа `struct`.
- Нужные поля выбираем обычным `SELECT name, email`.

### read_json()

`read_json_auto()` — это `read_json()` с включённым автоопределением. Ручная настройка нужна редко: когда функция не поняла формат или схему.

Параметр `format` бывает `array` (один массив объектов), `newline_delimited` или `nd` (один объект на строку, NDJSON), `unstructured` (любой JSON, в том числе нерегулярный) и `auto`. Параметр `columns` задаёт колонки и типы: `{id: 'INTEGER', name: 'VARCHAR'}`. Без него читаются все поля. Для NDJSON есть `read_ndjson_auto()`.

![Форматы JSON-файла и экспорта](/assets/duckdb-up-and-running/ch06-formats.png)

### Вложенный JSON

Вложенный объект `read_json()` кладёт в одну колонку типа `struct` (объект с именованными полями). Отдельные колонки получаем ключами в `SELECT`: `address['city']`. Глубже — цепочкой: `address['location']['zip']`. Если у части записей поля нет, будет `NULL`.

### Массив внутри ключа

Бывает, что весь JSON выглядит как `{"people": [ ... ]}`. Тогда массив попадает в одну ячейку. Два шага: `unnest(people) AS p` делает из элементов строки, потом поля достаём по ключу: `p['id']` или `p.id`.

![Вложенный объект и массив в колонки](/assets/duckdb-up-and-running/ch06-nested-flow.png)

Два запроса на наших данных:

```text
-- struct: поля по ключу
SELECT name, address['city'] AS city, address['location']['zip'] AS zip
FROM read_ndjson_auto('nested.ndjson');

-- unnest: массив people в строки
SELECT p['id'] AS id, p['name'] AS name, p['address']['city'] AS city
FROM (SELECT unnest(people) AS p FROM read_json('wrapped.json'));
```

```text
struct: поля по ключу, у Веры location нет
   ('Анна', 'Москва', 101000)
   ('Борис', 'Казань', 420000)
   ('Вера', 'Тверь', None)
unnest: массив people в строки
   (1, 'Анна', 'Москва')
   (2, 'Борис', 'Казань')
   (3, 'Вера', 'Тверь')
```

## Несколько файлов

Можно передать список: `read_json(['a.json', 'b.json'])`. Результат — объединение файлов. Колонки совпадают с ключами, порядок ключей неважен. Где поля нет, будет пропуск (`NaN` или `None` в Python, `NULL` в SQL). Структура файлов лучше совпадает. Автор советует проверять это Python-скриптом.

Ловушка: поле в одном файле число, в другом строка. Автор пишет, что DuckDB может привести колонку к строке, а при серьёзном конфликте выдаст ошибку. Выравнивайте типы заранее или используйте `CAST`.

> **Пояснение:** в DuckDB 1.4.3 такая колонка получает тип `JSON`, а не `VARCHAR` (см. вывод ниже).

Вместо списка можно дать маску `glob`: `*` — любые символы, `**` — любые подпапки, `?` — один символ, `[abc]` и `[a-z]` — символ из набора или диапазона. Например, `read_json('json?.json')` читает файлы с одним символом между `json` и `.json`.

## COPY ... FROM

Автор считает `COPY ... FROM` лучшим для больших данных. Он грузит пачками, тратит меньше памяти, использует параллелизм и пишет прямо в таблицу. `read_json()` читает весь файл в память и лучше для небольших интерактивных задач.

Сначала создайте таблицу с нужной схемой. Потом: `COPY people FROM 'f.json' (FORMAT JSON, AUTO_DETECT true)`. Для сложной структуры метод не рекомендуется.

## Экспорт в JSON

Экспорт нужен для обмена данными и резервной копии. Его делает `COPY ... TO`. По умолчанию получается не строгий JSON, а NDJSON. Чтобы получить валидный массив, добавьте `ARRAY true`.

Список файлов и два вида экспорта:

```text
SELECT * FROM read_json(['day1.json', 'day2.json']);
COPY people TO 'out.json' (FORMAT JSON);
COPY people TO 'out_array.json' (FORMAT JSON, ARRAY true);
```

```text
Два файла, поле temp: число и строка
   (1, 'Москва', '3')
   (2, 'Казань', '"холодно"')
Тип temp: JSON
COPY TO без ARRAY:
{"id":1,"name":"Анна","weight":61.5}
{"id":2,"name":"Борис","weight":80.0}
{"id":3,"name":"Вера","weight":55.25}
COPY TO с ARRAY true:
[
	{"id":1,"name":"Анна","weight":61.5},
	{"id":2,"name":"Борис","weight":80.0},
	{"id":3,"name":"Вера","weight":55.25}
]
```

Код: [ch06_snippet_nested.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch06_snippet_nested.py), [ch06_snippet_files.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch06_snippet_files.py), полный разбор: [ch06_json.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch06_json.py).

## Итоги главы

- `read_json_auto()` — первый и самый прямой способ. Пробуйте его всегда первым.
- `read_json()` нужен, когда автоопределение не справилось: там вы задаёте `format` и `columns`.
- `COPY ... FROM` подходит для простой структуры и больших файлов. Таблицу нужно создать заранее.
- Вложенный объект приходит как `struct`, массив внутри ключа разворачивает `unnest`.
- Несколько файлов читаем списком или маской. Структура и типы полей должны совпадать.
- Экспорт делает `COPY ... TO`. По умолчанию это NDJSON, строгий массив даёт `ARRAY true`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `struct` | Тип DuckDB для вложенного объекта с именованными полями |
| NDJSON | JSON, где одна строка файла — один объект |
| `unnest` | Разворачивает массив в строки |
| `glob` | Маска имён файлов: `*`, `?`, `**` |

## Что это значит на практике

- Ответы API и логи часто приходят как JSON. DuckDB читает их без ETL.
- Для логов и потоков лучше NDJSON. Его можно читать частями, а массив нужно читать целиком.
- Сначала смотрите схему: `DESCRIBE SELECT * FROM read_json_auto('f.json')`. Потом выбирайте поля.
- Для регулярной загрузки задавайте `columns` явно. Тогда новое поле в источнике не меняет схему тихо.
- Папку файлов за много дней читайте одной маской. Затем пишите результат в `Parquet`.

## Практика в DuckDB

Запустите `duckdb`. Блоки идут по порядку. JSON-файлы создаём сами в `/tmp`.

### Шаг 1. Создаём файлы

```sql
-- простой массив объектов
COPY (
    SELECT * FROM (VALUES
        (1, 'Анна',  'Москва',  140.5),
        (2, 'Борис', 'Казань',  155.0),
        (3, 'Вера',  'Тверь',   200.1)
    ) t(id, name, city, score)
) TO '/tmp/duck_ch6_ex_people.json' (FORMAT JSON, ARRAY true);

-- один объект на строку, с вложенным адресом
COPY (
    SELECT id, name, {'city': city, 'zip': zip} AS address
    FROM (VALUES
        (1, 'Анна',  'Москва', 101000),
        (2, 'Борис', 'Казань', 420000),
        (3, 'Вера',  'Тверь',  170000)
    ) t(id, name, city, zip)
) TO '/tmp/duck_ch6_ex_nested.ndjson' (FORMAT JSON, ARRAY false);

-- объект с массивом внутри ключа
COPY (
    SELECT [{'id': 10, 'item': 'Ручка'}, {'id': 11, 'item': 'Блокнот'}] AS orders
) TO '/tmp/duck_ch6_ex_orders.json' (FORMAT JSON, ARRAY false);
```

### Шаг 2. Проверяем

```sql
DESCRIBE SELECT * FROM read_json_auto('/tmp/duck_ch6_ex_people.json');

SELECT count(*) AS n FROM read_json_auto('/tmp/duck_ch6_ex_people.json');  -- ожидаем 3
```

### Задания

1. Прочитайте `ex_people.json`, но оставьте только `name` и `city`.

<details>
<summary>Решение</summary>

```sql
SELECT name, city FROM read_json_auto('/tmp/duck_ch6_ex_people.json');
```

</details>

2. Прочитайте `ex_nested.ndjson` и достаньте `address.city` и `address.zip` в отдельные колонки.

<details>
<summary>Решение</summary>

```sql
SELECT id, name,
       address['city'] AS city,
       address['zip']  AS zip
FROM read_json_auto('/tmp/duck_ch6_ex_nested.ndjson');
```

</details>

3. Разверните массив `orders` из `ex_orders.json` в строки и достаньте `id` и `item`.

<details>
<summary>Решение</summary>

```sql
SELECT o['id'] AS id, o['item'] AS item
FROM (
    SELECT unnest(orders) AS o
    FROM read_json_auto('/tmp/duck_ch6_ex_orders.json')
);
```

`unnest` делает из элементов массива строки.
</details>

## Вопросы для самопроверки

1. Когда нужен `read_json()`, а не `read_json_auto()`?
2. Как достать поле из вложенного объекта и из массива внутри ключа?
3. Что будет, если у поля в разных файлах разный тип?
4. Почему автор советует `COPY` для больших файлов?

Предыдущая: [Глава 5. EDA и геоанализ](/book-summaries/engineering/duckdb-up-and-running/05-eda-spatial/). Следующая: [Глава 7. JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/).
