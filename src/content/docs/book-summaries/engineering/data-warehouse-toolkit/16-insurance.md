---
title: "The Data Warehouse Toolkit, глава 16: Страхование"
head:
  - tag: title
    content: "Страхование в DWH: policy, premium и claims | Инжиниринг Данных"
description: "Конспект главы 16 The Data Warehouse Toolkit: транзакции полиса, written и earned premium, claims, accumulating snapshot и 10 ошибок моделирования."
sidebar:
  order: 16
  label: "16. Страхование"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** в страховании клиент платит заранее, а компания зарабатывает эти деньги по месяцам. Поэтому сумма транзакций полиса не равна выручке. Авторы строят две дополняющие друг друга `fact table`: транзакции полиса и ежемесячный снимок премий. Для убытков (claims) они добавляют транзакции и `accumulating snapshot`.

## О чём глава

[Глава 15](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/) показала, как встроить clickstream в остальной бизнес. Глава 16 — последний кейс книги. Она отвечает на вопрос: как собрать модель страховой компании, если нужны почти все техники из прошлых глав сразу? Поэтому глава работает как повторение: без предыдущих глав она непонятна.

- Кейс, цепочка создания стоимости и `bus matrix`.
- Транзакции полиса: роли дат, `SCD`, `mini-dimension`, `supertype` и `subtype`.
- Ежемесячный `periodic snapshot`: written и earned premium.
- Claims: транзакции и `accumulating snapshot`.
- Общая таблица премий и убытков, аварии.
- Десять ошибок dimensional modeling.

![Star schema страхования: транзакции полиса, premium snapshot, claim и общие dimensions](/assets/data-warehouse-toolkit/ch16-insurance-star.png)

Как читать схему: слева транзакции полиса, справа месячный снимок премий, сверху claim. У всех трёх `fact table` общие `dimension`: покрытие, объект, policyholder. Схема упрощена для практики: в ней нет employee, claimant, claim profile и audit.

## Страховой кейс

Авторы описывают крупного страховщика имущества и ответственности: автомобили, дома, личное имущество. Интервью прошли в отделах убытков, полевых операций, андеррайтинга, финансов и маркетинга. Везде хотят использовать информацию эффективнее.

Нужные данные уже есть, но они не связаны. Один policyholder (страхователь) может быть в системах авто и дома как несколько разных клиентов. Отделы собрали свои хранилища, и на встречах руководства цифры расходились. Руководство поручило CIO разрушить «острова данных» и перейти от ориентации на продукт к ориентации на клиента.

## Цепочка создания стоимости страховщика

Цепочка короткая: выдать полис, получить премию, обработать claim — требование клиента о выплате. Пользователи хотят анализировать транзакции полиса и claims по покрытию (`coverage`), застрахованному объекту (`covered item`), policyholder и каналу продаж, и по всей компании, и по линиям бизнеса.

Все транзакции полиса авторы сводят в один бизнес-процесс и одну `fact table`. Если этого мало, их делят на котировку, расчёт тарифа и андеррайтинг ([глава 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/)).

Ещё нужна месячная премия по каждому полису: из неё складывается прибыль. Транзакция полиса не равна кусочку выручки, как продажа в рознице. Клиент платит заранее, как за подписку на журнал или расширенную гарантию, а компания зарабатывает деньги месяц за месяцем. Логика пересчёта транзакций в выручку очень сложная. Поэтому нужны обе таблицы: транзакции и snapshot. Snapshot — не сводка транзакций, а отдельный процесс с отдельным источником.

## Черновик bus matrix

`Bus matrix` — таблица: строки — бизнес-процессы, столбцы — общие dimensions ([глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)). Команда начинает с двух строк: транзакции полиса и месячный снимок премий. Основные dimensions: дата, policyholder, employee, покрытие, объект, полис. В снимке дату заменяет месяц, а employee — агент. Книга советует брать в черновик только основные dimensions, которые нужны больше чем в одной схеме.

## Транзакции полиса

Полис — набор покрытий, проданных policyholder. Покрытие — продукт страховщика: у дома пожар, кража, наводнение, у автомобиля столкновение и ответственность. Покрытие относится к конкретному объекту, а у объекта обычно несколько покрытий. Полис продаёт агент, актуарий считает тариф, андеррайтер принимает окончательное решение. Система фиксирует создание, изменение и отмену полиса и покрытий, расчёт тарифа и андеррайтинг, включая отказы.

`Grain`: одна строка на одну транзакцию полиса. Dimensions: дата транзакции, дата вступления в силу, policyholder, employee, покрытие, объект, номер полиса, тип транзакции.

### Role-playing dimensions: две даты

Дата транзакции — когда запись попала в систему. Дата вступления в силу (`effective date`) — когда транзакция действует юридически. В `fact table` для них два FK с разными именами. Физически это одна таблица дат, а пользователям её показывают через views с разными именами колонок (`role-playing dimension`, [глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)).

### Slowly changing dimensions

К policyholder применяют три базовых типа `SCD` из [главы 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/). Страховщики следят за изменениями.

| Атрибут | Тип | Почему |
|---|---|---|
| Дата рождения | Type 1 (перезапись) | Изменение считают исправлением ошибки |
| ZIP-код | Type 2 (новая строка) | ZIP — ключевой вход для тарифа и риска. Нужна точная история |
| Сегмент клиента | Type 3 (новая колонка) | Нужно временно смотреть и по старой, и по новой классификации |

При type 2 появляется новая строка dimension с новым `surrogate key`. Старые строки `fact table` не трогают, новые берут новый ключ. Метод мощный, но он усложняет ETL и увеличивает число строк. Type 3 подходит после массового пересмотра классификации. Он нечастый и становится сложным, если нужно хранить больше одной старой версии.

### Mini-dimensions для больших и быстро меняющихся dimensions

Dimension policyholder может иметь больше миллиона строк. При этом нужны точные значения атрибутов на момент полиса, изменения или claim. Решение из [главы 5](/book-summaries/engineering/data-warehouse-toolkit/05-procurement/): вынести часто меняющиеся атрибуты в `mini-dimension` (type 4) с отдельным ключом в `fact table`. Если созданы все комбинации значений, изменение — это другой ключ в новых строках `fact table`. Цена: просматривать такие атрибуты сложнее.

Covered item обычно больше policyholder, поэтому ему тоже подходит mini-dimension. Описания объектов не превращают в facts: они текстовые, а текст принадлежит dimensions.

### Multivalued dimension attributes

Многозначные атрибуты уже были в главах [9](/book-summaries/engineering/data-warehouse-toolkit/09-human-resources/), [10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/) и [14](/book-summaries/engineering/data-warehouse-toolkit/14-healthcare/). Здесь у коммерческого клиента несколько кодов отрасли, SIC или NAICS, иногда больше десятка. Их связывает `bridge table`, подключённая к `fact table` или к dimension клиента как `outrigger` (dimension, связанная с другой dimension). Если известны доли, в bridge добавляют `weighting factor`. Если кода нет, создают строку Unknown.

### Числовые атрибуты: fact или dimension

Оценочная стоимость дома меняется непрерывно и со временем, поэтому это `fact`. В dimension можно держать диапазон, например «250 000–299 999», для группировки. Лимит покрытия стандартный («до 250 000»), поэтому он остаётся атрибутом dimension.

### Degenerate dimension: номер полиса

Номер полиса — `degenerate dimension`, если вся информация о полисе вынесена в другие dimensions. Авторы предостерегают от обратного: fact table с парой ключей и перегруженной dimension полиса. Если у полиса остались свои атрибуты, например общая оценка риска, нужна dimension полиса, и номер перестаёт быть degenerate.

### Dimension с малой кардинальностью

Тип транзакции с причинами — узкая и неглубокая dimension, меньше 50 строк. Она всё равно остаётся отдельной таблицей, потому что её текст нужен для фильтров и подписей.

### Audit dimension

Строку `fact table` можно связать с `audit dimension`, которую создаёт процесс извлечения. Она хранит происхождение данных: время извлечения, таблицу-источник, версию ПО ([глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)).

### Fact table транзакций полиса

Это классическая transaction `fact table`: почти одни ключи и один числовой fact, сумма транзакции. Чем детальнее grain, тем больше dimensions. Смысл суммы зависит от типа транзакции, поэтому назвать её точнее нельзя.

### Supertype и subtype для разных продуктов

Бизнес хочет смотреть на компанию целиком, но не терять специфику линий: покрытия дома и авто сильно различаются. Здесь работает техника `supertype` и `subtype` из [главы 10](/book-summaries/engineering/data-warehouse-toolkit/10-financial-services/).

- Для каждой линии создают subtype-dimensions покрытия и объекта. Для авто это марка, год, франшиза.
- Отдельные subtype `fact table` для транзакций не нужны: метрики во всех линиях одни. Достаточно view на supertype `fact table`.
- Новые ключи не создают: subtype расширяет существующие строки dimension.

### Accumulating snapshot для полиса

Дополнительно можно построить `accumulating snapshot` с накопленным эффектом транзакций ([глава 4](/book-summaries/engineering/data-warehouse-toolkit/04-inventory/)). Grain: одна строка на покрытие и объект в полисе. Даты: котировка, расчёт тарифа, андеррайтинг, вступление в силу, продление, окончание. Таблица показывает время между вехами. Но отдельные транзакции она не хранит, поэтому выбросы теряются.

## Premium periodic snapshot

Из потока транзакций трудно понять статус и ценность действующего полиса на нужную дату. Пришлось бы прокручивать все транзакции с начала истории по сложным правилам признания выручки. Поэтому строят отдельную companion-таблицу: месячный снимок премий. Grain: одна строка на покрытие и объект в полисе за месяц.

| | Транзакции полиса | Premium snapshot |
|---|---|---|
| Grain | Одна транзакция | Покрытие × объект × месяц |
| Меры | Сумма транзакции | Written и earned premium |
| Особая dimension | Тип транзакции | Статус полиса |

### Conformed dimensions

Здесь переиспользуют dimensions транзакций. `Conformed dimension` либо идентична в разных `fact table`, либо является `shrunken dimension` — подмножеством атрибутов. Policyholder, covered item и покрытие остаются теми же. Дату заменяет conformed месяц. Из сотрудников оставляют агента: полевые отделы постоянно следят за выручкой. Вместо типа транзакции вводят dimension статуса: новые полисы и отмены в этом месяце.

### Conformed facts

Если один fact лежит в нескольких таблицах, например в снимке и в общей таблице премий и убытков, определение и подпись должны совпадать. Если определения разные, нужны разные имена.

### Pay-in-advance facts: written и earned premium

Бизнесу нужно знать, сколько премии продали за месяц (`written premium`) и сколько заработали (`earned premium`). Выручка зарабатывается месяц за месяцем, пока клиент не отменил полис.

Пример книги: годовой полис за 600 выписан 1 января.

| Месяц | Written | Earned |
|---|---|---|
| Январь | 600 | 50 |
| Февраль | 0 | 50 |
| Март, отмена 31 марта | −450 | 50 |

![Пример written и earned premium для полиса на год с отменой в марте](/assets/data-warehouse-toolkit/ch16-premium-example.png)

После отмены заработанная выручка прекращается. Точный расчёт earned premium потребовал бы воспроизвести в BI все правила учётной системы, особенно при изменении покрытия в середине месяца. Поэтому эти метрики берут из отдельной операционной системы. При оплате вперёд нужны обе таблицы: транзакции отвечают на вопросы о частоте и времени, snapshot — о заработанном доходе. Одну таблицу другой почти нельзя заменить.

> **Пояснение:** практика ниже считает earned premium упрощённо, равными долями по месяцам. В реальной системе эту сумму берут из источника.

### Supertype и subtype ещё раз

В снимке facts у разных линий несовместимы, и в одной таблице большая часть строки была бы `NULL`. Поэтому здесь, в отличие от транзакций, `fact table` делят физически: один supertype snapshot и по одному subtype snapshot на линию. Каждый subtype — копия части supertype для одной линии. Общие facts туда тоже включают, чтобы анализу внутри линии не нужны были две большие таблицы.

### Multivalued dimensions ещё раз

У автополиса несколько застрахованных водителей. Между полисом и водителем строят `bridge table`. Вес водителя — его доля в стоимости премии. Связи меняются, поэтому в bridge добавляют даты начала и конца. Получается `factless fact table` об изменении связей полиса, policyholder, объекта и водителя.

## Claims: что ещё нужно знать о бизнесе

Главные расходы страховщика — убытки по claims. Claim подаёт claimant (policyholder или новая сторона) на конкретное покрытие и объект. Типичный ход:

1. При открытии создают резерв (`reserve`) — предварительную оценку итоговой ответственности. Потом его корректируют.
2. Расследование: эксперт осматривает объект и опрашивает участников. Это поток задач.
3. Платежи: часть идёт третьим лицам (врачам, юристам, мастерским), часть claimant. Для каждого платежа нужен ответственный сотрудник.
4. Если страховщик забрал объект, остатки приносят salvage — кредит против claim.
5. Закрытие. Из-за платежей или иска claim могут открыть повторно. Как часто это случается, важно для страховщика. Время от открытия до первого платежа показывает эффективность обработки.

> **Пояснение:** `subrogation` — взыскание страховщиком выплаченной суммы с виновника ущерба.

## Обновлённая bus matrix

В матрицу добавляют строку транзакций claim. Она переиспользует dimensions полиса (дата, policyholder, покрытие, объект, employee, полис) и добавляет три новых столбца: claim, claimant и third-party payee.

## Детальная implementation bus matrix

Команды спорят, насколько детальной делать `bus matrix`. На этапе планирования авторы советуют держать крупные процессы: из каждого вырастают несколько `fact table` разного grain. На этапе реализации матрицу разворачивают: каждая `fact table` или `OLAP cube` получает свою строку и столбцы с grain и метриками. Так появляются общие, автомобильные и домашние версии транзакций и премий, а также claim workflow (один claim на строку) и участие в аварии.

## Claim transactions

Система claims порождает много задач: открытие, закрытие и повторное открытие, резерв, salvage, осмотр, иск, платежи, `subrogation`. Grain: одна задача. Схема берёт многие dimensions мира полисов, включая две роли даты с другими именами колонок. Employee — тот, кто выполнил задачу, особенно при утверждении платежей.

Новые dimensions: `claimant` (сторона, подавшая claim, обычно человек) и `third-party payee` (человек или компания). Обе обычно «грязные»: их трудно надёжно опознать между claims, а недобросовестный получатель может скрываться.

### Transaction versus profile junk dimensions

У claim много индикаторов и описаний, и соблазн свалить всё в dimension claim. Для атрибутов с высокой кардинальностью, например адреса убытка или описания события, это разумно. Но не создавайте dimension с числом строк, как у `fact table`. Коды с малой кардинальностью, например способ сообщения об убытке или признак катастрофы, лучше положить в `junk dimension` ([глава 6](/book-summaries/engineering/data-warehouse-toolkit/06-order-management/)). Здесь её называют claim profile: одна строка на уникальную комбинацию. Фильтры по ней работают быстрее, чем по атрибутам большой dimension.

## Claim accumulating snapshot

Показатели claim «на сегодня» трудно получить из всех задач с начала истории. Поэтому, например раз в день, транзакции прогоняют и инкрементально обновляют `accumulating snapshot`. Grain: одна строка на claim. Её создают при открытии и обновляют до закрытия.

| Часть | Что внутри |
|---|---|
| Dimensions | Общие conformed dimensions и статус claim (открыт, закрыт, открыт повторно). Employee, payee и тип транзакции убраны |
| Даты (семь ролей) | Потеря, открытие, оценка, первый и последний платёж, subrogation, закрытие |
| Меры | Резерв (начальный и текущий), оценка, выплачено, salvage, subrogation, число транзакций |
| Lags | Потеря → открытие, открытие → оценка, → первый платёж, → subrogation, → закрытие |

Lag — разница между двумя датами. Её можно считать и только по рабочим дням.

### Accumulating snapshot для сложных workflow

Такая таблица подходит для процесса с пятью–десятью вехами. Иногда вех много, и они нестабильны: начало и конец есть всегда, а середина идёт без порядка. Авторы советуют:

- Оставить FK на `role-playing dimension` только для главных вех: начала, конца и частых важных событий. По ним фильтруют.
- Для остальных хранить lags, а не даты: пользователям нужны именно они.
- Хранить lags от вехи A, через которую проходит каждый процесс. При 20 вехах возможно 190 lags, а хранить нужно 19.
- Остальные считать: B → C = (A → C) − (A → B). Если одной вехи не было, результат `NULL`. Для подсчёта и среднего это не проблема.

### Timespan accumulating snapshot

Accumulating snapshot показывает текущее состояние, но стирает промежуточные. Claim может быть открыт, отклонён, закрыт, открыт снова. Таблица транзакций хранит каждое событие, но не накапливает метрики. Классический snapshot не показывает claim на дату в прошлом.

Решение: вместо обновления вставлять новую строку на отрезок времени. Как в `SCD` type 2, добавляют колонки snapshot start date, snapshot end date и snapshot current flag. Большинству нужен текущий вид: для него делают view с фильтром по current flag. Остальные фильтруют по start и end. Поддерживать такую таблицу сложнее: у прежней текущей строки обновляют служебные колонки и вставляют новую.

### Periodic snapshot вместо accumulating

Для долгих claims, например по длительной нетрудоспособности, лучше `periodic snapshot`. Grain: одна строка на активный claim за период, например за месяц. Facts — аддитивные суммы за период: заявлено, выплачено, изменение резерва.

## Consolidated periodic snapshot: полис и claim

Бизнесу нужна прибыль: премии и убытки вместе. Их можно получить запросом к двум таблицам и объединением результатов (`drill across`). Но ради удобства и скорости авторы строят отдельную `fact table`, как в [главе 7](/book-summaries/engineering/data-warehouse-toolkit/07-accounting/). Она consolidated, потому что объединяет несколько бизнес-процессов.

У неё меньше dimensions: только общий для обоих процессов уровень. Это месяц, policyholder, покрытие, объект, агент, статус полиса и статус claim. Facts: written и earned premium, выплаты по claims и полученные по claims суммы. Авторы советуют строить её после того, как базовые метрики доставлены в отдельных атомарных моделях.

> **Пояснение:** убыточность (loss ratio) — выплаты по claims, делённые на earned premium. Практика ниже считает её через общий уровень policy.

## Factless fact table: аварии

`Factless fact table` — пересечение ключей в точке пространства и времени (см. [главу 3](/book-summaries/engineering/data-warehouse-toolkit/03-retail-sales/)). У автостраховщика так записывают буквальные столкновения: связи многие-ко-многим между людьми и машинами в аварии.

Новые dimensions: loss party (участник аварии) и loss party role (пассажир, свидетель, юрист). Как в главе 3, добавляют fact, равный 1, чтобы считать. Участников и ролей может быть сколько угодно. Если у аварии несколько claimant или loss party, их можно сделать многозначными dimensions через bridge-таблицы групп. Тогда grain остаётся: одна запись на claim. Так можно ответить, например, на вопрос: сколько claims о телесных повреждениях вели, где claimant представляла юридическая фирма X, а ремонт делала мастерская Y?

## Десять ошибок dimensional modeling

В конце авторы перечисляют, чего делать нельзя. Ошибки идут в обратном порядке важности, но и менее важные могут серьёзно навредить DW/BI-системе.

### Ошибка 10: текст в fact table

Числовые измерения идут в `fact table`, описательный текст — в dimensions. Атрибут для фильтров и группировки почти всегда принадлежит dimension. Остальные коды решают по полю: нужен в расчётах — fact, нужен для фильтров и подписей — dimension. Настоящий текст, особенно комментарии, в `fact table` не оставляют.

### Ошибка 9: короткие описания ради экономии места

Dimensions почти всегда на порядки меньше `fact table`: dimension товара на 100 МБ ничтожна, если fact table больше в сто или тысячу раз. Добавьте к каждому коду понятный текст: он нужен для фильтров и заголовков отчётов.

### Ошибка 8: иерархия разбита на несколько dimensions

Иерархия — цепочка связей many-to-one: товары в бренде, бренды в категории. Если dimension на самом низком grain, верхние уровни лежат в строке как атрибуты. Иерархию фиксированной глубины держат в одной плоской dimension, без `snowflake` из всё меньших подтаблиц.

### Ошибка 7: не отслеживать изменения dimensions

Пользователи часто хотят видеть влияние изменений хотя бы части атрибутов. Не полагайтесь только на type 1. Быстро меняющуюся группу атрибутов вынесите в `mini-dimension`.

### Ошибка 6: решать все проблемы скорости железом

Агрегаты, то есть производные сводные таблицы, — экономичный способ ускорить запросы. Железо добавляйте как часть программы: агрегаты, партиционирование, индексы, быстрая СУБД.

### Ошибка 5: operational keys для join dimensions и facts

Нельзя делать ключом dimension набор атрибутов или operational key с датой действия: со временем это даст проблемы. Замените его простым целым `surrogate key` от 1 до N. Единственное исключение — dimension даты.

### Ошибка 4: не объявить grain и не соблюдать его

Сначала бизнес-процесс, потом точный grain, затем dimensions, которые ему соответствуют. Серьёзная ошибка — добавить «удобные» facts: итоги за больший период или регион. Суммы посчитают их несколько раз. Каждому grain нужна своя `fact table`.

### Ошибка 3: проектировать модель по отчёту

Dimensional model описывает процесс измерения, а не будущий отчёт. Авторы приводят случай: команда построила сотни fact tables для заказов, каждую под свой отчёт. Данные извлекали много раз, и команда не успевала обновлять базы за ночь. Нужна была одна схема атомарных данных и несколько агрегатов.

### Ошибка 2: ждать, что пользователи будут читать нормализованные данные

Данные нижнего уровня самые «размерные», на них строят модель. Агрегаты теряют часть dimensions. Нормализованная модель в `3NF` полезна для подготовки данных в ETL, но не для показа пользователям.

### Ошибка 1: не согласовать facts и dimensions

Авторы шутят, что здесь две ошибки в одной: номера кончились. Если fact, например выручка, есть в нескольких базах, определения должны совпадать точно. Иначе не называйте их одним словом.

Согласование dimensions — самая важная техника. Если несколько `fact table` используют одну dimension, она должна быть идентичной или подмножеством другой. Тогда работает `drill across` между источниками: фильтры и заголовки значат одно и то же. Это основа распределённых DW/BI-сред и подключения новых источников.

## Итоги главы

- Страховой кейс повторяет почти все техники книги.
- Транзакции полиса нельзя складывать в выручку: клиент платит заранее, а компания зарабатывает по месяцам.
- Поэтому нужны две таблицы: transaction `fact table` для событий и premium snapshot для written и earned premium.
- Earned premium считают по сложным правилам, поэтому его берут из операционной системы, а не пересчитывают в BI.
- Для claims строят transaction `fact table` и `accumulating snapshot` с датами вех и lags.
- Для сложных процессов lags хранят от одной вехи, для истории состояний есть timespan-вариант, для долгих claims — `periodic snapshot`.
- Consolidated `fact table` объединяет премии и убытки и строится после базовых моделей.
- Самая опасная из десяти ошибок — не согласовать facts и dimensions.

## Ключевые термины

| Термин | Значение |
|---|---|
| Coverage, covered item | Покрытие (продукт страховщика) и застрахованный объект |
| Written premium | Проданная премия за период |
| Earned premium | Заработанная премия: покрытие действовало |
| Reserve | Предварительная оценка итоговой ответственности по claim |
| Salvage, subrogation | Возврат денег по claim: остатки имущества, взыскание с виновника |
| Claim profile | `Junk dimension` с кодами claim малой кардинальности |
| Lag | Время между двумя вехами процесса |

## Что это значит на практике

- Для бизнеса с оплатой вперёд делайте transaction и snapshot. Это верно и для подписок, и для гарантий.
- Не складывайте транзакции в выручку в отчёте. Берите готовый earned premium из системы учёта.
- Держите `policyholder_id` рядом с `surrogate key`, чтобы видеть клиента через все версии `SCD` type 2.
- Убыточность считайте после агрегации обеих таблиц до общего уровня, например policy. Прямой join двух `fact table` размножает строки.
- Для claim с десятками вех храните lags от первой вехи, остальные считайте во view и учитывайте `NULL`.
- Коды claim с малой кардинальностью собирайте в одну `junk dimension`, а свободный текст держите вне `fact table`.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Суммы в условных единицах. Блоки ниже идут по порядку.

### Шаг 1. Создаём схему

```sql
CREATE TABLE dim_date AS
SELECT 0 AS date_key, NULL::DATE AS full_date, NULL::INT AS month_key
UNION ALL
SELECT strftime(d, '%Y%m%d')::INT, d::DATE, strftime(d, '%Y%m')::INT
FROM generate_series(DATE '2025-01-01', DATE '2025-12-31', INTERVAL 1 DAY) t(d);

CREATE TABLE dim_month AS
SELECT strftime(m, '%Y%m')::INT AS month_key,
       m::DATE AS month_start,
       (m + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE AS month_end,
       monthname(m) AS month_name
FROM generate_series(DATE '2025-01-01', DATE '2025-06-01', INTERVAL 1 MONTH) t(m);

-- SCD type 2: у Анны сменился ZIP-код 1 марта
CREATE TABLE dim_policyholder AS
SELECT * FROM (VALUES
    (1, 'H1', 'Анна',  '101000', DATE '2024-01-01', DATE '2025-02-28'),
    (2, 'H1', 'Анна',  '420000', DATE '2025-03-01', DATE '9999-12-31'),
    (3, 'H2', 'Борис', '190000', DATE '2024-01-01', DATE '9999-12-31'),
    (4, 'H3', 'Вера',  '630000', DATE '2024-01-01', DATE '9999-12-31')
) t(policyholder_key, policyholder_id, policyholder_name, zip_code, valid_from, valid_to);

CREATE TABLE dim_coverage AS
SELECT * FROM (VALUES
    (1, 'Auto liability', 'Auto'),
    (2, 'Home fire',      'Home'),
    (3, 'Auto collision', 'Auto'),
    (4, 'Home theft',     'Home')
) t(coverage_key, coverage_name, line_of_business);

CREATE TABLE dim_covered_item AS
SELECT * FROM (VALUES
    (1, 'Toyota Camry 2020'),
    (2, 'Дом, Казань'),
    (3, 'Mazda 3 2022'),
    (4, 'Квартира, Казань')
) t(covered_item_key, item_description);

CREATE TABLE dim_transaction_type AS
SELECT * FROM (VALUES (1, 'New business'), (2, 'Endorsement'), (3, 'Cancellation')) t(txn_type_key, txn_type);

-- полисы: каждый на 12 месяцев от начала
CREATE TABLE stg_policy AS
SELECT * FROM (VALUES
    ('P-100', 'H1', 1, 1, DATE '2025-01-01'),
    ('P-101', 'H2', 2, 2, DATE '2025-02-01'),
    ('P-102', 'H3', 3, 3, DATE '2025-01-15'),
    ('P-103', 'H1', 4, 4, DATE '2025-03-10')
) t(policy_number, holder_id, coverage_key, covered_item_key, term_start);

-- транзакции: дата записи, дата вступления в силу, сумма
CREATE TABLE stg_policy_txn AS
SELECT * FROM (VALUES
    (1, 'P-100', 1, DATE '2025-01-01', DATE '2025-01-01',  600),
    (2, 'P-100', 3, DATE '2025-03-31', DATE '2025-03-31', -450),
    (3, 'P-101', 1, DATE '2025-02-01', DATE '2025-02-01', 1200),
    (4, 'P-101', 2, DATE '2025-04-05', DATE '2025-04-01',  100),
    (5, 'P-102', 1, DATE '2025-01-15', DATE '2025-01-15',  480),
    (6, 'P-103', 1, DATE '2025-03-10', DATE '2025-03-10',  360)
) t(txn_id, policy_number, txn_type_key, txn_date, effective_date, amount);

-- grain: одна транзакция полиса. Две роли даты
CREATE TABLE fact_policy_transaction AS
SELECT
    t.txn_id,
    dt.date_key AS transaction_date_key,
    de.date_key AS effective_date_key,
    h.policyholder_key,
    p.coverage_key,
    p.covered_item_key,
    t.txn_type_key,
    t.policy_number,
    t.amount AS policy_transaction_amount
FROM stg_policy_txn t
JOIN stg_policy p USING (policy_number)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND t.txn_date BETWEEN h.valid_from AND h.valid_to
JOIN dim_date dt ON dt.full_date = t.txn_date
JOIN dim_date de ON de.full_date = t.effective_date;

-- grain: полис x покрытие x объект x месяц
-- earned: сумма транзакции делится поровну на месяцы от даты вступления до конца срока
CREATE TABLE fact_premium_snapshot AS
WITH spread AS (
    SELECT t.txn_id, t.policy_number, t.amount,
           date_trunc('month', t.effective_date + INTERVAL 1 DAY)::DATE   AS from_month,
           (date_trunc('month', p.term_start) + INTERVAL 11 MONTH)::DATE  AS to_month
    FROM stg_policy_txn t
    JOIN stg_policy p USING (policy_number)
), earned AS (
    SELECT s.policy_number, m.month_key,
           sum(s.amount / (date_diff('month', s.from_month, s.to_month) + 1)) AS earned_premium
    FROM spread s
    JOIN dim_month m ON m.month_start BETWEEN s.from_month AND s.to_month
    GROUP BY ALL
), written AS (
    SELECT t.policy_number, d.month_key, sum(t.amount) AS written_premium
    FROM stg_policy_txn t
    JOIN dim_date d ON d.full_date = t.txn_date
    GROUP BY ALL
)
SELECT
    p.policy_number,
    m.month_key,
    h.policyholder_key,
    p.coverage_key,
    p.covered_item_key,
    CASE WHEN EXISTS (SELECT 1 FROM stg_policy_txn c
                      WHERE c.policy_number = p.policy_number AND c.txn_type_key = 3
                        AND c.effective_date <= m.month_end)
         THEN 'Cancelled' ELSE 'In force' END AS policy_status,
    coalesce(w.written_premium, 0)          AS written_premium,
    round(coalesce(e.earned_premium, 0), 2) AS earned_premium
FROM stg_policy p
JOIN dim_month m ON m.month_start >= date_trunc('month', p.term_start)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND m.month_end BETWEEN h.valid_from AND h.valid_to
LEFT JOIN earned  e ON e.policy_number = p.policy_number AND e.month_key = m.month_key
LEFT JOIN written w ON w.policy_number = p.policy_number AND w.month_key = m.month_key;

-- claims: дата потери и поток транзакций
CREATE TABLE stg_claim AS
SELECT * FROM (VALUES
    ('C1', 'P-100', DATE '2025-02-10'),
    ('C2', 'P-101', DATE '2025-04-12'),
    ('C3', 'P-102', DATE '2025-05-02'),
    ('C4', 'P-103', DATE '2025-05-20')
) t(claim_id, policy_number, loss_date);

CREATE TABLE stg_claim_txn AS
SELECT * FROM (VALUES
    ('C1', DATE '2025-02-11', 'open',    0),
    ('C1', DATE '2025-02-11', 'reserve', 300),
    ('C1', DATE '2025-03-01', 'payment', 100),
    ('C1', DATE '2025-03-20', 'payment', 120),
    ('C1', DATE '2025-04-02', 'close',   0),
    ('C2', DATE '2025-04-13', 'open',    0),
    ('C2', DATE '2025-04-13', 'reserve', 2000),
    ('C2', DATE '2025-05-10', 'payment', 400),
    ('C2', DATE '2025-05-20', 'salvage', 50),
    ('C3', DATE '2025-05-03', 'open',    0),
    ('C3', DATE '2025-05-03', 'reserve', 200),
    ('C3', DATE '2025-05-15', 'payment', 190),
    ('C3', DATE '2025-05-20', 'close',   0),
    ('C4', DATE '2025-05-21', 'open',    0),
    ('C4', DATE '2025-05-21', 'reserve', 100)
) t(claim_id, txn_date, txn_type, amount);

-- accumulating snapshot: одна строка на claim, строка обновляется при новых событиях
CREATE TABLE fact_claim AS
SELECT
    c.claim_id,
    c.policy_number,
    p.coverage_key,
    p.covered_item_key,
    h.policyholder_key,
    c.loss_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'open')    AS open_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'payment') AS first_payment_date,
    max(t.txn_date) FILTER (WHERE t.txn_type = 'payment') AS last_payment_date,
    min(t.txn_date) FILTER (WHERE t.txn_type = 'close')   AS closed_date,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'reserve'), 0) AS original_reserve,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'payment'), 0) AS paid_to_date,
    coalesce(sum(t.amount) FILTER (WHERE t.txn_type = 'salvage'), 0) AS salvage_collected,
    count(*) AS transaction_count,
    CASE WHEN min(t.txn_date) FILTER (WHERE t.txn_type = 'close') IS NULL THEN 'Open' ELSE 'Closed' END AS claim_status
FROM stg_claim c
JOIN stg_policy p USING (policy_number)
JOIN dim_policyholder h ON h.policyholder_id = p.holder_id AND c.loss_date BETWEEN h.valid_from AND h.valid_to
JOIN stg_claim_txn t USING (claim_id)
GROUP BY ALL;
```

### Шаг 2. Проверяем

```sql
-- у P-100 за три месяца written и earned равны: 150 = 150
SELECT policy_number, sum(written_premium) AS written, sum(earned_premium) AS earned
FROM fact_premium_snapshot
WHERE policy_number = 'P-100'
GROUP BY policy_number;

-- 4 claim. Сумма transaction_count равна 15 строкам источника
SELECT count(*) AS claims, sum(transaction_count) AS source_rows FROM fact_claim;
```

### Задания

**1.** Written и earned по месяцам. Покажите оба показателя для всех полисов. Почему они разные в марте и апреле?

<details>
<summary>Решение</summary>

```sql
SELECT m.month_name,
       sum(s.written_premium) AS written,
       sum(s.earned_premium)  AS earned
FROM fact_premium_snapshot s
JOIN dim_month m USING (month_key)
GROUP BY m.month_key, m.month_name
ORDER BY m.month_key;
```

- Март: written = -90. Это отмена P-100 (-450) плюс новый P-103 (+360). Earned растёт до 220: P-100 действовал весь март, а P-103 добавил 30.
- Апрель: written = 100. Это изменение полиса P-101 (endorsement). Earned падает до 180: P-100 больше не зарабатывает (-50), а endorsement добавил +10.

Written показывает продажи в месяце. Earned показывает, сколько покрытия реально действовало.
</details>

**2.** Earned по линиям бизнеса. Покажите earned premium по месяцам для Auto и Home. Транзакции этого не дают: нужно распределение по времени.

<details>
<summary>Решение</summary>

```sql
SELECT m.month_name, c.line_of_business, sum(s.earned_premium) AS earned
FROM fact_premium_snapshot s
JOIN dim_month m USING (month_key)
JOIN dim_coverage c USING (coverage_key)
GROUP BY m.month_key, m.month_name, c.line_of_business
ORDER BY m.month_key, c.line_of_business;
```
</details>

**3.** SCD type 2. Покажите earned premium по ZIP-коду policyholder. Полис P-100 должен делиться между двумя ZIP: старый до февраля, новый с марта. Затем сверьте итог с суммой по всем полисам.

<details>
<summary>Решение</summary>

```sql
SELECT h.zip_code, h.policyholder_name,
       sum(s.earned_premium) AS earned
FROM fact_premium_snapshot s
JOIN dim_policyholder h USING (policyholder_key)
GROUP BY h.zip_code, h.policyholder_name
ORDER BY h.policyholder_name, h.zip_code;

SELECT sum(earned_premium) AS total_earned FROM fact_premium_snapshot;
```

Итого earned равно 1 040. Анна появляется в двух строках: 101000 за январь и февраль, 420000 с марта.
</details>

**4.** Claim как accumulating snapshot. Посчитайте lag от потери до открытия, от открытия до первого платежа и до закрытия в днях. Найдите открытые claims, где ещё не было платежей, на 2025-06-30.

<details>
<summary>Решение</summary>

```sql
SELECT claim_id, claim_status,
       date_diff('day', loss_date, open_date)           AS loss_to_open,
       date_diff('day', open_date, first_payment_date)  AS open_to_first_payment,
       date_diff('day', open_date, closed_date)         AS open_to_closed,
       paid_to_date
FROM fact_claim
ORDER BY claim_id;

-- открыты и нет платежей
SELECT claim_id, original_reserve,
       date_diff('day', open_date, DATE '2025-06-30') AS days_open
FROM fact_claim
WHERE claim_status = 'Open' AND first_payment_date IS NULL;
```

Claim C4 открыт 40 дней без платежей. У открытых claim lag закрытия равен `NULL`. Это нормально: события ещё не было.
</details>

**5.** Убыточность. Посчитайте loss ratio по линиям бизнеса: выплаты по claims делённые на earned premium. Сначала агрегируйте каждую таблицу до policy, потом соединяйте. Попробуйте и неправильный вариант: прямой join двух fact-таблиц.

<details>
<summary>Решение</summary>

```sql
-- правильно: drill across через общий уровень (policy)
WITH premium AS (
    SELECT policy_number, coverage_key, sum(earned_premium) AS earned
    FROM fact_premium_snapshot
    GROUP BY ALL
), claims AS (
    SELECT policy_number, sum(paid_to_date) AS paid
    FROM fact_claim
    GROUP BY policy_number
)
SELECT c.line_of_business,
       sum(p.earned)                       AS earned_premium,
       coalesce(sum(cl.paid), 0)           AS paid_claims,
       round(coalesce(sum(cl.paid), 0) / sum(p.earned), 2) AS loss_ratio
FROM premium p
JOIN dim_coverage c USING (coverage_key)
LEFT JOIN claims cl USING (policy_number)
GROUP BY c.line_of_business
ORDER BY c.line_of_business;

-- неправильно: прямой join строк snapshot и claim. Выплаты считаются много раз
SELECT sum(cl.paid_to_date) AS paid_wrong
FROM fact_premium_snapshot s
JOIN fact_claim cl USING (policy_number);
```

Правильные выплаты равны 810. Неправильный join размножает claim на число месяцев полиса, и сумма сильно больше.
</details>

## Вопросы для самопроверки

1. Почему для страхования нужны и transaction fact, и monthly snapshot? Почему одну таблицу нельзя заменить другой?
2. Чем written premium отличается от earned premium? Приведите пример с отменой полиса.
3. Как SCD type 2 для ZIP-кода влияет на отчёт по snapshot?
4. Когда для линий бизнеса хватает subtype-dimensions и view, а когда нужны отдельные subtype fact tables?
5. Почему при 20 вехах процесса хранят 19 lags, а не 190? Как получить lag между вехами B и C?
6. Почему consolidated fact table строят после базовых моделей и как считать убыточность без прямого join двух fact tables?

Предыдущая: [Глава 15. Электронная коммерция](/book-summaries/engineering/data-warehouse-toolkit/15-electronic-commerce/). Следующая: [Глава 17. Kimball Lifecycle](/book-summaries/engineering/data-warehouse-toolkit/17-lifecycle-overview/).
