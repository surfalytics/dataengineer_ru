---
title: "The Data Warehouse Toolkit, глава 18: Процесс моделирования"
head:
  - tag: title
    content: "Процесс dimensional modeling: bus matrix, grain | Инжиниринг Данных"
description: "Конспект главы 18 The Data Warehouse Toolkit: сессии dimensional modeling, bubble chart, design worksheet, review и документация. Практика в DuckDB."
sidebar:
  order: 18
  label: "18. Процесс моделирования"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** dimensional model строят итерациями и вместе с бизнесом. Работа идёт от общего к частному: bubble chart по `bus matrix`, потом таблица за таблицей, потом review. На выходе ETL-команда получает ясный старт.

## О чём глава

Главы 1–16 показали паттерны dimensional modeling. [Глава 17](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/) описала весь проект DW/BI. Эта глава отвечает, как проходит сама работа над моделью: кто участвует, в каком порядке идут шаги и что остаётся на выходе.

- Участники, срок и подготовка.
- Bubble chart и детальная модель.
- Три вида review и финальная документация.

![Процесс dimensional modeling: от подготовки до финальной документации](/assets/data-warehouse-toolkit/ch18-modeling-process.png)

Схема читается сверху вниз. Стрелки возврата справа — наша иллюстрация: книга лишь говорит, что на деле вы проходите модель несколько раз.

## Обзор процесса моделирования

Авторы настойчиво советуют звать на сессии представителей бизнеса и `data steward` — человека, который отвечает за данные и их определения. Порядок работы такой:

1. Начальная графическая модель по `bus matrix` (матрице «бизнес-процессы × dimensions»): границы, `grain` (что значит одна строка) и dimensions.
2. Детальные dimensions: атрибуты, источники, качество данных, преобразования.
3. Fact-таблицы.
4. Review с бизнесом и проверка модели.

Цели: модель отвечает требованиям бизнеса, данные для неё есть, ETL получает основу для `source-to-target mapping` (описания, откуда берётся каждая колонка). Входы — предварительная `bus matrix` и подробные требования. Результаты — high-level модель, детальные таблицы и журнал вопросов (issues log).

Один бизнес-процесс занимает обычно три-четыре недели. Срок зависит от опыта команды, полноты требований, участия бизнеса, сложности источников и готовых `conformed dimensions`. Процесс итеративный, хотя на схеме выглядит линейным. Внешний эксперт должен вести процесс вместе с командой, а не исчезать на недели. Иначе команда не поймёт компромиссы дизайна.

## Подготовка: Get Organized

### Участники, особенно представители бизнеса

Один человек не знает и бизнес, и особенности источников. Data modeler ведёт процесс, но к работе нужно подключить экспертов из бизнеса. Больше людей замедляет процесс, зато модель получается полнее. Позовите также DBA и ETL-инженера. Они поймут логику модели и не станут тянуть её к `3NF` (нормализованной схеме транзакционных систем) или переносить сложность в BI ради простого ETL. Цель обратная: сложность ETL в обмен на простоту BI.

Нужно и управление данными: если нет data governance, начните его. Выбор dimensional modeling — это выбор стратегии `conformed dimensions`, то есть dimensions с общими именами, определениями и значениями. Согласовать их трудно, но проблема организационная: у каждой группы свои правила. Критики называют это «слишком сложным». Авторы отвечают: договориться об именах и значениях — суть интегрированных данных. Иначе «единой версии правды» не будет. Технические шаги — в главе 19, [подсистемы 17 и 18](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/).

### Изучить бизнес-требования

Команда превращает требования в гибкую модель для широкого анализа, а не для нескольких отчётов. Если пропустить этот шаг, модель определяют только данные источника, и бизнес ничего не выигрывает.

### Инструмент для моделирования

Начните с электронной таблицы: правки в ней быстрые. Когда модель устоялась, переносите её в modeling tool компании. Из него DBA генерирует таблицы, индексы, партиции и views.

### Инструмент для data profiling

`Data profiling` — запросы к реальному содержимому источника вместо опоры на неполную или устаревшую документацию. Они показывают, что данные есть в пригодном виде и что нужно для их преобразования. Хватит нескольких SQL-запросов или специального инструмента.

### Naming conventions

Имена таблиц и колонок видны в BI. Колонка `Description` ясна в модели, но в отчёте ничего не говорит. У разных групп одно имя значит разное, а одно значение называют по-разному. Люди не любят отказываться от привычных слов. Работа скучная, но окупается. Если в компании есть стандарт имён из трёх частей (prime word, qualifiers, class word), расширьте его под понятные бизнесу имена. Если стандарта нет, создайте его.

> **Пояснение:** в имени `Customer Birth Date` prime word — `Customer`, qualifier — `Birth`, class word — `Date`.

### Календарь и помещение

Не резервируйте дни целиком. Проводите сессии по два-три часа утром и днём, три-четыре дня в неделю. В остальное время команда изучает источник, а modeler обновляет документы. Если основные dimensions уже есть, срок заметно сокращается. Нужна отдельная комната на весь период, бумага для flip chart и проектор.

## Дизайн dimensional model

Четыре решения те же, что в [главе 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/): бизнес-процесс, grain, dimensions, facts. Процесс выбран на приоритизации (глава 17). Дальше идут high-level модель, детальный дизайн, review и документация. Вы ходите между требованиями и источником и меняете модель по мере новых знаний. Новичкам сначала нужно короткое обучение.

### Bubble chart: общая модель, согласованная всей командой

`Bubble chart` — диаграмма процесса на уровне сущностей: fact-таблица и её dimensions. Первый вариант легко нарисовать по `bus matrix`. Авторы против того, чтобы опытный дизайнер рисовал его в одиночку: команда должна участвовать.

![Bubble chart для процесса Orders: fact в центре, dimensions вокруг](/assets/data-warehouse-toolkit/ch18-bubble-chart.png)

В примере книги `Orders` имеет grain «одна строка на строку заказа». Вокруг стоят даты, три роли клиента (покупатель, получатель, плательщик), товар, акция, канал, продавец и профиль заказа.

Grain учитывает и нужды бизнеса, и данные источника. Одна строка `bus matrix` может дать несколько диаграмм, если у fact-таблиц разный grain. Dimensions следуют из grain, но их выбор может заставить пересмотреть grain. Если dimension не подходит к grain, его убирают, меняют grain или берут multivalued-решение. Диаграмма помогает обсудить модель до деталей и показать границы проекта. Рисуйте каждую fact-таблицу на отдельной странице с dimensions в одном порядке.

### Детальная модель: таблица за таблицей

Команда часто встречается и описывает модель таблица за таблицей, колонка за колонкой. Бизнес даёт отзывы об атрибутах, фильтрах, группировках, названиях и метриках. Начинают с dimensions, затем идут fact-таблицы. Первыми берут простые dimensions, чаще дату: так команда быстро добивается успеха и учится работать вместе. Для всех полей записывают источники, определения и предварительные бизнес-правила.

#### Dimensions и их атрибуты

Ключевые conformed dimensions должны подойти всей компании. Имена и определения согласуют data stewards и аналитики, а выбирает их в итоге бизнес. Это отнимает время, но сильно повышает принятие модели пользователями. Иногда спор решает governance steering committee. Здесь же решают, нужны ли `junk dimensions` и `mini-dimensions` ([глава 2](/book-summaries/engineering/data-warehouse-toolkit/02-modeling-techniques/)). Их польза может стать ясной, лишь когда команда глубоко в модели.

#### Facts

Все facts должны быть верны для объявленного grain. Profiling показывает базовые счётчики и суммы источника. Бизнес может хотеть и производные метрики.

#### Выбрать техники SCD

Когда черновики готовы, вернитесь к dimensions. Для каждого атрибута решите, как изменения источника попадут в dimension (техника `SCD`, slowly changing dimension). Критично мнение data stewards. Спросите экспертов источника, вызвано ли изменение исправлением ошибки.

> **Пояснение:** исправление ошибки обычно перезаписывают (type 1), а реальное изменение может требовать новой строки с историей (type 2).

#### Design worksheet: описание каждой таблицы

Главный результат фазы — `design worksheets`, по одному на каждый dimension и fact-таблицу. Они нужны аналитикам, BI-разработчикам и прежде всего ETL-разработчикам. Для каждого атрибута или факта записывают минимум имя, описание, примеры значений и SCD type. Для fact-таблицы добавляют foreign keys, degenerate dimensions и правило аддитивности (`additive`, `semi-additive`, `non-additive`). Пример книги — junk dimension `DimOrderProfile`:

| Поле worksheet | Пример |
|---|---|
| Column name | `OrderMethod`, способ заказа |
| Примеры значений, SCD type | Phone, Fax, Internet; type 1 |
| Источник | система OEI, таблица OrderHeader, поле `Ord_Meth` |
| ETL rules | `1=Phone, 2=Fax, 3=Internet` |

Worksheet — первый шаг к `source-to-target mapping`. Физическая команда добавит типы данных и ключи.

#### Журнал вопросов (issues log)

В журнал идут проблемы, определения, правила и вопросы качества данных. За него отвечает один человек, часто project manager. В конце сессии проверьте новые записи и назначьте исполнителей. Между сессиями команда профилирует данные и встречается с экспертами источников.

#### Поддерживать bus matrix в актуальном виде

Детальная работа приносит новые fact-таблицы и dimensions, а иногда их разделение или объединение. Обновляйте `bus matrix`: это ключевой инструмент общения и планирования. По [главе 16](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/), в ней можно хранить grain и метрики каждой fact-таблицы.

## Review и проверка модели

Когда команда уверена в модели, её показывают IT, аналитикам бизнеса вне команды и широкому бизнесу.

### IT review

IT-коллеги знают бизнес-процесс, потому что поддерживают его систему. Но многие считают себя сильными в `3NF` и переносят правила транзакционных систем на dimensional model. Авторы советуют не спорить, а заранее провести короткое обучение. Начните с `bus matrix`: она показывает границы проекта, роль conformed dimensions и приоритеты процессов. Затем покажите, как её строка становится bubble chart. Основное время уйдёт на worksheets и открытые вопросы. Кто-то должен записывать правки.

### Review с core users

Часто он не нужен, потому что ключевые пользователи уже в команде. Иначе встреча похожа на IT review. Core users технически сильнее обычных пользователей и справляются с деталями. В небольших компаниях их часто объединяют.

### Review с широким кругом бизнес-пользователей

Эта встреча — и обучение, и проверка. Не перегружайте людей: начните с `bus matrix` как карты данных, затем bubble charts и ключевые dimensions (customer, product). Можно показать иерархии внутри dimension, например отдел, категория, бренд, SKU. Разберите на примерах из требований, как модель отвечает на вопросы бизнеса.

## Финальная документация

Из рабочих материалов собирают итоговый документ: описание проекта, high-level диаграмму, worksheet для каждой таблицы и открытые вопросы.

## Итоги главы

- Dimensional modeling — итеративная командная работа, в которой участвует бизнес.
- Порядок: bubble chart из `bus matrix`, детальный дизайн таблиц, review.
- Цели: модель отвечает требованиям, данные доступны, ETL получает ясное направление.
- Один бизнес-процесс занимает три-четыре недели. Готовые conformed dimensions сокращают срок.
- Первый bubble chart делает вся команда. Grain учитывает и бизнес, и данные источника.
- Детальный дизайн идёт от dimensions к facts. Результат — worksheets, основа source-to-target mapping.
- Review проходят IT, core users и широкий бизнес: они проверяют модель на нужды бизнеса и на реальность данных.
- Имена и определения колонок — скорее политическая задача, чем техническая. Она требует самого дипломатичного участника.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Bubble chart` | Общая диаграмма процесса: fact и его dimensions |
| `Bus matrix` | Бизнес-процессы в строках, dimensions в колонках |
| `Conformed dimension` | Dimension с общими именами и значениями для всех процессов |
| `Data steward` | Ответственный за данные и их определения |
| `Data profiling` | Запросы к реальным данным источника |
| `Design worksheet` | Описание таблицы: колонки, SCD, источник, правила ETL |
| `Source-to-target mapping` | Откуда берётся каждая колонка и как преобразуется |
| `Issues log` | Журнал открытых вопросов модели |

## Что это значит на практике

- Ведите `bus matrix` в таблице или в `dbt` docs и держите её актуальной.
- Проверяйте grain запросами. Тест `unique` на комбинации колонок в `dbt` делает то же самое.
- Профилируйте источник до обсуждения с бизнесом. Часто хватает `SELECT DISTINCT` и `count`.
- Ведите worksheet как YAML рядом с моделями или как таблицу. Для каждой колонки нужны SCD-тип и источник.
- Не откладывайте conformance: переименовывать колонки в десятках отчётов позже дорого.
- Зовите ETL-инженера и DBA на сессии моделирования, чтобы модель не тянули к `3NF`.
- Давайте колонкам понятные бизнесу имена: они видны в BI.
- Ведите issues log в одном месте и назначайте исполнителя на каждый вопрос.

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

**1.** Покажите bus matrix в широком виде. Для компактности транспонируйте её: строки — dimensions, колонки — процессы (в книге наоборот: строки — процессы). Поставьте `X`, если dimension нужен процессу.

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

1. Почему первый вариант bubble chart лучше делать всей командой, а не отдавать одному опытному дизайнеру?
2. Почему детальный дизайн начинают с dimensions, а не с facts, и почему первым часто берут dimension даты?
3. Что делать, если предложенный dimension не подходит к grain fact-таблицы?
4. Зачем в design worksheet нужны SCD-тип и источник каждой колонки, и кто потом использует этот лист?
5. Чем IT review отличается от review с широким кругом бизнеса? Как вы готовите IT-коллег к review?
6. Почему согласование conformed dimensions — организационная задача, а не техническая, и кто должен её вести?

Предыдущая: [Глава 17. Kimball Lifecycle](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/). Следующая: [Глава 19. ETL subsystems](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/).
