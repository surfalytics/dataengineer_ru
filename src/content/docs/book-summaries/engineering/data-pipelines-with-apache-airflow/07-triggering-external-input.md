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

## О чём глава

Как запускать DAG от событий вне Airflow? В [главе 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/) мы запускали DAG по времени, в [главе 4](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/) по обновлению `Asset`. Теперь триггер приходит снаружи: файл, коммит, сообщение в шине. Темы: sensors, CLI и REST API, очереди сообщений.

![Четыре способа запустить DAG от внешнего события: sensor, CLI, REST API и сообщение в очереди](/assets/data-pipelines-with-apache-airflow/ch07-triggers.png)

## Опрос условий с помощью sensors

Пример автора: мобильное приложение с купонами. Четыре сети супермаркетов каждый день выкладывают файлы с акциями в общее хранилище. Акции готовят вручную, поэтому файлы приходят в случайное время, обычно с 16:00 до 2:00 ночи. Гарантии нет.

В DAG `copy_to_raw` копирует файл каждого супермаркета в сырое хранилище, откуда результат всегда можно пересчитать. Затем `process_supermarket_N` кладёт данные в базу приложения. В конце `create_metrics` считает метрики.

Если запускать DAG в 2:00, чтобы точно все данные были на месте, получается долгое ожидание. Первый супермаркет прислал файл в 16:30, обработка началась в 2:00: данные лежали 9,5 часа.

![Запуск DAG в 02:00 против sensors: данные ждут часами или обрабатываются сразу](/assets/data-pipelines-with-apache-airflow/ch07-wait-timeline.png)

Решение в Airflow: `sensor`. Это особый подкласс `operator`. Sensor регулярно проверяет условие. Если оно верно, task получает `success`. Если нет, sensor ждёт и пробует снова, пока условие не выполнится или не наступит `timeout`. Одна проверка — `poke`. Пример: `FileSensor` проверяет, что файл существует. Пауза между проверками задаётся `poke_interval`, по умолчанию 60 секунд.

Автор предупреждает: слишком малый `poke_interval` (например, 2 секунды при ответе системы в 2 секунды) перегрузит внешнюю систему.

В DAG расписание ставят на начало окна прихода данных, а не на его конец. Перед обработкой каждого супермаркета стоит свой sensor. Готовая ветка идёт дальше сразу, остальные ждут.

### Свои условия: PythonSensor

Набор данных часто приходит несколькими файлами: `data-01.csv`, `data-02.csv`. `FileSensor` понимает шаблон `data-*.csv`, но сработает уже на первом файле, пока остальные грузятся. Обработается неполный набор.

Поэтому договариваются о маркере. Супермаркет пишет файл `_SUCCESS` последним. Нужно проверить два условия: есть файлы `data-*.csv` и есть `_SUCCESS`. Автор советует не усложнять шаблон для `FileSensor`, а написать две проверки в `PythonSensor`.

`PythonSensor` похож на `PythonOperator`, но функция должна вернуть только `True` или `False`. В маркер можно записать и метаданные: число записей, ошибки.

Наша версия с выдуманными именами. Функцию можно проверить без Airflow.

```python
from pathlib import Path


def batch_is_ready(folder):
    path = Path(folder)
    has_data = any(path.glob("part-*.csv"))
    return has_data and (path / "_DONE").exists()
```

```python
wait_a = PythonSensor(
    task_id="wait_partner_a",
    python_callable=batch_is_ready,
    op_kwargs={"folder": "/landing/partner_a"},
    poke_interval=300,
    timeout=timedelta(hours=10),   # вместо 7 дней по умолчанию
    mode="reschedule",             # между проверками слот свободен
)
```

Полный DAG: [ch07_sensor_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch07_sensor_dag.py).

### Что, если данных нет: sensor deadlock

Что, если супермаркет не прислал файл? Sensor упадёт по `timeout`. Но по умолчанию это 7 дней.

DAG идёт раз в день. Каждый день добавляются новые sensors для молчащих супермаркетов, а старые ещё живут. Число одновременных tasks ограничено: на DAG, на весь Airflow. На один DAG по умолчанию 16 tasks (`max_active_tasks`).

Пример автора. Супермаркет 1 присылает данные, а 2, 3 и 4 молчат:

- День 1: ждут 3 sensors, занято 3 слота. День 2: занято 6. День 5: занято 15.
- День 6: занято 16. Новые tasks не стартуют.

Это называют `sensor deadlock`: все слоты заняты sensors, а им ждать нечего. Если лимит исчерпан в одном DAG, остальные работают. Если исчерпан глобальный лимит, встаёт вся система.

Способы защиты:

- Задайте разумный `timeout`.
- Используйте `mode="reschedule"`: sensor освобождает слот между проверками. В режиме `poke` (по умолчанию) слот занят всё время, даже когда sensor ничего не делает.
- Возьмите deferrable operators.
- Настройте `max_active_tasks` и глобальные лимиты (глава 15 книги).

![Что делает worker slot при poke, reschedule и deferrable](/assets/data-pipelines-with-apache-airflow/ch07-slots.png)

В режиме `poke` слот занят всё время. В `reschedule` он занят только на проверку. У deferrable operator слот свободен, пока ждёт `triggerer`.

### Deferrable operators

Ожидающий deferrable operator отдаёт работу компоненту `triggerer` и освобождает worker. Triggerer запускает асинхронный код (`asyncio`) и ждёт много событий в одном процессе. Когда условие выполнено, task возвращается на worker.

- У таких operators суффикс `Async` или аргумент `deferrable=True`.
- Нужен хотя бы один процесс `triggerer`: вообще он необязателен, но для deferrable обязателен.
- `PythonOperator` и TaskFlow-tasks нельзя сделать deferrable. Они синхронные: идут до конца и всё время держат слот.

## Запуск через CLI и REST API

DAG можно запустить и снаружи, например из CI/CD. Или AWS Lambda вызывает API, когда в S3 появился файл. Sensors с постоянным опросом тогда не нужны.

CLI: `airflow dags trigger dag1`. Run получает `run_id` с префиксом `manual__` и `run_type = manual`.

Команда принимает параметры: `airflow dags trigger --conf '{"supermarket_id": 1}' dag1`. Эта конфигурация (`conf`) доступна во всех tasks этого run через контекст: `context["dag_run"].conf`.

`conf` упрощает DAG: не нужно копировать tasks ради разных значений.

Есть важное ограничение. Run по расписанию не имеет `conf`. Поэтому DAG, который опирается на `conf`, нельзя ставить на расписание. Ставьте `schedule=None`.

REST API даёт тот же результат, если нет доступа к CLI, но есть HTTP. Запрос: `POST /dags/<dag_id>/dagRuns` с телом `{"conf": {...}}`. Тело нужно всегда, даже пустое `{"conf": {}}`. Пароль в `curl` открытым текстом, как в книге, плохая практика: используйте другую аутентификацию.

Через API можно сообщить и об обновлении `Asset`: `POST` в endpoint событий (`datasets/events/`). Airflow запустит DAG, которые зависят от asset.

Наш DAG с `conf` и запуск через `dags test`:

```python
@task
def process(**context):
    conf = context["dag_run"].conf
    print("обрабатываем супермаркет:", conf["supermarket_id"])
```

```bash
airflow dags test ch07_conf_demo --conf '{"supermarket_id": 1}'
```

```text
обрабатываем супермаркет: 1
state=success, run_type=manual
```

Полный DAG: [ch07_conf_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch07_conf_dag.py).

## Запуск по сообщениям

Во многих компаниях есть очереди для near-real-time. Одно сообщение несёт один факт, например банковскую транзакцию. Примеры: Apache Kafka, RabbitMQ, Google Cloud Pub/Sub, Azure Event Hubs.

Очередь может запускать DAG, если часть сообщений означает «пора работать». Вместо `_SUCCESS` и `FileSensor` каждый супермаркет шлёт в очередь сообщение «загрузка завершена». Пример автора на Kafka, другие очереди работают так же.

Шаги:

1. Создайте `MessageQueueTrigger`. Он знает, где очередь и какой topic читать.
2. Добавьте `apply_function`. Она фильтрует сообщения. Если вернула `True`, DAG нужно запустить.
3. Оберните trigger в `AssetWatcher` и привяжите к `Asset`.
4. Передайте этот `Asset` в `schedule` DAG.

![Путь сообщения из Kafka до запуска DAG](/assets/data-pipelines-with-apache-airflow/ch07-kafka-asset.png)

> **Пояснение:** в книге адрес очереди задан строкой `queue="kafka://kafka:9092/events"`. В актуальном provider этот параметр устарел. Мы указываем `scheme="kafka"` и `topics`, а адрес брокера лежит в Airflow connection.

```python
trigger = MessageQueueTrigger(
    scheme="kafka",
    topics=["uploads"],
    apply_function="ch07_kafka_dag.only_done",
    kafka_config_id="kafka_default",
)
uploads = Asset("uploads_topic", watchers=[AssetWatcher(name="uploads_watcher", trigger=trigger)])

with DAG(dag_id="ch07_on_upload", schedule=[uploads]):
    ...
```

Старт может задержаться: consumer читает очередь с фиксированным интервалом.

Минус подхода: нужна дополнительная инфраструктура. Плюс: можно связать два экземпляра Airflow. DAG в экземпляре A пишет сообщение, DAG в экземпляре B стартует. Очередь служит интерфейсом, и API наружу открывать не нужно.

## Итоги главы

- Sensor проверяет условие по кругу, пока оно не станет `True` или не выйдет `timeout`.
- `PythonSensor` вызывает вашу функцию. Маркер `_SUCCESS` защищает от неполных данных.
- `timeout` по умолчанию 7 дней. В ежедневном DAG это ведёт к sensor deadlock.
- `mode="reschedule"` и deferrable operators освобождают slot во время ожидания.
- `PythonOperator` и TaskFlow-tasks нельзя сделать deferrable.
- DAG можно запустить через CLI или REST API. `conf` передаёт параметры, но такой DAG нельзя ставить на расписание.
- `MessageQueueTrigger` с `AssetWatcher` запускает DAG от сообщения. Так можно связать и два экземпляра Airflow.

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
- Следите за `poke_interval`: частый опрос нагружает внешнюю систему.

## Практика

Статус проверок: [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md). Airflow 3.4.0, Python 3.12. Kafka-DAG только разобран (DagBag). Настоящую очередь не запускали: нужен брокер Kafka.

Проверка условия и расчёт sensor deadlock ([ch07_check_sensor.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch07_check_sensor.py)):

```text
пустая папка: False
данные есть, маркера нет: False
данные и маркер: True

День | занято слотов sensors
   1 | 3
   2 | 6
   3 | 9
   4 | 12
   5 | 15
   6 | 16  <- лимит, новые tasks не стартуют
   7 | 16  <- лимит, новые tasks не стартуют
```

Разбор обоих DAG через DagBag:

```text
ch07_sensor_dag.py -> ch07_partner_sensors ['process_partner_a', 'wait_partner_a']
ошибки разбора: нет
ch07_kafka_dag.py -> ch07_on_upload ['copy_to_raw', 'process']
ошибки разбора: нет
```

### Задания

1. В `ch07_check_sensor.py` поставьте `waiting_per_day = 5`. На какой день занятых слотов станет 16?

<details>
<summary>Решение</summary>

Считаем: 5, 10, 15, потом 20, но лимит 16. Значит, на 4-й день. Сверьте с запуском.

</details>

2. Запустите `dags test` с другим `conf` (`{"supermarket_id": 3}`). Что будет без `--conf`?

<details>
<summary>Решение</summary>

Task напечатает «обрабатываем супермаркет: 3». Без `--conf` словарь пустой, `conf["supermarket_id"]` даёт `KeyError`, task падает. Так же упал бы run по расписанию.

</details>

## Вопросы для самопроверки

1. Чем `poke` отличается от `reschedule`? Что происходит со slot?
2. Как возникает sensor deadlock, если один поставщик не прислал данные?
3. Почему `PythonOperator` нельзя сделать deferrable?
4. Какие шаги нужны, чтобы DAG стартовал от сообщения в Kafka?

Предыдущая: [Зависимости между задачами](/book-summaries/engineering/data-pipelines-with-apache-airflow/06-task-dependencies/). Следующая: [Связь с внешними системами](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/).
