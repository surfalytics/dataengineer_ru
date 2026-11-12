---
title: "Data Pipelines with Apache Airflow, глава 7: Запуск workflow внешними событиями"
head:
  - tag: title
    content: "Airflow: sensors, REST API и запуск по сообщениям | Инжиниринг Данных"
description: "Конспект главы 7 Data Pipelines with Apache Airflow на русском. Sensors, sensor deadlock, deferrable operators, REST API, CLI, MessageQueueTrigger."
sidebar:
  order: 7
  label: "7. Внешние события"
tags:
  - books
  - airflow
  - sensors
  - orchestration
---

**Главная мысль:** данные приходят в случайное время. Не ждите «на всякий случай» в конце окна. Пусть Airflow сам узнает о событии: через sensor, вызов API или сообщение в очереди.

![Четыре способа запустить DAG от внешнего события: sensor, CLI, REST API и сообщение в очереди](/assets/data-pipelines-with-apache-airflow/ch07-triggers.png)

## Проблема: ожидание по расписанию

Пример из книги: приложение с купонами. Четыре супермаркета выкладывают файлы с акциями в общее хранилище. Время разное: с 16:00 до 2:00 ночи.

- Если запускать DAG в 2:00, первый супермаркет ждёт 9,5 часов.
- Данные есть, но не обработаны.
- Решение: запускать DAG раньше и проверять условие, пока данные не придут.

## Sensors

`Sensor` - особый вид `operator`. Он снова и снова проверяет условие. Если условие верно, task получает `success`. Если нет, sensor ждёт и пробует ещё раз. Одна проверка называется `poke`.

| Параметр | Что делает |
|---|---|
| `poke_interval` | Пауза между проверками. По умолчанию 60 секунд |
| `timeout` | Сколько sensor может работать всего. По умолчанию 7 дней |
| `mode` | `poke` держит slot всё время. `reschedule` отпускает slot между проверками |

Как строят DAG:

- `start_date` и расписание ставят в начало окна прихода данных.
- Перед каждой веткой обработки стоит свой sensor.
- Ветка готового супермаркета идёт дальше сразу. Остальные ждут.

Предупреждение: слишком частый `poke_interval` может перегрузить внешнюю систему.

### Свои условия: PythonSensor

`FileSensor` понимает wildcard, например `data-*.csv`. Но он сработает на первом файле, пока остальные ещё загружаются. Это плохо.

Решение: поставщик пишет файл `_SUCCESS` последним. `PythonSensor` вызывает вашу функцию. Она возвращает `True` или `False`. Проверяет и файлы данных, и `_SUCCESS`.

### Когда данных нет: sensor deadlock

Если супермаркет не прислал данные, sensor ждёт до `timeout`. Это 7 дней. Каждый день добавляется новый DAG run со своими ждущими sensors.

Что получается:

1. День 1: три sensors ждут и занимают 3 slots.
2. День 2: уже 6 slots. День 5: 15 slots.
3. По умолчанию в одном DAG работает до 16 tasks (`max_active_tasks`). Дальше новые tasks не стартуют.
4. Если достигнут общий лимит Airflow, встаёт вся система.

Это называют `sensor deadlock`. Способы защиты:

- Ставьте разумный `timeout`.
- Используйте `mode="reschedule"`.
- Используйте deferrable operators.
- Настройте лимиты `max_active_tasks` и глобальные лимиты.

### Deferrable operators

Deferrable operator отдаёт ожидание компоненту `triggerer`. Worker slot освобождается. `Triggerer` запускает асинхронный код (`asyncio`) и ждёт сотни событий сразу. Когда условие выполнено, task возвращается на worker.

- Такие операторы часто имеют суффикс `Async` или параметр `deferrable=True`.
- Нужен хотя бы один процесс `triggerer`.
- `PythonOperator` и TaskFlow-tasks нельзя сделать deferrable. Они синхронные.

## Запуск через CLI и REST API

Можно запустить DAG снаружи, например из CI/CD или из AWS Lambda. Тогда не нужны sensors, которые опрашивают всё время.

| Способ | Пример |
|---|---|
| CLI | `airflow dags trigger dag1` |
| CLI с параметрами | `airflow dags trigger --conf '{"supermarket_id": 1}' dag1` |
| REST API | `POST /dags/<dag_id>/dagRuns` с телом `{"conf": {...}}` |
| Обновление asset | `POST` в endpoint событий asset |

Важные детали:

- Run, запущенный снаружи, получает `run_type = manual`.
- `conf` доступен в tasks через `context["dag_run"].conf`.
- С `conf` не нужны копии tasks под разные значения. Один DAG обслуживает всех.
- DAG, который зависит от `conf`, нельзя ставить на расписание. Scheduled run не имеет `conf`. Ставьте `schedule=None`.
- Пароль в открытом виде в `curl` - плохая практика. Используйте другие способы аутентификации.

## Запуск по сообщениям

Очереди (Kafka, RabbitMQ, Google Pub/Sub, Azure Event Hubs) хорошо подходят для near-real-time. Каждый супермаркет мог бы отправлять сообщение «загрузка завершена» вместо файла `_SUCCESS`.

Как это собрать в Airflow 3:

1. `MessageQueueTrigger` получает `scheme="kafka"` и список `topics`. Адрес брокера берётся из Airflow connection (`kafka_default`).
2. `apply_function` фильтрует сообщения. Она возвращает `True`, если нужно запустить DAG.
3. Trigger оборачивают в `AssetWatcher` и привязывают к `Asset`.
4. DAG получает этот `Asset` в `schedule`.

Нюансы:

- Есть небольшая задержка. Consumer читает новые сообщения с фиксированным интервалом.
- Нужна дополнительная инфраструктура: очередь.
- Это удобный способ связать два экземпляра Airflow. Один DAG пишет сообщение, другой стартует. API не нужно открывать наружу.

## Пример кода

Проверено на Airflow 3.4: функция sensor проверена в pytest, DAG с Kafka загружается. Для запуска нужен брокер Kafka и provider `apache-airflow-providers-apache-kafka`.

Sensor с проверкой двух условий. Имена здесь выдуманы.

```python
from datetime import timedelta
from pathlib import Path

from airflow.providers.standard.sensors.python import PythonSensor


def _batch_is_ready(partner):
    folder = Path("/landing") / partner
    has_data = any(folder.glob("part-*.parquet"))
    return has_data and (folder / "_DONE").exists()


wait_partner_a = PythonSensor(
    task_id="wait_partner_a",
    python_callable=_batch_is_ready,
    op_kwargs={"partner": "partner_a"},
    poke_interval=300,
    timeout=timedelta(hours=10),
    mode="reschedule",
)
```

Запуск DAG при сообщении в очереди:

```python
from airflow.sdk import DAG, Asset, AssetWatcher
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
from airflow.providers.standard.operators.empty import EmptyOperator

trigger = MessageQueueTrigger(
    scheme="kafka",
    topics=["uploads"],
    apply_function="my_project.filters.only_done",
    kafka_config_id="kafka_default",
)
uploads = Asset("uploads_topic", watchers=[AssetWatcher(name="uploads_watcher", trigger=trigger)])

with DAG(dag_id="on_upload", schedule=[uploads]):
    EmptyOperator(task_id="load")
```

## Ключевые термины

| Термин | Значение |
|---|---|
| `Sensor` | Operator, который ждёт выполнения условия |
| `poke` | Одна проверка условия sensor |
| `mode="reschedule"` | Sensor освобождает worker slot между проверками |
| Sensor deadlock | Все slots заняты sensors, другие tasks не могут стартовать |
| Deferrable operator | Operator, который отдаёт ожидание процессу `triggerer` |
| `triggerer` | Компонент Airflow на `asyncio`. Ждёт много событий сразу |
| `dag_run.conf` | Параметры, переданные при запуске DAG снаружи |
| `MessageQueueTrigger` | Trigger, который реагирует на сообщения в очереди |
| `AssetWatcher` | Связывает trigger с `Asset`, чтобы DAG стартовал от события |

## Что это значит на практике

- Если поставщик присылает данные в разное время, не ставьте расписание «с запасом». Используйте sensor или событие.
- Всегда задавайте `timeout`. Значение 7 дней по умолчанию опасно для ежедневного DAG.
- Для долгих ожиданий берите `mode="reschedule"` или deferrable-версию.
- Договоритесь с поставщиком о маркере конца загрузки, например `_SUCCESS`. Иначе вы прочитаете половину файлов.
- Если источник умеет вызывать API (Lambda, CI/CD), запускайте DAG через REST API. Это дешевле, чем опрос.
- Параметризуйте DAG через `conf`, но помните: по расписанию он работать не будет.

## Вопросы для самопроверки

1. Чем `poke` отличается от `reschedule`? Что происходит со slot?
2. Как возникает sensor deadlock, если один поставщик не прислал данные?
3. Почему `PythonOperator` нельзя сделать deferrable?
4. Какие шаги нужны, чтобы DAG стартовал от сообщения в Kafka?

Предыдущая: [Зависимости между задачами](/book-summaries/engineering/data-pipelines-with-apache-airflow/06-task-dependencies/). Следующая: [Связь с внешними системами](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/).
