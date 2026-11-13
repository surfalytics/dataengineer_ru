---
title: "The Data Warehouse Toolkit, глава 6: Управление заказами"
head:
  - tag: title
    content: "Заказы по Kimball: header/line, allocation, lag | Инжиниринг Данных"
description: "Конспект главы 6 The Data Warehouse Toolkit. Заказы: header/line, allocation, role-playing dimension, accumulating snapshot, factless fact. Практика в DuckDB."
sidebar:
  order: 6
  label: "6. Управление заказами"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** заказ состоит из заголовка (`header`) и строк (`line`). Fact table строят на grain строки: описания заголовка идут в dimensions, а суммы заголовка раскладываются по строкам. Путь заказа до счёта описывает `accumulating snapshot` со сроками между вехами (lags).

## О чём глава

[Глава 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/) разобрала закупки и типы `SCD`. Глава 6 идёт дальше по цепочке создания стоимости (value chain): к заказу, отгрузке и счёту. Эти процессы дают объём продаж и выручку, поэтому команды часто начинают хранилище с них. Глава учит моделировать заказ с заголовком и строками.

- Role-playing, degenerate и junk dimensions.
- Dimensions продукта, клиента и сделки.
- Ловушки header/line и allocation.
- Валюты и единицы измерения.
- Счета, P&L, audit dimension.
- Accumulating snapshot.

![Star schema строки заказа: две роли даты, junk dimension и degenerate dimension](/assets/data-warehouse-toolkit/ch06-order-star.png)

В центре fact table на grain строки заказа. Два ключа даты ведут в одну `dim_date`. Поля `order_number` и `order_line_number` — degenerate dimensions, `order_profile_key` — junk dimension.

## Order management и bus matrix

Order management — это цепочка процессов: quote (предложение), заказ, отгрузка, счёт, получение платежей и возврат. Каждый процесс — строка `bus matrix`, таблицы «процессы × dimensions» (см. [главу 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)). Строки повторяют цепочку создания стоимости. Глава подробно разбирает заказ и счёт.

| Процессы | Dimensions |
|---|---|
| Quote, заказ | Date, Customer, Product, Sales Rep, Deal |
| Отгрузка, счёт, возврат | Те же и ещё Warehouse, Shipper |
| Платежи | Date, Customer, Sales Rep |

## Order transactions: заказы

Естественный grain — одна строка на строку заказа (line item). Dimensions: дата заказа, запрошенная дата отгрузки, продукт, клиент, sales rep и deal. Факты: количество и суммы gross, discount и net. Суммы здесь extended: цена за единицу, умноженная на количество.

### Fact normalization: почему не дробить факты

Некоторые дизайнеры хотят один общий факт `amount` и dimension «тип измерения» (gross, discount и так далее). Авторы советуют так не делать. Строк станет во столько раз больше, сколько типов фактов: 10 млн строк с 4 фактами превратятся в 40 млн строк с одним фактом. К тому же SQL плохо считает отношение значений из разных строк, например скидку в процентах от gross. Приём оправдан, когда фактов очень много, заполнена малая часть строки и вычислений между фактами нет, например в тестах качества на производстве. Ещё один случай — в [главе 14](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/).

### Role-playing dimensions: одна таблица в нескольких ролях

В заказе несколько дат, и каждая — foreign key в fact table. Но два ключа нельзя присоединить к одной таблице дат: SQL решит, что обе даты должны совпасть. Поэтому делают одну физическую `dim_date` и по одному view (или alias) на каждую роль. Так работает `role-playing dimension`: одна dimension несколько раз в одной fact table. Колонки в view называют по-разному (`order_month`, `req_ship_month`), иначе в отчёте их не отличить. Alias в BI-инструменте не советуют, если есть несколько BI-инструментов и прямой SQL. Одну таблицу на все комбинации дат делать нельзя: она раздует дневную таблицу (около 365 строк в год) и перестанет быть conformed.

### Роли и bus matrix

Роли даты записывают в одну ячейку bus matrix: Order Date, Requested Ship Date, Invoice Date и так далее. Если ролей мало и они повторяются, можно сделать подколонки внутри conformed dimension.

### Product dimension

Product dimension описывает весь ассортимент, а он бывает огромным: у производителя кормов больше 25 000 вариантов, у производителей окон — миллионы конфигураций. В ней много описательных колонок (у производителей 100 и больше) и иерархии фиксированной глубины в одной плоской таблице. Snowflake авторы не советуют: выигрыш в месте мал, а просмотр сложнее и медленнее. ETL строит её из справочника товаров так: заменяет код на `surrogate key`, добавляет читаемые описания вместо кодов, проверяет значения (из-за опечатки SQL выдаст лишнюю строку) и описывает атрибуты в metadata.

### Customer dimension

В customer dimension одна строка — одно место доставки (ship-to). В ней живут независимые иерархии: географическая (город, штат, ZIP) и организационная (ship-to, bill-to — кому выставляют счёт, материнская компания). Географию авторы советуют встраивать в сами dimensions, а не делать общую dimension «все точки на карте» (см. [главу 11](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/)). Иерархии переменной глубины разобраны в [главе 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/). Если один ship-to редко связан с двумя bill-to, grain dimension — пара ship-to и bill-to. Если связь many-to-many обычна, это отдельные dimensions, связанные через fact table.

### Одна dimension или несколько

Вопрос: добавить атрибуты sales organization в customer dimension или сделать отдельную? Если rep жёстко связан с клиентом и связь не меняется, их объединяют: связь видна без fact table. Разделяйте, если:

- связь many-to-many и это норма;
- связь меняется во времени;
- customer dimension огромна (миллионы строк);
- rep и клиент независимо входят в другие fact tables;
- бизнес думает о них как о разных сущностях.

Если в схеме уже 25 dimensions, подумайте об объединении. Таблица из двух ключей «клиент и rep» не нужна: связи между dimensions хранит fact table. Текущего rep хранят как type 1 или type 5 ([глава 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)).

### Factless fact table: закрепление rep за клиентами

Пользователи хотят видеть закрепление rep за клиентами во времени, даже без заказов. Для этого строят `factless fact table`: fact table без числовых фактов, где строка значит «связь или событие было». В ней два ключа даты (начало и конец закрепления), ключи rep и клиента и счётчик 1. У текущего закрепления дата конца ссылается на строку «будущая, неопределённая дата». Чтобы найти закрепления без заказов, сравнивают с fact table заказов: вычитают множества (`EXCEPT`) или пишут correlated subquery. В практике ниже та же идея на примере товаров по сделке.

### Deal dimension

Deal dimension похожа на promotion dimension из [главы 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/). Она описывает условия сделки: terms, allowances и incentives, иногда её называют contract. Если условия связаны между собой, их упаковывают в одну dimension. Если нет и получилось бы декартово произведение, dimension лучше разделить. В очень большой fact table (сотни миллионов строк) хочется меньше ключей, поэтому одна dimension выгоднее, если с этим согласен бизнес. Dimension до 100 000 строк приемлема.

### Degenerate dimension: номер заказа

Номер заказа лежит в каждой строке fact table. В отличие от операционной базы, он не ссылается на таблицу заголовка: описания заголовка разобраны по dimensions. Номер нужен, чтобы собрать строки в заказ, связать хранилище с источником и войти в primary key вместе с номером строки. Авторы предупреждают: degenerate dimensions только для идентификаторов транзакций, а не для непонятных кодов. Если у заказа есть данные, которым некуда лечь, номер становится обычной dimension. Но весь заголовок в неё переносить нельзя.

### Junk dimension: флаги и индикаторы

В источниках много флагов с малым числом значений: тип платежа, тип заказа, признак комиссии. Авторы называют неудачные варианты: выбросить флаги, оставить шифры в fact, сделать dimension на каждый флаг (терпимо, пока ключей не больше 20 или около того) или положить флаги в order header dimension. Книга советует упаковать их в `junk dimension`. В fact table остаётся один маленький ключ. Решает число комбинаций. Десять флагов по два значения дают не больше 1 024 строк. Пять флагов по три значения — 243 строки, и одна dimension подходит. Пять флагов по 100 значений — 100 млн комбинаций, нужны отдельные dimensions. Если комбинаций много, а встречаются не все, ETL добавляет строку при первой встрече. В header dimension фильтр «входящий заказ» превратился бы в огромный список номеров заказов.

### Header/line: первая ловушка — заголовок как dimension

Авторы описывают две ошибки в header/line. Обе точно отражают связи, поэтому их трудно заметить. Первая — копия операционного заголовка в виде dimension. Такая dimension огромна: при пяти строках на заказ она составляет 20% от fact table, а размеры должны различаться на порядки. Она растёт почти так же быстро, как fact. Любой анализ по клиенту или сделке идёт через эту большую таблицу.

### Несколько валют

Пример книги: заказы принимают больше чем в 15 валютах. Колонки на каждую валюту не нужны. Каждый факт заменяют парой: сумма в местной валюте и в корпоративной. Курс зависит от правил бизнеса: на момент заказа, на конец дня или другой. Корпоративные суммы полностью additive, местные additive только внутри одной валюты. Нужна и currency dimension: место сделки не определяет валюту. Можно хранить суммы в одной валюте и курс в строке, а пересчёт отдать view. Если менеджер любой страны хочет видеть объём в любой валюте, добавляют `currency conversion fact table`: дата, исходная и целевая валюты, курс в обе стороны. Все пары не нужны: валют около 100, а 10 000 строк в день ни к чему.

### Факты разного grain и allocation

Факты заголовка, например доставка на весь заказ, имеют другой grain. Первая реакция: опустить их на строку. Это `allocation`. Тогда факты заказа можно резать по всем dimensions, включая продукт. Согласовать правила — вопрос политики, лучше, если этим занимаются финансы, а не команда DW/BI. Если отделы спорят (финансы — по gross, логистика — по весу), в строке два столбца с разными именами. Если разложить не удалось, суммы заголовка идут в отдельную fact table на grain заказа, но продукта в ней нет. Не смешивайте grain в одной fact table, предупреждают авторы. Три плохих обхода:

- повторить сумму на каждой строке: сумма завысится;
- положить её на первую или последнюю строку: при фильтре по продукту она пропадёт;
- завести специальный product key для заголовка: нужен «шифровальный ключ».

> **Пояснение:** сумма по строкам должна равняться сумме заголовка. Остаток от округления отдайте одной строке, как в практике ниже.

### Header/line: вторая ловушка — заголовок как fact table

Вторая ошибка: заголовок хранят как отдельную fact table, а строки ссылаются на него по номеру заказа. Строки не наследуют dimensions заголовка. Чтобы разрезать строки по атрибуту заголовка, нужно присоединить большую header fact к ещё большей line fact. Книга советует иначе: строка сама несёт ключи всех dimensions заголовка.

## Invoice transactions: счета

У производителя счёт создают при отгрузке. В этот момент известны цены, скидки и затраты, поэтому в счетах видны клиенты, товары, выручка и прибыль. Авторы считают счета лучшим местом начать проект DW/BI: это «самые мощные данные». Grain — строка счёта. Dimension даты играет три роли: invoice, requested ship и actual ship. Customer, product и deal те же, что в заказах, и они conformed. Поэтому работает `drill across`: запрос по нескольким fact tables через общие атрибуты. Новые dimensions: warehouse, shipper и service level. Номер заказа — второй degenerate dimension.

### Service level: факты, dimensions или оба варианта

Роли даты уже дают фильтры и тренды по срокам. Если нужно больше, добавляют числа: счётчик on-time (0 или 1) и lag в днях между запрошенной и фактической датой, плюс или минус. Для качественной оценки добавляют dimension (или колонки в junk dimension) со значениями вроде «на 1 день раньше» и «на 2 дня позже» и с группами «раньше», «позже». Если сервис под пристальным контролем, берут оба подхода: число и текст дают разные взгляды.

### Profit and loss facts

Если есть activity-based costing или сильная ERP, строка счёта может нести выручку и затраты в порядке P&L: сверху стоимость без скидок, снизу остаток после скидок и затрат. Нижнюю строку называют `contribution`, а не прибылью: общие и административные расходы в неё не входят.

- Gross: list price, умноженный на количество.
- Allowance (off-invoice) и discount (за объём или условия оплаты) вычитаются из gross.
- Net: gross минус allowances и discounts, до налога.
- Затраты: fixed и variable manufacturing, storage, distribution. Клиент их не видит.
- Contribution: net минус все затраты.

Все суммы extended, поэтому они additive. Среднюю цену считают так: сумму extended делят на сумму количеств. Allowances и discounts уровня счёта нужно разложить по строкам, иначе contribution нельзя разрезать по продукту.

### Предупреждение о прибыльности

Затраты — слабое место. Даже в сильной ERP их часто нельзя получить на уровне строки, а каждый вид затрат может требовать отдельного extract: десять затрат — десять программ ETL. Если затраты — средние от средних, детальный P&L может потерять смысл. Книга советует сначала оценить, что есть в источниках, и не брать на команду согласование activity-based costing. Лучше сначала отдать выручку и затраты по отдельности, а прибыльность собрать позже.

### Audit dimension

При построении строк ETL создаёт metadata: индикаторы качества, версии обработки. Она интересна и бизнесу: можно ли верить числам, были ли аномалии, какая версия логики затрат и пересчёта валют использована. Чтобы ответить, в fact table добавляют ключ `audit dimension`. Авторы советуют начать с малого: quality indicator, out of bounds indicator, amount adjusted flag, cost allocation version и foreign currency version. Первые три берут из error event table ([глава 19](/book-summaries/engineering/data-warehouse-toolkit/19-etl-subsystems/)), версии — из таблицы статуса ETL. Dimension обычная, поэтому индикатор можно добавить в стандартный отчёт и отделить аномальные значения.

## Accumulating snapshot: конвейер выполнения заказа

Выполнение заказа — конвейер, особенно при производстве под заказ: заказ, backlog, запуск в производство, готовая продукция, отгрузка, счёт. Каждый этап можно вести в своей transaction fact table. Но иногда нужен весь путь и скорость продукта по конвейеру. Для этого есть `accumulating snapshot`: он показывает текущее состояние каждого заказа и находит узкие места. Transaction tables говорят, сколько продукта прошло, а `periodic snapshot` — сколько его лежит в конвейере. Считать среднее число дней между вехами по одним transactions «безумно трудно», пишут авторы.

![Вехи заказа: заказ, отгрузка, доставка, счёт и lags между ними](/assets/data-warehouse-toolkit/ch06-order-pipeline.png)

> **Пояснение:** рисунок и практика упрощены до четырёх вех. В схеме книги девять ролей даты, включая backlog, release to manufacturing, scheduled ship и arrival.

Grain — строка заказа, как в transactions, но строку обновляют при каждой вехе. Каждая веха — роль date dimension. В ней нужна строка Unknown или To Be Determined: при первой загрузке многих дат ещё нет. Колонок много: даты, количества на каждом этапе и lags. Несколько дат ещё не делают таблицу accumulating snapshot: главное — возврат к строкам при новых событиях.

Подход полезен, когда продукт идентифицирован (VIN, серийный номер, номер партии): тогда видны throughput и yield. Он подходит коротким процессам с чётким началом и концом. Долгие процессы, например банковский счёт, лучше описывает periodic snapshot.

> **Пояснение:** в практике ниже веха, которой ещё нет, ссылается на строку «не наступило» (ключ 0), а lag остаётся `NULL`.

### Accumulating snapshot и type 2

Accumulating snapshot показывает последнее состояние. Если в dimensions есть атрибуты type 2, для активных строк ключи обновляют до самой свежей surrogate key. Завершённую строку обычно больше не трогают.

### Lag calculations

Разница между двумя датами — число, которое удобно усреднять по любым dimensions. Это мера эффективности. Lags можно считать во view, например «заказ → отгрузка». Либо их считает ETL: он учтёт рабочие дни без выходных и праздников, а для коротких процессов посчитает часы или минуты.

### Несколько единиц измерения

Отделы хотят видеть одни количества в разных единицах: производство — в паллетах, продажи — в розничных ящиках или банках. Коэффициенты в product dimension не годятся: пользователь путается, умножать или делить, а коэффициенты меняются во времени. Книга советует хранить их в fact table. Пример: 10 количеств и 5 единиц дали бы 50 колонок, а достаточно 10 количеств в базовой единице и 4 коэффициентов, всего 14. Пересчитанные значения отдаёт view с уникальными именами. Плюс: product dimension не получает новые строки из-за мелких изменений коэффициентов.

### За пределами rearview mirror

Почти вся глава — взгляд назад, на метрики прошлого. Организации хотят добавить опережающие показатели, например активность prospecting и quoting, которая помогает прогнозировать заказы. Их добавляют как ещё строки bus matrix с теми же dimensions.

## Итоги главы

- Order management — цепочка процессов, и каждый из них — строка bus matrix с общими dimensions.
- Fact table заказа строят на grain строки. Данные заголовка идут в dimensions, а не в header dimension или fact table.
- Одна физическая date dimension играет несколько ролей через отдельные view.
- Факты разного grain опускают на строку через allocation. Правило согласует бизнес.
- Junk dimension собирает флаги. Число комбинаций решает, нужна одна таблица или несколько.
- Валюты решает пара фактов и currency dimension, единицы измерения — коэффициенты в fact table и view.
- Строка счёта несёт P&L до contribution. Но затраты часто недоступны на уровне строки, поэтому прибыльность лучше делать вторым шагом.
- Audit dimension делает metadata ETL обычной dimension для отчётов.
- Accumulating snapshot хранит одну строку на строку заказа, обновляет её по вехам и считает lags.

## Ключевые термины

| Термин | Значение |
|---|---|
| Allocation | Распределение суммы заголовка по строкам |
| Role-playing dimension | Одна dimension несколько раз в одной fact table |
| Degenerate dimension | Номер документа в fact table, без своей таблицы |
| Junk dimension | Флаги с малым числом значений в одной таблице |
| Factless fact table | Fact table без числовых фактов |
| Contribution | Net минус затраты, без общих расходов |
| Accumulating snapshot | Одна строка на процесс, обновляется по вехам |
| Lag | Время между двумя вехами |

## Что это значит на практике

- Выбирайте grain строки заказа, а не заголовка.
- Номер заказа держите как degenerate dimension: по нему собирают заказ из строк.
- Сумму allocation проверяйте тестом `dbt`: сумма по строкам равна сумме в заголовке.
- Для каждой роли даты делайте view: `dim_order_date`, `dim_ship_date`.
- Перед junk dimension умножьте числа значений флагов. Малое число комбинаций идёт в одну таблицу.
- Храните суммы в двух валютах и ключ валюты. Местные суммы разных валют не складывайте.
- Добавьте `audit_key` в fact table, чтобы отделять аномальные строки в отчётах.
- В `dbt` accumulating snapshot — это `incremental` с `merge` по `order_number` и `order_line_number`.
- Чтобы найти «чего не было», держите coverage table и делайте `anti join`.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку в одной сессии.

### Шаг 1. Создаём dimensions и staging заказов

Модель упрощена: без sales rep, deal и order profile. Техники от этого не меняются.

```sql
CREATE MACRO key_to_date(k) AS strptime(k::VARCHAR, '%Y%m%d')::DATE;

-- ключ 0 = «ещё не наступило»
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d::DATE AS full_date, dayname(d) AS day_name
FROM generate_series(DATE '2024-03-01', DATE '2024-03-31', INTERVAL 1 DAY) t(d)
UNION ALL
SELECT 0, NULL, 'Не наступило';

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES (1, 'Альфа'), (2, 'Бета'), (3, 'Гамма')) t(customer_key, customer_name);

CREATE TABLE dim_product AS
SELECT * FROM (VALUES (1, 'Товар A'), (2, 'Товар B'), (3, 'Товар C')) t(product_key, product_name);

-- заголовки заказов: freight относится ко всему заказу
CREATE TABLE stg_order_header AS
SELECT * FROM (VALUES
    ('O1', DATE '2024-03-01', DATE '2024-03-04', 1, 10.00),
    ('O2', DATE '2024-03-05', DATE '2024-03-08', 2, 12.00),
    ('O3', DATE '2024-03-10', DATE '2024-03-12', 1,  5.00),
    ('O4', DATE '2024-03-20', DATE '2024-03-25', 3,  8.00)
) t(order_number, order_date, requested_ship_date, customer_key, freight_amount);

-- строки заказов
CREATE TABLE stg_order_line AS
SELECT * FROM (VALUES
    ('O1', 1, 1, 2, 50.0),
    ('O1', 2, 2, 1, 100.0),
    ('O1', 3, 3, 4, 25.0),
    ('O2', 1, 1, 5, 50.0),
    ('O2', 2, 2, 1, 100.0),
    ('O3', 1, 3, 10, 25.0),
    ('O4', 1, 2, 2, 100.0),
    ('O4', 2, 1, 1, 50.0)
) t(order_number, order_line_number, product_key, order_quantity, unit_price);

-- события конвейера, пришедшие из склада и биллинга
CREATE TABLE stg_order_event AS
SELECT * FROM (VALUES
    ('O1', 1, 'shipped',   DATE '2024-03-03'),
    ('O1', 1, 'delivered', DATE '2024-03-05'),
    ('O1', 1, 'invoiced',  DATE '2024-03-03'),
    ('O1', 2, 'shipped',   DATE '2024-03-04'),
    ('O1', 2, 'delivered', DATE '2024-03-06'),
    ('O1', 2, 'invoiced',  DATE '2024-03-04'),
    ('O1', 3, 'shipped',   DATE '2024-03-04'),
    ('O1', 3, 'delivered', DATE '2024-03-07'),
    ('O1', 3, 'invoiced',  DATE '2024-03-04'),
    ('O2', 1, 'shipped',   DATE '2024-03-09'),
    ('O2', 1, 'delivered', DATE '2024-03-11'),
    ('O2', 1, 'invoiced',  DATE '2024-03-09'),
    ('O2', 2, 'shipped',   DATE '2024-03-08'),
    ('O2', 2, 'delivered', DATE '2024-03-10'),
    ('O2', 2, 'invoiced',  DATE '2024-03-08'),
    ('O3', 1, 'shipped',   DATE '2024-03-12')
) t(order_number, order_line_number, event_type, event_date);
```

### Задания

**1.** Header/line и allocation. Постройте `fact_order_line` на grain строки. Разложите `freight_amount` по строкам пропорционально gross amount. Сумма по заказу должна совпасть с заголовком. Сначала покажите ошибку: что будет, если просто присоединить freight к каждой строке.

<details>
<summary>Решение</summary>

```sql
-- ошибка: freight повторяется на каждой строке
SELECT sum(h.freight_amount) AS wrong_freight,
       (SELECT sum(freight_amount) FROM stg_order_header) AS right_freight
FROM stg_order_line l
JOIN stg_order_header h USING (order_number);

-- правильно: allocation пропорционально gross, остаток от округления в первую строку
CREATE TABLE fact_order_line AS
WITH lines AS (
    SELECT l.order_number, l.order_line_number, l.product_key, l.order_quantity,
           l.order_quantity * l.unit_price AS gross_amount,
           h.customer_key, h.freight_amount,
           strftime(h.order_date, '%Y%m%d')::INT AS order_date_key,
           strftime(h.requested_ship_date, '%Y%m%d')::INT AS requested_ship_date_key,
           round(h.freight_amount * (l.order_quantity * l.unit_price)
                 / sum(l.order_quantity * l.unit_price) OVER (PARTITION BY l.order_number), 2) AS alloc_raw
    FROM stg_order_line l
    JOIN stg_order_header h USING (order_number)
)
SELECT order_number, order_line_number, order_date_key, requested_ship_date_key,
       customer_key, product_key, order_quantity, gross_amount,
       (alloc_raw + CASE WHEN order_line_number = 1
            THEN freight_amount - sum(alloc_raw) OVER (PARTITION BY order_number)
            ELSE 0 END)::DECIMAL(10,2) AS allocated_freight
FROM lines;

-- проверка: разница равна 0 для каждого заказа
SELECT f.order_number, sum(f.allocated_freight) AS allocated, max(h.freight_amount) AS header_freight,
       sum(f.allocated_freight) - max(h.freight_amount) AS diff
FROM fact_order_line f
JOIN stg_order_header h USING (order_number)
GROUP BY f.order_number
ORDER BY f.order_number;
```

У заказа O1 три строки по 100. Без правки получится 3.33 × 3 = 9.99. Остаток 0.01 уходит в первую строку.
</details>

**2.** Accumulating snapshot. Создайте таблицу `fact_order_fulfillment` на grain строки заказа. Вставьте строки со всеми вехами = 0. Потом обновите вехи из `stg_order_event` и посчитайте lags.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_order_fulfillment AS
SELECT order_number, order_line_number, customer_key, product_key,
       order_date_key, requested_ship_date_key,
       0 AS ship_date_key, 0 AS delivery_date_key, 0 AS invoice_date_key,
       NULL::INT AS order_to_ship_days,
       NULL::INT AS ship_to_delivery_days
FROM fact_order_line;

UPDATE fact_order_fulfillment f
SET ship_date_key     = coalesce(e.ship_key,     f.ship_date_key),
    delivery_date_key = coalesce(e.delivery_key, f.delivery_date_key),
    invoice_date_key  = coalesce(e.invoice_key,  f.invoice_date_key)
FROM (
    SELECT order_number, order_line_number,
           max(CASE WHEN event_type = 'shipped'   THEN strftime(event_date, '%Y%m%d')::INT END) AS ship_key,
           max(CASE WHEN event_type = 'delivered' THEN strftime(event_date, '%Y%m%d')::INT END) AS delivery_key,
           max(CASE WHEN event_type = 'invoiced'  THEN strftime(event_date, '%Y%m%d')::INT END) AS invoice_key
    FROM stg_order_event
    GROUP BY order_number, order_line_number
) e
WHERE f.order_number = e.order_number AND f.order_line_number = e.order_line_number;

UPDATE fact_order_fulfillment
SET order_to_ship_days = CASE WHEN ship_date_key <> 0
        THEN date_diff('day', key_to_date(order_date_key), key_to_date(ship_date_key)) END,
    ship_to_delivery_days = CASE WHEN delivery_date_key <> 0
        THEN date_diff('day', key_to_date(ship_date_key), key_to_date(delivery_date_key)) END;

SELECT order_number, order_line_number, ship_date_key, delivery_date_key,
       order_to_ship_days, ship_to_delivery_days
FROM fact_order_fulfillment
ORDER BY order_number, order_line_number;
```
</details>

**3.** Анализ lags. Покажите средний срок «заказ → отгрузка» и «отгрузка → доставка» по клиентам. Затем найдите строки, которые ещё не отгружены, и их возраст в днях на 31 марта.

<details>
<summary>Решение</summary>

```sql
SELECT c.customer_name,
       round(avg(f.order_to_ship_days), 2)    AS avg_order_to_ship,
       round(avg(f.ship_to_delivery_days), 2) AS avg_ship_to_delivery
FROM fact_order_fulfillment f
JOIN dim_customer c USING (customer_key)
GROUP BY c.customer_name
ORDER BY c.customer_name;

-- открытые строки: ещё не отгружены
SELECT order_number, order_line_number,
       date_diff('day', key_to_date(order_date_key), DATE '2024-03-31') AS age_days
FROM fact_order_fulfillment
WHERE ship_date_key = 0
ORDER BY age_days DESC;
```

Строки без доставки дают `NULL` в lag. `avg` их пропускает, поэтому средние не портятся.
</details>

**4.** Role-playing dimension. Сделайте два view над `dim_date`: для запрошенной даты отгрузки и для фактической даты отгрузки. Найдите строки, отгруженные позже запрошенной даты. Покажите, во сколько дней просрочка.

<details>
<summary>Решение</summary>

```sql
CREATE VIEW dim_requested_date AS
SELECT date_key AS requested_ship_date_key, full_date AS requested_ship_date FROM dim_date;

CREATE VIEW dim_ship_date AS
SELECT date_key AS ship_date_key, full_date AS ship_date, day_name AS ship_day FROM dim_date;

SELECT f.order_number, f.order_line_number,
       r.requested_ship_date, s.ship_date,
       s.ship_date - r.requested_ship_date AS days_late
FROM fact_order_fulfillment f
JOIN dim_requested_date r USING (requested_ship_date_key)
JOIN dim_ship_date s USING (ship_date_key)
WHERE s.ship_date > r.requested_ship_date
ORDER BY days_late DESC;
```

Одна `dim_date` играет три роли: заказ, запрошенная и фактическая отгрузка. В fact каждая роль — свой foreign key.
</details>

**5.** Factless coverage. Создайте таблицу `fact_deal_coverage`: какие товары доступны каждому клиенту по сделке. Найдите товары по сделке, которые клиент ни разу не заказал.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_deal_coverage AS
SELECT * FROM (VALUES
    (1, 1), (1, 2),
    (2, 1), (2, 3),
    (3, 2), (3, 3)
) t(customer_key, product_key);

-- coverage минус то, что произошло
SELECT c.customer_name, p.product_name
FROM fact_deal_coverage cov
LEFT JOIN (SELECT DISTINCT customer_key, product_key FROM fact_order_line) act
       USING (customer_key, product_key)
JOIN dim_customer c USING (customer_key)
JOIN dim_product p USING (product_key)
WHERE act.customer_key IS NULL
ORDER BY c.customer_name, p.product_name;
```

Результат: Бета не заказывала Товар C, Гамма не заказывала Товар C. В `fact_order_line` этих строк нет, поэтому одним запросом по ней ответа не получить. Нужна coverage table.
</details>

## Вопросы для самопроверки

1. Почему сумму заголовка нельзя просто повторить в каждой строке? Какие ещё обходы авторы считают плохими?
2. Как выбрать правило allocation и как проверить, что сумма сошлась?
3. Чем accumulating snapshot отличается от transaction fact table? Когда он подходит, а когда лучше periodic snapshot?
4. Почему авторы не советуют делать `dim_order_header` и что делают вместо этого?
5. Когда флаги заказа лучше собрать в одну junk dimension, а когда сделать несколько dimensions?
6. Как найти события, которых не было, если в fact table есть только события, которые были?

Предыдущая: [Глава 5. Закупки и SCD](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/). Следующая: [Глава 7. Бухгалтерия](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/).
