---
title: "The Data Warehouse Toolkit, глава 15: Электронная коммерция"
head:
  - tag: title
    content: "Clickstream и сессии: моделирование, Kimball | Инжиниринг Данных"
description: "Конспект главы 15 The Data Warehouse Toolkit. Clickstream, сессии, fact события страницы, step dimension, aggregates и практика в DuckDB."
sidebar:
  order: 15
  label: "15. Электронная коммерция"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** лог веб-сайта становится данными для анализа после трёх шагов. Нужно найти сессии, выбрать grain и добавить специальные dimensions: страница, событие, сессия, referrer, шаг. Две fact-таблицы (событие страницы и сессия) работают вместе.

![Star schema clickstream: fact события страницы и fact сессии с общими dimensions](/assets/data-warehouse-toolkit/ch15-clickstream-star.png)

## Откуда приходят данные

Сервер пишет строку на каждое действие (hit). Из лога нужно понять, как посетитель попал на сайт и что он делал.

Основные источники входа:

| Источник | Что видно в данных |
|---|---|
| Прямой заход, закладка | Нет referrer |
| Поисковая система | Referrer и поисковый запрос |
| Рекламная ссылка (clickthrough) | Referring site. Нужен для оплаты рекламы |
| Письмо | Параметры в URL |

## Как определить сессию

HTTP не знает про сессии. Их нужно восстановить. Способы:

| Способ | Надёжность | Проблема |
|---|---|---|
| Hits с одного IP подряд (пауза не более N минут) | Низкая | IP общий или меняется |
| Session cookie | Хорошая | Работает, пока открыт браузер |
| SSL | Средняя | Тяжело и пугает пользователя |
| Session ID в URL | Средняя | Ломается при сторонних ссылках |
| Persistent cookie | Лучшая | Пользователь может его удалить |

Самый надёжный способ — persistent cookie. Если его нет, применяют время: пауза дольше порога (обычно 30 минут) начинает новую сессию.

### Кто этот посетитель

Идентифицировать человека трудно:

- Посетители хотят быть анонимными.
- Cookie указывает на браузер, а не на человека.
- Один человек заходит с нескольких устройств.
- Если человек указал данные, они могут быть неверными.

## Новые dimensions

Большинство dimensions знакомые: дата, время, клиент, товар, акция. Для clickstream нужны ещё четыре.

| Dimension | Что описывает | Пример значений |
|---|---|---|
| Page | Тип страницы, а не каждый экземпляр | Главная, поиск, товар, корзина |
| Event | Что произошло на странице | Open page, click link, enter data |
| Session | Класс сессии целиком | Вид, контекст, успех или нет |
| Referrer | Как человек пришёл | Search engine, remote site, intra site |

- Динамические страницы группируют по функции. Строка на каждый показ создала бы огромную dimension.
- Session dimension описывает категорию сессий, а не каждую. Идентификатор сессии идёт в fact как degenerate dimension.
- Метки вида «новый клиент» или «собирается уйти» кладите в session dimension, а не в customer. Они меняются за минуты.

## Две fact-таблицы

### Fact на уровне сессии

Grain: одна завершённая сессия. Это сознательный отход от правила «самый детальный grain». Причина: размер. Сто миллионов показов страниц в день дают около 20 миллионов сессий.

| Часть | Что внутри |
|---|---|
| Dimensions | Дата и время (UTC и локальные), клиент, страница входа, session, referrer |
| Facts | Секунды сессии, число страниц, число заказов, штуки, сумма заказа |

Заметки:

- Время хранят два раза: UTC (чтобы синхронизировать серверы) и по часам клиента (чтобы увидеть утро или вечер). Обе роли — view на одну `dim_date`.
- Вместо time-of-day dimension используют полный timestamp. В нём нет описательных атрибутов, а арифметика нужна.
- Causal dimension (акция по товару) сюда не подходит. За одну сессию клиент видит много товаров.

### Fact на уровне события страницы

Grain: одно событие страницы в сессии. Мелкие события (картинки) отбрасывают.

| Часть | Что внутри |
|---|---|
| Dimensions | Дата, время, клиент, страница, event, session, session ID (DD), step, товар, referrer, акция |
| Facts | `page_seconds`, штуки, сумма заказа (часто 0 или `NULL`) |

Заметки:

- Fact огромен. Не агрегируйте его. Агрегат теряет dimensions и вопросы.
- `page_seconds` и `session_seconds` называют по-разному. Это не одно и то же, и их нельзя смешивать. Это пример conformed facts.
- Сумма заказа в таблице связывает выручку и поведение без join с другой большой таблицей.

## Step dimension

Step dimension говорит, какая это по счёту страница и сколько шагов осталось.

- `step_number` — шаг с начала.
- `steps_until_end` — шагов до конца.
- Подпоследовательности: вся сессия, покупка, отказ. Для каждой своя роль `step`.

Примеры запросов:

- Шаг 1 в успешной покупке даёт стартовую страницу пути к покупке.
- «Ноль шагов до конца» в сессии без покупки даёт последнюю страницу перед уходом. Это точка отказа.

## Aggregates

Многие вопросы читают миллионы строк. Например: визиты и выручка по месяцам и демографической группе. Для них строят aggregate.

- Строят из fact сессии. Группируют по месяцу, сегменту, странице входа, исходу.
- Размер падает до 1% или меньше.
- Dimensions у aggregate — сжатые версии (`shrunken`) исходных: месяц вместо дня, сегмент вместо клиента. Они conformed с полными.

## Google Analytics

GA — это внешнее хранилище. Код на каждой странице отправляет события в Google. Внутри доступны почти все данные главы, кроме личных данных (запрещено условиями сервиса). Его можно использовать как источник.

## Ключевые термины

| Термин | Значение |
|---|---|
| Clickstream | Поток действий посетителя на сайте |
| Hit | Одна строка лога |
| Session | Последовательность действий одного посетителя |
| Sessionization | Разбиение hits на сессии |
| Page dimension | Описание типа страницы |
| Referrer | Источник, с которого пришёл посетитель |
| Step dimension | Номер шага и число шагов до конца |
| Shrunken dimension | Conformed подмножество атрибутов исходной dimension |

## Что это значит на практике

- Сессии считаются в ETL один раз. Не вычисляйте их в каждом отчёте.
- Для sessionization используйте window functions: `lag`, `sum() OVER`. Порог (30 минут) держите в одном месте.
- Храните `page_seconds` для всех страниц, кроме последней. Для последней он `NULL`. Это честнее, чем ноль.
- В `dbt` держите две модели: `fct_page_events` (grain событие) и `fct_sessions` (grain сессия). Сессии строятся из событий.
- Сверяйте две таблицы: число сессий, сумма заказов и сумма `page_seconds` должны сходиться.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d::DATE AS full_date, dayname(d) AS day_name
FROM generate_series(DATE '2025-05-01', DATE '2025-05-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_page AS
SELECT * FROM (VALUES
    (1, 'Home',         'Static'),
    (2, 'Search',       'Dynamic'),
    (3, 'Product',      'Dynamic'),
    (4, 'Cart',         'Dynamic'),
    (5, 'Checkout',     'Dynamic'),
    (6, 'Confirmation', 'Dynamic')
) t(page_key, page_function, page_source);

CREATE TABLE dim_product AS
SELECT * FROM (VALUES
    (0, 'Not a product page'),
    (1, 'Ноутбук'),
    (2, 'Наушники'),
    (3, 'Рюкзак')
) t(product_key, product_name);

CREATE TABLE dim_referrer AS
SELECT * FROM (VALUES
    (0, 'Intra site'),
    (1, 'Search engine'),
    (2, 'Direct'),
    (3, 'Email campaign')
) t(referrer_key, referral_type);

CREATE TABLE dim_session_outcome AS
SELECT * FROM (VALUES (1, 'Purchase'), (2, 'Abandoned')) t(session_outcome_key, outcome);

-- сырой лог: один hit = одна строка
CREATE TABLE stg_hit AS
SELECT * FROM (VALUES
    ('V1', TIMESTAMP '2025-05-01 10:00:00', '/home',               'google', NULL),
    ('V1', TIMESTAMP '2025-05-01 10:00:40', '/search',             NULL,     NULL),
    ('V1', TIMESTAMP '2025-05-01 10:01:30', '/product/1',          NULL,     NULL),
    ('V1', TIMESTAMP '2025-05-01 10:03:00', '/cart',               NULL,     NULL),
    ('V1', TIMESTAMP '2025-05-01 10:03:50', '/checkout',           NULL,     NULL),
    ('V1', TIMESTAMP '2025-05-01 10:05:10', '/order-confirmation', NULL,     59.90),
    ('V1', TIMESTAMP '2025-05-01 15:30:00', '/home',               'direct', NULL),
    ('V1', TIMESTAMP '2025-05-01 15:30:30', '/product/2',          NULL,     NULL),
    ('V1', TIMESTAMP '2025-05-01 15:32:00', '/product/3',          NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-01 11:00:00', '/home',               'email',  NULL),
    ('V2', TIMESTAMP '2025-05-01 11:00:20', '/product/1',          NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-01 11:01:10', '/cart',               NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-01 11:02:00', '/checkout',           NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-03 08:00:00', '/home',               'email',  NULL),
    ('V2', TIMESTAMP '2025-05-03 08:00:30', '/product/1',          NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-03 08:01:20', '/cart',               NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-03 08:02:10', '/checkout',           NULL,     NULL),
    ('V2', TIMESTAMP '2025-05-03 08:03:00', '/order-confirmation', NULL,     59.90),
    ('V3', TIMESTAMP '2025-05-02 09:00:00', '/home',               'google', NULL),
    ('V3', TIMESTAMP '2025-05-02 09:00:30', '/search',             NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 09:01:00', '/product/2',          NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 09:02:30', '/product/1',          NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 09:03:10', '/cart',               NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 09:04:00', '/checkout',           NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 09:05:20', '/order-confirmation', NULL,    120.00),
    ('V3', TIMESTAMP '2025-05-02 20:00:00', '/home',               'direct', NULL),
    ('V3', TIMESTAMP '2025-05-02 20:00:50', '/search',             NULL,     NULL),
    ('V3', TIMESTAMP '2025-05-02 20:02:00', '/product/3',          NULL,     NULL),
    ('V4', TIMESTAMP '2025-05-02 12:00:00', '/home',               'google', NULL),
    ('V4', TIMESTAMP '2025-05-02 12:01:00', '/product/3',          NULL,     NULL),
    ('V4', TIMESTAMP '2025-05-02 12:02:00', '/cart',               NULL,     NULL)
) t(visitor_id, hit_ts, url, referrer, order_amount);

-- grain: одно событие страницы в сессии
-- сессия: пауза больше 30 минут начинает новую
CREATE TABLE fact_page_event AS
WITH flagged AS (
    SELECT *,
        CASE WHEN lag(hit_ts) OVER w IS NULL
                  OR hit_ts - lag(hit_ts) OVER w > INTERVAL 30 MINUTE
             THEN 1 ELSE 0 END AS new_session
    FROM stg_hit
    WINDOW w AS (PARTITION BY visitor_id ORDER BY hit_ts)
), sessions AS (
    SELECT *,
        visitor_id || '-' || sum(new_session) OVER (PARTITION BY visitor_id ORDER BY hit_ts) AS session_id
    FROM flagged
), numbered AS (
    SELECT *,
        row_number() OVER (PARTITION BY session_id ORDER BY hit_ts) AS step_number,
        count(*)     OVER (PARTITION BY session_id)                 AS session_events,
        date_diff('second', hit_ts, lead(hit_ts) OVER (PARTITION BY session_id ORDER BY hit_ts)) AS page_seconds,
        bool_or(url = '/order-confirmation') OVER (PARTITION BY session_id) AS purchased
    FROM sessions
)
SELECT
    strftime(hit_ts, '%Y%m%d')::INT AS event_date_key,
    hit_ts                          AS event_ts_utc,
    visitor_id,
    session_id,
    CASE WHEN url = '/home' THEN 1
         WHEN url = '/search' THEN 2
         WHEN url LIKE '/product/%' THEN 3
         WHEN url = '/cart' THEN 4
         WHEN url = '/checkout' THEN 5
         ELSE 6 END AS page_key,
    CASE WHEN url LIKE '/product/%' THEN split_part(url, '/', 3)::INT ELSE 0 END AS product_key,
    CASE referrer WHEN 'google' THEN 1 WHEN 'direct' THEN 2 WHEN 'email' THEN 3 ELSE 0 END AS referrer_key,
    CASE WHEN purchased THEN 1 ELSE 2 END AS session_outcome_key,
    step_number,
    session_events - step_number AS steps_until_end,
    page_seconds,
    coalesce(order_amount, 0) AS order_amount
FROM numbered;
```

### Шаг 2. Проверяем

```sql
-- 7 сессий, 31 событие, 3 заказа
SELECT count(DISTINCT session_id) AS sessions,
       count(*)                   AS page_events,
       count(*) FILTER (WHERE order_amount > 0) AS orders
FROM fact_page_event;

-- последняя страница каждой сессии не имеет page_seconds
SELECT count(*) AS last_pages_with_null_seconds
FROM fact_page_event
WHERE steps_until_end = 0 AND page_seconds IS NULL;
```

### Задания

**1.** Порог сессии. Посчитайте, сколько сессий получится, если пауза равна 30 минут, 1 минута и 80 секунд. Сделайте порог параметром в запросе.

<details>
<summary>Решение</summary>

```sql
WITH gaps(gap_name, gap) AS (
    VALUES ('30 minutes', INTERVAL 30 MINUTE),
           ('80 seconds', INTERVAL 80 SECOND),
           ('1 minute',   INTERVAL 1 MINUTE)
), flagged AS (
    SELECT g.gap_name, h.visitor_id, h.hit_ts,
           CASE WHEN lag(h.hit_ts) OVER w IS NULL OR h.hit_ts - lag(h.hit_ts) OVER w > g.gap
                THEN 1 ELSE 0 END AS new_session
    FROM stg_hit h CROSS JOIN gaps g
    WINDOW w AS (PARTITION BY g.gap_name, h.visitor_id ORDER BY h.hit_ts)
)
SELECT gap_name, sum(new_session) AS sessions
FROM flagged
GROUP BY gap_name
ORDER BY sessions;
```

С порогом 30 минут сессий 7. Чем меньше порог, тем больше сессий. Выбор порога — это бизнес-правило. Храните его в одном месте.
</details>

**2.** Время на страницах. Покажите среднее `page_seconds` по типам страниц. Последние страницы сессий не входят (у них `NULL`). Какая страница самая долгая?

<details>
<summary>Решение</summary>

```sql
SELECT p.page_function,
       count(f.page_seconds)            AS measured_events,
       round(avg(f.page_seconds), 1)    AS avg_seconds
FROM fact_page_event f
JOIN dim_page p USING (page_key)
GROUP BY p.page_function
ORDER BY avg_seconds DESC;
```
</details>

**3.** Fact сессии. Постройте `fact_session` (grain: одна сессия) из событий: секунды сессии, число страниц, сумма заказа, страница входа и referrer входа. Проверьте, что сумма заказов равна сумме в fact событий.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_session AS
SELECT
    session_id,
    min(event_date_key)                                 AS start_date_key,
    max(page_key)    FILTER (WHERE step_number = 1)     AS entry_page_key,
    max(referrer_key) FILTER (WHERE step_number = 1)    AS entry_referrer_key,
    max(session_outcome_key)                            AS session_outcome_key,
    date_diff('second', min(event_ts_utc), max(event_ts_utc)) AS session_seconds,
    count(*)                                            AS pages_visited,
    sum(order_amount)                                   AS order_amount
FROM fact_page_event
GROUP BY session_id;

-- сверка: суммы совпадают, сессий 7
SELECT (SELECT count(*) FROM fact_session)           AS sessions,
       (SELECT sum(order_amount) FROM fact_session)  AS order_amount_session,
       (SELECT sum(order_amount) FROM fact_page_event) AS order_amount_events;

-- конверсия по источнику входа
SELECT r.referral_type,
       count(*)                                         AS sessions,
       count(*) FILTER (WHERE s.order_amount > 0)       AS purchases,
       round(100.0 * count(*) FILTER (WHERE s.order_amount > 0) / count(*), 0) AS conversion_pct
FROM fact_session s
JOIN dim_referrer r ON r.referrer_key = s.entry_referrer_key
GROUP BY r.referral_type
ORDER BY sessions DESC, r.referral_type;
```
</details>

**4.** Step dimension. Найдите точки отказа: последние страницы сессий без покупки. Потом посчитайте среднее число шагов до покупки в успешных сессиях.

<details>
<summary>Решение</summary>

```sql
-- где уходят без покупки (steps_until_end = 0)
SELECT p.page_function AS last_page, count(*) AS abandoned_sessions
FROM fact_page_event f
JOIN dim_page p USING (page_key)
JOIN dim_session_outcome o USING (session_outcome_key)
WHERE f.steps_until_end = 0 AND o.outcome = 'Abandoned'
GROUP BY p.page_function
ORDER BY abandoned_sessions DESC, last_page;

-- сколько шагов до покупки
SELECT round(avg(step_number), 1) AS avg_steps_to_purchase
FROM fact_page_event f
JOIN dim_page p USING (page_key)
WHERE p.page_function = 'Confirmation';
```
</details>

**5.** Воронка. Для каждой сессии определите, дошла ли она до товара, корзины, оформления и подтверждения. Посчитайте сессии на каждом шаге и долю от предыдущего шага.

<details>
<summary>Решение</summary>

```sql
WITH s AS (
    SELECT f.session_id,
           bool_or(p.page_function = 'Product')      AS saw_product,
           bool_or(p.page_function = 'Cart')         AS saw_cart,
           bool_or(p.page_function = 'Checkout')     AS saw_checkout,
           bool_or(p.page_function = 'Confirmation') AS purchased
    FROM fact_page_event f
    JOIN dim_page p USING (page_key)
    GROUP BY f.session_id
), funnel AS (
    SELECT 1 AS step, 'Product'      AS stage, count(*) FILTER (WHERE saw_product)  AS sessions FROM s
    UNION ALL
    SELECT 2, 'Cart',         count(*) FILTER (WHERE saw_cart)     FROM s
    UNION ALL
    SELECT 3, 'Checkout',     count(*) FILTER (WHERE saw_checkout) FROM s
    UNION ALL
    SELECT 4, 'Confirmation', count(*) FILTER (WHERE purchased)    FROM s
)
SELECT stage, sessions,
       round(100.0 * sessions / lag(sessions) OVER (ORDER BY step), 0) AS pct_of_previous
FROM funnel
ORDER BY step;
```

Из 7 сессий товар смотрели все. В корзину дошли 5, на оформление 4, купили 3.
</details>

## Вопросы для самопроверки

1. Почему fact сессии строят выше уровня самого детального grain?
2. Почему `page_seconds` и `session_seconds` нельзя называть одним словом?
3. Какие данные хранит step dimension и как найти точку отказа?
4. Как работает sessionization по паузе и что меняется при другом пороге?
