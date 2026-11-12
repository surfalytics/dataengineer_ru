---
title: "The Data Warehouse Toolkit, глава 5: Закупки и SCD"
head:
  - tag: title
    content: "Slowly changing dimension: типы SCD 0-7 по Kimball | Инжиниринг Данных"
description: "Конспект главы 5 The Data Warehouse Toolkit. Закупки и типы SCD 0-7: перезапись, новая строка, mini-dimension, hybrid. Практика в DuckDB."
sidebar:
  order: 5
  label: "5. Закупки и SCD"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** атрибуты dimension меняются, и для каждого атрибута нужно решить, что делать с историей. Глава 5 разбирает закупки и подробно описывает типы SCD от 0 до 7.

![Star schema закупок: строка заказа поставщику и dimensions](/assets/data-warehouse-toolkit/ch05-procurement-star.png)

## Закупки как процесс

Закупки — это цепочка событий:

1. Запрос и заказ поставщику (`purchase order`).
2. Уведомление об отгрузке.
3. Приёмка на складе.
4. Счёт поставщика.
5. Оплата.

Бизнес хочет знать, сколько мы тратим и у кого. Хочет сравнивать цены поставщиков. Хочет видеть, кто поставляет вовремя и в полном объёме.

### Transaction fact table закупок

- Grain: одна строка заказа (`purchase order line`).
- Dimensions: дата, товар, поставщик, склад, договор, условия поставки.
- Degenerate dimensions: `po_number` и номер строки.
- Facts: количество и сумма заказа.

Таблица очень похожа на розничные продажи из главы 3. Принцип тот же.

### Одна fact table или несколько

| Вариант | Когда подходит |
|---|---|
| Одна таблица с `transaction_type` | У всех событий одинаковые dimensions и похожие факты |
| Отдельная таблица на каждый тип события | Dimensions или факты разные. Это частый случай |

Книга предлагает четыре вопроса:

- Как бизнес обычно анализирует эти данные?
- Это правда разные бизнес-процессы? Подсказка: у каждого шага свой номер документа.
- Данные приходят из разных систем с разным grain?
- У событий разные dimensions?

В закупках ответы указывают на отдельные таблицы. Заказы, склад и оплаты живут в трёх разных системах. У приёмки есть склад, у заказа его может не быть. Поэтому лучше отдельные fact tables на каждый шаг. Их объединяет `bus matrix` и общие dimensions: дата, товар, поставщик, склад.

### Blanket order и договоры

Один договор может охватывать много заказов. В dimension договора храните условия. В fact добавьте ключ договора. Тогда можно сравнить цену по договору и цену по факту покупки.

### Дополнительный snapshot

Из transactions строят `periodic snapshot`: сколько заказов открыто. Или `accumulating snapshot` заказа: заказ, отгрузка, приёмка, оплата с lags между вехами (см. [главу 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)).

## Slowly Changing Dimensions

Dimension хранит описание сущности. Описание меняется: поставщик получил другой уровень, клиент переехал. Для каждого атрибута выбираем один из типов.

![Как выбрать тип SCD](/assets/data-warehouse-toolkit/ch05-scd-types.png)

### Type 0: оставить исходное

Значение никогда не меняется. Это атрибуты вида «исходный». Пример: дата первой покупки, исходный кредитный рейтинг. Даже если источник прислал другое значение, мы его игнорируем.

### Type 1: перезаписать

- Старое значение стирается. Истории нет.
- Подходит для исправления ошибок и для атрибутов, где история не нужна.
- Все прошлые факты теперь «видят» новое значение.
- Если по атрибуту есть агрегаты, их нужно пересчитать.

### Type 2: новая строка

- Это главный способ хранить историю. Создаём новую строку с новым surrogate key.
- Служебные колонки: `row_effective_date`, `row_expiration_date`, `is_current`.
- Факт хранит ключ той версии, которая действовала в момент события. Поэтому прошлые факты остаются за старым значением.
- Один natural key — много surrogate keys.
- Для новых фактов ищем версию по дате: `event_date >= row_effective_date AND event_date < row_expiration_date`. Здесь интервал полуоткрытый. В книге `row_expiration_date` — день до начала следующей версии, тогда в условии `<=`.
- Бывает отдельный флаг изменения и дата изменения.

### Type 3: новая колонка

- Храним текущее и предыдущее значение: `region` и `prior_region`.
- Строк не прибавляется. История — только одна смена.
- Удобно, когда бизнес хочет видеть и «по-старому», и «по-новому» сразу. Например, при реорганизации.
- Для частых изменений не подходит.

### Type 4: mini-dimension

Некоторые атрибуты клиента меняются часто: возрастная группа, доход, рейтинг. Type 2 раздул бы большую dimension.

- Выносим такие атрибуты в маленькую `mini-dimension`. В ней строки — комбинации диапазонов значений.
- Fact хранит два ключа: основной dimension и mini-dimension.
- История профиля хранится в fact. Она привязана к моменту события.
- Значения делят на диапазоны (band), чтобы строк было мало.

### Гибриды

| Тип | Идея | Когда нужен |
|---|---|---|
| 5 | Type 4 плюс Type 1 outrigger: в основную dimension добавляем ключ текущего профиля из mini-dimension | Нужен и профиль на момент события, и текущий профиль |
| 6 | В Type 2 dimension добавляем Type 1 колонки с текущим значением (1+2+3 = 6) | Нужно группировать по историческому и по текущему значению |
| 7 | Fact хранит два ключа: surrogate key версии (Type 2) и durable key. Через durable key view даёт текущую строку (Type 1) | Нужна любая из двух точек зрения без пересоздания таблиц |

### Сводная таблица

| Тип | История | Размер dimension | Сложность |
|---|---|---|---|
| 0 | Исходное значение | Не растёт | Низкая |
| 1 | Нет | Не растёт | Низкая |
| 2 | Полная | Растёт | Средняя |
| 3 | Одна смена | Не растёт | Средняя |
| 4 | Через fact | Растёт мало | Выше |
| 5, 6, 7 | Обе точки зрения | Зависит | Высокая |

Важное правило: для каждого атрибута свой тип. В одной таблице могут быть атрибуты Type 1, 2 и 3 вместе.

## Ключевые термины

| Термин | Значение |
|---|---|
| SCD | Slowly changing dimension: способ хранить изменение атрибута |
| Type 2 | Новая строка для новой версии |
| Durable key | Ключ сущности, который не меняется между версиями |
| Mini-dimension | Маленькая dimension для быстро меняющихся атрибутов |
| Purchase order line | Строка заказа. Grain fact table закупок |
| Row effective date | С какой даты версия строки действует |

## Что это значит на практике

- Спросите бизнес по каждому атрибуту: «История нужна?». Ответ определяет тип.
- В `dbt` Type 2 — это `snapshot` со стратегией `timestamp` или `check`. Ключ версии добавляйте сами.
- Type 1 атрибут в Type 2 dimension обновляйте во всех строках сущности. Иначе версии разойдутся.
- Для `Type 6` и `Type 7` часто хватает view `dim_current`.
- Late arriving факт: ищите версию dimension на дату события, а не берите последнюю.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку в одной сессии. Не пропускайте задания: каждое меняет таблицы для следующего.

### Шаг 1. Создаём схему и данные

```sql
CREATE MACRO key_to_date(k) AS strptime(k::VARCHAR, '%Y%m%d')::DATE;

CREATE TABLE dim_product AS
SELECT * FROM (VALUES (1, 'Болты М8'), (2, 'Гайки М8')) t(product_key, product_name);

-- tier = Type 2, region = Type 1
CREATE TABLE dim_vendor AS
SELECT * FROM (VALUES
    (1, 'V1', 'Acme', 'Silver', 'Запад',  DATE '2024-01-01', DATE '9999-12-31', true),
    (2, 'V2', 'Bolt', 'Gold',   'Восток', DATE '2024-01-01', DATE '9999-12-31', true)
) t(vendor_key, vendor_id, vendor_name, tier, region,
    row_effective_date, row_expiration_date, is_current);

-- срез из источника на 2024-03-01
CREATE TABLE stg_vendor AS
SELECT * FROM (VALUES
    ('V1', 'Acme', 'Gold', 'Центр'),   -- tier и region изменились
    ('V2', 'Bolt', 'Gold', 'Восток')
) t(vendor_id, vendor_name, tier, region);

-- grain: одна строка заказа. po_number и po_line_number - degenerate dimensions
CREATE TABLE fact_po_line AS
SELECT po_number, po_line_number,
       strftime(po_date, '%Y%m%d')::INT AS po_date_key,
       product_key, vendor_key, ordered_qty, ordered_amount
FROM (VALUES
    ('PO1', 1, DATE '2024-01-10', 1, 1, 100, 1000),
    ('PO1', 2, DATE '2024-01-10', 2, 1,  50,  400),
    ('PO2', 1, DATE '2024-02-05', 1, 2, 200, 3000)
) t(po_number, po_line_number, po_date, product_key, vendor_key, ordered_qty, ordered_amount);
```

### Задания

**1.** Type 2 через `MERGE`. Закройте текущую версию V1, у которой изменился `tier`. Потом вставьте новую версию. После этого загрузите три заказа за март и апрель (PO3–PO5, данные в решении) с поиском версии по дате.

<details>
<summary>Решение</summary>

```sql
-- 1) закрываем версию
MERGE INTO dim_vendor d
USING stg_vendor s
   ON d.vendor_id = s.vendor_id AND d.is_current
WHEN MATCHED AND d.tier <> s.tier THEN
    UPDATE SET row_expiration_date = DATE '2024-03-01', is_current = false;

-- 2) вставляем новую версию тем, у кого нет текущей строки
INSERT INTO dim_vendor
SELECT (SELECT max(vendor_key) FROM dim_vendor) + row_number() OVER (ORDER BY s.vendor_id),
       s.vendor_id, s.vendor_name, s.tier, s.region,
       DATE '2024-03-01', DATE '9999-12-31', true
FROM stg_vendor s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_vendor d WHERE d.vendor_id = s.vendor_id AND d.is_current
);

-- 3) новые факты: версия на дату заказа
INSERT INTO fact_po_line
SELECT o.po_number, o.po_line_number,
       strftime(o.po_date, '%Y%m%d')::INT,
       o.product_key, v.vendor_key, o.ordered_qty, o.ordered_amount
FROM (VALUES
    ('PO3', 1, DATE '2024-03-12', 1, 'V1',  80,  800),
    ('PO4', 1, DATE '2024-04-03', 2, 'V2',  60,  900),
    ('PO5', 1, DATE '2024-04-20', 1, 'V1',  40,  420)
) o(po_number, po_line_number, po_date, product_key, vendor_id, ordered_qty, ordered_amount)
JOIN dim_vendor v
  ON v.vendor_id = o.vendor_id
 AND o.po_date >= v.row_effective_date
 AND o.po_date <  v.row_expiration_date;

SELECT vendor_key, vendor_id, tier, region, row_effective_date, is_current
FROM dim_vendor ORDER BY vendor_id, vendor_key;
```

У V1 теперь две версии. Заметьте: в старой строке region `Запад`, в новой `Центр`. Это несогласованность. Её исправит задание 4.
</details>

**2.** Две fact tables. Создайте `fact_po_receipt` (приёмки) на grain «одна приёмка строки заказа». Сравните заказанное и полученное по поставщику. Агрегируйте каждый fact отдельно.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_po_receipt AS
SELECT * FROM (VALUES
    ('PO1', 1, 20240120,  90),
    ('PO1', 1, 20240125,  10),   -- вторая поставка по той же строке
    ('PO1', 2, 20240122,  50),
    ('PO2', 1, 20240215, 150),
    ('PO3', 1, 20240320,  80),
    ('PO4', 1, 20240410,  30)
) t(po_number, po_line_number, receipt_date_key, received_qty);

WITH ordered AS (
    SELECT po_number, po_line_number, vendor_key,
           sum(ordered_qty) AS ordered_qty
    FROM fact_po_line GROUP BY ALL
), received AS (
    SELECT po_number, po_line_number, sum(received_qty) AS received_qty
    FROM fact_po_receipt GROUP BY ALL
)
SELECT v.vendor_id,
       sum(o.ordered_qty)                       AS ordered,
       sum(coalesce(r.received_qty, 0))         AS received,
       round(sum(coalesce(r.received_qty, 0)) * 100.0 / sum(o.ordered_qty), 1) AS fill_rate_pct
FROM ordered o
LEFT JOIN received r USING (po_number, po_line_number)
JOIN dim_vendor v USING (vendor_key)
GROUP BY v.vendor_id
ORDER BY v.vendor_id;
```

Fill rate — это отношение двух сумм. Мы не храним его в fact. Строка PO5 ещё не получена, поэтому нужен `LEFT JOIN`.
</details>

**3.** Type 6. Добавьте в `dim_vendor` колонку `current_tier` со значением из текущей версии. Покажите расходы по историческому `tier` и по `current_tier`.

<details>
<summary>Решение</summary>

```sql
ALTER TABLE dim_vendor ADD COLUMN current_tier VARCHAR;

UPDATE dim_vendor d
SET current_tier = c.tier
FROM dim_vendor c
WHERE c.vendor_id = d.vendor_id AND c.is_current;

SELECT v.tier AS tier_at_order, v.current_tier, sum(f.ordered_amount) AS spend
FROM fact_po_line f
JOIN dim_vendor v USING (vendor_key)
GROUP BY ALL
ORDER BY 1, 2;
```

Расходы на V1 до марта попадают в `Silver` по истории. По `current_tier` они все в `Gold`. Одна таблица отвечает на оба вопроса.
</details>

**4.** Type 1 внутри Type 2. Исправьте `region` у V1 во всех версиях, а не только в текущей. Проверьте, что у каждого vendor один region.

<details>
<summary>Решение</summary>

```sql
UPDATE dim_vendor d
SET region = s.region
FROM stg_vendor s
WHERE d.vendor_id = s.vendor_id
  AND d.region <> s.region;     -- без is_current: меняем все версии

SELECT vendor_id, count(DISTINCT region) AS regions
FROM dim_vendor
GROUP BY vendor_id
ORDER BY vendor_id;
```

Каждый vendor теперь имеет ровно один region. Type 1 атрибут нельзя обновлять только в текущей строке.
</details>

**5.** Type 4. У поставщика быстро меняется оценка надёжности. Вынесите её в mini-dimension с диапазонами. Привяжите каждый заказ к диапазону оценки на дату заказа. Используйте `ASOF JOIN`.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE dim_score_band AS
SELECT * FROM (VALUES
    (1, 'Low',    0,  49),
    (2, 'Medium', 50, 79),
    (3, 'High',   80, 100)
) t(score_band_key, band_name, min_score, max_score);

CREATE TABLE stg_vendor_score AS
SELECT * FROM (VALUES
    ('V1', DATE '2024-01-01', 55),
    ('V1', DATE '2024-03-15', 80),
    ('V2', DATE '2024-01-01', 90),
    ('V2', DATE '2024-04-01', 40)
) t(vendor_id, score_date, score);

CREATE TABLE fact_po_line_scored AS
WITH po AS (
    SELECT f.*, v.vendor_id, key_to_date(f.po_date_key) AS po_date
    FROM fact_po_line f
    JOIN dim_vendor v USING (vendor_key)
)
SELECT po.po_number, po.po_line_number, po.vendor_key, b.score_band_key, po.ordered_amount
FROM po
ASOF JOIN stg_vendor_score s
  ON po.vendor_id = s.vendor_id AND po.po_date >= s.score_date
JOIN dim_score_band b ON s.score BETWEEN b.min_score AND b.max_score;

SELECT b.band_name, count(*) AS po_lines, sum(f.ordered_amount) AS spend
FROM fact_po_line_scored f
JOIN dim_score_band b USING (score_band_key)
GROUP BY b.band_name
ORDER BY min(b.min_score);
```

В fact лежит ключ диапазона на момент заказа. В `dim_vendor` не нужны новые строки при каждой смене оценки. Мы создали новую таблицу для наглядности. В реальной загрузке `score_band_key` — просто ещё одна колонка в `fact_po_line`.
</details>

## Вопросы для самопроверки

1. Какой тип SCD вы выберете для исправления опечатки в названии? А для переезда клиента?
2. Почему для Type 2 нужен surrogate key, а не natural key?
3. Что такое mini-dimension и какую проблему она решает?
4. Чем Type 6 отличается от Type 2?
