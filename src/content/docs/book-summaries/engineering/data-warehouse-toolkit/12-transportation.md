---
title: "The Data Warehouse Toolkit, глава 12: Транспорт"
head:
  - tag: title
    content: "Моделирование авиаперелётов: Kimball, grain | Инжиниринг Данных"
description: "Конспект главы 12 The Data Warehouse Toolkit: модель авиакомпании, fact-таблицы разного grain, role-playing dimensions, часовые пояса. Практика в DuckDB."
sidebar:
  order: 12
  label: "12. Транспорт"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** у одного бизнес-процесса может быть несколько fact-таблиц с разным `grain`. В авиакомпании это `leg`, `segment`, `trip` и `itinerary`. Книга советует начать с `segment`: это самый детальный уровень, где уже есть осмысленные деньги.

## О чём глава

В [главе 11](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/) мы проверяли готовый черновик биллинга. Здесь мы снова строим модель с нуля. Тема — путешествия (`voyage`): человек или груз едут из точки A в точку B, иногда с остановками. Авторы берут авиакомпанию, потому что она знакома почти всем. Похожие схемы подходят для грузоперевозок, проката машин и даже для маршрутов звонков в телекоме.

- fact-таблицы разного `grain` и связь segments с trips;
- грузоперевозки и travel services;
- объединение связанных dimensions;
- календари стран и часовые пояса;
- обзор локализации.

![Star schema сегмента рейса с ролями дат и аэропортов](/assets/data-warehouse-toolkit/ch12-flight-segment-star.png)

Схема показывает fact с одной строкой на `segment` пассажира и dimensions вокруг неё. Она упрощена: нет самолёта, канала продажи и времени суток.

## Airline case study и bus matrix

Авторы начинают с упрощённой `bus matrix` авиакомпании. В строках бизнес-процессы: бронирования, выписанные билеты, полёты (`flight activity`), начисление миль, обращения в поддержку, ремонт, планирование экипажей. В столбцах общие dimensions: дата, аэропорт, пассажир, класс обслуживания, `fare basis` (условия тарифа) и другие. Ещё один столбец отведён под `degenerate dimension`, например номер билета.

Продажа билета даёт `unearned revenue`: деньги получены, но ещё не заработаны. Авиакомпания зарабатывает их, когда пассажир летит. Для первой поставки выбрали процесс `flight activity`. Маркетинг хочет знать, какими рейсами и тарифами летают участники программы лояльности (`frequent flyers`), как часто они повышают класс, как тратят мили и какой у них статус. Брони, после которых пассажир не сел в самолёт, отложили на следующие фазы.

### Fact-таблицы разного grain

У авиакомпании есть четыре уровня, и у каждого свои метрики и пользователи.

| Уровень | Что это | Что на нём считают |
|---|---|---|
| `Leg` | Один взлёт и одна посадка | Длительность полёта, опоздания, загрузка кресел |
| `Segment` | Один flight number на одном самолёте. Строка в купоне билета | Выручка и мили |
| `Trip` | Путь пассажира из A в B, возможно с пересадками | Спрос клиентов |
| `Itinerary` | Весь билет или номер подтверждения брони | Данные тоже собирают |

Пример: перелёт SFO–MSP с остановкой в Денвере (DEN). Если рейс и самолёт не меняются, это один `segment` и два `leg` (SFO–DEN, DEN–MSP). Если в Денвере пересадка на другой самолёт, это один `trip` и два `segment`. Пассажир хотел попасть в Миннеаполис, остановка для него вынужденная.

![Уровни grain перелёта и их fact-таблицы](/assets/data-warehouse-toolkit/ch12-flight-grains.png)

**Выбор grain.** Команда начала с `segment`: это самый низкий уровень с осмысленной выручкой. Другой путь — получить от бизнеса правила, как раскладывать метрики segment на `leg`. Данные по `leg` добавят позже на тех же conformed dimensions. Одна строка fact — один посадочный талон. Даты, времена и аэропорты в схеме — это `view` на одну физическую таблицу (как в [главе 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)).

**Dimensions и facts.**

- Дата и время суток (плановый и фактический вылет), аэропорт вылета и прилёта: у каждой по две роли.
- Пассажир: обычная customer dimension. Клиенты сами следят за её точностью: им важны мили. У крупной авиакомпании в ней десятки и сотни миллионов строк.
- Самолёт, класс обслуживания в полёте, `fare basis` и канал продажи. Канал относится ко всему билету, но каждый `segment` наследует его.
- Degenerate dimensions: номер брони, билета, рейса и порядковый номер `segment`.
- Facts: базовый тариф, сборы и налоги, мили налёта и начисленные мили. Начисленные мили отличаются от налёта, если авиакомпания даёт минимум миль независимо от расстояния.

**Passenger profile как mini-dimension.** Маркетингу нужен анализ по уровню `frequent flyer`, домашнему аэропорту, членству в клубе и уровню накопленных миль. Эти атрибуты меняются не быстро, и авторы думали о `SCD type 2`. Но пассажиров слишком много, поэтому выбрали `type 4`: отдельная `mini-dimension` с одной строкой на каждую комбинацию четырёх атрибутов (см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)). Аналитики часто работают только с ней и не трогают миллионы строк passenger.

### Связываем segments в trips

Схема не отвечает на вопрос «Куда летят клиенты?». Segments билета, даже отсортированные, не показывают начало и конец поездки. Искать пункт назначения по длинной остановке в BI-слое слишком сложно.

Решение: добавить в fact два role-playing аэропорта, `trip origin` и `trip destination`, и оставить grain `segment`. ETL находит их при загрузке: ищет в билете остановку дольше четырёх часов, так авиакомпания определяет `stopover`. Часть dimensions не применима к поездке целиком, например `fare basis` и класс обслуживания.

Если пользователи постоянно смотрят данные по trip, можно построить aggregate fact table на grain trip с суммами по поездке и числом segments. Книга советует делать это, только если отчёты по segment явно тормозят. При трёх segments в поездке ускорение будет примерно в три раза, и это может не окупить работу.

### Связанные fact-таблицы

Для операций вылета и прилёта строят fact-таблицу на grain `leg`: длительность полёта, опоздания, вес топлива. Ещё нужны fact-таблицы бронирований и выписанных билетов. Для выручки полезен snapshot по рейсу за 90 дней до вылета: накопленная незаработанная выручка и оставшиеся места по классам. Dimension «дни до вылета» позволяет сравнивать похожие рейсы на одном этапе, например за 60 дней.

## Другие отрасли

Схема `voyage` подходит не только авиакомпаниям. Книга разбирает две другие отрасли.

### Cargo shipper: грузоперевозчик

Морская компания возит контейнеры из иностранных портов в свои. По пути бывают остановки, перегрузка с судна на судно, иногда leg идёт грузовиком. Grain fact: контейнер по номеру коносамента (`bill-of-lading`) на одном leg. Вокруг стоят dimensions судна, контейнера и товара. У товара есть гармонизированные коды: это главная conformed dimension, её используют госорганы. Одна `business entity` играет семь ролей: shipper, consignee, transporter и другие. Порты и даты тоже в нескольких ролях. Номер коносамента — `degenerate dimension`. Сборы, тарифы и мили относятся к отдельному leg.

### Travel services

Турагентство добавляет к полётам fact-таблицы отелей и проката машин. У них общие dimensions, например дата и клиент. Grain отеля — всё проживание, grain проката — вся аренда. У отеля три роли даты: бронирование, заезд, выезд.

## Combining correlated dimensions: объединяем связанные dimensions

Обычно связанные группы атрибутов держат в отдельных dimensions с отдельными foreign key. Иногда их выгодно слить в одну. Авторы называют это исключением.

### Class of service

Пользователи хотят видеть купленный класс и фильтровать повышения и понижения. Первая мысль — вторая роль для класса и третий ключ для индикатора upgrade. Но в dimension класса четыре строки, в индикаторе три (upgrade, downgrade, no class change). Поэтому авторы сливают их в одну dimension: 4 × 4 = 16 строк.

| class_purchased | class_flown | class_change_indicator |
|---|---|---|
| Economy | Business | Upgrade |
| Business | Economy | Downgrade |

Это вид `junk dimension` (одна таблица для мелких связанных атрибутов, см. [главу 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). Правило книги: обычно role-playing dimensions остаются отдельными логическими dimensions на одной таблице. Сливают их, когда строк очень мало или нужны атрибуты комбинации ролей.

### Origin и destination: маршрут (city pair)

Здесь данных больше, поэтому аэропорты вылета и прилёта остаются отдельными. Но бизнесу нужны атрибуты пары: расстояние и тип (внутренний или трансатлантический). Вопрос «сколько рейсов между SFO и DEN в обе стороны» с двумя dimensions задать непросто. К тому же нет стандартного имени маршрута: одно приложение напишет SFO-DEN, другое DEN-SFO. Авторы советуют хранить метки в dimension, а не в коде BI.

Есть два варианта. Первый: добавить в fact dimension `city pair route` с именем с направлением (BOS-JFK), именем без направления (JFK-BOS тоже даёт BOS-JFK), расстоянием, группой расстояния и признаками внутреннего и океанского маршрута. Второй: слить аэропорты вылета и прилёта с маршрутом в одну dimension. Но у каждого аэропорта десятки атрибутов, поэтому авторы склоняются к первому. `Bridge table` здесь не нужна: связь many-to-many чисто выражена в fact.

## Ещё о датах и времени

С первых глав книга требует подробную date dimension. Здесь добавляются две темы.

### Country-specific calendars как outriggers

Основная date dimension хранит общие атрибуты календаря. Если бизнес живёт по нескольким календарям, в ней несколько наборов дней, месяцев и лет. Атрибуты страны (названия праздников и сезонов) выносят в дополнительную dimension с ключом «дата + код страны». Её присоединяют как `outrigger` (dimension, подключённая к другой dimension) или прямо к fact. Это похоже на несколько финансовых календарей из [главы 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/). Такие календари сложно строить, особенно когда местные праздники в разных частях страны разные.

### Дата и время в нескольких часовых поясах

Нужно хранить и стандартное время (UTC), и локальное. Стандартное показывает, какие события произошли одновременно. Локальное показывает время суток события. Часовых поясов больше 24: в Индии один пояс со сдвигом 5,5 часа, в Непале сдвиг в четверть часа. Есть и летнее время.

Поэтому одного сдвига от UTC в fact мало. Его нельзя положить и в dimension аэропорта: сдвиг зависит и от места, и от даты. Книга рекомендует отдельные date и time-of-day dimensions для локального и стандартного времени. В fact четыре ключа, по две роли у каждой dimension. Time-of-day dimension группирует время по сменам и периодам пик (см. [главу 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/)).

> **Пояснение:** в практике ниже вместо time-of-day dimension мы храним полные timestamp, локальный и UTC.

## Localization recap: обзор локализации

Часовые пояса и календари разобраны здесь, мультивалютность — в [главе 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/), языки — в [главе 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/). Всё это называют локализацией. В широком смысле она включает и перевод интерфейса BI-инструментов. Европейские переводы длиннее английского текста, арабский читают справа налево, поэтому приложение приходится перерисовывать. Авторы советуют заранее выбрать набор проблем локализации и учесть его в дизайне.

## Итоги главы

- У одного процесса может быть несколько fact-таблиц с разным `grain`: `leg`, `segment`, `trip`, `itinerary`.
- Книга начинает с `segment`: это самый детальный уровень с осмысленной выручкой.
- Даты, времена и аэропорты в схеме `segment` — это `view` на одну физическую таблицу (role playing).
- Профиль пассажира выносят в `mini-dimension` (`type 4`): пассажиров слишком много для `SCD type 2`.
- Чтобы узнать, куда летят клиенты, в fact добавляют `trip origin` и `trip destination`. Aggregate на grain `trip` нужен только при явных проблемах с производительностью.
- Связанные dimensions сливают как исключение: когда строк очень мало (4 × 4 = 16) или нужны атрибуты комбинации (маршрут).
- Календарь страны — `outrigger` к date dimension.
- Время хранят и локальное, и стандартное: сдвиг от UTC зависит от места и даты.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Segment` | Один flight number на одном самолёте. Строка в купоне билета |
| `Leg` | Один взлёт и одна посадка |
| `Trip origin` / `trip destination` | Начало и конец поездки. Role-playing аэропорты в fact |
| `Role-playing dimension` | Одна физическая dimension в нескольких ролях через разные foreign key |
| `Mini-dimension` | Маленькая dimension для меняющихся атрибутов (`type 4`) |
| `Junk dimension` | Одна dimension для мелких связанных атрибутов |
| `Outrigger` | Dimension, подключённая к другой dimension |
| `Equivalized time` | Время в одном стандарте, например UTC |

## Что это значит на практике

- Пишите grain одной фразой для каждой fact-таблицы. Не смешивайте facts разных уровней: мили segment и опоздание leg живут в разных таблицах.
- Не соединяйте fact-таблицы разного grain напрямую. Агрегируйте каждую до общего уровня (`drill across`, см. [главу 2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/)). Иначе суммы задвоятся.
- `Trip origin` и `trip destination` считайте в ETL по правилу бизнеса (например, остановка дольше четырёх часов), а не в BI.
- Aggregate на grain `trip` стройте после замера, а не заранее.
- Для каждой роли dimension делайте `view` с переименованными колонками. В `dbt` это отдельные модели-view или `ref('dim_airport')` с разными псевдонимами.
- Храните время дважды: UTC и локальное. Часовой пояс аэропорта храните именем (`America/Denver`), а не смещением.
- Сливайте dimensions, только если они совсем маленькие или нужны атрибуты комбинации. Названия маршрутов храните в dimension, а не в коде BI.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_airport AS
SELECT * FROM (VALUES
    (1, 'ATL', 'Атланта',        'US', 'America/New_York'),
    (2, 'BOS', 'Бостон',         'US', 'America/New_York'),
    (3, 'DEN', 'Денвер',         'US', 'America/Denver'),
    (4, 'SFO', 'Сан-Франциско',  'US', 'America/Los_Angeles'),
    (5, 'MSP', 'Миннеаполис',    'US', 'America/Chicago'),
    (6, 'LGW', 'Лондон',         'UK', 'Europe/London')
) t(airport_key, airport_code, city, country, time_zone);
-- в dimension хранится имя часового пояса, а не смещение:
-- смещение зависит и от места, и от даты (летнее время)

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
-- UTC считает ETL по поясу аэропорта и дате вылета. timezone() учитывает летнее время
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
    strftime(timezone('UTC', timezone(o.time_zone, s.dep_local_ts)), '%Y%m%d')::INT AS dep_utc_date_key,
    s.dep_local_ts,
    timezone('UTC', timezone(o.time_zone, s.dep_local_ts)) AS dep_utc_ts,
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

-- смещение от UTC у одного аэропорта меняется: 9 марта 2025 в США перешли на летнее время
SELECT a.airport_code, f.dep_local_ts, f.dep_utc_ts,
       date_diff('hour', f.dep_utc_ts, f.dep_local_ts) AS utc_offset_hours
FROM fact_segment_flight f
JOIN dim_airport a ON a.airport_key = f.origin_airport_key
WHERE a.airport_code IN ('SFO', 'DEN')
ORDER BY a.airport_code, f.dep_local_ts;
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

1. Чем `segment` отличается от `leg` и от `trip`? Приведите пример из одного перелёта.
2. Почему команда начала с `segment`, а не с `leg`?
3. Как `trip origin` и `trip destination` помогают узнать, куда летят клиенты? Когда стоит строить aggregate на grain `trip`?
4. Когда можно слить две dimensions в одну, как class of service? Почему аэропорты вылета и прилёта оставили отдельными?
5. Зачем хранить названия маршрутов в dimension, а не считать их в BI?
6. Почему сдвиг от UTC нельзя хранить ни в fact, ни в dimension аэропорта?

Предыдущая: [Глава 11. Телеком](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/). Следующая: [Глава 13. Образование](/book-summaries/engineering/data-warehouse-toolkit/13-education/).
