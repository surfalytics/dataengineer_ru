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

## Минимум про JSON

| Тип | Пример |
|---|---|
| Object | `{"id": 1}`. Набор пар ключ-значение |
| String | `"Анна"` |
| Number | `79.5`, `3` |
| Boolean | `true`, `false` |
| Array | `[1, 2, 3]`. Упорядоченный список |
| null | Пустое значение |

- Ключи в объекте уникальны. Ключ — всегда строка.
- Объект может лежать внутри объекта. Это `nested object`.
- После последней пары запятой нет.

## Три способа загрузки

| Способ | Когда использовать |
|---|---|
| `read_json_auto()` | По умолчанию. Тип и схема определяются сами |
| `read_json()` | Когда авто-определение ошибается. Вы задаёте `format` и `columns` |
| `COPY ... FROM` | Большие файлы. Грузит пачками и параллельно |

## read_json_auto

- Массив объектов превращается в таблицу. Ключи становятся колонками.
- Параметр `records = false` кладёт каждый объект в одну колонку `json` как `struct`.
- Можно выбрать только нужные поля: `SELECT name, email FROM read_json_auto('f.json')`.
- `CREATE TABLE t AS FROM 'f.json'` сохраняет результат в таблицу.

## read_json

`read_json_auto()` — это `read_json()` с включённым автоопределением. Ручная настройка нужна редко.

Параметр `format`:

| Значение | Что это |
|---|---|
| `array` | Один массив объектов |
| `newline_delimited` или `nd` | Один объект на строку (NDJSON) |
| `unstructured` | Любой JSON, в том числе нерегулярный |
| `auto` | Определить самому |

- Параметр `columns` задаёт типы: `{id: 'INTEGER', name: 'VARCHAR'}`. Колонки, которых нет в списке, не читаются.
- Для NDJSON есть короткая функция `read_ndjson_auto()`.

## Вложенный JSON

- Вложенный объект приходит в одну колонку типа `struct`.
- Поле достаём по ключу: `address['city']`. Или через точку: `address.city`.
- Если глубже ещё один объект, ключи идут цепочкой: `address['location']['zip']`.
- Если у части записей поля нет, в этой колонке будет `NULL`.

### Массив внутри ключа

Если файл выглядит как `{"people": [ ... ]}`, весь массив попадает в одну ячейку. Дальше два шага:

1. `unnest(people)` разворачивает массив в строки.
2. Обращаемся к полям каждой строки по ключу.

## Несколько файлов

- Можно дать список: `read_json(['a.json', 'b.json'])`. Колонки объединяются по имени. Недостающие поля станут `NULL`.
- Можно дать маску (`glob`): `read_json('data/*.json')`.

| Символ | Значение |
|---|---|
| `*` | Любое число символов |
| `**` | Любое число подпапок |
| `?` | Один любой символ |
| `[abc]`, `[a-z]` | Один символ из набора или диапазона |

- Если тип поля в файлах разный (число и строка), DuckDB приведёт колонку к строке. Иногда будет ошибка. Лучше привести тип явно через `CAST`.

## COPY и экспорт

- Для `COPY FROM` таблицу нужно создать заранее с нужной схемой. Затем `COPY t FROM 'f.json' (FORMAT JSON, AUTO_DETECT true)`.
- Автор советует `COPY` для больших файлов. Для сложной структуры он не подходит.
- Экспорт делает тот же `COPY`, только в другую сторону: `COPY t TO 'out.json'`.
- Экспорт нужен для обмена с другими системами и для резервной копии.

## Ключевые термины

| Термин | Значение |
|---|---|
| `struct` | Тип DuckDB для вложенного объекта с именованными полями |
| NDJSON | JSON, где одна строка файла — один объект |
| `unnest` | Разворачивает массив в строки |
| `glob` | Маска имён файлов: `*`, `?`, `**` |
| `AUTO_DETECT` | Определение схемы по файлу |
| `records` | Параметр: разложить объект по колонкам или оставить в одной |

## Что это значит на практике

- Ответы API и логи часто приходят как JSON. DuckDB читает их без отдельного ETL.
- Для логов и потоков лучше NDJSON. Его можно читать частями, а массив нужно читать целиком.
- Сначала смотрите схему: `DESCRIBE SELECT * FROM read_json_auto('f.json')`. Потом выбирайте поля.
- Для регулярной загрузки задавайте `columns` явно. Тогда новое поле в источнике не меняет схему тихо.
- Папку файлов за много дней читайте одной маской. Затем пишите результат в `Parquet`.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. JSON-файлы мы создаём сами командой `COPY ... TO` в папке `/tmp`.

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

Колонки определились сами, нужные мы выбрали обычным `SELECT`.
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

Поле `address` — это `struct`. К его полям обращаемся по ключу.
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

Получим две строки: ручка и блокнот. `unnest` делает из элементов массива строки.
</details>

4. Загрузите `ex_people.json` в таблицу через `COPY` с заранее заданной схемой. Затем выгрузите её в `ex_out.json`.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE people (id INTEGER, name VARCHAR, city VARCHAR, score FLOAT);
COPY people FROM '/tmp/duck_ch6_ex_people.json' (FORMAT JSON, AUTO_DETECT true);
SELECT count(*) AS n FROM people;  -- 3
COPY people TO '/tmp/duck_ch6_ex_out.json' (FORMAT JSON, ARRAY true);
```

Схема задана вручную, поэтому типы предсказуемы. Файлы `/tmp/duck_ch6_*` можно удалить после занятия.
</details>

## Вопросы для самопроверки

1. Чем `read_json_auto()` отличается от `read_json()`? Когда нужен второй?
2. Как достать поле из вложенного объекта? Как из массива внутри ключа?
3. Что станет с колонкой, если в разных файлах у поля разный тип?
4. Почему для больших файлов автор советует `COPY`?

Предыдущая: [Глава 5. EDA и геоанализ](/book-summaries/engineering/duckdb-up-and-running/05-eda-spatial/). Следующая: [Глава 7. JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/).
