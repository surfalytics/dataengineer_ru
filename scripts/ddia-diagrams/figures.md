# Рисунки книги DDIA (2-е издание) и наши схемы

Статус: `redrawn` — перерисован по-нашему; `own` — наша схема; `skipped: причина`.
Исходники схем: `scripts/ddia-diagrams/chNN_diagrams.py`, рисует `excb.py`.

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 0 | — (наша) | Карта книги: 3 части, 14 глав | ch00-book-map.png | own |
| 1 | Figure 1-1 | ETL из OLTP-систем в хранилище данных | ch01-operational-analytical.png | redrawn (дополнено data lake и reverse ETL, главная схема главы) |
| 1 | Figure 1-2 | Спектр: своё ПО, self-hosting, облачный сервис | ch01-build-vs-buy.png | redrawn |
| 1 | — (наша) | System of record и производные данные | — | skipped: та же идея, что ch13-derived-data.png; в главе 1 ссылка на главу 13 |
| 1 | — (наша) | Разделение хранения и вычислений | ch01-storage-compute.png | own |
| 1 | Table 1-1, 1-2 | Сравнение OLTP/OLAP; self-hosted и cloud native системы | на странице | пересобраны своими таблицами |
| 2 | 2-1 | Реляционная схема соцсети: users, posts, follows | — | skipped: таблицы описаны в тексте и созданы в SQL-примере «Код из главы» |
| 2 | 2-2 | Fan-out: пост доставляется в ленту каждого подписчика | ch02-fanout.png | redrawn: старая картинка 1-го издания (твиты, load parameter) перерисована под 2-е издание; добавлен путь для знаменитостей и расчёт 400 млн против 1,16 млн |
| 2 | 2-3 | Время ответа резко растёт, когда throughput подходит к пределу | — | skipped: график; идея очередей пересказана в тексте |
| 2 | 2-4 | Response time, service time, network latency, queueing delay | ch02-response-time.png | redrawn |
| 2 | 2-5 | Среднее и перцентили на выборке из 100 запросов | ch02-percentiles.png | reused: картинка 1-го издания, термины совпадают с глоссарием |
| 2 | 2-6 | Один медленный backend-вызов замедляет весь запрос | ch02-percentiles.png | reused: tail latency amplification показан в той же картинке |
| 2 | — (наша) | Три источника сбоев и меры против них | ch02-faults.png | redrawn: старая картинка 1-го издания (sandbox, telemetry) перерисована по 2-му изданию |
| 3 | — (наш) | Выбор модели по типу связей | ch03-model-choice.png | reused (1-е издание, без исходника) |
| 3 | — (наш) | История конкурентов реляционной модели | ch03-history.png | redrawn: старая картинка показывала историю 1-го издания (IMS, CODASYL); исходник в ch03_diagrams.py |
| 3 | 3-1 | Резюме в реляционной схеме | — | skipped: показано JSON-примером и текстом |
| 3 | 3-2 | Связи one-to-many как дерево | — | skipped: дерево видно в JSON-примере |
| 3 | 3-3 | Many-to-many в реляционной модели | — | skipped: простая связующая таблица, описана текстом |
| 3 | 3-4 | Many-to-many в документной модели | — | skipped: показано JSON-примером со ссылками org_id |
| 3 | 3-5 | Star schema продуктовой сети | — | skipped: ER-схема подробно нарисована в конспекте The Data Warehouse Toolkit, на неё ссылка |
| 3 | 3-6 | Граф Lucy и Alain | ch03-graph-example.png | redrawn (упрощён: без промежуточных регионов) |
| 3 | 3-7 | Вывод правил Datalog | — | skipped: шаги перечислены нумерованным списком |
| 3 | — (наш) | Графовые модели и языки | ch03-graph-models.png | reused (1-е издание, без исходника) |
| 3 | 3-8 | Event sourcing и CQRS | ch03-event-sourcing.png | redrawn |
| 3 | 3-9 | Таблица оценок в матрицу | — | skipped: показано PIVOT в практике DuckDB |
| 4 | 4-1 | Лог пар с хеш-таблицей смещений в памяти | — | skipped: просто объяснено текстом |
| 4 | 4-2 | SSTable с разреженным индексом | ch04-lsm-tree.png | redrawn (объединён в схему LSM: путь чтения, sparse index) |
| 4 | 4-3 | Слияние сегментов SSTable | ch04-lsm-tree.png | redrawn (объединён: compaction) |
| 4 | 4-4 | Bloom filter | ch04-lsm-tree.png | redrawn (объединён: проверка Bloom filter в пути чтения); биты показаны в тексте |
| 4 | 4-5 | Поиск ключа 251 в B-tree | ch04-btree.png | redrawn (новый файл) |
| 4 | 4-6 | Деление страницы B-tree на границе 337 | ch04-btree.png | redrawn (новый файл) |
| 4 | — | Сравнение B-tree и LSM-tree (раздел без рисунка) | ch04-btree-vs-lsm.png | reused, redrawn: в старой картинке были пункты 1-го издания (блокировки диапазонов) |
| 4 | 4-7 | Строчное и колоночное хранение | ch04-oltp-olap-columnar.png | reused, redrawn: старая картинка показывала поток OLTP → ETL → warehouse из 1-го издания |
| 4 | 4-8 | Bitmap encoding и run-length encoding колонки | — | skipped: показано в «Практика в DuckDB» (задания 2 и 3) |
| 4 | 4-9 | Побитовое AND двух карт | — | skipped: показано в «Практика в DuckDB» (задание 2) |
| 4 | 4-10 | Два измерения data cube | — | skipped: объяснено текстом |
| 4 | 4-11 | Поиск в HNSW | — | skipped: объяснено в таблице векторных индексов |
| 5 | 5-1 | Старый код читает запись нового кода, перезаписывает её и теряет новое поле | ch05-unknown-field.png | redrawn |
| 5 | 5-2 | Байты записи в MessagePack | — | skipped: байтовая раскладка пересказана текстом, размеры в таблице и в выводе `ch05_encodings.py` |
| 5 | 5-3 | Байты записи в Protocol Buffers | — | skipped: то же, таблица размеров и `varint` в коде |
| 5 | 5-4 | Байты записи в Avro | — | skipped: то же, вывод `ch05_encodings.py` |
| 5 | 5-5 | Protobuf: одна схема при декодировании; Avro: схема писателя и схема читателя | ch05-avro-resolution.png | reused (1st edition, без исходника) |
| 5 | 5-6 | Avro сопоставляет поля писателя и читателя по имени | ch05-avro-resolution.png | reused (1st edition, без исходника) |
| 5 | 5-7 | Платёжный `workflow` в BPMN: мошенничество, карта, банк | — | skipped: цепочка из трёх шагов понятна из текста; лимит 3-4 схемы на главу |
| 5 | наша | `Backward` и `forward compatibility` при `rolling upgrade` | ch05-compatibility.png | reused (1st edition, без исходника) |
| 5 | наша | Четыре пути данных: база, сервисы, `workflow engine`, `message broker` | ch05-data-flow.png | redrawn (в 1st edition было три пути и «брокер сообщений») |
| 6 | 6-1, 6-6 | Один leader и follower; leader в каждом регионе | ch06-replication-models.png | reused: redrawn (старые подписи «фолловеры», «датацентр», «Нужны конфликты»); источник ch06_diagrams.py |
| 6 | 6-2 | Синхронный и асинхронный follower | — | skipped: в тексте таблица режимов |
| 6 | 6-3, 6-4, 6-5 | Аномалии лага: read-after-write, monotonic reads, consistent prefix | ch06-replication-lag.png | reused: redrawn (старая подпись «партиция» вместо shard) |
| 6 | 6-7 | Топологии circular, star, all-to-all | — | skipped: три простые формы описаны списком |
| 6 | 6-8 | Записи приходят не в том порядке | — | skipped: пример в тексте |
| 6 | 6-9 | Конфликт записи на двух leader | — | skipped: пример в тексте |
| 6 | 6-10 | Аномалия корзины Amazon | — | skipped: пример в тексте |
| 6 | 6-11 | OT и CRDT сливают вставки в ice | ch06-ot-crdt.png | redrawn (новый) |
| 6 | 6-12, 6-13 | Кворумная запись и чтение, read repair, w + r > n | ch06-quorum-conflicts.png | reused: redrawn (старая схема про sloppy quorum и version vectors не совпадала с 2-м изданием) |
| 6 | 6-14 | Параллельные записи в Dynamo-style | — | skipped: пример списком в тексте |
| 6 | 6-15, 6-16 | Корзина с номерами версий и граф причинности | — | skipped: показано скриптом scripts/ddia-code/ch06_cart_versions.py и его выводом |
| 7 | 7-1 | Узел — `leader` для одних `shard` и `follower` для других | — | skipped: идея простая, описана в тексте; репликация — тема главы 6 |
| 7 | 7-2 | Энциклопедия: `sharding` по диапазону ключей | ch07-partitioning-schemes.png | reused, redrawn (старые подписи «партиция»): левая колонка |
| 7 | 7-3 | `hash mod N`: при смене N переезжает почти всё | ch07-fixed-shards.png | redrawn (новый файл): левая колонка, цифры из ch07_rebalance.py |
| 7 | 7-4 | Новый узел забирает целые `shard` | ch07-fixed-shards.png | redrawn (новый файл): правая колонка |
| 7 | 7-5 | Диапазоны хешей по `shard` | ch07-partitioning-schemes.png | reused, redrawn: правая колонка |
| 7 | 7-6 | Cassandra/ScyllaDB: случайные границы диапазонов хешей | — | skipped: вариант 7-5, описан в тексте |
| 7 | 7-7 | Три способа маршрутизации запроса | ch07-rebalancing-routing.png | reused, redrawn (старая версия смешивала стратегии 1-го издания и «партиции») |
| 7 | 7-8 | ZooKeeper хранит карту `shard` → узел | ch07-rebalancing-routing.png | reused, redrawn: сервис координации справа |
| 7 | 7-9 | Local secondary index | ch07-secondary-indexes.png | reused, redrawn (старые подписи «партиция») |
| 7 | 7-10 | Global secondary index, поделённый по term | ch07-secondary-indexes.png | reused, redrawn |
| 8 | Table 8-1 (+ наш) | Какие аномалии предотвращает каждый уровень изоляции | ch08-isolation-levels.png | reused: redrawn (добавлен read uncommitted, убрано неверное «в MySQL snapshot isolation = repeatable read»); главная схема главы |
| 8 | 8-1 | Гонка двух инкрементов счётчика: 42 → 43 вместо 44 | — | skipped: пример пересказан текстом, атомарный `UPDATE` проверен в DuckDB на странице |
| 8 | 8-2 | `Dirty read`: письмо видно, счётчик ещё 0 | — | skipped: пример пересказан текстом |
| 8 | 8-3 | Атомарность: ошибка в счётчике откатывает вставку письма | — | skipped: пример пересказан текстом |
| 8 | 8-4 | Нет `dirty read`: x = 2 до commit | — | skipped: одна фраза в тексте |
| 8 | 8-5 | `Dirty write`: машина у Bryce, счёт у Aaliyah | — | skipped: пример пересказан текстом |
| 8 | 8-6 | `Read skew`: Aaliyah видит $900 вместо $1000 | — | skipped: пример с числами в тексте |
| 8 | 8-7 | MVCC: версии строк с `inserted_by` / `deleted_by` | — | skipped: показано таблицей версий в «Практике в DuckDB» (задания 1–2) |
| 8 | 8-8 | `Write skew`: два врача уходят с дежурства | ch08-write-skew.png | reused: redrawn (имена 2-го издания Aaliyah и Bryce вместо Alice и Bob) |
| 8 | 8-9 | Интерактивная транзакция против хранимой процедуры | — | skipped: одна фраза в тексте |
| 8 | 8-10 | SSI: чтение устаревшей версии MVCC | — | skipped: пересказано текстом на примере транзакций 42 и 43 |
| 8 | 8-11 | SSI: запись меняет уже прочитанное | — | skipped: пересказано текстом |
| 8 | — (наш) | Три способа получить `serializability` и их цена | ch08-serializable-options.png | reused: redrawn (было «один partition» — нарушало глоссарий; добавлен SSI в PostgreSQL, CockroachDB) |
| 8 | 8-12 | `Commit` прошёл на одном узле и не прошёл на другом | — | skipped: пересказано текстом |
| 8 | 8-13, 8-14 | Успешный `2PC`; сбой координатора после «да» | ch08-two-phase-commit.png | redrawn (новая схема; две точки невозврата и `in doubt` в подписи) |
| 9 | 9-1 | Нет ответа: запрос потерян, узел упал или ответ потерян | ch09-lost-request.png | reused (1st edition, без исходника) |
| 9 | 9-2 | Очередь коммутатора: порты 1, 2, 4 шлют на порт 3 | — | skipped: текст о перегрузке сети понятен без схемы |
| 9 | 9-3 | LWW теряет инкремент из-за разницы часов | ch09-lww-clock-skew.png | redrawn |
| 9 | 9-4 | Клиент на паузе пишет с истёкшим lease | ch09-fencing-token.png | redrawn (вместе с 9-6, имя файла старое) |
| 9 | 9-5 | Задержанный запрос бывшего владельца lease | ch09-fencing-token.png | skipped: та же идея, что 9-4, объяснена текстом |
| 9 | 9-6 | Хранилище принимает записи только с растущим fencing token | ch09-fencing-token.png | redrawn (раньше reused, добавлены стрелки) |
| 9 | 9-7 | Fencing token в старших цифрах timestamp у leaderless-хранилища | ch09-fencing-replicas.png | redrawn |
| 9 | наша | Какие часы для какой задачи | ch09-clocks.png | reused (1st edition, без исходника) |
| 10 | — | Eventual consistency, слабые модели, linearizability | ch10-consistency-levels.png | reused, redrawn: старая версия показывала causal consistency из 1-го издания |
| 10 | 10-1 | Спортивный сайт: Брайс видит старый счёт после Алии | — | skipped: пример короткий, объяснён текстом |
| 10 | 10-2 | Чтение, одновременное с записью, вернёт старое или новое | — | skipped: временная диаграмма, объяснена списком |
| 10 | 10-3 | После первого чтения нового значения все следующие видят его | — | skipped: объяснено текстом |
| 10 | 10-4 | Точки, в которых операции вступают в силу; последнее чтение B не linearizable | — | skipped: сложная временная диаграмма, разобрана списком |
| 10 | 10-5 | Веб-сервер и транскодер общаются через хранилище и очередь | ch10-cross-channel.png | redrawn |
| 10 | 10-6 | Кворум не спасает от нарушения linearizability | — | skipped: пример разобран текстом |
| 10 | 10-7 | Разрыв сети между регионами: выбор между linearizability и доступностью | — | skipped: объяснено текстом |
| 10 | 10-8 | Чат с автоинкрементными ID сообщений | — | skipped: объяснено текстом, продолжение на 10-9 |
| 10 | 10-9 | Метки Лэмпорта в чате | ch10-lamport-clock.png | redrawn |
| 10 | 10-10 | Фото видно постороннему из-за генератора ID без linearizability | — | skipped: сценарий разобран по шагам в тексте |
| 10 | — | Задачи, эквивалентные консенсусу | ch10-consensus-equivalence.png | reused, redrawn: старая версия связывала задачи цепочкой, нет fetch-and-add |
| 10 | — | 2PC и голосование в консенсусе | ch10-two-phase-commit.png | reused, redrawn: механика 2PC теперь в главе 8, здесь сравнение с консенсусом |
| 11 | — | Распределённый batch-фреймворк похож на ОС: файловая система, планировщик, программы | ch11-os-analogy.png | redrawn: новая схема по тексту раздела «Batch Processing in Distributed Systems» |
| 11 | 11-1 | MapReduce job: три mapper, три reducer, файлы shuffle (m, r) | ch11-mapreduce.png | reused, redrawn: старая версия писала «партиции» и не показывала файлы по reducer |
| 11 | 11-2, 11-3 | Join событий активности и профилей пользователей: sort-merge join по user_id | ch11-joins.png | reused, redrawn: старая версия показывала broadcast и partitioned hash join из 1-го издания |
| 11 | — | MapReduce workflow через DFS и dataflow engine с операторами в одном job | ch11-dataflow.png | reused, redrawn: у старой версии была стрелка без смысла (HDFS -> оператор) |
| 12 | 12-1 | Load balancing и fan-out между consumer | ch12-brokers.png | redrawn: картинка 1-го издания перерисована под тем же именем (shard вместо partition, consumer group A и B, fan-out и балансировка) |
| 12 | 12-2 | Повторная доставка меняет порядок m3 и m4 | — | skipped: пример m3/m4 рассказан в тексте |
| 12 | 12-3 | Topic из shard, producer дописывают, consumer читают по offset | ch12-brokers.png | redrawn (нижняя часть той же схемы) |
| 12 | 12-4 | Гонка при dual writes: база и индекс получают записи в разном порядке | ch12-cdc-vs-dual-writes.png | reused (картинка 1-го издания, исходника нет) |
| 12 | 12-5 | CDC: изменения идут из базы в индекс в том же порядке | ch12-cdc-vs-dual-writes.png | reused |
| 12 | 12-6 | Log compaction: остаётся последнее значение каждого ключа | ch12-log-compaction.png | redrawn: наши данные (цены milk, tea, coffee и tombstone), те же данные в задании 3 DuckDB |
| 12 | 12-7 | Состояние — интеграл потока, поток — производная состояния | — | skipped: аналогия объяснена одним предложением |
| 12 | 12-8 | Окна по processing time дают ложный всплеск | — | skipped: эффект показан в задании 1 DuckDB (6 запросов в минуту против 0, 0, 18) |
| 12 | — | Время в потоках, типы окон, exactly-once | ch12-time-windows.png | reused (картинка 1-го издания, исходника нет; подписи совпадают с глоссарием) |
| 13 | — (своя, главная) | Одна база-источник, CDC-журнал с единым порядком, производные системы | ch13-derived-data.png | redrawn (own) |
| 13 | 13-1 | В поисковом индексе встречаются write path и read path; сдвиг границы | ch13-write-read-path.png | redrawn |
| 13 | — (своя) | Курс валют: запрос к микросервису против подписки на поток | ch13-rate-dataflow.png | redrawn (own) |
| 13 | 13-2 | Перевод денег с комиссией через журналы с sharding и потоковые процессоры | ch13-payment-flow.png | redrawn |
| 14 | — (наша) | Карта главы: решения о людях и сбор данных, риски, что делать инженеру | ch14-chapter-map.png | own |
| 14 | — (наша) | Петля обратной связи: кредитный рейтинг и найм | ch14-feedback-loop.png | own |
| 14 | — (наша) | Сервис против слежки: кто клиент | ch14-service-vs-surveillance.png | own |

## Заметки

- Глава 8: Исходники: `scripts/ddia-diagrams/ch08_diagrams.py`.
- Глава 14: В главе 14 нет рисунков книги. Все схемы наши.
