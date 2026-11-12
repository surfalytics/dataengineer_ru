---
title: "The Data Warehouse Toolkit, глава 12: Транспорт"
head:
  - tag: title
    content: "Моделирование авиаперелётов: Kimball, grain | Инжиниринг Данных"
description: "Конспект главы 12 The Data Warehouse Toolkit. Несколько fact-таблиц разного grain, role-playing dimensions, часовые пояса и практика в DuckDB."
sidebar:
  order: 12
  label: "12. Транспорт"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** у одного процесса может быть несколько grain. Для авиакомпании это leg, segment, trip и itinerary. Выбирайте самый детальный grain, у которого есть осмысленные деньги. Остальные уровни получайте через dimensions или отдельные fact-таблицы.

Схема подходит не только авиакомпаниям. Так же устроены грузовые перевозки, прокат машин, путешествия и телеком-маршруты.

![Star schema сегмента рейса: fact-таблица и dimensions с ролями дат и аэропортов](/assets/data-warehouse-toolkit/ch12-flight-segment-star.png)

## Четыре уровня grain

У перелёта есть вложенные уровни. Каждый нужен своей группе пользователей.

| Уровень | Что это | Кто использует |
|---|---|---|
| Leg | Один взлёт и одна посадка | Операции, расписание, загрузка кресел |
| Segment | Один flight number на одном самолёте. Строка в билете | Маркетинг и выручка, мили |
| Trip | Поездка из A в B, возможно с пересадками | Продажи, анализ спроса |
| Itinerary | Весь билет или номер бронирования | Клиентский сервис |

Пример. Рейс SFO → DEN → MSP без смены самолёта: это один segment и два leg. Если в Денвере пассажир меняет самолёт, это уже два segment, но одна trip.

![Уровни grain перелёта: itinerary, trip, segment, leg и их fact-таблицы](/assets/data-warehouse-toolkit/ch12-flight-grains.png)

## Какой grain выбрать

Книга начинает с segment. Одна строка — один посадочный талон. Причины:

- На уровне segment уже есть выручка: тариф, налоги, сборы, мили.
- Leg можно добавить позже. Dimensions уже будут conformed.
- Trip считать из segment сложно. Для этого есть приём ниже.

Нельзя смешивать уровни в одной таблице. Мили сегмента и задержка leg живут в разных fact-таблицах.

## Trip origin и trip destination

Из списка segment трудно понять, куда летел клиент. Сегмент BOS → ATL и ATL → DEN — это одна поездка BOS → DEN.

Решение: оставить grain segment и добавить ещё два role-playing airport. Это `trip_origin` и `trip_destination`. Их считает ETL. Правило из книги: остановка дольше четырёх часов — конец поездки.

- Запрос «куда летают клиенты» становится простым `GROUP BY`.
- Не все dimensions имеют смысл на уровне trip. Класс обслуживания у поездки может быть разным по segment.
- Если trip-отчёты тормозят, строят aggregate на grain trip. Это нужно не всегда. Три segment в поездке дают выигрыш примерно в три раза.

## Role-playing dimensions

Один физический `dim_airport` играет несколько ролей. Каждая роль — отдельный foreign key в fact.

| Роль | Что значит |
|---|---|
| Origin airport | Откуда вылетел segment |
| Destination airport | Куда прилетел segment |
| Trip origin | Откуда началась поездка |
| Trip destination | Куда поездка закончилась |

То же с датами: плановая и фактическая дата вылета, локальная и UTC. В BI-слое для каждой роли делают `view` с переименованными колонками. Тогда пользователь видит `origin_city`, а не два одинаковых `city`.

## Объединение связанных dimensions

Обычно две независимые dimensions держат отдельно. Но есть исключения.

### Class of service

Бизнес хочет знать купленный класс и класс полёта. Ещё нужен признак upgrade или downgrade. Классов всего четыре. Их комбинаций 4 × 4 = 16 строк. Поэтому делают одну dimension `class_of_service` с полями:

- `class_purchased`
- `class_flown`
- `class_change_indicator` (Upgrade, Downgrade, No Class Change)

Это похоже на `junk dimension`. Правило upgrade хранится в одном месте, а не в каждом отчёте.

### City pair

Вопрос «сколько пассажиров между SFO и DEN в обе стороны» трудно задать с двумя airport dimensions. Нужно общее название маршрута. Решение: dimension `route` с атрибутами:

- направленное имя (`SFO-DEN`);
- ненаправленное имя (`DEN-SFO` и `SFO-DEN` оба дают `DEN-SFO`);
- расстояние и группа расстояния;
- домашний или международный маршрут.

Метки маршрутов лежат в dimension. Тогда все отчёты показывают одно и то же имя. Bridge table для origin и destination не нужна.

## Mini-dimension для профиля пассажира

Таблица пассажиров очень большая. Статус frequent flyer, домашний аэропорт, членство в клубе и накопленные мили меняются. Хранить их как SCD type 2 дорого.

Решение: `passenger_profile` — это type 4 `mini-dimension`. В ней одна строка на каждую комбинацию значений. В fact есть отдельный ключ профиля. Статус на момент полёта сохраняется без роста основной dimension.

## Даты и время

| Тема | Решение |
|---|---|
| Несколько часовых поясов | Два набора ключей: локальное время и UTC (equivalized). Смещение зависит от места и даты, поэтому его нельзя хранить только в dimension |
| Разные календари стран | Основная `dim_date` плюс outrigger с атрибутами страны: праздники, сезон, название |
| Время суток | Отдельная dimension `time_of_day` или полный timestamp в fact, если нужна арифметика |

## Другие отрасли

| Отрасль | Grain | Особенность |
|---|---|---|
| Грузовые перевозки | Контейнер на одном leg по bill-of-lading | Одна `business_entity` играет 7 ролей: shipper, consignee и другие |
| Гостиницы и прокат машин (travel services) | Весь отдых или вся аренда | Общие dimensions: дата и клиент |
| Телеком | Звонок от номера A к номеру B | Маршрут сети похож на voyage |

## Ключевые термины

| Термин | Значение |
|---|---|
| Leg | Один взлёт и одна посадка |
| Segment | Один flight number на одном самолёте |
| Trip | Поездка от начала до цели |
| Itinerary | Весь билет |
| Role-playing dimension | Одна таблица, несколько ролей через разные foreign key |
| Mini-dimension | Быстро меняющиеся атрибуты в отдельной маленькой таблице (type 4) |
| Junk dimension | Одна таблица для связанных флагов и малых dimensions |
| Equivalized time | Время в одном стандартном часовом поясе, например UTC |

## Что это значит на практике

- Пишите grain одной фразой для каждой fact-таблицы. «Один segment на посадочный талон».
- Не соединяйте две fact-таблицы разного grain напрямую. Сначала агрегируйте каждую до общего уровня (`drill across`). Иначе суммы задвоятся.
- В `dbt` role-playing — это несколько `ref('dim_airport')` с разными псевдонимами или отдельные модели-view.
- Храните время дважды: UTC и локальное. UTC нужен для сравнения событий. Локальное — для вопросов «утром или вечером».
- Маленькие связанные dimensions (4 × 4 строки) можно слить. Большие нельзя.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_airport AS
SELECT * FROM (VALUES
    (1, 'ATL', 'Атланта',        'US', -5),
    (2, 'BOS', 'Бостон',         'US', -5),
    (3, 'DEN', 'Денвер',         'US', -7),
    (4, 'SFO', 'Сан-Франциско',  'US', -8),
    (5, 'MSP', 'Миннеаполис',    'US', -6),
    (6, 'LGW', 'Лондон',         'UK',  0)
) t(airport_key, airport_code, city, country, utc_offset_hours);

-- role-playing: два view на одну физическую таблицу
CREATE VIEW dim_origin_airport AS
SELECT airport_key AS origin_airport_key, airport_code AS origin_code, city AS origin_city
FROM dim_airport;

CREATE VIEW dim_destination_airport AS
SELECT airport_key AS destination_airport_key, airport_code AS destination_code, city AS destination_city
FROM dim_airport;

-- объединённая dimension: 4 x 4 = 16 строк
CREATE TABLE dim_class_of_service AS
WITH c(class_name, class_rank) AS (
    VALUES ('Economy', 1), ('Premium Economy', 2), ('Business', 3), ('First', 4)
)
SELECT
    row_number() OVER (ORDER BY p.class_rank, f.class_rank) AS class_of_service_key,
    p.class_name AS class_purchased,
    f.class_name AS class_flown,
    CASE WHEN f.class_rank > p.class_rank THEN 'Upgrade'
         WHEN f.class_rank < p.class_rank THEN 'Downgrade'
         ELSE 'No Class Change' END AS class_change_indicator
FROM c p CROSS JOIN c f;

-- dimension маршрутов (city pair)
CREATE TABLE dim_route AS
SELECT
    row_number() OVER (ORDER BY o.airport_code, d.airport_code) AS route_key,
    o.airport_code || '-' || d.airport_code AS directional_route_name,
    least(o.airport_code, d.airport_code) || '-' || greatest(o.airport_code, d.airport_code) AS non_directional_route_name,
    CASE WHEN o.country = d.country THEN 'Domestic' ELSE 'International' END AS route_type
FROM dim_airport o
JOIN dim_airport d ON o.airport_key <> d.airport_key;

-- источник: один segment = одна строка
CREATE TABLE stg_segment AS
SELECT * FROM (VALUES
    ('T1', 1, 1, 'AB10', 'SFO', 'MSP', 'Economy',         'Economy',         310, 1589, TIMESTAMP '2025-03-03 08:15:00'),
    ('T1', 2, 2, 'AB11', 'MSP', 'SFO', 'Economy',         'Economy',         290, 1589, TIMESTAMP '2025-03-07 18:40:00'),
    ('T2', 1, 1, 'AB20', 'BOS', 'ATL', 'Economy',         'Business',        300,  946, TIMESTAMP '2025-03-04 07:00:00'),
    ('T2', 1, 2, 'AB21', 'ATL', 'DEN', 'Economy',         'Economy',         210, 1199, TIMESTAMP '2025-03-04 11:30:00'),
    ('T2', 2, 3, 'AB22', 'DEN', 'BOS', 'Economy',         'Economy',         380, 1754, TIMESTAMP '2025-03-09 13:00:00'),
    ('T3', 1, 1, 'AB30', 'DEN', 'SFO', 'Business',        'Business',        450,  967, TIMESTAMP '2025-03-05 20:30:00'),
    ('T4', 1, 1, 'AB40', 'BOS', 'LGW', 'Premium Economy', 'Business',        900, 3267, TIMESTAMP '2025-03-06 21:00:00'),
    ('T4', 2, 2, 'AB41', 'LGW', 'BOS', 'Premium Economy', 'Premium Economy', 850, 3267, TIMESTAMP '2025-03-12 10:00:00'),
    ('T5', 1, 1, 'AB50', 'SFO', 'DEN', 'Economy',         'Economy',         170,  967, TIMESTAMP '2025-03-10 09:00:00'),
    ('T6', 1, 1, 'AB60', 'DEN', 'SFO', 'First',           'Business',        700,  967, TIMESTAMP '2025-03-11 15:00:00'),
    ('T7', 1, 1, 'AB70', 'MSP', 'DEN', 'Economy',         'Economy',         140,  680, TIMESTAMP '2025-03-11 06:30:00'),
    ('T8', 1, 1, 'AB71', 'DEN', 'MSP', 'Economy',         'Economy',         150,  680, TIMESTAMP '2025-03-12 12:00:00')
) t(ticket_number, trip_no, segment_seq, flight_number, origin_code, dest_code,
    class_purchased, class_flown, base_fare, miles_flown, dep_local_ts);

-- grain: один segment (одна посадка пассажира)
-- trip origin и trip destination считает ETL: первый и последний segment поездки
CREATE TABLE fact_segment_flight AS
WITH s AS (
    SELECT *,
        first_value(origin_code) OVER (PARTITION BY ticket_number, trip_no ORDER BY segment_seq) AS trip_origin_code,
        last_value(dest_code)    OVER (PARTITION BY ticket_number, trip_no ORDER BY segment_seq
                                       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS trip_dest_code
    FROM stg_segment
)
SELECT
    strftime(s.dep_local_ts, '%Y%m%d')::INT AS dep_local_date_key,
    strftime(s.dep_local_ts - to_hours(o.utc_offset_hours), '%Y%m%d')::INT AS dep_utc_date_key,
    s.dep_local_ts,
    s.dep_local_ts - to_hours(o.utc_offset_hours) AS dep_utc_ts,
    o.airport_key   AS origin_airport_key,
    d.airport_key   AS destination_airport_key,
    tro.airport_key AS trip_origin_airport_key,
    trd.airport_key AS trip_destination_airport_key,
    r.route_key,
    cs.class_of_service_key,
    s.ticket_number, s.trip_no, s.segment_seq, s.flight_number,
    s.base_fare, s.miles_flown
FROM s
JOIN dim_airport o   ON o.airport_code   = s.origin_code
JOIN dim_airport d   ON d.airport_code   = s.dest_code
JOIN dim_airport tro ON tro.airport_code = s.trip_origin_code
JOIN dim_airport trd ON trd.airport_code = s.trip_dest_code
JOIN dim_route r     ON r.directional_route_name = s.origin_code || '-' || s.dest_code
JOIN dim_class_of_service cs ON cs.class_purchased = s.class_purchased AND cs.class_flown = s.class_flown;

-- grain: один leg. Рейс AB10 имеет два leg и один segment
CREATE TABLE fact_leg_flight AS
SELECT * FROM (VALUES
    ('AB10', 1, 'SFO', 'DEN', 967, 12),
    ('AB10', 2, 'DEN', 'MSP', 622,  0)
) t(flight_number, leg_seq, origin_code, dest_code, leg_miles, delay_minutes)
UNION ALL
SELECT flight_number, 1, origin_code, dest_code, miles_flown, (segment_seq * 7) % 20
FROM stg_segment
WHERE flight_number <> 'AB10';
```

### Шаг 2. Проверяем даты и сегменты

```sql
-- должно быть 12 segment. Столько же строк в источнике
SELECT count(*) AS segments, count(DISTINCT ticket_number) AS tickets FROM fact_segment_flight;

-- вечерний вылет с запада это уже следующий день по UTC
SELECT ticket_number, flight_number, dep_local_ts, dep_utc_ts
FROM fact_segment_flight
WHERE dep_local_date_key <> dep_utc_date_key
ORDER BY dep_local_ts;
```

### Задания

**1.** Выручка по городам вылета и прилёта. Подключите две role-playing dimensions.

<details>
<summary>Решение</summary>

```sql
SELECT o.origin_city, d.destination_city,
       count(*)         AS segments,
       sum(f.base_fare) AS revenue
FROM fact_segment_flight f
JOIN dim_origin_airport o USING (origin_airport_key)
JOIN dim_destination_airport d USING (destination_airport_key)
GROUP BY ALL
ORDER BY revenue DESC;
```
</details>

**2.** Куда летают клиенты? Покажите выручку и число segment по поездкам (trip origin и trip destination). Для поездок с пересадкой должно быть больше одного segment.

<details>
<summary>Решение</summary>

```sql
WITH trips AS (
    SELECT ticket_number, trip_no,
           trip_origin_airport_key, trip_destination_airport_key,
           count(*)         AS segments,
           sum(base_fare)   AS trip_fare
    FROM fact_segment_flight
    GROUP BY ALL
)
SELECT o.airport_code || ' -> ' || d.airport_code AS trip_route,
       count(*)           AS trips,
       sum(t.segments)    AS segments,
       sum(t.trip_fare)   AS revenue
FROM trips t
JOIN dim_airport o ON o.airport_key = t.trip_origin_airport_key
JOIN dim_airport d ON d.airport_key = t.trip_destination_airport_key
GROUP BY ALL
ORDER BY segments DESC, revenue DESC;
```

Поездка BOS -> DEN состоит из двух segment (через ATL). Это то, что скрывает segment grain.
</details>

**3.** Upgrade и downgrade. Посчитайте segment и выручку по `class_change_indicator`. Не пишите `CASE` в запросе.

<details>
<summary>Решение</summary>

```sql
SELECT c.class_change_indicator,
       count(*)         AS segments,
       sum(f.base_fare) AS revenue
FROM fact_segment_flight f
JOIN dim_class_of_service c USING (class_of_service_key)
GROUP BY c.class_change_indicator
ORDER BY segments DESC;
```
</details>

**4.** Маршруты в обе стороны. Сколько segment и какие мили на ненаправленных маршрутах? SFO-DEN и DEN-SFO должны слиться.

<details>
<summary>Решение</summary>

```sql
SELECT r.non_directional_route_name, r.route_type,
       count(*)              AS segments,
       sum(f.miles_flown)    AS miles
FROM fact_segment_flight f
JOIN dim_route r USING (route_key)
GROUP BY ALL
ORDER BY segments DESC, r.non_directional_route_name;
```

Маршрут DEN-SFO набирает три segment: SFO → DEN один раз и DEN → SFO два раза.
</details>

**5.** Fan-out. Соедините segment и leg по `flight_number` и посмотрите на мили. Потом сделайте правильно: агрегируйте обе таблицы до рейса и только потом соединяйте.

<details>
<summary>Решение</summary>

```sql
-- неправильно: рейс AB10 имеет два leg, его мили считаются дважды
SELECT sum(f.miles_flown) AS miles_wrong
FROM fact_segment_flight f
JOIN fact_leg_flight l USING (flight_number);

-- правильно: drill across через общий уровень (рейс)
WITH seg AS (
    SELECT flight_number, sum(miles_flown) AS segment_miles, sum(base_fare) AS fare
    FROM fact_segment_flight GROUP BY flight_number
), leg AS (
    SELECT flight_number, count(*) AS legs, sum(delay_minutes) AS delay_minutes
    FROM fact_leg_flight GROUP BY flight_number
)
SELECT sum(seg.segment_miles) AS miles_right,
       sum(leg.delay_minutes) AS total_delay,
       max(leg.legs)          AS max_legs
FROM seg JOIN leg USING (flight_number);
```

Правильная сумма миль равна 17 872. Неправильная равна 19 461. Разница 1 589 — это мили рейса AB10, посчитанные второй раз.
</details>

## Вопросы для самопроверки

1. Чем segment отличается от leg и от trip? Приведите пример из одного перелёта.
2. Почему в fact segment-уровня добавляют trip origin и trip destination, а не строят отдельную таблицу?
3. Когда можно слить две dimensions в одну, как class of service?
4. Почему для времени хранят и локальное значение, и UTC?
