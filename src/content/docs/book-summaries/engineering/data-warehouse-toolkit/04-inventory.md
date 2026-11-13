---
title: "The Data Warehouse Toolkit, глава 4: Склад и запасы"
head:
  - tag: title
    content: "Snapshot fact table и bus matrix: склад по Kimball | Инжиниринг Данных"
description: "Конспект главы 4 The Data Warehouse Toolkit. Модели склада: periodic и accumulating snapshot, transactions, bus matrix, conformed dimensions. Практика в DuckDB."
sidebar:
  order: 4
  label: "4. Склад и запасы"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** у запасов есть три модели данных: `periodic snapshot`, `transaction` и `accumulating snapshot`. Они дополняют друг друга, потому что отвечают на разные вопросы. Вторая тема главы — `bus architecture`: хранилище строят по бизнес-процессам, а процессы сходятся через общие `conformed dimensions`.

## О чём глава

В [главе 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/) мы смоделировали продажи в магазине. Теперь книга берёт запасы и спрашивает: как их смоделировать и как связать модели разных процессов в одно хранилище.

- Цепочка создания стоимости (`value chain`).
- Три модели запасов и три типа fact tables.
- `Semi-additive` факты: почему остаток нельзя суммировать по датам.
- `Bus matrix` и `conformed dimensions`.
- `Conformed facts`, data governance и agile.

![Две fact tables склада: ежедневный snapshot остатков и transactions движения](/assets/data-warehouse-toolkit/ch04-inventory-snapshot.png)

Слева snapshot остатков: строка на товар, склад и день. Справа transactions: строка на каждое движение. Таблицы делят dimensions даты, товара и склада.

> **Пояснение:** книга строит snapshot для магазинов, а transactions и accumulating snapshot — для склада. На схеме и в практике везде склад.

## Цепочка создания стоимости (value chain)

У компании есть цепочка ключевых бизнес-процессов. Ритейлер заказывает товар у производителя, принимает его на склад, хранит, везёт в магазин, хранит на полке и продаёт.

У каждого шага свои метрики, интервал времени, `grain` и dimensions. Поэтому каждый процесс даёт одну или несколько fact tables. Цель DW/BI — следить за результатами процессов.

## Три модели запасов

Книга показывает три дополняющие модели. Каждая рассказывает свою историю. Для одних задач хватает одной модели, для других нужны две или все три.

Это `periodic snapshot` (остаток по периодам), `transaction` (каждое движение) и `accumulating snapshot` (путь партии по этапам).

## Periodic snapshot: остаток по дням

`Periodic snapshot` — fact table, в которую через равные интервалы записывают срез состояния. Книга берёт задачу ритейлера: анализировать ежедневный остаток по товарам и магазинам. Проектирование идёт по четырём шагам:

- Процесс: регулярные срезы запасов.
- `Grain`: один товар в одном магазине за один день.
- Dimensions следуют из grain: дата, товар, магазин.
- Fact: один, `quantity on hand`.

У periodic snapshot grain часто нельзя описать через транзакцию, поэтому его задают списком dimensions. Dimension акций не нужна: акции связаны с движением товара, а не с остатком. Атрибут вроде минимального объёма заказа попадает в dimension товара, только если он постоянный для товара.

Продажи дают разреженную fact table, а остатки — плотную: строка есть на каждый товар в каждом магазине каждый день, даже при нуле. В примере книги 60 000 товаров в 100 магазинах дают около 6 млн строк за ночь, но при ширине 14 байт это только 84 МБ. Если данных слишком много, старые срезы делают реже: 60 дней по дням, дальше по неделям. За 3 года вместо 1 095 срезов будет 208, в двух разных fact tables.

### Semi-additive facts: остаток нельзя суммировать по датам

`Semi-additive fact` суммируют по одним dimensions, но не по другим. Остаток можно складывать по товарам и магазинам. По датам нельзя: это уровень на один момент. Так же ведут себя финансовые остатки.

Пример книги: на счёте 50 $ в понедельник и вторник, 100 $ со среды до пятницы. Сумма пяти дневных остатков равна 400 $, но в пятницу на счёте 100 $. По датам остатки усредняют: 80 $. Книга относит сюда любые показатели статического уровня, например температуру в комнате.

В SQL есть ловушка. Функция `AVG` усредняет по всем строкам запроса, а не по датам. Для 3 товаров, 4 магазинов и 7 дат она разделит сумму на 84, а нужно на 7.

> **Пояснение:** сначала суммируйте остаток по товарам и магазинам внутри каждой даты, потом берите `avg` по датам. Так сделано в практике ниже.

### Расширенные факты запасов

Одного остатка мало. Чтобы измерить скорость запасов, добавляют `quantity sold` (для склада — отгружено). Тогда считают оборачиваемость (`turns`) и запас в днях (`days' supply`):

- Turns за день: продано делить на остаток. За период: всего продано делить на средний дневной остаток.
- Days' supply за период: остаток на последний день делить на среднее проданное за день.

Ещё нужна стоимость запасов: по себестоимости и по последней цене продажи. Остаток `semi-additive`, остальные факты книга называет `additive`.

> **Пояснение:** стоимость остатка — тоже уровень на дату, по датам её не суммируют. Поэтому на схеме `inventory_value` помечен как `semi-additive`. Turns и days' supply — отношения: считайте их в запросе из компонентов.

## Inventory transactions: каждое движение

Второй способ — записывать каждое событие, которое меняет остаток: приёмку, проверку, размещение в ячейку, отбор, отгрузку, возврат, списание. В строке есть дата, товар, склад, поставщик, тип транзакции и обычно одно число: на сколько изменился остаток.

Такая таблица отвечает на вопросы о частоте и времени движений, на которые snapshot не отвечает. Но остаток по ней восстанавливать громоздко: надо идти вперёд от известной точки. Для широких вопросов это непрактично, поэтому книга советует держать рядом snapshot.

Если у типов движений разные dimensions, например перевозчик у приёмки, а клиент у отгрузки, делают несколько связанных fact tables. Общее правило: разный естественный grain или набор dimensions значит разные процессы и разные fact tables.

## Accumulating snapshot: путь партии

`Accumulating snapshot` нужен для процесса с началом, концом и вехами между ними. Строку добавляют, когда партия принята, и обновляют, пока партия не уйдёт со склада. Это возможно, только если различать поставки или вести учёт по серийному номеру или номеру партии (`lot`).

В строке есть несколько date keys (приёмка, проверка, размещение, первая и последняя отгрузка), количества на этапах и lags. Пример книги: партия 101 принята 1 января.

| Момент | Received | Inspected | Bin | Lag проверки | Lag размещения |
|---|---|---|---|---|---|
| Принята | 20130101 | 0 | 0 | пусто | пусто |
| Проверена 3 января | 20130101 | 20130103 | 0 | 2 | пусто |
| Размещена 4 января | 20130101 | 20130103 | 20130104 | 2 | 3 |

![Вехи accumulating snapshot партии: приёмка, проверка, склад, первая продажа](/assets/data-warehouse-toolkit/ch04-inventory-pipeline.png)

Схема показывает путь партии сверху вниз. Одна строка обновляется на каждой вехе.

> **Пояснение:** в книге lags считают в основном от приёмки, а последние вехи — отгрузки. На схеме и в практике последняя веха — первая продажа, а lag — дни между соседними вехами.

## Три типа fact tables

Книга называет всего три основных типа fact tables и считает, что так в любой отрасли. Все три полезны. Часто нужны две дополняющие таблицы, но работать с ними приходится по-разному.

| Свойство | Transaction | Periodic snapshot | Accumulating snapshot |
|---|---|---|---|
| Строка | Событие | Период | Проход через процесс |
| Даты | Дата события | Дата среза | Несколько дат вех |
| Обновления | Нет | Нет | При каждом шаге |

### Transaction fact tables

Строка описывает событие в одну точку времени и есть, только если событие было. Транзакцию после записи обычно не трогают. Это самые естественные данные для dimensional model. Но часть вопросов по ним решать непрактично: нельзя выжить на одних транзакциях.

### Periodic snapshot fact tables

Periodic snapshots дают регулярный ряд для трендов: конец дня, недели, месяца. Если транзакции — кусочки выручки, дневной snapshot получают суммой, и его строят ради скорости. В запасах так не выходит: логика влияния разных типов транзакций на остаток сложная. Лучше брать остаток из операционной системы. Иначе эту логику реализует `ETL` (загрузка данных в хранилище).

### Accumulating snapshot fact tables

Accumulating snapshot описывает процесс с началом, концом и стандартными шагами и подходит для анализа workflow. Для каждой вехи есть date key, иногда ещё дата последнего обновления. Каждая дата — отдельная роль одной dimension даты (`role-playing dimension`, [глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). Неизвестные даты получают default surrogate key.

### Lags и счётчики вех

Такая таблица показывает время процесса, поэтому хранит длительности между вехами. По transactions это трудно: надо сопоставлять строки. Lag бывает простой разницей дат или учитывает рабочие дни и праздники. Ещё бывают счётчики вех (0 или 1) и ключ dimension статуса.

### Обновления и OLAP cubes

Строки accumulating snapshot обновляют намеренно. Прежние состояния не сохраняются, таблица показывает текущий статус. Редкие сложные случаи анализируют по transactions. С `OLAP cube` (многомерным кубом для анализа) такая таблица работает плохо: обновления меняют факты и ключи, и куб надо пересчитывать. Исключение — загрузка строки только после конца процесса.

### Дополняющие типы

Snapshots иногда работают вместе. Например, транзакции каждого дня добавляют в текущий accumulating snapshot месяца, а 36 месяцев истории лежат в periodic snapshot. В конце месяца текущая таблица становится новым месяцем ряда.

Transactions и snapshots дают разные взгляды на одну историю, и в одной таблице их не объединить. Небольшая избыточность допустима: задача DW/BI — публиковать данные для анализа.

## Интеграция по цепочке создания стоимости

Бизнесу нужен сквозной взгляд: например, клиент от запроса цены до оплаты и поддержки. IT нужна интеграция, чтобы не плодить несвязанные базы и использовать общие компоненты.

Книга предупреждает: без поддержки руководства проект, скорее всего, провалится. Согласие нельзя возлагать на одного менеджера DW/BI. Модели глав 3 и 4 уже делят dimensions даты, товара и магазина. Без общих dimensions модели не объединить.

## Enterprise data warehouse bus architecture

Строить всё хранилище одним проектом слишком сложно, а изолированные части теряют согласованность. Книга советует архитектурный, инкрементальный подход: `enterprise data warehouse bus architecture`.

### Что такое bus

`Bus` — не сокращение от business. Это общая структура, к которой всё подключается, как шина компьютера: устройства разных производителей работают вместе. Если команды следуют стандарту, модели процессов «подключаются» друг к другу.

Процессы цепочки образуют семейство dimensional models с общими `conformed dimensions`. Единый набор стандартных dimensions и facts даёт каркас. Команды строят процессы почти независимо, а модели потом складываются вместе. Bus не зависит от технологии: подходят реляционные и OLAP-модели.

### Bus matrix

`Bus matrix` документирует bus architecture. Строки — бизнес-процессы, столбцы — общие dimensions, крестик — процесс использует dimension.

| Процесс | Дата | Товар | Склад | Магазин | Акция | Клиент |
|---|---|---|---|---|---|---|
| Заказы поставщикам | X | X | X | | | |
| Запасы на складе | X | X | X | | | |
| Запасы в магазине | X | X | | X | | |
| Розничные продажи | X | X | | X | X | X |

Строки — процессы, а не отделы. Проект начинают с одной строки: главный риск — слишком большой ETL, а одна строка часто значит один источник. Сводные процессы вроде прибыльности откладывают: на них легко утонуть.

### Как используют матрицу

Матрица — один из важнейших результатов проекта. Она служит для планирования архитектуры, проектирования, governance, оценки и коммуникации. Общие dimensions определяют ответственные за данные, а не один отдел. По числу dimensions в строке оценивают объём работ. Руководству матрица показывает поэтапный план и нужду в экспертах бизнеса.

### Opportunity/stakeholder matrix

Те же процессы-строки сравнивают не с dimensions, а с бизнес-функциями: мерчандайзинг, маркетинг, операции магазина, логистика, финансы. Так видно, кого звать на встречи по требованиям, когда процесс становится проектом.

### Типичные ошибки в bus matrix

Чаще всего путают уровень детали строк и столбцов.

| Что | Слишком широко | Слишком узко |
|---|---|---|
| Строки | Отделы компании | Список отчётов |
| Столбцы | «Person» из сотрудников, поставщиков и клиентов | Столбец на каждый уровень иерархии или атрибут |

### Привязка существующих моделей к bus matrix

Изолированные модели хуже упущенной возможности: отчёты несравнимы, а модели становятся legacy. Если начинать не с нуля, честно оцените разрыв, составьте поэтапный план и продайте его руководству.

Хорошую dimension можно сопоставить со стандартной через cross-reference map и пересчитать fact table с новыми ключами. Если атрибуты различаются, BI-запросы придётся переделать. Чаще в моделях и другие ошибки, например неверный grain. Тогда проще начать заново: книга признаёт, что «stovepipe» модели часто закрывают.

## Conformed dimensions

`Conformed dimension` — стандартная dimension, общая для fact tables разных процессов. Её строят один раз в ETL и копируют по хранилищу. Команды обязаны её использовать. Книга советует, чтобы использование предписал CIO.

### Drill across

Conformed dimensions позволяют собрать в одном отчёте метрики разных процессов. Каждую модель запрашивают отдельно (`multipass SQL`), потом результаты соединяют `full outer join` по общему атрибуту, например названию товара. Full outer join сохраняет строки, которые есть только в одном результате. Это `drill across`. Расчёты между fact tables обычно делают уже в BI-приложении.

### Identical conformed dimensions

Простейший вариант: одинаковы ключи, названия атрибутов, определения и значения. `Month` и `Month Name`, `July` и `JULY` не conform. Если у dimension есть лишние атрибуты для запасов, она всё равно conform, но по ним drill across невозможен.

### Shrunken rollup: подмножество атрибутов

`Shrunken rollup dimension` нужна, когда fact table хранит данные выше базового уровня. Пример: недельный snapshot рядом с дневным или прогноз по бренду при продажах по товару. Dimension бренда conform с dimension товара, если её атрибуты — строгое подмножество. Общие атрибуты (бренд, категория) называют и заполняют одинаково, но ключи разные.

### Shrunken: подмножество строк

`Shrunken dimension` с подмножеством строк: тот же уровень детали, но только часть строк. Пример: корпоративная dimension товаров, из которой направление бизнеса берёт свои товары. Fact table тоже нужно ограничить этим подмножеством, иначе нарушится ссылочная целостность. Подробнее — в [главе 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/). Dimension месяца — оба случая сразу: строки конца месяца из dimension даты без дневных столбцов, например признака выходного.

### Shrunken dimensions в bus matrix

Новый несвязанный столбец не нужен. Отметьте клетку базовой dimension и запишите уровень текстом либо разделите столбец на уровни, например «день» и «месяц».

### Limited conformity

Полная conformity бывает нереальна. Пример: дочерние компании из разных отраслей без общих клиентов и товаров. Но готовность договориться об определении товара или клиента — главный тест для enterprise DW/BI. Если её нет, книга советует отдельные хранилища. Обычно хватает начать с нескольких общих атрибутов: описание товара, категория, направление бизнеса.

## Data governance и stewardship

Главная трудность — согласие по названиям и содержимому атрибутов (как менять значения атрибутов со временем, см. [главу 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)). Отделы задавали правила сами, отсюда силосы: похожие, но разные версии правды. Руководство должно признать проблему. IT может помочь, но не имеет полномочий вести её одна.

### Governance, которым управляет бизнес

Вести работу должны эксперты бизнеса: уважаемые в компании, знающие операции, умеющие балансировать нужды отдела и компании, с авторитетом и навыками переговоров. Conformed dimensions критикуют за сложность. Книга согласна, но в этом суть единых данных: если все требуют свои названия и правила, единой версии правды нет.

### Цели governance

Главная цель — общие определения, названия и значения. Иначе одинаковые слова значат разное, а разные слова — одно. Общие master data — вопрос культуры, а не технологии. Governance также задаёт правила качества, безопасности и доступа. ERP и `MDM` помогают, но не решают проблему: сильный governance нужен при любом подходе.

## Conformed dimensions и agile

Возражение: при agile нет времени согласовывать dimensions. Книга отвечает: conformed dimensions ускоряют agile. Dimension строят один раз, а не пересоздают в каждом цикле. Новый источник подключается быстрее, и работа в основном сводится к fact tables.

Согласовывать все атрибуты не нужно. Начните с атрибутов, важных для всей компании, даже с одного, например категории товара, и расширяйте набор итерациями. Без этого наборы выглядят сопоставимыми, а правила чуть отличаются, и пользователи тратят время на сверку.

## Conformed facts

Conformed dimensions — 95 % работы над архитектурой данных, а определения фактов — остальные 5 %. Выручка, прибыль, цены, себестоимость и другие KPI тоже должны conform.

Одинаковое название требует одинакового определения, формулы и единиц. Выручку из разных процессов можно складывать, только если определения совпадают. Если точно согласовать нельзя, дайте разные названия. Единицы тоже бывают разные: коробки на складе, штуки в магазине. Коэффициент в dimension товара книга считает плохим решением: легко ошибиться. Правильно хранить факт в обеих единицах (подробнее в [главе 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)).

## Итоги главы

- `Periodic snapshot` подходит для постоянно пополняемых запасов, `accumulating snapshot` — для конечного конвейера. Обычно нужна ещё `transaction` fact table.
- Остаток `semi-additive`: по датам его усредняют, а SQL `AVG` считает по строкам, а не по датам.
- Periodic snapshot плотный: строки пишут и при нулевом остатке, а старые срезы можно делать реже.
- Строки accumulating snapshot обновляют намеренно, и с OLAP cubes это плохо работает.
- Разный grain или набор dimensions значит разные процессы и разные fact tables.
- Строки `bus matrix` — процессы, столбцы — общие dimensions. Проект начинают с одной строки.
- `Conformed dimension` одинакова везде или является строгим подмножеством базовой. Это позволяет делать `drill across`.
- Согласие по dimensions и фактам — задача governance под руководством бизнеса. Она ускоряет agile.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Periodic snapshot` | Срез состояния через равные интервалы |
| `Semi-additive fact` | Суммируется не по всем dimensions, например остаток |
| `Accumulating snapshot` | Одна обновляемая строка на проход через процесс |
| `Bus matrix` | Процессы в строках, conformed dimensions в столбцах |
| `Conformed dimension` | Одна и та же dimension в разных моделях |
| `Shrunken dimension` | Conformed dimension с подмножеством атрибутов или строк |
| `Drill across` | Объединение метрик разных fact tables |

## Что это значит на практике

- Не берите `sum` остатка по датам. Сначала суммируйте по товарам и складам внутри даты, потом `avg` по датам или значение на последнюю дату.
- В `dbt` snapshot остатков строят как `incremental`: новая порция строк на каждый день. Не путайте его с `dbt snapshot`, который хранит историю изменений.
- Accumulating snapshot в `dbt` — это `incremental` с `merge` по ключу партии. Lags пересчитывайте при каждом обновлении.
- Оцените объём snapshot заранее: товары × места × дни. Старые данные храните по неделям в отдельной таблице.
- Нарисуйте bus matrix до кода и начните с одной строки.
- Тест `relationships` в `dbt` проверяет, что у каждого ключа в fact есть строка в conformed dimension.
- Для отчёта по двум fact tables агрегируйте каждую отдельно, потом делайте `full outer join` по общему атрибуту.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку в одной сессии.

### Шаг 1. Создаём dimensions и transactions

```sql
-- превращает date key вида 20240105 в DATE
CREATE MACRO key_to_date(k) AS strptime(k::VARCHAR, '%Y%m%d')::DATE;

-- ключ 0 = «ещё не наступило» для вех accumulating snapshot
CREATE TABLE dim_date AS
SELECT strftime(d, '%Y%m%d')::INT AS date_key, d::DATE AS full_date
FROM generate_series(DATE '2024-01-01', DATE '2024-01-07', INTERVAL 1 DAY) t(d)
UNION ALL
SELECT 0, NULL;

CREATE TABLE dim_product AS
SELECT * FROM (VALUES
    (1, 'SKU-1', 'Дрель',  50.0),
    (2, 'SKU-2', 'Молоток', 8.0)
) t(product_key, sku, product_name, unit_cost);

CREATE TABLE dim_warehouse AS
SELECT * FROM (VALUES
    (1, 'Склад Север', 'Москва'),
    (2, 'Склад Юг',    'Краснодар')
) t(warehouse_key, warehouse_name, city);

CREATE TABLE dim_txn_type AS
SELECT * FROM (VALUES (1, 'receipt'), (2, 'sale'), (3, 'adjustment')) t(txn_type_key, txn_type);

-- grain: одно движение товара
CREATE TABLE fact_inventory_txn AS
SELECT strftime(txn_date, '%Y%m%d')::INT AS date_key,
       product_key, warehouse_key, txn_type_key, quantity_change
FROM (VALUES
    (DATE '2024-01-01', 1, 1, 1, 100),
    (DATE '2024-01-01', 2, 1, 1,  50),
    (DATE '2024-01-01', 1, 2, 1,  40),
    (DATE '2024-01-02', 1, 1, 2, -30),
    (DATE '2024-01-02', 2, 1, 2, -10),
    (DATE '2024-01-03', 1, 1, 1,  20),
    (DATE '2024-01-03', 1, 2, 2, -15),
    (DATE '2024-01-05', 1, 1, 2, -40),
    (DATE '2024-01-05', 2, 1, 3,  -2),
    (DATE '2024-01-06', 2, 1, 2,  -8),
    (DATE '2024-01-06', 1, 2, 2,  -5),
    (DATE '2024-01-07', 2, 1, 1,  30)
) t(txn_date, product_key, warehouse_key, txn_type_key, quantity_change);
```

### Задания

**1.** Постройте periodic snapshot из transactions. Grain: товар × склад × день. Строка должна быть и в дни без движений (например, 4 января). Остаток — накопленная сумма. Добавьте `inventory_value` = остаток × `unit_cost`.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_inventory_snapshot AS
WITH grid AS (
    SELECT d.date_key, pw.product_key, pw.warehouse_key
    FROM dim_date d
    CROSS JOIN (SELECT DISTINCT product_key, warehouse_key FROM fact_inventory_txn) pw
    WHERE d.date_key <> 0
), daily AS (
    SELECT date_key, product_key, warehouse_key,
           sum(quantity_change) AS qty_change,
           sum(CASE WHEN txn_type_key = 2 THEN -quantity_change ELSE 0 END) AS quantity_sold
    FROM fact_inventory_txn
    GROUP BY ALL
), snap AS (
    SELECT g.date_key, g.product_key, g.warehouse_key,
           sum(coalesce(d.qty_change, 0)) OVER (
               PARTITION BY g.product_key, g.warehouse_key ORDER BY g.date_key
           )::INT AS quantity_on_hand,
           coalesce(d.quantity_sold, 0)::INT AS quantity_sold
    FROM grid g
    LEFT JOIN daily d USING (date_key, product_key, warehouse_key)
)
-- стоимость остатка: остаток × себестоимость единицы
SELECT s.*, s.quantity_on_hand * p.unit_cost AS inventory_value
FROM snap s
JOIN dim_product p USING (product_key);

-- проверка: остаток на 7 января равен сумме всех движений
SELECT (SELECT sum(quantity_on_hand) FROM fact_inventory_snapshot WHERE date_key = 20240107) AS from_snapshot,
       (SELECT sum(quantity_change) FROM fact_inventory_txn) AS from_txn;
```
</details>

**2.** Semi-additive остаток. Для каждого товара покажите: неверную сумму остатков по дням, средний дневной остаток и остаток на последний день. Остаток считайте по всем складам вместе.

<details>
<summary>Решение</summary>

```sql
WITH daily AS (
    SELECT date_key, product_key, sum(quantity_on_hand) AS qoh
    FROM fact_inventory_snapshot
    GROUP BY ALL
)
SELECT p.product_name,
       sum(qoh)                AS wrong_sum_over_days,   -- так нельзя
       round(avg(qoh), 1)      AS avg_daily_qoh,
       max_by(qoh, date_key)   AS qoh_last_day
FROM daily
JOIN dim_product p USING (product_key)
GROUP BY p.product_name
ORDER BY p.product_name;
```

`wrong_sum_over_days` растёт с числом дней. Это бессмысленное число. Для времени берите `avg` или последний день.
</details>

**3.** Inventory turns и days of supply. Для каждого товара посчитайте оборачиваемость: продано штук за неделю делить на средний остаток. И запас в днях (days of supply): остаток на последний день делить на средние продажи в день. Оба показателя non-additive: считаем их из компонентов.

<details>
<summary>Решение</summary>

```sql
WITH daily AS (
    SELECT date_key, product_key,
           sum(quantity_on_hand) AS qoh,
           sum(quantity_sold)    AS sold
    FROM fact_inventory_snapshot
    GROUP BY ALL
)
SELECT p.product_name,
       sum(sold)                         AS units_sold,
       round(avg(qoh), 1)                AS avg_qoh,
       round(sum(sold) / avg(qoh), 2)    AS turns,
       round(max_by(qoh, date_key) / avg(sold), 1) AS days_of_supply
FROM daily
JOIN dim_product p USING (product_key)
GROUP BY p.product_name
ORDER BY p.product_name;
```
</details>

**4.** Accumulating snapshot. Создайте таблицу партий. Grain: одна партия. Вставьте новые партии с датой приёмки. Потом обновите строки по событиям и посчитайте lags.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE fact_receipt_pipeline AS
SELECT lot_number, product_key, warehouse_key,
       received_date_key,
       0 AS inspected_date_key,
       0 AS bin_date_key,
       0 AS first_sale_date_key,
       NULL::INT AS inspect_lag_days,
       NULL::INT AS bin_lag_days,
       NULL::INT AS sale_lag_days
FROM (VALUES
    ('L1', 1, 1, 20240101),
    ('L2', 2, 1, 20240101),
    ('L3', 1, 2, 20240102),
    ('L4', 1, 1, 20240103)
) t(lot_number, product_key, warehouse_key, received_date_key);

-- события, которые пришли позже
CREATE TABLE stg_lot_events AS
SELECT * FROM (VALUES
    ('L1', 20240102, 20240103, 20240105),
    ('L2', 20240103, 20240104, 0),
    ('L3', 20240104, 0,        0)
) t(lot_number, inspected_key, bin_key, first_sale_key);

UPDATE fact_receipt_pipeline f
SET inspected_date_key  = e.inspected_key,
    bin_date_key        = e.bin_key,
    first_sale_date_key = e.first_sale_key
FROM stg_lot_events e
WHERE f.lot_number = e.lot_number;

UPDATE fact_receipt_pipeline
SET inspect_lag_days = CASE WHEN inspected_date_key <> 0
        THEN date_diff('day', key_to_date(received_date_key), key_to_date(inspected_date_key)) END,
    bin_lag_days = CASE WHEN bin_date_key <> 0
        THEN date_diff('day', key_to_date(inspected_date_key), key_to_date(bin_date_key)) END,
    sale_lag_days = CASE WHEN first_sale_date_key <> 0
        THEN date_diff('day', key_to_date(bin_date_key), key_to_date(first_sale_date_key)) END;

SELECT * FROM fact_receipt_pipeline ORDER BY lot_number;
```

Одна строка на партию. Каждый lag — дни между соседними вехами. Полный путь от приёмки до продажи — их сумма. Вехи, которых ещё не было, равны 0 («ещё не наступило»), а lag равен `NULL`.
</details>

**5.** Анализ конвейера. Покажите воронку: сколько партий дошло до каждой вехи. Потом средние lags. Затем найдите «застрявшие» партии: проверены, но ещё не размещены на складе.

<details>
<summary>Решение</summary>

```sql
SELECT count(*)                                              AS lots_received,
       count(*) FILTER (WHERE inspected_date_key  <> 0)      AS lots_inspected,
       count(*) FILTER (WHERE bin_date_key        <> 0)      AS lots_binned,
       count(*) FILTER (WHERE first_sale_date_key <> 0)      AS lots_sold
FROM fact_receipt_pipeline;

SELECT round(avg(inspect_lag_days), 2) AS avg_inspect_lag,
       round(avg(bin_lag_days), 2)     AS avg_bin_lag,
       round(avg(sale_lag_days), 2)    AS avg_sale_lag
FROM fact_receipt_pipeline;

-- застряли после проверки
SELECT lot_number, key_to_date(inspected_date_key) AS inspected_on
FROM fact_receipt_pipeline
WHERE inspected_date_key <> 0 AND bin_date_key = 0;
```

`avg` игнорирует `NULL`, поэтому незавершённые вехи не портят средние. Застряла партия L3.
</details>

## Вопросы для самопроверки

1. Почему остаток нельзя суммировать по датам? Что взять вместо `sum` и почему SQL `AVG` по строкам даёт неверный результат?
2. Когда для запасов выбирают periodic snapshot, когда accumulating snapshot, а когда нужна ещё и transaction fact table?
3. Почему строки accumulating snapshot обновляют, а в других типах нет? Какую проблему это создаёт для OLAP cubes?
4. Почему строки bus matrix — это процессы, а не отделы? Почему проект начинают с одной строки?
5. Чем shrunken rollup dimension отличается от shrunken dimension с подмножеством строк? Приведите пример каждой.
6. Почему книга говорит, что conformed dimensions помогают agile, а не мешают?

Предыдущая: [Глава 3. Продажи в рознице](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/). Следующая: [Глава 5. Закупки и SCD](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/).
