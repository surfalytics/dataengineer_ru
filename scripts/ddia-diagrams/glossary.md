# Глоссарий: Designing Data-Intensive Applications, 2nd Edition (Martin Kleppmann, Chris Riccomini)

Единые слова для всех глав. Правила: навык `book-summary`, раздел «Glossary first».
Колонка «Как пишем»: термин в обратных кавычках = оставляем английским; обычное слово = пишем по-русски.

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| data-intensive application | приложение с большим объёмом данных (`data-intensive`) | данно-интенсивное приложение | Главная трудность приложения в данных, а не в вычислениях |
| trade-off | компромисс (`trade-off`) | торговля, обмен | Выигрыш в одном свойстве стоит потери в другом |
| fault tolerance | отказоустойчивость | устойчивость к ошибкам | Система переживает сбои частей |
| maintainability | простота сопровождения | поддерживаемость | Легко чинить, менять и понимать систему |
| throughput | `throughput` | пропускная способность | Сколько записей или байт система обрабатывает за секунду |
| latency | задержка (`latency`) | латентность | Время от запроса до ответа |
| tail latency | `tail latency` | хвостовая задержка | Самые медленные запросы: p99 и выше |
| percentile | перцентиль (`p50`, `p99`) | процентиль | Доля запросов быстрее порога |
| data warehouse | хранилище данных (`data warehouse`) | склад данных | Хранилище для аналитики |
| data lake | `data lake` | озеро данных | Хранилище сырых файлов любого формата |
| lakehouse | `lakehouse` | озерохранилище | Файлы озера плюс таблицы и транзакции хранилища |
| data pipeline | `pipeline` | пайплайн | Цепочка шагов, которая переносит и преобразует данные |
| star schema | `star schema` | звёздная схема | Таблица фактов в центре, измерения вокруг |
| fact table | таблица фактов (`fact table`) | факт-таблица | Измеримые события |
| B-tree | `B-tree` | Б-дерево | Дерево страниц фиксированного размера с обновлением на месте |
| compaction | `compaction` | уплотнение, сжатие | Фоновое слияние файлов `LSM-tree` |
| write-ahead log | `write-ahead log` (`WAL`) | журнал упреждающей записи | Журнал, в который пишут до изменения данных |
| schema evolution | `schema evolution` | эволюция схемы | Схема меняется, старые и новые данные живут вместе |
| leader / follower | `leader` / `follower` | ведущий / ведомый, мастер / слейв | Узел, который принимает записи / узел, который их повторяет |
| failover | `failover` | фейловер | Переход на другую реплику, когда лидер упал |
| replication lag | лаг репликации (`replication lag`) | отставание реплики | Насколько реплика отстала от лидера |
| eventual consistency | `eventual consistency` | согласованность в конечном счёте | Реплики со временем сходятся к одному значению |
| multi-leader replication | репликация с несколькими `leader` | мульти-мастер | Записи принимают несколько узлов |
| sharding | `sharding` | шардинг, шардирование | Деление набора данных между узлами |
| shard | `shard` | шард | Одна часть набора данных на одном узле |
| partition (shard) | `shard` | партиция | В DDIA2 `partition` для частей данных не используем |
| network partition | разрыв сети (`network partition`) | сетевая партиция | Часть узлов не видит остальные |
| rebalancing | `rebalancing` | ребалансировка | Перенос `shard` между узлами |
| hot spot | `hot spot` | горячая точка | `Shard` или ключ с непропорционально большой нагрузкой |
| durability | долговечность | устойчивость | Записанное не пропадает после сбоя |
| serializability | `serializability` | сериализуемость | Результат такой, будто транзакции шли по очереди |
| dirty read / dirty write | `dirty read` / `dirty write` | грязное чтение | Чтение или запись чужих незафиксированных данных |
| lost update | `lost update` | потерянное обновление | Две транзакции читают и пишут одно значение, одна запись теряется |
| phantom | `phantom` | фантом | Запись меняет результат чужого запроса `WHERE` |
| two-phase locking | `two-phase locking` (`2PL`) | двухфазная блокировка | Блокировки на чтение и запись держатся до конца транзакции |
| deadlock | `deadlock` | взаимная блокировка | Транзакции ждут друг друга |
| commit / abort | `commit` / `abort` | коммит | Зафиксировать / отменить транзакцию |
| two-phase commit | `two-phase commit` (`2PC`) | двухфазный коммит | Протокол атомарной транзакции на нескольких узлах |
| saga | `saga` | сага | Цепочка шагов с компенсирующими действиями |
| lease | `lease` | аренда | Блокировка с ограниченным сроком |
| linearizability | `linearizability` | линеаризуемость | Система выглядит как одна копия данных |
| CAP theorem | теорема `CAP` | — | При разрыве сети нельзя иметь и `linearizability`, и доступность |
| shuffle | `shuffle` | перемешивание | Перераспределение записей по ключу между узлами |
| message broker | `message broker` | брокер сообщений | Сервис, который хранит и раздаёт сообщения |
| producer / consumer | `producer` / `consumer` | продюсер / консьюмер | Кто пишет сообщения / кто их читает |
| offset | `offset` | офсет, смещение | Позиция `consumer` в журнале |
| watermark | `watermark` | водяной знак | Отметка: события старше неё больше не ждём |
| backpressure | `backpressure` | обратное давление | Медленный получатель тормозит отправителя |
| dual writes | `dual writes` | двойная запись | Приложение пишет в две системы отдельно, они расходятся |
| end-to-end argument | `end-to-end argument` | сквозной аргумент | Корректность проверяют на краях системы, а не в каждом слое |
| encoding | кодирование (`encoding`) | сериализация | Превращение данных из памяти в байты |
| operational system | операционная система (`operational`) | — | Система, где данные создаются и меняются; не ОС. Ведущий решает, нужен ли вариант «OLTP-система» |
| analytical system | аналитическая система | — | Копия данных только для чтения, настроенная под аналитику |
| OLTP / OLAP | `OLTP` / `OLAP` | — | Шаблоны доступа: точечные запросы / агрегаты по многим записям |
| point query | точечный запрос (`point query`) | — | Поиск нескольких записей по ключу |
| ETL / ELT | `ETL` / `ELT` | — | Выгрузка, преобразование, загрузка |
| reverse ETL | `reverse ETL` | обратный ETL | Результаты аналитики идут в операционные системы |
| HTAP | `HTAP` | — | OLTP и аналитика в одной системе |
| data silos | `data silos` | — | Данные разбросаны по системам |
| system of record | `system of record` | система записи | Источник истины (`source of truth`) |
| derived data | производные данные (`derived data`) | выведенные данные | Можно пересоздать из источника |
| materialized view | `materialized view` | — | — |
| feature engineering | `feature engineering` | — | Подбор признаков для ML |
| self-hosting | `self-hosting` | самохостинг | Готовое ПО, которое запускаете сами |
| on premises | `on premises` | — | Своё железо |
| cloud native | `cloud native` | облачно-нативный | Архитектура поверх облачных сервисов |
| object storage | объектное хранилище (`object storage`) | — | S3 и аналоги |
| multitenancy | `multitenancy` | мультиарендность | Один сервис обслуживает многих клиентов |
| vendor lock-in | `vendor lock-in` | — | Привязка к поставщику |
| distributed system | распределённая система | — | — |
| node | узел (`node`) | нода | Процесс в распределённой системе |
| observability | `observability` | наблюдаемость | Данные о работе системы для поиска проблем |
| serverless / FaaS | `serverless` (`FaaS`) | бессерверный | — |
| microservices | микросервисы | — | — |
| data minimization | минимизация данных | — | `Datensparsamkeit` |
| right to be forgotten | право на забвение | — | GDPR |
| nonfunctional requirements | нефункциональные требования | нефункциональные потребности | Каким должно быть приложение: быстрым, надёжным, масштабируемым |
| home timeline | домашняя лента (`home timeline`) | хронология | Свежие посты тех, на кого подписан пользователь |
| polling | `polling` | поллинг | Клиент регулярно повторяет запрос |
| fan-out | `fan-out` | веер, разветвление | Во сколько раз растёт число запросов дальше по цепочке |
| response time | время ответа (`response time`) | время отклика | Всё время от запроса до ответа на стороне клиента |
| service time | время обработки (`service time`) | время сервиса | Время активной работы над запросом |
| queueing delay | задержка в очереди (`queueing delay`) | — | Ожидание свободного CPU или буфера |
| head-of-line blocking | `head-of-line blocking` | блокировка головы очереди | Медленные запросы задерживают быстрые за ними |
| jitter | `jitter` | джиттер | Разброс сетевой задержки |
| tail latency amplification | `tail latency amplification` | — | Один медленный вызов замедляет весь запрос |
| SLO / SLA | SLO / SLA | — | Цель уровня сервиса / договор о последствиях |
| retry storm | `retry storm` | шторм ретраев | Повторы усиливают перегрузку |
| metastable failure | метастабильный отказ (`metastable failure`) | — | Система не выходит из перегрузки сама |
| exponential backoff | `exponential backoff` | экспоненциальная задержка | Растущие паузы между повторами со случайным сдвигом |
| circuit breaker | `circuit breaker` | предохранитель | Временно не звать сервис, который недавно падал |
| load shedding | `load shedding` | сброс нагрузки | Сервер заранее отклоняет часть запросов |
| fault / failure | `fault` / `failure` | — | Сбой части / отказ всей системы |
| single point of failure | единая точка отказа (SPOF) | — | Часть, сбой которой роняет всю систему |
| fault injection | `fault injection` | инъекция сбоев | Сбои вызывают нарочно |
| chaos engineering | `chaos engineering` | инженерия хаоса | Эксперименты со сбоями для проверки защиты |
| redundancy | избыточность (`redundancy`) | резервность | Запасные компоненты |
| availability zone | зона доступности (`availability zone`) | — | Ресурсы, которые стоят физически рядом |
| rolling upgrade | `rolling upgrade` | катящееся обновление | Обновление узлов по одному без простоя |
| blameless postmortem | `blameless postmortem` | постмортем без вины | Разбор инцидента без поиска виноватых |
| scalability | масштабируемость (`scalability`) | скалируемость | Способность справляться с ростом нагрузки |
| linear scalability | линейная масштабируемость | — | Вдвое больше ресурсов — вдвое больше нагрузки |
| scaling up / scaling out | `scaling up` / `scaling out` | — | Мощнее машина / больше машин |
| shared-memory / shared-disk / shared-nothing | `shared-memory` / `shared-disk` / `shared-nothing` | — | Три архитектуры масштабирования |
| operability | удобство эксплуатации (`operability`) | операбельность | Легко поддерживать работу системы |
| simplicity | простота (`simplicity`) | — | Систему легко понять |
| evolvability | способность к развитию (`evolvability`) | эволюционируемость | Систему легко менять |
| essential / accidental complexity | `essential complexity` / `accidental complexity` | — | Сложность задачи / сложность от инструментов |
| big ball of mud | `big ball of mud` | — | Проект, увязший в сложности |
| relational model | реляционная модель | — | Данные в таблицах (отношениях) из строк |
| document model | документная модель | — | Данные как самодостаточные JSON-документы |
| join | `join` | джойн | Связь строк двух таблиц по ключу |
| impedance mismatch | `impedance mismatch` | несоответствие импедансов | Разрыв между объектами в коде и таблицами |
| ORM | ORM | — | Фреймворк, который переводит объекты в таблицы и обратно |
| N+1 query problem | проблема `N+1` | — | Запрос за списком и ещё по запросу на каждый элемент |
| normalization / denormalization | нормализация / денормализация | — | Данные в одном месте со ссылками по ID / копии ради чтения |
| one-to-many, many-to-one, many-to-many | one-to-many, many-to-one, many-to-many | один-ко-многим без пояснения | Виды связей; по-русски в скобках при первом упоминании |
| hydrating | `hydrating` | гидрирование | Подстановка данных по ID в коде приложения |
| dimension table | таблица измерений (`dimension table`) | таблица размерностей | Описывает «кто, что, где, когда» для фактов |
| snowflake schema | `snowflake schema` | схема снежинки | Измерения разбиты на подизмерения |
| one big table | `one big table` (`OBT`) | — | Измерения влиты в таблицу фактов |
| shredding | `shredding` | шреддинг | Разбиение документа на несколько таблиц |
| schema-on-read / schema-on-write | `schema-on-read` / `schema-on-write` | схема при чтении | Схема неявная при чтении / явная при записи |
| locality | локальность | — | Связанные данные лежат рядом |
| vertex / edge | вершина / ребро | нода, эдж | Части графа |
| property graph | `property graph` | граф свойств | Граф из вершин и рёбер с метками и свойствами |
| triple store | `triple store` | хранилище троек, triple-store | Факты как тройки (субъект, предикат, объект) |
| recursive CTE | рекурсивный CTE (`WITH RECURSIVE`) | — | Путь переменной длины в SQL |
| event sourcing | `event sourcing` | событийное хранение | События — источник истины |
| CQRS | `CQRS` | — | Отдельные представления для чтения из формы для записи |
| crypto-shredding | `crypto-shredding` | — | Удаление данных через удаление ключа шифрования |
| DataFrame | DataFrame | датафрейм | Таблица в памяти, с которой работают серией команд |
| one-hot encoding | `one-hot encoding` | — | Столбец на каждое значение категории |
| storage engine | движок хранения (`storage engine`) | двигатель хранения | Часть базы, которая пишет и читает данные на диске |
| log (append-only) | лог (`append-only`) | — | Последовательность записей, в которую только дописывают |
| index | индекс | — | Дополнительная структура из основных данных для быстрого поиска |
| SSTable | `SSTable` | — | Файл пар «ключ, значение», отсортированных по ключу |
| sparse index | разреженный индекс (`sparse index`) | — | Индекс по первому ключу каждого блока |
| memtable | `memtable` | мемтейбл | Отсортированная структура в памяти для свежих записей |
| LSM-tree | `LSM-tree` | LSM-дерево | Каскад `SSTable`, которые сливаются в фоне |
| segment | сегмент | — | Один файл `SSTable` в LSM-движке |
| tombstone | `tombstone` | надгробие | Запись-метка удаления ключа |
| Bloom filter | `Bloom filter` | фильтр Блума | Битовый массив: «ключа точно нет» или «возможно есть» |
| false positive | ложное срабатывание (`false positive`) | — | Фильтр говорит «есть», а ключа нет |
| size-tiered / leveled compaction | size-tiered / leveled `compaction` | — | Стратегии слияния: по размеру / по уровням |
| embedded database | встроенная база (`embedded`) | — | База-библиотека в процессе приложения |
| page (B-tree) | страница | — | Блок фиксированного размера (4–16 КиБ) |
| branching factor | коэффициент ветвления (`branching factor`) | — | Число ссылок на потомков в странице |
| page split | деление страницы (`split`) | — | Полную страницу делят на две |
| torn page | `torn page` | — | Страница, записанная наполовину при сбое |
| copy-on-write | `copy-on-write` | — | Изменённую страницу пишут в новое место |
| write amplification | `write amplification` | — | Отношение байтов на диске к байтам простого лога |
| random / sequential writes | случайная / последовательная запись | — | Мелкие записи вразброс / большие подряд |
| secondary index | вторичный индекс (`secondary index`) | — | Индекс не по первичному ключу, ключи не уникальны |
| clustered index | clustered index | кластерный индекс | Индекс хранит всю строку |
| covering index | covering index | покрывающий индекс | Индекс хранит часть колонок |
| heap file | `heap file` | — | Файл строк без порядка |
| in-memory database | база в памяти (`in-memory`) | — | Все чтения из RAM, диск только для долговечности |
| column-oriented storage | колоночное хранение (`column-oriented storage`) | столбцовое хранение | Значения колонки хранятся вместе |
| compression | компрессия; глагол «сжимать» | сжатие | «Сжатие» запрещено глоссарием для `compaction`; см. вопрос лиду |
| bitmap encoding | `bitmap encoding`, битовая карта (`bitmap`) | — | Битовая карта на значение колонки |
| run-length encoding | `run-length encoding` | — | Хранить длины серий одинаковых значений |
| sort key | `sort key` | — | Колонка сортировки строк |
| query compilation | компиляция запроса | — | SQL превращают в машинный код |
| vectorized processing | векторизованная обработка (`vectorized processing`) | — | Операторы обрабатывают колонку пачками |
| data cube | data cube (OLAP cube) | — | Сетка заранее посчитанных агрегатов |
| table format | табличный формат (`table format`) | — | Iceberg, Delta: какие файлы составляют таблицу |
| data catalog | каталог данных (`data catalog`) | — | Список таблиц базы |
| concatenated index | составной индекс (`concatenated index`) | — | Несколько полей в одном ключе |
| inverted index | обратный индекс (`inverted index`) | инвертированный индекс | Слово → список документов |
| postings list | `postings list` | — | Список ID документов со словом |
| edit distance | расстояние редактирования (`edit distance`) | — | Сколько букв добавить, удалить или заменить |
| semantic search | семантический поиск (`semantic search`) | — | Поиск по смыслу |
| vector embedding | `vector embedding` | эмбеддинг | Вектор чисел, задающий смысл документа |
| HNSW / IVF | HNSW / IVF | — | Приблизительные векторные индексы |
| backward compatibility | `backward compatibility` | обратная совместимость | Новый код читает данные старого кода |
| forward compatibility | `forward compatibility` | прямая совместимость | Старый код читает данные нового кода |
| decoding | декодирование (`decoding`) | десериализация | Перевод байтов обратно в структуры в памяти |
| field tag | тег поля (`field tag`) | — | Номер поля в Protocol Buffers вместо имени |
| varint | `varint` | — | Целое число переменной длины: 7 бит в байте |
| writer's schema / reader's schema | схема писателя / схема читателя | схема записи / схема чтения | Avro: схема, которой записали данные, и схема, которую ждёт код |
| union (Avro) | `union` | — | Тип с несколькими ветками, например `null` и `long` |
| schema registry | реестр схем (`schema registry`) | — | Хранилище версий схем с проверкой совместимости |
| object container file | `object container file` | — | Файл Avro: схема один раз в начале, затем записи |
| IDL | `IDL` | — | Язык описания схем и API |
| RPC | `RPC` | — | Удалённый вызов процедуры |
| location transparency | `location transparency` | прозрачность расположения | Удалённый вызов выглядит как локальный |
| service discovery | `service discovery` | обнаружение сервисов | Поиск адреса сервиса |
| load balancing | балансировка нагрузки (`load balancing`) | — | Распределение запросов между копиями сервиса |
| service mesh | `service mesh` | сервисная сетка | Балансировщики рядом с каждым клиентом и сервером |
| workflow | `workflow` | воркфлоу | Граф задач, например шаги платежа |
| workflow engine | `workflow engine` | — | Движок, который запускает `workflow`: `orchestrator` и `executor` |
| durable execution | `durable execution` | — | Повтор `workflow` с пропуском уже сделанных шагов по журналу |
| idempotence | идемпотентность (`idempotence`) | — | Повтор операции не меняет результат |
| event-driven architecture | архитектура на событиях (`event-driven`) | — | Процессы обмениваются сообщениями через посредника |
| topic / queue | `topic` / очередь (`queue`) | топик | Все подписчики / один из `consumer` получает сообщение |
| actor model | модель акторов (`actor model`) | — | Акторы с локальным состоянием общаются только сообщениями |
| replica | реплика | — | Узел с копией данных |
| single-leader replication | репликация с одним `leader` | мастер-слейв | Все записи идут через один узел |
| leaderless replication | репликация без `leader` (`leaderless`, `Dynamo-style`) | безлидерная | Любая реплика принимает записи |
| replication log | `replication log` | — | Поток изменений от `leader` к `follower` |
| semi-synchronous | `semi-synchronous` | полусинхронная | Один `follower` синхронный, остальные асинхронные |
| split brain | `split brain` | расщепление мозга | Два узла считают себя `leader` |
| fencing | `fencing` | ограждение | Ограничение или выключение старого `leader` |
| statement-based replication | репликация операторов (`statement-based`) | — | Пересылка SQL-операторов |
| WAL shipping | `WAL shipping` | — | Пересылка байтов `write-ahead log` |
| logical log | `logical log` (логическая, построчная репликация) | — | Журнал изменений на уровне строк |
| change data capture | `change data capture` (`CDC`) | захват изменений | Передача изменений базы во внешние системы |
| read-after-write consistency | `read-after-write` (`read-your-writes`) | чтение после записи | Пользователь видит свои записи |
| monotonic reads | `monotonic reads` (монотонное чтение в заголовке) | — | Нельзя прочитать старое после нового |
| consistent prefix reads | `consistent prefix reads` (согласованный префикс в заголовке) | — | Записи видны в порядке, в каком произошли |
| region / availability zone | регион / зона доступности (`availability zone`) | датацентр как синоним региона | Группа дата-центров в одном месте / один дата-центр в регионе |
| tiered storage | многоуровневое хранение (`tiered storage`) | — | Редкие данные в дешёвом хранилище, частые на быстром |
| zero-disk architecture | `zero-disk architecture` (ZDA) | — | Все данные в объектном хранилище, диски только кэш |
| sync engine | `sync engine` | движок синхронизации | Библиотека синхронизации данных клиента |
| offline-first / local-first | `offline-first` / `local-first` | — | Работает без сети / работает без сервисов разработчика |
| concurrent (writes) | параллельные (`concurrent`) | — | Ни одна запись не знала о другой. «Управление конкурентностью» (concurrency control) — допустимо |
| last write wins | `last write wins` (LWW) | — | Побеждает больший timestamp, остальные теряются |
| siblings | `siblings` | сиблинги | Параллельно записанные версии значения |
| strong eventual consistency | `strong eventual consistency` | — | Реплики с одним набором записей совпадают |
| CRDT / operational transformation | `CRDT` / `OT` | — | Алгоритмы автоматического слияния |
| quorum | кворум | — | `w + r > n` |
| read repair / hinted handoff / anti-entropy | `read repair` / `hinted handoff` / `anti-entropy` | — | Починка реплик при чтении / подсказками / в фоне |
| sloppy quorum | `sloppy quorum` | нестрогий кворум | Запись на любые доступные реплики |
| request hedging | `request hedging` | — | Берут ответы самых быстрых реплик |
| gray failure | `gray failure` | серый отказ | Узел не упал, но очень медленный |
| happens-before | `happens-before` | — | B знает об A или построена на ней |
| version vector | `version vector` | вектор версий | Номера версий по всем репликам |
| vector clock | векторные часы (`vector clock`) | — | Похоже на `version vector`, но не то же самое |
| partition key | `partition key` | ключ партиции, ключ партиционирования | Поле, по которому запись попадает в `shard` |
| skew | перекос (`skew`) | скос | Данные или запросы распределены неровно |
| hot key | `hot key` | горячий ключ (как термин) | Один ключ с огромной нагрузкой |
| key-range sharding | `sharding` по диапазону ключей | шардирование по диапазону | `Shard` владеет непрерывным диапазоном ключей |
| hash sharding / hash-range sharding | `sharding` по хешу / по диапазону хешей | — | `Shard` владеет диапазоном значений хеша |
| pre-splitting | `pre-splitting` | предразбиение | Начальные `shard` в пустой базе |
| resharding | `resharding` | решардинг | Смена числа `shard` с перезаписью данных |
| consistent hashing | `consistent hashing` | согласованное хеширование | При смене числа `shard` переезжает минимум ключей |
| multitenancy / tenant | `multitenant`, `tenant` | тенант | Один сервис, много клиентов с раздельными данными |
| cell-based architecture | `cell-based architecture` | клеточная архитектура | Сервисы и данные группы клиентов в автономной ячейке |
| request routing | маршрутизация запросов (request routing) | роутинг запросов | Выбор узла для запроса |
| routing tier | `routing tier` | слой роутинга | Слой, который знает карту `shard` и пересылает запросы |
| coordination service | сервис координации | — | ZooKeeper, etcd: хранит карту `shard` |
| gossip protocol | `gossip protocol` | протокол сплетен | Узлы передают друг другу состояние кластера |
| local / global secondary index | локальный / глобальный вторичный индекс (`local index` / `global index`) | — | Индекс внутри `shard` / индекс, поделённый по значению |
| document-partitioned / term-partitioned | `document-partitioned` / `term-partitioned` | — | Другие названия local / global index |
| transaction | транзакция | — | Группа чтений и записей как одна операция |
| atomicity | атомарность | — | В ACID: «всё или ничего» при сбое, отменяемость |
| consistency (ACID) | согласованность | консистентность | Инварианты приложения выполняются |
| isolation | изоляция | — | Параллельные транзакции не мешают друг другу |
| invariant | инвариант | — | Правило о данных, верное всегда |
| race condition | гонка (`race condition`) | состояние гонки | Ошибка зависит от совпадения времени двух клиентов |
| read committed / read uncommitted | `read committed` / `read uncommitted` | чтение зафиксированного | Уровни изоляции |
| snapshot isolation | `snapshot isolation` | изоляция снимков | Транзакция читает согласованный snapshot |
| repeatable read | `repeatable read` | повторяемое чтение | Название уровня в стандарте SQL, в базах значит разное |
| snapshot | snapshot | снапшот | Состояние базы на один момент |
| MVCC | MVCC | — | `Multiversion concurrency control`: несколько версий строки |
| read skew / nonrepeatable read | `read skew` / неповторяемое чтение (`nonrepeatable read`) | — | Транзакция видит части базы в разные моменты |
| write skew | `write skew` | перекос записи | Решение по устаревшей предпосылке |
| read-modify-write | `read-modify-write` | — | Цикл «прочитать — изменить — записать» |
| compare-and-set | `compare-and-set` (CAS) | — | Условная запись: только если значение не изменилось |
| optimistic locking | оптимистичная блокировка (`optimistic locking`) | — | Условная запись по номеру версии |
| materializing conflicts | материализация конфликтов | — | Таблица строк-блокировок против `phantom` |
| stored procedure | хранимая процедура (`stored procedure`) | — | Код транзакции целиком внутри базы |
| predicate lock | `predicate lock` (предикатная блокировка) | — | Блокировка по условию поиска |
| index-range lock / next-key locking | `index-range lock` | — | Приближение `predicate lock` по индексу |
| serializable snapshot isolation | SSI | — | Оптимистичная `serializability` поверх `snapshot isolation` |
| contention | конкуренция (`contention`) | — | Много транзакций трогают одни объекты |
| coordinator / participant | координатор / участник | — | Роли в `2PC` |
| in doubt | `in doubt` | в сомнении | Участник сказал «да», но не знает решения |
| commit point | точка фиксации (`commit point`) | — | Решение координатора записано в журнал |
| atomic commitment | атомарный `commit` (`atomic commitment`) | — | Все узлы вместе делают `commit` или `abort` |
| exactly-once | `exactly-once` | ровно-однажды | Эффект ровно один раз, даже при повторах |
| idempotent | идемпотентный | — | Повтор не меняет результат |
| heuristic decision | эвристическое решение (`heuristic decision`) | — | Участник решает сам, рискуя атомарностью |
| garbage collection | сборка мусора (GC) | — | Удаление старых версий строк |
| serialization failure | `serialization failure` | ошибка сериализации | Ошибка базы при нарушении `serializability`; «сериализация» в глоссарии занята под `encoding` |
| partial failure | частичный отказ (`partial failure`) | частичный сбой | Часть системы сломана, остальная работает |
| timeout | `timeout` | — | Сколько ждать ответа, прежде чем считать узел мёртвым |
| network congestion | перегрузка сети | конгестия | Пакеты ждут в очереди коммутатора |
| noisy neighbor | `noisy neighbor` | шумный сосед | Чужая нагрузка на общем железе облака |
| circuit / packet switching | коммутация каналов / коммутация пакетов | — | Телефонная сеть с резервом канала / Ethernet и IP |
| time-of-day clock | `time-of-day clock` | часы времени суток | Часы с датой и временем, могут прыгать назад |
| monotonic clock | `monotonic clock` | монотонные часы | Часы для длительности, только вперёд |
| clock drift | дрейф часов | уход часов | Кварц идёт быстрее или медленнее нужного |
| logical clock | логические часы (`logical clock`) | — | Счётчик для порядка событий без времени суток |
| confidence interval | интервал уверенности | доверительный интервал | Часы дают диапазон `[earliest, latest]`, а не точку |
| process pause | пауза процесса | — | Поток замер: GC, swap, VM, SIGSTOP |
| fencing token | `fencing token` | токен ограждения | Растущий номер lease, хранилище отклоняет старые |
| zombie | зомби | — | Бывший владелец lease, который не знает, что потерял его |
| Byzantine fault | `Byzantine fault` | византийская ошибка | Узел лжёт или ведёт себя произвольно |
| system model | модель системы | системная модель | Допущения алгоритма о времени и отказах |
| safety / liveness | `safety` / `liveness` | безопасность / живучесть | «Плохое не случится» / «хорошее в итоге случится» |
| crash-stop / crash-recovery | `crash-stop` / `crash-recovery` | — | Узел падает навсегда / падает и возвращается |
| deterministic simulation testing | `deterministic simulation testing` (`DST`) | — | Тест реального кода в симуляции с полным контролем порядка |
| model checking | `model checking` | проверка моделей | Перебор состояний спецификации алгоритма |
| consistency | согласованность | консистентность | Насколько реплики показывают одни и те же данные |
| strong consistency | сильная согласованность | — | Система ведёт себя как один узел |
| consensus | консенсус | `consensus` | Узлы договариваются об одном значении и не меняют решение |
| register | регистр (`register`) | — | Один объект: ключ, строка или документ |
| compare-and-set (CAS) | `CAS` | — | Атомарная запись, если текущее значение равно ожидаемому |
| fetch-and-add | `fetch-and-add` | — | Атомарно увеличить счётчик и вернуть старое значение |
| strict serializability | `strict serializability` | строгая сериализуемость | `serializability` плюс `linearizability` |
| Lamport clock / timestamp | часы Лэмпорта / метка Лэмпорта | лампортовы часы | Пара (счётчик, ID узла), порядок согласован с причинностью |
| hybrid logical clock | гибридные логические часы (`HLC`) | — | Физическое время плюс правило часов Лэмпорта |
| timestamp | метка времени | таймстемп | Значение часов, приписанное событию |
| shared log | общий журнал (`shared log`) | общий лог | Журнал, в который просят дописывать многие узлы |
| total order broadcast | `total order broadcast` | — | Все узлы получают все сообщения в одном порядке |
| epoch number | номер эпохи (`epoch`) | — | `term` в Raft, `ballot` в Paxos, `view` в VSR |
| state machine replication | `state machine replication` | — | Реплики применяют одни записи в одном порядке |
| ephemeral node | `ephemeral node` | — | Ключ ZooKeeper, который исчезает с сессией клиента |
| batch processing | пакетная обработка | батч-обработка | Job читает весь неизменяемый вход и заново строит выход |
| batch job | `batch job`, `job` | джоба, батч-джоб | Одна задача пакетной обработки |
| task | `task` | таска | Часть job, которая работает на одном узле |
| stream processing | потоковая обработка | стриминговая обработка | Job не заканчивается и обрабатывает новые данные сразу |
| online / offline system | онлайн-система / офлайн-система | — | Отвечает на запросы сразу / обрабатывает большие объёмы без ожидания клиента |
| human fault tolerance | устойчивость к ошибкам людей (`human fault tolerance`) | — | Ошибку в коде можно исправить откатом и перезапуском |
| time travel | `time travel` | путешествие во времени | Чтение старой версии данных |
| distributed filesystem (DFS) | распределённая файловая система (`DFS`) | — | HDFS, GlusterFS, CephFS |
| object store | объектное хранилище (`object store`) | объектный стор | S3, GCS, Azure Blob Storage |
| bucket | `bucket` | бакет, ведро | Контейнер объектов с глобально уникальным именем |
| data node | `data node` | — | Демон на машине, который хранит блоки DFS |
| erasure coding | `erasure coding` | — | Код (например, Reed–Solomon), который восстанавливает потерянные блоки дешевле полной репликации |
| job orchestrator | оркестратор | — | Kubernetes, YARN: запускают tasks на узлах |
| scheduler | планировщик (`scheduler`) | шедулер | Решает, какая task на каком узле работает |
| resource manager | `resource manager` | — | Знает ресурсы и состояние всех узлов |
| task executor | `executor` | — | Демон на узле: kubelet, NodeManager |
| gang scheduling | `gang scheduling` | — | Все tasks job стартуют только вместе |
| preemption | вытеснение (`preemption`) | преэмпция | Планировщик убивает task, чтобы освободить ресурсы |
| starvation | голодание (`starvation`) | — | Job долго не получает ресурсы |
| spot instance | `spot instance` | — | Дешёвая машина, которую облако может забрать в любой момент |
| mapper / reducer | `mapper` / `reducer` | маппер, редьюсер | Функции map и reduce в MapReduce |
| dataflow engine | `dataflow engine` | — | Spark, Flink: весь workflow — один job |
| sort-merge join | `sort-merge join` | — | Обе стороны сортируют по ключу, reducer сливает их |
| secondary sort | `secondary sort` | вторичная сортировка | Порядок значений внутри одного ключа |
| batch inference | `batch inference` | — | Предсказания модели сразу для большого набора данных |
| bulk load | массовая загрузка (`bulk load`) | — | Готовые файлы базы загружают целиком |
| working set | рабочий набор (`working set`) | — | Данные, к которым job нужен произвольный доступ в памяти |
| stream processor | обработчик потока (`stream processor`) | стрим-процессор | Код или фреймворк, который читает поток и пишет новый поток |
| event | событие (`event`) | ивент | Небольшая неизменяемая запись о том, что случилось |
| bounded / unbounded | ограниченный (`bounded`) / неограниченный (`unbounded`) | — | Вход с известным концом / поток без конца |
| messaging system | система сообщений (`messaging system`) | система обмена сообщениями | В DDIA2 «обмен» в «Не писать» общего глоссария (trade-off) |
| acknowledgment | подтверждение (`ack`) | аск | `Consumer` сообщает брокеру, что обработал сообщение |
| load balancing / fan-out | балансировка нагрузки (`load balancing`) / `fan-out` | — | Сообщение получает один `consumer` / все `consumer` |
| consumer group | `consumer group` | группа потребителей | Группа, которая делит `shard` одного `topic` |
| dead letter queue | `dead letter queue` (`DLQ`) | — | Очередь для сообщений, которые не удаётся обработать |
| log-based message broker | брокер на основе лога | лог-брокер | `Message broker`, который хранит сообщения в логе и не удаляет их при чтении |
| log compaction | `log compaction` | уплотнение лога | Остаётся последнее значение каждого ключа |
| changelog | `changelog` | — | Лог всех изменений состояния |
| outbox pattern | паттерн `outbox` | исходящая таблица | Отдельная таблица для внешних событий в той же транзакции |
| data contract | `data contract` | контракт данных | Договор о схеме между источником и `consumer` |
| complex event processing | `complex event processing` (`CEP`) | — | Поиск шаблонов событий по постоянным запросам |
| incremental view maintenance | `incremental view maintenance` (`IVM`) | — | Пересчёт только изменившихся данных |
| event time / processing time | `event time` / `processing time` | время процессинга | Когда событие произошло / когда его обработали |
| straggler events | опоздавшие события (`straggler events`) | отстающие события | Пришли после закрытия окна |
| window (tumbling, hopping, sliding, session) | окно: `tumbling window`, `hopping window`, `sliding window`, `session window` | — | Типы окон агрегации |
| enrichment | обогащение (`enrichment`) | — | `Stream–table join`: к событию добавляют данные из таблицы |
| stream–stream / stream–table / table–table join | `stream–stream join` / `stream–table join` / `table–table join` | — | Три вида `join` в потоках |
| microbatching | `microbatching` | микробатчинг | Поток режут на пакеты около секунды |
| checkpoint | `checkpoint` | чекпойнт | Периодический снимок состояния оператора |
| effectively-once | `effectively-once` | — | Точнее название для `exactly-once` |
| unbundling (databases) | `unbundling` (разборка базы данных) | разбандлинг | Функции базы делают отдельные инструменты, связанные журналами |
| federated database / polystore | федеративная база данных (`federated database`) | — | Один интерфейс запросов над многими хранилищами |
| dataflow | `dataflow` | датафлоу | Код отвечает на изменения состояния новыми изменениями |
| write path / read path | `write path` / `read path` | путь записи / путь чтения | Работа при записи заранее / работа при запросе |
| exactly-once / at-least-once | `exactly-once` / `at-least-once` | ровно-один-раз | Семантика обработки сообщений |
| request ID | `request ID` | — | Уникальный ID запроса от клиента для подавления дублей |
| timeliness | своевременность (`timeliness`) | актуальность | Пользователь видит свежее состояние; нарушение временное |
| integrity | целостность (`integrity`) | интегральность | Нет потерь и противоречий; нарушение постоянное |
| compensating transaction | компенсирующая транзакция | — | Исправление нарушенного ограничения задним числом |
| coordination-avoiding | без координации (`coordination-avoiding`) | — | Система без синхронной координации, но с целостностью |
| auditing | аудит (`auditing`) | — | Проверка целостности данных |
| Merkle tree | дерево Меркла (`Merkle tree`) | — | Дерево хешей для доказательства, что запись есть в наборе |
| lambda / kappa architecture | `lambda`-архитектура / `kappa`-архитектура | лямбда-архитектура | Два пайплайна / один движок для пакетов и потоков |
| predictive analytics | предиктивная аналитика (`predictive analytics`) | прогнозная аналитика | Прогнозы о людях и событиях на основе данных |
| bias | предвзятость (`bias`) | смещение, байес | Систематический перекос в данных, который модель усиливает |
| feedback loop | петля обратной связи (`feedback loop`) | цикл фидбэка | Прогноз меняет реальность и сам себя подтверждает |
| systems thinking | системное мышление (`systems thinking`) | — | Взгляд на систему целиком, вместе с людьми |
| tracking | `tracking` | трекинг | Запись действий пользователя как побочный эффект |
| surveillance | слежка (`surveillance`) | надзор, сюрвейланс | `Tracking` в интересах тех, кто платит за сервис |
| privacy | приватность | прайваси | Право решать, что раскрыть, кому и что оставить в секрете |
| legitimate interest | законный интерес (`legitimate interest`) | легитимный интерес | Основание GDPR для обработки без согласия |
| data broker | брокер данных (`data broker`) | дата-брокер | Компания, которая скупает и перепродаёт данные о людях |
| data exhaust | `data exhaust` | — | «Выхлоп»: поведенческие данные как побочный продукт |
| echo chamber | эхо-камера | — | Человек видит только близкие ему мнения |
