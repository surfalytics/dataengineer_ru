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

**Главная мысль:** `Polars` быстро обрабатывает таблицы в памяти. DuckDB позволяет писать SQL прямо по `DataFrame`. Вместе они дают скорость и привычный язык.

## Зачем Polars

`pandas` грузит всю таблицу в память. На больших файлах он медленный. `Polars` решает это.

| Свойство | Что даёт |
|---|---|
| Написан на Rust | Высокая скорость |
| Параллельность | Использует все ядра процессора |
| Колоночное хранение | Эффективная память |
| Lazy evaluation | Запрос оптимизируется до запуска |
| Синтаксис | Похож на pandas и SQL |

- У `Polars DataFrame` нет индекса. Автор считает индекс ненужным.
- Под названием колонки `Polars` показывает её тип: `str`, `i64`, `f64`, `bool`.
- Квадратные скобки `df['col']` работают, но не рекомендуются. Используйте `select()` и `filter()`.

## Основы Polars

| Задача | Метод |
|---|---|
| Выбрать колонки | `df.select('a', 'b')` |
| Выбрать колонки по типу | `df.select(pl.col(pl.String))` |
| Выбрать строки | `df.filter(pl.col('year') > 1980)` |
| Несколько условий | Каждое условие в скобках, между ними `&` и `\|` |
| Значение из списка | `pl.col('x').is_in([...])` |
| Сортировка | `.sort_by(...)` в выражении или `df.sort(...)` |
| Первая строка | `df.row(0)` |

`pl.col(...)` называется `expression`. Выражения можно соединять в цепочку.

### SQL внутри Polars

Класс `SQLContext` выполняет SQL по `DataFrame`. Имя таблицы вы задаёте сами: `ctx = pl.SQLContext(cars=df)`.

## Lazy evaluation

Идея: не выполнять шаги сразу. Собрать план, оптимизировать, и только потом запустить.

| Режим | Как включить | Что происходит |
|---|---|---|
| Eager | `pl.read_csv()` | Файл целиком читается в память сразу |
| Implicit lazy | `pl.scan_csv()` | Возвращает `LazyFrame`. Ничего не читается |
| Explicit lazy | `pl.read_csv(...).lazy()` | Файл уже прочитан, но дальше шаги оптимизируются |

- `collect()` запускает план и возвращает `DataFrame`.
- `show_graph()` рисует план. Оптимизированный план читает только нужные колонки и применяет фильтр при чтении.
- На файле в 5,8 млн строк это экономит память: выбираются 3 колонки из 31.

## DuckDB поверх DataFrame

DuckDB видит `DataFrame` через `Apache Arrow`. Нужна библиотека `pyarrow`. Имя Python-переменной с `DataFrame` можно использовать как имя таблицы.

```python
import duckdb
# df — любая переменная с Polars или pandas DataFrame
result = duckdb.sql("SELECT * FROM df")
```

Функция `duckdb.sql()` возвращает объект `DuckDBPyRelation`. Из него можно получить результат в нужном виде.

| Метод | Результат |
|---|---|
| `.pl()` | `Polars DataFrame` |
| `.df()` | `pandas DataFrame` |
| `.describe()` | Статистика по колонкам |
| `.order('year DESC')` | Сортировка |
| `.apply('min', 'year')` | Агрегат по колонке |

Автор советует: если задачу проще выразить на SQL, пишите SQL и забирайте результат через `.pl()`.

## Объект DuckDBPyRelation

Это второй способ строить запросы. Вместо текста SQL вы вызываете методы.

| Метод | Аналог в SQL |
|---|---|
| `conn.table('t')` | `FROM t` |
| `.insert([...])` | `INSERT INTO` |
| `.join(other, condition=..., how='inner')` | `JOIN` |
| `.filter('customer_id = 1')` | `WHERE` |
| `.aggregate('...', 'group_col')` | `GROUP BY` |
| `.project('a, b')` | `SELECT a, b` |
| `.limit(3, 2)` | `LIMIT 3 OFFSET 2` |

- Методы можно соединять в цепочку.
- Для повторного запроса к результату можно вызвать `conn.execute('SELECT ... FROM result')`.

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

## Практика в DuckDB

Нужны Python и пакеты: `pip install polars duckdb pyarrow`. Блоки идут по порядку. SQL-блоки можно запустить и в терминале `duckdb`.

### Шаг 1. Создаём DataFrame

```python
import polars as pl
import duckdb

cars = pl.DataFrame({
    "model":   ["Alfa", "Bravo", "Cargo", "Delta", "Echo", "Fox"],
    "year":    [1982, 1994, 2000, 1975, 2007, 1966],
    "company": ["A", "A", "B", "B", "C", "C"],
    "engine":  [2.5, 2.0, 1.5, 2.7, 1.4, 1.8],
})
print(cars)
```

### Шаг 2. SQL по DataFrame

```python
# DuckDB находит переменную cars по имени
duckdb.sql("""
    SELECT company, count(*) AS models, round(avg(engine), 2) AS avg_engine
    FROM cars
    GROUP BY company
    ORDER BY company
""").pl()
```

Ожидаем три строки: A, B, C. По 2 модели в каждой.

### Шаг 3. Ленивый запрос

```python
q = (
    cars.lazy()
    .filter(pl.col("year") > 1980)
    .select("model", "year")
)
print(q.collect())   # 4 строки: Alfa, Bravo, Cargo, Echo
```

### Шаг 4. Тот же результат на SQL

Этот блок работает в терминале `duckdb`. Он проверяет логику без Python.

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

SELECT model, year FROM cars WHERE year > 1980 ORDER BY year;
```

### Задания

**1.** На Polars выберите модели компании `A`, у которых двигатель больше 2.0. Выведите только `model`.

<details>
<summary>Решение</summary>

```python
cars.filter(
    (pl.col("company") == "A") & (pl.col("engine") > 2.0)
).select("model")
```

Результат: одна строка, `Alfa`. Каждое условие стоит в скобках.
</details>

**2.** Запросом SQL по `DataFrame` посчитайте самый ранний год для каждой компании.

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

**3.** Сделайте то же через методы `DuckDBPyRelation`, без текста SQL: отфильтруйте `year > 1980`, оставьте `model` и `year`, ограничьте до 2 строк.

<details>
<summary>Решение</summary>

```python
rel = duckdb.sql("SELECT * FROM cars")
rel.filter("year > 1980").project("model, year").limit(2)
```

Методы идут по цепочке, как `WHERE`, `SELECT`, `LIMIT` в SQL.
</details>

## Вопросы для самопроверки

1. Чем `read_csv` отличается от `scan_csv` в Polars?
2. Что делает `collect()`? Что будет, если его не вызвать?
3. Как DuckDB читает Python-переменную с `DataFrame`? Какая библиотека нужна?
4. Когда лучше писать запрос на SQL, а когда в выражениях Polars?

Предыдущая: [Глава 3. Основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/). Следующая: [Глава 5. EDA и геоанализ](/book-summaries/engineering/duckdb-up-and-running/05-eda-spatial/).
