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

**Главная мысль:** DuckDB читает файлы по ссылке, без ручной загрузки. Для CSV это скачивает файл целиком. Для Parquet DuckDB берёт только нужные куски: схему, метаданные и нужные колонки. Поэтому для удалённых данных выбирайте Parquet.

## О чём глава

В главах 1-7 данные лежали локально. На практике они чаще лежат на удалённых серверах, и источников несколько. Глава учит читать удалённые CSV и Parquet, датасеты Hugging Face и закрытые датасеты с токеном. Предыдущая глава: [JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/).

![DuckDB читает через расширение httpfs файлы по URL, из объектного хранилища и с Hugging Face](/assets/duckdb-up-and-running/ch08-remote-sources.png)

## Расширение httpfs

`httpfs` — это расширение, которое добавляет DuckDB файловую систему поверх HTTP и HTTPS. DuckDB читает и пишет удалённые файлы напрямую, не скачивая их заранее. Это полезно, когда данные больше диска, часто обновляются, лежат в нескольких местах или в облачном озере данных (`data lake`). Расширение работает с CSV, Parquet и другими форматами, а также с объектным хранилищем через S3 API и glob-масками. Подключают его командами `INSTALL httpfs; LOAD httpfs;`, один раз за сессию.

## CSV по ссылке

Вместо имени файла в `FROM` ставят URL. С GitHub нужен адрес «raw»: откройте файл и нажмите кнопку Raw. Автор берёт CSV с ценами акций Amazon. Фильтры работают как обычно: `WHERE year(Date) = 2018`. Несколько файлов читают через `read_csv([url1, url2])`. Если схемы разные, строки не склеятся.

CSV хранится по строкам, поэтому DuckDB обычно скачивает его целиком. Для больших файлов это долго. Автор советует Parquet (см. [главу 2](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/)).

## Parquet по ссылке

Для Parquet DuckDB берёт метаданные файла и шлёт HTTP range requests: запросы не всего файла, а его части. Автор показывает это на Parquet с данными о страховках путешественников. `SELECT *` скачивает весь файл. Лучше сначала выполнить `DESCRIBE`: схема приходит почти без загрузки. Потом выбирают нужные столбцы. `SELECT Agency, "Agency Type"` читает два столбца, `avg(age)` один. `count(*)` ничего не качает: число строк лежит в метаданных.

![CSV по сети скачивается целиком, Parquet отдаёт метаданные и нужные столбцы: наш замер в мегабайтах](/assets/duckdb-up-and-running/ch08-remote-bytes.png)

Мы проверили это замером: файл с 1 млн строк лежал на локальном HTTP-сервере, который считает отданные байты. Код: `scripts/duckdb-code/ch08_range_demo.py`. Каждый запрос шёл в новом соединении, чтобы кеш не скрыл загрузку.

```text
Размер файлов: CSV 58.7 МБ, Parquet 23.8 МБ (1 000 000 строк, 6 столбцов)

Запрос                             скачано, МБ  доля файла
CSV     SELECT count(*)                  90.74       154%
Parquet SELECT *                         23.70       100%
Parquet DESCRIBE                          0.03         0%
Parquet SELECT count(*)                   0.03         0%
Parquet SELECT avg(age)                   0.07         0%
Parquet SELECT agency, age                0.09         0%
```

Для CSV скачано больше размера файла: DuckDB читает его и для определения типов, и для самого запроса. Parquet при `count(*)`, `avg(age)` и двух столбцах берёт доли мегабайта.

> **Пояснение:** это наш замер на локальном сервере, не пример автора.

## Hugging Face Datasets

Hugging Face — открытое сообщество вокруг машинного обучения. Там лежат готовые модели и большая коллекция датасетов. DuckDB читает их файлы по пути `hf://`.

Автор собирает путь на датасете Tips из `scikit-learn`. На странице датасета видны имя пользователя и имя датасета. Вкладка Files показывает файлы. Путь: `hf://datasets/scikit-learn/tips/tips.csv`.

![Из чего состоит путь hf://: пользователь, датасет, папка и файл](/assets/duckdb-up-and-running/ch08-hf-path.png)

Автор советует сохранить данные в таблицу: `CREATE TABLE Tips AS FROM 'hf://...'`. Тогда следующие запросы не ходят в сеть.

Если файлы лежат в папке, её добавляют в путь. В датасете Adult Census Income это папка `data`: `hf://datasets/AiresPucrs/adult-census-income/data/train-00000-of-00001-7e70ed54d8cbb057.parquet`.

## Много файлов: glob-маски

Маски те же, что в главе 6: `*` (любое число символов), `**` (любое число подпапок), `?` (один символ), `[abc]` (символ из списка), `[a-z]` (символ из диапазона).

Датасет `gabrielwu/city_country` состоит из `geo_test.csv` и `geo_train.csv`. Маска `*.csv` читает оба. Автор предупреждает: у всех файлов должна быть одна схема, иначе будет исключение. Фильтры работают как на одном файле.

Лучше всего маски работают с Parquet. В датасете `Stanford/web_questions` два Parquet-файла. Запрос читает только столбец `question` из обоих и ищет слово «happened». Целиком файлы качать не нужно.

## Закрытые датасеты

Для закрытого (private) датасета нужны учётные данные. Автор создаёт аккаунт на huggingface.co, делает датасет с признаком Private и грузит в него CSV. Затем в Settings → Access Tokens создаёт токен типа Read: для чтения он достаточен. Токен показывают один раз. Если потеряли, его отзывают и выпускают новый.

DuckDB поддерживает два способа передать токен.

![Два способа дать DuckDB токен Hugging Face: в команде CONFIG и из файла CREDENTIAL_CHAIN](/assets/duckdb-up-and-running/ch08-auth.png)

**`CONFIG`.** Вы сами задаёте токен в команде `CREATE SECRET hf_token (TYPE HUGGINGFACE, TOKEN '...')`. Подходит, если токены часто меняют. Минус: токен виден в коде.

**`CREDENTIAL_CHAIN`.** DuckDB сам ищет токен в стандартных местах (папка, переменная окружения, файл) и останавливается на первом найденном. Автор считает способ намного безопаснее. Порядок: `pip install huggingface_hub`, потом `huggingface-cli login`. Токен ложится в `~/.cache/huggingface/token`. Затем `CREATE SECRET hf_token (TYPE HUGGINGFACE, PROVIDER CREDENTIAL_CHAIN)`. Если токен недействителен, удалите файл. Если сменился, обновите файл.

После создания секрета закрытый файл читается так же, как публичный: `SELECT * FROM 'hf://datasets/<user>/<dataset>/<file>'`.

## Что мы запустили по сети

Мы проверили примеры автора на GitHub и Hugging Face в DuckDB 1.4.3. Код: `scripts/duckdb-code/ch08_remote_real.py`. Нужен интернет.

```text
CSV с GitHub: строк всего, строк за 2018 год: (5665, 251)
Parquet с GitHub: число столбцов: 11
Parquet с GitHub: строк, средний возраст: (63326, 39.97)
Hugging Face, tips.csv: первая строка: (16.99, 1.01, 'Female', 'Sun')
Hugging Face, Parquet в папке data/: строк: 32561
Hugging Face, glob по двум CSV: строк: 2479
Hugging Face, glob по Parquet, question LIKE '%happened%': строк: 35
Локальная таблица tips (следующие запросы не ходят в сеть): строк: 244
Секрет создан (токен фальшивый): ('hf_token', 'huggingface', 'config')
```

Закрытый датасет и `CREDENTIAL_CHAIN` мы не запускали: нужен личный токен. Мы создали только секрет с фальшивым токеном.

## Итоги главы

- Расширение `httpfs` читает и пишет файлы по HTTP, HTTPS и S3 API без ручной загрузки.
- Удалённый CSV обычно скачивается целиком, потому что хранится по строкам.
- Для Parquet DuckDB использует метаданные и range requests. Скачиваются только нужные столбцы.
- Путь `hf://datasets/<пользователь>/<датасет>/<файл>` открывает файлы Hugging Face, в том числе из папок.
- Glob-маски читают много файлов сразу. Схемы должны совпадать.
- Для закрытых датасетов нужен токен. Способ `CREDENTIAL_CHAIN` безопаснее `CONFIG`, потому что токена нет в коде.

## Ключевые термины

| Термин | Значение |
|---|---|
| `httpfs` | Расширение для чтения и записи файлов по HTTP(S) и S3 |
| Range request | HTTP-запрос части файла |
| `hf://` | Путь к файлам на Hugging Face |
| Glob | Маска имён файлов с `*` и `?` |
| `CREATE SECRET` | Команда для хранения доступа (токена, ключа) |
| `CREDENTIAL_CHAIN` | Автопоиск доступа в известных местах |

## Что это значит на практике

- Parquet по HTTP и S3 — основа «лёгкого» озера данных. DuckDB читает его без загрузки в базу.
- Смотрите схему до запроса. Затем выбирайте только нужные столбцы.
- Для повторных запросов делайте локальную таблицу или копию Parquet.
- Не пишите токены в код и не коммитьте их. Используйте `CREDENTIAL_CHAIN`, переменные окружения или секреты CI.
- Тесты пайплайна могут читать эталонные файлы по ссылке.
- Не рассчитывайте на публичную ссылку в продакшене: файл могут удалить или заменить. Копируйте нужные данные к себе.
- Для CSV по сети сначала переведите файл в Parquet, если читаете его много раз.

## Практика в DuckDB

Запустите `duckdb` в терминале. Блоки идут по порядку. Сеть не нужна: мы читаем локальные файлы теми же функциями, что работают с URL.

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

### Шаг 2. Схема, метаданные и glob

```sql
DESCRIBE SELECT * FROM '/tmp/duck_ch8_sales_part1.parquet';

-- число строк берётся из метаданных. Колонки не читаются
SELECT file_name, num_rows, num_row_groups
FROM parquet_file_metadata('/tmp/duck_ch8_sales_part1.parquet');

-- какой файл дал какие строки
SELECT filename, count(*) AS n
FROM read_parquet('/tmp/duck_ch8_sales_part*.parquet', filename = true)
GROUP BY filename
ORDER BY filename;
```

Проверка: в последнем запросе должно быть две строки по 1000.

### Задания

**1.** Посчитайте сумму `net_sales` по `agency`. Читайте только две колонки.

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

**2.** Добавьте файл с другими колонками. Прочитайте все файлы одной маской.

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

По сети те же запросы выглядят так:

```text
INSTALL httpfs;
LOAD httpfs;
SELECT agency, avg(age) FROM 'https://example.com/data/sales.parquet' GROUP BY agency;
SELECT * FROM 'hf://datasets/<user>/<dataset>/data/<file>.parquet' LIMIT 10;
```

Адрес `example.com` условный, этот блок не запускали.

## Вопросы для самопроверки

1. Почему Parquet удобнее CSV для чтения по сети?
2. Какие запросы к удалённому Parquet почти ничего не скачивают и почему?
3. Как собрать путь `hf://` к файлу датасета в папке?
4. Чем `CREDENTIAL_CHAIN` лучше, чем `CONFIG` для токена Hugging Face?
5. Что случится, если читать маской файлы с разными схемами? Как это исправить?

Предыдущая: [Глава 7. JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/). Следующая: [Глава 9. MotherDuck](/book-summaries/engineering/duckdb-up-and-running/09-motherduck/).
