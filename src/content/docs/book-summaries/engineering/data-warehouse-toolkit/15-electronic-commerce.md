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

**Главная мысль:** лог веб-сервера становится данными для анализа, когда из отдельных hits собраны сессии, а к привычным dimensions добавлены четыре новые: page, event, session и referral. Авторы строят две `fact table`: на уровне сессии и на уровне события страницы. Clickstream входит в общую `bus matrix`. Прибыльность веба считают на fact продаж, а не на кликах.

## О чём глава

Глава 14 ([Здравоохранение](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/)) разбирала multivalued dimensions и claims. Эта глава отвечает на вопрос: как превратить поток кликов сайта в dimensional model и связать его с остальным хранилищем. Clickstream — это каждое событие страницы, которое записали веб-серверы. Авторы называют его лавиной данных и спрашивают: можно ли согласовать его dimensions и facts в архитектуре `bus matrix`.

Основные темы:

- Источники clickstream: откуда пришёл посетитель, как найти сессию, кто он.
- Четыре новые dimensions: page, event, session, referral.
- Две `fact table` (сессия и событие страницы), `step dimension` и агрегаты.
- Google Analytics, `bus matrix` веб-ритейлера и прибыльность по каналам.

![Star schema clickstream: fact события страницы и fact сессии с общими dimensions](/assets/data-warehouse-toolkit/ch15-clickstream-star.png)

Слева `fact_page_event` (grain: одно событие страницы), справа `fact_session` (grain: одна сессия). Общие dimensions и `session_id` связывают обе таблицы. Схема упрощена под практику ниже. В книге у fact события есть ещё customer, event, promotion и step (в трёх ролях), а дата и время хранятся в двух ролях: UTC и местное время.

## Исходные данные clickstream

Clickstream — это не один источник, а набор меняющихся источников. Форматы логов разные. Необязательные поля в них помогают найти посетителя и сессию. Авторы выделяют три сложности:

- Сайт обслуживают несколько серверов, а их часы не совпадают с точностью до сотой доли секунды. Поэтому логи трудно синхронизировать после записи.
- Данные приходят от разных сторон: из ваших логов, от партнёров, от интернет-провайдеров (ISP) и из поисковых запросов.
- Простой лог `stateless` (без состояния): строка описывает одно получение страницы и не связана с другими. Посетитель к тому же анонимен, пока сам не назовётся.

### Трудности: откуда пришёл посетитель

Авторы называют определение происхождения, сессии и личности посетителя «искусством интерпретации». Кеши браузеров и прокси усложняют его. Посетитель приходит одним из четырёх путей:

- Сайт стоит стартовой страницей браузера. Это редкость, и по логу её не увидеть.
- Поисковый портал: из индекса (возможно, вы платили за размещение) или по слову из содержимого.
- Закладка. Посетитель добавляет её, только когда доверяет сайту.
- Ссылка с другого сайта (`clickthrough`), платная (баннер) или бесплатная. Referring site почти всегда есть в записи. Его сохраняют, чтобы проверять маркетинг и счета за рекламу.

### Как определить сессию

Для веб-анализа каждой сессии нужен свой `session ID`. Авторы сравнивают его с номером чека в супермаркете. Он должен быть в каждой записи действия посетителя. Но HTTP не знает про сессии: в нём нет входа и выхода. Поэтому ID строят другим способом. Его генерирует операционное приложение, а не веб-сервер. Книга описывает пять способов:

| Способ | Слабое место |
|---|---|
| Записи с одного IP подряд (окно, например час) | IP переиспользуют другие посетители, у одного человека он меняется, мешают firewalls |
| Session cookie: живёт, пока открыт браузер | Нельзя понять, что посетитель вернулся позже |
| SSL: есть вход и обмен ключами | Высокая нагрузка, предупреждения браузера, сертификат на каждый хост |
| Session ID в скрытом поле и в URL | Нужен полный контроль над страницами. Сторонняя ссылка рвёт цепочку |
| Persistent cookie: живёт после закрытия браузера | Посетитель может запретить или удалить его |

Вывод авторов: самый надёжный способ — persistent cookie. Неплохо работает и связка session cookie с группировкой записей одного хоста по времени, но ей нужен надёжный алгоритм постобработки. Он же решает, когда результату нельзя доверять.

> **Пояснение:** для группировки по времени нужен порог паузы: пауза длиннее порога начинает новую сессию. В индустрии часто берут 30 минут. Этого числа нет в книге, но практика ниже использует его.

### Кто этот посетитель

Определить конкретного человека — одна из самых трудных задач. Причины:

- Посетители хотят быть анонимными, а данные, которые они вводят, могут быть неверными.
- Cookie указывает на компьютер, а не на человека: им мог пользоваться любой член семьи или сотрудник компании.
- Один человек заходит с рабочего, домашнего компьютера и телефона, и в каждом будет свой cookie.

## Dimensional models для clickstream

Сначала авторы собирают портфель возможных dimensions веб-ритейлера. Одна модель использует лишь часть. Почти все знакомы по прошлым главам: дата, время суток, товар, клиент, promotion и другие. Четыре уникальны для clickstream:

- Page — контекст страницы, на которой произошло событие.
- Event — что произошло на странице.
- Session — диагноз сессии в целом.
- Referral — как посетитель попал на текущую страницу.

### Page dimension: тип страницы, а не каждый показ

Grain этой dimension — страница. Определение гибкое: сайты переходят от статичных страниц к динамическим, где страница уникальна для каждого показа. Авторы допускают, что у динамической страницы есть понятная функция, и описывают страницу через неё. Строка на каждый показ дала бы астрономическое число одинаковых строк. Поэтому статичные страницы получают свою строку, а динамические группируют по функции и типу.

Атрибуты: источник (статичная или динамическая), функция (портал, поиск, описание товара), шаблон, тип позиции (SKU, ISBN), тип графики, анимации и звука, имя файла. Если описание страницы изменилось, строку перезаписывают (`SCD` type 1) или применяют другой тип SCD. Выбор зависит от того, сильно ли отличаются описания и нужна ли история.

Авторы подчёркивают организационный шаг. Веб-дизайнеры, data governance и архитекторы DW/BI вместе назначают коды и атрибуты страницам. В идеале разработчики кладут их в необязательные поля лога. Это фундамент page dimension.

Некоторые компании пишут строку на каждый элемент страницы (больше 10 терабайт в день) или жест игрока (сотни миллионов строк в день). Тогда самая атомарная fact table получает ещё dimensions: элемент, ссылка или игровая ситуация.

### Event dimension: что произошло на странице

Эта небольшая dimension описывает, что случилось на странице. Главные события: открытие страницы, обновление, клик по ссылке и ввод данных. Атрибуты: тип события и его содержимое, которое зависит от приложения.

### Session dimension: итог сессии целиком

Session dimension даёт диагноз сессии в целом:

- `local context` — контекст по текущей странице, например «запрашивает информацию о товаре».
- `session context` — контекст по всей траектории, например «заказывает товар». Обычно его можно определить, только обработав сессию целиком при извлечении данных.
- `success status` — выполнил ли посетитель свою задачу.
- `customer status` — метка клиента на период: «новый клиент», «ценный клиент», «собирается уйти», «в просрочке».

Статусы клиента авторы советуют держать здесь, а не в customer dimension: они меняются за очень короткие периоды. Если их много, их выносят в отдельную `mini-dimension` (небольшую dimension для быстро меняющихся атрибутов). Dimension группирует сессии для вопросов вроде: сколько клиентов смотрели товар перед заказом и не заказали, сколько не закончили заказ и где остановились.

### Referral dimension: как пришёл посетитель

Dimension описывает, как клиент попал на страницу. Данные берут из лога: URL предыдущей страницы, а при поиске — и поисковую строку. Атрибуты: тип (внутри сайта, внешний сайт, поисковая система), referring URL, сайт, домен, тип и текст запроса. Сырые запросы слишком сложные и индивидуальные, поэтому в атрибут кладут упрощённую, очищенную версию. В fact table ключ называется referrer key.

## Fact таблица сессий

Первая fact table имеет grain «одна завершённая сессия клиента». Это намеренный отход от совета начинать с самого детального grain. Причина — размер. Пример авторов: большой сайт получает больше 100 миллионов загрузок страниц в день. Если на сессию приходится 5 страниц, это 20 миллионов сессий. С такого числа строк в день начинать проще.

- Dimensions: дата, время суток, клиент, страница, session, referrer.
- Facts: секунды сессии (`session seconds`), страницы, заказы, единицы, сумма заказов.

Решения, на которые обращают внимание авторы:

- **Две роли даты и времени.** Все сессии записывают в одном часовом поясе (UTC), чтобы синхронизировать серверы и системы. Но нужно и местное время клиента, чтобы видеть, утро это или вечер. Поэтому в fact два foreign key на dimension даты и две метки времени. Часовой пояс в customer dimension не помогает: расчёт местного времени был бы слишком сложным из-за перехода на летнее время. Это должна хранить база, а не BI-приложение. Такая `role-playing dimension` — два view на одну таблицу дат. Метка означает начало сессии, а конец считают по секундам.
- **Полная метка времени вместо time-of-day dimension.** У времени суток нет описательных атрибутов, а на уровне секунд такая dimension была бы огромной. Метки можно вычитать напрямую, даже через границу дней.
- **Page — страница входа.** Вместе с referrer она показывает, как и почему клиент пришёл. Можно добавить и страницу выхода.
- **Causal dimension.** Акции по отдельным товарам здесь не подходят: за сессию клиент видит много товаров, и причин получается много (multivalued). Рыночные условия, общие для всех товаров, подходят.
- **Секунды сессии.** Часто неизвестно, когда клиент ушёл: ввёл другой URL, отошёл на час или закрыл браузер. Лог этого не видит. Авторы советуют назначить последнему шагу небольшое условное число секунд, чтобы не исказить анализ.

## Fact таблица событий страницы

Вторая fact table опускается до самого детального практичного grain: одно событие страницы в сессии. Микро-события вроде картинок отбрасывают (если вы не Yahoo! или eBay). На простых HTML-страницах событие одно: показ страницы. На динамических XML-страницах идёт диалог с посетителем, и событий больше.

Таблица может стать огромной. Авторы советуют не агрегировать её: агрегация неизбежно отбрасывает dimensions. Первая таблица как раз такой агрегат. Она полезна, но по ней нельзя спросить про поведение и отдельные страницы.

Dimensions: дата, время суток, клиент, страница, event, session, `session ID`, step (три роли), товар, referrer, promotion. Facts: `page seconds`, единицы и сумма заказа. Что важно:

- Схема похожа на первую. Авторы называют «скучное» сходство моделей их силой: ПО по всей цепочке использует предсказуемую структуру.
- Page здесь — каждая страница, которую открыл клиент. В этом главное отличие по grain.
- Session ID — `degenerate dimension` (идентификатор без своей таблицы). Он группирует события одной сессии и служит «родительским ключом» для связи с первой fact table. Session dimension описывает классы сессий, а не каждую сессию.
- Dimension товара зависит от сайта: у консалтинга это услуга, у новостей — тема, у аукциона — категория лотов. Рядом ставят promotion, чтобы объяснять изменения спроса.
- `page seconds` — секунды до следующего события. Название отличается от `session seconds` намеренно: это пример внимания к `conformed facts`. Если назвать обе меры «секундами», их могут сложить или смешать. Сумма `page seconds` по сессии должна совпасть с `session seconds`.
- Единицы и сумма заказа часто равны нулю или `NULL`. Колонки нужны, потому что связывают выручку и поведение без join больших таблиц.

### Step dimension: место события в сессии

Раз grain — событие, можно добавить `step dimension` из [главы 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/). Она показывает позицию события: номер шага и сколько шагов осталось. Сила приёма в ролях. В схеме их три: вся сессия, подсессия покупки (кончается покупкой) и подсессия отказа (покупки нет). Примеры запросов:

- Роль покупки с шагом 1 возвращает стартовые страницы успешных покупок.
- Роль отказа с нулём оставшихся шагов возвращает последние, самые разочаровывающие страницы неудачных сессий.

Приём подходит для анализа любого последовательного процесса.

### Aggregate fact tables для clickstream

Многие вопросы заставляют суммировать миллионы строк, например визиты и выручка по месяцам и демографическим группам клиентов. Без агрегата такой запрос медленный, поэтому DBA строит агрегатную таблицу. Её строят из первой fact table: группируют по месяцу, демографической группе, странице входа и исходу сессии, считают сессии и суммируют остальные additive facts. Результат почти наверняка меньше 1% исходной таблицы, а запросы идут минимум в 100 раз быстрее. Агрегат связан со `shrunken dimensions` (уменьшенными версиями исходных): месяц — `conformed` подмножество атрибутов дня, демографическая группа — подмножество атрибутов клиента. Page и session остаются без изменений.

## Google Analytics

Авторы описывают Google Analytics (GA) как внешнее хранилище данных о том, как используют ваш сайт. Код отслеживания добавляют в `<head>` каждой страницы. Когда посетитель открывает страницу, код отправляет данные в Google, если включён JavaScript. Через GA можно собрать почти всё из этой главы, кроме персональных данных (PII): их запрещают условия сервиса. GA соединяют с AdWords, чтобы отслеживать кампании и конверсии. Как сообщают, GA используют больше половины самых популярных сайтов.

Данные доступны в онлайн-дашбордах и отчётах, поэтому из них можно построить собственную схему.

## Clickstream в bus matrix веб-ритейлера

Авторы берут веб-ритейлера компьютеров. Строки его `bus matrix` — бизнес-процессы, а не отдельные fact table. Каждая строка обычно даёт набор связанных fact table или `OLAP cube`. В матрице много отметок. Дата и время, организация и сотрудник есть почти везде. Товар и клиент занимают середину, где клиентские процессы. Сверху поставщики и детали: закупка деталей и сборка под заказ. Снизу инфраструктура и cost drivers, не связанные напрямую с поведением клиентов.

Веб-клик стоит среди клиентских процессов и делит с соседями date/time, product, customer, media, causal и service policy dimensions. Поэтому он встроен в общую систему: запросы к каждой fact table выполняют отдельно и объединяют по строкам отчёта (`drill across`). Четыре специальные веб-dimensions не мешают. Они соединяют веб-мир с обычным: по ним фильтруют и смотрят влияние на другие процессы. Пример авторов: какой опыт на сайте приводит к покупке сервисных полисов и затем к запросам на обслуживание.

Матрица помогает и в общении с бизнесом: колонка — это список приглашённых на встречу по согласованию этой dimension.

## Прибыльность по каналам, включая веб

Когда clickstream связан с продажами и коммуникациями с клиентами, команда может взяться за самую сложную область: прибыльность веба. Авторы предлагают строить её как расширение процесса продаж. На clickstream затраты пришлось бы делить по сессиям, а к сессии без товара и без продажи их трудно отнести. Плюс продаж: видна прибыльность всех каналов, а не только веба.

Grain — позиция чека в момент времени: магазин, телефон или веб-покупка. Dimensions те же, что у продаж: дата, время, клиент, канал, товар, promotion и номер чека (`degenerate dimension`). Отличие в разбивке затрат. Facts выстроены как отчёт о прибылях и убытках (P&L):

1. `units sold` и `gross revenue` (цена по прайс-листу).
2. Вычитаются скидки: manufacturer's allowance, marketing promotion и markdown. Остаётся `net revenue` — реальная цена клиента, умноженная на число единиц.
3. Вычитаются стоимость производства или закупки и хранения. Остаётся `gross profit`. Его делят на gross revenue и получают gross margin ratio.
4. Вычитаются доставка, особые условия сделки и накладные расходы. Остаётся `net profit`.

Хранить ли вычисляемые колонки, зависит от доступа. Если все читают через view, их можно считать во view. Если читают физическую таблицу, `net revenue`, `gross profit` и `net profit` хранят колонками, чтобы их не посчитали неверно.

Главная трудность — затраты. Команде DW/BI приходится искать или оценивать каждую статью и распределять до уровня строки. Качество данных разное: одни затраты есть только как годовое среднее по стране (условное значение), другие разбиты по кварталам и регионам, третьи основаны на активностях (activity-based). Затраты на сайт — инфраструктура, но без них веб-P&L не построить. Их распределяют по числу страниц на линейку товаров, по просмотренным страницам или по веб-покупкам.

Команда DW/BI не отвечает за activity-based costing во всей компании. Она берёт лучшие данные, какие есть, публикует P&L и подключает новые источники по мере их улучшения.

Когда P&L встроен в богатую dimensional модель, видно не только, что прибыльно, но и почему. Можно сравнивать каналы, сегменты клиентов, линейки товаров, акции и периоды, и комбинировать условия: например, какие акции работают в вебе, но не в других каналах.

## Итоги главы

- Clickstream — набор меняющихся источников: логи нескольких серверов, партнёры, провайдеры и поисковые запросы.
- HTTP не знает про сессии, поэтому их восстанавливают. Самый надёжный способ — persistent cookie. Но cookie указывает на компьютер, а не на человека.
- Clickstream добавляет dimensions page, event, session и referral. Page описывает тип страницы, а не каждый показ.
- Fact сессии намеренно крупнее по grain ради размера. Fact события остаётся самым детальным, и его не агрегируют.
- Две таблицы связывает session ID как degenerate dimension. `page seconds` и `session seconds` называют по-разному, а сумма первых равна второй.
- `Step dimension` в трёх ролях находит стартовые страницы покупок и последние страницы отказов. Агрегаты весят меньше 1% и ускоряют запросы минимум в 100 раз.
- Google Analytics — внешнее хранилище. Оно даёт почти все данные главы, кроме PII.
- Clickstream делит conformed dimensions с клиентскими процессами, поэтому его связывают с заказами и поддержкой. Авторы считают такую интеграцию главной задачей для любого бизнеса с заметным присутствием в вебе.
- Прибыльность веба считают как P&L на fact продаж по всем каналам. Слабое место — качество данных о затратах.

## Ключевые термины

| Термин | Значение |
|---|---|
| Clickstream | Поток событий страниц, которые записывают веб-серверы |
| Session ID | Уникальный идентификатор сессии, как номер чека |
| Persistent cookie | Cookie, который остаётся после закрытия браузера. Самый надёжный способ найти сессию |
| Page seconds, session seconds | Секунды на странице и секунды всей сессии. Названы по-разному, чтобы их не смешали |
| Step dimension | Номер шага и число шагов до конца, с ролями для сессии, покупки и отказа |
| Shrunken dimension | Conformed подмножество атрибутов исходной dimension: месяц вместо дня |
| P&L fact | Прибыль и убытки на уровне позиции чека по всем каналам |

## Что это значит на практике

- Сессии собирают в ETL один раз. Не вычисляйте их в каждом отчёте.
- Для sessionization используйте window functions: `lag`, `sum() OVER`. Порог паузы держите в одном месте.
- Время на последней странице неизвестно. Книга советует небольшое условное значение. В практике ниже мы оставляем `NULL`, чтобы пропуск было видно. Выберите одно правило.
- Договоритесь с веб-командой о кодах страниц заранее: это фундамент page dimension.
- Храните время события в UTC и в местном времени. Не вычисляйте местное время в запросах.
- В `dbt` держите две модели: `fct_page_events` (grain: событие) и `fct_sessions` (grain: сессия). Сессии строятся из событий.
- Сверяйте две таблицы: число сессий, сумма заказов и сумма `page_seconds` должны сходиться.
- Не стройте прибыльность на кликах. Расширяйте fact продаж.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки ниже идут по порядку.

![Поток практики: web log, sessionization, fact событий, fact сессии и aggregate](/assets/data-warehouse-toolkit/ch15-clickstream-flow.png)

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

Дольше всего смотрят Checkout (70 секунд), потом Product (67). У Confirmation нет замеров: это всегда последняя страница сессии.
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

-- сверка: сессий 7, суммы заказов и секунд совпадают
SELECT (SELECT count(*) FROM fact_session)              AS sessions,
       (SELECT sum(order_amount) FROM fact_session)     AS order_amount_session,
       (SELECT sum(order_amount) FROM fact_page_event)  AS order_amount_events,
       (SELECT sum(session_seconds) FROM fact_session)  AS session_seconds,
       (SELECT sum(page_seconds) FROM fact_page_event)  AS page_seconds;

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

1. Почему fact сессии построили на более крупном grain, чем самый детальный? Когда такой отход от правила оправдан?
2. Почему `page seconds` и `session seconds` называют по-разному? Как проверить, что две fact table сходятся?
3. Почему persistent cookie надёжнее других способов найти сессию? Что остаётся проблемой даже с ним?
4. Какие данные хранит step dimension и как с её помощью найти точку отказа?
5. Почему fact события не агрегируют, а агрегат строят из fact сессии? Зачем агрегату shrunken dimensions?
6. Почему прибыльность веба строят на fact продаж, а не на clickstream?

Предыдущая: [Глава 14. Здравоохранение](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/). Следующая: [Глава 16. Страхование](/book-summaries/engineering/data-warehouse-toolkit/16-insurance/).
