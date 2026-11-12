---
title: "DuckDB: Up and Running, глава 7: DuckDB и JupySQL"
head:
  - tag: title
    content: "JupySQL и DuckDB: SQL в Jupyter Notebook | Инжиниринг Данных"
description: "Конспект главы 7 DuckDB: Up and Running на русском. JupySQL, magic-команды %sql и %sqlplot, snippets, графики, подключение к MySQL и хранение паролей."
sidebar:
  order: 7
  label: "7. JupySQL"
tags:
  - books
  - duckdb
  - sql
  - jupyter
---

**Главная мысль:** не тащите все данные в `pandas`, чтобы построить график. Пусть SQL посчитает итог в DuckDB. В ноутбук приходит только маленький результат. JupySQL даёт для этого SQL-ячейки и команды для графиков.

## Проблема: данные в памяти ноутбука

Обычный путь аналитика такой: прочитать данные из базы или CSV в `DataFrame`, потом строить график в `matplotlib`.

- Запросы к рабочей базе могут её замедлить. Она не рассчитана на аналитику.
- Весь набор данных лежит в памяти, даже если для графика нужны 5 чисел.
- `matplotlib` тоже держит в памяти объекты рисунка.

Автор предлагает другой порядок. Фильтрация и агрегация идут в движке DuckDB. График строится по маленькой таблице.

## Что такое JupySQL

JupySQL — расширение для Jupyter Notebook. Это форк `ipython-sql`, его развивает команда Ploomber. Оно добавляет SQL-ячейки.

| Команда | Что делает |
|---|---|
| `%sql` | Одна строка SQL (line magic) |
| `%%sql` | Ячейка с многострочным SQL (cell magic) |
| `%sqlplot` | График по таблице или по сохранённому запросу |
| `%sqlcmd` | Служебные команды: `tables`, `columns`, `profile` |

Установка: `pip install jupysql duckdb-engine`. Пакет `duckdb-engine` — это драйвер DuckDB для `SQLAlchemy`. Для графиков нужен ещё `matplotlib`.

## Подключение к DuckDB

```text
%load_ext sql
%sql duckdb://
%sql duckdb:///MyDB.db
```

- `duckdb://` — база в памяти. После перезапуска ядра всё пропадёт.
- `duckdb:///MyDB.db` — база в файле. Таблицы останутся.
- Не пишите комментарий в той же строке, что `%load_ext sql`. Он станет частью имени модуля, будет ошибка.
- `%sql?` показывает справку.

## Запросы и результат

- Можно читать файлы прямо в SQL: `%sql SELECT * FROM 'airlines.csv'`.
- Результат — объект `ResultSet`. Метод `.DataFrame()` делает из него `pandas`.
- JupySQL показывает только 10 строк. Чтобы увидеть всё: `%config SqlMagic.displaylimit = None`.
- Запрос из файла не сохраняется в базу. Чтобы сохранить, нужен `CREATE TABLE ... AS`.
- `%sqlcmd tables` — список таблиц. `%sqlcmd columns -t имя` — схема. `%sqlcmd profile -t имя` — статистика по колонкам.

## Snippets: сохранённые запросы

`%%sql --save имя` даёт запросу имя. Потом его можно использовать как таблицу.

- Опция `--no-execute` только сохраняет запрос. Он не запускается.
- Snippets живут в ноутбуке. В файл DuckDB они не попадают, даже в файловой базе.
- Сохранённый запрос можно подставить в `%sqlplot` через `--table` или `--with`.

## Графики: `%sqlplot`

| График | Команда | Когда нужен |
|---|---|---|
| Гистограмма | `histogram` | Распределение числа. Есть `--bins`, `--breaks`, `--binwidth` |
| Box plot | `boxplot` | Медиана, квартили и выбросы. Опция `--orient h` делает его горизонтальным |
| Круговая | `pie` | Доли целого. Мало категорий, лучше топ-5 |
| Столбчатая | `bar` | Сравнение категорий. `--show-numbers` пишет числа на столбцах |

- Каждая команда возвращает объект осей `matplotlib`. Присвойте его переменной: `ax = %sqlplot ...`. Потом меняйте цвета, заголовок и подписи обычным кодом.
- Два графика на одной оси дают сравнение. В примере книги так сравнивают выживших и невыживших по возрастным группам Titanic.
- Возрастные группы считает SQL с `CASE WHEN`. График получает 7 строк, а не 900.

## Подключение к MySQL

JupySQL подключается и к серверам: MySQL, PostgreSQL, SQL Server, Oracle. Для MySQL нужен драйвер `mysqlclient`. Книга показывает три способа хранить доступ.

| Способ | Как работает | Минус |
|---|---|---|
| Переменная `DATABASE_URL` | Строка подключения `SQLAlchemy`, пароль вводится через `getpass()` | Пароль нужно вводить при каждом запуске |
| Файл `.ini` | Секции `[mysqldb]` в `~/.jupysql/connections.ini`. Выбор: `%sql --section mysqldb` | Пароль лежит открытым текстом |
| `keyring` | Пароль в хранилище паролей операционной системы | Нужна настройка. Автор рекомендует этот способ |

Список подключений: `%sql --connections`. Переключиться: `%sql имя_секции`.

## Ключевые термины

| Термин | Значение |
|---|---|
| JupySQL | Расширение Jupyter для SQL-ячеек |
| Magic command | Команда ноутбука с `%` или `%%` |
| Snippet | Сохранённый именованный запрос |
| `duckdb-engine` | Драйвер DuckDB для `SQLAlchemy` |
| Connection string | Строка с типом базы, пользователем, хостом и именем базы |
| `keyring` | Библиотека доступа к хранилищу паролей ОС |
| Outlier | Выброс: значение далеко от остальных |

## Что это значит на практике

- Агрегируйте в SQL, рисуйте по результату. Так ноутбук не упирается в память.
- Для быстрой EDA JupySQL удобен. Для отчётов лучше BI-инструмент или `dbt` с витринами.
- Не храните пароль в ноутбуке и в git. Файл `connections.ini` добавьте в `.gitignore` или используйте `keyring`.
- Ноутбук с `%%sql` читается как SQL-скрипт. Его проще показать коллеге, чем код на `pandas`.
- Книга использует аэропорты, Boston и Titanic. Ниже практика на придуманных данных.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Магические команды JupySQL (`%sql`, `%sqlplot`) работают только в Jupyter. Мы отрабатываем ту часть, которую делает SQL: итоги для графиков.

### Шаг 1. Создаём данные

```sql
-- 200 пассажиров: возраст, класс и признак «рейс прибыл вовремя»
CREATE TABLE passengers AS
SELECT
    i AS passenger_id,
    (5 + (i * 37) % 70)::INT AS age,
    CASE WHEN (i * 11) % 5 < 2 THEN 'business' ELSE 'economy' END AS cabin,
    (i * 7) % 3 = 0 AS on_time
FROM range(1, 201) t(i);
```

### Шаг 2. Проверяем

```sql
-- должно быть 200 строк, возраст от 5 до 74
SELECT count(*) AS n, min(age) AS min_age, max(age) AS max_age FROM passengers;
```

### Шаг 3. Итоги для столбчатого графика

То, что `%sqlplot bar` рисует, — это такая таблица. Возрастные группы считает SQL.

```sql
CREATE TABLE age_groups AS
SELECT
    CASE
        WHEN age < 20 THEN '0-19'
        WHEN age < 40 THEN '20-39'
        WHEN age < 60 THEN '40-59'
        ELSE '60+'
    END AS age_group,
    count(*) FILTER (WHERE on_time)     AS on_time_count,
    count(*) FILTER (WHERE NOT on_time) AS late_count
FROM passengers
GROUP BY age_group
ORDER BY age_group;

SELECT * FROM age_groups;
```

### Задания

**1.** Посчитайте число пассажиров в каждом `cabin`. Это данные для круговой диаграммы.

<details>
<summary>Решение</summary>

```sql
SELECT cabin, count(*) AS n FROM passengers GROUP BY cabin ORDER BY n DESC;
```

`economy` — 120, `business` — 80. Для pie chart хватает двух строк.

</details>

**2.** Найдите медиану и квартили `age`. Это данные для box plot.

<details>
<summary>Решение</summary>

```sql
SELECT
    quantile_cont(age, 0.25) AS q1,
    median(age)              AS q2,
    quantile_cont(age, 0.75) AS q3
FROM passengers;
```

Q1 = 21,75, медиана = 40, Q3 = 56,25. Box plot строится из этих трёх чисел, `min` и `max`.

</details>

**3.** Постройте данные для гистограммы с шагом 10 лет: колонка `bucket` и число пассажиров.

<details>
<summary>Решение</summary>

```sql
SELECT (age // 10) * 10 AS bucket, count(*) AS n
FROM passengers
GROUP BY bucket
ORDER BY bucket;
```

Восемь строк от 0 до 70. В крайних корзинах по 14 человек, в остальных 27–30. Все 200 строк в `pandas` не нужны.

</details>

## Вопросы для самопроверки

1. Почему лучше агрегировать данные в SQL, а не в `pandas`, перед построением графика?
2. Чем отличаются `%sql` и `%%sql`?
3. Что делает опция `--no-execute` у `%%sql --save`? Где живёт snippet?
4. Какой из трёх способов хранить пароль MySQL лучший и почему?

Предыдущая: [Глава 6. JSON](/book-summaries/engineering/duckdb-up-and-running/06-json/). Следующая: [Глава 8. Удалённые данные](/book-summaries/engineering/duckdb-up-and-running/08-remote-data/).
