---
title: "DuckDB: Up and Running, глава 5: EDA и геоанализ"
head:
  - tag: title
    content: "EDA в DuckDB: расширение spatial и SQL | Инжиниринг Данных"
description: "Конспект главы 5 DuckDB: Up and Running на русском. EDA на SQL, расширение spatial, ST_Distance, ближайшие аэропорты, доли отмен и задержек рейсов."
sidebar:
  order: 5
  label: "5. EDA и геоанализ"
tags:
  - books
  - duckdb
  - sql
  - eda
---

**Главная мысль:** разведочный анализ (`EDA`) можно сделать почти целиком на SQL в DuckDB. Python нужен только для карт и графиков. В главе всё идёт на одном датасете: рейсы США за 2015 год.

## Что такое EDA

`EDA` (exploratory data analysis) — первый взгляд на данные. Цель: понять, что в них есть, и найти закономерности.

| Приём | Что делаем |
|---|---|
| Summarization | Считаем среднее, медиану, `count`, `min`, `max` |
| Visualization | Рисуем графики |
| Trends | Ищем закономерности и аномалии |

## Датасет

Автор берёт три CSV-файла и грузит их в таблицы через `read_csv_auto()`.

| Таблица | Что в ней |
|---|---|
| `airlines` | Авиакомпании: код и название |
| `airports` | Аэропорты: код, город, штат, широта, долгота |
| `flights` | Рейсы: дата, маршрут, задержки, отмены. Больше 5 млн строк |

## Геоанализ с расширением spatial

Расширение ставится одной командой: `INSTALL spatial; LOAD spatial;`. Дальше доступны функции для точек и расстояний.

| Функция | Что делает |
|---|---|
| `ST_Point(lon, lat)` | Делает точку из долготы и широты |
| `ST_AsText(geom)` | Показывает точку как текст (WKT) |
| `ST_GeomFromText(wkt)` | Читает точку из текста |
| `ST_Distance(a, b)` | Расстояние между точками |
| `ST_DWithin(a, b, d)` | Лежат ли точки не дальше `d` друг от друга |

- Порядок аргументов в `ST_Point`: сначала долгота, потом широта. Это частая ошибка.
- Расстояние на плоскости считается в градусах, не в километрах. Для грубого поиска «ближайших» этого хватает. Для километров нужны сферические функции.
- Автор делает точку двумя способами: через `Shapely` в pandas и через `ST_Point` в SQL. Второй способ проще.
- Для карты автор берёт `folium` и `leafmap`. Это библиотеки Python, они не часть DuckDB.

### Поиск ближайших аэропортов

Два способа:

- `ST_DWithin` — все аэропорты в радиусе. Радиус 3 градуса вокруг Майами дал 8 аэропортов, 2 градуса — 5.
- `ST_Distance` + `ORDER BY distance LIMIT 3` — три самых близких. Этот способ удобнее, когда нужно «топ N».

## Описательная аналитика на SQL

Автор отвечает на вопросы бизнеса обычными запросами.

| Вопрос | Приём |
|---|---|
| Сколько аэропортов в каждом штате? | `GROUP BY state`, `ORDER BY count DESC` |
| Сколько рейсов между каждой парой аэропортов? | `GROUP BY origin, destination` |
| Какая доля рейсов отменена? | `SUM(cancelled) * 100.0 / COUNT(*)` |
| Как рейсы распределены по дням недели? | `GROUP BY day_of_week`, отмены исключаем |
| В какое время суток задержки больше? | `CASE WHEN` по часам вылета |
| Какая авиакомпания задерживает чаще? | Доля, а не число задержек |

### Доля вместо числа

- Авиакомпания с большим числом рейсов всегда лидирует по числу задержек. Это не значит, что она хуже.
- Сравнивайте доли: `задержанные / все`. Автор считает долю отмен по каждой авиакомпании. Названия берёт через `JOIN` с `airlines`.
- Доля рейсов по дням недели считается через два `CTE`: рейсы за день и рейсы за всё время по маршруту.

### Временные слоты

Сутки делятся на четыре окна по шесть часов. Каждому рейсу ставится окно через `CASE WHEN`. Затем считается средняя задержка прибытия. Вывод автора: вечерний слот самый плохой.

### Проверка данных

В данных за октябрь коды аэропортов числовые, а не буквенные. Автор находит это запросом с `NOT SIMILAR TO '[A-Za-z]+'`. Урок: перед анализом проверьте формат ключей.

## Что автор делает в Python

- Рисует карты через `folium`.
- Строит pie и bar chart через `matplotlib`.
- Превращает результат в `pandas DataFrame` через `.df()` и применяет `pivot()`.

Совет автора для pie chart: оставляйте топ-10, иначе диаграмма нечитаема. Для сравнения долей лучше bar chart.

## Ключевые термины

| Термин | Значение |
|---|---|
| EDA | Первый разведочный анализ данных |
| `spatial` | Расширение DuckDB для геоданных |
| WKT | Текстовый формат геометрии, например `POINT (-80.29 25.79)` |
| `ST_Distance` | Расстояние между двумя геометриями |
| `ST_DWithin` | Проверка «в пределах расстояния» |
| `CTE` | `WITH`-запрос, временная именованная таблица внутри запроса |
| Pivot | Разворот строк в столбцы |

## Что это значит на практике

- Начинайте новый источник с `count`, `min`, `max`, числа `NULL` и проверки формата ключей.
- Сравнивайте группы по доле, а не по числу строк.
- Для «топ N ближайших» берите расстояние и `ORDER BY ... LIMIT N`. Не нужен сложный GIS.
- Исключайте отменённые и тестовые записи явно, в `WHERE`. Пишите это в комментарии.
- Тяжёлые агрегаты по большому CSV или Parquet работают локально и быстро. Хранилище для первого взгляда не нужно.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Данные придуманы, файлы скачивать не нужно.

### Шаг 1. Создаём аэропорты и рейсы

```sql
CREATE TABLE airports AS
SELECT * FROM (VALUES
    ('MIA', 'Майами',     'FL', 25.79, -80.29),
    ('FLL', 'Форт-Лодердейл', 'FL', 26.07, -80.15),
    ('PBI', 'Палм-Бич',   'FL', 26.68, -80.10),
    ('ORL', 'Орландо',    'FL', 28.43, -81.31),
    ('JFK', 'Нью-Йорк',   'NY', 40.64, -73.78),
    ('LAX', 'Лос-Анджелес', 'CA', 33.94, -118.41)
) t(iata, city, state, lat, lng);

CREATE TABLE airlines AS
SELECT * FROM (VALUES
    ('AA', 'Альфа Эйр'),
    ('BB', 'Бета Лайнс'),
    ('CC', 'Гамма Джет')
) t(iata, airline);

-- 600 рейсов, фиксированный шаблон без случайных чисел
CREATE TABLE flights AS
SELECT
    i AS flight_id,
    CASE i % 3 WHEN 0 THEN 'AA' WHEN 1 THEN 'BB' ELSE 'CC' END AS airline,
    ['FLL', 'JFK', 'LAX', 'MIA', 'ORL', 'PBI'][1 + i % 6] AS origin,
    ['FLL', 'JFK', 'LAX', 'MIA', 'ORL', 'PBI'][1 + (i % 6 + 1 + (i // 6) % 5) % 6] AS destination,
    1 + (i % 7) AS day_of_week,
    (i * 37) % 24 AS dep_hour,
    CASE WHEN i % 25 = 0 THEN 1 ELSE 0 END AS cancelled,
    (i * 13) % 60 - 15 AS arrival_delay
FROM range(0, 600) t(i);
```

### Шаг 2. Проверяем

```sql
-- рейс не должен лететь сам в себя: ожидаем 0 строк
SELECT count(*) AS bad_routes FROM flights WHERE origin = destination;

SELECT count(*) AS flights_total, sum(cancelled) AS cancelled_total FROM flights;
```

### Шаг 3. Расстояния и ближайшие аэропорты

```sql
INSTALL spatial;
LOAD spatial;

CREATE TABLE airports_geo AS
SELECT *, ST_Point(lng, lat) AS geom FROM airports;

-- три ближайших к точке в центре Майами
SELECT iata, city,
       round(ST_Distance(geom, ST_Point(-80.19, 25.77)), 3) AS dist_deg
FROM airports_geo
ORDER BY dist_deg
LIMIT 3;
```

### Задания

**1.** Посчитайте долю отмен по каждой авиакомпании с её названием. Покажите от большей к меньшей.

<details>
<summary>Решение</summary>

```sql
SELECT a.airline,
       round(sum(f.cancelled) * 100.0 / count(*), 2) AS cancelled_pct
FROM flights f
JOIN airlines a ON f.airline = a.iata
GROUP BY a.airline
ORDER BY cancelled_pct DESC;
```

Каждый 25-й рейс отменён, поэтому у всех трёх компаний доля 4%. `JOIN` нужен только для названия.
</details>

**2.** Найдите аэропорты, которые лежат не дальше 1 градуса от Майами (`-80.29, 25.79`).

<details>
<summary>Решение</summary>

```sql
SELECT iata, city
FROM airports_geo
WHERE ST_DWithin(geom, ST_Point(-80.29, 25.79), 1)
ORDER BY iata;
```

В радиус попадают MIA, FLL и PBI. Орландо дальше.
</details>

**3.** Разбейте день на четыре слота по 6 часов. Для каждого слота найдите среднюю задержку прибытия только по неотменённым рейсам.

<details>
<summary>Решение</summary>

```sql
SELECT
    CASE WHEN dep_hour < 6  THEN '00-06'
         WHEN dep_hour < 12 THEN '06-12'
         WHEN dep_hour < 18 THEN '12-18'
         ELSE '18-24' END AS slot,
    round(avg(arrival_delay), 1) AS avg_delay
FROM flights
WHERE cancelled = 0
GROUP BY slot
ORDER BY slot;
```

Поле `cancelled = 0` убирает отмены. Без этого фильтра среднее было бы искажено.
</details>

**4.** Для каждой пары (`origin`, `destination`) посчитайте долю рейсов по дням недели. Покажите первые 5 строк.

<details>
<summary>Решение</summary>

```sql
WITH per_day AS (
    SELECT origin, destination, day_of_week, count(*) AS n_day
    FROM flights WHERE cancelled = 0
    GROUP BY ALL
), per_route AS (
    SELECT origin, destination, count(*) AS n_total
    FROM flights WHERE cancelled = 0
    GROUP BY ALL
)
SELECT d.origin, d.destination, d.day_of_week,
       round(100.0 * d.n_day / r.n_total, 1) AS pct
FROM per_day d
JOIN per_route r USING (origin, destination)
ORDER BY d.origin, d.destination, d.day_of_week
LIMIT 5;
```

Два `CTE` дают числитель и знаменатель. Так же считает автор книги.
</details>

## Вопросы для самопроверки

1. Почему для сравнения авиакомпаний нужна доля задержек, а не их число?
2. В каком порядке `ST_Point` принимает координаты? К чему приводит ошибка?
3. Чем `ST_DWithin` отличается от `ST_Distance` + `LIMIT`? Когда нужен каждый?
4. Зачем автор проверяет формат кодов аэропортов перед анализом?

Предыдущая: [Глава 4. DuckDB и Polars](/book-summaries/engineering/duckdb-up-and-running/04-polars/). Следующая: [Глава 6. JSON](/book-summaries/engineering/duckdb-up-and-running/06-json/).
