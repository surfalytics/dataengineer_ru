---
title: "The Data Warehouse Toolkit, глава 18: Процесс моделирования"
head:
  - tag: title
    content: "Процесс dimensional modeling: bus matrix, grain | Инжиниринг Данных"
description: "Конспект главы 18 The Data Warehouse Toolkit. Workshop по dimensional modeling: bubble chart, bus matrix, review, документация и практика в DuckDB."
sidebar:
  order: 18
  label: "18. Процесс моделирования"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** dimensional model строят итерациями, вместе с бизнесом. Начинают с bus matrix и bubble chart. Потом описывают каждую таблицу. В конце проверяют модель и документируют её для ETL.

![Процесс dimensional modeling: от подготовки до финальной документации](/assets/data-warehouse-toolkit/ch18-modeling-process.png)

## Процесс в общих чертах

- Входы: предварительная bus matrix и подробные бизнес-требования.
- Выходы: high-level модель, детальные таблицы dimensions и facts, журнал вопросов (issues log).
- Для одного бизнес-процесса нужно в среднем 3-4 недели. Время зависит от опыта, доступности бизнеса, сложности источников и готовых conformed dimensions.
- Процесс линейный только на схеме. На деле вы много раз возвращаетесь назад.
- Внешнего эксперта просите вести процесс вместе с командой. Не отпускайте его на три недели «рисовать модель».

## Подготовка

| Что сделать | Зачем |
|---|---|
| Позвать бизнес-представителей и data stewards | Модель отражает реальные вопросы, а не только структуру источника |
| Позвать эксперта по источнику, DBA, ETL-инженера | Они знают данные. Они не дадут свести модель к 3NF |
| Подготовить data stewardship | Для conformed dimensions нужны общие определения |
| Взять инструмент для модели | Сначала подходит таблица. Потом специальный modeling tool |
| Взять инструмент для data profiling | Проверять данные, а не документацию. Можно простым SQL |
| Согласовать naming conventions | Имена колонок видны в BI. `Description` без контекста бесполезно |
| Расписание и комната | Сессии по 2-3 часа, 3-4 дня в неделю. Одна комната на весь период |

Naming: структура «prime word, qualifiers, class word». Например `Customer Birth Date`.

Conformed dimensions — это скорее организационная задача, чем техническая. Нужно договориться об именах, определениях и значениях. Это трудно, но в этом и есть интеграция.

## Дизайн модели

Четыре решения из главы 3 остаются теми же: process, grain, dimensions, facts. Процесс выбран ещё на этапе приоритизации (глава 17).

### Шаг 1. Bubble chart

![Bubble chart для процесса Orders: fact в центре, dimensions вокруг](/assets/data-warehouse-toolkit/ch18-bubble-chart.png)

- Это граф высокого уровня: fact-таблица и её dimensions.
- Начинают с bus matrix. Строка матрицы может дать несколько bubble charts, если у fact-таблиц разный grain.
- Всю команду приглашают. Не рисуйте первый вариант в одиночку.
- Grain должен опираться на реальные данные источника.
- Если dimension не подходит к grain, есть три выхода: убрать dimension, изменить grain, использовать multivalued-решение.

### Шаг 2. Детальная модель

Идут таблица за таблицей, колонка за колонкой. Бизнес участвует всё время.

1. **Dimensions первыми.** Начните с простых: date. Команда научится работать вместе.
2. **Атрибуты и определения.** Имена и определения должны иметь смысл для бизнеса. Иногда нужен governance committee.
3. **Facts.** Все facts должны соответствовать grain. Кроме базовых есть производные метрики.
4. **SCD.** Для каждого атрибута выберите тип: 1, 2 или 3. Спросите эксперта источника: изменение — это исправление ошибки или реальное изменение?
5. **Junk и mini-dimensions.** Часто нужны, когда вы уже глубоко в деталях.

Результат — design worksheet на каждую таблицу.

| Поле worksheet | Пример |
|---|---|
| Table name, тип, описание | `DimOrderProfile`, dimension, junk |
| Column name и описание | `OrderMethod`, способ заказа |
| Data type, size | `varchar(8)` |
| Sample values | Phone, Fax, Internet |
| SCD type | 1 |
| Source system, table, field | OEI, OrderHeader, Ord_Meth |
| ETL rules | `1=Phone, 2=Fax, 3=Internet` |

Для facts добавляют foreign keys, degenerate dimensions и тип аддитивности. Worksheet — первая версия source-to-target mapping для ETL.

### Журнал вопросов и bus matrix

- **Issues log.** Каждый вопрос про определение, правило или качество данных записывают. Кто-то один отвечает за журнал. В конце сессии проверьте новые записи.
- **Bus matrix.** Обновляйте её в процессе. Появляются новые fact-таблицы, dimensions делятся и объединяются.

## Review и документация

| Review | Кто | Как проходит |
|---|---|---|
| IT review | Коллеги из IT, эксперты источников, DBA | Часто они считают себя специалистами по 3NF. Дайте им краткое обучение. Начните с bus matrix |
| Core user review | Ключевые пользователи | Если они были в команде, можно объединить с IT review |
| Broader business review | Широкий круг бизнеса | Это ещё и обучение. Покажите bus matrix, bubble charts, иерархии. Разберите вопросы из требований |

Финальная документация:

- описание целей и bus matrix;
- bubble charts;
- design worksheets;
- открытые вопросы;
- примеры вопросов, на которые модель отвечает.

## Типичные ошибки

- Модель строит одна IT-команда без бизнеса.
- Пропущен просмотр требований. Модель повторяет источник и не добавляет ценности.
- Grain не объявлен или смешан.
- Нет data profiling. Выясняется потом, что данных нет.
- Для каждого отдела своя версия dimension. Нет conformance.

## Ключевые термины

| Термин | Значение |
|---|---|
| Bubble chart | Диаграмма: fact и dimensions кружками |
| Bus matrix | Процессы в строках, dimensions в колонках |
| Conformed dimension | Dimension с общими ключами, именами и значениями |
| Design worksheet | Описание таблицы: колонки, SCD, источник, правила |
| Issues log | Журнал открытых вопросов по модели |
| Data profiling | Анализ реального содержимого источника |
| Source-to-target mapping | Откуда каждая колонка берётся и как преобразуется |

## Что это значит на практике

- Начинайте с bus matrix в таблице или в `dbt` docs. Держите её актуальной.
- Проверяйте grain запросами, а не на глаз. Тест `unique` на комбинации колонок в `dbt` делает то же самое.
- Профилируйте источник до обсуждения с бизнесом. Простого `SELECT DISTINCT` и `count` часто хватает.
- Worksheet можно вести как YAML рядом с моделями или как таблицу в базе. Главное — SCD-тип и источник для каждой колонки.
- Не откладывайте conformance на потом. Позже переименовывать колонки в десятках отчётов дорого.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Решения тоже запускайте по порядку.

### Шаг 1. Создаём данные

```sql
-- bus matrix в виде пар «процесс и dimension»
CREATE TABLE bus_matrix AS
SELECT * FROM (VALUES
    ('orders','date'), ('orders','customer'), ('orders','product'), ('orders','promotion'), ('orders','sales_rep'),
    ('shipments','date'), ('shipments','customer'), ('shipments','product'), ('shipments','warehouse'),
    ('inventory','date'), ('inventory','product'), ('inventory','warehouse'),
    ('returns','customer'), ('returns','product')
) t(process_id, dimension_name);

-- черновая fact-таблица. Заявленный grain: одна строка на строку заказа (order_id, line_no)
CREATE TABLE fact_orders_draft AS
SELECT * FROM (VALUES
    (1001, 1, 10, 1, 2, 40.0),
    (1001, 2, 11, 1, 1, 15.0),
    (1002, 1, 10, 2, 5, 100.0),
    (1003, 1, 12, 3, 1, 99.0),
    (1003, 1, 12, 3, 1, 99.0),   -- дубликат строки
    (1004, 1, 99, 2, 3, 60.0),   -- product_key 99 нет в dimension
    (1005, 1, NULL, 1, 1, 20.0)  -- пустой foreign key
) t(order_id, line_no, product_key, customer_key, quantity, amount);

CREATE TABLE dim_product AS
SELECT * FROM (VALUES (10,'Молоко'), (11,'Хлеб'), (12,'Кофе')) t(product_key, product_name);

-- один и тот же dimension «клиент» у двух команд
CREATE TABLE dim_customer_sales AS
SELECT * FROM (VALUES
    (1, 'Иван',  'Центр',   'Retail'),
    (2, 'Анна',  'Юг',      'Retail'),
    (3, 'Олег',  'Урал',    'Corporate')
) t(customer_id, customer_name, region, segment);

CREATE TABLE dim_customer_support AS
SELECT * FROM (VALUES
    (1, 'Иван',  'ЦФО',  'Gold'),
    (2, 'Анна',  'Юг',   'Silver'),
    (3, 'Олег',  'УрФО', 'Gold')
) t(customer_id, name, region_name, tier);

-- design worksheet в виде таблицы
CREATE TABLE design_worksheet AS
SELECT * FROM (VALUES
    ('dim_customer', 'customer_key',  'key',       'Surrogate key',        NULL, 'derived'),
    ('dim_customer', 'customer_id',   'attribute', 'Natural key',          1,    'CRM.customers.id'),
    ('dim_customer', 'customer_name', 'attribute', 'Имя клиента',          1,    'CRM.customers.name'),
    ('dim_customer', 'region',        'attribute', 'Регион',               2,    'CRM.customers.region'),
    ('dim_customer', 'segment',       'attribute', NULL,                   NULL, 'CRM.customers.seg'),
    ('dim_customer', 'tier',          'attribute', 'Уровень лояльности',   2,    NULL),
    ('dim_product',  'product_key',   'key',       'Surrogate key',        NULL, 'derived'),
    ('dim_product',  'product_name',  'attribute', 'Название товара',      1,    'ERP.items.name'),
    ('dim_product',  'category',      'attribute', 'Категория',            2,    'ERP.items.cat')
) t(table_name, column_name, column_role, description, scd_type, source_field);
```

### Задания

**1.** Покажите bus matrix в широком виде: строки — dimensions, колонки — процессы. Поставьте `X`, если dimension нужен процессу.

<details>
<summary>Решение</summary>

```sql
SELECT dimension_name,
       max(CASE WHEN process_id = 'orders'    THEN 'X' END) AS orders,
       max(CASE WHEN process_id = 'shipments' THEN 'X' END) AS shipments,
       max(CASE WHEN process_id = 'inventory' THEN 'X' END) AS inventory,
       max(CASE WHEN process_id = 'returns'   THEN 'X' END) AS returns
FROM bus_matrix
GROUP BY dimension_name
ORDER BY count(*) DESC, dimension_name;
```
</details>

**2.** Найдите кандидатов в conformed dimensions: dimensions, которые нужны хотя бы двум процессам. Потом найдите процессы без dimension `date`. Это возможная ошибка модели.

<details>
<summary>Решение</summary>

```sql
-- кандидаты в conformed dimensions
SELECT dimension_name, count(*) AS processes,
       string_agg(process_id, ', ' ORDER BY process_id) AS used_by
FROM bus_matrix
GROUP BY dimension_name
HAVING count(*) >= 2
ORDER BY processes DESC, dimension_name;

-- процессы без date
SELECT DISTINCT p.process_id
FROM bus_matrix p
WHERE NOT EXISTS (
    SELECT 1 FROM bus_matrix d
    WHERE d.process_id = p.process_id AND d.dimension_name = 'date'
);
```

Процесс `returns` не имеет `date`. Для fact-таблицы возвратов это почти наверняка ошибка.
</details>

**3.** Проверьте grain черновой fact-таблицы. Найдите строки, которые нарушают заявленный grain. Потом найдите строки, у которых foreign key пустой или не найден в dimension.

<details>
<summary>Решение</summary>

```sql
-- 1) нарушение уникальности grain
SELECT order_id, line_no, count(*) AS rows_with_same_grain
FROM fact_orders_draft
GROUP BY order_id, line_no
HAVING count(*) > 1;

-- 2) пустой или неизвестный product_key
SELECT f.order_id, f.line_no, f.product_key,
       CASE WHEN f.product_key IS NULL THEN 'NULL в foreign key'
            ELSE 'нет в dim_product' END AS problem
FROM fact_orders_draft f
LEFT JOIN dim_product p USING (product_key)
WHERE f.product_key IS NULL OR p.product_key IS NULL;
```

Первый запрос возвращает заказ 1003. Второй — заказы 1004 и 1005.
</details>

**4.** Проверьте, что `dim_customer_sales` и `dim_customer_support` можно считать одним conformed dimension. Сравните колонки и значения региона для одного клиента.

<details>
<summary>Решение</summary>

```sql
-- какие колонки совпадают по имени
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'dim_customer_sales'
INTERSECT
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'dim_customer_support';

-- разные значения для одного клиента
SELECT s.customer_id, s.region AS region_sales, c.region_name AS region_support
FROM dim_customer_sales s
JOIN dim_customer_support c USING (customer_id)
WHERE s.region <> c.region_name;
```

Совпадает только `customer_id`. Название региона записано по-разному: `Центр` и `ЦФО`, `Урал` и `УрФО`. Это не conformed dimension. Нужны общие имена колонок и общий справочник значений.
</details>

**5.** Проверьте design worksheet. Найдите атрибуты, у которых нет описания, SCD-типа или источника. Ключи не проверяйте.

<details>
<summary>Решение</summary>

```sql
SELECT table_name, column_name,
       concat_ws(', ',
           CASE WHEN description  IS NULL THEN 'нет описания' END,
           CASE WHEN scd_type     IS NULL THEN 'нет SCD-типа' END,
           CASE WHEN source_field IS NULL THEN 'нет источника' END) AS gaps
FROM design_worksheet
WHERE column_role = 'attribute'
  AND (description IS NULL OR scd_type IS NULL OR source_field IS NULL)
ORDER BY table_name, column_name;
```

Вернутся `segment` (без описания и SCD) и `tier` (без источника). ETL-разработчик не сможет начать работу, пока это не закрыто.
</details>

## Вопросы для самопроверки

1. Почему первый вариант bubble chart лучше делать всей командой?
2. Почему детальный дизайн начинают с dimensions, а не с facts?
3. Что делать, если предложенный dimension не подходит к grain fact-таблицы?
4. Зачем в design worksheet нужны SCD-тип и источник каждой колонки?
5. Чем IT review отличается от review с широким кругом бизнеса?
