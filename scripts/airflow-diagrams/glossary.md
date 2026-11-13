| English | Как пишем | Пояснение |
|---|---|---|
| DAG | `DAG` | Directed acyclic graph: граф tasks без циклов |
| task | `task` | Один шаг pipeline, узел графа |
| upstream / downstream | `upstream` / `downstream` | Задачи до данной и после неё |
| deadlock | `deadlock` | Задачи ждут друг друга, обе стоят |
| DAG file | `DAG file` | Python-файл с описанием DAG |
| DAG processor | `DAG processor` | Парсит DAG-файлы, пишет в metastore |
| scheduler | `scheduler` | Решает, когда и что запускать |
| worker | `worker` | Выполняет tasks |
| triggerer | `triggerer` | Ждёт внешние события для deferred tasks |
| API server | `API server` | Веб-интерфейс и шлюз к metastore |
| metastore | `metastore` | База метаданных Airflow |
| provider | `provider` | Пакет интеграции с внешней системой |
| schedule interval | `schedule interval` | Интервал, по которому идут runs |
| incremental pipeline | `incremental pipeline` | Run обрабатывает только delta своего интервала |
| backfilling | `backfilling` | Запуск DAG за прошлые интервалы |
| workflow manager | `workflow manager` | Инструмент для запуска графов задач |
| Термин (EN) | Русский | Заметка |
| operator | operator | не переводим |
| context manager | context manager | блок `with DAG(...)` |
| dependency | зависимость | |
| task instance | task instance | |
| upstream_failed | `upstream_failed` | статус |
| clear | `clear` | сброс состояния task |
| graph view / grid view | graph view / grid view | не переводим |
| DAG versioning | DAG versioning | Airflow 3 |
| DAG bundle | DAG bundle | |
| trigger-based schedule | `trigger timetable` | Расписание по точкам времени: run сразу после точки |
| data-interval-based schedule | `data interval timetable` | Расписание по интервалам: run в конце интервала |
| logical_date | `logical_date` | Время, за которое идёт run |
| data_interval_start / end | `data_interval_start/end` | Границы интервала данных run |
| partition | `partition` | Кусок набора данных, обычно по дате |
| catchup | `catchup` | Запускать ли пропущенные точки из прошлого |
| atomicity | `atomicity` (атомарность) | Task даёт результат целиком или не меняет систему |
| idempotency | `idempotency` (идемпотентность) | Повтор с теми же входами не меняет результат |
| timetable | `timetable` | Класс правила расписания |
| asset | `asset` | Виртуальная ссылка на данные с URI |
| outlets | `outlets` | Параметр задачи: какие assets она обновляет |
| asset event | `asset event` | Событие "asset обновлён" |
| producer / consumer DAG | producer / consumer DAG | DAG, который создаёт asset / запускается по нему |
| triggering_asset_events | `triggering_asset_events` | Контекст: события, запустившие DAG |
| context | `context` | Словарь переменных запуска задачи |
| Jinja | `Jinja` | Шаблонизатор, синтаксис `{{ ... }}` |
| template_fields | `template_fields` | Аргументы оператора, которые шаблонизируются |
| template_ext | `template_ext` | Расширения файлов, которые оператор шаблонизирует |
| template_searchpath | `template_searchpath` | Папки для поиска файлов-шаблонов |
| op_args / op_kwargs | `op_args` / `op_kwargs` | Свои аргументы для функции PythonOperator |
| pendulum | `pendulum` | Библиотека дат, замена `datetime` |
| Connection | `Connection` | Сохранённые credentials внешней системы |
| hook | `hook` | Объект, который общается с внешней системой |
| string interpolation | string interpolation | Подстановка значений в строку во время запуска |
| fan-out / fan-in | `fan-out` / `fan-in` | Одна задача ведёт к нескольким / несколько к одной |
| trigger rule | `trigger rule` | Условие запуска задачи по статусам upstream |
| propagation | `propagation` | Передача сбоя или пропуска вниз по графу |
| skipped / upstream_failed | `skipped` / `upstream_failed` | Статусы задачи: пропущена / не запущена из-за сбоя upstream |
| XCom | `XCom` | Маленькое сообщение между задачами в metastore |
| custom XCom backend | custom XCom backend | Свой класс хранения XCom |
| Taskflow API | Taskflow API | Декораторы `@dag`, `@task` |
| sensor | `sensor` | Operator, который ждёт выполнения условия |
| poke | `poke` | Одна проверка условия sensor |
| sensor deadlock | `sensor deadlock` | Все slots заняты sensors, другие tasks не стартуют |
| deferrable operator | deferrable operator | Operator, который отдаёт ожидание `triggerer` |
| DAG run conf | `dag_run.conf` | Параметры запуска DAG снаружи |
| MessageQueueTrigger | `MessageQueueTrigger` | Trigger для сообщений очереди |
| AssetWatcher | `AssetWatcher` | Связывает trigger с `Asset` |
| provider package | `provider package` | Пакет с operators и hooks для одной системы |
| A-to-B operator | `A-to-B operator` | Operator, который переносит данные из системы A в систему B |
| fire and forget | `fire and forget` | Запустить работу и не проверять результат |
| orchestration / execution | orchestration / execution | Запуск и контроль работы против самой работы |
| training job | `training job` | Задача обучения модели в SageMaker |
| object storage | Object Storage | Единый код для S3, GCS и Azure Blob (с Airflow 2.8) |
| custom operator | свой `operator` | Класс-наследник `BaseOperator` с методом `execute()` |
| trigger | `trigger` | Асинхронный класс с `serialize()` и `async run()` |
| DAG integrity test | DAG integrity test | тест, который загружает все DAG и ищет ошибки |
| fixture | `fixture` | подготовка и уборка окружения в pytest |
| mock / monkey patch | `mock` | подмена вызова готовым ответом |
| CI/CD | CI/CD | проверки и deploy при изменении репозитория |
| DTAP | DTAP | dev, test, acceptance, production |
| Whirl | Whirl | инструмент для копии production в Docker |
| container | container | Изолированный процесс со своими зависимостями |
| image | image | Шаблон, из которого запускают контейнер |
| container engine | container engine | Сервис, который управляет контейнерами (Docker, Podman) |
| registry | registry | Хранилище образов, например Docker Hub |
| volume | volume | Хранилище, которое живёт дольше контейнера |
| pod | pod | Минимальная единица Kubernetes. Для Airflow это одна задача |
| PersistentVolumeClaim | `PersistentVolumeClaim` | Заявка на хранилище для pod |
| control plane / master | master (control plane) | Управляющая часть кластера Kubernetes |
| factory function | `factory function` | Функция, которая создаёт задачи или DAG по конфигу |
| Dynamic Task Mapping | `Dynamic Task Mapping` | Создание задач по данным запуска через `expand()` и `partial()` |
| idempotent | `idempotent` | Повтор задачи даёт тот же итог |
| deterministic | `deterministic` | Тот же вход даёт тот же выход |
| pool / slot | `pool`, `slot` | Набор слотов, ограничивающий параллелизм задач |
| secrets backend | `secrets backend` | Подключение внешнего хранилища секретов |
| offloading | `offload` | Перенос тяжёлой работы во внешнюю систему |
| MinIO | `MinIO` | Хранилище с интерфейсом S3, подходит для локальной работы |
| S3Hook | `S3Hook` | Hook для S3-совместимого хранилища |
| EAFP | `EAFP` | Сначала пробуем, потом ловим исключение |
| raw / processed / export | `raw` / `processed` / `export` | Слои данных по жизненному циклу |
| PandasOperator | `PandasOperator` | Свой оператор: input, transform, output вокруг DataFrame |
| GenAI / LLM | GenAI, LLM | Генеративный ИИ, большая языковая модель |
| fine-tuning | `fine-tuning` | Дообучение модели на своих данных |
| RAG | `RAG` | Поиск документов и передача их LLM как контекста |
| embedding model | `embedding model` | Модель, превращающая текст в вектор |
| vector database | векторная база | Хранит векторы и ищет по близости |
| cosine similarity | `cosine similarity` | Мера близости по направлению векторов |
| chunk | `chunk` | Небольшой кусок текста для векторизации |
| collection | `collection` | Аналог таблицы в Weaviate |
| prompt template | `prompt template` | Шаблон инструкций для LLM |
| text corpus | text corpus | Набор текстов для обучения модели |
| executor | `executor` | Часть scheduler. Задаёт, как и где запускаются tasks |
| broker | `broker` | Очередь Celery (Redis, RabbitMQ, SQS) |
| heartbeat | `heartbeat` | Периодический сигнал, что task или scheduler живы |
| remote logging | `remote logging` | Отправка логов во внешнее хранилище |
| push / pull | `push`, `pull` | Модели доставки метрик: отправитель шлёт сам или сборщик забирает |
| statsd-exporter | `statsd-exporter` | Переводит метрики StatsD в формат Prometheus |
| alert fatigue | `alert fatigue` | Усталость от алертов: частые сигналы перестают читать |
| callback | `callback` | Функция, которая вызывается при событии (сбой, успех, retry) |
| RBAC | `RBAC` | Доступ по ролям: пользователь, роль, права |
| Attack surface | `attack surface` | Число точек, через которые можно атаковать |
| Fernet key | `Fernet key` | Ключ для шифрования секретов в metastore |
| Symmetric / asymmetric encryption | `symmetric` / `asymmetric encryption` | Один ключ или пара public и private |
| LDAP, DIT, DN | `LDAP`, `DIT`, `DN` | Протокол каталога, его дерево, уникальное имя записи |
| MITM | `MITM` | Атака с чтением трафика между двумя сторонами |
| TLS / HTTPS | `TLS` / `HTTPS` | Шифрование трафика между браузером и сервером |
| Self-signed certificate | `self-signed certificate` | Certificate без подписи официального центра |
| managed Airflow | managed Airflow | сервис, где провайдер ведёт инфраструктуру |
| Helm chart | Helm, `chart` | package manager Kubernetes и его пакет |
| values file | values-файл | YAML с правками настроек chart |
| persistent volume | persistent volume | общее хранилище в Kubernetes |
| git-sync | `git-sync` | sidecar, который тянет DAG из Git |
| PgBouncer | `PgBouncer` | пул соединений для PostgreSQL |
| multiple executors | несколько executors | выбор executor для каждой task |
