---
title: "Data Pipelines with Apache Airflow, глава 15: Airflow в production"
head:
  - tag: title
    content: "Airflow в production: executors, логи, метрики | Инжиниринг Данных"
description: "Конспект главы 15 Data Pipelines with Apache Airflow на русском. Компоненты, executors, metastore, настройки scheduler, логи, Prometheus, Grafana и алерты."
sidebar:
  order: 15
  label: "15. Airflow в production"
tags:
  - books
  - airflow
  - operations
  - monitoring
---

**Главная мысль:** в production Airflow нужно выбрать executor под нагрузку, настроить лимиты параллелизма и логи, следить за метриками и получать алерты о сбоях. Если Airflow пользуются несколько команд, отдельно решают, делать один общий экземпляр или свой у каждой.

## О чём глава

До сих пор книга учила писать pipelines. Теперь, в начале части 4, она смотрит на Airflow глазами оператора: как его запускать и держать здоровым. Предыдущая тема: [проект с GenAI](/book-summaries/engineering/data-pipelines-with-apache-airflow/14-project-genai-family-traditions/).

Темы: компоненты и `executor`, `metastore`, `scheduler` и лимиты, `DAG processor`, логи, метрики, алерты и вопрос "один Airflow или несколько".

![Executors Airflow: Local, Celery, Kubernetes и Edge](/assets/data-pipelines-with-apache-airflow/ch15-executors.png)

## Компоненты Airflow

Минимальный Airflow состоит из нескольких частей. API server и scheduler это процессы Airflow. Базу данных вы поднимаете отдельно. DAG processor должен видеть папку с файлами DAG.

| Компонент | Роль |
|---|---|
| API server | Показывает состояние pipelines и даёт действия, например запуск DAG. Это шлюз для всех других компонентов к metastore |
| DAG processor | Читает файлы DAG, достаёт из них нужное и кладёт в metastore |
| Scheduler | Решает, какие tasks запускать, и ставит их в очередь |
| Workers | Берут tasks и делают работу. Их тип задаёт executor: для Celery это процессы Celery |
| Triggerer | Выполняет deferred tasks асинхронно. Нужен только для deferrable operators |
| Metastore | Хранит метаданные: DAG runs, triggers, datasets и сериализованные DAG. Так компонентам не нужно самим парсить файлы |

Раньше DAG мог обращаться к metastore напрямую. Это могло сломать весь экземпляр, поэтому Airflow 3 поставил API server посредником. Авторы предупреждают: шлюз пока реализован не для всех компонентов, поведение вашей версии может отличаться.

## Выбор executor

Airflow запускает tasks через `executor`. Вы выбираете его настройкой `AIRFLOW__CORE__EXECUTOR`. Executors шесть. Четыре книга разбирает: `LocalExecutor`, `CeleryExecutor`, `KubernetesExecutor`, `EdgeExecutor`. Ещё два для AWS: `BatchExecutor` (alpha, аналог Celery) и `EcsExecutor` (похож на Kubernetes).

> **Пояснение:** приоритет настроек такой: переменная `AIRFLOW__<SECTION>__<KEY>`, её вариант с `_CMD`, значение в `airflow.cfg`, команда в cfg, значение по умолчанию. Книга пишет настройки как переменные окружения. Текущие значения видны на странице Configurations.

### Как выбрать

| Executor | Распределённый | Установка | Когда подходит |
|---|---|---|---|
| `LocalExecutor` | Нет | Простая | Хватает одной машины |
| `CeleryExecutor` | Да | Средняя | Нужно масштабироваться на несколько машин |
| `KubernetesExecutor` | Да | Сложная | Вы знаете Kubernetes и хотите контейнеры |
| `EdgeExecutor` | Да | Средняя | Tasks должны идти вне среды Airflow, например on-premise при Airflow в облаке |

Зачем распределять работу: вы упёрлись в ресурсы одной машины, хотите резервирование или скорость.

- **LocalExecutor** самый простой. Tasks идут в подпроцессах scheduler (форк). Лимит задаёт `AIRFLOW__CORE__PARALLELISM`, по умолчанию 32. Нужна база MySQL или PostgreSQL и extra `apache-airflow[postgres]`. Предел один: ресурсы машины scheduler. В Airflow 3 это default.
- **CeleryExecutor** кладёт tasks в очередь Celery, которую называют `broker` (Redis, RabbitMQ, AWS SQS). Компоненты могут жить на разных машинах. Для мониторинга есть Flower.
- **KubernetesExecutor** запускает каждый task в своём pod. Pod это минимальная единица запуска в Kubernetes: один или несколько контейнеров. Изоляция высокая, накладных расходов больше.
- **EdgeExecutor** новый. Worker работает вне среды Airflow и говорит с API server. Есть ограничения (особенно с логами), производительность не проверена.

### Установка

В Airflow 3 DAG processor нужно запускать отдельно: `airflow dag-processor`. Чтобы проверить установку executor, запустите любой DAG: если task дошла до `running`, executor её подхватил.

**CeleryExecutor.** Нужны три вещи:

1. Extra `apache-airflow[celery]` и `AIRFLOW__CORE__EXECUTOR=CeleryExecutor`.
2. `AIRFLOW__CELERY__BROKER_URL` (например `redis://localhost:6379/0`) и `AIRFLOW__CELERY__RESULT_BACKEND` (префикс `db+` значит база, например `db+postgresql://...`).
3. Папка DAG на всех машинах по одному пути. Это общая файловая система или образ с DAG внутри. Во втором случае каждая правка кода значит передеплой компонентов.

Затем запустите API server, scheduler и `airflow celery worker`. Flower: `airflow celery flower`, порт 5555. Из двух распределённых executors Celery проще: Kubernetes не нужен.

**KubernetesExecutor.** Scheduler просит Kubernetes API создать pod с командой `airflow tasks run ...`, а состояние pod следит Kubernetes. Ставят обычно через Helm (глава 17). Сложнее всего доставить файлы DAG. Три способа:

- общий `PersistentVolume`, но непросто положить в него код;
- init container с git-sync: код тянется из репозитория, с задержкой по интервалу;
- DAG внутри Docker-образа, тогда новый DAG значит передеплой.

**EdgeExecutor.** Подходит, если часть tasks должна идти вне Airflow, например on-premise. Нужны провайдер `apache-airflow-providers-edge3`, executor с полным путём `airflow.providers.edge3.executors.EdgeExecutor`, общий ключ `AIRFLOW__CORE__INTERNAL_API_SECRET_KEY`, `AIRFLOW__EDGE__API_ENABLED=True` и `AIRFLOW__EDGE__API_URL`. Статус workers показывает `airflow edge list-workers`. Worker можно перевести в maintenance mode командой `airflow edge maintenance on`: scheduler не шлёт ему tasks.

### Несколько executors сразу

Старые hybrid executors (`CeleryKubernetesExecutor`) авторы не советуют: они злоупотребляют атрибутом `queue`. Вместо них есть поддержка нескольких executors сразу, её использует официальный Helm chart. Их перечисляют в конфиге: `executor = LocalExecutor,CeleryExecutor`. Для task executor задают аргументом `executor=`, иначе берётся первый в списке.

## Metastore

Всё, что делает Airflow, записано в metastore. Airflow работает с базой через SQLAlchemy, поэтому поддерживаются базы, которые знает SQLAlchemy. Рекомендуют PostgreSQL или MySQL. Без настройки `airflow db migrate` создаёт SQLite-файл. Для production создайте базу заранее и задайте строку подключения в `AIRFLOW__CORE__SQL_ALCHEMY_CONN`.

Команды CLI для базы:

| Команда | Что делает |
|---|---|
| `airflow db migrate` | Создаёт схему или обновляет до последней версии |
| `airflow db check` | Проверяет, доступна ли база |
| `airflow db clean` | Удаляет старые записи. Нужна дата |
| `airflow db downgrade` | Откатывает схему на указанную версию |
| `airflow db shell` | Открывает консоль базы. Не правьте данные руками: результат непредсказуем |
| `airflow db reset` | Стирает базу и создаёт пустую. Операция разрушающая |

После обновления Airflow запускайте `airflow db migrate`: он применит новые миграции схемы.

На свежей установке видны примеры DAG и connections. В production они не нужны. Но `AIRFLOW__CORE__LOAD_EXAMPLES=False` не убирает примеры из работающей базы: загруженные DAG остаются в metastore, их файлы просто больше не парсятся. То же для `LOAD_DEFAULT_CONNECTIONS=False`. Чистая база: поставьте Airflow, задайте оба флага, затем запустите `airflow db migrate`. Если забыли, чистите metastore вручную.

## Scheduler и параллелизм

![Путь task: scheduled, queued, running, success или failed](/assets/data-pipelines-with-apache-airflow/ch15-task-states.png)

У scheduler две обязанности: решить, какие tasks готовы, и поставить их в `queued` (task scheduler), и выполнить queued tasks (task executor). До Airflow 3 scheduler ещё парсил DAG, теперь это делает DAG processor.

### Task scheduler и task executor

Task scheduler работает в цикле `while True`. Он проверяет каждый task instance: выполнены ли upstream, закончился ли интервал, успешен ли прошлый run при `depends_on_past=True`. Если всё выполнено, task получает `scheduled`. Другой цикл переводит `scheduled` в `queued`: он проверяет свободные слоты и приоритет (`priority_weight`). Когда команда попала в очередь, работа scheduler закончена.

Дальше работает task executor. Он создаёт для task отдельный процесс, чтобы сбой не уронил Airflow, и запускает `airflow tasks run <dag_id> <task_id> <run_id>`. Перед запуском Airflow пишет в metastore `running`. Потом он шлёт heartbeat и проверяет, закончился ли task. Код возврата 0 значит успех, другой значит сбой. Пока task идёт, Airflow ждёт `AIRFLOW__SCHEDULER__JOB_HEARTBEAT_SEC` (по умолчанию 5) и проверяет снова. Каждая смена состояния пишется в metastore. На схеме идеальный путь, при сбоях task попадёт и в другие состояния.

### Несколько schedulers

Scheduler можно запустить в нескольких экземплярах для масштаба и надёжности. Лидера выбирать не нужно: Airflow использует блокировки строк в базе (`SELECT ... FOR UPDATE`), поэтому база должна их поддерживать. Проверены PostgreSQL 9.6+ и MySQL 8+. Если отключить блокировки, несколько schedulers запускать нельзя. Чтобы добавить scheduler, запустите ещё один `airflow scheduler`. Они берут работу по принципу "кто первый". Если одна машина упала, остальные работают.

### Производительность

Много tasks нагружают metastore. Новые версии Airflow улучшают производительность, поэтому обновляйтесь. Чтобы снизить число запросов, поднимите `AIRFLOW__SCHEDULER__SCHEDULER_HEARTBEAT_SEC` (по умолчанию 5), разумно 60. Интерфейс предупреждает о проблеме через 30 секунд после последнего heartbeat (`SCHEDULER_HEALTH_CHECK_THRESHOLD`).

При нескольких schedulers и огромных DAG (больше 10 000 tasks) пробуйте `MAX_DAGRUNS_TO_CREATE_PER_LOOP`: он ограничивает число DAG runs за проход, и один scheduler не забирает всю работу. Похожий смысл у `MAX_DAGRUNS_PER_LOOP_TO_SCHEDULE`. `IDLE_SLEEP_TIME` задаёт паузу, когда работы нет.

### Сколько tasks идёт параллельно

![Лимиты параллелизма работают вместе: действует самый строгий](/assets/data-pipelines-with-apache-airflow/ch15-concurrency-limits.png)

Названия настроек обманчивы, поэтому читайте описания.

| Настройка | По умолчанию | Что ограничивает |
|---|---|---|
| `MAX_ACTIVE_TASKS_PER_DAG` | 16 | Tasks в queued или running на один DAG |
| `MAX_ACTIVE_RUNS_PER_DAG` | 16 | Параллельные DAG runs одного DAG |
| `PARALLELISM` | 32 | Все task instances во всей системе |
| `WORKER_CONCURRENCY` (Celery) | 16 | Процессы на один worker |

Большой DAG упрётся в 16 параллельных tasks, хотя `parallelism` равен 32. Второй большой DAG тоже получит 16, и вместе они дойдут до глобальных 32. Есть ещё лимит `default_pool` на 128 слотов: до него надо дойти, подняв оба лимита выше. Для отдельного DAG число runs можно переопределить аргументом `concurrency`. Проверим арифметику простой моделью без Airflow. Три DAG по 40 готовых tasks:

```text
один DAG, 40 готовых tasks
dag_a: готово 40, лимит DAG даёт 16
всего в работе: 16 (parallelism 32, pool 128)
два DAG по 40 готовых tasks
dag_a: готово 40, лимит DAG даёт 16
dag_b: готово 40, лимит DAG даёт 16
всего в работе: 32 (parallelism 32, pool 128)
три DAG по 40 готовых tasks
dag_a: готово 40, лимит DAG даёт 16
dag_b: готово 40, лимит DAG даёт 16
dag_c: готово 40, лимит DAG даёт 16
всего в работе: 32 (parallelism 32, pool 128)
```

Скрипт: [ch15_limits.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch15_limits.py).

Airflow ресурсоёмок: на один процесс worker закладывайте не меньше 200 МБ RAM и считайте худший случай, когда тяжёлые tasks идут вместе. Для отдельной task есть аргумент `pool`. Например, 20 tasks, которые ждут базу, безопасны, а 5 CPU-тяжёлых нет. Их отправляют в отдельный `high_resource` pool с малым числом слотов.

## DAG processor

DAG processor регулярно читает файлы в папке DAG, даже если они не менялись. Причина: бывают динамические DAG с тем же кодом, но структурой из внешнего источника, например из YAML. Событийного разбора по изменению файлов пока нет.

Разбор требует CPU. Чем он чаще, тем быстрее видны правки, но выше нагрузка. Если DAG меняются редко, интервалы можно поднять. Главные настройки раздела `DAG_PROCESSOR`:

- `MIN_FILE_PROCESS_INTERVAL`: минимальный интервал между разборами файла. Это нижняя граница, не гарантия.
- `REFRESH_INTERVAL` (по умолчанию 300 секунд): как часто искать новые файлы. Тоже нижняя граница: проверка может прийти через 305 секунд.
- `PARSING_PROCESSES` (по умолчанию 2, при SQLite 1): число процессов разбора. Больше процессов значит меньше задержка и больше CPU. Меняйте понемногу и измеряйте.

Если новые DAG появляются долго, уменьшите `REFRESH_INTERVAL`. Предупреждение авторов: слишком малое значение сильно поднимет CPU, потому что DAG будут разбираться постоянно. Лог лежит в `logs/dag_processor_manager/dag_processor_manager.log`, в нём статистика по каждому файлу.

## Логи

Три вида логов. По умолчанию все пишутся в `$AIRFLOW_HOME/logs`.

- **API server logs.** Access-логи (запросы) и error-логи. По умолчанию идут в stdout или stderr. API server работает на Gunicorn, поэтому в файл их пишут через `airflow api-server --log_config <файл>`, где заданы `accesslog` и `errorlog`.
- **Scheduler logs.** Пишутся в файлы по дням, по одному на файл DAG. Каждый разбор оставляет строки: DAG найден, создан DAG run, обновлены task instances. По ним видно, работает ли scheduler как задумано.
- **Task logs.** Один файл на одну попытку одного task. Путь: `dag_id=.../task_id=.../<run_id>/attempt=N.log`. Их же показывает интерфейс.

Если Airflow живёт в эфемерных контейнерах, логи исчезают вместе с ними. Для этого и для архива есть `remote logging`: S3, GCS, Azure Blob, Alibaba OSS, Elasticsearch, OpenSearch, Redis (нужны свои extras). Включают так:

```text
AIRFLOW__LOGGING__REMOTE_LOGGING=True
AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=<id connection с доступом>
AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=gs://my-bucket/path/to/logs
```

Последняя строка пример для GCS. Остальное читайте в документации нужной системы.

## Метрики

Наблюдаемость (observability) складывается из трёх частей: логи, метрики и traces. Traces книга не разбирает: это сложно и зависит от окружения. Метрики это числа о состоянии системы, например задержка между постановкой task в очередь и стартом. Установки очень разные, поэтому глава показывает основные идеи.

### Как это устроено

![Стек метрик: Airflow, StatsD exporter, Prometheus, Grafana и алерты](/assets/data-pipelines-with-apache-airflow/ch15-metrics-stack.png)

Airflow отправляет метрики через StatsD или OpenTelemetry. Они взаимозаменяемы, книга показывает StatsD. Airflow "instrumented": события в нём порождают сообщения. Например, при падении task уходит `ti_failures` со значением 1.

Доставка бывает двух видов. При `push` система сама шлёт метрики сборщику, но при многих отправителях сборщик может захлебнуться. При `pull` сборщик сам забирает метрики с endpoint. StatsD работает по push, Prometheus по pull, и Airflow не отдаёт формат Prometheus. Поэтому между ними ставят `statsd-exporter`: он принимает StatsD и отдаёт Prometheus. Авторы выбирают Prometheus: он гибче, проще в эксплуатации и дружит почти со всем.

Модели данных тоже разные. Prometheus идентифицирует метрику по имени и меткам: `task_duration{dag_id="mydag", task_id="first_task"}`. Так можно выбрать любую комбинацию меток. StatsD кодирует метки точками в имени: `task_duration.my_dag.first_task`, и выбрать одну task по всем DAG трудно. Exporter превращает точки в метки по общим правилам, но не всегда удачно: в `dag.<dag_id>.<task_id>.duration` метки сами не появятся. Для таких имён настраивают свои правила.

### Настройка по шагам

Все шаги ниже мы не запускали: они требуют Docker с exporter, Prometheus и Grafana.

1. **Airflow.** Нужен extra `apache-airflow[statsd]`. Настройки: `AIRFLOW__METRICS__STATSD_ON=True`, `STATSD_HOST` (по умолчанию localhost), `STATSD_PORT=9125`, `STATSD_PREFIX` (по умолчанию `airflow`). Airflow шлёт события по UDP на этот порт.
2. **statsd-exporter.** Запускают в Docker: `docker run -d -p 9102:9102 -p 9125:9125/udp prom/statsd-exporter`. Метрики видны на `http://localhost:9102/metrics`.
3. **Prometheus.** Это time-series база с языком PromQL. Данные в неё не вставляют: она сама забирает их с targets. В конфиге одна job с адресом exporter (`localhost:9102`). Страница `/targets` должна показать цель в состоянии UP.
4. **Grafana.** Запускают в Docker, добавляют Prometheus как data source и строят панель по метрике, например `airflow_dag_processing_total_parse_time`.

Авторы отмечают три вещи про такую схему:

- Метрики почти в реальном времени. Prometheus по умолчанию опрашивает раз в минуту, поэтому задержка до графика в пределах минуты. Обычно этого достаточно.
- Prometheus не хранит отдельные события и не годится для отчётов. Для событий лучше подойдёт InfluxDB.
- Схема про мониторинг, а не про алерты. Алерты умеют Grafana и PagerDuty. Но их избыток ведёт к `alert fatigue`: частые алерты перестают читать. Решайте, за чем следить, а о чём предупреждать.

Что Airflow отправляет, можно проверить без всей цепочки. Скрипт поднимает UDP-сервер вместо exporter, включает StatsD, как это делает Airflow, и показывает пакеты. Проверено на Airflow 3.4.0.

```text
airflow.ti_failures:1|c
airflow.executor.open_slots:28|g
airflow.dag_processing.import_errors:0|g
```

Формат `имя:значение|тип`: `c` это счётчик, `g` это gauge (текущее значение). Скрипт: [ch15_statsd.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch15_statsd.py).

### За чем следить

Для любой системы есть четыре базовых сигнала. В Airflow они видны на уровне tasks, DAG и компонентов.

| Сигнал | Вопрос | Пример в Airflow |
|---|---|---|
| Latency | Как долго обслуживается запрос? | Ответ API server, время от queued до running |
| Load | Сколько работы просят? | Tasks в минуту, свободные слоты pool |
| Errors | Какие ошибки возникают? | Zombie tasks (процесс пропал, а task числится running), не-200 ответы, timeouts |
| Saturation | Какая доля мощности занята? | CPU машины, число работающих tasks. Нужно знать верхнюю границу, а она не всегда очевидна |

Остальные системы смотрят через exporters Prometheus: node exporter для машин, exporters для PostgreSQL или MySQL, Celery, Redis и Kubernetes, Black Box exporter для проверки HTTP-кода. Полный список метрик Airflow есть в документации. Хорошие метрики для старта:

| Метрика | Что показывает |
|---|---|
| `dag_processing.import_errors` | Ошибки разбора DAG. Больше 0 плохо |
| `dag_processing.total_parse_time` | Время разбора всех DAG. Резкий рост после правок плохо |
| `ti_failures` | Число упавших task instances |
| `dag_processing.last_run.seconds_ago.<файл>` | Сколько секунд назад scheduler смотрел файл. Должно быть секунды, иначе scheduler перегружен |
| `dagrun.<dag_id>.first_task_scheduling_delay` | Задержка между плановым и реальным стартом DAG run |
| `executor.open_slots` | Свободные слоты executor |
| `executor.queued_tasks` | Tasks в состоянии queued |

## Алерты

Для критичных pipelines нужно знать о сбое сразу: о падении task или о task, которая задержала другие. Airflow даёт несколько уровней.

На уровне DAG есть `on_failure_callback`: функция, которая вызывается при падении DAG run. Что она делает, решаете вы: сообщение в Slack, инцидент в PagerDuty или письмо. Для частых систем есть providers.

На уровне task каждый operator наследует `on_failure_callback` от `BaseOperator`. Чтобы не задавать его у каждой task, его кладут в `default_args`: он доходит до всех tasks. Есть также `on_success_callback` и `on_retry_callback`. Если callback задан и у DAG, и в `default_args`, при падении task придут два уведомления: за task и за DAG run.

Проверим на примере по мотивам книги. Task падает (`exit 1`), у DAG и у task один callback, а у task свой executor. Проверено на Airflow 3.4.0.

```python
"""Глава 15: callback при сбое на уровне DAG и task, общий default_args, свой executor у task."""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG


def notify_failure(context):
    # здесь был бы Slack, PagerDuty или email
    ti = context["ti"]
    print(f"ALERT: task {ti.task_id} упала в DAG {ti.dag_id}")


with DAG(
    dag_id="nightly_export",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    on_failure_callback=notify_failure,  # сработает при падении всего DAG run
    default_args={"on_failure_callback": notify_failure, "retries": 0},  # и для каждой task
) as dag:
    export = BashOperator(
        task_id="export",
        bash_command="exit 1",  # task падает: код возврата не 0
        executor="LocalExecutor",  # executor можно задать для одной task
    )
```

Разбор без сервера показывает, что Airflow увидел настройки:

```text
значения по умолчанию в Airflow 3.4:
  core.executor = LocalExecutor
  core.parallelism = 32
  core.max_active_tasks_per_dag = 16
  core.max_active_runs_per_dag = 16
  celery.worker_concurrency = 16
  dag_processor.refresh_interval = 300
  dag_processor.parsing_processes = 2
  scheduler.job_heartbeat_sec = 5
ошибки разбора: нет
callback у DAG: ['notify_failure']
callback у task: ['notify_failure']
executor у task: LocalExecutor
```

Запуск `airflow dags test` показал, что DAG run упал и сработал callback DAG: `ALERT: task export упала в DAG nightly_export`. Скрипты: [ch15_callbacks_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch15_callbacks_dag.py) и [ch15_check.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch15_check.py).

Для писем есть аргументы `email_on_failure` и `email`. Airflow формирует письмо сам, но нужен SMTP в конфиге: `AIRFLOW__SMTP__SMTP_HOST`, `SMTP_PORT`, `SMTP_STARTTLS`, `SMTP_MAIL_FROM`. Логин и пароль в конфиг не кладут: их берут из connection (по умолчанию `smtp_default`, другое имя нужно указать явно). Хост и порт из полей connection Airflow игнорирует. `email_on_failure` по умолчанию уже `True`, но без SMTP и адреса в `email` письмо не уйдёт. Отправку SMTP мы не запускали.

## Один Airflow или несколько

Когда растут число DAG, их сложность и число команд, стоит подумать о нескольких экземплярах. Два крайних варианта: один общий Airflow или свой у каждой команды.

| | Один на всех | Свой на команду |
|---|---|---|
| Стоимость | Ниже: ресурсы общие, особенно если расписания команд почти не пересекаются | Выше: компоненты дублируются, есть расходы на управление |
| Изоляция | Слабая. Один сбой касается всех, апгрейд нужно согласовать со всеми | Полная. Каждая команда сама настраивает среду и сроки апгрейда |
| Права и владение DAG | Сложнее. RBAC скрывает DAG, но DAG другой команды можно перезаписать | Проще |
| Связь между командами | Datasets работают | События datasets видны только внутри экземпляра. Нужны обходные решения, например Airbridge: свой код и вызовы API |

Общий Airflow становится проблемой, если ресурсы команд сильно пересекаются, и он единая точка отказа. Выбор (или гибрид) это важное решение организации. Авторы советуют сверить его с рекомендациями Astronomer, Google и AWS.

## Итоги главы

- Для production важно выбрать executor под нагрузку и окружение.
- `LocalExecutor` прост, но ограничен одной машиной и годится для небольших установок.
- `CeleryExecutor` и `KubernetesExecutor` сложнее, зато масштабируют tasks на много машин. Если Kubernetes уже есть, он логичен и изолирует хорошо, но с накладными расходами. Поэтому и на Kubernetes иногда выбирают Celery.
- `EdgeExecutor` запускает tasks вне среды Airflow. Он ещё экспериментальный.
- Можно настроить несколько executors сразу и смешивать их свойства.
- Параллелизм и производительность настраиваются переменными окружения или в `airflow.cfg`.
- Для хранения и показа метрик Airflow подходят Prometheus и Grafana. Данные в них даёт StatsD или OpenTelemetry.
- Failure callbacks отправляют письма или свои уведомления при событиях.
- Если организация и использование Airflow растут, подумайте о нескольких экземплярах.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Executor` | Часть scheduler. Задаёт, как и где запускаются tasks |
| `Broker` | Очередь Celery (Redis, RabbitMQ, SQS) |
| `Pod` | Минимальная единица запуска в Kubernetes |
| `Metastore` | База метаданных Airflow |
| `parallelism` | Глобальный лимит параллельных task instances |
| `Pool` | Ограничение числа слотов для группы tasks |
| `Heartbeat` | Периодический сигнал, что task или scheduler живы |
| `StatsD` | Протокол отправки метрик по модели push |
| `Prometheus` | Система сбора метрик по модели pull, база time series |
| `Grafana` | Инструмент дашбордов |
| `Callback` | Функция, которая вызывается при событии (сбой, успех, retry) |
| `Alert fatigue` | Усталость от алертов: частые сигналы перестают читать |

## Что это значит на практике

- Начните с `LocalExecutor`. Переходите на Celery или Kubernetes, когда не хватает ресурсов одной машины или нужна отказоустойчивость.
- Для production берите PostgreSQL. Регулярно запускайте `airflow db clean`, чтобы metastore не рос бесконечно.
- Подбирайте лимиты вместе: `parallelism`, `max_active_tasks_per_dag`, pools и память workers.
- Включите remote logging до первого сбоя. Потом старые логи уже не вернуть.
- Следите минимум за `import_errors`, `ti_failures`, очередью и задержкой планирования.
- Добавьте `on_failure_callback` в `default_args`. Алерты выбирайте внимательно, иначе их перестанут читать.
- Если у вас несколько команд, решите заранее, как делить Airflow. Это влияет на стоимость, права и связи через assets.
- Отключайте примеры DAG и connections до первой инициализации базы. Позже их придётся чистить вручную.
- После каждого обновления Airflow запускайте `airflow db migrate`.
- Не опускайте `refresh_interval` слишком низко: DAG processor съест CPU.

## Практика

Скрипты работают без запущенного Airflow, проверены на Airflow 3.4.0. Не запускали: Celery, Kubernetes, EdgeExecutor, exporter, Prometheus, Grafana, SMTP (нужны брокер, кластер, Docker). Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

### Задания

**1. Поднимите лимит.** В [ch15_limits.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch15_limits.py) поставьте `PARALLELISM = 64`. Сколько tasks пойдёт в работу при трёх DAG по 40 готовых tasks?

<details>
<summary>Решение</summary>

48. Каждый DAG даёт 16 (лимит DAG), вместе 48. Это меньше 64 и меньше 128 слотов `default_pool`. Проверено запуском.

</details>

**2. Какой executor?** Выберите для каждого случая: (а) один сервер, 20 DAG, ресурсов хватает; (б) нужно распределить работу, Kubernetes в компании нет; (в) часть tasks должна идти в on-premise сети, Airflow в облаке.

<details>
<summary>Решение</summary>

(а) `LocalExecutor`: прост и достаточен. (б) `CeleryExecutor`: нужен только broker, Kubernetes не нужен. (в) `EdgeExecutor`, помня, что он экспериментальный. Выбор рассуждением по таблице главы, не запускали.

</details>

**3. Какая настройка победит?** В `airflow.cfg` стоит `parallelism = 16`, а в окружении `AIRFLOW__CORE__PARALLELISM=64`. Какое значение увидит Airflow?

<details>
<summary>Решение</summary>

64. Переменная окружения стоит выше `airflow.cfg` в порядке приоритета. Проверено запуском: `conf.get('core', 'parallelism')` вернул 64 при такой переменной.

</details>

## Вопросы для самопроверки

1. Какую роль в Airflow 3 играет API server? Чем DAG processor отличается от scheduler?
2. Когда выбрать `CeleryExecutor`, а когда `KubernetesExecutor`? Почему и на Kubernetes иногда берут Celery?
3. Почему DAG может выполнять только 16 tasks параллельно, хотя `parallelism` равен 32?
4. Зачем между Airflow и Prometheus ставят `statsd-exporter`?
5. Почему `LOAD_EXAMPLES=False` не убирает примеры из уже работающей базы?
6. Когда лучше один Airflow на всех, а когда свой у каждой команды?

Предыдущая: [Проект: GenAI и семейные традиции](/book-summaries/engineering/data-pipelines-with-apache-airflow/14-project-genai-family-traditions/). Следующая: [Защита Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/16-securing-airflow/).
