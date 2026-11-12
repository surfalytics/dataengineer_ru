---
title: "DuckDB: Up and Running, глава 3: Основы SQL"
head:
  - tag: title
    content: "DuckDB CLI и основы SQL: JOIN, агрегаты, view | Инжиниринг Данных"
description: "Конспект главы 3 DuckDB: Up and Running на русском. Консоль duckdb, dot-команды, EXPORT DATABASE, CREATE TABLE, JOIN, агрегаты, view и вложенные запросы."
sidebar:
  order: 3
  label: "3. Основы SQL"
tags:
  - books
  - duckdb
  - sql
---

**Главная мысль:** для DuckDB не нужен Python. Консоль `duckdb` и обычный SQL закрывают почти всё: создать базу, загрузить файл, сделать запрос, сохранить результат.

## Консоль DuckDB (CLI)

| Действие | Как |
|---|---|
| Поставить на macOS | `brew install duckdb` |
| Поставить на Windows | `winget install DuckDB.cli` |
| База в памяти | `duckdb` |
| База в файле | `duckdb mydb.duckdb` |
| Выйти | `.quit` или `Ctrl+D` |
| Справка по ключам | `duckdb -help` |

- Запрос SQL заканчивается точкой с запятой. Без неё консоль ждёт продолжения.
- Файл CSV можно сразу превратить в таблицу: `CREATE TABLE t AS FROM 'file.csv';`.

## Dot-команды

Это команды консоли, не SQL. Точка с запятой не нужна.

| Команда | Что делает |
|---|---|
| `.help` | Список команд |
| `.databases` | Какие базы подключены |
| `.open file.duckdb` | Закрыть текущую базу и открыть другую |
| `.tables` | Все таблицы |
| `.schema` | `CREATE`-операторы всей базы |
| `.dump t` | Вывести таблицу как SQL-скрипт |
| `.read file.sql` | Выполнить SQL из файла |
| `.timer on` | Показывать время запроса |
| `.mode`, `.output` | Формат и направление вывода |

Чтобы работать с двумя базами сразу, используйте SQL: `ATTACH 'mydb.duckdb' AS mydb;`. Затем `USE mydb;` выбирает активную.

## Сохранить базу из памяти

Команда `EXPORT DATABASE 'dir'` создаёт папку. В ней три вида файлов:

| Файл | Содержимое |
|---|---|
| `schema.sql` | `CREATE TABLE` для всех таблиц |
| `load.sql` | `COPY ... FROM` для загрузки данных |
| `<table>.csv` | Данные каждой таблицы |

Восстановить: `IMPORT DATABASE 'dir'` в пустой базе. Это переносимый формат. Подходит для резервной копии и миграции.

## Основы SQL на примере

Автор строит базу мини-библиотеки: авторы, книги, читатели, выдачи. Мы покажем те же приёмы на своей схеме магазина: клиенты, товары, заказы.

### Создание таблиц

- `CREATE TABLE` с типами и ограничениями: `PRIMARY KEY`, `NOT NULL`.
- `FOREIGN KEY ... REFERENCES` задаёт связь между таблицами. Нельзя вставить строку с несуществующим ключом.
- Нельзя удалить таблицу, на которую ссылается другая. DuckDB вернёт `Catalog Error`.
- Посмотреть схему: `DESCRIBE t`, `SHOW t`.
- Удалить: `DROP TABLE t`.

### Изменение данных

| Задача | Оператор |
|---|---|
| Вставить строки | `INSERT INTO t (cols) VALUES (...), (...)` |
| Изменить | `UPDATE t SET col = v WHERE ...` |
| Удалить | `DELETE FROM t WHERE ...` |

Всегда пишите `WHERE` в `UPDATE` и `DELETE`. Без него изменятся все строки. Для больших объёмов `INSERT` по одной строке медленный. Используйте `COPY` или `INSERT ... SELECT`.

### Фильтры

- Условия: `=`, `>`, `>=`, `LIKE '%текст%'`.
- Дату можно писать строкой `'2022-01-01'`. DuckDB сам приведёт её к `DATE`.
- Функции дат: `current_date`, `year(...)`, `date_diff('day', a, b)`.

### JOIN

| Тип | Что вернёт |
|---|---|
| `INNER JOIN` | Только совпавшие строки |
| `LEFT JOIN` | Все строки слева. Справа `NULL`, если пары нет |
| `RIGHT JOIN` | Все строки справа |
| `FULL JOIN` | Все строки из обеих таблиц |
| `CROSS JOIN` | Все пары строк |

Порядок таблиц важен для `LEFT` и `RIGHT`. Несколько `JOIN` подряд соединяют цепочку: выдачи → книги → авторы.

### Агрегаты

- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` с `GROUP BY`.
- `ORDER BY ... DESC LIMIT 1` — самая частая запись.
- Без `ORDER BY` порядок строк не гарантирован.

### View и вложенные запросы

- `CREATE VIEW v AS SELECT ...` сохраняет запрос как виртуальную таблицу. Данные не копируются.
- Вложенный `SELECT` в `WHERE ... IN (...)` ищет, например, самые частые значения. Автор показывает запрос с тремя уровнями вложенности.
- Тот же результат часто проще получить через `CTE` (`WITH`) или оконную функцию.

Один пример автора считает возраст через `year(current_date)`. Результат зависит от дня запуска. Для воспроизводимых запросов подставляйте дату явно.

## Ключевые термины

| Термин | Значение |
|---|---|
| `CLI` | Консоль `duckdb` |
| Dot command | Команда консоли, начинается с точки |
| `ATTACH` / `USE` | Подключить базу / сделать её активной |
| `EXPORT DATABASE` | Выгрузить базу в папку с SQL и CSV |
| `FOREIGN KEY` | Ссылка на ключ другой таблицы |
| `View` | Сохранённый запрос |
| `Subquery` | Запрос внутри запроса |

## Что это значит на практике

- Знайте `.read`, `.timer on` и `.mode`. Они экономят много времени при отладке.
- Скрипты `.sql` и `duckdb -c "..."` удобно запускать в `Makefile` и CI.
- Не рассчитывайте на `FOREIGN KEY` как защиту данных в хранилище. Проверяйте связи тестами `relationships` в `dbt`.
- Фиксируйте даты в тестовых запросах. Иначе результат меняется каждый день.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём схему магазина

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        VARCHAR NOT NULL,
    city        VARCHAR,
    joined      DATE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    title      VARCHAR NOT NULL,
    category   VARCHAR,
    price      DECIMAL(10, 2)
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    ordered_at  DATE,
    shipped_at  DATE,
    status      VARCHAR,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

INSERT INTO customers VALUES
    (1, 'Алина',  'Москва', DATE '2023-01-10'),
    (2, 'Игорь',  'Казань', DATE '2023-03-05'),
    (3, 'Мария',  'Москва', DATE '2023-06-20'),
    (4, 'Павел',  'Тверь',  DATE '2024-02-01');

INSERT INTO products VALUES
    (1, 'Ноутбук',  'Техника', 900.00),
    (2, 'Мышь',     'Техника',  20.00),
    (3, 'Книга SQL','Книги',    35.00),
    (4, 'Лампа',    'Дом',      40.00);

INSERT INTO orders VALUES
    (1, 1, 1, DATE '2024-03-01', DATE '2024-03-03', 'shipped'),
    (2, 1, 2, DATE '2024-03-01', DATE '2024-03-20', 'shipped'),
    (3, 2, 3, DATE '2024-03-05', NULL,              'open'),
    (4, 3, 3, DATE '2024-03-07', DATE '2024-03-08', 'shipped'),
    (5, 3, 1, DATE '2024-03-10', NULL,              'open'),
    (6, 1, 3, DATE '2024-03-15', DATE '2024-03-16', 'shipped');
```

### Шаг 2. Проверяем

```sql
DESCRIBE orders;

SELECT
    (SELECT count(*) FROM customers) AS customers,
    (SELECT count(*) FROM products)  AS products,
    (SELECT count(*) FROM orders)    AS orders;
```

Ожидаемо: 4, 4, 6.

### Задания

**1.** Покажите всех клиентов и число их заказов. Клиент без заказов должен быть в списке с нулём.

<details>
<summary>Решение</summary>

```sql
SELECT c.name, count(o.order_id) AS orders_cnt
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.name
ORDER BY orders_cnt DESC, c.name;
```

Алина — 3, Мария — 2, Игорь — 1, Павел — 0. `count(o.order_id)` не считает `NULL`, поэтому у Павла ноль.

</details>

**2.** Создайте view `late_orders`: отгруженные заказы, где от заказа до отгрузки прошло больше 14 дней. Покажите клиента, товар и число дней сверх 14.

<details>
<summary>Решение</summary>

```sql
CREATE VIEW late_orders AS
SELECT c.name AS customer, p.title AS product,
       date_diff('day', o.ordered_at, o.shipped_at) - 14 AS days_over
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN products  p ON p.product_id  = o.product_id
WHERE o.shipped_at IS NOT NULL
  AND date_diff('day', o.ordered_at, o.shipped_at) > 14;

SELECT * FROM late_orders;
```

Одна строка: Алина, Мышь, 5 дней сверх нормы (19 дней в пути).

</details>

**3.** Найдите самый популярный товар. Выведите название и число заказов. Если товаров с максимумом несколько, покажите все.

<details>
<summary>Решение</summary>

```sql
SELECT p.title, count(*) AS orders_cnt
FROM orders o
JOIN products p ON p.product_id = o.product_id
GROUP BY p.title
HAVING count(*) = (
    SELECT max(cnt)
    FROM (SELECT count(*) AS cnt FROM orders GROUP BY product_id)
)
ORDER BY p.title;
```

«Книга SQL» — 3 заказа. Вложенный запрос находит максимум, `HAVING` оставляет товары с ним.

</details>

**4.** Выгрузите всю базу в папку и проверьте, какие файлы получились.

<details>
<summary>Решение</summary>

```sql
EXPORT DATABASE '/tmp/duck_ch3_shop';

SELECT count(*) AS files
FROM glob('/tmp/duck_ch3_shop/*');
```

Файлов 5: `schema.sql`, `load.sql` и три CSV. Чтобы восстановить базу, в пустой сессии выполните `IMPORT DATABASE '/tmp/duck_ch3_shop';`.

</details>

## Вопросы для самопроверки

1. Чем dot-команда отличается от SQL-запроса?
2. Что создаёт `EXPORT DATABASE`? Как восстановить базу?
3. Чем `LEFT JOIN` отличается от `INNER JOIN`? Когда нужен первый?
4. Почему запрос с `year(current_date)` даёт разный результат в разные дни?

Предыдущая: [Глава 2. Импорт данных](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/). Следующая: [Глава 4. DuckDB и Polars](/book-summaries/engineering/duckdb-up-and-running/04-polars/).
