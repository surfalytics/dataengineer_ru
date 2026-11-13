---
title: "The Data Warehouse Toolkit, глава 10: Финансовые услуги"
head:
  - tag: title
    content: "Банк: household, bridge, supertype в DWH | Инжиниринг Данных"
description: "Конспект главы 10 The Data Warehouse Toolkit: снимок счетов, household, bridge с весами, mini-dimension, dynamic banding, supertype. Практика в DuckDB."
sidebar:
  order: 10
  label: "10. Финансовые услуги"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в банке главный процесс — ежемесячный снимок счетов. Схема из двух dimensions здесь слишком бедная, поэтому авторы добавляют филиал, продукт, статус счёта, клиента и household. Для совместных счетов они вводят `bridge table` с весами, а для разных продуктов — пары `supertype` и `subtype` fact table.

## О чём глава

[Глава 9](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/) разобрала HR: историю сотрудника, headcount snapshot и многозначные атрибуты. Глава 10 берёт розничный банк. Она отвечает на вопрос: как смоделировать счета с несколькими владельцами, меняющимися профилями и очень разными продуктами? Техники подходят и другим бизнесам.

- `Dimension triage`: как найти пропущенные dimensions.
- `Household` и клиенты счёта через `bridge table` с весами.
- `Mini-dimension` в fact table и в bridge.
- `Dynamic value banding`.
- `Supertype` и `subtype` для разных продуктов.
- `Hot swappable dimensions`.

![Модель банка: снимок счетов, mini-dimension профиля, bridge счёт-клиент и household](/assets/data-warehouse-toolkit/ch10-bank-star.png)

Как читать схему: слева вверху общая fact table по всем счетам (`supertype`), справа fact table чековых счетов (`subtype`). Клиенты подключаются к счёту через `bridge_account_customer`. Схема упрощена для практики: продукт и филиал лежат в `dim_account`, а книга выносит их в отдельные dimensions.

## Банковский кейс и bus matrix

Банк хочет смотреть и на счёт, и на `household` — группу счетов одного домохозяйства. Цель — маркетинг: предлагать новые продукты тем household, у которых уже есть счёт.

Строки `bus matrix` (таблица процессов и dimensions, см. [главу 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)) идут вдоль жизни клиента. Поиск клиентов и лиды работают с `prospect` (потенциальным клиентом). Заявка на счёт добавляет клиента и счёт, открытие счёта — household. Операции, ежемесячный снимок и обслуживание используют дату, клиента, счёт, продукт, household и филиал.

Из интервью вышли пять требований:

- Пять лет ежемесячных снимков по каждому счёту.
- У каждого счёта есть основной остаток, и бизнес сравнивает разные типы счетов.
- У каждого типа счёта (в банке — продукта) свои атрибуты и факты.
- Каждый счёт принадлежит одному household, и эта связь заметно меняется из-за жизненных событий.
- Нужны демография клиентов и household и поведенческие оценки (`scores`).

## Dimension triage: как не получить слишком мало dimensions

Требования дают `grain`: одна строка на счёт за месяц. Это `periodic snapshot`. С таким grain можно сделать схему всего из двух dimensions, месяца и счёта. Филиал, продукт и household тогда становятся атрибутами `dim_account`, ведь у счёта один филиал, один продукт и один household.

Связи в такой схеме верны, но авторы считают её плохой:

- Пользователи видят филиал и продукт как отдельные срезы. Отдельные dimensions — маленькие точки входа в fact table.
- В банке миллионы счетов, и `SCD` type 2 раздует `dim_account`. Вынос продукта и филиала замедляет рост строк.
- Продукт и филиал — разные dimensions: у них связь many-to-many и разный ритм изменений.

В большинстве моделей от 5 до 20 dimensions. Если их пять или меньше, возможно, вы что-то забыли. Проверьте:

- `causal`: promotion, договор, погода ([глава 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/));
- несколько дат, особенно в `accumulating snapshot` ([глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/));
- `degenerate dimension`: номер заказа или счёта;
- `role-playing dimension`: несколько сущностей или дат одной операции ([глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/));
- `status`, `audit dimension` и `junk dimension`.

Такие dimensions можно добавить даже в работающую систему: они не меняют grain, ключи, факты и отчёты. Критерий простой: описательный атрибут с одним значением на строку fact можно добавить в dimension или сделать из него новую.

Авторы выбрали семь dimensions: дата конца месяца, филиал, счёт, основной клиент, продукт, статус счёта и household. В снимке лежат общие факты: остаток на конец месяца, средний дневной остаток, число операций, проценты и комиссии. Остаток похож на складской: по времени его не суммируют (`semi-additive`), а усредняют, то есть делят сумму на число периодов. Эту fact table авторы называют `supertype`, а таблицы по продуктам — `subtype`.

- `Product` — простая иерархия: название, тип, категория, как иерархия товаров в магазине.
- `Branch` похожа на dimension магазина или склада.
- `Account status` показывает состояние на конец месяца: активен, открыт или закрыт. Это полноценная dimension с расшифровками и причинами, а не код в fact table и не атрибут `dim_account`. Авторы считают её ещё одним примером `mini-dimension` из [главы 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/).

### Household dimension: домохозяйство как отдельная dimension

Бизнесу нужен взгляд на всю экономическую единицу: профиль household, масштаб отношений и продукты, которые ему ещё можно продать. Атрибуты household (доход, жильё, пенсионеры, дети) меняются, и пользователи хотят видеть историю.

Пример книги: у John и Mary Smith есть чековый счёт John, сберегательный счёт Mary, совместный чековый счёт, кредитная карта и ипотека. Все пять счетов входят в один household, хотя имя и адрес в системах могут слегка отличаться.

`Householding` — непростая задача: нужны бизнес-правила и алгоритмы, и крупные банки вкладывают в это заметные ресурсы.

Account и household авторы делают отдельными dimensions по двум причинам. Первая — размер: `dim_account` легко превышает 10 миллионов строк, а household бывают миллионами, и они дают меньшую точку входа в fact table. Вторая — изменчивость: связь счетов с household часто меняется. Поэтому ключ household лежит в fact table, а не в `dim_account`. Так банк не ведёт `SCD` type 2 на таблице в 10 миллионов строк.

### Multivalued dimensions и weighting factors

У счёта бывает несколько владельцев. Клиента нельзя сделать атрибутом счёта (кроме основного клиента): нарушится grain dimension. Нельзя и добавить `customer_key` в fact table: нарушится grain «счёт за месяц». Это `multivalued dimension`. Её связывают с fact table через `bridge table` «счёт-клиент». Ключ bridge — как минимум surrogate keys счёта и клиента. Если связь меняется, строки bridge получают отметки времени, как в [главе 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/).

У счёта с двумя владельцами в bridge две строки. Каждая получает `weighting factor` — долю, и сумма весов счёта ровно 1,00. Веса делят аддитивные факты между владельцами, поэтому итог по клиентам сходится с общим. Такой отчёт авторы называют `correctly weighted report`.

> **Пояснение:** в SQL это `sum(balance * weighting_factor)` после `JOIN` fact и bridge.

Можно сменить grain на «счёт за месяц на владельца» и физически умножить факты на веса. Авторы так почти не делают, по трём причинам:

- Fact table вырастет в число владельцев раз.
- Multivalued dimensions бывает несколько, число строк выходит из-под контроля, и строка теряет смысл.
- Бизнесу нужны и неразделённые суммы, а восстановить их из умноженных значений трудно.

Без весов получается `impact report`. Пример: «Каков общий остаток всех людей с таким-то демографическим профилем?» Счёт считается у каждого владельца полностью, поэтому итог может быть больше реального. Чтобы BI-инструмент видел обычную fact table, авторы советуют два SQL view поверх fact и bridge: с весами и без.

Если клиент известен в каждой операции, bridge не нужен. Например, у каждого держателя кредитной карты свой номер. Но для метрик уровня счёта, например биллинга, bridge нужен.

### Mini-dimensions: ещё раз

У счетов, клиентов и household много изменчивых атрибутов: ежемесячные данные кредитного бюро, внешняя демография, оценки поведения, прибыльности и просрочек. Банку важна история изменений, но `SCD` type 2 на `dim_account` не подходит: строк много, а атрибуты часто меняются.

Авторы выносят их в несколько `mini-dimension` (type 4), например «кредитное бюро» и «демография». Их ключи лежат в fact table. Так fact можно фильтровать по профилю, а история сохраняется, даже при разной частоте обновления. Технику разбирали в [главе 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/) и [главе 8](/book-summaries/engineering/data-warehouse-toolkit/08-crm/).

В банке она работает хорошо: в periodic snapshot у каждого счёта каждый месяц есть строка для ключей. Но авторы предупреждают: не злоупотребляйте. Mini-dimension — группа связанных атрибутов, а не по одной на атрибут.

Значения хранят диапазонами, иначе строк слишком много. Вместо дохода $31 257,98 лежит диапазон $30 000–34 999, а оценка прибыльности от 1 до 1200 попадает в диапазон вроде 101–150. Для data mining и проверки самих диапазонов нужны точные значения. Тогда диапазон остаётся в mini-dimension для ежедневных отчётов, а точный score хранится ещё и как факт в месячном снимке. Названия копий должны различаться. Авторы советуют взвешивать пользу копий и рост сложности ETL и BI.

> **Пояснение:** в практике ниже `dim_account_profile` хранит диапазон остатка и статус активности. Это упрощение. В книге в mini-dimension лежат демография и оценки риска.

### Mini-dimension в bridge table

Bridge «счёт-клиент» может стать огромным. При 20 миллионах счетов и 25 миллионах клиентов он за несколько лет вырастет до сотен миллионов строк, если обе dimensions ведутся как `SCD` type 2. А быстро меняющаяся демография превратит и 25 миллионов клиентов в `monster dimension`.

Обычно демографию выносят в mini-dimension в fact table. Но клиент подключён через bridge, и места в fact table нет. Решение: добавить ключ mini-dimension в сам bridge. Теперь ключ bridge — счёт, клиент и демография. Чтобы bridge не рос слишком быстро, в него пишут только изменения на конец месяца: grain корневой fact table — счёт за месяц.

### Dynamic value banding

Бизнес хочет отчёт по диапазонам остатка: 0–1000, 1001–2000, до «10 001 и выше». Для каждого диапазона нужны число счетов и сумма остатков. В примере книги отчёт читает больше миллиона счетов. Готовые диапазоны в dimension бизнесу не подходят: он хочет менять границы прямо в запросе. Это трудно: в SQL нет `GROUP BY` для диапазонов, а диапазоны бывают разного размера и с текстовыми названиями.

Решение — таблица определения диапазонов (`band definition table`): группа диапазонов, порядок сортировки, название, нижняя и верхняя граница. Групп может быть сколько угодно. Таблица соединяется с fact table условиями «больше» и «меньше». Название диапазона служит заголовком строки.

> **Пояснение:** границу обычно берут `>= нижняя AND < верхняя`, чтобы значение попало только в один диапазон.

Скорость запроса — проблема: у него почти нет фильтров, а соединение по диапазонам не сужает выборку. Тогда может понадобиться индекс прямо на остатке в fact table. Если СУБД умеет быстро сортировать и сжимать колонку, запросы сильно ускоряются. Эту идею первой реализовала колоночная СУБД Sybase IQ в начале 1990-х.

## Supertype и subtype для разных продуктов

У банка много продуктов и общие клиенты. У каждого счёта есть основной остаток и проценты, но у каждого продукта есть и своё. У чековых счетов это минимальный остаток, лимит овердрафта, комиссии и метрики онлайн-банка. У срочных депозитов (CD) почти ничего общего с ними, зато есть срок погашения, частота капитализации и текущая ставка.

Пользователям нужны два взгляда, и в одной fact table их трудно совместить:

- **Глобальный.** Все счета вместе, для cross-sell и up-sell по всей клиентской базе. Для этого нужна одна `supertype` fact table. В ней только факты, общие почти для всех продуктов: несовместимых фактов сотни. Dimension продукта в supertype тоже содержит только общие атрибуты.
- **Линия бизнеса.** Глубокий анализ одного продукта, например чековых счетов, с его особыми фактами и атрибутами.

Если собрать всё в одну таблицу, получатся сотни особых фактов, и в каждой строке почти везде `NULL`. Авторы сравнивают такие таблицы со швейцарским сыром, полным дыр. Решение — `subtype` схема для линии бизнеса: fact table и dimension только для чековых счетов. В примере книги в ней есть число овердрафтов, штрафы за них, число операций по банкомату и онлайн, дни ниже минимального остатка.

Subtype содержит и общие факты и атрибуты supertype, чтобы не соединять таблицы двух схем. Пользователь работает либо на supertype (кросс-продуктовый анализ), либо на одной subtype схеме: объединять несколько subtype обычно не нужно, их факты почти не пересекаются.

Subtype dimension счёта использует те же surrogate keys, что supertype dimension со всеми счетами. Поэтому она — `shrunken conformed dimension`: часть строк supertype с дополнительными атрибутами. Авторы советуют такое семейство таблиц, когда у продуктов разные факты и описания, а клиентская база одна. Подход годится любому бизнесу с разными продуктами. Если линии бизнеса физически разделены, данные supertype копируются ровно один раз: subtype делят счета без пересечений.

### Supertype и subtype с общими facts

Метрики некоторых процессов не зависят от линии бизнеса, например заявки на новые счета. Тогда хватает одной supertype fact table. Но продукты остаются разными, поэтому строят полный набор subtype dimensions счетов. В кросс-продуктовом анализе берут supertype dimension, а для одного типа счёта можно взять subtype dimension с его особыми атрибутами.

## Hot swappable dimensions

У брокера много клиентов, которые читают одну fact table с дневными ценами акций (максимум, минимум, закрытие). У каждого клиента свой конфиденциальный набор атрибутов акций. Поэтому у каждого своя копия dimension акции, и она подключается к fact table в момент запроса. Авторы называют такие dimensions `hot swappable`. В реляционной СУБД ограничения ссылочной целостности между fact и dimensions, скорее всего, придётся отключить, чтобы подстановка работала в каждом запросе.

## Итоги главы

- Главный процесс банка — месячный снимок счетов с grain «один счёт за месяц».
- Схема из двух dimensions бедна. В модели обычно от 5 до 20 dimensions, а пропущенные можно добавить без смены grain.
- Остаток — `semi-additive` факт: по времени его усредняют, а не суммируют.
- Ключ household лежит в fact table, чтобы не вести `SCD` type 2 на миллионах счетов.
- Bridge «счёт-клиент» с `weighting factor` (сумма 1,00) даёт `correctly weighted report`. Без весов получается `impact report`.
- Быстро меняющиеся профили выносят в `mini-dimension` из связанных атрибутов. Если клиент подключён через bridge, ключ mini-dimension кладут в bridge.
- `Dynamic value banding` строится на таблице диапазонов, а скорость дают индекс на факте или колоночная СУБД.
- Общие факты всех продуктов лежат в `supertype`, особые факты линий — в `subtype`, с теми же surrogate keys.
- `Hot swappable dimensions` дают каждому клиенту свою версию dimension при одной fact table.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Dimension triage` | Проверка модели с малым числом dimensions: ищем пропущенные |
| `Periodic snapshot` | Fact table с одной строкой на объект в каждом периоде |
| `Semi-additive` | Факт не суммируется по времени, например остаток |
| `Household` | Группа счетов и клиентов с общими финансами |
| `Multivalued dimension` | Dimension с несколькими значениями на строку fact, например владельцы счёта |
| `Bridge table` | Таблица связи many-to-many |
| `Weighting factor` | Доля факта на владельца, сумма по счёту 1,00 |
| `Impact report` | Отчёт без весов, итог может быть больше реального |
| `Mini-dimension` | Маленькая dimension быстро меняющихся атрибутов (type 4) |
| `Supertype` / `subtype` | Общая fact table всех продуктов и таблицы особых фактов по линиям |
| `Shrunken conformed dimension` | Часть строк общей dimension с теми же ключами |

## Что это значит на практике

- Остаток не суммируйте по времени. Берите среднее (сумма, делённая на число периодов) или остаток на нужную дату.
- Проверяйте веса: `sum(weighting_factor) = 1` для каждого счёта. Это хороший тест для `dbt`.
- Изменчивые атрибуты выносите в mini-dimension при загрузке. Не создавайте новую версию счёта на каждое изменение.
- Делайте два view над fact и bridge, с весами и без, и называйте их так, чтобы никто не смешал точные итоги с impact-анализом.
- Границы диапазонов держите в таблице, а не в SQL и не в fact table.
- Для общего отчёта и особых метрик держите два уровня fact table и одни и те же surrogate keys счёта.
- Household определяет отдельный алгоритм. Запишите правило в документацию и добавьте тесты.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.

### Шаг 1. Создаём счета, клиентов, bridge и снимки

```sql
CREATE TABLE dim_date AS
SELECT strftime(last_day(d), '%Y%m')::INT AS month_key, last_day(d) AS month_end
FROM generate_series(DATE '2024-01-01', DATE '2024-06-01', INTERVAL 1 MONTH) t(d);

CREATE TABLE dim_household AS
SELECT * FROM (VALUES (1,'Ивановы'),(2,'Петровы'),(3,'Сидоров'),(4,'Кузнецова')) t(household_key, household_name);

CREATE TABLE dim_customer AS
SELECT * FROM (VALUES
    (1,'Иван Иванов'),(2,'Мария Иванова'),
    (3,'Пётр Петров'),(4,'Ольга Петрова'),
    (5,'Сергей Сидоров'),(6,'Анна Кузнецова')
) t(customer_key, customer_name);

CREATE TABLE dim_account AS
SELECT * FROM (VALUES
    (1,'40817-001','checking','Центр'),
    (2,'40817-002','savings', 'Центр'),
    (3,'40817-003','checking','Север'),
    (4,'40817-004','savings', 'Север'),
    (5,'40817-005','checking','Север'),
    (6,'40817-006','checking','Центр'),
    (7,'40817-007','savings', 'Центр'),
    (8,'40817-008','checking','Юг')
) t(account_key, account_number, product_type, branch);

-- результат householding-алгоритма: какой household у счёта (staging для ETL)
CREATE TABLE stg_account_household AS
SELECT * FROM (VALUES (1,1),(2,1),(3,2),(4,2),(5,2),(6,3),(7,4),(8,2)) t(account_key, household_key);

-- bridge: сумма весов на счёт равна 1
CREATE TABLE bridge_account_customer AS
SELECT * FROM (VALUES
    (1,1,0.5),(1,2,0.5),
    (2,1,1.0),
    (3,3,1.0),
    (4,3,0.5),(4,4,0.5),
    (5,4,1.0),
    (6,5,1.0),
    (7,6,1.0),
    (8,3,0.5),(8,4,0.5)
) t(account_key, customer_key, weighting_factor);

-- mini-dimension: комбинации банд остатка и активности
CREATE TABLE dim_account_profile AS
SELECT row_number() OVER () AS profile_key, b.balance_band, s.activity_status
FROM (VALUES ('1. до 3 000'),('2. 3 000-8 000'),('3. выше 8 000')) b(balance_band)
CROSS JOIN (VALUES ('active'),('dormant')) s(activity_status);

-- supertype: один счёт x месяц. Общие facts для всех продуктов.
-- household_key лежит в fact: связь счёт-household меняется со временем
CREATE TABLE fact_account_snapshot AS
WITH base AS (
    SELECT a.account_key, h.household_key, d.month_key,
           (a.account_key * 7919 + (d.month_key % 100) * 104729) % 1301 + 200 AS deposit_amount,
           (a.account_key * 6007 + (d.month_key % 100) * 86969) % 1499      AS withdrawal_amount,
           (a.account_key * (d.month_key % 100)) % 5                  AS txn_count,
           1500 * a.account_key                                       AS opening_balance
    FROM dim_account a
    JOIN stg_account_household h USING (account_key)
    CROSS JOIN dim_date d
),
bal AS (
    SELECT *, opening_balance
              + sum(deposit_amount - withdrawal_amount) OVER (PARTITION BY account_key ORDER BY month_key) AS ending_balance
    FROM base
)
SELECT b.month_key, b.account_key, b.household_key, p.profile_key,
       b.ending_balance, b.deposit_amount, b.withdrawal_amount, b.txn_count
FROM bal b
JOIN dim_account_profile p
  ON p.balance_band = CASE WHEN b.ending_balance < 3000 THEN '1. до 3 000'
                           WHEN b.ending_balance < 8000 THEN '2. 3 000-8 000'
                           ELSE '3. выше 8 000' END
 AND p.activity_status = CASE WHEN b.txn_count = 0 THEN 'dormant' ELSE 'active' END;

-- subtype: только чековые счета. Повторяет общие facts и добавляет свои
CREATE TABLE fact_checking_snapshot AS
SELECT s.month_key, s.account_key,
       s.ending_balance, s.deposit_amount, s.withdrawal_amount, s.txn_count,
       CASE WHEN s.ending_balance < 6000 THEN 25 ELSE 0 END AS overdraft_fee,
       s.txn_count * 3 AS atm_withdrawal_count
FROM fact_account_snapshot s
JOIN dim_account a USING (account_key)
WHERE a.product_type = 'checking';

CREATE TABLE band_ranges AS
SELECT * FROM (VALUES
    ('низкий',  0,     3000),
    ('средний', 3000,  8000),
    ('высокий', 8000,  1000000)
) t(band_name, from_amount, to_amount);
```

### Шаг 2. Проверяем

```sql
-- должно вернуть 0 строк: сумма весов каждого счёта равна 1
SELECT account_key, sum(weighting_factor) AS total_weight
FROM bridge_account_customer
GROUP BY account_key
HAVING abs(sum(weighting_factor) - 1) > 1e-9;

SELECT count(*) AS snapshot_rows, count(DISTINCT account_key) AS accounts FROM fact_account_snapshot;
```

### Задания

**1.** Household и bridge. Покажите остаток по household на июнь: `household_key` есть прямо в fact. Затем покажите остаток по клиентам через bridge: с весами и без весов. Сравните итоги с общим остатком.

<details>
<summary>Решение</summary>

```sql
SELECT h.household_name, sum(s.ending_balance) AS household_balance
FROM fact_account_snapshot s
JOIN dim_household h USING (household_key)
WHERE s.month_key = 202406
GROUP BY h.household_name
ORDER BY household_balance DESC;

SELECT c.customer_name,
       sum(s.ending_balance * b.weighting_factor) AS weighted_balance,
       sum(s.ending_balance)                      AS impact_balance
FROM fact_account_snapshot s
JOIN bridge_account_customer b USING (account_key)
JOIN dim_customer c USING (customer_key)
WHERE s.month_key = 202406
GROUP BY c.customer_name
ORDER BY weighted_balance DESC;

SELECT sum(ending_balance) AS total_balance FROM fact_account_snapshot WHERE month_key = 202406;
```

- Сумма по household и сумма `weighted_balance` равны общему остатку.
- Сумма `impact_balance` больше: совместные счета посчитаны у обоих владельцев. Книга называет это impact report. Он полезен («какие деньги затрагивает клиент»), но не для итогов.
</details>

**2.** Semi-additive. Покажите общий остаток банка по месяцам. Потом покажите, что будет, если просуммировать остаток по всем месяцам. Найдите правильное «среднее значение за период».

<details>
<summary>Решение</summary>

```sql
WITH m AS (
    SELECT month_key, sum(ending_balance) AS total_balance
    FROM fact_account_snapshot
    GROUP BY month_key
)
SELECT month_key, total_balance FROM m ORDER BY month_key;

SELECT sum(ending_balance) AS wrong_sum_over_time,
       sum(ending_balance) / count(DISTINCT month_key) AS avg_total_balance
FROM fact_account_snapshot;
```

Сумма по времени бессмысленна: она примерно в 6 раз больше реального остатка. Средний остаток за период считается как сумма, делённая на число месяцев.
</details>

**3.** Mini-dimension. Покажите число счетов в каждом банде остатка в январе и в июне. Затем найдите счета, у которых банд изменился между январём и июнем.

<details>
<summary>Решение</summary>

```sql
SELECT s.month_key, p.balance_band, count(*) AS accounts
FROM fact_account_snapshot s
JOIN dim_account_profile p USING (profile_key)
WHERE s.month_key IN (202401, 202406)
GROUP BY ALL
ORDER BY s.month_key, p.balance_band;

SELECT jan.account_key, pj.balance_band AS band_jan, pn.balance_band AS band_jun
FROM fact_account_snapshot jan
JOIN fact_account_snapshot jun
  ON jun.account_key = jan.account_key AND jun.month_key = 202406
JOIN dim_account_profile pj ON pj.profile_key = jan.profile_key
JOIN dim_account_profile pn ON pn.profile_key = jun.profile_key
WHERE jan.month_key = 202401 AND pj.balance_band <> pn.balance_band
ORDER BY jan.account_key;
```
</details>

**4.** Dynamic banding. Посчитайте число счетов и средний остаток по бандам из `band_ranges` на июнь. Затем измените границы в таблице и повторите запрос.

<details>
<summary>Решение</summary>

```sql
SELECT r.band_name, count(*) AS accounts, round(avg(s.ending_balance), 1) AS avg_balance
FROM fact_account_snapshot s
JOIN band_ranges r
  ON s.ending_balance >= r.from_amount AND s.ending_balance < r.to_amount
WHERE s.month_key = 202406
GROUP BY r.band_name
ORDER BY min(r.from_amount);
```

Fact не менялся. Банды можно менять без перезагрузки.
</details>

**5.** Supertype и subtype. Для чековых счетов покажите по месяцам остаток и комиссию за овердрафт. Используйте только subtype fact, без `JOIN`. Затем проверьте, что остаток чековых счетов на июнь в supertype и subtype совпадает.

<details>
<summary>Решение</summary>

```sql
SELECT month_key,
       count(*)                  AS checking_accounts,
       sum(ending_balance)       AS checking_balance,
       sum(overdraft_fee)        AS overdraft_fees,
       sum(atm_withdrawal_count) AS atm_withdrawals
FROM fact_checking_snapshot
GROUP BY month_key
ORDER BY month_key;

SELECT (SELECT sum(s.ending_balance) FROM fact_account_snapshot s
        JOIN dim_account a USING (account_key) WHERE a.product_type = 'checking' AND s.month_key = 202406) AS supertype_checking_jun,
       (SELECT sum(ending_balance) FROM fact_checking_snapshot WHERE month_key = 202406) AS subtype_checking_jun;
```

Subtype содержит только чековые счета (5 из 8). Он повторяет общие facts. Поэтому аналитик чековых счетов работает с одной таблицей и не соединяет её с supertype.
</details>

## Вопросы для самопроверки

1. Почему остаток на счёте — `semi-additive` факт и как считать средний остаток за период?
2. Зачем нужен `weighting factor` в bridge между счётом и клиентом? Чем `correctly weighted report` отличается от `impact report` и когда нужен второй?
3. Почему авторы кладут ключ household в fact table, а не в `dim_account`?
4. Когда выбрать mini-dimension, а когда dynamic value banding?
5. Где хранить ключ mini-dimension демографии, если клиент подключён через bridge, и почему?
6. Что выигрываем от разделения на `supertype` и `subtype`? Почему не одна широкая таблица и почему subtype повторяет общие факты?

Предыдущая: [Глава 9. HR](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/). Следующая: [Глава 11. Телеком](/book-summaries/engineering/data-warehouse-toolkit/11-telecommunications/).
