---
title: "Data Pipelines with Apache Airflow, глава 4: Asset-aware scheduling"
head:
  - tag: title
    content: "Airflow assets: запуск DAG по событию данных | Инжиниринг Данных"
description: "Конспект главы 4 Data Pipelines with Apache Airflow на русском. Assets, producer и consumer DAG, asset events, extra metadata, несколько assets."
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

## О чём глава

В [главе 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/) DAG запускались по времени. Для одного DAG это работает. Но время плохо связывает много DAG между собой. Глава вводит `asset-aware scheduling`: запуск по событию "данные обновились". Темы: `asset`, producer и consumer, события, `extra`, пропуск обновления, несколько assets.

![Producer DAG обновляет asset, Airflow запускает три consumer DAG](/assets/data-pipelines-with-apache-airflow/ch04-asset-flow.png)

*Как читать: слева producer, в центре asset, справа три consumer. Стрелки справа Airflow рисует сам.*

## Проблема: много команд, одни данные

В главе 3 мы забирали события пользователей из API. Теперь те же данные нужны аналитике, маркетингу и мониторингу. Есть три пути.

| Путь | Проблема |
|---|---|
| Каждая команда качает данные сама | Лишняя нагрузка на API. Логику правят в трёх местах. Цифры расходятся |
| Один producer DAG, consumer по расписанию "чуть позже" | Хрупко. Если producer задержался, consumer берёт неполные данные. Если данных нет, он всё равно работает |
| Producer сам запускает consumer DAG | Тесная связь. Producer знает всех потребителей и держит их список вручную |

Asset-aware scheduling снимает эти проблемы.

## Что такое asset

`Asset` это виртуальная ссылка на данные: таблицу, файл, ML-модель. Его идентифицирует URI, например `s3://example_bucket/example.csv`.

- Airflow считает URI просто строкой. Он не проверяет, что лежит по адресу.
- Автор советует настоящий URI в общем хранилище. Тогда все потребители понимают, о чём речь.

Исходный DAG делится на две части:

- **Producer** указывает asset в `outlets` задачи. Когда задача успешно закончилась, Airflow создаёт `asset event`.
- **Consumer** указывает asset в `schedule`. Airflow запускает его на каждое обновление и передаёт ему события.

Новый потребитель добавляется просто: ещё один DAG ссылается на тот же asset. Producer не меняется.

Asset ничего не знает о времени. Поэтому он плохо подходит для DAG с жёстким расписанием. Но подходы смешивают: producer идёт по cron, consumers идут по событиям.

## Producer: как создать событие

Producer остаётся как в главе 3, с расписанием по времени. Нужно создать `Asset("...")` и передать его в `outlets` задачи, которая обновляет данные. События видно в UI на вкладке Assets: слева связи DAG и asset, справа список событий.

## Consumer: как получить событие

Меняем расписание на `schedule=[asset]`. Каждое новое событие запускает DAG. Но шаблон `{{ logical_date | ds }}` из главы 3 теперь даёт `UndefinedError`. У DAG, запущенного событием, нет `logical_date` и `data_interval`. Это логично: у него нет расписания по времени.

Возникает вопрос: какой кусок данных брать? Ответ в `triggering_asset_events` из контекста. Это словарь. Ключ это asset, значение это список событий. Событий может быть несколько, и assets тоже.

Дату данных можно получить двумя путями:

| Способ | Как работает | Риск |
|---|---|---|
| `source_dag_run.logical_date` | Берём дату из запуска producer, который создал событие | Работает, только пока producer идёт по расписанию. В Airflow 3 на момент выхода книги этот атрибут пропал из-за ошибки |
| `extra` в событии | Producer кладёт дату в метаданные, consumer читает | Нужно договориться о полях |

Автор предупреждает: если сменить тип расписания producer (например, на ручной запуск), `logical_date` исчезнет, и consumer сломается.

## Extra: метаданные события

Событие несёт словарь `extra` с любыми значениями. Producer возвращает `Metadata(asset, extra={...})` из функции задачи. Consumer читает `.extra.<поле>` у события.

> **Пояснение:** поля `extra` это часть data contract. Если producer переименует `day`, все consumers сломаются. Согласуйте поля заранее, как схему таблицы.

## Пропуск обновления

Успешная задача с `outlets` всегда создаёт событие. Иногда данные не изменились: в источнике нет нового. Тогда задача выбрасывает `AirflowSkipException`.

Задача получает статус `skipped` (глава 6). События нет, consumers не запускаются. Книга проверяет, есть ли уже файл за эту дату: если да, consumers уже отработали. Автор оговаривает, что в других случаях это допущение может быть неверным.

## Несколько assets

DAG может зависеть от нескольких assets. Типичный случай: consumer объединяет два набора данных. Тогда `schedule=[a, b]`.

- По умолчанию это AND: запуск, когда **оба** asset получили событие после прошлого запуска.
- Порядок не важен. Много событий одного asset не заменяют событие второго.
- Условия задают операторы: `&` это AND, `|` это OR. Например, `a | (b & c)`. Автор просит не усложнять выражения.
- Чтобы взять событие нужного asset, обращаемся к `triggering_asset_events[Asset(uri)]`. Книга оформляет это маленьким macro `get_event` (макросы разберём в главе 5).

![Consumer ждёт события от двух assets и запускается, когда пришли оба](/assets/data-pipelines-with-apache-airflow/ch04-multi-assets.png)

*Как читать: звёзды это события. Consumer стартует только после события от каждого asset.*

Главная оговорка: Airflow не сверяет даты. Он запустит consumer на любую комбинацию событий. Если нужны данные за один день из обоих источников, проверяйте это сами.

## Время плюс assets

`AssetOrTimeSchedule(timetable=..., assets=[...])` запускает DAG либо по событию, либо по cron. Это нужно, когда DAG должен быстро реагировать на новые данные и ещё регулярно что-то проверять. Осторожно: у разных timetable разная семантика, например data interval есть не у всех. DAG должен это учитывать.

## Код: producer, consumer и два assets

Наш пример с заказами. Полный файл: [ch04_asset_dags.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch04_asset_dags.py).

```python
orders = Asset("s3://shop-lake/raw/orders")

# Producer: по расписанию, обновляет asset и кладёт дату в extra
with DAG(dag_id="orders_producer", schedule="@daily", start_date=START):

    @task(outlets=[orders])
    def load_orders(logical_date=None):
        yield Metadata(orders, extra={"day": logical_date.strftime("%Y-%m-%d")})

    load_orders()
```

```python
# Consumer: нет расписания по времени, запуск по событию asset
with DAG(dag_id="orders_report", schedule=[orders], start_date=START):

    @task
    def build_report(triggering_asset_events=None):
        events = triggering_asset_events[orders]
        print("Строим отчёт за", events[0].extra["day"])

    build_report()
```

Проверка без сервера: [ch04_check_asset_dags.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch04_check_asset_dags.py). Она разбирает DAG в `DagBag` и запускает producers через `airflow dags test`. Второй producer без данных пропускает обновление.

```text
ошибки импорта: нет
orders_producer -> @daily
orders_report -> ['s3://shop-lake/raw/orders']
payments_producer -> @daily
revenue_report -> ['s3://shop-lake/raw/orders', 's3://shop-lake/raw/payments']
dags test producer: state=success
asset event: s3://shop-lake/raw/orders {'day': '2025-01-02'}
всего событий: 1 (payments пропущен, события нет)
```

Ошибок нет. Событие несёт `extra`. Пропущенный producer события не создал. Сам consumer не запускали: его запускает scheduler.

## Итоги главы

- Asset-aware scheduling запускает DAG по доступности данных, а не по времени.
- Producer готовит данные. Consumer реагирует на обновление.
- Asset это ссылка с URI. Producer указывает его в `outlets`, consumer в `schedule`.
- У DAG, запущенного событием, нет `logical_date`. Информацию о запуске берут из `triggering_asset_events`.
- Producer может передать данные в поле `extra`. Это часть data contract.
- `AirflowSkipException` пропускает обновление и не будит consumers.
- Несколько assets по умолчанию значат AND. Операторы `&` и `|` задают сложные условия.
- Airflow не сверяет даты событий. Проверка лежит на вас.
- `AssetOrTimeSchedule` смешивает время и assets.

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

## Практика

### Задания

**1. Сделайте OR.** В `revenue_report` нужен запуск при событии любого из двух assets. Как изменить `schedule`?

<details>
<summary>Решение</summary>

`schedule=orders | payments`. В `triggering_asset_events` будет только asset, который сработал. Читайте словарь аккуратно.

</details>

**2. Почему падает шаблон?** Consumer пишет `{{ data_interval_start | ds }}` и падает. Что делать?

<details>
<summary>Решение</summary>

У DAG, запущенного событием, нет `data_interval_start`. Producer кладёт дату в `extra`, consumer берёт её из `triggering_asset_events`.

</details>

## Вопросы для самопроверки

1. Почему общее расписание хуже связи через asset?
2. Чем отличается `outlets` от `schedule=[asset]`?
3. Почему в consumer DAG нет `logical_date` и как получить дату данных?
4. Когда запустится DAG с `schedule=[a, b]`? Как задать "a или b"?
5. Что произойдёт у consumer, если producer сменит расписание на ручной запуск?

Предыдущая: [Time-based scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/). Следующая: [Templating и контекст](/book-summaries/engineering/data-pipelines-with-apache-airflow/05-templating-context/).
