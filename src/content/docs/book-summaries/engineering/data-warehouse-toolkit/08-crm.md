---
title: "The Data Warehouse Toolkit, глава 8: CRM"
head:
  - tag: title
    content: "CRM и customer dimension: конспект Kimball | Инжиниринг Данных"
description: "Конспект главы 8 The Data Warehouse Toolkit: customer dimension, bridge table, behavior study group, timespan fact table, MDM. Практика в DuckDB."
sidebar:
  order: 8
  label: "8. CRM"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** CRM нужен единый взгляд на клиента. Для него авторы строят одну conformed `customer dimension`: очень широкую, глубокую и собранную из многих источников. Остальное в главе — приёмы вокруг неё: атрибуты клиента, `bridge table`, модели сложного поведения и способы свести источники.

## О чём глава

Глава 7 ([Бухгалтерия](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/)) показала иерархии, в том числе ragged. Эта глава отвечает на вопрос: как смоделировать клиента — самую трудную dimension в DW/BI. Приёмы работают в любой отрасли, поэтому bus matrix авторы не рисуют.

- Атрибуты клиента: имена, адреса, даты, сегменты, теги поведения.
- Bridge table, `outrigger` и иерархии клиентов.
- Cohort, `step dimension`, `timespan fact table`.
- Сведение источников и запрет на соединение двух fact table.

![Учебная схема CRM для практики: fact_orders, customer dimension с версиями, mini-dimension demographics, bridge с тегами клиента и dim_date](/assets/data-warehouse-toolkit/ch08-crm-star.png)

Схема — наш учебный пример для практики, а не рисунок книги. Читайте её от `fact_orders`: заказ ссылается на версию клиента (`customer_key`), на профиль в mini-dimension (`demo_key`, см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)) и на дату. Теги клиента лежат в bridge table.

## CRM: обзор

CRM — переход от ориентации на продукт к ориентации на нужды клиента. Идея простая: чем лучше вы знаете клиентов, тем лучше держите с ними долгие и выгодные отношения. Для этого нужен единый взгляд на каждого клиента. Придётся свести до 100 источников, в основном внешних, с разным grain и несовместимыми атрибутами. Как и для всего DW/BI (см. [главу 17](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/)), нужны видение и совместная поддержка бизнеса и IT: CRM меняет каналы продаж и мотивацию.

### Операционный и аналитический CRM

- **Operational CRM** синхронизирует процессы с клиентом: контакт, предложение, покупка, оплата, поддержка.
- **Analytic CRM** опирается на хранилище: оно интегрирует эти данные, чтобы оценивать прошлые решения и искать up-sell и cross-sell.

Модели и scores из хранилища возвращаются туда, где ведут отношения: менеджеру, в колл-центр, на сайт (замкнутый цикл). CRM растит хранилище, усложняет ETL и делает conformed customer dimension ещё важнее.

## Атрибуты customer dimension

Авторы называют `customer dimension` самой трудной dimension. Она глубокая (миллионы строк, у крупнейших компаний больше 100 миллионов), широкая (десятки и сотни атрибутов), быстро меняется и собирается из внутренних и внешних источников.

### Разбор имён и адресов

Операционные системы часто хранят имя и адрес в общих колонках: `Name-1`..`Name-3`, `Address-1`..`Address-6`. Авторы считают такие колонки почти бесполезными для сегментации и источником ошибок. Нельзя понять, какое имя первое и как обратиться к человеку. В одной колонке бывают несколько клиентов, а адрес нельзя проверить по правилам почты.

Книга советует делить имя и адрес на максимум мелких частей: обращение, имя, фамилия, суффикс, улица, город, индекс, части телефона. ETL разбирает грязные значения, приводит к стандарту (`Rd` в `Road`) и проверяет (индекс подходит к штату).

### Международные имена и адреса

Для чужих алфавитов нужен не другой шрифт, а другой набор символов. ASCII мал, основа решения — `Unicode`. Он нужен на всём пути: от ОС и ETL до BI-серверов и браузеров. Книга советует проверить цепочку: ввести имена со спецсимволами в старой системе и найти их в итоговом отчёте.

#### Цели международного DW/BI

- **Универсальность.** Переводить сами dimensions опасно: сортировка отличается, итоги не сходятся. Лучше строить отчёт на одном языке, а оформление переводить после (localization, см. [главу 12](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/)).
- **Качество от начала до конца.** За имена и адреса отвечает вся цепочка, не только хранилище.
- **Культурная корректность.** Нужно знать, где фамилия, и как обращаться к человеку.
- **Ответ в реальном времени.** Приветствие для оператора нужно за 5 секунд, поэтому держат hot response cache с готовым ответом на клиента.
- **Телефоны и другие адреса.** Телефон показывают по-разному в зависимости от места звонка.

### Даты клиента

Даты в customer dimension (первая покупка, дата рождения) делают внешними ключами на dimension `date`. Так их можно группировать по сезонам и фискальным периодам. Каждую роль задают отдельным view, например «дата первой покупки» (role-playing, см. [главу 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). Это вариант `outrigger` (о нём ниже).

### Aggregated facts как атрибуты dimension

Бизнес хочет отбирать клиентов по метрикам: «потратили больше N за прошлый год». Вместо двух запросов можно хранить агрегат в dimension (`aggregated fact as dimension attribute`) и фильтровать как по городу. Эти атрибуты нужны для фильтров и подписей, не для расчётов. Нагрузка ложится на ETL: значения должны совпадать с fact. Авторы советуют брать только частые атрибуты и обновлять их редко: «расходы за прошлый год» дешевле, чем «с начала года». Иногда вместо суммы (или вместе с ней) хранят описание, например `High Spender`.

### Сегментация и scores

Сегменты — сильные атрибуты клиента: возраст или этап жизни, доход, статус (новый, активный, закрытый), источник привлечения. Scores строят статистические модели: они группируют клиентов по покупкам, платежам, склонности к оттоку и риску дефолта.

### Временной ряд behavior tags

Популярный способ профилировать клиента — RFI (или RFM): `recency` (дней с последнего заказа), `frequency` (число заказов, обычно за год) и `intensity` (сумма расходов за тот же период). Когда клиентов миллионы, специалист по data mining находит кластеры, и их называют `behavior tags`. Пример книги: `A` — частый покупатель с хорошим кредитом и малым числом возвратов, `B` — такой же, но с большим числом возвратов. В каждый период клиент получает тег ближайшего кластера: `C C C D D A A A B B`.

Теги нельзя складывать, но можно искать: «был A три–пять периодов назад, а недавно стал B» — клиент начал возвращать товар. Авторы предупреждают: не храните теги как строки fact, иначе запрос превращается в цепочку коррелированных подзапросов. Книга советует хранить ряд как колонки customer dimension (`positional design`: колонка на каждый период). Добавьте колонку со всеми тегами подряд, `CCCDDAAABB`, и ищите по шаблону вроде «D, затем B».

### Data mining и DW/BI

Команда data mining — хороший клиент хранилища, но скорости не совпадают: decision tree обрабатывает сотни записей в секунду, а большой отчёт из многих fact table (drill across) на миллионы «наблюдений о клиенте» так быстро данные не отдаёт. Книга советует записать набор в файл и отдать команде.

### Счёт клиентов при type 2

При `SCD` type 2 каждое изменение атрибутов даёт новую строку, поэтому у клиента несколько строк (см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)), и счёт завышается. Выход: `COUNT DISTINCT` по постоянному идентификатору клиента (`durable key`). Для счёта по свежим значениям нужен индикатор текущей строки (`is_current`). Чтобы посчитать клиентов на дату в прошлом, ограничивают `effective_date <= дата` и `expiration_date >= дата`. Знаки сравнения зависят от правил дат в ETL.

### Outrigger для набора атрибутов с низкой cardinality

В [главе 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) книга советовала не делать `snowflake`: он усложняет работу и замедляет просмотр. Исключение — `outrigger`, отдельная таблица, на которую ссылается dimension. Пример: внешний поставщик даёт 150 демографических атрибутов по округу проживания, для всех клиентов округа они одинаковы. Причины: другой grain, меньшая ценность, другое время загрузки и экономия места. Если BI-инструмент требует чистый star schema, outrigger прячут под `view`. Авторы предупреждают: если в дизайне много outrigger, вы слишком нормализовали модель.

### Иерархии клиентов

Самое трудное для бизнес-клиентов — внутренняя иерархия: площадка, региональный офис, штаб бизнес-единицы, материнская компания. Приёмы те же, что в [главе 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/):

- **Фиксированная глубина.** Три уровня — три атрибута в dimension.
- **Немного переменная глубина.** Значение нижнего уровня копируют в верхние атрибуты, чтобы итоги по любому уровню сходились.
- **Ragged hierarchy.** Глубина неизвестна. Нужен приём из главы 7 (`bridge table`). Хуже всего общие колонки `Level-1`, `Level-2`: по ним нельзя понять, как фильтровать.

## Bridge tables для multivalued dimensions

Сначала выбирают grain fact table, потом добавляют dimensions, которые ему верны. Поэтому dimension обычно даёт одно значение на строку fact. Но бывают «проблемные» dimensions с несколькими значениями на том же grain: хобби, диагнозы пациента, опции автомобиля, совладельцы счёта, контакты компании. Выбирают из двух решений:

| Подход | Плюс | Минус |
|---|---|---|
| `Positional design`: колонка на каждое значение | Простые запросы, BI видит колонки | Колонки кончаются, в строке много NULL |
| `Bridge table` | Сотни и тысячи значений, строки только для реальных значений | Сложный запрос, его надо прятать от пользователей |

Авторы предупреждают: SQL для bridge может выходить за возможности BI-инструментов. Построение таких bridge разбирает [глава 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/).

> **Пояснение:** Как делить числовые факты между значениями bridge (`weighting factor`, сумма весов равна 1), книга объясняет в [главе 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/). Этот приём есть в практике ниже.

### Bridge для разреженных атрибутов

`Positional design` удобен: BI легко показывает колонки, а bitmap-индексы ускоряют колонки с малым числом значений. Он масштабируется примерно до 100 колонок. Если атрибутов больше и новые появляются часто, книга рекомендует `bridge table`: outrigger и mini-dimension такой объём не тянут. Пример — кредитная заявка как открытые пары «имя — значение» (доход, иждивенцы, банкротство и сотни других). Значение может быть числом, текстом или ссылкой, поэтому его хранят как текст. Bridge связывает заявку с dimension элементов (название, тип, значение).

### Bridge для нескольких контактов клиента

У крупных клиентов много контактов с разными ролями: руководитель, закупщик, пользователь. Их число неизвестно, поэтому подходит bridge с ролью контакта. Авторы предупреждают: не делайте из dimension контактов свалку для всех сотрудников и граждан.

## Сложное поведение клиента

Четыре темы: cohort, последовательности, интервалы и пометки в fact table.

### Behavior study groups для cohort

Вопросы о клиентах быстро усложняются, и один SQL уже не справляется. Тогда сохраняют набор клиентов из запроса (топ-100, потратили больше $1 000, получили тестовое предложение) и используют его повторно. Этот набор — `behavior study group`:

1. Запустите запрос и найдите клиентов.
2. Сохраните их `durable key` в физическую таблицу из одной колонки.
3. Присоединяйте её к customer dimension по `durable key` и фильтруйте любую fact table с ключом клиента.

Из-за `durable key` группу не ломают новые версии клиента. Join можно спрятать под `view`. Группы легко объединять через union, пересечение и разность: пересечение проблемных клиентов двух месяцев даёт тех, кто был проблемой два месяца подряд. Компромисс: нужен интерфейс для таких таблиц, они лежат рядом с fact table, и это добавляет работы DBA.

### Step dimension для последовательного поведения

В большинстве хранилищ нет последовательных процессов. Пример — веб-сессия, собранная из событий страниц по cookie. Место шага в сессии показывает `step dimension`: абстрактная dimension, заданная заранее, с колонками «сколько всего шагов», «номер шага», «сколько шагов осталось». Для сессии из трёх шагов (всего, номер, осталось) это строки (3, 1, 2), (3, 2, 1), (3, 3, 0). В примере книги она подключена к fact «событие страницы» в трёх ролях: вся сессия, успешная покупка, брошенная корзина. Так можно взять только первую страницу успешных покупок или последнюю страницу брошенных корзин.

### Timespan fact tables

Иногда нужен точный статус клиента в любой момент прошлого: был ли он под fraud alert, когда ему отказали в кредите? Решение — transaction fact table со всеми событиями клиента и двумя метками времени: момент события и момент следующего события. Интервалы идут подряд без «дыр», и внутри интервала статус не меняется. Это `timespan fact table`. Запросы простые:

- статус в момент `t`: `begin <= t AND t < end`;
- клиенты под alert хотя бы раз в 2013 году: `begin <= конец_года AND end >= начало_года`. Одно условие покрывает все случаи пересечения с годом.

#### Администрирование двух меток времени в ETL

Конец интервала должен равняться началу следующего. Конец на один «тик» меньше позволил бы писать `BETWEEN`, но событие может попасть в щель. Новая строка добавляется в два шага. Сначала у текущей строки конец ставят в дату далеко в будущем, не в `NULL`: `NULL` создаёт проблемы в условиях. После вставки ETL ставит предыдущей строке конец, равный началу новой. ETL делает больше работы, но запросы проще.

### Метки удовлетворённости в fact table

Удовлетворённость клиентов — второй по важности KPI после прибыли, а в госорганах первый. Книга называет два способа для текстовых данных, в зависимости от числа атрибутов и разреженности, но показывает один: `positional design`, если список ограничен и стабилен. Пример — dimension удовлетворённости авиапассажиров (флаги «задержка прилёта», «потерян багаж»): её подключают к fact table полётов из [главы 12](/book-summaries/engineering/data-warehouse-toolkit/12-transportation/).

### Метки аномальных сценариев в fact table

`Accumulating snapshot` (одна строка на процесс с датами его этапов) строится на датах стандартного сценария: заказ создан, отправлен, доставлен, оплачен (см. [главу 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). Это работает, когда 90% заказов и больше идут без исключений. Редкие отклонения (груз промок, клиент отказался, дело дошло до суда) в сценарий не входят и не должны. Добавьте в snapshot dimension статуса доставки и пометьте такую строку статусом `Weird`. Полную историю аналитик берёт из парной transaction fact table по номеру заказа и строки. Её dimension транзакций (`Flat Tire`, `Damaged Shipment`, `Lawsuit`) растёт, но остаётся ограниченной и стабильной.

## Подходы к интеграции данных о клиенте

Есть два пути: одна customer dimension из записей всех источников или несколько customer dimensions, связанных conformed-атрибутами.

### MDM: единая customer dimension

Одну dimension можно собрать из лучших источников. Но у клиента обычно несколько идентификаторов в разных системах, а ввод данных плохо проверяется. Книга описывает два стиля master data management (MDM): в `enterprise MDM` центральная система создаёт единого клиента, но авторы пишут, что так бывает редко. Чаще хранилище само извлекает несовместимые файлы клиентов и строит `downstream MDM`.

Главная работа — matching и дедупликация: они убирают расходы на дубли и недоставленную почту и не дают завышать число клиентов. Matching сложнее, чем кажется: нужны нечёткая логика и большие справочники. Группировка клиентов по домохозяйствам (`householding`) описана в [главе 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/).

### Partial conformity нескольких customer dimensions

В крупной компании бывает до 20 внутренних и 50 внешних источников клиентов. Их grain и качество различаются, а общего ключа нет. В идеале строят одну полную conformed dimension (см. [главу 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)). Для десятков dimensions это невозможно. Авторы предлагают лёгкий вариант: dimensions не обязаны совпадать, им достаточно общих атрибутов с одинаковыми названиями и значениями. Вводить их можно постепенно: сначала `customer category` в каждую dimension, не меняя её grain, потом город, округ, страна. На любом шаге можно делать `drill across` по dimensions с общим атрибутом.

## Как избежать fact-to-fact joins

В fact продаж и fact поддержки есть ключ клиента, и возникает соблазн соединить их через общую dimension в одном запросе. Но join «многие к одному ко многим» вернёт неверный ответ из-за разной cardinality fact table, и ни один вариант inner или outer join его не исправит. Пример книги: fact рассылок и fact ответов. Не на каждую рассылку есть ответ, и бывают ответы без рассылки.

> **Пояснение:** Пример: у клиента 2 рассылки и 3 ответа. Один join даст 2 × 3 = 6 строк, и суммы каждой fact table вырастут.

Выход — `drill across` (см. [главу 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)): запросите каждую fact table отдельно и соедините результаты через outer join. Если бизнес часто объединяет одни и те же данные, постройте consolidated fact table (см. [главу 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/)). Но и для неё нужны правила для разной cardinality: брать все рассылки и ответы или только пары.

## Low latency: проверка реальностью

Поведение клиента за последние минуты интересно, но чем ближе данные к real time, тем хуже их качество. При batch раз в сутки приходят полные наборы транзакций, и у ETL есть время на все проверки (см. [главу 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)). При загрузке много раз в день заказ может прийти без пройденной проверки кредита, а часть ключей не определена, поэтому нужны временные записи в dimension. При мгновенной доставке приходят фрагменты без проверок. Бизнес надо предупредить о компромиссах. Гибрид: быстрая доставка днём и ночной batch, который исправляет дневные проблемы. Влияние на ETL — в [главе 20](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/).

## Итоги главы

- CRM нужен единый взгляд на клиента, и хранилище стоит в центре и operational, и analytic CRM.
- Customer dimension — самая трудная dimension: глубокая, широкая и собранная из многих источников.
- Имена и адреса разбирают на части, стандартизируют и проверяют в ETL, а не хранят в общих колонках.
- Международные данные требуют Unicode на всём пути и перевода отчёта после построения.
- Агрегаты, сегменты и behavior tags хранят в customer dimension, но только для фильтров и подписей.
- Для многих значений на клиента выбирают `positional design` (проще, до 100 колонок) или `bridge table` (масштабируется, сложнее).
- Cohort хранят как таблицу `durable key`, а `timespan fact table` ведёт непрерывные интервалы с двумя метками времени.
- Источники клиента сводят через MDM или partial conformity, а две fact table соединяют только через `drill across`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Customer dimension` | Широкая conformed dimension клиента, ядро CRM-анализа |
| `Behavior tag` | Текстовый тег кластера поведения клиента за период |
| `Positional design` | Отдельная колонка на каждое значение или период |
| `Bridge table` | Связь «многие ко многим» между fact и набором значений |
| `Behavior study group` | Таблица `durable key` клиентов для повторного фильтра (cohort) |
| `Timespan fact table` | Fact с парой меток времени: интервал, где статус не менялся |
| MDM | Единая сущность клиента: из центральной системы или построенная в ETL |

## Что это значит на практике

- В `dbt` SCD2 делают через `snapshot`. Он сохраняет `dbt_valid_from` и `dbt_valid_to`.
- Клиентов считайте по `count(DISTINCT customer_id)` (durable key), а не по `customer_key`.
- Для cohort сохраняйте в таблицу только `durable key` и прячьте join под `view`.
- Не соединяйте две fact table через общую dimension. Агрегируйте каждую отдельно и соедините результаты через `FULL OUTER JOIN`.
- В `timespan fact table` конец строки равен началу следующей, а текущая строка заканчивается далёкой датой, не `NULL`.
- Проверяйте веса bridge: `sum(weighting_factor) = 1` для каждого клиента.
- Для клиента без тега добавляйте строку «Без тега», иначе он пропадёт из отчёта.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём customer dimension, mini-dimension и bridge

```sql
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d AS full_date
FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) t(d);

-- SCD type 2: у клиентов 101 и 102 есть история
CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1, 101, 'Анна',   'Москва', 'Standard', DATE '2024-01-01', DATE '2024-06-30', FALSE),
    (2, 101, 'Анна',   'Казань', 'Standard', DATE '2024-07-01', DATE '9999-12-31', TRUE),
    (3, 102, 'Борис',  'Москва', 'Standard', DATE '2024-01-01', DATE '2024-03-31', FALSE),
    (4, 102, 'Борис',  'Москва', 'Premium',  DATE '2024-04-01', DATE '9999-12-31', TRUE),
    (5, 103, 'Вера',   'Казань', 'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (6, 104, 'Глеб',   'Тверь',  'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (7, 105, 'Дина',   'Москва', 'Premium',  DATE '2024-01-01', DATE '9999-12-31', TRUE),
    (8, 106, 'Егор',   'Тверь',  'Standard', DATE '2024-01-01', DATE '9999-12-31', TRUE)
) t(customer_key, customer_id, customer_name, city, segment, effective_date, expiration_date, is_current);

-- mini-dimension: банды вместо точных значений
CREATE TABLE dim_demographics AS
SELECT * FROM (VALUES
    (1, 'до 50 тыс',     '18-30', 'редко'),
    (2, '50-100 тыс',    '31-45', 'регулярно'),
    (3, 'выше 100 тыс',  '46+',   'часто')
) t(demo_key, income_band, age_band, purchase_frequency_band);

CREATE TABLE dim_tag AS
SELECT * FROM (VALUES
    (0, 'Без тега'),
    (1, 'Любит акции'),
    (2, 'Покупает онлайн'),
    (3, 'Семья')
) t(tag_key, tag_name);

-- bridge: сумма weighting_factor по клиенту равна 1
CREATE TABLE bridge_customer_tag AS
SELECT * FROM (VALUES
    (101, 1, 0.5), (101, 2, 0.5),
    (102, 2, 1.0),
    (103, 1, 1.0/3), (103, 2, 1.0/3), (103, 3, 1.0/3),
    (104, 3, 1.0),
    (105, 1, 1.0),
    (106, 0, 1.0)
) t(customer_id, tag_key, weighting_factor);

-- grain: один заказ. Версия клиента выбирается по дате заказа
CREATE TABLE fact_orders AS
WITH o AS (
    SELECT i,
           101 + i % 6 AS customer_id,
           DATE '2024-01-01' + ((i * 7) % 360)::INT AS order_date,
           50 + (i * 13) % 200 AS order_amount
    FROM range(0, 120) t(i)
)
SELECT 'O-' || lpad(o.i::VARCHAR, 4, '0') AS order_number,
       c.customer_key,
       1 + ((o.customer_id - 101) + (o.order_date >= DATE '2024-04-01')::INT) % 3 AS demo_key,
       strftime(o.order_date, '%Y%m%d')::INT AS date_key,
       o.order_amount
FROM o
JOIN dim_customer c
  ON c.customer_id = o.customer_id
 AND o.order_date BETWEEN c.effective_date AND c.expiration_date;
```

### Шаг 2. Проверяем SCD2 и bridge

```sql
-- должно вернуть 120: каждый заказ нашёл ровно одну версию клиента
SELECT count(*) AS orders, count(DISTINCT order_number) AS distinct_orders FROM fact_orders;

-- веса bridge: у каждого клиента сумма равна 1
SELECT customer_id, round(sum(weighting_factor), 6) AS total_weight
FROM bridge_customer_tag GROUP BY customer_id ORDER BY customer_id;
```

### Задания

**1.** Выручка по городам «как было» и «как сейчас». Исторический город берут из версии, привязанной к заказу. Текущий — из строки с `is_current`.

<details>
<summary>Решение</summary>

```sql
SELECT c.city AS city_at_order, cur.city AS city_now, sum(f.order_amount) AS revenue
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
JOIN dim_customer cur ON cur.customer_id = c.customer_id AND cur.is_current
WHERE c.customer_id = 101
GROUP BY ALL
ORDER BY city_at_order;
```

У клиента 101 заказы разделились на два города. Если взять только текущий город, вся выручка уйдёт в Казань.
</details>

**2.** Сколько клиентов? Сравните `count(DISTINCT customer_key)` и `count(DISTINCT customer_id)`.

<details>
<summary>Решение</summary>

```sql
SELECT count(DISTINCT f.customer_key) AS by_surrogate_key,
       count(DISTINCT c.customer_id)  AS by_durable_key
FROM fact_orders f
JOIN dim_customer c USING (customer_key);
```

Surrogate key даёт 8. Это версии. Реальных клиентов 6.
</details>

**3.** Mini-dimension. Покажите средний заказ по `income_band`. Затем покажите, как клиент 101 переходит между бандами после апреля.

<details>
<summary>Решение</summary>

```sql
SELECT d.income_band, count(*) AS orders, round(avg(f.order_amount), 1) AS avg_order
FROM fact_orders f
JOIN dim_demographics d USING (demo_key)
GROUP BY d.income_band
ORDER BY d.income_band;

SELECT (f.date_key >= 20240401) AS after_april, d.income_band, count(*) AS orders
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
JOIN dim_demographics d USING (demo_key)
WHERE c.customer_id = 101
GROUP BY ALL
ORDER BY after_april;
```
</details>

**4.** Bridge. Посчитайте выручку по тегам с `weighting_factor`. Проверьте, что сумма равна общей выручке.

<details>
<summary>Решение</summary>

```sql
WITH rev AS (
    SELECT c.customer_id, sum(f.order_amount) AS revenue
    FROM fact_orders f
    JOIN dim_customer c USING (customer_key)
    GROUP BY c.customer_id
)
SELECT t.tag_name,
       round(sum(r.revenue * b.weighting_factor), 2) AS weighted_revenue,
       sum(r.revenue)                                AS unweighted_revenue
FROM rev r
JOIN bridge_customer_tag b USING (customer_id)
JOIN dim_tag t USING (tag_key)
GROUP BY t.tag_name
ORDER BY weighted_revenue DESC;
```

Сумма `weighted_revenue` равна общей выручке. Сумма `unweighted_revenue` больше: клиенты с несколькими тегами посчитаны много раз.
</details>

**5.** Банд расходов как атрибут. Посчитайте общие расходы клиента и присвойте банд («до 2 000», «2 000-3 000», «выше»). Затем посчитайте клиентов в каждом банде.

<details>
<summary>Решение</summary>

```sql
WITH spend AS (
    SELECT c.customer_id, sum(f.order_amount) AS lifetime_spend
    FROM fact_orders f
    JOIN dim_customer c USING (customer_key)
    GROUP BY c.customer_id
)
SELECT CASE WHEN lifetime_spend < 2000 THEN '1. до 2 000'
            WHEN lifetime_spend < 3000 THEN '2. 2 000-3 000'
            ELSE '3. выше 3 000' END AS spend_band,
       count(*) AS customers
FROM spend
GROUP BY ALL
ORDER BY spend_band;
```

Подберите границы по своим данным. Идея в том, что банд считается при загрузке и хранится как атрибут.
</details>

**6.** Behavior study group. Сохраните в таблицу `cohort_q1_big` клиентов, у которых выручка в I квартале выше 900. Затем посчитайте выручку этой группы во II полугодии.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE cohort_q1_big AS
SELECT c.customer_id
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
WHERE f.date_key < 20240401
GROUP BY c.customer_id
HAVING sum(f.order_amount) > 900;

SELECT count(DISTINCT c.customer_id) AS customers, sum(f.order_amount) AS revenue_h2
FROM fact_orders f
JOIN dim_customer c USING (customer_key)
JOIN cohort_q1_big g ON g.customer_id = c.customer_id
WHERE f.date_key >= 20240701;
```

В группе 4 клиента из 6. Группа хранит durable key `customer_id`. Клиент 101 сменил город в июле, у него новый `customer_key`. Но он всё равно попадает в отчёт за II полугодие.
</details>

## Вопросы для самопроверки

1. Почему общие колонки `Name-1`..`Name-3` и `Address-1`..`Address-6` плохи для хранилища? Что делать вместо них?
2. Когда для многозначного атрибута выбрать `positional design`, а когда `bridge table`?
3. Почему `behavior study group` хранит `durable key`, а не `surrogate key`?
4. Почему в `timespan fact table` конец интервала равен началу следующего, и почему не ставят `NULL`?
5. Почему join двух fact table через общую dimension даёт неверный результат? Как сделать правильно?
6. Чем MDM отличается от partial conformity? Когда подходит второй вариант?

Предыдущая: [Глава 7. Бухгалтерия](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/). Следующая: [Глава 9. HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/).
