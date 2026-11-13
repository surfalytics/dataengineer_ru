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

## О чём глава

Глава 2 учила загружать данные в DuckDB из Python. Теперь автор переходит к главному инструменту: SQL. Загрузку данных мы разбирали в [главе 2](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/). Автор учит SQL на примерах, а не по справочнику.

Темы: консоль `duckdb` и dot-команды, сохранение базы, основы SQL, пять видов `JOIN`, агрегаты, view и вложенные запросы.

![Консоль duckdb: база в памяти и в файле, смена и подключение баз, выгрузка в папку и загрузка обратно](/assets/duckdb-up-and-running/ch03-cli-map.png)

Слева два способа начать, справа перенос базы через папку.

## Консоль DuckDB (CLI)

Иногда проще работать с базой напрямую, без языка программирования. Для этого нужна консоль `duckdb`. Она собрана для Windows, macOS и Linux.

| Действие | Как |
|---|---|
| Поставить на macOS | `brew install duckdb` |
| Поставить на Windows | `winget install DuckDB.cli` |
| Синтаксис и ключи | `duckdb [OPTIONS] [FILENAME]`, справка: `duckdb -help` |
| База в памяти | `duckdb` |
| База в файле | `duckdb mydb.duckdb` |

Без имени файла консоль открывает базу в памяти. Всё в ней пропадает при выходе, это годится только для опытов. Для долгой работы берите файл.

### Загрузка данных в консоли

CSV загружают так: `CREATE TABLE airlines AS FROM 'airlines.csv';`. Запрос SQL заканчивается точкой с запятой, без неё консоль ждёт продолжения. Проверка: `SHOW TABLES;` и `SELECT * FROM airlines;`.

## Dot-команды

Это команды самой консоли, а не SQL. Точка с запятой не нужна. Полный список даёт `.help`.

| Команда | Что делает |
|---|---|
| `.databases` | Показывает текущую базу. Для базы в памяти пишет `memory:` |
| `.open file.duckdb` | Закрывает текущую базу и открывает другую. Если файла нет, он создаётся |
| `.tables` | Все таблицы |
| `.schema` | `CREATE`-операторы всей базы |
| `.dump t` | Выводит таблицу как SQL-скрипт. Подходит, чтобы перенести таблицу в другую СУБД, например в MySQL |
| `.read file.sql` | Выполняет SQL из файла |
| `.timer on` | Показывает время запроса |

Чтобы держать открытой текущую базу и работать со второй, используйте SQL: `ATTACH 'mydb.duckdb' AS mydb;` (имя файла в кавычках). Без псевдонима им станет имя файла. Затем `USE mydb;` выбирает активную базу.

## Сохранить базу из памяти

Чтобы сохранить базу из памяти, используйте `EXPORT DATABASE 'dir'`. Команда создаёт папку `dir` с тремя видами файлов:

| Файл | Содержимое |
|---|---|
| `schema.sql` | `CREATE TABLE` для всех таблиц |
| `load.sql` | `COPY ... FROM` для загрузки данных |
| `<table>.csv` | Данные каждой таблицы |

Чтобы восстановить базу, запустите консоль рядом с `dir` и выполните `IMPORT DATABASE 'dir'`. Подходит для резервной копии и миграции. Настоящий запуск, код: [`scripts/duckdb-code/ch03_export.py`](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch03_export.py):

```text
Файлы в папке shop_db: ['load.sql', 'products.csv', 'schema.sql']

schema.sql:
CREATE TABLE products(product_id INTEGER PRIMARY KEY, title VARCHAR, price DECIMAL(10,2));;

load.sql:
COPY products FROM 'shop_db/products.csv' (FORMAT 'csv', force_not_null 'product_id', quote '"', delimiter ',', header 1);

IMPORT DATABASE в новой базе:
product_id,title,price
1,"Мышь",20.00
2,"Лампа",40.00
```

## Основы SQL на примере

Автор строит базу мини-библиотеки из четырёх таблиц: авторы, книги, читатели, выдачи. DuckDB почти полностью следует стандарту SQL (особенно SQL:1999), поэтому разбор похож на любую другую базу. Мы покажем те же приёмы на своей схеме магазина: клиенты, товары, заказы.

![ER-схема магазина: таблицы customers и products связаны с orders через customer_id и product_id](/assets/duckdb-up-and-running/ch03-shop-er.png)

Таблица `orders` ссылается на две другие, как таблица выдач у автора.

### Создание базы и таблиц

Базу создаёт запуск `duckdb library.duckdb`. Таблицу создаёт `CREATE TABLE`: имя, столбцы с типами и ограничения.

- `PRIMARY KEY` делает столбец ключом. `NOT NULL` запрещает пустые значения.
- `FOREIGN KEY ... REFERENCES` связывает таблицы и защищает целостность. Нельзя вставить в `Books` строку с `author_id`, которого нет в `Authors`.
- Таблицу, на которую ссылаются другие, удалить нельзя: `Catalog Error`.
- Схему таблицы показывают `DESCRIBE t` и `SHOW t`. Таблицу удаляет `DROP TABLE t`.

### Изменение данных

| Задача | Оператор |
|---|---|
| Вставить строки | `INSERT INTO t (cols) VALUES (...), (...)`. |
| Изменить | `UPDATE t SET col = v WHERE ...` |
| Удалить | `DELETE FROM t WHERE ...` |

`UPDATE` автор показывает на выдаче 3: статус `Returned` и дата возврата. `DELETE` работает по имени, по ключу или по шаблону `LIKE '%Jane%'` (`%` заменяет любые символы).

> Всегда пишите `WHERE` в `UPDATE` и `DELETE`. Без него изменятся все строки.


### Фильтры

Условия: `=`, `>`, `>=`, `LIKE`. Даты сравнивают строкой `'2022-01-01'`: DuckDB сам приведёт её к `DATE`. Функции `CURRENT_DATE` и `YEAR(...)` дают, например, «авторы старше 100 лет».

## JOIN

`JOIN` соединяет таблицы по общим столбцам. DuckDB поддерживает пять видов.

![Пять видов JOIN на таблицах с ключами 1, 2, 3 и 2, 3, 4: что вернёт каждый](/assets/duckdb-up-and-running/ch03-joins.png)

| Тип | Что вернёт |
|---|---|
| `INNER JOIN` | Только строки, у которых есть пара в обеих таблицах |
| `LEFT JOIN` | Все строки левой таблицы. Справа `NULL`, если пары нет |
| `RIGHT JOIN` | Все строки правой таблицы. Слева `NULL`, если пары нет |
| `FULL JOIN` | Все строки обеих таблиц |
| `CROSS JOIN` | Все пары строк |

Порядок таблиц важен для `LEFT` и `RIGHT`. У автора `Books LEFT JOIN Authors` даёт пять строк. Если поменять таблицы местами, появляется шестая строка: автор Mark Twain без книг, у него `book_id` и `title` равны `NULL`. `RIGHT JOIN` и `FULL JOIN` тоже показывают Mark Twain, `INNER JOIN` скрывает. Тот же эффект на нашей схеме, код: [`scripts/duckdb-code/ch03_joins.py`](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch03_joins.py):

```text
INNER JOIN: только товары с заказами
   ('Книга SQL', 3)
   ('Мышь', 1)
   ('Ноутбук', 2)
LEFT JOIN: все товары, у лампы заказов 0
   ('Книга SQL', 3)
   ('Лампа', 0)
   ('Мышь', 1)
   ('Ноутбук', 2)
Таблицы в другом порядке: orders LEFT JOIN products (лампы нет)
   ('Книга SQL', 3)
   ('Мышь', 1)
   ('Ноутбук', 2)
```

### JOIN нескольких таблиц

Несколько `JOIN` подряд соединяют цепочку: выдачи, книги, читатели, авторы. Автор находит книги читателя John Smith, затем добавляет имена читателей и авторов. Без `ORDER BY` порядок строк не гарантирован.

## Агрегаты

Агрегат сворачивает много строк в одно значение: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. С `GROUP BY` их считают по группам.

- Сколько книг взял каждый читатель: `COUNT` с `GROUP BY` по имени.
- Самая популярная книга: считаем выдачи, сортируем `ORDER BY ... DESC` и берём `LIMIT 1`.
- Средний возраст авторов: `AVG(YEAR(CURRENT_DATE) - birth_year)`, у автора 162,5.
- Самый старый автор: `WHERE birth_year = (SELECT MIN(birth_year) FROM Authors)`. Это Jane Austen, ей «249 лет» (на 2024 год).

Запросы с `CURRENT_DATE` зависят от дня запуска: «249 лет» верно только для 2024 года.

## Аналитика: просрочки, view и вложенные запросы

### Просроченные книги и view

Срок выдачи автор принимает за 14 дней. Просрочку считает `DATEDIFF('day', borrow_date, return_date) - 14`. Так находятся поздние возвраты: John Smith на 1 день, William Taylor на 7.

`CREATE VIEW v AS SELECT ...` сохраняет запрос как виртуальную таблицу. Данные не копируются. View записывается в базу, и к нему обращаются как к таблице.

Для невозвращённых книг вместо даты возврата берут `CURRENT_DATE`. Просрочки вышли 710 дней и больше, ведь выдачи были в 2022 году. Автор повторяет запрос с датой `'2022-06-10'` и получает 31, 42 и 68 дней.

### Три уровня вложенных запросов

Задача: найти самую популярную книгу и показать, кто её брал. Автор пишет три вложенных `SELECT` и внешний запрос.

![Вложенный запрос: считаем заказы на товар, берём максимум, оставляем товары с максимумом, соединяем с таблицей товаров](/assets/duckdb-up-and-running/ch03-nested-query.png)

Читаем изнутри наружу. Результат: «Pride and Prejudice», две выдачи.

1. Самый внутренний `SELECT` считает выдачи каждой книги.
2. Средний берёт максимум из этих чисел.
3. Условие `IN` с `HAVING` оставляет книги, у которых счётчик равен максимуму. Так учтены книги с одинаковым рекордом.
4. Внешний запрос соединяет их с остальными таблицами и показывает детали.

> **Пояснение:** тот же ответ часто проще получить через `CTE` (`WITH`) или оконную функцию. Шаги в `WITH` читать легче, чем вложенные запросы.

## Итоги главы

- Консоль `duckdb` позволяет работать с базой без Python. База в памяти пропадает при выходе, для долгой работы открывайте файл `.duckdb`.
- Dot-команды относятся к консоли, а не к SQL: `.open`, `.tables`, `.schema`, `.dump`, `.read`.
- `EXPORT DATABASE` и `IMPORT DATABASE` переносят базу через папку с `schema.sql`, `load.sql` и CSV.
- `FOREIGN KEY` не даёт вставить несуществующий ключ. Всегда пишите `WHERE` в `UPDATE` и `DELETE`.
- Пять видов `JOIN` отличаются тем, какие строки без пары попадают в результат. Порядок таблиц важен для `LEFT` и `RIGHT`.
- `View` хранит запрос. Запросы с `CURRENT_DATE` нужно фиксировать для воспроизводимости.

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
- Добавляйте `ORDER BY` в тестовые запросы. Без него порядок строк не гарантирован.

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

## Вопросы для самопроверки

1. Чем dot-команда отличается от SQL-запроса?
2. Что создаёт `EXPORT DATABASE`? Как восстановить базу?
3. Чем `LEFT JOIN` отличается от `INNER JOIN`? Когда нужен первый?
4. Почему запрос с `year(current_date)` даёт разный результат в разные дни?

Предыдущая: [Глава 2. Импорт данных](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/). Следующая: [Глава 4. DuckDB и Polars](/book-summaries/engineering/duckdb-up-and-running/04-polars/).
