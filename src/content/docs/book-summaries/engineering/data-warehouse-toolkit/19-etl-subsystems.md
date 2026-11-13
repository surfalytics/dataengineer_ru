---
title: "The Data Warehouse Toolkit, глава 19: ETL subsystems"
head:
  - tag: title
    content: "ETL: 34 подсистемы по Kimball, CDC, SCD, качество | Инжиниринг Данных"
description: "Конспект главы 19 The Data Warehouse Toolkit. 34 подсистемы ETL по группам. Практика в DuckDB: dedup, SCD2, inferred member, data quality."
sidebar:
  order: 19
  label: "19. ETL subsystems"
tags:
  - books
  - data-modeling
  - kimball
  - sql
---

**Главная мысль:** ETL съедает непропорционально много сил в проекте хранилища, а ответ «это зависит» ведёт к хаосу из скриптов и расписаний. Опыт тысяч проектов показывает, что почти в каждом хранилище нужны 34 подсистемы в четырёх группах: extract (3), clean и conform (5), deliver (13) и manage (13).

## О чём глава

[Глава 18](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/) закончила дизайн модели. Эта глава показывает, из чего состоит система, которая наполняет модель данными: `ETL` (extract, transform, load — забрать данные из источника, изменить и загрузить в таблицы для пользователей). Как строить эти подсистемы по шагам, покажет [глава 20](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/).

- Требования, которые собирают до дизайна.
- Extract (3): profiling, CDC, extract.
- Clean и conform (5), включая error event schema.
- Deliver (13): SCD, surrogate keys, загрузка facts, late arriving data.
- Manage (13): расписание, restart, мониторинг, compliance.

![34 подсистемы ETL по четырём группам: extract, clean и conform, deliver, manage](/assets/data-warehouse-toolkit/ch19-etl-subsystems.png)

Читайте схему сверху вниз: данные идут от источников через extract, clean и conform, deliver в presentation area, а группа manage (22–34) обслуживает все три шага.

## Сначала соберите требования

Архитектуру ETL начинают со сбора требований. Это в основном ограничения, под которые нужно подстроить систему. Книга советует коротко ответить по каждой из десяти областей, потому что любая из них может остановить проект.

### Business needs

Требования бизнеса определяют источники и преобразования. Ведите список KPI, которые проект обещает поддержать, и целей для drill-down и `drill across` (переход между бизнес-процессами по общим dimensions). Они нужны на вопрос «почему KPI изменился».

### Compliance и security

Нужно доказать, что отчёты точны, полны и не подделаны. Для этого перечислите данные под compliance и шаги, где нужна `chain of custody` (доказательство, что отчёт получен из исходных данных). Security спорит с идеей хранилища: оно публикует данные широко, а безопасность ограничивает доступ. Защита нужна и носителям backup.

### Data quality

Качество волнует руководство: источники разбросаны по миру, а compliance не прощает небрежность. Составьте список полей с известным плохим качеством и отметьте, договорились ли с источником их исправить.

### Data integration

Интеграция в хранилище — это `conformed dimensions` (общие атрибуты в разных базах, чтобы работал drill across) и `conformed facts` (согласованные метрики, которые можно сравнивать). Приоритеты для conformed dimensions книга советует брать из bus matrix.

### Data latency

Параллелизм и мощное железо ускоряют batch. Но при жёстком требовании ETL нужно перевести на `microbatch` (частые маленькие пакеты) или streaming. Это не плавный шаг, а смена парадигмы: почти каждый этап нужно переписать.

### Archiving и lineage

Книга советует делать `staging` (запись данных на диск) после extract, после clean и conform и после deliver. Консервативное правило авторов: архивируйте всё, если вы не решили сознательно, что набор данных не понадобится. Читать архив проще, чем гнать данные через ETL заново. К каждому набору нужны метаданные о происхождении: это `lineage`.

### BI delivery interfaces

Авторы жёстко требуют: команда ETL отвечает за то, чтобы данные делали BI простым и быстрым. Самая серьёзная ошибка — отдать BI нормализованную модель и уйти. Согласуйте с разработчиками BI, какие таблицы, кубы, индексы и агрегаты им нужны.

### Available skills и legacy licenses

Не стройте систему на навыках, которых нет в команде. Это касается и выбора между ручным кодом и ETL tool. Руководство часто требует использовать уже купленные лицензии. Обычно с этим можно жить, но иногда это ошибка.

## 34 подсистемы ETL

У ETL четыре части.

| Группа | Подсистемы | Задача |
|---|---|---|
| Extracting | 1–3 | Забрать сырые данные и записать на диск |
| Cleaning and conforming | 4–8 | Улучшить качество, объединить источники |
| Delivering | 9–21 | Загрузить данные в dimensional models |
| Managing | 22–34 | Управлять средой ETL |

## Extract: подсистемы 1–3

Первые подсистемы работают с источниками: понять данные, забрать их и перенести в среду ETL.

### Подсистема 1. Data profiling

`Data profiling` — анализ содержимого, согласованности и структуры данных. У профилирования две роли. Strategic: лёгкая оценка сразу после выбора источника, чтобы рано решить «брать или нет». Поздний отказ через месяцы может сорвать проект. Tactical: долгий поиск проблем. Находки идут владельцу источника или становятся требованиями к quality screens. Авторы призывают делать профилирование в самом начале.

### Подсистема 2. Change data capture

`CDC` (change data capture) выделяет только те данные, которые изменились с прошлой загрузки. Многие таблицы слишком большие, чтобы обновлять их целиком в каждом цикле. Хороший CDC ловит insert, update и delete и работает как можно раньше. Способ выбирают для каждого источника.

| Способ | Что важно знать |
|---|---|
| Audit columns | Колонки с датой изменения. Если скрипты DBA меняют данные в обход этих колонок, изменения теряются. Delete они тоже могут не показать |
| Timed extract | Выбор строк «за вчера». Книга считает его крайне ненадёжным: при перезапуске появятся дубли, а пропущенный день может потеряться |
| Full diff compare | Построчное сравнение со вчерашним снимком. Находит всё, но дорого. Контрольная сумма строки (CRC) ускоряет поиск изменений |
| Log scraping | Чтение журнала БД. Самый грязный способ: журнал могут очистить вместе с транзакциями |
| Message queue | Чтение очереди. Мало нагрузки, но replay может не быть, и при обрыве данные теряются |

### Подсистема 3. Extract system

Источники бывают разные: mainframe, реляционные БД, файлы, XML, web logs, ERP. Если язык старой системы вам недоступен, попросите владельца выгрузить плоский файл.

Данные забирают потоком или файлом. Поток привлекательнее, но у файла есть плюсы. Его проще перезапустить, можно перегрузить без нагрузки на источник, сжать и зашифровать. Число строк до и после переноса легко сверить. Сжимайте до шифрования: зашифрованные файлы плохо сжимаются.

## Clean и conform: подсистемы 4–8

Здесь ETL добавляет данным ценность: extract и delivery только переносят данные, а эти подсистемы их меняют.

### Культура качества данных

Технические ограничения ввода часто обходят проблему. Пример из книги: номер соцстрахования ввели с обязательным форматом, и операторы без настоящего номера стали вписывать выдуманный. Майкл Хаммер заметил, что мелкие проблемы качества показывают сломанные бизнес-процессы. Значит, чинить надо процесс, а культура качества должна идти сверху. Книга даёт шаблон из девяти шагов. Среди них: обязательство руководства, реинжиниринг процессов, деньги на ввод данных и интеграцию, публичное признание и постоянное измерение качества.

### Подсистема 4. Data cleansing system

От ETL ждут двух вещей: исправлять грязные данные и показывать их такими, какими их записала операционная система. Нужен баланс. Новичкам авторы советуют начать с data profiling: он покажет нужную сложность очистки.

#### Quality screens

Основа — `quality screens`: тесты в потоке данных. Если тест пройден, ничего не происходит. Если нет, screen пишет событие в error event schema и выбирает реакцию. По Jack Olson, screens бывают трёх типов:

- **Column:** одна колонка. Например, неожиданный `NULL`, значение вне диапазона, неверный формат.
- **Structure:** связи между колонками. Например, иерархии, foreign key или целый блок колонок вроде адреса.
- **Business rule:** сложные правила. Например, пассажир уровня lifetime platinum должен быть участником не менее пяти лет и налетать более 2 млн миль. Сюда же относятся пороги по агрегатам, например слишком много МРТ при лёгких диагнозах.

#### Реакция на события качества

Реакций три: остановить процесс, отправить записи в `suspense file` (отложить на потом) или пометить данные и передать дальше. Остановка требует ручного разбора. Для suspense неясно, когда записи исправят, а пока их нет, данные неполны. Авторы называют третий вариант лучшим, когда он возможен. Плохие строки fact помечают через audit dimension. Плохие строки dimension помечают так же или значением ошибки прямо в атрибуте.

### Подсистема 5. Error event schema

`Error event schema` — центральная dimensional schema для всех событий от screens. Главная таблица, error event fact, имеет `grain` «одна ошибка от одного screen». Её dimensions: дата, batch (при потоке — шаг обработки) и screen с описанием проверки и действия при ошибке. Вторая таблица, error event detail fact, имеет grain ниже: одно поле в одной записи, участвовавшее в ошибке. Сложная ошибка даёт одну строку наверху и много строк внизу.

### Подсистема 6. Audit dimension assembler

`Audit dimension` ETL собирает для каждой fact-таблицы (глава 6). Она хранит метаданные на момент создания строки: оценку качества, флаги (полнота, валидация, выход за границы, сбой screen, запись изменена) и номера версий ETL. При идеальной загрузке за день будет одна строка audit dimension на все строки fact. Если у части строк скидка вышла за границы, добавляется ещё одна строка с этим флагом.

### Подсистема 7. Deduplication system

Dimension часто собирают из нескольких источников, например из клиентских систем разных подразделений. Универсального ключа обычно нет, и иногда совпадение ищут по сходству имён и адресов. Остальные колонки совпавших записей могут противоречить друг другу. `Survivorship` — сборка из совпавших записей одной строки с лучшими значениями колонок. Для неё нужны правила приоритета источников. Храните и natural keys всех источников.

### Подсистема 8. Conforming system

Conforming приводит колонки dimension к колонкам похожих dimensions в других частях хранилища. Например, счета и обращения в поддержку используют customer, но хранят клиентов в разных базах. Результат — conformed dimension с номером версии и ссылками на natural keys всех источников. Книга связывает это с agile-подходом: dimensions conformed, если у них есть хотя бы один общий атрибут (например, `Customer Category`), а список таких атрибутов можно наращивать постепенно. Публикуют их подсистемы 17 и 18.

## Deliver: подсистемы 9–21

Главная задача ETL — передать готовые dimension и fact таблицы, поэтому delivery — самые важные подсистемы. Для многих dimensions план простой: назначить `surrogate key`, подставить описания кодов, сджойнить нормализованные (`3NF`) таблицы в плоскую dimension. Facts большие, но готовить их проще.

### Подсистема 9. Slowly changing dimension manager

Когда атрибут изменился, SCD manager решает, что делать (типы `SCD` — в главе 5), и ведёт служебные колонки type 2. Изменения ему даёт CDC.

| Тип | Что делает ETL |
|---|---|
| 1 | Перезаписывает атрибут. Если есть type 2, колонку меняют во всех версиях. Агрегаты нужно пересобрать |
| 2 | Копирует строку с новым surrogate key и меняет колонки. Обновляет таблицу соответствия ключей для загрузки facts. Агрегаты не ломаются, если изменение сделано не задним числом |
| 3 | Добавляет колонку для старого значения, например при смене региона. Агрегаты нужно пересобрать |
| 4 | Выносит быстро меняющиеся атрибуты в `mini-dimension`; в fact есть оба ключа |
| 5 | Type 4 плюс type 1 ссылка на mini-dimension в основной dimension, её перезаписывают при смене статуса |
| 6 | В строке type 2 есть ещё и текущее значение атрибута, его перезаписывают |
| 7 | Type 2 dimension плюс fact с двумя ключами: обычным и `durable key` (постоянный ключ объекта). Нужен признак текущей строки |

Для type 2 нужны даты начала и конца версии. Расширенный вариант добавляет пять служебных колонок, включая причину изменения и current flag. У текущей строки конец ставят на 31.12.9999. Даты версий берите из системной даты загрузки, а не из `last_modified` источника: скрипты могут менять данные и не обновлять это поле. Не используйте «UPDATE else INSERT» на больших объёмах. Разделяйте UPDATE существующих строк и INSERT новых.

> **Пояснение:** дальняя дата вместо `NULL` позволяет искать версию условием `BETWEEN row_start AND row_end`.

### Подсистема 10. Surrogate key generator

Книга рекомендует surrogate keys для всех dimensions (глава 3). Генератор должен работать отдельно для каждой dimension и не зависеть от экземпляра БД. Триггеры БД для ключей могут стать узким местом. Не склеивайте ключ источника с датой: это не масштабируется.

### Подсистема 11. Hierarchy manager

Иерархии лежат в dimension как обычные атрибуты, и каждый должен быть однозначным при данном primary key. `Fixed depth` (постоянное число уровней, в том числе слегка неровные, как адрес) хранят отдельными атрибутами. `Ragged` (неровные, например оргструктура) требуют `bridge table`. Snowflake в presentation не рекомендуются.

### Подсистема 12. Special dimensions manager

Это подсистема «на всё остальное» для особенностей дизайна.

| Тип | Что делает ETL |
|---|---|
| Date/time | Нет обычного источника. Строят в начале проекта, обычно за полдня в таблице |
| Junk | Флаги и тексты, оставшиеся в fact. Комбинации создают заранее или на лету при загрузке facts |
| Mini-dimensions | Для больших dimensions, где type 2 не подходит. Строят как junk, но из dimension. Часто нужно несколько |
| Shrunken | Conformed подмножество базовой dimension. Строят из базовой, а ключ генерируют независимо |
| Small static | Маленькие справочники «код — слова». ETL создаёт их сразу в финальном виде |
| User maintained | Справочники бизнеса без системы-источника. Владельцем должен стать бизнес-отдел, а не ETL-команда. Новым строкам ставят заглушку вроде `Not Yet Assigned 157` (фраза и surrogate key), чтобы пустые значения не слиплись |

### Подсистема 13. Fact table builders

Для facts главное — ссылочная целостность с dimensions (подсистема 14). Три типа fact-таблиц грузятся по-разному.

#### Transaction fact table loader

`Transaction fact table` описывает событие в один момент: строку счёта, скан на кассе. Это самые большие таблицы. Новые строки грузят bulk-загрузкой в таблицу, партиционированную по времени. Исправление существующих строк делают в два шага: вставить исправленные строки, потом удалить старые. Это возможно, если у fact есть одноколоночный surrogate key.

#### Periodic snapshot fact table loader

`Periodic snapshot` — регулярный срез, например месячная выписка по счёту. Грузится похоже на transaction fact, традиционно в конце периода. Чаще делают `hot rolling periodic snapshot`: кроме итоговых строк месяца в таблице лежат строки с балансами на вчера, и их обновляют каждый день. Это трудно, если расчёт итогов сложный.

#### Accumulating snapshot fact table loader

`Accumulating snapshot` показывает состояние процесса с началом и концом, например заказа. В строке несколько дат этапов. Строку создают с первой датой и перезаписывают ключи дат и метрики по мере событий. Таблица показывает только последнее состояние, поэтому часто используют все три типа вместе. Процессы с циклами для неё не подходят.

### Подсистема 14. Surrogate key pipeline

Каждый ETL заменяет natural keys в fact на surrogate keys. Без строки в dimension продажа выглядит как продажа несуществующего продукта, а запрос может молча потерять её. Это ссылочная целостность (referential integrity, RI).

- Сначала обновите dimensions, потом грузите facts.
- Ищите ключ в самой dimension. Natural key в fact не оставляйте.
- Каждый natural key должен найти ключ или получить значение по умолчанию. Сбои RI возвращайте на разбор.
- Дубли (key collisions) — ошибка для quality screen: остановить загрузку, отложить строки или исправить по правилу и записать событие.

При перезагрузке истории и при late arriving facts нужен ключ, действовавший в момент события: дата события между датами начала и конца версии.

> **Пояснение:** в SQL это `LEFT JOIN` с условием `event_date BETWEEN row_start AND row_end` и `coalesce(key, 0)`. Так сделано в практике ниже.

### Подсистема 15. Multivalued dimension bridge table builder

Когда dimension принимает несколько значений на grain fact (глава 8), а grain менять нельзя, нужна `bridge table`. ETL решает: делать для каждого набора значений новую группу или переиспользовать одинаковую. Простого правила нет. Если у dimension есть type 2 атрибуты, bridge тоже меняется во времени.

### Подсистема 16. Late arriving data handler

Обычно fact и его dimensions приходят вместе. Но бывает иначе.

- **Late arriving fact:** событие пришло с опозданием. Нужно найти версию dimension на дату события и иногда поправить `semi-additive` балансы (их нельзя суммировать по времени) в следующих строках.
- **Late arriving dimension:** fact пришёл без описания. В суточном batch часто можно подождать. В real-time нельзя.

Для late arriving dimension возможны два случая. Опоздало type 2 изменение: вставьте новую версию, поправьте даты версий и ключи в facts после даты изменения. Natural key есть, а строки клиента нет: создайте `inferred member` — строку с новым surrogate key и временными значениями, потом перезапишите её как type 1. Ссылка на общую строку по умолчанию хуже: ключи в facts придётся менять.

### Подсистемы 17 и 18. Dimension manager и fact provider

`Dimension manager` — центральный владелец conformed dimension, у каждой он свой. Он добавляет строки (для type 2 с новыми ключами), правит type 1 и 3 на месте, обновляет номер версии и одновременно рассылает dimension всем fact providers. Номер версии используют в drill across: у всех должна быть одна версия.

`Fact provider` владеет fact-таблицами и обязан использовать conformed dimensions. Он грузит новые строки facts с заменой ключей, правит строки (исправления, accumulating snapshots, late arriving dimensions), пересчитывает затронутые агрегаты и сообщает пользователям о важных изменениях.

### Подсистема 19. Aggregate builder

Агрегаты — самый заметный способ ускорить большое хранилище, они похожи на индексы. ETL заполняет aggregate fact tables и нужные shrunken dimensions. Самая быстрая стратегия — инкрементальная. Агрегаты должны совпадать с atomic данными, иначе fact provider отключает их.

### Подсистема 20. OLAP cube builder

`OLAP cube` строят из реляционной dimensional schema: куб — расширение хранилища, а не конкурент. Кубы грузят после обычного ETL, потому что многие OLAP-системы не решают ссылочную целостность и очистку. Type 2 хорошо подходит кубам: новый ключ — просто новый член. Type 1, который переписывает историю, подходит плохо: перезапись может заставить пересчитать кубы, испортить их или удалить.

### Подсистема 21. Data propagation manager

Иногда данные из presentation server нужно отдать другим системам: партнёрам, госорганам (например Medicare), пакетным аналитическим приложениям и data mining tools. Это тоже ETL: extract, лёгкая трансформация, load. Отличие в том, что требования получателя не обсуждаются.

## Manage: подсистемы 22–34

Хранилищу должны доверять при принятии решений. Для этого ETL должен давать reliability (процессы стабильно доходят до конца), availability (хранилище доступно, как обещано в SLA) и manageability (ETL меняется вместе с бизнесом).

### Подсистема 22. Job scheduler

Планировщик должен быть единым и управляться метаданными. Он больше, чем запуск по часам: знает зависимости между задачами (если customer не загрузился, грузить продажи новых клиентов рискованно) и готовность файлов или таблиц. Он запускает задачи по времени и по событию, пишет метаданные и лог (лучше в базу, чем в файлы) и сообщает о проблемах в подсистему 30.

### Подсистема 23. Backup system

Backup обычно ведёт не команда ETL, но проектируют его вместе с ETL: нужны и staging-данные для перезапуска. `Archive and retrieval` переносит старые данные на дешёвые носители: это баланс стоимости и пользы, и аудитор может запросить архив. Сроки хранения бывают от пяти до 50 лет, поэтому нужно уметь читать данные в будущем.

### Подсистема 24. Recovery and restart system

Сбои неизбежны, поэтому их планируют заранее. Грузите небольшими порциями и помните, что закоммичено. Можно продолжить с места остановки (нужны надёжные checkpoint) или откатить задачу и начать заново. Во многих случаях лучше второе. Авторы советуют давать fact-таблицам одноколоночный последовательный surrogate key. Он помогает возобновить или откатить загрузку по диапазону ключей и позволяет заменить update на insert и delete.

### Подсистемы 25 и 26. Version control и version migration

`Version control` хранит снимки всей логики и метаданных ETL и умеет сравнивать версии. `Version migration` переносит версию из development в test и production и умеет откатить перенос. Всё, что меняют в production (схема, индексы, агрегаты), сначала проектируют в development и проверяют скриптом в test.

### Подсистема 27. Workflow monitor

Монитор использует метаданные планировщика и показывает статус задач, число обработанных записей, ошибки и тренды. Он шлёт алерт, если задача идёт заметно дольше или короче обычного. С него начинают поиск узких мест. Среди частых причин книга называет плохо проиндексированные запросы, нехватку памяти, сортировку в СУБД, пересборку агрегатов с нуля, слишком позднюю фильтрацию (CDC) и неиспользованный параллелизм.

### Подсистема 28. Sorting system

Сортировка нужна для агрегации и join плоских файлов, поэтому она выделена в подсистему. Специальная утилита очень быстра на текстовых файлах. Сортировка со счётом помогает искать проблемы качества. Простой выбор для большинства — функция сортировки ETL tool.

### Подсистема 29. Lineage and dependency analyzer

`Lineage` идёт назад: от поля в таблице или отчёте к источнику и всем преобразованиям. `Dependency` идёт вперёд: от поля источника ко всем таблицам и отчётам, где оно используется. Lineage нужен при compliance, dependency — чтобы оценить влияние изменений в источнике.

### Подсистема 30. Problem escalation system

Систему эскалации проблем проектируют заранее. Загрузка идёт без людей, а при проблеме ETL сам сообщает о ней: в лог или сообщением оператору, руководителю или разработчику. Первая линия поддержки — группа мониторинга, разработчики подключаются последними. Книга описывает уровни: help desk, администратор или DBA, руководитель ETL, разработчик ETL.

### Подсистема 31. Parallelizing/pipelining system

Цель — уложиться в окно загрузки на нескольких процессорах или в кластере (grid). Parallelizing и pipelining лучше включать автоматически, например разделять extract по диапазонам значений. Проверьте, что СУБД источника справляется с параллелизмом.

### Подсистема 32. Security system

Серьёзная утечка вероятнее изнутри, а команда ETL — такой же риск. Авторы советуют ролевой доступ ко всем данным и метаданным ETL, журнал обращений и шифрование bulk-передачи даже внутри firewall. Доступ к production-серверу строго ограничивают, но кто-то должен уметь его перезапустить. Носители backup защищают как онлайн-системы.

### Подсистема 33. Compliance manager

Compliance — это `chain of custody`, как у полиции с уликами: хранилище охраняет данные с момента поступления, показывает их состояние на любой момент и фиксирует, кто имел доступ. Копию исходных данных хранят у доверенной третьей стороны. Иногда данные нельзя менять вообще: изменение — это новая версия строки с датами начала и конца. Авторы пишут, что тогда type 1 и type 3 «мертвы»: остаются только insert.

Для fact добавляют пять колонок: surrogate key строки, начало и конец версии, ссылки на причину изменения и на источник. Изменение создаёт новую строку с тем же ключом. Такую таблицу можно держать в фоне, а рабочую fact-таблицу оставить обычной. Авторы предупреждают: не все данные подпадают под такие правила, сначала получите указания chief compliance officer.

### Подсистема 34. Metadata repository manager

ETL создаёт много метаданных: process, technical и business. Нужна сбалансированная стратегия между «ничего» и «слишком много». Заложите время на метаданные и назначьте ответственного.

## Итоги главы

- Авторы дают ETL структуру: 34 подсистемы в четырёх группах.
- Требования по десяти областям собирают до дизайна, а переход от batch к streaming переписывает почти все шаги.
- Data profiling делают в самом начале: он решает, брать ли источник. Timed extract ненадёжен как CDC.
- Quality screens бывают column, structure и business rule, и лучшая реакция на ошибку — пометить данные и идти дальше.
- События качества пишутся в error event schema, а строки fact ссылаются на audit dimension.
- Dedup и survivorship собирают одну строку из нескольких источников, а conforming приводит колонки к общим значениям.
- Surrogate key pipeline заменяет natural keys: dimensions обновляют раньше facts, а историю грузят по версии на дату события.
- Для late arriving dimension создают inferred member и потом перезаписывают его как type 1.
- Группа manage делает ETL надёжным и управляемым, а загрузка должна идти без людей.

## Ключевые термины

| Термин | Значение |
|---|---|
| `CDC` | Выделение только тех данных, которые изменились с прошлой загрузки |
| `Quality screen` | Тест данных в потоке. При ошибке пишет событие в error event schema |
| `Error event schema` | Dimensional schema для событий качества: fact на ошибку и detail fact на поле |
| `Audit dimension` | Dimension с метаданными загрузки, на неё ссылается строка fact |
| `Survivorship` | Правила сборки одной строки из совпавших записей |
| `Surrogate key pipeline` | Шаг, который заменяет natural keys в fact на surrogate keys |
| `Inferred member` | Строка dimension с временными значениями для раннего факта |
| `Chain of custody` | Доказательство, что итоговые данные получены из исходных и не изменены |
| `Lineage / dependency` | Путь данных назад к источнику и вперёд к таблицам и отчётам |
| `Late arriving fact / dimension` | Событие или описание, которые пришли позже, чем нужно для обычной загрузки |

## Что это значит на практике

- Начните с data profiling: он покажет, сколько нужно чистки.
- Не используйте timed extract («все строки за вчера») как единственный CDC. Если опираетесь на `updated_at`, храните отметку по данным, а не по часам, и проверьте, что поле надёжно.
- Quality screens — это тесты в `dbt` (`not_null`, `accepted_values`, `relationships`). Результаты тестов храните в таблице.
- Помечайте плохие строки и записывайте событие. Останавливайте загрузку, только если без этого нельзя.
- Всегда держите строку Unknown в каждой dimension. Тогда fact не получает `NULL` в ключе.
- Для раннего факта создавайте inferred member, а не отправляйте его на общую строку Unknown.
- Добавляйте в fact audit key: batch, число строк, статус качества.
- Сначала загружайте dimensions, потом facts. Для истории ищите версию dimension по дате события.
- Сохраняйте сырой слой (raw или staging): это архив и точка перезапуска.
- Современные оркестраторы закрывают группу manage: расписание, повторы, мониторинг, lineage.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Решения тоже запускайте по порядку: каждое использует результат предыдущего.

### Шаг 1. Создаём сырые данные

```sql
-- выгрузка клиентов из источника. Есть дубли, лишние пробелы, плохие значения
CREATE TABLE src_customer AS
SELECT * FROM (VALUES
    (101, '  Иван Петров ', 'IVAN@MAIL.RU',      'Москва', TIMESTAMP '2024-03-01 10:00:00'),
    (101, 'Иван Петров',    'ivan@mail.ru',      'Москва', TIMESTAMP '2024-03-01 18:00:00'),
    (102, 'Анна Смирнова',  'anna@mail.ru',      'Казань', TIMESTAMP '2024-03-01 11:00:00'),
    (103, 'Олег Иванов',    NULL,                'Самара', TIMESTAMP '2024-03-01 12:00:00'),
    (104, 'Мария Орлова',   'maria(at)mail.ru',  'Москва', TIMESTAMP '2024-03-01 13:00:00'),
    (105, 'Сергей Волков',  'sergey@mail.ru',    NULL,     TIMESTAMP '2024-03-01 14:00:00')
) t(customer_id, name, email, city, updated_at);

-- выгрузка продаж
CREATE TABLE src_sales AS
SELECT * FROM (VALUES
    (5001, 1, 101,  DATE '2024-03-15', 100.0),
    (5002, 1, 101,  DATE '2024-04-10', 150.0),
    (5003, 1, 102,  DATE '2024-04-11',  80.0),
    (5004, 1, 107,  DATE '2024-04-12',  60.0),   -- клиента 107 ещё нет в dimension
    (5005, 1, NULL, DATE '2024-04-12',  30.0)    -- клиент не указан
) t(order_id, line_no, customer_id, order_date, amount);
```

### Задания

**1.** Data profiling и deduplication. Сначала посмотрите на сырые данные: число строк, число разных `customer_id`, число `NULL`, диапазон времени. Потом создайте `stg_customer`: очистите пробелы, приведите email к нижнему регистру, оставьте одну последнюю строку на клиента.

<details>
<summary>Решение</summary>

```sql
-- profiling
SELECT count(*)                                  AS rows_total,
       count(DISTINCT customer_id)               AS distinct_ids,
       count(*) FILTER (WHERE email IS NULL)     AS null_email,
       count(*) FILTER (WHERE city IS NULL)      AS null_city,
       min(updated_at) AS min_ts, max(updated_at) AS max_ts
FROM src_customer;

-- dedup: победитель — самая свежая строка
CREATE TABLE stg_customer AS
SELECT customer_id, trim(name) AS name, lower(email) AS email, city, updated_at
FROM src_customer
QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1;

SELECT * FROM stg_customer ORDER BY customer_id;
```

Было 6 строк и 5 разных клиентов. После dedup в `stg_customer` 5 строк. Здесь самое простое правило: побеждает строка с самым поздним `updated_at`. В книге survivorship сложнее: для каждой колонки задают приоритет источников и собирают одну строку из лучших значений.
</details>

**2.** Quality screens и error event. Создайте таблицу `error_event`. Запишите в неё: пустой email (warning), email без нормального формата (warning), пустой город (error).

<details>
<summary>Решение</summary>

```sql
CREATE TABLE error_event (
    event_key INT, batch_id INT, screen_name VARCHAR, table_name VARCHAR,
    record_id VARCHAR, severity VARCHAR, event_ts TIMESTAMP);

INSERT INTO error_event
SELECT coalesce((SELECT max(event_key) FROM error_event), 0) + row_number() OVER (ORDER BY screen, customer_id),
       1, screen, 'stg_customer', customer_id::VARCHAR, severity, TIMESTAMP '2024-03-02 02:00:00'
FROM (
    SELECT customer_id, 'email_not_null' AS screen, 'warning' AS severity
    FROM stg_customer WHERE email IS NULL
    UNION ALL
    SELECT customer_id, 'email_format', 'warning'
    FROM stg_customer
    WHERE email IS NOT NULL AND NOT regexp_matches(email, '^[^@ ]+@[^@ ]+\.[a-z]+$')
    UNION ALL
    SELECT customer_id, 'city_not_null', 'error'
    FROM stg_customer WHERE city IS NULL
) e;

SELECT * FROM error_event ORDER BY event_key;
```

Три события: клиенты 103, 104 и 105. Клиент 105 имеет severity `error`, его мы не загрузим.
</details>

**3.** Surrogate keys, unknown member и audit dimension. Создайте `dim_audit` и запишите одну строку для batch 1. Создайте `dim_customer` с версиями (`row_start`, `row_end`, `is_current`). Добавьте строку Unknown с ключом 0. Загрузите клиентов без `error` и дайте им ключи.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE dim_audit (
    audit_key INT, batch_id INT, load_ts TIMESTAMP,
    rows_read INT, rows_loaded INT, rows_rejected INT, quality_status VARCHAR);

INSERT INTO dim_audit
SELECT 1, 1, TIMESTAMP '2024-03-02 02:00:00',
       (SELECT count(*) FROM src_customer),
       (SELECT count(*) FROM stg_customer WHERE city IS NOT NULL),
       (SELECT count(DISTINCT record_id) FROM error_event WHERE severity = 'error'),
       CASE WHEN EXISTS (SELECT 1 FROM error_event WHERE severity = 'error')
            THEN 'with errors' ELSE 'clean' END;

CREATE TABLE dim_customer (
    customer_key INT, customer_id INT, name VARCHAR, email VARCHAR, city VARCHAR,
    row_start DATE, row_end DATE, is_current BOOLEAN, is_inferred BOOLEAN, audit_key INT);

-- unknown member
INSERT INTO dim_customer VALUES
    (0, NULL, 'Unknown', NULL, 'Unknown', DATE '1900-01-01', DATE '9999-12-31', TRUE, FALSE, 0);

-- ключ = max + порядковый номер
INSERT INTO dim_customer
SELECT (SELECT max(customer_key) FROM dim_customer) + row_number() OVER (ORDER BY customer_id),
       customer_id, name, email, city, DATE '2024-03-01', DATE '9999-12-31', TRUE, FALSE, 1
FROM stg_customer
WHERE city IS NOT NULL;

SELECT * FROM dim_audit;
SELECT * FROM dim_customer ORDER BY customer_key;
```

В `dim_audit`: прочитано 6, загружено 4, отклонено 1. В `dim_customer` пять строк: Unknown и клиенты 101-104.
</details>

**4.** SCD в ETL. Пришёл второй batch. У клиента 101 изменился город (type 2). У клиентов 101 и 103 изменился email (type 1). Появился новый клиент 106. Примените изменения.

<details>
<summary>Решение</summary>

```sql
CREATE TABLE stg_customer_2 AS
SELECT * FROM (VALUES
    (101, 'Иван Петров',   'ivan.new@mail.ru', 'Санкт-Петербург', TIMESTAMP '2024-04-01 09:00:00'),
    (102, 'Анна Смирнова', 'anna@mail.ru',      'Казань',          TIMESTAMP '2024-04-01 09:00:00'),
    (103, 'Олег Иванов',   'oleg@mail.ru',      'Самара',          TIMESTAMP '2024-04-01 09:00:00'),
    (106, 'Павел Седов',   'pavel@mail.ru',     'Омск',            TIMESTAMP '2024-04-01 09:00:00')
) t(customer_id, name, email, city, updated_at);

-- audit-строка для batch 2
INSERT INTO dim_audit VALUES (2, 2, TIMESTAMP '2024-04-02 02:00:00', 4, 4, 0, 'clean');

-- type 1: перезаписываем email во всех версиях
UPDATE dim_customer d SET email = s.email
FROM stg_customer_2 s
WHERE d.customer_id = s.customer_id AND d.email IS DISTINCT FROM s.email;

-- type 2: находим изменения города у текущих строк
CREATE TEMP TABLE scd2_changes AS
SELECT s.*
FROM stg_customer_2 s
JOIN dim_customer d ON d.customer_id = s.customer_id AND d.is_current
WHERE d.city IS DISTINCT FROM s.city;

-- шаг 1: закрываем старые версии
UPDATE dim_customer
SET row_end = DATE '2024-03-31', is_current = FALSE
WHERE is_current AND customer_id IN (SELECT customer_id FROM scd2_changes);

-- шаг 2: вставляем новые версии и новых клиентов
INSERT INTO dim_customer
SELECT (SELECT max(customer_key) FROM dim_customer) + row_number() OVER (ORDER BY customer_id),
       customer_id, name, email, city, DATE '2024-04-01', DATE '9999-12-31', TRUE, FALSE, 2
FROM (
    SELECT * FROM scd2_changes
    UNION ALL
    SELECT * FROM stg_customer_2
    WHERE customer_id NOT IN (SELECT customer_id FROM dim_customer WHERE customer_id IS NOT NULL)
);

SELECT customer_key, customer_id, email, city, row_start, row_end, is_current
FROM dim_customer
ORDER BY customer_id NULLS FIRST, row_start;
```

У клиента 101 две версии: Москва (до 31 марта) и Санкт-Петербург (с 1 апреля). Email новый в обеих. Клиент 106 добавлен.
</details>

**5.** Surrogate key pipeline и late arriving dimension. Загрузите `fact_sales`. Для клиента 107 в dimension нет строки. Создайте inferred member. Клиента без `customer_id` отправьте на unknown member. Для 101 подберите версию по дате заказа. Потом «пришли» данные клиента 107: обновите строку.

<details>
<summary>Решение</summary>

```sql
-- inferred members для ранних фактов
INSERT INTO dim_customer
SELECT (SELECT max(customer_key) FROM dim_customer) + row_number() OVER (ORDER BY customer_id),
       customer_id, 'Не определён', NULL, 'Unknown',
       DATE '1900-01-01', DATE '9999-12-31', TRUE, TRUE, 2
FROM (
    SELECT DISTINCT customer_id
    FROM src_sales
    WHERE customer_id IS NOT NULL
      AND customer_id NOT IN (SELECT customer_id FROM dim_customer WHERE customer_id IS NOT NULL)
);

-- surrogate key pipeline: версия, действующая на дату заказа
CREATE TABLE fact_sales AS
SELECT s.order_id, s.line_no,
       coalesce(d.customer_key, 0) AS customer_key,
       s.order_date, s.amount,
       2 AS audit_key          -- каждая fact-строка ссылается на audit dimension
FROM src_sales s
LEFT JOIN dim_customer d
       ON d.customer_id = s.customer_id
      AND s.order_date BETWEEN d.row_start AND d.row_end;

SELECT f.order_id, f.order_date, f.customer_key, d.city, d.is_inferred
FROM fact_sales f
JOIN dim_customer d USING (customer_key)
ORDER BY f.order_id;

-- пришли настоящие данные клиента 107: перезаписываем inferred-строку
UPDATE dim_customer
SET name = 'Роман Лис', email = 'roman@mail.ru', city = 'Тверь', is_inferred = FALSE
WHERE customer_id = 107 AND is_inferred;

SELECT * FROM dim_customer WHERE customer_id = 107;
```

Заказ 5001 (март) указывает на версию «Москва». Заказ 5002 (апрель) — на «Санкт-Петербург». Заказ 5004 использует inferred member, заказ 5005 — ключ 0. После обновления строки 107 факт остаётся на том же ключе. Ничего перезагружать не нужно.
</details>

## Вопросы для самопроверки

1. Почему timed extract («все строки за вчера») ненадёжен как CDC? Какой способ надёжнее и когда он дорог?
2. Какие три типа quality screens описывает книга? Приведите по примеру. Почему авторы советуют помечать данные, а не останавливать загрузку или отправлять строки в suspense file?
3. Зачем строке fact ссылка на audit dimension?
4. Чем inferred member отличается от Unknown member? Почему при раннем факте лучше первый?
5. Почему dimensions обновляют до загрузки facts? Когда ключ ищут по текущей версии, а когда по дате события?
6. Почему при жёстких требованиях compliance type 1 и type 3 «мертвы» и как тогда меняют строки fact?

Предыдущая: [Глава 18. Процесс моделирования](/book-summaries/engineering/data-warehouse-toolkit/18-dimensional-modeling-process/). Следующая: [Глава 20. Разработка ETL](/book-summaries/engineering/data-warehouse-toolkit/20-etl-development-process/).
