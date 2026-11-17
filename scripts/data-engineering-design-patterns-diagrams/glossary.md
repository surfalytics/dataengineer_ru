# Глоссарий: Data Engineering Design Patterns (Bartosz Konieczny)

Единые слова для всех глав. Правила: навык `book-summary`, раздел «Glossary first».
Колонка «Как пишем»: термин в обратных кавычках = оставляем английским; обычное слово = пишем по-русски.
Имена паттернов книги (`Full Loader`, `Dead-Letter`) пишем по-английски в обратных кавычках. Русское описание даём при первом упоминании.

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| change data capture | `CDC` (`change data capture`) | — | Читаем лог изменений базы. Паттерн `Change Data Capture` |
| partition | `partition` | — | Часть таблицы по значению ключа, например по дате |
| partitioning | `partitioning` | партицирование | Разбиение таблицы на `partition`. Не путать с `sharding` |
| sharding | `sharding` | шардинг, шардирование | Разбиение данных по узлам. Книга сравнивает его с `partitioning` |
| horizontal partitioning | `horizontal partitioning` | горизонтальное партицирование | Разбиение по строкам. Паттерн `Horizontal Partitioner` |
| vertical partitioning | `vertical partitioning` | вертикальное партицирование | Разбиение по колонкам. Паттерн `Vertical Partitioner` |
| dead-letter | `Dead-Letter` | мёртвое письмо, очередь мёртвых писем | Хранилище записей, которые не удалось обработать |
| transient error | временная ошибка (`transient`) | транзиентная ошибка | Пройдёт при повторе. Противоположность: `nontransient` |
| nontransient error | постоянная ошибка (`nontransient`) | нетранзиентная | Повтор не поможет |
| checkpoint | `checkpoint` | чекпоинт, контрольная точка | Сохранённая позиция обработки. Паттерн `Checkpointer` |
| idempotency | идемпотентность | — | Повторный запуск даёт тот же результат |
| overwrite | перезапись (`overwrite`) | оверрайт | Замена данных новыми. Паттерны `Data Overwrite`, `In-Place Overwriter` |
| backfill | `backfill` | бэкфилл | Перезапуск обработки за прошлые периоды |
| merge / upsert | `MERGE` / `upsert` | апсерт | Вставка или обновление по ключу. Паттерн `Merger` |
| partial commit | `partial commit` | — | Часть записи уже видна, часть нет |
| denormalization | `denormalization` | денормализация без пояснения | Склеивание таблиц в одну. Паттерн `Denormalizer` |
| normalization | `normalization` | нормализация без пояснения | Разнесение данных по таблицам. Паттерн `Normalizer` |
| sessionization | `sessionization` | — | Группировка событий в сессии. Паттерн `Incremental Sessionizer` |
| watermark | `watermark` | водяной знак | Отметка: события старше неё больше не ждём |
| late data | поздние данные (`late data`) | запоздавшие данные | События, пришедшие после watermark |
| event time / processing time | `event time` / `processing time` | время события / время обработки без `event time | Когда событие случилось и когда его обработали |
| fan-in / fan-out | `fan-in` / `fan-out` | веер, разветвление | Слияние нескольких потоков в один и разделение одного на несколько |
| at-least-once / at-most-once / exactly-once | `at-least-once` / `at-most-once` / `exactly-once` | ровно-один-раз | Гарантии доставки |
| state store | `state store` | — | Где `stateful`-job держит состояние |
| anonymization | анонимизация (`anonymization`) | — | Данные нельзя связать с человеком. Паттерн `Anonymizer` |
| pseudo-anonymization | псевдоанонимизация (`pseudo-anonymization`) | — | Связь с человеком можно восстановить. Паттерн `Pseudo-Anonymizer` |
| fine-grained access | точечный доступ (`fine-grained access`) | тонкий доступ | Права на строки и колонки. Паттерн `Fine-Grained Accessor for Tables` |
| clustering | `clustering` | кластеризация | Физическая сортировка данных по ключу. Не путать с ML |
| skew | `skew` | скос | Неравномерное распределение данных |
| bucket pruning / partition pruning | `pruning` | отсечение | Движок пропускает ненужные части данных |
| deletion vector | `deletion vector` | — | Метка удаления строки внутри файла |
| slowly changing dimension | `SCD` | — | Измерение, которое меняется со временем |
| schema evolution | `schema evolution` | — | Схема меняется со временем |
| backward / forward compatibility | `backward` / `forward` compatibility | обратная / прямая совместимость | Новая схема читает старые данные / старая читает новые |
| constraint | ограничение (`constraint`) | констрейнт | Правило на колонку: тип, `NOT NULL` |
| lag | лаг (`lag`) | — | Насколько обработка отстаёт от источника |
| data lineage | `lineage` | линидж | Путь данных от источника к набору. Паттерн `Fine-Grained Tracker` |
