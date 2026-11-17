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

**Главная мысль:** для DuckDB не нужен Python. Консоли `duckdb` и обычного SQL хватает почти для всего: создать базу, загрузить файл, сделать запрос, сохранить результат.

## О чём глава

В [главе 2](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/) данные попадали в DuckDB через Python. Теперь автор переходит к главному инструменту DuckDB: SQL. Делает он это в два шага. Сначала показывает консоль `duckdb`, с которой можно работать без языка программирования. А потом учит SQL на примерах, а не по справочнику.

Темы главы:

- консоль `duckdb` и dot-команды;
- сохранение базы из памяти на диск;
- создание таблиц, вставка, изменение и удаление строк;
- пять видов `JOIN`;
- агрегаты, `view` и вложенные запросы.

![Консоль duckdb: база в памяти и в файле, смена и подключение баз, выгрузка в папку и загрузка обратно](/assets/duckdb-up-and-running/ch03-cli-map.png)

Слева два способа начать работу и два способа сменить базу, а справа — перенос базы через папку.

## Консоль DuckDB (CLI)

Консоль нужна там, где язык программирования только мешает: создать таблицы, загрузить файлы, сделать административную работу. Автор считает, что здесь она эффективнее Python. К тому же консоль собрана заранее для Windows, macOS и Linux, поэтому ставить её просто.

| Действие | Как |
|---|---|
| Поставить на macOS | `brew install duckdb` |
| Поставить на Windows | `winget install DuckDB.cli` |
| Синтаксис и ключи | `duckdb [OPTIONS] [FILENAME]`, справка: `duckdb -help` |
| База в памяти | `duckdb` |
| База в файле | `duckdb mydb.duckdb` |

`brew` — это пакетный менеджер для macOS и Linux. Права администратора для установки через него не нужны.

Справка `-help` показывает много ключей, и их можно разделить на две группы. Одни задают формат вывода: `-csv`, `-json`, `-markdown`, `-table`, `-box`. Другие управляют запуском: `-c "команда"` выполняет команду и выходит, `-init файл` читает команды из файла, `-readonly` открывает базу только для чтения, `-bail` останавливается после первой ошибки.

Без имени файла консоль открывает `in-memory` базу. В приветствии стоит слово transient (временная), а приглашение выглядит как `D`. Всё в такой базе пропадает при выходе, поэтому она годится только для опытов. Выйти можно двойным `Ctrl+C` на macOS и Linux или одним на Windows.

Для настоящей работы нужна файловая база (`persistent`). Её данные остаются между сессиями, и их не надо каждый раз загружать заново. А если файла нет, консоль создаёт его в папке запуска.

### Загрузка данных в консоли

Глава 2 разобрала все способы загрузки. Здесь автор берёт самый короткий: `CREATE TABLE airlines AS FROM 'airlines.csv';`. DuckDB сам определит имена и типы столбцов. При этом SQL-запрос должен заканчиваться точкой с запятой: без неё консоль просто ждёт продолжения и ничего не выполняет.

Проверить результат можно двумя запросами: `SHOW TABLES;` покажет список таблиц, а `SELECT * FROM airlines;` покажет строки. В примере автора это 14 авиакомпаний с двумя столбцами, `IATA_CODE` и `AIRLINE`.

## Dot-команды

Dot-команда управляет самой консолью, а не базой. Она начинается с точки и не требует точки с запятой. Полный список выводит `.help`, а ниже — самые нужные.

| Команда | Что делает |
|---|---|
| `.databases` | Показывает текущую базу и её псевдоним. Для базы в памяти пишет `memory:` |
| `.open file.duckdb` | Закрывает текущую базу и открывает другую. Если файла нет, он создаётся |
| `.tables` | Все таблицы |
| `.schema` | `CREATE`-операторы всей базы |
| `.dump t` | Выводит таблицу как SQL-скрипт |
| `.read file.sql` | Выполняет SQL из файла |
| `.timer on` | Показывает время запроса |

Пример для `.open`: вы запустили консоль без файла, а потом решили работать с файловой базой. Команда `.open mydb2.duckdb` переключает консоль на неё. Файл появится в папке запуска, если его там не было.

`.open` закрывает старую базу. Чтобы держать открытой и её, и вторую базу, используйте SQL: `ATTACH 'mydb.duckdb' AS mydb;`. Имя файла берут в кавычки, а если псевдоним не указать, им станет имя файла. Первой в `.databases` стоит активная база, и сменить её можно командой `USE mydb2;`.

`.dump airlines` превращает таблицу в набор `CREATE TABLE` и `INSERT`, обёрнутый в транзакцию (`BEGIN TRANSACTION` ... `COMMIT`). Этот скрипт можно запустить в другой СУБД, например в MySQL. Есть одно условие: таблица должна лежать в текущей базе, а если она в другой, сначала сделайте `USE`.

`.read commands.sql` читает файл с SQL и выполняет его команды одну за другой. Так удобно запускать готовые скрипты.

## Сохранить базу из памяти

Допустим, вы загрузили `airports.csv` в базу в памяти, и теперь ей надо жить дольше сессии. Для этого есть `EXPORT DATABASE 'dir'`: команда создаёт папку `dir` с тремя видами файлов.

| Файл | Содержимое |
|---|---|
| `schema.sql` | `CREATE TABLE` для всех таблиц |
| `load.sql` | `COPY ... FROM` для загрузки данных |
| `<table>.csv` | Данные каждой таблицы |

Чтобы восстановить базу, запустите консоль в папке, где лежит `dir`, например `duckdb mydb3.duckdb`, и выполните `IMPORT DATABASE 'dir'`. Так делают резервную копию и переносят базу на другой компьютер. Ниже вывод нашего скрипта на маленькой базе магазина, код: [`scripts/duckdb-code/ch03_export.py`](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch03_export.py):

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

Дальше автор учит SQL на базе мини-библиотеки. В ней четыре таблицы:

- `Authors`: имя автора, национальность, год рождения;
- `Books`: название, автор, жанр, год издания;
- `Borrowers`: читатели с почтой и датой вступления;
- `Borrowings`: кто, когда и какую книгу взял, когда вернул и в каком статусе выдача.

Автор отмечает, что DuckDB почти полностью следует стандарту SQL, особенно SQL:1999. Поэтому SQL ниже почти такой же, как в других реляционных базах. А в нашем конспекте та же логика показана на схеме магазина: клиенты, товары, заказы. Таблица `orders` ссылается на две другие, как таблица выдач у автора.

![ER-схема магазина: таблицы customers и products связаны с orders через customer_id и product_id](/assets/duckdb-up-and-running/ch03-shop-er.png)

### Создание базы и таблиц

Базу создаёт запуск консоли с новым именем: `duckdb library.duckdb`. Таблицу создаёт `CREATE TABLE`: имя, список столбцов с типами и необязательные ограничения.

- `PRIMARY KEY` делает столбец ключом: значения не повторяются. `NOT NULL` запрещает пустые значения.
- `FOREIGN KEY ... REFERENCES` связывает таблицы и защищает целостность. Например, `author_id` в `Books` должен существовать в `Authors`, то есть вставить книгу с неизвестным автором нельзя.
- Таблицу, на которую ссылаются другие, удалить нельзя. DuckDB ответит `Catalog Error`.

### Схема и удаление таблиц

Схему таблицы показывают `DESCRIBE Authors` или `SHOW Authors`. Для всей базы есть `.schema`, но это уже dot-команда. Таблицу удаляет `DROP TABLE t`, и автор проверяет это на лишней таблице `OverdueBorrowers`. А вот попытка удалить `Authors` даёт ошибку, потому что на неё ссылается `Books`.

### Вставка строк

Все операции со строками автор называет `CRUD`: создать, прочитать, обновить, удалить. Начинается всё со вставки: `INSERT INTO t (cols) VALUES (...), (...)`. Одна команда может вставить сразу несколько строк, каждая в скобках. Автор наполняет четыре таблицы по порядку: сначала `Authors`, потом `Borrowers`, `Books` и `Borrowings`. Порядок важен: строка, на которую ссылается внешний ключ, должна уже быть в своей таблице. После каждой вставки он проверяет таблицу через `SELECT *`.

### Изменение и удаление

| Задача | Оператор |
|---|---|
| Изменить | `UPDATE t SET col = v WHERE ...` |
| Удалить | `DELETE FROM t WHERE ...` |

`UPDATE` автор показывает на выдаче 3: статус `Returned` и дата возврата. `DELETE` работает тремя способами: по имени, по ключу и по шаблону `LIKE '%Jane%'`. Знак `%` в шаблоне заменяет любые символы, так что шаблон находит «Jane» в любом месте строки.

> Всегда пишите `WHERE` в `UPDATE` и `DELETE`. Без него изменятся или удалятся все строки.

### Фильтры

Условия в `WHERE` строят из `=`, `>`, `>=` и `LIKE`. Даты можно сравнивать прямо со строкой `'2022-01-01'`: DuckDB сам приведёт её к `DATE`. Так автор находит читателей, вступивших не раньше 2022 года. Ещё один пример: «авторы старше 100 лет». Условие `YEAR(CURRENT_DATE) - birth_year > 100` берёт текущий год из `CURRENT_DATE` и вычитает год рождения.

## JOIN

Данные редко лежат в одной таблице, а `JOIN` соединяет таблицы по общим столбцам. DuckDB поддерживает пять видов.

![Пять видов JOIN на таблицах с ключами 1, 2, 3 и 2, 3, 4: что вернёт каждый](/assets/duckdb-up-and-running/ch03-joins.png)

Схема показывает одну и ту же пару таблиц: совпадают ключи 2 и 3, ключ 1 есть только слева, ключ 4 — только справа.

| Тип | Что вернёт |
|---|---|
| `INNER JOIN` | Только строки, у которых есть пара в обеих таблицах |
| `LEFT JOIN` | Все строки левой таблицы. Справа `NULL`, если пары нет |
| `RIGHT JOIN` | Все строки правой таблицы. Слева `NULL`, если пары нет |
| `FULL JOIN` | Все строки обеих таблиц |
| `CROSS JOIN` | Все пары строк |

Автор начинает с `LEFT JOIN`. Задача: вывести название каждой книги и имя автора. Запрос `Books b LEFT JOIN Authors a ON b.author_id = a.author_id` даёт пять строк, по одной на книгу.

Порядок таблиц важен для `LEFT` и `RIGHT`. Если поменять таблицы местами, то есть написать `Authors a LEFT JOIN Books b`, строк станет шесть. Последняя строка — автор Mark Twain: книг у него нет, поэтому `book_id` и `title` равны `NULL`. `RIGHT JOIN` и `FULL JOIN` тоже оставляют Mark Twain в результате, а `INNER JOIN` его скрывает.

На практике выбор простой. Нужны только строки с парой в обеих таблицах — берите `INNER JOIN`. Нужно сохранить все строки одной таблицы, даже без пары, — `LEFT JOIN`. Тот же эффект на нашей схеме показывает код [`scripts/duckdb-code/ch03_joins.py`](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch03_joins.py):

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

Несколько `JOIN` подряд соединяют цепочку таблиц. Сначала автор ищет книги читателя John Smith: `Books` соединяется с `Borrowings`, а та с `Borrowers`, после чего условие `WHERE` оставляет нужное имя. Результат: «Pride and Prejudice». Затем он убирает фильтр и выводит всех читателей с книгами. В третьем запросе добавляется `Authors`, чтобы показать ещё и автора. А в последнем примере автор смотрит, какие книги брал Michael Brown и когда.

Без `ORDER BY` порядок строк не гарантирован. Поэтому, если нужен стабильный порядок, добавляйте `ORDER BY`, например по имени читателя и названию книги.

## Агрегаты

Агрегатная функция сворачивает много строк в одно значение: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. С `GROUP BY` их считают по группам.

- Сколько книг взял каждый читатель: `COUNT(br.book_id)` с `GROUP BY` по имени. Результат: у Michael Brown две книги, у остальных по одной.
- Самая популярная книга: считаем выдачи по книгам, сортируем `ORDER BY ... DESC` и берём `LIMIT 1`. Это «Pride and Prejudice», две выдачи.
- Средний возраст авторов: `AVG(YEAR(CURRENT_DATE) - birth_year)`. У автора вышло 162,5 года, а средний год издания книг — 1903,6.
- Самый старый автор: `WHERE birth_year = (SELECT MIN(birth_year) FROM Authors)`. Это Jane Austen, ей «249 лет» (на 2024 год).

Запросы с `CURRENT_DATE` зависят от дня запуска: «249 лет» верно только для 2024 года.

## Аналитика: просрочки, view и вложенные запросы

### Просроченные книги и view

Задача: найти читателей, которые вернули книги с опозданием. Срок выдачи автор принимает за 14 дней. Три таблицы соединяются через `INNER JOIN`, а просрочку считает `DATEDIFF('day', borrow_date, return_date) - 14`. Условие `return_date IS NOT NULL` отбирает только возвращённые книги. Итог: John Smith опоздал на 1 день, William Taylor — на 7.

Такой запрос можно сохранить как `view`: `CREATE VIEW v AS SELECT ...` записывает запрос в базу как виртуальную таблицу. Данные при этом не копируются: при каждом обращении запрос выполняется заново. А обращаются к `view` как к таблице: `SELECT * FROM overdue_borrowings;`.

Теперь очередь невозвращённых книг. Здесь вместо даты возврата берут `CURRENT_DATE()`, а фильтр заменяют на `return_date IS NULL`. Просрочки получаются огромными, от 710 дней и больше, ведь выдачи были в 2022 году. Поэтому автор повторяет запрос с фиксированной датой `'2022-06-10'`. Теперь просрочки 31, 42 и 68 дней: у Michael Brown, Sophia Wilson и Emma Johnson.

### Три уровня вложенных запросов

Последняя задача: найти самую популярную книгу и показать, кто её брал и когда. Автор решает её тремя вложенными `SELECT` и внешним запросом.

![Вложенный запрос: считаем заказы на товар, берём максимум, оставляем товары с максимумом, соединяем с таблицей товаров](/assets/duckdb-up-and-running/ch03-nested-query.png)

Читаем изнутри наружу.

1. Самый внутренний `SELECT` считает выдачи каждой книги: `GROUP BY book_id`.
2. Средний SELECT берёт максимум из этих чисел.
3. Условие `IN` с `HAVING` оставляет книги, у которых счётчик равен максимуму. Так в результат попадут все книги, если рекорд у нескольких.
4. Внешний запрос соединяет эти книги с `Books` и `Borrowers` и выводит детали: название, читателя, дату выдачи и возврата.

Результат: две строки по «Pride and Prejudice», John Smith и Michael Brown.

> **Пояснение:** тот же ответ часто проще получить через `CTE` (`WITH`) или оконную функцию. Шаги в `WITH` читать легче, чем вложенные запросы.

Мы запустили всё это на данных библиотеки из книги, дата зафиксирована. Код: [`scripts/duckdb-code/ch03_library.py`](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch03_library.py).

```text
-- Authors LEFT JOIN Books: шесть строк, Mark Twain без книги
name,title
Jane Austen,Pride and Prejudice
Charles Dickens,Oliver Twist
Agatha Christie,Murder on the Orient Express
J.K. Rowling,"Harry Potter and the Philosopher's Stone"
Tolkien,The Hobbit
Mark Twain,NULL

-- Books INNER JOIN Authors: пять строк
books
5

-- Средний возраст авторов и самый старый автор на 2024 год
avg_age
162.5
name,age
Jane Austen,249

-- View просрочек: возвращённые книги (срок 14 дней)
borrower_name,book_title,overdue
John Smith,Pride and Prejudice,1
William Taylor,The Hobbit,7

-- Невозвращённые книги на дату 2022-06-10
title,borrower_name,overdue
Pride and Prejudice,Michael Brown,31
Oliver Twist,Sophia Wilson,42
Murder on the Orient Express,Emma Johnson,68

-- Самая популярная книга: три вложенных SELECT
title,borrower_name,borrow_date
Pride and Prejudice,John Smith,2022-04-10
Pride and Prejudice,Michael Brown,2022-04-26

-- Ошибка: удалить таблицу, на которую ссылаются
Catalog Error: Could not drop the table because this table is main key table of the table "Books"
```

## Итоги главы

- Консоль `duckdb` позволяет работать с базой без Python. `in-memory` база пропадает при выходе, для долгой работы открывайте файл `.duckdb`.
- Dot-команды относятся к консоли, а не к SQL: `.open`, `.tables`, `.schema`, `.dump`, `.read`. Они не требуют точки с запятой.
- `.open` закрывает текущую базу, а `ATTACH` и `USE` позволяют держать две базы открытыми.
- `EXPORT DATABASE` и `IMPORT DATABASE` переносят базу через папку с `schema.sql`, `load.sql` и CSV.
- `FOREIGN KEY` не даёт вставить несуществующий ключ и не даёт удалить таблицу, на которую ссылаются.
- Всегда пишите `WHERE` в `UPDATE` и `DELETE`. Без него изменятся все строки.
- Пять видов `JOIN` отличаются тем, какие строки без пары попадают в результат. Порядок таблиц важен для `LEFT` и `RIGHT`.
- Агрегатные функции с `GROUP BY` считают по группам. `ORDER BY ... DESC` и `LIMIT 1` находят лидера.
- `View` хранит запрос, а не данные. В запросах с `CURRENT_DATE` фиксируйте дату, чтобы результат повторялся.

## Что изменилось к 2026 году

Это наше дополнение, его нет в книге. Автор работал с DuckDB 0.10.1, мы проверили примеры на версии 1.4.3.

- Выйти из консоли проще: `.exit` или `Ctrl+D`. Автор пишет эти команды без «s» на конце, а в справке они называются `.databases` и `.tables`.
- `FROM t;` без `SELECT *` работает как `SELECT * FROM t`. Автор уже использует эту форму в `CREATE TABLE ... AS FROM`.
- `GROUP BY ALL` сам берёт все столбцы без агрегата, а `SELECT * EXCLUDE (b)` выбирает все столбцы, кроме `b`.
- `ATTACH 'file.duckdb' AS x (READ_ONLY);` подключает базу только для чтения.
- `EXPORT DATABASE 'dir' (FORMAT parquet);` кладёт в папку файлы `.parquet` вместо CSV. Они меньше и хранят типы.

## Ключевые термины

| Термин | Значение |
|---|---|
| `CLI` | Консоль `duckdb` |
| `in-memory` база | База живёт, пока работает процесс |
| Файловая база (`persistent`) | База в файле `.duckdb`, данные остаются после выхода |
| Dot-команда | Команда консоли, начинается с точки |
| `ATTACH` / `USE` | Подключить базу / сделать её активной |
| `EXPORT DATABASE` | Выгрузить базу в папку с SQL и CSV |
| `FOREIGN KEY` | Ссылка на ключ другой таблицы |
| `CRUD` | Создать, прочитать, обновить, удалить |
| `View` | Сохранённый запрос |
| `Subquery` (вложенный запрос) | Запрос внутри запроса |

## Что это значит на практике

- Знайте `.read`, `.timer on` и `.mode`. Они экономят много времени при отладке.
- Скрипты `.sql` и `duckdb -c "..."` удобно запускать в `Makefile` и CI.
- Не рассчитывайте на `FOREIGN KEY` как защиту данных в хранилище. Проверяйте связи тестами `relationships` в `dbt`.
- Фиксируйте даты в тестовых запросах. Иначе результат меняется каждый день.
- Добавляйте `ORDER BY` в тестовые запросы. Без него порядок строк не гарантирован.
- Для разовой проверки файла хватает `duckdb -csv -c "SELECT ..."`: ключи формата вывода делают результат пригодным для других программ.
- Перед `DELETE` и `UPDATE` запустите тот же `WHERE` в `SELECT` и посмотрите, сколько строк он найдёт.

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
3. Чем `.open` отличается от `ATTACH`? Когда нужен второй?
4. Чем `LEFT JOIN` отличается от `INNER JOIN`? Когда нужен первый?
5. Почему запрос с `year(current_date)` даёт разный результат в разные дни?
6. Зачем во вложенном запросе популярной книги стоит `IN` с `HAVING`, а не `ORDER BY ... LIMIT 1`?

Предыдущая: [Глава 2. Импорт данных](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/). Следующая: [Глава 4. DuckDB и Polars](/book-summaries/engineering/duckdb-up-and-running/04-polars/).
