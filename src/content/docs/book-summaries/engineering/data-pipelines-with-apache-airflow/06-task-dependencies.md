---
title: "Data Pipelines with Apache Airflow, глава 6: Зависимости между задачами"
head:
  - tag: title
    content: "Airflow: зависимости, branching, trigger rules | Инжиниринг Данных"
description: "Конспект главы 6 Data Pipelines with Apache Airflow на русском. Fan-in и fan-out, BranchPythonOperator, trigger rules, LatestOnlyOperator, XCom и Taskflow API."
sidebar:
  order: 6
  label: "6. Зависимости задач"
tags:
  - books
  - airflow
  - dependencies
  - xcom
  - taskflow
---

**Главная мысль:** порядок задач задают зависимости, а решение "запускать или нет" принимают `trigger rules`. Ветки и условия лучше показывать в структуре DAG, а не прятать в коде задачи. Тогда по интерфейсу видно, что произошло.

## О чём глава

В [главе 5](/book-summaries/engineering/data-pipelines-with-apache-airflow/05-templating-context/) мы разобрали context и шаблоны. Здесь автор углубляет зависимости: линейные цепочки, fan-in и fan-out, ветки, условные задачи. Потом trigger rules, `XCom` и Taskflow API. Сквозной пример тот же, что в [главе 1](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/): DAG для прогноза спроса на зонты.

![Ветка выбирает один из двух путей, join с trigger rule none_failed объединяет их](/assets/data-pipelines-with-apache-airflow/ch06-branching.png)

## Базовые зависимости

### Линейные зависимости

Раньше мы строили цепочки: DAG с ракетами из [главы 2](/book-summaries/engineering/data-pipelines-with-apache-airflow/02-anatomy-of-dag/) скачивает метаданные, потом картинки, потом шлёт уведомление. Порядок задаёт оператор `>>`: `download >> get_pictures >> notify`.

Зависимость значит: задача стартует, только когда upstream закончился успешно. Это надёжнее, чем cron "на час позже". Если upstream упал, Airflow не запускает downstream, пока причина не устранена. Для временных сбоев, например сети, есть автоматические повторы (`retries`).

### Fan-out и fan-in

Вернёмся к DAG про зонты. Загрузка и очистка погоды не зависят от продаж. Поэтому есть две линейные цепочки, которые идут параллельно: `fetch_weather >> clean_weather` и `fetch_sales >> clean_sales`.

- **Fan-out:** одна задача запускает несколько. Например, пустая задача `start` из `EmptyOperator` запускает обе ветки: `start >> [fetch_weather, fetch_sales]`. 
- **Fan-in:** несколько задач ведут в одну. `join_datasets` объединяет данные и ждёт обе очистки: `[clean_weather, clean_sales] >> join_datasets`.
- Дальше снова цепочка: `join_datasets >> train_model >> deploy_model`.

![DAG про зонты: start запускает две ветки, join_datasets ждёт обе, дальше train и deploy](/assets/data-pipelines-with-apache-airflow/ch06-fanout-fanin.png)

Порядок такой: `start`, потом обе загрузки параллельно (если есть несколько workers), потом каждая очистка после своей загрузки. Ветки независимы, поэтому очистка продаж может начаться раньше загрузки погоды. `join_datasets` ждёт обе очистки.

## Branching

Пример автора: компания меняет ERP-систему. Скоро продажи придут из другого источника и в другом формате. Модель не должна ломаться, а старые данные нужны для анализа. Значит, DAG должен работать с обеими системами.

### Ветка внутри задачи

Первый способ: в задачах `fetch_sales` и `clean_sales` смотреть на `data_interval_start` и выбирать код по дате: если дата раньше `ERP_CHANGE_DATE`, вызвать функцию для старой системы, иначе для новой. Структура DAG не меняется. Но у способа три минуса.

- Он работает, пока ветки похожи. Если новая система требует другой цепочки шагов (старая отдаёт zip, который надо распаковать и обогатить, новая отдаёт данные через REST API), код задачи разрастается.
- В интерфейсе не видно, какая ветка сработала. Ответ скрыт внутри задач. Помогает только логирование.
- Ветку можно спрятать только в универсальный `PythonOperator`. Готовые операторы недоступны. Для SQL-источника `SqlExecuteQueryOperator` взял бы на себя запрос и подключение.

### Ветка в структуре DAG

Второй способ: сделать два набора задач, по одному на систему (`fetch_sales_old >> clean_sales_old` и `fetch_sales_new >> clean_sales_new`), и дать Airflow выбрать. Для этого есть `BranchPythonOperator`. Он берёт Python-функцию, как `PythonOperator`. Но функция должна вернуть `task_id` следующей задачи. Можно вернуть список `task_id`: выполнятся все. Здесь функция сравнивает `data_interval_start` с датой переключения и возвращает `fetch_sales_old` или `fetch_sales_new`. Связь: `start >> pick_erp_system >> [fetch_sales_old, fetch_sales_new]`.

Оператор помечает невыбранные задачи как `skipped`. И тут ловушка. Если соединить обе очистки с `join_datasets`, то по умолчанию весь DAG после ветки будет пропущен. Правило по умолчанию `all_success` требует успеха всех upstream. Но одна ветка не запускалась, и условие никогда не выполнится. Автор предупреждает: неверное trigger rule вместе с веткой молча пропускает задачи.

Решение: на задаче после ветки поставить `trigger_rule="none_failed"`. Оно запускает задачу, когда нет упавших upstream, а пропуск не считается сбоем. Но тогда у `join_datasets` три входа: `clean_weather`, `clean_sales_old` и `clean_sales_new`. Это не отражает суть: сначала выбрать ERP, потом объединить два источника. Поэтому многие добавляют пустой join-task (`EmptyOperator`) после веток. Правило ставят только на нём, а `join_datasets` остаётся с правилом по умолчанию.

## Условные задачи

Иногда нужно пропускать отдельные задачи. Пример: коллега поменял код очистки и запустил backfill за весь период. Тогда `train_model` и `deploy_model` выполнятся сотни раз, и мы задеплоим кучу ненужных моделей. Хотим деплоить только по самому свежему run.

- **Условие внутри задачи.** `deploy_model` сам проверяет, что текущее время лежит в окне последнего интервала. Минусы те же: логика смешана с условием, нужен `PythonOperator`, по интерфейсу не видно, был ли деплой.
- **Условие как задача.** Добавляем задачу `latest_only` перед `deploy_model`. Если run не самый свежий, она бросает `AirflowSkipException` и получает статус `skipped`. У `deploy_model` правило `all_success`: родитель пропущен, значит и он пропущен. Если исключения нет, `latest_only` успешна, и деплой идёт. Условие теперь видно в графе.
- **Готовые операторы.** `LatestOnlyOperator` делает ровно это и избавляет от своего кода: `train_model >> latest_only >> deploy_model`. Для других условий есть `ShortCircuitOperator`: он продолжает или пропускает следующие задачи по булеву результату функции.

## Trigger rules

Airflow постоянно проверяет задачи DAG run. Готовность задачи определяет `trigger rule`: условие по статусам upstream-задач. Готовую задачу scheduler берёт, и она стартует при первом свободном слоте. Правило по умолчанию, `all_success`, требует, чтобы все upstream завершились успешно.

На DAG про зонты сначала готова только `start`: у неё нет upstream. Когда она успешна, готовы обе загрузки, и так до конца DAG. А что при сбое?

Пусть `fetch_sales` упала. Она получает статус `failed`. Её downstream `clean_sales` не может запуститься и получает `upstream_failed`. Ветка погоды, не связанная с упавшей задачей, продолжает работу. Такую передачу влияния вниз по графу называют `propagation`. Правило `all_success` передаёт вниз и сбой, и пропуск: всё после пропущенной задачи тоже пропускается.

![Три trigger rules по-разному реагируют на сбой или пропуск upstream-задачи](/assets/data-pipelines-with-apache-airflow/ch06-trigger-rules.png)

Остальные правила дают другое поведение.

- `none_failed` ждёт, пока все upstream закончатся, и терпит успех и пропуск. Пропуск вниз не передаётся, а сбой передаётся. Поэтому оно подходит для join после ветки.
- `all_done` запускает задачу, когда все upstream закончились с любым статусом. Так делают cleanup: остановить машину или кластер независимо от результата.
- `one_failed` и `one_success` это eager-правила. Они не ждут остальных upstream. Первое быстро запускает обработку ошибки: уведомление или откат. Второе запускается, как только готов один результат.

| Правило | Когда запускается |
|---|---|
| `all_success` (по умолчанию) | Все upstream успешны |
| `all_failed` | Все upstream упали |
| `all_done` | Все upstream закончились с любым статусом |
| `all_skipped` | Все upstream пропущены |
| `one_failed` | Упал хотя бы один, не ждёт остальных |
| `one_success` | Успешен хотя бы один, не ждёт остальных |
| `one_done` | Хотя бы один завершился успешно или с ошибкой |
| `none_failed` | Нет упавших, пропуск допустим |
| `none_failed_min_one_success` | Нет упавших и хотя бы один успешен |
| `none_skipped` | Нет пропущенных, сбой допустим |
| `always` | Всегда |
| `all_done_setup_success` | Все setup успешны, остальные завершены |

## XCom: данные между задачами

`XCom` (cross-communication) это маленькое сообщение, которое одна задача кладёт в metastore, а другая читает. Пример: `train_model` регистрирует модель в реестре под случайным идентификатором, и `deploy_model` должен узнать этот идентификатор.

![Обычный API с xcom_push и xcom_pull и Taskflow API с return и аргументом](/assets/data-pipelines-with-apache-airflow/ch06-xcom-taskflow.png)

### Как работает XCom

- `xcom_push(key, value)` на task instance из context кладёт значение под ключом. `xcom_pull(task_ids, key)` читает его.
- По умолчанию `xcom_pull` берёт значения текущего DAG и текущего run. Можно читать чужие DAG и даты. Автор категорически не советует, если нет очень веской причины.
- Значения видны в интерфейсе: Browse, XComs.
- Многие операторы кладут результат сами. У них аргумент `do_xcom_push` по умолчанию `True`. `BashOperator` кладёт последнюю строку stdout. `PythonOperator` кладёт возвращённое значение под ключом `return_value`.

### Когда XCom не нужен

У XCom есть минусы.

- **Скрытая зависимость.** Читающая задача зависит от пишущей, но в графе этой стрелки нет, и scheduler её не учитывает. Порядок должны обеспечить вы. С другими DAG или датами всё ещё запутаннее.
- **Нарушенная атомарность** (см. [главу 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-scheduling/)). Автор видел, как токен API получали в одной задаче и передавали через XCom в другую. Токен жил пару часов, и перезапуск второй задачи падал. Надо получать токен и использовать его в одной задаче.
- **Сериализация.** Значение должно сериализоваться. Lambda и многие классы multiprocessing не подойдут.
- **Размер.** XCom лежит в metastore, и лимит зависит от базы: SQLite 2 GB, PostgreSQL 1 GB, MySQL 64 KB. Лимит большой, но это не повод хранить большое.

XCom хорош для имён файлов, путей и небольших ответов API. Большие данные кладите во внешнее хранилище. Зависимости через XCom документируйте.

### Custom XCom backend и очистка

Metastore плохо масштабируется на большие объёмы. Поэтому можно задать custom XCom backend: класс от `BaseXCom` с двумя static-методами `serialize_value` и `deserialize_value`. Первый вызывается при записи, второй при чтении. Класс включают параметром `xcom_backend`. Для больших значений есть готовая поддержка object storage.

Старые значения из metastore чистит `airflow db clean`. Для custom backend мониторинг и очистку делаете вы сами.

## Taskflow API

Обмен через XCom громоздок, особенно в длинных цепочках. Для Python-задач в Airflow есть API на декораторах: Taskflow API. Он заметно упрощает код.

### Задачи из функций

Обычный стиль требует функции вне DAG, обёртки в `PythonOperator`, явных `xcom_push` и `xcom_pull` и ключа в двух местах. В Taskflow функцию помечают `@task`, возвращают значение из неё, а следующая задача принимает его как аргумент. Связь строится из вызовов: `model_id = train_model()` и `deploy_model(model_id)`.

Вызов `train_model()` создаёт оператор, а `return` кладёт значение в XCom. Когда результат передан в `deploy_model`, Airflow понимает, что есть зависимость, и передаёт значение сам.

| Декоратор | Что создаёт |
|---|---|
| `@dag` | DAG |
| `@task` | `PythonOperator` |
| `@task.branch` | `BranchPythonOperator` |
| `@task.short_circuit` | `ShortCircuitOperator` |
| `@task.bash` | `BashOperator` |
| `@task_group` | `TaskGroup` |
| `@task.sensor` | `PythonSensor` |
| `@task.virtualenv`, `@task.external_python` | Код в виртуальном окружении |
| `@task.docker`, `@task.kubernetes` | Код в контейнере или pod |
| `@task.pyspark` | Функция в `SparkSession` |
| `@task.run_if`, `@task.skip_if` | Запуск или пропуск по условию |

### DAG из функции

DAG тоже можно описать декоратором. Внутри функции задачи, а `@dag` принимает `dag_id`, `schedule`, `start_date` и другие параметры. Если `dag_id` не задан, им станет имя функции. В конце файла функцию нужно вызвать. Иначе Airflow не увидит DAG.

### Плюсы и минусы

Taskflow сильно сокращает шаблонный код. Он решает часть проблем XCom: значения передаются явно, а не прячутся в функциях. Минус: декораторов меньше, чем операторов. Для остальных нужен обычный API. Стили можно смешивать, но зависимость между ними пишется иначе, например `join_datasets >> model_id`, и это сбивает. Данные между Taskflow-задачами всё равно лежат в XCom. Значит, лимиты и требование сериализации те же.

## Итоги главы

- Зависимости задают порядок: задача стартует после успешного upstream. Это надёжнее, чем cron с запасом по времени.
- Fan-out и fan-in дают параллельные ветки и join.
- Сбой upstream передаётся вниз: downstream получает `upstream_failed`.
- `BranchPythonOperator` выбирает по Python-функции, какие задачи запустить. Остальные получают `skipped`.
- Ветку и условие лучше выносить в структуру DAG. Тогда в интерфейсе видно, что произошло, и можно использовать готовые операторы.
- Trigger rule определяет, что делает задача при сбое или пропуске upstream. Join после ветки требует `none_failed`.
- `LatestOnlyOperator` и `ShortCircuitOperator` пропускают задачи по условию.
- XCom передаёт небольшие значения: имена файлов, пути, идентификаторы. Большие данные лежат во внешнем хранилище.
- XCom прячет зависимость и может нарушить атомарность. Документируйте такие связи.
- Taskflow API превращает функции в задачи и сам строит зависимости и XCom, но покрывает не все операторы.

## Ключевые термины

| Термин | Значение |
|---|---|
| Fan-out / fan-in | Одна задача ведёт к нескольким / несколько к одной |
| `trigger_rule` | Условие запуска задачи по статусам upstream |
| `skipped` | Задача пропущена |
| `upstream_failed` | Задача не запущена, потому что upstream упал |
| Propagation | Передача сбоя или пропуска вниз по графу |
| `BranchPythonOperator` | Выбирает, какие задачи запускать |
| `LatestOnlyOperator` | Пропускает всё, кроме последнего запуска |
| `XCom` | Маленькое сообщение между задачами в metastore |
| Custom XCom backend | Свой класс хранения XCom, например в S3 |
| Taskflow API | Декораторы `@dag`, `@task` |

## Что это значит на практике

- После ветки ставьте отдельный join-task с `none_failed`. Не меняйте правила у остальных задач.
- Для cleanup и алертов используйте `all_done` и `one_failed`.
- Деплой и дорогие шаги защитите `LatestOnlyOperator`, если запускаете backfill.
- Не гоняйте таблицы и DataFrame через XCom. Передавайте путь в хранилище.
- Следите за размером metastore. Запланируйте `airflow db clean`.
- Для простых Python-цепочек берите Taskflow. Меньше кода и явные зависимости.
- Не читайте XCom из другого DAG или другого run. Это скрытая связь, которую scheduler не видит.
- Не передавайте через XCom токены с коротким сроком жизни. Получайте и используйте их в одной задаче.

## Практика

Проверено на Airflow 3.4.0 без запущенного сервера. DAG запускает `dag.test()`. Файлы лежат в [scripts/airflow-code/](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code), статус всех примеров в [README.md](https://github.com/surfalytics/dataengineer.ru/blob/main/scripts/airflow-code/README.md).

Первый DAG собирает всё вместе: fan-out, ветку по дате переключения ERP, join после ветки, `LatestOnlyOperator` и Taskflow с XCom. Имена придуманы для примера.

```python
"""Глава 6: umbrella DAG с fan-out, веткой по ERP, join, LatestOnly и Taskflow XCom."""
import pendulum
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.latest_only import LatestOnlyOperator
from airflow.sdk import dag, task

ERP_CHANGE_DATE = pendulum.datetime(2025, 6, 1, tz="UTC")


@dag(dag_id="umbrella_branch", schedule="@daily", start_date=pendulum.datetime(2025, 1, 1, tz="UTC"))
def umbrella_branch():
    start = EmptyOperator(task_id="start")

    @task
    def fetch_weather():
        return "weather.csv"

    @task.branch
    def pick_erp_system(data_interval_start=None):
        # возвращаем task_id ветки, которая должна выполниться
        if data_interval_start < ERP_CHANGE_DATE:
            return "fetch_sales_old"
        return "fetch_sales_new"

    @task
    def fetch_sales_old():
        return "sales_old.csv"

    @task
    def fetch_sales_new():
        return "sales_new.csv"

    # один join после ветки: правило none_failed ставим только на нём
    join_erp_branch = EmptyOperator(task_id="join_erp_branch", trigger_rule="none_failed")
    join_datasets = EmptyOperator(task_id="join_datasets")

    @task
    def train_model(ds=None):
        return f"model-{ds}"  # return кладёт значение в XCom

    @task
    def deploy_model(model_id: str):
        print("deploy", model_id)  # model_id пришёл из XCom

    pick = pick_erp_system()
    old, new = fetch_sales_old(), fetch_sales_new()
    model_id = train_model()
    latest_only = LatestOnlyOperator(task_id="latest_only")

    weather = fetch_weather()
    start >> [weather, pick]  # fan-out
    pick >> [old, new] >> join_erp_branch
    [weather, join_erp_branch] >> join_datasets  # fan-in
    join_datasets >> model_id >> latest_only >> deploy_model(model_id)


umbrella_branch()
```

Второй DAG показывает trigger rules. Два upstream-варианта: один успешен и один пропущен (случай A), один успешен и один упал (случай B).

```python
"""Глава 6: как trigger rules реагируют на upstream-задачи со статусами success, failed, skipped."""
import pendulum
from airflow.exceptions import AirflowSkipException
from airflow.sdk import DAG, task

with DAG(dag_id="trigger_rules_demo", schedule=None, start_date=pendulum.datetime(2025, 1, 1, tz="UTC")):

    @task
    def up_ok():
        return "ok"

    @task
    def up_skip():
        raise AirflowSkipException("пропускаем")

    @task
    def up_fail():
        raise RuntimeError("сбой")

    def downstream(name, rule):
        @task(task_id=name, trigger_rule=rule)
        def step():
            return name

        return step()

    ok, skip, fail = up_ok(), up_skip(), up_fail()
    # случай A: один upstream успешен, другой пропущен
    [ok, skip] >> downstream("a_all_success", "all_success")
    [ok, skip] >> downstream("a_none_failed", "none_failed")
    # случай B: один upstream успешен, другой упал
    for rule in ("all_success", "none_failed", "all_done", "one_failed"):
        [ok, fail] >> downstream(f"b_{rule}", rule)
```

Скрипт [ch06_check.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch06_check.py) запускает оба DAG и печатает статусы. Вывод настоящий.

```text
ошибки импорта: нет
umbrella_branch, logical_date 2025-01-02:
  pick_erp_system: success
  fetch_sales_old: success
  fetch_sales_new: skipped
  join_erp_branch: success
  join_datasets: success
  deploy_model: success
umbrella_branch, logical_date 2025-07-02:
  pick_erp_system: success
  fetch_sales_old: skipped
  fetch_sales_new: success
  join_erp_branch: success
  join_datasets: success
  deploy_model: success
trigger_rules_demo:
  a_all_success: skipped
  a_none_failed: success
  b_all_done: success
  b_all_success: upstream_failed
  b_none_failed: upstream_failed
  b_one_failed: success
```

Как читать вывод.

- До даты переключения сработала ветка `old`, после неё `new`. Вторая получает `skipped`.
- `join_erp_branch` успешен в обоих случаях: у него `none_failed`.
- Случай A: `all_success` пропускает задачу, `none_failed` запускает её.
- Случай B: сбой идёт дальше и при `all_success`, и при `none_failed`.
- `deploy_model` успешен, потому что `dag.test()` это ручной запуск (`manual`). `LatestOnlyOperator` ручные запуски не пропускает. В запусках по расписанию он пропустил бы старые интервалы.

### Задания

1. Добавьте во второй DAG в случае A задачи с правилами `all_done` и `none_skipped`. Какие у них будут статусы?
2. Уберите `trigger_rule="none_failed"` у `join_erp_branch`. Что будет с `join_datasets` и `deploy_model`?
3. Какие из значений можно класть в XCom: путь `s3://bucket/sales/2025-01-02.parquet`, DataFrame на 5 млн строк, идентификатор модели, токен API на два часа?

<details>
<summary>Решение</summary>

1. `a_all_done` получит `success`: правило ждёт завершения любых upstream. `a_none_skipped` получит `skipped`: один upstream пропущен. Мы запустили этот вариант, статусы совпали.
2. `join_erp_branch` станет `skipped`: один из его upstream пропущен, а правило `all_success`. Пропуск идёт дальше: `join_datasets` и `deploy_model` тоже `skipped`. Мы запустили этот вариант, статусы совпали.
3. Можно путь и идентификатор модели: они маленькие. DataFrame кладите в хранилище и передавайте путь. Токен лучше получать в той же задаче, где он нужен: он истечёт, и перезапуск упадёт.

</details>

## Вопросы для самопроверки

1. Почему после `BranchPythonOperator` задача `join` с `all_success` пропускается?
2. Чем `none_failed` отличается от `all_done`?
3. Почему ветку лучше вынести из кода задачи в структуру DAG?
4. Какие минусы у XCom и что передавать вместо больших данных?
5. Что делает Taskflow API с XCom и зависимостями?

Предыдущая: [Templating и контекст](/book-summaries/engineering/data-pipelines-with-apache-airflow/05-templating-context/). Следующая: [Запуск по внешним событиям](/book-summaries/engineering/data-pipelines-with-apache-airflow/07-triggering-external-input/).
