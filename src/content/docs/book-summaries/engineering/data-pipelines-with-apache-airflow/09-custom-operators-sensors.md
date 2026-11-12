---
title: "Data Pipelines with Apache Airflow, глава 9: Свои operators и sensors"
head:
  - tag: title
    content: "Свои hooks, operators и triggers в Airflow | Инжиниринг Данных"
description: "Конспект главы 9 Data Pipelines with Apache Airflow на русском. Custom hook, operator, sensor, deferrable operator, trigger, упаковка в Python-пакет."
sidebar:
  order: 9
  label: "9. Свои operators"
tags:
  - books
  - airflow
  - operators
  - hooks
  - triggerer
---

**Главная мысль:** если для системы нет готового оператора или код повторяется в разных DAG, вынесите его в свои классы. Логика доступа идёт в `hook`, действие в `operator`, ожидание в `sensor`. Долгое ожидание отдавайте `triggerer`.

![Слои custom-компонентов: hook скрывает API, operator и sensor используют hook, DAG вызывает их](/assets/data-pipelines-with-apache-airflow/ch09-layers.png)

## Начинаем с PythonOperator

Пример книги: рекомендательная система для фильмов. Данные о рейтингах дают через REST API (набор MovieLens). Нужен ежедневный импорт и рейтинг популярных фильмов.

API умеет:

- пагинацию через `limit` и `offset`, поле `total` показывает общее число записей;
- фильтр по датам `start_date` и `end_date`;
- basic-авторизацию.

Первая версия на `PythonOperator` требует много кода:

1. Сессия `requests` с логином и паролем.
2. Функция с пагинацией. Она использует `yield from`, поэтому читает страницы лениво.
3. Функция, которая пишет результат в JSON-файл с датой в имени.
4. Вторая task считает рейтинг фильмов в `pandas`.

Параметры передают через `templates_dict` и template вида `{{ data_interval_start | ds }}`. Работает, но большая часть кода про доступ к API, а не про бизнес-логику. Этот код трудно переиспользовать.

## Custom hook

`Hook` - класс, который хранит всю логику работы с внешней системой. Любой hook наследуется от `BaseHook`.

Что делает hook:

- Получает адрес и пароль по `conn_id` из Airflow Connections. В DAG нет секретов.
- Метод `get_conn()` создаёт подключение. Метод `get_connection()` из `BaseHook` читает данные из metastore.
- Значения по умолчанию (host, port, schema) лежат в переменных класса.
- Сессию кэшируют в атрибутах `_session` и `_base_url`. Иначе каждый вызов идёт в metastore.
- Публичные методы, например `get_ratings()`, прячут детали. Пагинация живёт в приватном методе.

Совет авторов: не вызывайте `get_conn()` снаружи hook. Это раскрывает внутреннее устройство и связывает ваш код с типом подключения.

Где хранить код: пакет `custom` рядом с папкой `dags` (например `custom/hooks.py`). Потом `from custom.hooks import MovielensHook`. 

## Custom operator

Hook убрал сложность API. Но в DAG ещё остаётся шаблонный код: даты, запись файла. Его убирает operator.

- Наследуйтесь от `BaseOperator`.
- В `__init__` принимайте свои аргументы и передавайте `**kwargs` в `super().__init__`. Так работают `retries`, `retry_delay` и другие общие аргументы.
- Логика живёт в методе `execute(self, context)`.
- Закрывайте hook в блоке `finally`, даже если запрос упал.
- Чтобы значения принимали Jinja-шаблоны, перечислите их в `template_fields`.

Без `template_fields` операция работает только с жёстко заданными датами. С ними оператор получает `data_interval_start` и `data_interval_end`.

## Custom sensor

`Sensor` наследуется от `BaseSensorOperator`. Вместо `execute` вы пишете метод `poke(context)`. Он возвращает `True` или `False`.

- `True` - sensor завершён, downstream tasks стартуют.
- `False` - sensor ждёт и проверяет снова, пока не истечёт `timeout`.

В примере sensor проверяет, есть ли хотя бы один рейтинг за интервал. Он берёт первый элемент генератора через `next()`. Если пусто, возникает `StopIteration`, и метод возвращает `False`. Hook делает код короткой и понятной. Hook нужно закрыть в `finally`.

В DAG sensor ставят перед fetch: `wait_for_ratings >> fetch_ratings >> rank_movies`.

## Custom deferrable operator

Проблема: каждый долгий task занимает worker slot, хотя работает внешняя система. Если у вас 10 workers и 100 Spark job по часу, всё идёт пачками по 10.

`Triggerer` решает это. Один процесс на `asyncio` ведёт сотни ожидающих tasks. Но есть условие: код ожидания должен быть асинхронным. Например, `boto3` не поддерживает async.

![Как работает deferrable sensor: worker вызывает defer, triggerer ждёт, затем worker завершает task](/assets/data-pipelines-with-apache-airflow/ch09-deferrable.png)

Порядок выполнения:

1. Worker запускает `execute()`. Он вызывает `self.defer(trigger=..., method_name=...)`.
2. Task переходит в состояние `deferred`. Worker slot свободен.
3. `Triggerer` выполняет `async run()` у trigger. Там `await asyncio.sleep(...)` между проверками.
4. Когда условие выполнено, trigger отдаёт `TriggerEvent`.
5. Task возвращается на worker. Выполняется метод из `method_name` (`execute_complete`).
6. Scheduler отмечает task как `success`.

Trigger состоит из двух частей:

| Метод | Зачем |
|---|---|
| `serialize()` | Возвращает путь к классу и аргументы. По ним Airflow пересоздаёт trigger, даже в другом процессе |
| `async run()` | Асинхронно ждёт и отдаёт `TriggerEvent` |

Важные детали:

- Выигрыш даёт только асинхронная часть. Тяжёлый синхронный код в `run()` блокирует весь `triggerer`.
- Deferrable sensor наследуется от `BaseOperator`, а не от `BaseSensorOperator`: метод `poke` не нужен.
- Два способа организации: один класс с параметром `deferrable` или отдельный класс. Второй проще.

Предупреждение: в листинге книги флаг `found_records` в начале равен `True`, и цикл `while not found_records` никогда не выполнится. Это похоже на ошибку в примере. В своём коде начинайте с `False`.

## Упаковка в Python-пакет

Папка `custom` в `dags` подходит для старта. Для общего использования лучше пакет.

- Структура `src/<package>/` с файлами `hooks.py`, `operators.py`, `sensors.py` и `setup.py` с метаданными (`name`, `version`, `install_requires`, `packages`, `package_dir`).
- Установка: `pip install ./airflow-movielens`.
- Пакет и зависимости должны стоять во всех окружениях Airflow: scheduler, web server, workers (и triggerer для trigger).
- Как делиться: `pip install git+https://...`, PyPI или приватный индекс, общая папка.
- Лучше добавить operator в существующий open source provider. Свой provider - самый трудный путь.

Альтернатива: не расширять Airflow, а запускать задачи в контейнерах (`DockerOperator`, `KubernetesPodOperator`). Установка Airflow остаётся лёгкой, зависимости живут в контейнере. Это тема главы 11.

## Пример кода

Проверено на Airflow 3.4 в pytest: hook с mock, operator уходит в `defer`, trigger отдаёт `TriggerEvent`.

Hook и deferrable operator вокруг выдуманного API заказов.

```python
import requests
from airflow.sdk import BaseHook


class ShopApiHook(BaseHook):
    def __init__(self, conn_id):
        super().__init__()
        self._conn_id = conn_id
        self._session = None
        self._base_url = None

    def _connect(self):
        if self._session is None:
            conf = self.get_connection(self._conn_id)
            self._base_url = f"https://{conf.host}"
            self._session = requests.Session()
            self._session.auth = (conf.login, conf.password)
        return self._session, self._base_url

    def get_orders(self, day):
        session, base = self._connect()
        resp = session.get(f"{base}/orders", params={"day": day})
        resp.raise_for_status()
        return resp.json()["items"]

```

Deferrable-вариант. Здесь trigger сам проверяет условие в цикле.

```python
import asyncio

from airflow.sdk import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent


class OrdersReadyTrigger(BaseTrigger):
    def __init__(self, conn_id, day, pause=30):
        super().__init__()
        self.conn_id, self.day, self.pause = conn_id, day, pause

    def serialize(self):
        return (
            "my_package.triggers.OrdersReadyTrigger",
            {"conn_id": self.conn_id, "day": self.day, "pause": self.pause},
        )

    async def run(self):
        found = False
        while not found:
            found = await self._has_orders()
            if not found:
                await asyncio.sleep(self.pause)
        yield TriggerEvent({"day": self.day})

    async def _has_orders(self):
        # Здесь должен быть асинхронный запрос к API.
        return False


class WaitForOrdersAsync(BaseOperator):
    template_fields = ("day",)

    def __init__(self, conn_id, day="{{ ds }}", **kwargs):
        super().__init__(**kwargs)
        self.conn_id, self.day = conn_id, day

    def execute(self, context):
        self.defer(
            trigger=OrdersReadyTrigger(self.conn_id, self.day),
            method_name="execute_complete",
        )

    def execute_complete(self, context, event):
        self.log.info("Orders are ready for %s", event["day"])
```

## Ключевые термины

| Термин | Значение |
|---|---|
| `BaseHook` | Базовый класс для hooks. Даёт `get_connection()` |
| `BaseOperator` | Базовый класс operators. Нужен метод `execute()` |
| `template_fields` | Список атрибутов, в которых работает Jinja |
| `poke()` | Возвращает `True`, если условие выполнено |
| `defer()` | Передаёт ожидание процессу `triggerer` |
| `BaseTrigger` | Базовый класс trigger. Методы `serialize()` и `async run()` |
| `execute_complete` | Метод, который работает после завершения trigger |

## Что это значит на практике

- Если один и тот же код доступа к API есть в трёх DAG, пора писать hook.
- Не забывайте `template_fields`. Без них operator не примет `{{ ds }}`.
- Для долгих ожиданий (Spark, внешний API) пишите deferrable-версию. Проверьте, что клиент умеет `async`.

## Вопросы для самопроверки

1. Что должен делать hook, а что operator? Почему не писать всё в одном месте?
2. Зачем нужен `template_fields`? Что будет без него?
3. Какие шаги проходит deferrable task от `defer()` до `success`? Что делают `serialize()` и `run()`?
4. Как поделиться custom-компонентами с командой и что нужно проверить при установке?

Предыдущая: [Связь с внешними системами](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/). Следующая: [Testing](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/).
