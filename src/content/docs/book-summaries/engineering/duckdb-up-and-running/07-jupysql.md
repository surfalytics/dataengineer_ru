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

## О чём глава

Глава отвечает на вопрос: как работать с SQL в Jupyter Notebook и строить графики, не загружая всё в память. После [главы 6](/book-summaries/engineering/duckdb-up-and-running/06-json/) про JSON мы смотрим на ноутбук как на рабочее место аналитика. Темы: запросы и `snippets`, четыре вида графиков, подключение к MySQL.

![Обычный путь через DataFrame и путь через JupySQL: SQL считает итог в DuckDB, на график идёт маленькая таблица](/assets/duckdb-up-and-running/ch07-jupysql-flow.png)

Верхняя полоса — привычный путь: данные целиком в `DataFrame`, потом график. Нижняя — путь главы: SQL сжимает данные, график строится по маленькой таблице.

## Проблема: данные в памяти ноутбука

Обычно аналитик читает данные из сервера БД или из файла в `pandas DataFrame` и рисует график. Автор называет три минуса:

- Запросы к серверу БД могут замедлить его: сервер часто не рассчитан на аналитику.
- Чтобы показать одну сторону данных, нужно загрузить в память весь набор.
- `matplotlib` тоже занимает память: он держит фигуры, оси, текст и массивы данных, пока фигура не закрыта.

`pandas` хорош для быстрых графиков при EDA. Но фильтрацию и агрегацию лучше отдать быстрому движку, а для графика взять готовый итог. Таким движком служит DuckDB.

## Что такое JupySQL

JupySQL — SQL-клиент для Jupyter Notebook. Это форк `ipython-sql`, его развивает команда Ploomber. Через движок DuckDB он читает CSV и ходит на серверы вроде MySQL и PostgreSQL. Хранить `DataFrame` не нужно.

Установка: `pip install jupysql duckdb-engine`. Пакет `duckdb-engine` — драйвер DuckDB для `SQLAlchemy` (библиотека Python для работы с реляционными базами). Для графиков нужен ещё `matplotlib`.

![Команды JupySQL: подключение, %sql, %%sql, %sqlcmd, сохранённый запрос и %sqlplot](/assets/duckdb-up-and-running/ch07-magics.png)

| Команда | Что делает |
|---|---|
| `%sql` | Одна строка SQL (line magic) |
| `%%sql` | Ячейка с многострочным SQL (cell magic) |
| `%sqlplot` | График |
| `%sqlcmd` | Служебные команды: `tables`, `columns`, `profile` |

### Подключение к DuckDB

```text
%load_ext sql
%sql duckdb://
%sql duckdb:///MyDB.db
```

- `duckdb://` — база в памяти. После перезапуска ядра таблицы пропадут.
- `duckdb:///MyDB.db` — база в файле. Таблицы остаются между сессиями.
- Автор предупреждает: не пишите комментарий в строке с `%load_ext sql`. JupySQL примет его за имя модуля и выдаст ошибку. Комментарий пишите отдельной строкой.
- `%sql?` показывает справку.

### Запросы и результат

- Файлы читаются прямо в SQL: `%sql SELECT * FROM 'airlines.csv'`.
- Результат — объект `ResultSet`. Метод `.DataFrame()` делает из него `pandas`.
- JupySQL показывает только 10 строк. Чтобы увидеть всё: `%config SqlMagic.displaylimit = None` (или 0).
- Запрос к файлу не сохраняет данные в базу. Чтобы сохранить, нужен `CREATE TABLE airlines AS FROM 'airlines.csv'`. В файловой базе такая таблица остаётся навсегда.
- `%sqlcmd tables` — список таблиц, `%sqlcmd columns -t имя` — схема, `%sqlcmd profile -t имя` — статистика по столбцам.

### Snippets: сохранённые запросы

`snippet` — это запрос с именем. `%%sql --save state_count` сохраняет и выполняет запрос. Потом его вызывают как таблицу: `%sql SELECT * FROM state_count`.

- Опция `--no-execute` только сохраняет запрос. Он не запускается.
- Snippets живут в ноутбуке. В базу DuckDB они не попадают, даже если база в файле.

Ниже короткий пример. Мы выполнили эти команды через IPython, а не в браузере, но команды те же. Данные придуманы и строятся в скрипте ([полный код](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch07_jupysql.py), файл `scripts/duckdb-code/ch07_jupysql.py`):

```text
%load_ext sql
%sql duckdb://
%%sql --save state_count --no-execute
SELECT state, count(*) AS n FROM 'airports.csv' GROUP BY state ORDER BY n DESC LIMIT 3
%sql SELECT * FROM state_count
%sqlplot bar --table state_count --column state n
```

```text
Connecting to 'duckdb://'
1. Запрос к CSV без загрузки (%sql):
ResultSet -> [{'state': 'CA', 'n': 22}, {'state': 'FL', 'n': 7}, {'state': 'NY', 'n': 8}, {'state': 'TX', 'n': 15}, {'state': 'WA', 'n': 8}]

2. Snippet: --save и --no-execute (%%sql):
Skipping execution...
snippet не выполнился, но его можно вызвать как таблицу:
Generating CTE with stored snippets: 'state_count'
[{'state': 'CA', 'n': 22}, {'state': 'TX', 'n': 15}, {'state': 'NY', 'n': 8}]

3. Служебные команды (%sqlcmd):
tables: ['airports']

4. График (%sqlplot) строится по маленькой таблице:
Removing NULLs, if there exists any from state and n
Axes столбцов: 3 высоты: [22, 15, 8]
файл графика создан: True
Closing duckdb://
```

## Графики: `%sqlplot`

Каждая команда читает таблицу или snippet: `--table` или `--with`. Столбец задаёт `--column`.

![Четыре вида графиков JupySQL и вопросы, на которые они отвечают](/assets/duckdb-up-and-running/ch07-plots.png)

### Histogram

`histogram` показывает, как значения числа распределены по корзинам (`bins`). Корзина — это диапазон значений, а высота столбца — сколько значений в него попало. Опции: `--bins` (число корзин, по умолчанию 50), `--breaks` (свои границы), `--binwidth` (ширина корзины).

Автор строит гистограммы для аэропортов, для Boston housing (возраст и цена `medv` в одной команде) и для Titanic. Возраст на Titanic он делит на 10 корзин. Больше всего пассажиров было за тридцать.

### Настройка графика

Команда возвращает объект осей `matplotlib`. Присвойте его: `ax = %sqlplot histogram ...`. Дальше цвета, заголовок и подписи меняются обычным кодом. Через `ax.patches` (фигуры графика, например столбцы) автор красит столбцы в цвета палитры `seaborn` и меняет `set_title`.

### Box plot

`boxplot` показывает минимум, Q1, медиану, Q3 и максимум. Ящик — это межквартильный размах: в нём лежит средняя половина данных. «Усы» показывают остальной диапазон. Выбросы (`outliers`) — значения, далёкие от остальных, — рисуются кружками. Так удобно сравнивать группы. Опция `--orient h` делает ящик горизонтальным.

### Pie chart

Круговая диаграмма показывает доли. Чтобы она читалась, автор берёт топ-5 штатов по числу аэропортов. `--show-numbers` пишет проценты на долях.

### Bar plot

Столбчатая диаграмма сравнивает категории. `--show-numbers` пишет число над столбцом.

Главный пример автора: влиял ли возраст на выживание на Titanic? SQL с `CASE WHEN` делит пассажиров на возрастные группы (от 0-9 до 60+) и считает выживших и погибших. График получает 7 строк, а не сотни пассажиров. Два `bar` рисуются на одной оси. Вывод: среди детей до 9 лет выжила больше половины, в остальных группах погибла больше половины, хуже всего у старше 60.

## Подключение к MySQL

Данные чаще лежат на сервере. JupySQL подключается к MySQL, PostgreSQL, SQL Server и Oracle, для каждого нужен свой драйвер. Для MySQL автор ставит `mysqlclient`. Пример опирается на базу `My_DB` из главы 2. Книга показывает три способа хранить доступ.

![Три способа хранить доступ к MySQL: переменная DATABASE_URL, файл connections.ini и keyring](/assets/duckdb-up-and-running/ch07-connect-ways.png)

**Переменная `DATABASE_URL`.** Строка `SQLAlchemy` вида `mysql://user:password@host/db`. Пароль запрашивают через `getpass()`, а не пишут в коде. Строку кладут в `environ["DATABASE_URL"]`, и `%sql` без аргументов подключается сам. `%sql --connections` показывает подключения.

**Файл `.ini`.** Параметры лежат в `connections.ini`, по умолчанию в `~/.jupysql/`. В файле секции вроде `[mysqldb]` с полями `drivername`, `username`, `password`, `host`, `port`, `database`. Секцию загружают так: `%sql --section mysqldb`. Настройки отделены от кода, их легко менять для разных сред. Между подключениями переключаются через `%sql mysqldb`. Активное помечено `*`.

**`keyring`.** У первых двух способов есть слабость. Пароль надо вводить при каждом запуске, а это мешает автозапуску ноутбука. В `.ini` он лежит открытым текстом. `keyring` кладёт пароль в менеджер паролей ОС: `keyring.set_password(...)`. Потом пароль читают через `keyring.get_password(...)`, создают `create_engine(db_url)` и подключаются через `%sql engine`. Автор советует этот способ как самый безопасный.

## Итоги главы

- Фильтрация и агрегация идут в DuckDB. Данные не проходят через `DataFrame`, поэтому память ноутбука не растёт.
- `duckdb://` — база в памяти, `duckdb:///файл.db` — база в файле. Запрос к CSV сам по себе ничего не сохраняет.
- `snippet` — сохранённый запрос. Он живёт в ноутбуке, а не в базе.
- `%sqlplot` строит `histogram`, `boxplot`, `pie` и `bar`. Результат — объект осей `matplotlib`, его можно настроить.
- Самый безопасный способ хранить пароль — `keyring`.

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
- Snippets пропадают вместе с ноутбуком. Запрос, который нужен всем, сохраните как `VIEW` или таблицу в базе.
- Закрепляйте версии `jupysql`, `duckdb-engine`, `SQLAlchemy` и `pandas`: пакеты быстро меняются.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Команды `%sql` и `%sqlplot` работают только в Jupyter, поэтому мы делаем SQL-часть: итоги для графиков.

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
5. Когда для графика лучше взять `boxplot`, а когда `histogram`?

Предыдущая: [Глава 6. JSON](/book-summaries/engineering/duckdb-up-and-running/06-json/). Следующая: [Глава 8. Удалённые данные](/book-summaries/engineering/duckdb-up-and-running/08-remote-data/).
