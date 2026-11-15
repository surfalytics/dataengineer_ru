# Глоссарий: Data Pipelines with Apache Airflow, Second Edition

Одна форма на термин. Термин в обратных кавычках остаётся английским.

| English | Как пишем | Не писать | Пояснение |
|---|---|---|---|
| DAG | `DAG` | даг, ДАГ | Directed acyclic graph: граф tasks без циклов |
| task | `task` | задача (в тексте про Airflow), таск | Один шаг pipeline, узел графа |
| upstream / downstream | `upstream` / `downstream` | апстрим, даунстрим | Задачи до данной и после неё |
| deadlock | `deadlock` | дедлок | Задачи ждут друг друга, обе стоят |
| DAG file | `DAG file` | даг-файл | Python-файл с описанием DAG |
| DAG processor | `DAG processor` | — | Парсит DAG-файлы, пишет в metastore |
| scheduler | `scheduler` | планировщик | Решает, когда и что запускать |
| worker | `worker` | воркер | Выполняет tasks |
| triggerer | `triggerer` | — | Ждёт внешние события для deferred tasks |
| API server | `API server` | — | Веб-интерфейс и шлюз к metastore |
| metastore | `metastore` | метастор, база метаданных (вместо термина) | База метаданных Airflow |
| provider | `provider` | — | Пакет интеграции с внешней системой |
| schedule interval | `schedule interval` | — | Интервал, по которому идут runs |
| incremental pipeline | `incremental pipeline` | — | Run обрабатывает только delta своего интервала |
| backfilling | `backfilling` | бэкфилл, бэкфиллинг | Запуск DAG за прошлые интервалы |
| workflow manager | `workflow manager` | — | Инструмент для запуска графов задач |
| operator | operator | оператор (кириллицей) | не переводим |
| context manager | context manager | — | блок `with DAG(...)` |
| dependency | зависимость | — |  |
| task instance | task instance | экземпляр задачи |  |
| upstream_failed | `upstream_failed` | — | статус |
| clear | `clear` | — | сброс состояния task |
| graph view / grid view | graph view / grid view | — | не переводим |
| DAG versioning | DAG versioning | — | Airflow 3 |
| DAG bundle | DAG bundle | — |  |
| trigger-based schedule | `trigger timetable` | — | Расписание по точкам времени: run сразу после точки |
| data-interval-based schedule | `data interval timetable` | — | Расписание по интервалам: run в конце интервала |
| logical_date | `logical_date` | — | Время, за которое идёт run |
| data_interval_start / end | `data_interval_start/end` | — | Границы интервала данных run |
| partition | `partition` | партиция (для интервала run) | Кусок набора данных, обычно по дате |
| catchup | `catchup` | катчап | Запускать ли пропущенные точки из прошлого |
| atomicity | `atomicity` (атомарность) | — | Task даёт результат целиком или не меняет систему |
| idempotency | `idempotency` (идемпотентность) | идемпотентность без `idempotency` при первом упоминании | Повтор с теми же входами не меняет результат |
| timetable | `timetable` | — | Класс правила расписания |
| asset | `asset` | ассет, датасет (в Airflow 3) | Виртуальная ссылка на данные с URI |
| outlets | `outlets` | — | Параметр задачи: какие assets она обновляет |
| asset event | `asset event` | — | Событие "asset обновлён" |
| producer / consumer DAG | producer / consumer DAG | — | DAG, который создаёт asset / запускается по нему |
| triggering_asset_events | `triggering_asset_events` | — | Контекст: события, запустившие DAG |
| context | `context` | — | Словарь переменных запуска задачи |
| Jinja | `Jinja` | — | Шаблонизатор, синтаксис `{{ ... }}` |
| template_fields | `template_fields` | — | Аргументы оператора, которые шаблонизируются |
| template_ext | `template_ext` | — | Расширения файлов, которые оператор шаблонизирует |
| template_searchpath | `template_searchpath` | — | Папки для поиска файлов-шаблонов |
| op_args / op_kwargs | `op_args` / `op_kwargs` | — | Свои аргументы для функции PythonOperator |
| pendulum | `pendulum` | — | Библиотека дат, замена `datetime` |
| Connection | `Connection` | коннекшн, подключение (для объекта Airflow) | Сохранённые credentials внешней системы |
| hook | `hook` | хук | Объект, который общается с внешней системой |
| string interpolation | string interpolation | — | Подстановка значений в строку во время запуска |
| fan-out / fan-in | `fan-out` / `fan-in` | веер, фан-аут | Одна задача ведёт к нескольким / несколько к одной |
| trigger rule | `trigger rule` | правило триггера | Условие запуска задачи по статусам upstream |
| propagation | `propagation` | — | Передача сбоя или пропуска вниз по графу |
| skipped / upstream_failed | `skipped` / `upstream_failed` | — | Статусы задачи: пропущена / не запущена из-за сбоя upstream |
| XCom | `XCom` | иксКом | Маленькое сообщение между задачами в metastore |
| custom XCom backend | custom XCom backend | — | Свой класс хранения XCom |
| Taskflow API | Taskflow API | — | Декораторы `@dag`, `@task` |
| sensor | `sensor` | сенсор | Operator, который ждёт выполнения условия |
| poke | `poke` | — | Одна проверка условия sensor |
| sensor deadlock | `sensor deadlock` | — | Все slots заняты sensors, другие tasks не стартуют |
| deferrable operator | deferrable operator | — | Operator, который отдаёт ожидание `triggerer` |
| DAG run conf | `dag_run.conf` | — | Параметры запуска DAG снаружи |
| MessageQueueTrigger | `MessageQueueTrigger` | — | Trigger для сообщений очереди |
| AssetWatcher | `AssetWatcher` | — | Связывает trigger с `Asset` |
| provider package | `provider package` | — | Пакет с operators и hooks для одной системы |
| A-to-B operator | `A-to-B operator` | — | Operator, который переносит данные из системы A в систему B |
| fire and forget | `fire and forget` | — | Запустить работу и не проверять результат |
| orchestration / execution | orchestration / execution | — | Запуск и контроль работы против самой работы |
| training job | `training job` | — | Задача обучения модели в SageMaker |
| object storage | Object Storage | — | Единый код для S3, GCS и Azure Blob (с Airflow 2.8) |
| custom operator | свой `operator` | — | Класс-наследник `BaseOperator` с методом `execute()` |
| trigger | `trigger` | — | Асинхронный класс с `serialize()` и `async run()` |
| DAG integrity test | DAG integrity test | — | тест, который загружает все DAG и ищет ошибки |
| fixture | `fixture` | фикстура | подготовка и уборка окружения в pytest |
| mock / monkey patch | `mock` | мок, манки-патч | подмена вызова готовым ответом |
| CI/CD | CI/CD | — | проверки и deploy при изменении репозитория |
| DTAP | DTAP | — | dev, test, acceptance, production |
| Whirl | Whirl | — | инструмент для копии production в Docker |
| container | container | — | Изолированный процесс со своими зависимостями |
| image | image | — | Шаблон, из которого запускают контейнер |
| container engine | container engine | — | Сервис, который управляет контейнерами (Docker, Podman) |
| registry | registry | — | Хранилище образов, например Docker Hub |
| volume | volume | — | Хранилище, которое живёт дольше контейнера |
| pod | pod | — | Минимальная единица Kubernetes. Для Airflow это одна задача |
| PersistentVolumeClaim | `PersistentVolumeClaim` | — | Заявка на хранилище для pod |
| control plane / master | master (control plane) | — | Управляющая часть кластера Kubernetes |
| factory function | `factory function` | — | Функция, которая создаёт задачи или DAG по конфигу |
| Dynamic Task Mapping | `Dynamic Task Mapping` | динамическое отображение задач | Создание задач по данным запуска через `expand()` и `partial()` |
| idempotent | `idempotent` | — | Повтор задачи даёт тот же итог |
| deterministic | `deterministic` | — | Тот же вход даёт тот же выход |
| pool / slot | `pool`, `slot` | — | Набор слотов, ограничивающий параллелизм задач |
| secrets backend | `secrets backend` | — | Подключение внешнего хранилища секретов |
| offloading | `offload` | — | Перенос тяжёлой работы во внешнюю систему |
| MinIO | `MinIO` | — | Хранилище с интерфейсом S3, подходит для локальной работы |
| S3Hook | `S3Hook` | — | Hook для S3-совместимого хранилища |
| EAFP | `EAFP` | — | Сначала пробуем, потом ловим исключение |
| raw / processed / export | `raw` / `processed` / `export` | — | Слои данных по жизненному циклу |
| PandasOperator | `PandasOperator` | — | Свой оператор: input, transform, output вокруг DataFrame |
| GenAI / LLM | GenAI, LLM | — | Генеративный ИИ, большая языковая модель |
| fine-tuning | `fine-tuning` | — | Дообучение модели на своих данных |
| RAG | `RAG` | — | Поиск документов и передача их LLM как контекста |
| embedding model | `embedding model` | — | Модель, превращающая текст в вектор |
| vector database | векторная база | — | Хранит векторы и ищет по близости |
| cosine similarity | `cosine similarity` | — | Мера близости по направлению векторов |
| chunk | `chunk` | — | Небольшой кусок текста для векторизации |
| collection | `collection` | — | Аналог таблицы в Weaviate |
| prompt template | `prompt template` | — | Шаблон инструкций для LLM |
| text corpus | text corpus | — | Набор текстов для обучения модели |
| executor | `executor` | исполнитель | Часть scheduler. Задаёт, как и где запускаются tasks |
| broker | `broker` | — | Очередь Celery (Redis, RabbitMQ, SQS) |
| heartbeat | `heartbeat` | хартбит | Периодический сигнал, что task или scheduler живы |
| remote logging | `remote logging` | — | Отправка логов во внешнее хранилище |
| push / pull | `push`, `pull` | — | Модели доставки метрик: отправитель шлёт сам или сборщик забирает |
| statsd-exporter | `statsd-exporter` | — | Переводит метрики StatsD в формат Prometheus |
| alert fatigue | `alert fatigue` | — | Усталость от алертов: частые сигналы перестают читать |
| callback | `callback` | колбэк | Функция, которая вызывается при событии (сбой, успех, retry) |
| RBAC | `RBAC` | — | Доступ по ролям: пользователь, роль, права |
| Attack surface | `attack surface` | — | Число точек, через которые можно атаковать |
| Fernet key | `Fernet key` | — | Ключ для шифрования секретов в metastore |
| Symmetric / asymmetric encryption | `symmetric` / `asymmetric encryption` | — | Один ключ или пара public и private |
| LDAP, DIT, DN | `LDAP`, `DIT`, `DN` | — | Протокол каталога, его дерево, уникальное имя записи |
| MITM | `MITM` | — | Атака с чтением трафика между двумя сторонами |
| TLS / HTTPS | `TLS` / `HTTPS` | — | Шифрование трафика между браузером и сервером |
| Self-signed certificate | `self-signed certificate` | — | Certificate без подписи официального центра |
| managed Airflow | managed Airflow | — | сервис, где провайдер ведёт инфраструктуру |
| Helm chart | Helm, `chart` | — | package manager Kubernetes и его пакет |
| values file | values-файл | — | YAML с правками настроек chart |
| persistent volume | persistent volume | — | общее хранилище в Kubernetes |
| git-sync | `git-sync` | — | sidecar, который тянет DAG из Git |
| PgBouncer | `PgBouncer` | — | пул соединений для PostgreSQL |
| multiple executors | несколько executors | — | выбор executor для каждой task |
| DAG run | `DAG run` | даг-ран | Один запуск DAG за один интервал или вручную |
| pipeline | `pipeline` | пайплайн | Цепочка шагов обработки данных. Единая форма сайта |
| workflow | `workflow` | — | Общее слово для связанной работы. В Airflow оно записано как DAG |
| task group | `task group` | — | Группа tasks в UI и в коде, не влияет на запуск |
| Variable | `Variable` | переменная Airflow | Значение в metastore, доступное из любого DAG |
| retries | `retries` | ретраи | Параметр: сколько раз повторить task после сбоя |
| retry delay | `retry_delay` | — | Пауза между повторами task |
| SLA | `SLA` | — | Срок, к которому DAG или task должны закончиться |
| deferred task | `deferred` task | отложенная задача | Task, которая отдала ожидание triggerer и не занимает slot |
| branching | `branching` | ветвление задач | Выбор, какой путь графа выполнять. `BranchPythonOperator` |
| latest only | `LatestOnlyOperator` | — | Пропускает tasks в прошлых runs, оставляет только последний |
| cron expression | `cron`-выражение | крон-выражение | Строка вида `0 0 * * *`, задаёт расписание |
| mapped task | `mapped task` | размеченная задача, маппнутая задача | Один из экземпляров task, созданных через `expand()` |
| serialization | сериализация (`serialize`) | — | Перевод DAG или данных в формат для metastore |
| parsing | парсинг DAG-файлов | — | DAG processor читает файлы и строит DAG |
| Dataset | `Dataset` | — | Старое имя `asset` в Airflow 2. Не использовать в новом тексте |
| LocalExecutor | `LocalExecutor` | — | Executor: tasks идут процессами на одной машине |
| CeleryExecutor | `CeleryExecutor` | — | Executor: tasks идут на workers через broker |
| KubernetesExecutor | `KubernetesExecutor` | — | Executor: каждая task идёт в своём pod |
| queue | `queue` | очередь (для Celery) | Очередь tasks для группы workers |
| slot | `slot` | — | Место в pool, одна task занимает один slot |
| default_args | `default_args` | — | Словарь параметров, общих для всех tasks DAG |
| DAG schedule | `schedule` | — | Параметр DAG. Раньше назывался `schedule_interval` |
| run id | `run_id` | — | Уникальный id запуска DAG |
| task state | статус task (`state`) | — | success, failed, skipped, running и другие |
| Airflow UI | `Airflow UI` | — | Веб-интерфейс. В Airflow 3 его отдаёт API server |
| Task SDK | `Task SDK` | — | Библиотека для DAG-кода в Airflow 3 |
| log | логи task | — | Вывод task, хранится локально или remotely |
| data-aware scheduling | расписание по `asset` | — | DAG стартует, когда обновился asset |
| manual trigger | ручной запуск (`trigger`) | — | Запуск DAG из UI, CLI или API |
| Edge Executor | `Edge Executor` | — | Executor для workers вне основного кластера |
