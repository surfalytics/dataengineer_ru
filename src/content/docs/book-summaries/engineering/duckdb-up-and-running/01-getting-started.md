---
title: "DuckDB: Up and Running, глава 1: Старт с DuckDB"
head:
  - tag: title
    content: "Что такое DuckDB и зачем он нужен | Инжиниринг Данных"
description: "Конспект главы 1 DuckDB: Up and Running на русском. Колоночное хранение, векторные вычисления, in-process база, запросы к CSV и DataFrame, скорость и память."
sidebar:
  order: 1
  label: "1. Старт с DuckDB"
tags:
  - books
  - duckdb
  - sql
---

**Главная мысль:** DuckDB — это аналитическая база данных, которая работает внутри вашего процесса. Не нужен сервер. Не нужно сначала загружать файл в базу. Вы пишете SQL и сразу читаете CSV, Parquet или DataFrame.

## Что такое DuckDB

- Это `in-process` база: она живёт внутри Python, R, Java, Node.js и других программ. Как библиотека.
- Она заточена под `OLAP`: агрегаты, `JOIN`, фильтры по большим таблицам.
- Она открытая и бесплатная. Работает на Windows, Linux и macOS.
- SQL почти стандартный. Есть `SELECT`, `INSERT`, `UPDATE`, `DELETE`.

Обычный путь без DuckDB: файл → загрузка в сервер БД → запрос → DataFrame. С DuckDB: файл → запрос SQL → результат. Лишний шаг пропадает.

## Почему DuckDB быстрый

| Приём | Что это значит |
|---|---|
| `Columnar storage` | Данные лежат по столбцам. Запрос читает только нужные столбцы |
| `Vectorized execution` | Строки обрабатываются пачками. CPU использует кеш лучше |
| `Parallel execution` | Запрос делится на части и идёт на всех ядрах |
| `Late materialization` | Полные строки собираются как можно позже |
| `Query planner` | Оптимизатор двигает фильтры ближе к данным (`predicate pushdown`) и меняет порядок `JOIN` |
| Экономия памяти | Данные обрабатываются кусками. Таблица не обязана помещаться в RAM |

## Быстрый старт

Книга показывает путь через Python и Jupyter. Шаги такие:

1. Поставить пакет: `pip install duckdb`.
2. Открыть соединение: `duckdb.connect('file.db')` — файл на диске. `duckdb.connect(':memory:')` — база в памяти.
3. Создать таблицу, вставить строки, выполнить запрос.
4. Забрать результат как pandas DataFrame методом `.df()`.

> База в памяти пропадает при закрытии сессии. Для данных, которые нужны потом, используйте файл.

Тот же набор операций делается в консоли `duckdb`. Он описан в практике ниже.

## DuckDB читает DataFrame по имени

Если в Python есть pandas DataFrame, его можно вызвать в SQL по имени переменной. Копировать данные в таблицу не нужно. Так делают `JOIN` и агрегаты прямо над DataFrame. Подробно эту тему развивает [глава 4](/book-summaries/engineering/duckdb-up-and-running/04-polars/) на примере Polars.

## Скорость и память: опыт автора

Автор берёт большой CSV с рейсами за 2015 год: около 600 МБ и 5,8 млн строк. Считает среднюю задержку по авиакомпаниям.

| Способ | Время | Память |
|---|---|---|
| pandas: загрузить CSV и посчитать | около 7,5 с | около 4,2 ГБ |
| DuckDB: `read_csv_auto` и `GROUP BY` | около 0,5 с | около 280 МБ |

Выводы автора:

- Для разового анализа файла DuckDB быстрее и легче.
- Если вы делаете много операций подряд и памяти хватает, DataFrame в памяти тоже работает.
- Цифры зависят от машины и версии. Не считайте их законом.

## Ключевые термины

| Термин | Значение |
|---|---|
| `In-process database` | База внутри вашей программы, без сервера |
| `OLAP` | Аналитические запросы: большие чтения и агрегаты |
| `Columnar storage` | Хранение по столбцам |
| `Vectorized execution` | Обработка пачками строк |
| `Late materialization` | Сборка полных строк в последний момент |
| `Predicate pushdown` | Фильтр применяется как можно ближе к источнику |
| `read_csv_auto` | Функция чтения CSV с автоопределением типов |

## Что это значит на практике

- Для локальной разработки пайплайна и `dbt` DuckDB заменяет тяжёлый сервер. Тесты идут быстро.
- Проверить файл от поставщика можно одним запросом, без загрузки в хранилище.
- DuckDB не заменяет сервер для многих одновременных пишущих пользователей. Он про аналитику на одной машине.
- Сравнение скорости делайте на своих данных. Цифры из книги — только пример.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём таблицы

```sql
CREATE TABLE staff (id INTEGER PRIMARY KEY, name VARCHAR, age INTEGER, team VARCHAR);

INSERT INTO staff VALUES
    (1, 'Анна',  31, 'Data'),
    (2, 'Борис', 36, 'Data'),
    (3, 'Вера',  27, 'BI'),
    (4, 'Глеб',  42, 'Platform');

CREATE TABLE orders (order_id INTEGER, staff_id INTEGER, amount DOUBLE);

INSERT INTO orders VALUES
    (1, 1, 100.0),
    (2, 2, 200.0),
    (3, 1, 150.0),
    (4, 3, 80.0);
```

### Шаг 2. Проверяем

```sql
SHOW TABLES;

SELECT team, count(*) AS people, round(avg(age), 1) AS avg_age
FROM staff
GROUP BY team
ORDER BY team;
```

Ожидаемо: три команды. В `Data` двое, средний возраст 33,5.

### Задания

**1.** Посчитайте сумму заказов для каждого сотрудника. Выведите имя и сумму.

<details>
<summary>Решение</summary>

```sql
SELECT s.name, sum(o.amount) AS total
FROM orders o
JOIN staff s ON s.id = o.staff_id
GROUP BY s.name
ORDER BY s.name;
```

Анна — 250, Борис — 200, Вера — 80. У Глеба заказов нет, `INNER JOIN` его не показывает.

</details>

**2.** Покажите всех сотрудников, даже без заказов. Для них сумма должна быть 0.

<details>
<summary>Решение</summary>

```sql
SELECT s.name, coalesce(sum(o.amount), 0) AS total
FROM staff s
LEFT JOIN orders o ON s.id = o.staff_id
GROUP BY s.name
ORDER BY s.name;
```

Теперь Глеб есть в результате, его сумма 0.

</details>

**3.** Сгенерируйте файл на 2 млн строк, запишите его в CSV и посчитайте среднее по группам без `CREATE TABLE`.

<details>
<summary>Решение</summary>

```sql
COPY (
    SELECT i AS id, 'A' || (i % 5) AS grp, (i % 100) * 1.5 AS val
    FROM range(2000000) t(i)
) TO '/tmp/duck_ch1_big.csv' (HEADER, DELIMITER ',');

SELECT grp, round(avg(val), 2) AS avg_val
FROM read_csv_auto('/tmp/duck_ch1_big.csv')
GROUP BY grp
ORDER BY grp;
```

Пять групп `A0`–`A4`. Среднее растёт от 71,25 до 77,25. Файл читается прямо в запросе, таблицу создавать не пришлось.

</details>

## Вопросы для самопроверки

1. Чем `in-process` база отличается от сервера БД?
2. Почему колоночное хранение ускоряет аналитические запросы?
3. Зачем нужен `vectorized execution`?
4. Когда DataFrame в памяти может быть лучше, чем запрос к файлу?

Предыдущая: [Обзор книги](/book-summaries/engineering/duckdb-up-and-running/). Следующая: [Глава 2. Импорт данных](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/).
