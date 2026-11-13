---
title: "DuckDB: Up and Running, глава 4: DuckDB и Polars"
head:
  - tag: title
    content: "DuckDB и Polars: SQL по DataFrame | Инжиниринг Данных"
description: "Конспект главы 4 DuckDB: Up and Running на русском. Polars DataFrame, lazy evaluation, запросы SQL к DataFrame через duckdb.sql и объект DuckDBPyRelation."
sidebar:
  order: 4
  label: "4. DuckDB и Polars"
tags:
  - books
  - duckdb
  - python
  - polars
---

**Главная мысль:** `Polars` быстро и экономно обрабатывает таблицы в памяти, особенно за счёт ленивых вычислений. DuckDB читает `Polars DataFrame` прямо из переменной Python. Так в одном скрипте можно смешивать методы `Polars` и привычный SQL.

## О чём глава

Предыдущая глава была про [основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/). Здесь автор отвечает: как работать с `DataFrame` быстрее, чем в `pandas`, и не отказываться от SQL? Темы: основы `Polars`, `lazy evaluation`, запросы к `DataFrame` через DuckDB и объект `DuckDBPyRelation`.

![Polars и DuckDB вместе: DataFrame читается по имени, результат возвращается в Polars или pandas](/assets/duckdb-up-and-running/ch04-polars-duckdb.png)

Слева переменная с `DataFrame`. DuckDB выполняет SQL и отдаёт `DuckDBPyRelation`.

## Зачем Polars

`pandas` рассчитан на таблицы, которые помещаются в память. На больших наборах он замедляется. `Polars` решает эту проблему. Автор называет пять свойств:

- **Скорость:** он целиком написан на Rust.
- **Параллельность:** он использует все ядра процессора.
- **Экономия памяти:** вычисления ленивые, цепочку операций оптимизируют до запуска.
- **Колоночное хранение**, эффективнее строкового.
- **Простота:** есть SQL-подобный синтаксис и методы, знакомые по `pandas`.

В книге версия `Polars` 1.8.2.

## Основы Polars

`DataFrame` создают из словаря Python. Автор берёт таблицу машин: 8 строк, 6 колонок. Наш код: [ch04_polars_basics.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_polars_basics.py). Два отличия от `pandas`: у `Polars DataFrame` нет индекса, а под именем колонки печатается её тип (`str`, `i64`, `f64`, `bool`).

**Колонки** выбирает `select()`. Запись `df['Model']` работает, но документация `Polars` называет её антипаттерном и может убрать. Внутри `select()` пишут `expression` (выражение): `pl.col(pl.String)` значит «все строковые колонки».

**Строки** выбирает `filter()`. Одну строку по номеру даёт `df.row(0)`, срезы `df[1:3]` не рекомендуются.

| Задача | Запись |
|---|---|
| Условие | `df.filter(pl.col('Company') == 'Toyota')` |
| «и» / «или» | `(...) & (...)`, `(...) \| (...)`, каждое условие в скобках |
| Значение из списка | `pl.col('Company').is_in(['Toyota', 'Ford'])` |
| Отрицание | `~(...)` или `!=` |

Методы соединяют цепочкой: `filter(...).select('Model', 'Year')`. Класс `SQLContext` запускает SQL по `DataFrame`: `ctx = pl.SQLContext(cars=df)`, затем `ctx.execute("SELECT ...", eager=True)`.

## Lazy evaluation

Это главная причина выбрать `Polars`. Ленивое вычисление строит план запроса и запускает его, только когда вы просите результат.

В `pandas` вы делаете `read_csv()` и потом фильтруете. Файл `flights.csv` из книги (больше 5,8 млн строк) приходится целиком грузить в память ради маленького среза. В `Polars` есть два вида ленивости: **implicit** (функция ленива сама, как `scan_csv()`) и **explicit** (вы делаете ленивой функцию вроде `read_csv()`).

![Три способа читать CSV в Polars: eager, implicit lazy и explicit lazy](/assets/duckdb-up-and-running/ch04-lazy-modes.png)

`scan_csv()` возвращает `LazyFrame`: это план запроса, а не данные. Файл не читается. К `LazyFrame` добавляют `select()` и `filter()`, а `collect()` запускает план и возвращает `DataFrame`. Для сравнения, `read_csv()` работает в eager-режиме: сразу читает весь файл.

Метод `show_graph()` рисует план. Без оптимизации `Polars` прочитал бы все 31 колонку и потом фильтровал. С оптимизацией он читает три нужные колонки и фильтрует при чтении.

![Неоптимизированный план читает всё, оптимизированный читает три колонки и фильтрует при чтении](/assets/duckdb-up-and-running/ch04-lazy-plan.png)

Повторим на своём CSV (200 000 строк). Вместо `show_graph()` мы печатаем план через `explain()` (все три режима: [ch04_lazy.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_lazy.py)):

```python
import polars as pl
import duckdb, tempfile, os

path = os.path.join(tempfile.mkdtemp(), "flights.csv")
duckdb.sql(f"""COPY (SELECT i AS id, 1 + i % 12 AS month,
    ['SFO','SEA','LAX','JFK','ORD'][1 + i % 5] AS origin, i % 97 AS delay,
    i % 31 AS c1, i % 37 AS c2, i % 41 AS c3
    FROM range(200000) t(i)) TO '{path}' (HEADER)""")

q = (
    pl.scan_csv(path)                          # ничего не читаем, получаем LazyFrame
    .select(["month", "origin"])
    .filter((pl.col("month") == 5) & (pl.col("origin") == "SFO"))
)
print(type(q).__name__)
for line in q.explain().replace(path, "flights.csv").splitlines():   # оптимизированный план
    print(line if not line.startswith("SELECTION") else "SELECTION: [условия фильтра]")  # Polars сам решает их порядок
print(q.collect().shape)                          # collect() запускает план
```

```text
LazyFrame
Csv SCAN [flights.csv]
PROJECT 2/7 COLUMNS
SELECTION: [условия фильтра]
(3333, 2)
```

`PROJECT 2/7 COLUMNS`: из файла читаются 2 колонки из 7. Фильтр (`SELECTION`) идёт при чтении.

**Explicit lazy.** После `read_csv()` шаги `select()` и `filter()` идут по очереди без оптимизации. Чтобы их оптимизировать, вызовите `.lazy()` сразу после чтения. Файл всё равно уже прочитан целиком.

> **Пояснение:** `scan_csv()` выгоднее, чем `read_csv().lazy()`: он не читает с диска лишние колонки.

## Запросы к Polars через DuckDB

Методы `Polars` требуют практики. Но большинство разработчиков знают SQL. Автор предлагает взять лучшее от обоих подходов. DuckDB видит `Polars DataFrame` через `Apache Arrow` (платформу для быстрого хранения и передачи данных в памяти). Для этого нужен `pyarrow`.

### Функция sql()

`duckdb.sql()` берёт имя переменной с `DataFrame` как имя таблицы. Она возвращает объект `DuckDBPyRelation` из Relational API DuckDB ([код](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_df_by_name.py)):

```python
import duckdb
import polars as pl

cars = pl.DataFrame({
    "model":   ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox", "Golf", "Hawk"],
    "year":    [1982, 1966, 1994, 1964, 1975, 2000, 1974, 2007],
    "company": ["A", "A", "A", "B", "B", "B", "C", "C"],
})

# cars - переменная Python. DuckDB находит её по имени (через Apache Arrow).
rel = duckdb.sql("""
    SELECT company, count(*) AS models, min(year) AS first_year
    FROM cars GROUP BY company ORDER BY company
""")
print(type(rel).__name__)   # DuckDBPyRelation
print(rel.pl())             # результат обратно в Polars
```

```text
DuckDBPyRelation
shape: (3, 3)
┌─────────┬────────┬────────────┐
│ company ┆ models ┆ first_year │
│ ---     ┆ ---    ┆ ---        │
│ str     ┆ i64    ┆ i64        │
╞═════════╪════════╪════════════╡
│ A       ┆ 3      ┆ 1966       │
│ B       ┆ 3      ┆ 1964       │
│ C       ┆ 2      ┆ 1974       │
└─────────┴────────┴────────────┘
```

Результат переводят в нужный формат: `.pl()` даёт `Polars`, `.df()` даёт `pandas`. Сам объект тоже умеет `describe()` (базовая статистика), `order('Year DESC')` и `apply('min', 'Year')`.

Автор советует: если SQL проще, пишите SQL. Сортировка и подсчёт по группам в SQL занимают одну фразу. В `Polars` для подсчёта нужны `value_counts()` и `unnest()`. Оба варианта: [ch04_duckdb_polars.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_duckdb_polars.py).

### Объект DuckDBPyRelation

Это второй способ строить запросы: вместо текста SQL вы вызываете методы. Объект получают из SQL-запроса или из соединения: `conn.table('customers')`. Автор создаёт три таблицы (`customers`, `products`, `sales`) и показывает методы.

![Методы DuckDBPyRelation и их аналоги в SQL](/assets/duckdb-up-and-running/ch04-relation-sql.png)

- `insert()` добавляет строку.
- `join()` соединяет таблицы (параметры `condition` и `how`). Клиентов соединяют с продажами, потом с товарами.
- `filter()` отбирает строки, `aggregate()` считает агрегаты по группе, `project()` выбирает колонки.
- `limit(3, 2)` возвращает 3 строки, начиная со смещения 2.

Весь код: [ch04_relation.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_relation.py).

## Итоги главы

- `Polars` написан на Rust: быстрый, параллельный, колоночный, без индекса. Колонки выбирают через `select()`, строки через `filter()`.
- `Lazy evaluation` строит план. `collect()` запускает его, читая только нужные колонки.
- `scan_csv()` ленив сам, `read_csv()` ленив только после `.lazy()`.
- DuckDB читает `Polars DataFrame` по имени переменной через `Apache Arrow`.
- `duckdb.sql()` возвращает `DuckDBPyRelation`. Его строят методами или SQL и забирают через `.pl()` или `.df()`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Polars` | Библиотека DataFrame на Rust |
| `LazyFrame` | План запроса, который ещё не выполнен |
| `expression` | Выражение `pl.col(...)`, из которых строят запрос |
| `collect()` | Запуск ленивого плана |
| `Apache Arrow` | Колоночный формат данных в памяти. Через него DuckDB читает DataFrame без копирования |
| `DuckDBPyRelation` | Объект запроса DuckDB в Python |

## Что это значит на практике

- DuckDB читает `pandas` и `Polars` без загрузки в базу. Это удобно в ноутбуке.
- Для больших CSV и Parquet используйте ленивое чтение (`scan_csv`, `scan_parquet`). Вы не платите за колонки, которые не нужны.
- Смешивайте стили. Фильтры и выражения пишите в `Polars`, сложные `JOIN` и оконные функции пишите в SQL.
- Если команда знает SQL, DuckDB снижает порог входа в `DataFrame`.
- Версия в книге: Polars 1.8.2. В новых версиях API мог поменяться. Проверяйте документацию.
- Порядок условий в плане `Polars` не фиксирован. Не проверяйте текст плана в тестах.

## Практика в DuckDB

SQL запускайте в `duckdb` или на [shell.duckdb.org](https://shell.duckdb.org). Для Python: `pip install polars==1.8.2 duckdb pyarrow`.

### Шаг 1. Те же операции на SQL

```sql
CREATE TABLE cars AS
SELECT * FROM (VALUES
    ('Alfa',  1982, 'A', 2.5),
    ('Bravo', 1994, 'A', 2.0),
    ('Cargo', 2000, 'B', 1.5),
    ('Delta', 1975, 'B', 2.7),
    ('Echo',  2007, 'C', 1.4),
    ('Fox',   1966, 'C', 1.8)
) t(model, year, company, engine);

SELECT company, count(*) AS models, round(avg(engine), 2) AS avg_engine
FROM cars GROUP BY company ORDER BY company;
```

Ожидаем три строки: A, B, C. По 2 модели в каждой.

### Задания

В Python те же данные лежат в `Polars DataFrame` `cars`. Решения запущены в [ch04_practice.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/duckdb-code/ch04_practice.py).

**1.** На Polars выберите модели компании `A` с двигателем больше 2.0.

<details>
<summary>Решение</summary>

```python
cars.filter(
    (pl.col("company") == "A") & (pl.col("engine") > 2.0)
).select("model")
```

Результат: `Alfa`. Каждое условие стоит в скобках.
</details>

**2.** Запросом SQL по `DataFrame` найдите самый ранний год у каждой компании.

<details>
<summary>Решение</summary>

```python
duckdb.sql("""
    SELECT company, min(year) AS first_year
    FROM cars GROUP BY company ORDER BY company
""").pl()
```

Получим A: 1982, B: 1975, C: 1966.
</details>

**3.** Методами `DuckDBPyRelation`: `year > 1980`, колонки `model` и `year`, сортировка по году, 2 строки.

<details>
<summary>Решение</summary>

```python
rel = duckdb.sql("SELECT * FROM cars")
rel.filter("year > 1980").project("model, year").order("year").limit(2)
```

Результат: `Alfa` 1982 и `Bravo` 1994.
</details>

## Вопросы для самопроверки

1. Чем `read_csv` отличается от `scan_csv` в Polars?
2. Что делает `collect()`? Что будет, если его не вызвать?
3. Как DuckDB читает Python-переменную с `DataFrame`? Какая библиотека нужна?
4. Когда лучше писать SQL, а когда выражения Polars?

Предыдущая: [Глава 3. Основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/). Следующая: [Глава 5. EDA и геоанализ](/book-summaries/engineering/duckdb-up-and-running/05-eda-spatial/).
