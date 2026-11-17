# Глоссарий: Fundamentals of Data Engineering (Joe Reis, Matt Housley)

Единые слова для всех глав. Правила: навык `book-summary`, раздел «Glossary first».
Колонка «Как пишем»: термин в обратных кавычках = оставляем английским; обычное слово = пишем по-русски.

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| data engineering | инжиниринг данных (`data engineering`) | дата-инжиниринг, инженерия данных | Работа по сбору, хранению, обработке и выдаче данных |
| data engineer | дата-инженер | инженер данных, датаинженер | Строит и поддерживает системы данных |
| data engineering lifecycle | `data engineering lifecycle` (жизненный цикл инжиниринга данных) | — | Пять стадий: generation, storage, ingestion, transformation, serving |
| undercurrents | `undercurrents` | подводные течения | Шесть сквозных тем цикла: security, data management, DataOps, data architecture, orchestration, software engineering |
| generation | `generation` (порождение данных) | — | Стадия, где источник создаёт данные |
| ingestion | `ingestion` | — | Стадия, где данные забирают из источника |
| transformation | `transformation` (преобразование) | — | Стадия, где данные превращают в полезный вид |
| serving | `serving` (выдача данных) | подача, сервинг | Стадия, где данные получают аналитика, ML и приложения |
| source system | система-источник (`source system`) | исходная система | Система, которая порождает данные |
| data pipeline | `pipeline` | пайплайн | Цепочка шагов, которая двигает и меняет данные |
| scalability | масштабируемость | скалируемость | Способность системы расти вместе с нагрузкой |
| data warehouse | хранилище данных (`data warehouse`) | склад данных | Центральная система для аналитики |
| data lake | `data lake` | озеро данных | Большое хранилище сырых данных любого формата |
| data lakehouse | `lakehouse` | озерохранилище | Файлы озера плюс таблицы и транзакции хранилища |
| data mesh | `data mesh` | — | Подход: данными владеют доменные команды |
| lambda / kappa architecture | `lambda`-архитектура / `kappa`-архитектура | лямбда-архитектура | Два пути обработки / один потоковый путь |
| event-driven architecture | архитектура на событиях (`event-driven`) | событийно-ориентированная | Системы обмениваются событиями |
| on premises | `on premises` | — | Свои серверы в своём дата-центре |
| vendor lock-in | `vendor lock-in` | — | Зависимость от одного поставщика |
| total cost of ownership | `total cost of ownership` (`TCO`) | общая стоимость владения без пояснения | Все прямые и косвенные расходы на систему |
| build versus buy | `build` или `buy` (строить или покупать) | — | Выбор: писать своё или брать готовое |
| DataOps | `DataOps` | — | Идеи DevOps для данных: автоматизация, мониторинг, реакция на инциденты |
| data governance | `data governance` | — |  Качество, безопасность и доступ к данным |
| data lineage | `lineage` | линидж | Путь данных от источника к потребителю |
| master data management | `MDM` (`master data management`) | — | Единый справочник ключевых сущностей |
| data modeling | моделирование данных | — | Описание, как данные хранятся и связаны |
| orchestration | `orchestration` | — | Запуск задач по расписанию и зависимостям |
| zero-trust security | `zero-trust` | нулевое доверие | Нет доверенной сети: проверяют каждый запрос |
| OLTP / OLAP | `OLTP` / `OLAP` | — | Транзакции против аналитических запросов |
| CAP theorem | теорема `CAP` | — | Согласованность, доступность, устойчивость к разрыву сети: все три сразу нельзя |
| change data capture | `CDC` (`change data capture`) | захват изменений | Передача изменений базы во внешние системы |
| webhook | `webhook` | вебхук | Источник сам вызывает ваш адрес при событии |
| producer / consumer | `producer` / `consumer` | продюсер / консьюмер | Тот, кто пишет, и тот, кто читает |
| topic | `topic` | топик | Именованный поток сообщений |
| partition | `partition` | — | Часть topic или таблицы для параллельной работы |
| shard | `shard` | шард | Часть данных на одном узле |
| eventual consistency | `eventual consistency` | согласованность в конечном счёте | Копии сойдутся позже |
| batch / stream | пакетная / потоковая обработка (`batch` / `stream`) | — | Порциями или по одной записи |
| backfill | `backfill` | бэкфилл | Догрузка данных за прошлый период |
| idempotency | идемпотентность | — | Повторный запуск не меняет результат |
| exactly-once / at-least-once | `exactly-once` / `at-least-once` | ровно-один-раз | Гарантии доставки |
| backpressure | `backpressure` | обратное давление | Приёмник просит источник замедлиться |
| schema evolution | `schema evolution` | эволюция схемы | Схема меняется со временем |
| schema drift | `schema drift` | дрейф схемы | Схема меняется без предупреждения |
| ETL / ELT | `ETL` / `ELT` | — | Порядок: transform до load или после |
| reverse ETL | `reverse ETL` | обратный ETL | Возврат данных из хранилища в системы-источники |
| object storage | объектное хранилище (`object storage`) | — | Хранение объектов по ключу (S3) |
| hot / warm / cold data | `hot` / `warm` / `cold` data | — | Как часто к данным обращаются |
| columnar storage | колоночное хранение (`columnar`) | столбцовое хранение | Значения колонки лежат рядом |
| semantic layer | `semantic layer` | семантический слой | Единые определения метрик |
| data swamp | `data swamp` | болото данных | Озеро, где ничего не найти |
| data product | `data product` | — | Набор данных, которым управляют как продуктом |
| data observability | `data observability` | — | Видно, что с данными происходит |
| infrastructure as code | `infrastructure as code` (`IaC`) | инфраструктура как код без пояснения | Инфраструктуру описывают кодом |
| FinOps | `FinOps` | — | Управление расходами на облако |
| data catalog | каталог данных (`data catalog`) | — | Описание наборов данных: владелец, схема, смысл |
| metadata | метаданные | — | Данные о данных: схема, владелец, время обновления |
| data mart | `data mart` | витрина данных | Небольшой набор данных под одну тему или команду |
| data vault | `Data Vault` | — | Моделирование через hub, link, satellite |
| serverless | `serverless` | бессерверный | Сервис без управления серверами: платите за вызовы |
| multitenancy | `multitenancy` | мультиарендность | Много клиентов делят одну систему и изолированы друг от друга |
| push / pull / poll | `push` / `pull` / `poll` | пуш, пулл, поллинг | Источник отправляет / ingestion забирает / забирает по кругу |
| undifferentiated heavy lifting | `undifferentiated heavy lifting` | недифференцированная тяжёлая работа | Рутина, которая не даёт конкурентного преимущества: её отдают облаку |
| lift and shift | `lift and shift` | — | Перенос системы в облако без переделки |
| technical debt | технический долг | — | Быстрые решения сейчас, которые дорого обойдутся позже |
| data sharing | `data sharing` | шеринг данных | Доступ к данным другой организации без копирования |
| operational analytics | `operational analytics` | операционная аналитика | Аналитика в реальном времени для текущих решений |
| embedded analytics | `embedded analytics` | встроенная аналитика | Аналитика внутри продукта для клиентов |
| data wrangling | `data wrangling` | — | Ручная очистка и подготовка данных |
| dark data | `dark data` | тёмные данные | Данные, которые собирают, но не используют |
| data fabric | `data fabric` | — | Единый слой доступа к разрозненным данным через metadata и автоматизацию |
| data cascade | `data cascade` | каскад данных | Ошибка в данных ломает всё, что стоит дальше по цепочке |
| query optimizer | `query optimizer` | оптимизатор запросов | Часть базы, которая выбирает самый дешёвый план запроса |
| explain plan | `explain plan` | — | План выполнения запроса |
| row explosion | `row explosion` | — | Рост числа строк из-за повторов в ключах join |
| pruning | `pruning` | — | Чтение только нужных колонок и партиций |
| vacuum | `vacuum` | — | Удаление старых версий записей |
| grain | `grain` | — | Уровень детализации строки |
| normalization | `normalization` | нормализация без пояснения | Устранение дублирования через нормальные формы |
| SCD | `SCD` | — | Slowly changing dimension |
| conformed dimension | `conformed dimension` | — | Dimension, общий для нескольких star schemas |
| star schema | `star schema` | звёздная схема | Fact-таблица, окружённая dimensions |
| window / watermark | окно (`window`) / `watermark` | — | Окна в streaming и порог для поздних данных |
| copy on write | `copy on write` (`COW`) | — | Изменение файла через его полную перезапись |
| materialized view | `materialized view` | — | View с заранее посчитанным результатом |
| data virtualization | `data virtualization` | — | Запросы к внешним источникам без своего хранилища |
| metrics layer | `metrics layer` | — | Слой с определениями бизнес-метрик |
| derived data | `derived data` | — | Данные, вычисленные из других данных |
| micro-batch / true streaming | `micro-batch` / `true streaming` | — | Пачки каждые 1 с или 2 мин / по одному событию |
| партиция | партиция | — | Часть таблицы (форма уже принята на страницах) |
| trust | доверие | — | Главное условие выдачи данных |
| SLA / SLO | `SLA` / `SLO` | — | Обещание потребителю / способ измерить его выполнение |
| jobs to be done | `jobs to be done` | — | Работа, ради которой пользователь «нанимает» продукт |
| self-service | self-service | самообслуживание | Пользователь сам строит отчёты и модели |
| data definition / data logic | `data definition` / `data logic` | — | Смысл данных в компании / формулы метрик |
| tribal knowledge | `tribal knowledge` | — | Знания, которые передают устно |
| business analytics | business analytics | бизнес-аналитика | Аналитика для решений по трендам |
| query pushdown | `query pushdown` | — | BI генерирует SQL и выполняет его в базе |
| query federation | `query federation` | федерация запросов | Один запрос к нескольким системам |
| featurization | `featurization` | — | Превращение данных в признаки для ML |
| data obfuscation | `data obfuscation` | — | Синтетические, перемешанные или обезличенные данные |
| least privilege | `least privilege` | — | Минимально нужный доступ |
| credentials | credentials | — | Пароли, ключи, токены |
| notebook | notebook | ноутбук (как термин) | Jupyter и подобные |
| bidirectional load and transform | `BLT` | — | Шутливое название reverse ETL |
| security theater | `security theater` | театр безопасности | Формальное соблюдение требований без реальной защиты |
| security habit | `security habit` (привычка к безопасности) | — | Простые правила, которые выполняют каждый день |
| active security | `active security` | активная безопасность | Поиск угроз под вашу организацию |
| shared responsibility | `shared responsibility` | разделённая ответственность | Облако защищает дата-центр, вы защищаете свои системы |
| broken glass | `broken glass` | — | Экстренный доступ с согласованием, закрывается сразу после работы |
| PII | `PII` | — | Персональные данные |
| IAM role | `IAM role` | — | Набор прав в облаке |
| service account | `service account` | — | Учётная запись для программы, не для человека |
| SSO | `SSO` | — | Единый вход |
| multifactor authentication | `multifactor authentication` | многофакторная аутентификация | Второй фактор кроме пароля |
| secrets manager | `secrets manager` | — | Сервис для хранения паролей и ключей |
| phishing | `phishing` | — | Обман, чтобы выманить credentials |
| ransomware | `ransomware` | — | Вирус, который блокирует данные ради выкупа |
| encryption at rest / over the wire | `encryption at rest` / `encryption over the wire` | — | Шифрование на диске / при передаче |
| air gap | `air gap` | — | Полная изоляция от сетей |
| man-in-the-middle | `man-in-the-middle` | — | Атакующий перехватывает и меняет трафик |
| anomaly detection | `anomaly detection` | — | Автоматический поиск необычных событий |
| modern data stack | `modern data stack` (`MDS`) | современный стек данных | Cloud warehouse, ELT, SaaS-pipeline, BI |
| live data stack | `live data stack` | живой стек | Стек на streaming и real-time OLAP внутри приложений |
| STL | `STL` (stream, transform, load) | — | Преобразование в потоке |
| real-time OLAP | `real-time OLAP` | — | База с быстрой загрузкой и запросами за доли секунды |
| feature store | `feature store` | — | Хранилище признаков для ML |
| enterprisey | `enterprisey` | — | Хорошие практики больших компаний: governance, DataOps |
| dark matter data | `dark matter data` | — | Данные в таблицах вне основных систем |
| bounded / unbounded data | `bounded` / `unbounded` | — | Данные с концом / бесконечный поток |
| cloud-scale data OS | cloud-scale data OS | — | Облачные сервисы как слой операционной системы |
