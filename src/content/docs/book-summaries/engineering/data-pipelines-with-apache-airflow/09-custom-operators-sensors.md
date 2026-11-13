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

**Главная мысль:** если для системы нет готового оператора или один код повторяется в разных DAG, вынесите его в свои классы. Логика доступа идёт в `hook`, действие в `operator`, ожидание в `sensor`. Долгое ожидание отдавайте `triggerer`, чтобы не занимать worker.

## О чём глава

В главе 8 мы пользовались готовыми операторами для внешних систем. Теперь вопрос другой: что делать, если готового оператора нет? Авторы показывают путь на одном примере. Сначала решают задачу через `PythonOperator`. Потом выносят код в hook, operator, sensor и deferrable operator. В конце упаковывают всё в Python-пакет. Предыдущая тема: [связь с внешними системами](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/).

![Слои custom-компонентов: DAG вызывает operator и sensor, они используют hook, hook читает Connection и ходит во внешний API](/assets/data-pipelines-with-apache-airflow/ch09-layers.png)

## Начинаем с PythonOperator

Пример книги: рекомендательная система для фильмов. Данные о рейтингах дают через REST API (набор MovieLens, около 34 млн оценок). Для пилота нужны два шага: ежедневно забирать новые рейтинги и строить рейтинг популярных фильмов.

API умеет три вещи:

- **Пагинация.** Параметры `limit` и `offset` выбирают страницу. Поле `total` показывает, сколько всего записей.
- **Фильтр по датам.** Параметры `start_date` и `end_date` дают инкрементальную загрузку без полной выгрузки.
- **Basic-авторизация.** Логин и пароль нужны для эндпоинта `/ratings`.

Первая версия на `PythonOperator` занимает много кода:

1. Сессия `requests` с логином и паролем. Адрес и пароль читаются из переменных окружения.
2. Функция с пагинацией. Она отдаёт записи через `yield from`, поэтому работает как ленивый генератор: следующую страницу берёт, только когда кончилась текущая.
3. Функция, которая пишет результат в JSON-файл с датой в имени. Так fetch можно перезапускать.
4. Вторая task считает рейтинг фильмов в `pandas`: средняя оценка и число оценок, с порогом по минимуму.

Это работает, но большая часть кода про доступ к API, а не про бизнес-логику. Такой код трудно переиспользовать.

## Custom hook

`Hook` — это класс, в котором лежит вся логика работы с внешней системой. Операторы переиспользуют его. Hook ещё даёт Connections: адрес и пароль хранятся в metastore и редактируются в интерфейсе, а в DAG нет секретов. Любой hook наследуется от `BaseHook`.

В `__init__` hook принимает `conn_id` и сохраняет его. Большинство hooks имеют метод `get_conn()`, который создаёт подключение. Шаги авторов такие:

1. Создайте Connection в интерфейсе (Admin > Connections): имя, тип HTTP, host, port, login, password.
2. В `get_conn()` вызовите `self.get_connection(conn_id)`. Метод из `BaseHook` читает данные из metastore.
3. Значения по умолчанию (host, schema, port) положите в переменные класса. Они работают, если поле в Connection пустое. Если поле обязательное, вместо значения по умолчанию можно поднять ошибку.
4. Закэшируйте сессию и base URL в атрибутах `_session` и `_base_url`. Иначе каждый вызов `get_conn()` идёт в metastore.
5. Спрячьте детали за публичными методами, например `get_ratings()`. Пагинация живёт в приватном методе.

Авторы предупреждают: не вызывайте `get_conn()` снаружи hook. Метод публичный, но он раскрывает внутреннее устройство и связывает ваш код с типом подключения. Пример из Airflow: `HdfsHook` был привязан к библиотеке, которая работала только на Python 2.7.

Ниже наш метод `get_orders()` для выдуманного API заказов. Он повторяет идею книги: генератор читает страницы лениво.

```python
def get_orders(self, day, batch_size=100):
    """Генератор заказов за день. Страницы читает лениво."""
    session, base = self._connect()
    offset, total = 0, None
    while total is None or offset < total:
        resp = session.get(
            f"{base}/orders",
            params={"day": day, "offset": offset, "limit": batch_size},
        )
        resp.raise_for_status()
        page = resp.json()
        yield from page["items"]
        offset += batch_size
        total = page["total"]
```

Hook кладут в пакет рядом с папкой `dags`, например `custom/hooks.py`. Тогда в DAG пишут `from custom.hooks import MovielensHook`. Код DAG после этого сильно сокращается: нужно создать hook с `conn_id` и вызвать метод. 

## Custom operator

После hook в DAG остаётся шаблонный код: даты и запись файла. Если нужен тот же шаг в других DAG, код дублируется. Эту часть берёт на себя operator.

- Наследуйтесь от `BaseOperator`.
- В `__init__` принимайте свои аргументы: `conn_id`, даты, путь. Остальные аргументы (`retries`, `retry_delay`, `task_id`) передайте через `**kwargs` в `super().__init__`. Так работают и `default_args` DAG.
- Основная логика живёт в методе `execute(self, context)`. Airflow вызывает его при запуске task. В `context` лежат все переменные контекста.
- Hook закрывайте в `finally`, даже если запрос упал. Так вы не оставите открытые сессии.

Первая версия принимает жёстко заданные даты. Она всегда берёт один и тот же период. Чтобы значения принимали Jinja-шаблоны, перечислите их в `template_fields`. Тогда Airflow подставит `data_interval_start` и `data_interval_end` до вызова `execute`. В книге в этом списке стоят атрибуты с подчёркиванием, у нас имена без него.

```python
class OrdersFetchOperator(BaseOperator):
    """Забирает заказы за день и пишет их в JSON."""

    template_fields = ("day", "output_path")  # в этих полях работает Jinja

    def __init__(self, conn_id, output_path, day="{{ ds }}", **kwargs):
        super().__init__(**kwargs)  # retries, retry_delay и другие общие аргументы
        self.conn_id, self.output_path, self.day = conn_id, output_path, day

    def execute(self, context):
        hook = OrdersHook(self.conn_id)
        try:
            orders = list(hook.get_orders(self.day))
        finally:
            hook.close()  # закрываем, даже если запрос упал
        self.log.info("Fetched %s orders for %s", len(orders), self.day)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(orders, f)
        return len(orders)
```

## Custom sensor

Sensor — это особый operator, который ждёт условие. Он наследуется от `BaseSensorOperator`. Вместо `execute` вы пишете метод `poke(context)`, и он возвращает `True` или `False`.

- `True`: sensor завершён, downstream tasks стартуют.
- `False`: sensor ждёт несколько секунд и проверяет снова. Так до успеха или до `timeout`.

В примере sensor проверяет, есть ли хотя бы один рейтинг за интервал. Все записи читать не нужно. Sensor берёт первый элемент генератора через `next()`. Если генератор пуст, возникает `StopIteration`, и метод возвращает `False`. Hook делает код коротким.

В DAG sensor ставят перед fetch: `wait_for_ratings >> fetch_ratings >> rank_movies`. Об обычных sensors и `mode="reschedule"` мы говорили в [главе 7](/book-summaries/engineering/data-pipelines-with-apache-airflow/07-triggering-external-input/).

## Custom deferrable operator

Долгие tasks (Spark job на час, большой файл по FTP, ожидание файла в S3) занимают worker slot, хотя вся работа идёт во внешней системе. В главе 6 это называлось sensor deadlock. Режим `reschedule` решал проблему для sensors, но для обычных операторов такого режима нет. Если у вас 10 workers и 100 Spark job по часу, всё идёт пачками по 10, и на всё нужно не меньше 10 часов.

![Обычные tasks держат по worker slot, deferrable tasks ждёт один triggerer](/assets/data-pipelines-with-apache-airflow/ch09-worker-slots.png)

Решение: `deferrable operators` и компонент `triggerer`. Это один процесс на `asyncio`. Он ведёт сотни и тысячи ожидающих tasks. Triggerer сам работу не делает: он следит за внешней системой.

У этого пути есть условие: код ожидания должен быть асинхронным. Например, `boto3` не поддерживает async, и сразу получить выигрыш нельзя.

Deferrable operator можно сделать двумя способами. Первый: один класс с параметром `deferrable`, где живут обе версии логики. Второй: отдельный класс только для deferrable. Авторы считают второй способ проще. Обычно такой класс получает суффикс `Async`, но это не правило.

![Как работает deferrable sensor: worker вызывает defer, triggerer ждёт, затем worker завершает task](/assets/data-pipelines-with-apache-airflow/ch09-deferrable.png)

Порядок выполнения у deferrable sensor такой:

1. Worker запускает `execute()`. Метод вызывает `self.defer(trigger=..., method_name=...)`. Можно указать и `timeout`.
2. Task переходит в состояние `deferred`. Worker slot свободен.
3. Triggerer выполняет `async run()` у trigger. Между проверками стоит `await asyncio.sleep(...)`.
4. Когда условие выполнено, trigger отдаёт `TriggerEvent`.
5. Task возвращается на worker, и выполняется метод из `method_name` (обычно `execute_complete`).
6. Scheduler отмечает task как `success` и запускает downstream.

Deferrable sensor наследуется от `BaseOperator`, а не от `BaseSensorOperator`: метод `poke` не нужен.

Trigger состоит из двух частей:

| Метод | Зачем |
|---|---|
| `serialize()` | Возвращает путь к классу и аргументы. По ним Airflow пересоздаёт trigger в другом процессе |
| `async run()` | Асинхронно ждёт и отдаёт `TriggerEvent` |

Выигрыш даёт только асинхронная часть. Если в `run()` будет тяжёлый синхронный код, он заблокирует весь triggerer. Без `async` логики deferrable не даёт ничего.

```python
def serialize(self):
    # путь к классу и аргументы: по ним Airflow пересоздаёт trigger
    return (
        "ch09_components.OrdersTrigger",
        {"conn_id": self.conn_id, "day": self.day, "pause": self.pause},
    )

async def run(self):
    found = False  # в книге здесь стоит True: цикл не работал бы
    while not found:
        found = await self._has_orders()
        if not found:
            await asyncio.sleep(self.pause)  # здесь worker не занят
    yield TriggerEvent({"day": self.day})
```

> **Пояснение:** в листинге книги флаг `found_records` в начале равен `True`, и цикл `while not found_records` никогда не выполнится. Это похоже на ошибку. В нашем коде флаг начинается с `False`. Тест из практики показывает разницу.

В DAG deferrable sensor работает как обычный. В интерфейсе task имеет статус `deferred`, пока trigger ждёт данные. Downstream не стартует, пока sensor не найдёт данные.

## Упаковка в Python-пакет

Папка `custom` внутри `dags` подходит для старта. Для других проектов, для совместной работы и для тестов лучше пакет. Он ставится как любая библиотека. Код отдельно от DAG позволяет настроить CI/CD.

![Пакет с hooks, operators и sensors ставится во все окружения Airflow](/assets/data-pipelines-with-apache-airflow/ch09-package.png)

Авторы показывают самый простой вариант на `setuptools`:

- Структура: `airflow-movielens/src/airflow_movielens/` с файлами `hooks.py`, `operators.py`, `sensors.py` и `__init__.py`. Рядом лежит `setup.py`.
- В `setup.py` главные поля: `name`, `version`, `install_requires` (зависимости, здесь `apache-airflow` и `requests`), `packages` и `package_dir`. Остальные поля (`author`, `description`, `url`, `license`) необязательные.
- Установка: `python -m pip install ./airflow-movielens`. Проверка: `from airflow_movielens.hooks import MovielensHook` в Python.
- Пакет и зависимости должны стоять во всех окружениях Airflow: scheduler, web server и workers. Для trigger то же самое с triggerer.

Поделиться пакетом можно тремя способами:

1. Установка из GitHub (`pip install git+https://...`), из PyPI или приватного индекса, или из папки. В последнем случае папка должна быть доступна среде Airflow.
2. Добавить operator в существующий open source provider. Это лучший путь, если вы расширяете готовую интеграцию.
3. Создать свой provider. Это самый трудный путь: он должен отличаться от существующих.

Есть и другой подход. Не расширяйте Airflow, а запускайте задачи в контейнерах: `DockerOperator`, `KubernetesPodOperator`. Установка Airflow остаётся лёгкой, а зависимости живут в контейнере. Это тема [главы 11](/book-summaries/engineering/data-pipelines-with-apache-airflow/11-tasks-in-containers/).

## Итоги главы

- Custom-компоненты нужны для систем без поддержки в Airflow и для частых операций, которые удобно дать команде.
- Компонент это Python-класс: наследник `BaseHook`, `BaseOperator` или `BaseSensorOperator`.
- Hook скрывает доступ к системе, берёт данные из Connection и кэширует сессию.
- Operator реализует `execute()` и принимает общие аргументы через `**kwargs`. Поля с Jinja перечисляют в `template_fields`.
- Sensor реализует `poke()`, который возвращает `True` или `False`.
- Deferrable operator вызывает `defer()` и отдаёт ожидание процессу triggerer, а worker slot освобождается.
- Trigger состоит из `serialize()` и `async run()`. Выигрыш даёт только асинхронный код.
- Для общего использования custom-компоненты упаковывают в пакет и ставят во все окружения Airflow.

## Ключевые термины

| Термин | Значение |
|---|---|
| `Hook` | Класс с логикой доступа к внешней системе |
| `BaseHook` | Базовый класс для hooks. Даёт `get_connection()` |
| `BaseOperator` | Базовый класс operators. Нужен метод `execute()` |
| `template_fields` | Список атрибутов, в которых работает Jinja |
| `poke()` | Метод sensor: `True`, если условие выполнено |
| `Deferrable operator` | Operator, который отдаёт ожидание triggerer |
| `defer()` | Передаёт ожидание процессу `triggerer` |
| `BaseTrigger` | Базовый класс trigger. Методы `serialize()` и `async run()` |
| `TriggerEvent` | Событие, которым trigger возвращает task на worker |
| `execute_complete` | Метод, который работает после завершения trigger |

## Что это значит на практике

- Если один и тот же код доступа к API есть в трёх DAG, пора писать hook.
- Не забывайте `template_fields`. Без них operator не примет `{{ ds }}`.
- Для долгих ожиданий (Spark, внешний API) пишите deferrable-версию. Проверьте, что клиент умеет `async`.
- Не вызывайте `get_conn()` снаружи hook. Пусть наружу торчат только понятные методы.
- Закрывайте hook в `finally`. Сессия не должна оставаться открытой при сбое.
- Общий код держите в пакете, а не копируйте между репозиториями. Ставьте его во все окружения Airflow.

## Практика

Код проверен на Airflow 3.4.0 без сервера и без сети. API и Connection заменены заглушками. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md). Классы лежат в [ch09_components.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch09_components.py), DAG в [ch09_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch09_dag.py). Реальный triggerer и `airflow dags test` мы не запускали: нужен живой API.

Скрипт [ch09_check.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch09_check.py) проверяет всю цепочку: пагинацию hook, шаблоны operator, `poke()`, `defer()` и цикл trigger.

```text
hook: заказов 7 | страницы (offset, limit): [(0, 3), (3, 3), (6, 3)]
hook: пустой день -> []
operator: day = 2026-01-02 | файл = 2026-01-02.json
operator: записано 7 заказов, в файле 7
sensor: пустой день, poke = False
sensor: есть заказы, poke = True
defer: method_name = execute_complete | trigger = OrdersTrigger
serialize: ch09_components.OrdersTrigger ['conn_id', 'day', 'pause']
trigger: проверок 3 | событие: {'day': '2026-01-02'}
DagBag: ошибки импорта: нет
DagBag: tasks = ['fetch_orders', 'wait_for_orders', 'wait_for_orders_async'] | upstream fetch_orders = ['wait_for_orders', 'wait_for_orders_async']
```

Hook прочитал 7 заказов тремя страницами. Operator подставил `ds` и записал файл. Sensor вернул `False` для пустого дня. Trigger получил событие после третьей проверки. Airflow разобрал DAG без ошибок.

### Задания

**1. Забытый template_fields.** Уберите `output_path` из `template_fields` оператора. Что будет с путём `/tmp/{{ ds }}.json`?

<details>
<summary>Решение</summary>

Airflow подставит `ds` только в `day`. Путь останется буквальной строкой `/tmp/{{ ds }}.json`, а файл получит это странное имя. Проверено запуском: после рендера `op.output_path` равен `/tmp/{{ ds }}.json`.

</details>

**2. Ошибка из книги.** Замените в `run()` строку `found = False` на `found = True`. Сколько проверок сделает trigger, если заказов нет?

<details>
<summary>Решение</summary>

Ни одной. Цикл `while not found` не выполняется, и trigger сразу отдаёт событие, хотя заказов нет. Проверено запуском с заглушкой: 0 проверок, событие приходит сразу.

</details>

**3. Сколько ждать.** У вас 10 workers и 100 Spark job по часу. Сколько часов займут jobs в обычных tasks? Что изменит deferrable?

<details>
<summary>Решение</summary>

Обычные tasks идут пачками по 10, поэтому нужно 10 часов. В deferrable версии все 100 ждут в triggerer, и общее время близко к одному часу работы кластера. Это оценка по логике книги, мы её не измеряли.

</details>

## Вопросы для самопроверки

1. Что должен делать hook, а что operator? Почему не писать всё в одном месте?
2. Зачем нужен `template_fields`? Что будет без него?
3. Какие шаги проходит deferrable task от `defer()` до `success`? Что делают `serialize()` и `run()`?
4. Почему deferrable не помогает, если клиент не умеет `async`?
5. Как поделиться custom-компонентами с командой и что нужно проверить при установке?

Предыдущая: [Связь с внешними системами](/book-summaries/engineering/data-pipelines-with-apache-airflow/08-external-systems/). Следующая: [Testing](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/).
