---
title: "Data Pipelines with Apache Airflow, глава 4: Asset-aware scheduling"
head:
  - tag: title
    content: "Airflow assets: запуск DAG по событию данных | Инжиниринг Данных"
description: "Конспект главы 4 Data Pipelines with Apache Airflow на русском. Assets, producer и consumer DAG, asset events, extra metadata, несколько assets, AssetOrTimeSchedule."
sidebar:
  order: 4
  label: "4. Asset-aware scheduling"
tags:
  - books
  - airflow
  - scheduling
  - assets
---

**Главная мысль:** вместо общего расписания связывайте DAG через `asset`. Producer DAG обновляет asset. Airflow сам запускает consumer DAG, когда данные готовы.

![Producer DAG обновляет asset, Airflow запускает три consumer DAG](/assets/data-pipelines-with-apache-airflow/ch04-asset-flow.png)

## Проблема: много команд, одни данные

Три команды (analytics, marketing, monitoring) читают события из одного API. Есть три пути.

| Путь | Проблема |
|---|---|
| Каждая команда качает данные сама | Лишняя нагрузка на API. Логику правят в трёх местах. Цифры расходятся |
| Один producer DAG, consumer по расписанию "чуть позже" | Хрупко. Если producer задержался, consumer берёт неполные данные. Если данных нет, он всё равно работает |
| Producer сам запускает consumer DAG | Тесная связь. Producer знает всех потребителей и хранит их список вручную |

Asset-aware scheduling убирает эти проблемы.

## Что такое asset

- `Asset` это виртуальная ссылка на данные: таблица, файл, ML-модель.
- Его идентифицирует URI, например `s3://bucket/events.csv`.
- Airflow считает URI просто строкой. Он не проверяет, что там лежит.
- Лучше использовать настоящий URI в общем хранилище. Тогда все потребители понимают, о чём речь.

Роли DAG:

- **Producer** указывает asset в `outlets` задачи. Когда задача успешно закончилась, Airflow создаёт `asset event`.
- **Consumer** указывает asset в `schedule`. Airflow запускает его на каждое обновление и передаёт события.

Добавить ещё одного потребителя просто: новый DAG ссылается на тот же asset. Producer не меняется.

Asset не знает о времени. Поэтому подход можно смешать с расписанием: producer идёт по cron, consumers идут по событиям.

## Producer: как создать событие

- Создайте объект `Asset("...")`.
- Передайте его в `outlets` задачи, которая обновляет данные.
- Расписание producer может остаться по времени.
- События видно в UI на вкладке Assets: слева связи DAG и asset, справа список событий.

## Consumer: как получить событие

- Вместо расписания пишем `schedule=[asset]`.
- У такого DAG нет `logical_date` и `data_interval`. Шаблоны с ними дадут `UndefinedError`.
- Откуда тогда знать, какой кусок данных брать? Из контекста `triggering_asset_events`.
- Это словарь: ключ это asset, значение это список событий. Один asset может создать несколько событий.

Как узнать дату данных:

| Способ | Как работает | Риск |
|---|---|---|
| `source_dag_run.logical_date` | Берём дату из запуска producer | Работает, только если producer по расписанию. Автор книги пишет, что в Airflow 3 атрибут пропал (баг на момент выхода) |
| `extra` в событии | Producer кладёт дату в метаданные, consumer читает | Нужно договориться о полях |

## Extra: метаданные события

- Producer отдаёт `Metadata(asset, extra={...})` из функции задачи.
- Consumer читает `.extra.<поле>` из события.
- Поля `extra` это часть data contract. Если producer их переименует, consumer сломается. Согласуйте их заранее.

## Пропуск обновления

- По умолчанию успешная задача с `outlets` всегда создаёт событие.
- Иногда данные не изменились. Тогда выбросьте `AirflowSkipException`.
- Задача станет `skipped`, события не будет, consumers не запустятся.
- Пример: файл за эту дату уже есть, значит повторять не надо.

## Несколько assets

- `schedule=[a, b]` значит AND: запуск, когда оба asset получили событие после прошлого запуска.
- Порядок событий не важен. Два события от одного asset не заменяют событие от второго.
- Условия задают операторы: `a | (b & c)`. `&` это AND, `|` это OR. Не усложняйте выражения.
- Чтобы взять событие конкретного asset, обращайтесь к `triggering_asset_events` по ключу `Asset(uri)`. Книга делает для этого маленький macro.

![Consumer ждёт события от двух assets и запускается, когда пришли оба](/assets/data-pipelines-with-apache-airflow/ch04-multi-assets.png)

Важная оговорка: Airflow не сверяет даты. Он запустит consumer на любую комбинацию событий. Если нужны данные за один день из обоих источников, проверяйте это сами.

## Время плюс assets

- `AssetOrTimeSchedule(timetable=..., assets=[...])` запускает DAG по событию или по cron.
- Подходит, когда нужна быстрая реакция и регулярная проверка.
- Осторожно: у разных timetable разная семантика (data interval есть не у всех).

## Пример кода

Проверено на Airflow 3.4: оба DAG загружаются, producer проходит `airflow dags test` и пишет событие с `extra`.

Producer и consumer. Имена придуманы для примера.

```python
import pendulum
from airflow.sdk import DAG, Asset, Metadata, task

orders = Asset("s3://shop-lake/raw/orders")

with DAG(
    dag_id="orders_producer",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
):
    @task(outlets=[orders])
    def load_orders(logical_date=None):
        # ... загрузить заказы за день ...
        yield Metadata(orders, extra={"day": logical_date.strftime("%Y-%m-%d")})

    load_orders()

with DAG(
    dag_id="orders_report",
    schedule=[orders],
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
):
    @task
    def build_report(triggering_asset_events=None):
        events = triggering_asset_events[orders]
        print("Строим отчёт за", events[0].extra["day"])

    build_report()
```

Условное расписание:

```python
from airflow.sdk import Asset

a, b, c = Asset("s3://x/a"), Asset("s3://x/b"), Asset("s3://x/c")
schedule = a | (b & c)  # запуск: событие a, либо события b и c
```

## Ключевые термины

| Термин | Значение |
|---|---|
| `asset` | Виртуальная ссылка на данные с уникальным URI |
| `outlets` | Параметр задачи: какие assets она обновляет |
| `asset event` | Событие "asset обновлён". Создаётся после успешной задачи |
| Producer DAG | DAG, который создаёт или обновляет asset |
| Consumer DAG | DAG, который запускается по событиям asset |
| `triggering_asset_events` | Переменная контекста со списком событий, которые запустили DAG |
| `Metadata` / `extra` | Дополнительные данные в событии |
| `AirflowSkipException` | Пропуск задачи без события |
| `AssetOrTimeSchedule` | Запуск по времени или по событию |

## Что это значит на практике

- Делите большие пайплайны на producer и consumer DAG. Тогда команды независимы.
- Не гадайте с расписанием "через час после загрузки". Используйте asset.
- Пишите в `extra` дату или партицию. Считайте эти поля контрактом.
- Не создавайте событие, если данные не изменились. Иначе consumers будут работать вхолостую.
- Если consumer ждёт два источника, добавьте проверку, что даты совпадают.
- Смена расписания producer может сломать consumer, который берёт дату из `logical_date` producer.

## Вопросы для самопроверки

1. Почему общее расписание хуже связи через asset?
2. Чем отличается `outlets` от `schedule=[asset]`?
3. Почему в consumer DAG нет `logical_date` и как получить дату данных?
4. Когда запустится DAG с `schedule=[a, b]`? Как задать "a или b"?

Предыдущая: [Time-based scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/). Следующая: [Templating и контекст](/book-summaries/engineering/data-pipelines-with-apache-airflow/05-templating-context/).
