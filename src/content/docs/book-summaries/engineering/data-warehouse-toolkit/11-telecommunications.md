---
title: "The Data Warehouse Toolkit, глава 11: Телеком"
head:
  - tag: title
    content: "Биллинг телеком и design review: Kimball | Инжиниринг Данных"
description: "Конспект главы 11 The Data Warehouse Toolkit: модель биллинга, ревью дизайна, grain, degenerate dimension, surrogate keys и YTD. Практика в DuckDB."
sidebar:
  order: 11
  label: "11. Телеком"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в этой главе вы не проектируете модель с нуля, а проверяете чужой черновик. Черновик биллинга телеком-компании содержит типичные ошибки. Книга разбирает их и даёт чеклист для `design review`.

## О чём глава

В [главе 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) мы строили модель банка с нуля. Здесь вы приходите в проект, где команда уже нарисовала первую модель, и ищете в ней слабые места. Пример — биллинг телеком-компании, похожие данные есть у коммунальных компаний.

- выбор первого процесса по `bus matrix`;
- чеклист частых ошибок в dimensional model;
- как провести `design review`;
- разбор черновика биллинга;
- переделка готовых таблиц;
- географическая dimension.

![Исправленная star schema биллинга: одна fact-таблица и пять dimensions](/assets/data-warehouse-toolkit/ch11-billing-star.png)

Схема показывает модель после ревью: в центре `fact_billing` с одной строкой на линию в счёте, вокруг пять dimensions. Колонка `due_date_key` — наше дополнение для практики, в книге у fact только дата счёта.

## Телеком-кейс и bus matrix

Вы — новый `dimensional modeler` в команде DW/BI большой компании мобильной связи. Команда собрала требования и нарисовала черновик `bus matrix`: строки — бизнес-процессы, столбцы — общие dimensions.

- **Процессы:** закупки, запасы, активация услуги, продажи, акции, детальный трафик (звонки и сообщения), биллинг, звонки в поддержку, ремонт.
- **Общие dimensions:** дата, продукт, клиент, тариф (`rate plan`), организация продаж (`sales organization`), линия связи (`service line`), коммутатор, сотрудник, профиль звонка в поддержку.

Комитет спонсоров выбрал для первой итерации биллинг. Он сильно влияет на бизнес, и IT считало, что данные реально загрузить. Руководство хочет видеть месячное потребление и выручку по клиентам, организациям продаж и тарифам. Часть IT предлагала начать с каждого звонка и сообщения. Комитет отказал: такие данные сложнее загрузить, а быстрой пользы они дают меньше.

Раз в месяц система выпускает счёт на каждый телефонный номер, то есть на `service line`. Линий миллионы. У линии один клиент, но у клиента может быть несколько линий, и они идут отдельными строками одного счёта. У каждой линии свои метрики: минуты, сообщения, мегабайты, ежемесячная плата. Тариф на счёте один, но со временем он меняется. У линии есть организация продаж и канал.

Моделер сделал черновик: `fact table` с grain «одна строка на счёт в месяц» и dimensions клиента, счёта, организации продаж, канала, тарифа и линии. Автор просит сначала поискать ошибки самому.

## Общие замечания для design review

Автор перечисляет ошибки, которые чаще всего находит на ревью. Команда из кейса не обязана была попасть во все.

### Баланс требований и источника

Модель строят по требованиям бизнеса и по реальным данным источника вместе, а источник профилируют. Только по требованиям: в модель попадут данные, которых нет в источнике. Только по источнику: пропадут данные, важные для аналитики.

### Фокус на бизнес-процессах

Модель отражает события бизнес-процесса, а не один отчёт. Модель под отчёт не переживёт его небольших изменений и обслужит один отдел. Модель процесса устойчивее и закрывает запросы разных отделов. После базовых схем можно добавить агрегаты, `accumulating snapshot`, `consolidated fact table` (facts нескольких процессов на общем grain) и `subset fact table` (часть данных для безопасности). Это второстепенные дополнения.

### Grain

Первый вопрос ревью всегда один: «Какой `grain` у fact table?» Команды часто отвечают по-разному, и тогда работа идёт по кругу. Авторы советуют строить fact на самом детальном grain, потому что заранее неизвестно, как пользователи захотят фильтровать и группировать данные. «Самый детальный» значит самый детальный для выбранного процесса, а не для всей компании.

### Один grain для всех facts

Все additive facts должны соответствовать выбранному grain. Иногда в fact кладут итог `year-to-date` (YTD), чтобы упростить запрос. Это опасно: он не полностью additive, и при нескольких датах в запросе его посчитают дважды.

Текстовые поля, флаги и индикаторы в fact запрещены. Они обычно занимают больше места, чем `surrogate key`, а пользователи хотят по ним фильтровать. Их место в dimension вместе с описательными атрибутами.

### Гранулярность dimension и иерархии

Каждая dimension даёт одно значение для строки fact. Иерархию «много к одному» кладут в одну таблицу, то есть денормализуют. Опытные моделисты по привычке нормализуют данные, как в `OLTP`. Но в dimensional model нормализация вредит понятности и скорости. Типичных ловушек четыре:

- `centipede fact table`: вместо одного ключа продукта в fact лежат ключи бренда, категории и других уровней. Fact обрастает десятками join. Если внешних ключей больше 20 или около того, объединяйте dimensions.
- `snowflake`: иерархия разложена по связанным таблицам. Экономия места мала на фоне всего хранилища и не окупает потерю удобства и скорости.
- `outrigger` — таблица, подключённая к другой dimension. Она допустима для группы атрибутов с малой cardinality, но как исключение.
- Строки разных уровней в одной dimension: продукты и бренды с колонкой `level`. Так делали давно. Теперь авторы не советуют: пользователи путаются, а без фильтра по `level` суммы задваиваются.

### Date dimension

У каждой fact table есть хотя бы один ключ на явную `date dimension`. Иногда её подключают просто потому, что так принято, и не могут объяснить, о какой дате речь. Авторы советуют date dimension с атрибутами для группировки и фильтров.

### Фиксированные time buckets вместо date dimension

Старые системы хранят в одной строке метрики за 12 месяцев: `month_1`, `month_2` и так далее. У этого три проблемы:

- слоты жёсткие: когда они заполнены, нужно расширять таблицу или сдвигать данные и ломать запросы;
- свойства даты остаются на совести приложения, календарных описаний для фильтров нет;
- если измерения были не во всех периодах, в строках много NULL.

Книга советует хранить каждый период отдельной строкой fact.

### Degenerate dimensions

Иногда для номера счёта или заказа делают отдельную dimension с датой и клиентом. Авторы советуют другое: номер транзакции — это `degenerate dimension`, он лежит в fact без своей таблицы, а дата и клиент идут в fact как ключи. Сигнал для ревью: dimension, в которой строк почти столько же, сколько в fact.

### Surrogate keys

Первичный ключ dimension — `surrogate key`, а не ключ источника. Исключение только одно: стабильная и предсказуемая date dimension. Причины описаны в [главе 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/).

### Decodes и описания

Каждый код в dimension должен иметь понятное описание, `decode`. Опытным моделистам это кажется лишним: они привыкли убирать повторы через справочники. Но dimension хранит то, что пользователи хотят видеть в отчётах и выпадающих списках. Авторы просят отбросить миф, что бизнес любит коды: новички теряются в бессмысленных списках.

Описания обычно можно взять из операционных систем. Если их там нет, их дают бизнес-партнёры, и нужно решить, кто поддерживает их качество. Не прячьте расшифровки в семантическом слое BI-инструмента: хранить их как данные в dimension. Тогда подписи одинаковы во всех BI-инструментах компании.

### Conformity commitment

Команда обязана использовать общие `conformed dimensions` во всех процессах. Без них каждый процесс показывает свои показатели несовместимо с другими (`stovepipe`). Правило верно и для подхода Kimball, и для hub-and-spoke архитектуры.

## Как проводить design review

По опыту авторов, ревью занимает два дня сфокусированной работы.

**До встречи**

- Позовите моделистов, BI-разработчиков и знатоков бизнеса. Не зовите 25 человек.
- Назначьте ведущего (`facilitator`) и договоритесь о scope.
- Заблокируйте два дня и одну комнату с доской. Все остаются до конца.
- Дайте домашнее задание: каждый присылает ведущему топ-5 проблем полными предложениями. Так меньше риск `group think`.

**Во время встречи**

- Не защищайте прошлые решения. Уберите ноутбуки и телефоны.
- Потратьте первый час на разбор текущей модели. Назначьте секретаря.
- Начните с общей картины: `bus matrix`, один процесс, его grain, потом dimensions. Сложное не откладывайте на конец второго дня.
- Помните: главное — принятие бизнесом. Рисуйте примеры строк с данными.
- Закончите итогами: кто что делает и к какому сроку.

**После встречи**

- Назначьте ответственных за нерешённые вопросы. Оцените цену и пользу улучшений и составьте план.
- Пересматривайте модели каждые 12–24 месяца. Изменения — признак успеха, а не провала.

## Разбор черновика: что было не так

В черновике fact ссылался на счёт, клиента, организацию продаж, канал и тариф. Дата счёта и номер линии лежали в dimension счёта. Ещё в fact были YTD и текстовый код типа тарифа.

![Ошибки черновика биллинга и их исправления после ревью](/assets/data-warehouse-toolkit/ch11-design-review.png)

| Что было | Что сделали | Почему |
|---|---|---|
| Grain «один счёт в месяц» | Grain «одна линия на счёте» | У каждой линии свои метрики |
| Dimension счёта | `bill_number` — degenerate dimension | Строк почти столько же, сколько в fact |
| Нет date dimension | Дата счёта в fact, date dimension в роли bill date | У fact нужна явная дата |
| Канал в отдельной таблице | Канал внутри `sales organization` | Лишний snowflake и двойной join |
| Код типа тарифа в fact | Код и описание в `rate plan` | Текст хранят в dimension |
| Ключи источника как primary key | `surrogate key` везде | Единый подход к ключам |
| YTD в fact | YTD убрали | Не additive, риск двойного счёта |
| Только коды | Понятные названия | Бизнес читает названия |

Сначала пересмотрели grain. Документация и профилирование источника показали, что самый детальный уровень — линия на счёте. Команда возражала: линия уже есть в dimension счёта. Но у каждой линии свои метрики, и команда согласилась. Ключ линии перенесли в fact.

Потом проверили dimension счёта. Каждая строка счёта в fact порождала строку в ней. Строк было бы почти поровну: многие клиенты платят за одну линию. Поэтому номер счёта стал degenerate dimension, а дата счёта ушла в fact и связана с date dimension в роли даты счёта (`role-playing dimension`).

> **Пояснение:** `role-playing dimension` — одна физическая таблица, которую fact использует несколько раз под разными именами. В практике ниже `dim_date` служит и датой счёта, и сроком оплаты.

Канал продаж был лишним snowflake: fact ссылался и на организацию продаж, и на канал. Атрибуты канала перенесли в `sales organization`, ключ канала убрали.

У линии один клиент, одна организация продаж и один тариф, поэтому в теории всё можно слить в `service line`. Тогда осталось бы две dimensions: дата и линия. Но линий миллионы, и их число растёт. Поэтому клиента, организацию продаж и тариф оставили отдельными сущностями. Книга называет их `mini-dimensions` линии.

> **Пояснение:** здесь `mini-dimension` значит небольшие отдельные dimensions рядом с большой dimension линии.

Остальное: `surrogate key` везде, а коды источника остались как `natural key` и атрибуты; YTD пользователь считает в запросе по году из date dimension или в BI-инструменте. Осталось разобраться с изменениями атрибутов (`SCD`).

## Переделка существующих структур

Исправить ошибки в работающем хранилище сложнее, чем найти их. Книга разбирает три случая.

- **Новый атрибут.** Если это `SCD type 1`, добавить его почти безболезненно. Так же просто, если значения нужны только с этого момента, а для истории стоит «Нет данных», но анализ усложняется. Если нужен `type 2` с историей, работы заметно больше: добавляют версии строк dimension и пересчитывают ключи в части строк fact.
- **Переход на conformed dimensions.** Как в [главе 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/), минимум нужно заново обработать все строки fact под новые ключи.
- **Отчёты и BI.** View между BI и таблицами помогают, но обычно не защищают полностью.

Взвесьте цену и пользу. Варианты: улучшить текущие таблицы, начать заново или оставить как есть. Удобный момент для переделки — смена источника или BI-инструмента.

## Geographic location dimension

У телеком и коммунальных компаний во многих dimensions есть точное место: улица, город, индекс, широта и долгота. Дизайнеры иногда придумывают одну мастер-таблицу адресов как `outrigger` к линии, оборудованию, сетевой инфраструктуре, недвижимости и клиентам.

Стандартизировать адреса полезно, но это задача `ETL` в back room. Пользователям не нужна единая таблица всех адресов. География живёт как атрибуты внутри разных dimensions: адреса в них почти не пересекаются, а общая таблица замедлит запросы. Шире: общие абстрактные dimensions вредят простоте и скорости в presentation area. За кулисами, в ETL, они допустимы.

## Итоги главы

- Design review проверяет модель по чеклисту вместе с командой и бизнесом.
- Первый вопрос ревью — какой grain у fact table. Ответ один для всех и самый детальный для процесса.
- В fact лежат только факты одного grain. YTD убирают, текстовые флаги и коды живут в dimension.
- Dimensions делают плоскими. Snowflake, centipede fact и строки с колонкой `level` вредят понятности и скорости.
- Номер документа — degenerate dimension. Dimension размером с fact скрывает degenerate dimension.
- Нужны surrogate keys (кроме date dimension), описания кодов и conformed dimensions.
- У fact есть явная date dimension. Колонки `month_1`...`month_12` заменяют строками.
- Переделка готовых таблиц дорога, особенно type 2 атрибут и переход на conformed dimensions.
- Общую dimension адресов в presentation area не строят: география лежит атрибутами в dimensions.

## Ключевые термины

| Термин | Значение |
|---|---|
| Design review | Проверка модели по чеклисту с командой и бизнесом |
| Service line | Телефонный номер, линия связи |
| Degenerate dimension | Номер документа в fact без отдельной таблицы |
| Role-playing dimension | Одна dimension в нескольких ролях |
| Snowflake | Нормализованная dimension. Обычно не нужна |
| Centipede fact table | Fact с десятками внешних ключей |
| Year-to-date (YTD) | Накопленная сумма с начала года. Не additive |

## Что это значит на практике

- Перед ревью запишите grain одним предложением. Потом сверьте с ним каждую колонку fact.
- Колонки `ytd_*` и `*_flag` в fact — повод для вопроса. Обычно им место в запросе или в dimension.
- В `dbt` тест `relationships` проверяет ключи. Тест `unique` на сочетании ключей проверяет grain.
- Если dimension почти такого же размера, как fact, ищите в ней degenerate dimension.
- Не отказывайтесь от surrogate keys ради «простоты»: источник меняет коды.
- Колонки `month_1`...`month_12` из источника превращайте в строки при загрузке.
- Храните расшифровки кодов в таблице, а не в семантическом слое BI.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём модель биллинга

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d::DATE AS full_date,
       month(d) AS month_number, year(d) AS year_number
FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1,'Анна','Москва'),(2,'Борис','Москва'),(3,'Вера','Казань'),
    (4,'Глеб','Казань'),(5,'Дина','Тверь'),(6,'Егор','Тверь')
) t(customer_key, customer_name, city);

-- география как атрибуты dimension: город -> регион (без общей location-таблицы)
CREATE TABLE dim_service_line AS
SELECT l AS service_line_key,
       '+7-9' || lpad((l * 1117)::VARCHAR, 3, '0') || '-0000' AS phone_number,
       CASE WHEN l % 3 = 1 THEN '495' WHEN l % 3 = 2 THEN '843' ELSE '482' END AS area_code,
       CASE WHEN l % 3 = 1 THEN 'Москва' WHEN l % 3 = 2 THEN 'Казань' ELSE 'Тверь' END AS city,
       CASE WHEN l % 3 = 1 THEN 'Центр' WHEN l % 3 = 2 THEN 'Поволжье' ELSE 'Центр' END AS region,
       DATE '2022-01-01' + (l * 40)::INT AS activation_date
FROM range(1, 11) t(l);

CREATE TABLE dim_rate_plan AS
SELECT * FROM (VALUES
    (1,'Старт',  'P', 'Предоплата',  300, 30.0),
    (2,'Оптимум','C', 'Контракт',    800, 50.0),
    (3,'Макси',  'C', 'Контракт',   2000, 80.0)
) t(rate_plan_key, plan_name, plan_type_code, plan_type_description, plan_minutes_allowed, monthly_fee);

-- канал продаж внутри sales organization (без snowflake)
CREATE TABLE dim_sales_org AS
SELECT * FROM (VALUES
    (1,'Салон Центр','Розница'),
    (2,'Онлайн-магазин','Онлайн')
) t(sales_org_key, sales_org_name, sales_channel_name);

-- grain: одна линия на одном счёте (месяц)
CREATE TABLE fact_billing AS
WITH x AS (
    SELECT l AS service_line_key, m,
           1 + (l - 1) % 6 AS customer_key,
           1 + l % 3 AS rate_plan_key,
           1 + l % 2 AS sales_org_key,
           make_date(2024, m, 1 + ((1 + (l - 1) % 6) % 3) * 10) AS bill_date,
           100 + (l * 37 + m * 91) % 400 AS total_minutes,
           (l * 13 + m * 7) % 40 AS roam_minutes,
           (l * 53 + m * 17) % 300 AS message_count,
           500 + (l * 211 + m * 97) % 4000 AS data_mb
    FROM range(1, 11) a(l), range(1, 7) b(m)
)
SELECT strftime(bill_date, '%Y%m%d')::INT AS bill_date_key,
       strftime(bill_date + 20, '%Y%m%d')::INT AS due_date_key,
       x.customer_key, x.service_line_key, x.sales_org_key, x.rate_plan_key,
       'B-' || x.customer_key || '-' || lpad(x.m::VARCHAR, 2, '0') AS bill_number,
       x.total_minutes, x.roam_minutes, x.message_count, x.data_mb,
       p.monthly_fee AS month_service_charge,
       round(x.message_count * 0.05, 2) AS message_charge,
       round(x.data_mb * 0.01, 2)       AS data_charge,
       round(x.roam_minutes * 0.5, 2)   AS roaming_charge,
       round((p.monthly_fee + x.message_count * 0.05 + x.data_mb * 0.01 + x.roam_minutes * 0.5) * 0.1, 2) AS taxes
FROM x
JOIN dim_rate_plan p USING (rate_plan_key);
```

### Шаг 2. Проверяем grain

```sql
-- должно вернуть 0 строк: линия встречается один раз на счёте
SELECT bill_number, service_line_key, count(*)
FROM fact_billing
GROUP BY bill_number, service_line_key
HAVING count(*) > 1;

-- 60 строк fact (10 линий x 6 месяцев), но счетов меньше: в счёте несколько линий
SELECT count(*) AS fact_rows, count(DISTINCT bill_number) AS bills FROM fact_billing;
```

### Задания

**1.** Degenerate dimension. Найдите средний счёт: сумму по `bill_number`, число линий и общую сумму. Это заменяет dimension `bill`.

<details>
<summary>Решение</summary>

```sql
WITH bills AS (
    SELECT bill_number,
           count(*) AS lines,
           sum(month_service_charge + message_charge + data_charge + roaming_charge + taxes) AS bill_total
    FROM fact_billing
    GROUP BY bill_number
)
SELECT count(*) AS bills, round(avg(lines), 2) AS avg_lines_per_bill,
       round(avg(bill_total), 2) AS avg_bill_total
FROM bills;
```

Отдельная таблица `bill` не нужна. Номер счёта в fact группирует линии.
</details>

**2.** Выручка по типу тарифа и каналу продаж. Канал лежит в `dim_sales_org`, тип тарифа в `dim_rate_plan`. Нужен один `JOIN` на dimension.

<details>
<summary>Решение</summary>

```sql
SELECT p.plan_type_description, s.sales_channel_name,
       round(sum(f.month_service_charge + f.message_charge + f.data_charge + f.roaming_charge), 2) AS revenue
FROM fact_billing f
JOIN dim_rate_plan p USING (rate_plan_key)
JOIN dim_sales_org s USING (sales_org_key)
GROUP BY ALL
ORDER BY p.plan_type_description, s.sales_channel_name;
```
</details>

**3.** YTD без хранения. Посчитайте выручку по месяцам счёта и накопленный итог с начала года с помощью window-функции.

<details>
<summary>Решение</summary>

```sql
WITH m AS (
    SELECT d.month_number,
           round(sum(f.month_service_charge + f.message_charge + f.data_charge + f.roaming_charge), 2) AS revenue
    FROM fact_billing f
    JOIN dim_date d ON d.date_key = f.bill_date_key
    GROUP BY d.month_number
)
SELECT month_number, revenue,
       round(sum(revenue) OVER (ORDER BY month_number), 2) AS revenue_ytd
FROM m
ORDER BY month_number;
```

Если хранить YTD в fact, сумма по двум датам даст двойной счёт.
</details>

**4.** Role-playing dimension. Используйте `dim_date` дважды: как дату счёта и как срок оплаты. Найдите счета, срок оплаты которых попадает на другой месяц.

<details>
<summary>Решение</summary>

```sql
SELECT bill_number, bd.full_date AS bill_date, dd.full_date AS due_date
FROM fact_billing f
JOIN dim_date bd ON bd.date_key = f.bill_date_key
JOIN dim_date dd ON dd.date_key = f.due_date_key
WHERE bd.month_number <> dd.month_number
GROUP BY ALL
ORDER BY bill_date, bill_number
LIMIT 10;
```

Это одна физическая таблица в двух ролях. В BI делают два view: `dim_bill_date` и `dim_due_date`.
</details>

**5.** Non-additive и география. Посчитайте долю роуминга как `sum(roam)/sum(total)` по региону. Сравните со средним долей по строкам. Почему они различаются?

<details>
<summary>Решение</summary>

```sql
SELECT sl.region, sl.city,
       round(100.0 * sum(f.roam_minutes) / sum(f.total_minutes), 2) AS roam_pct_correct,
       round(100.0 * avg(f.roam_minutes * 1.0 / f.total_minutes), 2) AS roam_pct_avg_of_ratios
FROM fact_billing f
JOIN dim_service_line sl USING (service_line_key)
GROUP BY sl.region, sl.city
ORDER BY sl.region, sl.city;
```

Первое значение взвешено по минутам. Среднее долей даёт одинаковый вес линиям с малым и большим числом минут. Храните компоненты (числитель и знаменатель). Не храните готовый процент.
</details>

## Вопросы для самопроверки

1. Почему первый вопрос design review — «какой grain у fact table»? Что будет, если команда отвечает по-разному?
2. Почему команда заменила grain «один счёт в месяц» на «одна линия на одном счёте»? Что на это указало?
3. Как понять, что в dimension спрятан degenerate dimension? Куда тогда перенести номер счёта?
4. Почему year-to-date в fact table опасен? Как получить YTD без хранения?
5. Почему описания кодов лучше хранить в dimension, а не в семантическом слое BI-инструмента?
6. Почему авторы не советуют общую dimension адресов в presentation area? Где такая таблица допустима?

Предыдущая: [Глава 10. Финансовые услуги](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/). Следующая: [Глава 12. Транспорт](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/).
