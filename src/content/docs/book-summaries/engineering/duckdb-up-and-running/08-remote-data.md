---
title: "DuckDB: Up and Running, глава 8: удалённые данные"
head:
  - tag: title
    content: "DuckDB httpfs и Hugging Face: читать файлы по URL | Инжиниринг Данных"
description: "Конспект главы 8 DuckDB: Up and Running на русском. Расширение httpfs, чтение CSV и Parquet по URL, hf:// пути Hugging Face, glob-маски, секреты и токены."
sidebar:
  order: 8
  label: "8. Удалённые данные"
tags:
  - books
  - duckdb
  - parquet
  - sql
---

**Главная мысль:** DuckDB читает файлы по ссылке, без ручной загрузки. Для CSV это скачивает файл целиком. Для Parquet DuckDB берёт только нужные колонки. Поэтому для удалённых данных выбирайте Parquet.

## Расширение httpfs

`httpfs` реализует файловую систему поверх HTTP и HTTPS. Его устанавливают один раз, потом оно подгружается автоматически.

```text
INSTALL httpfs;
LOAD httpfs;
```

- Работает с CSV, Parquet и другими форматами, которые знает DuckDB.
- Поддерживает объектное хранилище через S3 API и glob-маски.
- Подходит, когда данные больше диска, часто обновляются или лежат у нескольких источников.

> Блоки `text` в этой главе ходят в сеть или требуют аккаунта. Мы их не запускаем. Блоки `sql` в практике делают то же самое на локальных файлах.

## CSV по ссылке

- Для файла на GitHub нужен адрес «raw». На странице файла нажмите кнопку Raw и скопируйте URL.
- Ссылку вставляют вместо имени файла: `SELECT * FROM 'https://.../file.csv'`.
- Фильтр работает как обычно: `WHERE year(Date) = 2018`.
- Несколько файлов: `read_csv([url1, url2])`. Схемы файлов должны совпадать.
- CSV хранится построчно. Обычно DuckDB скачивает его целиком. Для больших файлов это медленно.

## Parquet по ссылке

Parquet хранит данные по колонкам и держит метаданные. DuckDB использует их и HTTP range requests. Это запросы части файла.

| Запрос | Что скачивается |
|---|---|
| `SELECT *` | Весь файл |
| `DESCRIBE` | Только схема |
| `SELECT col_a, col_b` | Только эти две колонки |
| `SELECT avg(age)` | Только колонка `age` |
| `SELECT count(*)` | Почти ничего. Число строк лежит в метаданных |

Правило: сначала `DESCRIBE`, потом выбирайте колонки. Не пишите `SELECT *` по удалённому файлу.

## Hugging Face Datasets

Hugging Face — площадка с моделями и датасетами для машинного обучения. DuckDB читает её файлы по пути `hf://`.

```text
hf://datasets/<пользователь>/<датасет>/<файл>
hf://datasets/<пользователь>/<датасет>/data/<файл>.parquet
```

- Имя пользователя и датасета видно на странице датасета. Имена файлов — на вкладке Files.
- Если файлы лежат в папке, добавьте её в путь (например `data/`).
- Сохраните данные в таблицу: `CREATE TABLE tips AS SELECT * FROM 'hf://...'`. Тогда следующие запросы не идут в сеть.

## Glob: много файлов одним запросом

| Маска | Значение |
|---|---|
| `*` | Любое число любых символов |
| `**` | Любое число подпапок |
| `?` | Один любой символ |
| `[abc]` | Один символ из списка |
| `[a-z]` | Один символ из диапазона |

- Пример: `hf://datasets/<user>/<dataset>/*.csv` читает все CSV датасета.
- Схема у всех файлов должна быть одной. Иначе будет ошибка. Параметр `union_by_name = true` объединяет колонки по имени.
- Лучше всего маски работают с Parquet. Можно взять одну колонку из нескольких файлов и скачать только её.

## Приватные датасеты

Для приватных данных нужен токен доступа. Его создают в настройках Hugging Face. Для чтения хватает типа Read. Токен показывают один раз.

| Способ | Как | Оценка |
|---|---|---|
| `CONFIG` | `CREATE SECRET hf_token (TYPE HUGGINGFACE, TOKEN '...')` | Токен виден в коде |
| `CREDENTIAL_CHAIN` | `CREATE SECRET hf_token (TYPE HUGGINGFACE, PROVIDER CREDENTIAL_CHAIN)`. Токен берётся из файла, куда его сохранил `huggingface-cli login` | Безопаснее: токена нет в коде |

После создания секрета приватный файл читается так же, как публичный.

## Ключевые термины

| Термин | Значение |
|---|---|
| `httpfs` | Расширение для чтения и записи файлов по HTTP(S) и S3 |
| Raw URL | Прямая ссылка на содержимое файла |
| Range request | HTTP-запрос части файла |
| `hf://` | Путь к файлам на Hugging Face |
| Glob | Маска имён файлов с `*` и `?` |
| `CREATE SECRET` | Команда для хранения доступа (токена, ключа) |
| Credential chain | Автопоиск доступа в известных местах |

## Что это значит на практике

- Parquet по HTTP и S3 — основа «лёгкого» озера данных. DuckDB читает его без загрузки в базу.
- Смотрите схему до запроса. Затем выбирайте только нужные колонки.
- Для повторных запросов делайте локальную таблицу или копию Parquet.
- Не пишите токены в код и не коммитьте их. Используйте `CREDENTIAL_CHAIN`, переменные окружения или секреты CI.
- Тесты пайплайна могут читать эталонные файлы по ссылке.

## Практика в DuckDB

Запустите `duckdb` в терминале. Блоки идут по порядку. Файлы создаются в папке `/tmp`. Сеть не нужна: мы читаем локальные файлы теми же функциями, что работают с URL.

### Шаг 1. Создаём два Parquet-файла

```sql
COPY (
    SELECT i AS id, 'A' AS agency, 20 + i % 40 AS age, round(10 + i * 1.5, 2) AS net_sales
    FROM range(1, 1001) t(i)
) TO '/tmp/duck_ch8_sales_part1.parquet' (FORMAT PARQUET);

COPY (
    SELECT i AS id, 'B' AS agency, 20 + i % 40 AS age, round(10 + i * 1.5, 2) AS net_sales
    FROM range(1001, 2001) t(i)
) TO '/tmp/duck_ch8_sales_part2.parquet' (FORMAT PARQUET);
```

### Шаг 2. Схема и метаданные

```sql
DESCRIBE SELECT * FROM '/tmp/duck_ch8_sales_part1.parquet';

-- число строк берётся из метаданных. Колонки не читаются
SELECT count(*) AS n FROM '/tmp/duck_ch8_sales_part1.parquet';

-- метаданные файла: строки и колонки
SELECT file_name, num_rows, num_row_groups
FROM parquet_file_metadata('/tmp/duck_ch8_sales_part1.parquet');
```

### Шаг 3. Только нужные колонки и glob

```sql
-- две колонки из двух файлов по маске
SELECT agency, avg(age) AS avg_age, count(*) AS n
FROM '/tmp/duck_ch8_sales_part*.parquet'
GROUP BY agency
ORDER BY agency;

-- какой файл дал какие строки
SELECT filename, count(*) AS n
FROM read_parquet('/tmp/duck_ch8_sales_part*.parquet', filename = true)
GROUP BY filename
ORDER BY filename;
```

Проверка: во втором запросе должно быть две строки по 1000.

### Задания

**1.** Покажите, сколько строк всего в обоих файлах, не читая колонки с данными.

<details>
<summary>Решение</summary>

```sql
SELECT sum(num_rows) AS total_rows
FROM parquet_file_metadata('/tmp/duck_ch8_sales_part*.parquet');
```

2000 строк. Число берётся из метаданных, данные не читаются.

</details>

**2.** Посчитайте сумму `net_sales` по `agency`. Читайте только две колонки.

<details>
<summary>Решение</summary>

```sql
SELECT agency, sum(net_sales) AS total_sales
FROM '/tmp/duck_ch8_sales_part*.parquet'
GROUP BY agency
ORDER BY agency;
```

A — 760 750, B — 2 260 750. Запрос читает только `agency` и `net_sales`.

</details>

**3.** Прочитайте два файла списком через `read_parquet([...])` и найдите максимальный `id`.

<details>
<summary>Решение</summary>

```sql
SELECT max(id) AS max_id
FROM read_parquet(['/tmp/duck_ch8_sales_part1.parquet', '/tmp/duck_ch8_sales_part2.parquet']);
```

Максимальный `id` равен 2000. Он из второго файла.

</details>

**4.** Добавьте файл с другими колонками. Прочитайте все файлы одной маской.

<details>
<summary>Решение</summary>

```sql
COPY (SELECT 1 AS id, 'x' AS other_col) TO '/tmp/duck_ch8_extra.parquet' (FORMAT PARQUET);

SELECT count(*) AS n, count(other_col) AS with_other_col
FROM read_parquet('/tmp/duck_ch8_*.parquet', union_by_name = true);
```

2001 строка, `other_col` заполнен в одной. Без `union_by_name` DuckDB вернёт ошибку `schema mismatch`. С `union_by_name = true` колонки объединяются по имени, а пропуски равны `NULL`.

</details>

Удалить созданные файлы: `rm /tmp/duck_ch8_*.parquet`.

Те же запросы по сети выглядят так. Без доступа к сети их не запускайте:

```text
INSTALL httpfs;
LOAD httpfs;
SELECT agency, avg(age) FROM 'https://example.com/data/sales.parquet' GROUP BY agency;
SELECT * FROM 'hf://datasets/<user>/<dataset>/data/<file>.parquet' LIMIT 10;
```

## Вопросы для самопроверки

1. Почему Parquet удобнее CSV для чтения по сети?
2. Какие запросы к удалённому Parquet почти ничего не скачивают?
3. Как собрать путь `hf://` к файлу датасета?
4. Чем `CREDENTIAL_CHAIN` лучше, чем `CONFIG` для токена Hugging Face?

Предыдущая: [Глава 7. JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/). Следующая: [Глава 9. MotherDuck](/book-summaries/engineering/duckdb-up-and-running/09-motherduck/).
