---
title: "The Data Warehouse Toolkit, глава 21: Big Data"
head:
  - tag: title
    content: "Big data и dimensional model: Kimball, JSON | Инжиниринг Данных"
description: "Конспект главы 21 The Data Warehouse Toolkit. Big data, data highway, лучшие практики. Практика в DuckDB: JSON, schema-on-read, загрузка в star schema."
sidebar:
  order: 21
  label: "21. Big Data"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** big data не отменяет dimensional modeling. Это новые типы данных и новые платформы. Но принципы те же: бизнес-цель, dimensions и facts, conformed dimensions, durable keys. Сырые данные превращают в факты и подключают к dimensions.

![Data highway: кеши с растущей задержкой и качеством, и backflow из хранилища](/assets/data-warehouse-toolkit/ch21-data-highway.png)

## Что такое big data

- Важен не размер. Важны разные форматы: структурированные, полуструктурированные, неструктурированные и сырые данные.
- Многие из них нельзя обработать обычным SQL: изображения, тексты, логи, пары «имя и значение».
- Это смена подхода: что собирать, где хранить и как получать из этого деньги.

Примеры задач из книги: ранжирование поиска, учёт рекламы, геолокация, соцсети и CRM, генетика, датчики и умные счётчики, антифрод, анализ оттока.

Книга перечисляет около 19 требований к системе для big data. Вот главные:

- масштаб до петабайт и тысяч узлов;
- хранение данных в исходном формате;
- загрузка с высокой скоростью до объявления структуры;
- пользовательские функции (UDF) на разных языках;
- сложные типы данных: изображения, иерархии, пары «имя и значение»;
- работа без единой точки отказа.

## Две архитектуры

| | Extended RDBMS | MapReduce / Hadoop |
|---|---|---|
| Идея | Реляционная база расширяет типы данных и UDF | Фреймворк для выполнения функций над данными на множестве машин |
| Лицензия | В основном проприетарная | Open source |
| Данные | Нужна структура | Структура не обязательна |
| Сильная сторона | Быстрый поиск по индексам, SQL, транзакции | Полное сканирование больших объёмов |
| Сложные структуры | Косвенная поддержка | Прямая поддержка |
| Итерации, сложная логика | Косвенная поддержка | Прямая поддержка |

Книга считает, что обе архитектуры будут существовать вместе. Hadoop часто используют как гибкую среду для ETL: он добавляет структуру, и данные попадают в RDBMS.

## Стандартные практики остаются

Проверенные за 30 лет практики применимы и здесь:

- выбирайте источники по бизнес-задаче;
- заботьтесь о простоте и скорости интерфейса;
- мыслите dimensions и facts;
- объединяйте источники через conformed dimensions;
- отслеживайте изменения через SCD;
- используйте durable surrogate keys.

## Практики управления

| Практика | Смысл |
|---|---|
| Стройте среду вокруг аналитики | Каждый шаг пути данных должен поддерживать сложные функции, а не только отчёты |
| Не строите legacy сейчас | Рынок быстро меняется. Закладывайте, что вы перепишете и перенесёте приложения за пару лет |
| Идите от sandbox | Data scientists экспериментируют в любых языках. Потом IT переписывает удачное на поддерживаемый стек |
| Начните с простого | Например, дешёвый backup и archive |

## Практики архитектуры

### Data highway

Это цепочка кешей с растущей задержкой и растущим качеством.

| Кеш | Задержка | Примеры |
|---|---|---|
| Raw source | Сразу | Антифрод по карте, обнаружение атак |
| Real time | Секунды | Выбор рекламы, персональные акции |
| Business activity | Минуты | Dashboards с низкой задержкой, отслеживание тикетов |
| Top line | 24 часа | Дневная сводка для руководства. Похож на ODS |
| DW и long time series | День, период, год | Отчёты, ad hoc, история |

В реальности внедряют только нужные кеши. Данные идут не только вперёд.

### Другие практики

- **Fact extractor.** Анализ неструктурированных данных создаёт числа. Например, из твитов получают счётчики тональности. Эти числа идут в следующий кеш.
- **Качество растёт вдоль highway.** Мгновенные данные неизбежно грязнее. Проверка поля быстрая, проверка связей между источниками медленнее.
- **Добавляйте ценность как можно раньше.** Фильтрация, чистка, conforming. Но есть мнение, что чистку нужно делать при анализе, чтобы не потерять интересные выбросы.
- **Backflow.** Из хранилища возвращайте в ранние кеши durable keys и производные итоги. Тогда в раннем кеше можно сделать простой join с conformed dimensions.
- **Streaming.** Анализ потока, пока данные идут. Запросы с движущимися окнами.
- **Избегайте boundary crash.** Планируйте масштаб заранее.
- **Прототипы в публичном облаке** можно делать быстро. Данные чувствительны? Тогда переносите в private cloud.
- **Ищите ускорение в 10-100 раз.** Узкие решения бывают быстрее универсальных.
- **Отделяйте нагрузку.** Аналитика на big data не должна ломать SLA хранилища.
- **Используйте in-database analytics.** После загрузки в таблицы SQL и функции мощны.

## Практики моделирования

- **Мыслите dimensions и facts.** Бизнесу это понятно и для big data.
- **Объединяйте источники через conformed dimensions.** Иначе у вас просто набор несвязанных таблиц.
- **Закрепляйте dimensions durable keys.** Один ключ клиента во всех кешах.
- **Отслеживайте изменения через SCD.**
- **Структуру можно объявить при анализе** (schema-on-read). Но для повторяемых отчётов структуру всё равно нужно зафиксировать.
- **Пары «имя и значение»** удобны для сырого слоя. Для частых полей создавайте колонки.
- **Интегрируйте структурированные и неструктурированные данные.** Например, комментарии клиентов с таблицей клиентов.

## Практики governance

- Big data требует тех же правил, что и хранилище: владельцы, определения, качество.
- **Приватность.** Персональные данные нужно защищать: маскирование, агрегация, ограничение доступа. Многие источники big data содержат личные данные людей.
- Dimensionalize данные до governance. Когда есть dimension «клиент», ему можно задать правила доступа.

## Ключевые термины

| Термин | Значение |
|---|---|
| Big data | Данные разных форматов, часто не для обычного SQL |
| MapReduce / Hadoop | Фреймворк для распределённых функций над данными |
| UDF | Функция пользователя внутри обработки данных |
| Data highway | Цепочка кешей с растущей задержкой и качеством |
| Fact extractor | Преобразование сырых данных в числовые факты |
| Backflow | Возврат ключей и итогов из DW в ранние кеши |
| Schema-on-read | Структуру определяют в момент чтения |
| Schema-on-write | Структура задана при записи |
| Durable key | Постоянный ключ сущности для всех систем |

## Что это значит на практике

- Сегодня Hadoop заменили lakehouse и облачные платформы (Parquet, Iceberg, Spark, облачные хранилища). Идеи главы остаются верными.
- Сырой слой держите в исходном виде (JSON, Parquet). Это ваш архив.
- Для отчётов делайте типизированную модель: dimensions и facts. Не просите BI читать JSON каждый раз.
- Часть полей, которые часто используют, выносите из JSON в колонки.
- Строки, которые не прошли приведение типов, не выбрасывайте. Записывайте их в отдельную таблицу отклонений.
- Не забывайте про приватность: исключите или замаскируйте персональные поля до публикации.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Расширение `json` встроено в DuckDB. Блоки идут по порядку. Решения тоже запускайте по порядку.

### Шаг 1. Создаём сырые JSON-данные

```sql
-- сырые события. Структура у них разная: у кого-то есть coupon, у кого-то attrs
CREATE TABLE raw_events (event_id INT, payload JSON);
INSERT INTO raw_events VALUES
 (1, '{"ts":"2025-03-01T10:15:00","type":"purchase","user":{"id":"u1","country":"RU"},"items":[{"sku":"A1","qty":2,"price":10.5},{"sku":"B2","qty":1,"price":99}],"attrs":{"device":"ios","campaign":"spring"}}'),
 (2, '{"ts":"2025-03-01T11:00:00","type":"view","user":{"id":"u2"},"items":[],"attrs":{"device":"web"}}'),
 (3, '{"ts":"2025-03-02T09:30:00","type":"purchase","user":{"id":"u1","country":"RU"},"items":[{"sku":"A1","qty":1,"price":10.5}],"coupon":"SPRING10"}'),
 (4, '{"ts":"bad-date","type":"purchase","user":{"id":"u3","country":"KZ"},"items":[{"sku":"C3","qty":"two","price":5}]}'),
 (5, '{"ts":"2025-03-02T14:00:00","type":"purchase","user":{"id":"u2","country":"DE"},"items":[{"sku":"C3","qty":3,"price":5}],"attrs":{"device":"android"}}'),
 (6, '{"ts":"2025-03-03T08:00:00","type":"view","user":{"id":"u3","country":"KZ"},"items":[]}');

-- отзывы клиентов (текст)
CREATE TABLE raw_feedback (feedback_id INT, payload JSON);
INSERT INTO raw_feedback VALUES
 (1, '{"user":"u1","ts":"2025-03-02","text":"Отлично, быстро доставили"}'),
 (2, '{"user":"u2","ts":"2025-03-02","text":"Долго ждал, плохая упаковка","stars":2}'),
 (3, '{"user":"u1","ts":"2025-03-03","text":"Супер, возьму ещё"}'),
 (4, '{"user":"u3","ts":"2025-03-03","text":"Нормально"}');
```

### Задания

**1.** Schema-on-read. Не создавая схему, найдите, какие поля встречаются в событиях и как часто. Потом достаньте `user.id`, `user.country` и `coupon` из JSON.

<details>
<summary>Решение</summary>

```sql
-- профиль структуры: какие поля есть и в скольких событиях
SELECT k AS field, count(*) AS events
FROM (SELECT unnest(json_keys(payload)) AS k FROM raw_events)
GROUP BY k
ORDER BY events DESC, field;

-- достаём значения. Если поля нет, получаем NULL
SELECT event_id,
       payload->>'$.user.id'      AS user_id,
       payload->>'$.user.country' AS country,
       payload->>'$.coupon'       AS coupon
FROM raw_events
ORDER BY event_id;
```

Поля `items`, `ts`, `type`, `user` есть во всех шести событиях. `attrs` есть в трёх, `coupon` в одном. Отсутствие поля не ломает запрос: вернётся `NULL`.
</details>

**2.** Flatten. Разверните массив `items` из покупок в строки: одна строка на товар. Потом разверните `attrs` в пары «имя и значение».

<details>
<summary>Решение</summary>

```sql
-- одна строка на товар в покупке
SELECT e.event_id,
       i->>'$.sku'                                  AS sku,
       i->>'$.qty'                                  AS qty_raw,
       try_cast(i->>'$.price' AS DECIMAL(10,2))     AS price
FROM raw_events e, unnest(from_json(e.payload->'$.items', '["JSON"]')) AS t(i)
WHERE e.payload->>'$.type' = 'purchase'
ORDER BY e.event_id, sku;

-- пары имя и значение
SELECT e.event_id, j.key AS attr_name, trim(j.value::VARCHAR, '"') AS attr_value
FROM raw_events e, json_each(e.payload->'$.attrs') AS j
ORDER BY e.event_id, attr_name;
```

Первый запрос вернёт 5 строк (товары из событий 1, 3, 4 и 5). Второй вернёт 4 пары. События 3, 4 и 6 не имеют `attrs`, и в результат не попадут.
</details>

**3.** Schema-on-write. Создайте типизированную таблицу `stg_event_item` с `try_cast` для времени и количества. Строки, где приведение не удалось, сохраните в `rejected_event_item`. Оставшиеся поместите в `clean_event_item`.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE stg_event_item AS
SELECT e.event_id,
       try_cast(e.payload->>'$.ts' AS TIMESTAMP)  AS event_ts,
       e.payload->>'$.user.id'                    AS user_id,
       e.payload->>'$.user.country'               AS country,
       i->>'$.sku'                                AS sku,
       try_cast(i->>'$.qty' AS INT)               AS qty,
       try_cast(i->>'$.price' AS DECIMAL(10,2))   AS price,
       e.payload::VARCHAR                         AS raw_json
FROM raw_events e, unnest(from_json(e.payload->'$.items', '["JSON"]')) AS t(i)
WHERE e.payload->>'$.type' = 'purchase';

CREATE TABLE rejected_event_item AS
SELECT * FROM stg_event_item
WHERE event_ts IS NULL OR qty IS NULL OR price IS NULL;

CREATE TABLE clean_event_item AS
SELECT * FROM stg_event_item
WHERE event_ts IS NOT NULL AND qty IS NOT NULL AND price IS NOT NULL;

SELECT 'clean' AS bucket, count(*) AS rows_cnt FROM clean_event_item
UNION ALL
SELECT 'rejected', count(*) FROM rejected_event_item;
```

Чистых строк 4, отклонена 1 (событие 4: плохая дата и `qty = "two"`). В `raw_json` лежит исходный документ. Так можно разобрать причину и перезагрузить.
</details>

**4.** Fact extractor. Из текстов отзывов получите числовые факты. Определите тональность по ключевым словам и посчитайте по дням число положительных, отрицательных и нейтральных отзывов, а также долю положительных.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_feedback AS
SELECT feedback_id,
       payload->>'$.user'                       AS user_id,
       CAST(payload->>'$.ts' AS DATE)           AS feedback_date,
       CASE
           WHEN lower(payload->>'$.text') LIKE '%отлично%' OR lower(payload->>'$.text') LIKE '%супер%'  THEN 'positive'
           WHEN lower(payload->>'$.text') LIKE '%плох%'    OR lower(payload->>'$.text') LIKE '%долго%'  THEN 'negative'
           ELSE 'neutral'
       END AS sentiment
FROM raw_feedback;

SELECT feedback_date,
       count(*) FILTER (WHERE sentiment = 'positive') AS positive,
       count(*) FILTER (WHERE sentiment = 'negative') AS negative,
       count(*) FILTER (WHERE sentiment = 'neutral')  AS neutral,
       round(count(*) FILTER (WHERE sentiment = 'positive') / count(*), 2) AS positive_share
FROM fact_feedback
GROUP BY feedback_date
ORDER BY feedback_date;
```

2 марта: 1 положительный, 1 отрицательный. 3 марта: 1 положительный, 1 нейтральный. Тексты превратились в числа, которые можно суммировать. Это и есть fact extractor. Правила на ключевых словах — простой пример. В реальной системе тут стоит модель.
</details>

**5.** Загрузка в dimensional model. Постройте `dim_user` с unknown member и surrogate key. Создайте `dim_product` из sku. Загрузите `fact_purchase_item` с grain «один товар в одном событии покупки». Затем посчитайте выручку по странам.

<details>
<summary>Решение</summary>

```sql
-- dim_user: durable natural key = user_id, страна берётся из самого свежего события
CREATE TABLE dim_user AS
SELECT 0 AS user_key, 'unknown' AS user_id, 'Unknown' AS country
UNION ALL
SELECT row_number() OVER (ORDER BY user_id), user_id, coalesce(country, 'Unknown')
FROM (
    SELECT payload->>'$.user.id' AS user_id,
           arg_max(payload->>'$.user.country', try_cast(payload->>'$.ts' AS TIMESTAMP)) AS country
    FROM raw_events
    GROUP BY 1
);

CREATE TABLE dim_product AS
SELECT row_number() OVER (ORDER BY sku) AS product_key, sku
FROM (SELECT DISTINCT sku FROM clean_event_item);

-- grain: один товар в одном событии покупки
CREATE TABLE fact_purchase_item AS
SELECT c.event_id,
       row_number() OVER (PARTITION BY c.event_id ORDER BY c.sku) AS line_no,
       strftime(c.event_ts, '%Y%m%d')::INT      AS date_key,
       coalesce(u.user_key, 0)                  AS user_key,
       p.product_key,
       c.qty,
       c.qty * c.price                          AS amount
FROM clean_event_item c
LEFT JOIN dim_user u    ON u.user_id = c.user_id
JOIN dim_product p      ON p.sku = c.sku;

SELECT u.country, sum(f.amount) AS revenue, count(*) AS items
FROM fact_purchase_item f
JOIN dim_user u USING (user_key)
GROUP BY u.country
ORDER BY revenue DESC;
```

Выручка RU: `2 * 10.5 + 99 + 10.5 = 130.50`, три позиции. DE: 15.00, одна позиция. KZ в результате нет, потому что событие 4 отклонено. Его нужно разобрать в `rejected_event_item`.
</details>

## Вопросы для самопроверки

1. Почему big data не отменяет dimensional modeling?
2. Чем отличаются Extended RDBMS и MapReduce/Hadoop? Для каких задач подходит каждый?
3. Что такое data highway и зачем нужен backflow?
4. В чём разница между schema-on-read и schema-on-write? Когда нужна вторая?
5. Что такое fact extractor? Приведите пример.
