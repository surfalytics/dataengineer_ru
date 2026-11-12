---
title: "Data Pipelines with Apache Airflow, глава 5: Templating и контекст задачи"
head:
  - tag: title
    content: "Airflow templating: Jinja и context | Инжиниринг Данных"
description: "Конспект главы 5 Data Pipelines with Apache Airflow на русском. Jinja templating, task context, template_fields, op_kwargs, airflow tasks render, hooks и connections."
sidebar:
  order: 5
  label: "5. Templating и контекст"
tags:
  - books
  - airflow
  - templating
  - jinja
---

**Главная мысль:** Airflow подставляет значения в задачу во время запуска. Значения берутся из `context`: даты интервала, `run_id` и другое. Так один DAG работает для любого интервала.

![Как значения из context попадают в шаблон оператора и в функцию PythonOperator](/assets/data-pipelines-with-apache-airflow/ch05-context-flow.png)

## Пример книги: StockSense

Автор строит учебный пайплайн. Он скачивает почасовые дампы просмотров страниц Wikipedia. Идея такая: рост просмотров страницы компании значит рост интереса к акции.

- Дамп за один час это файл `.gz` (около 50 MB). URL строится по шаблону из даты и часа.
- Строки файла: код домена, название страницы, число просмотров, размер ответа.
- Перед пайплайном посмотрите данные руками (`wget`, `gunzip`, `head`, `awk`). Так вы поймёте формат и проверите, что чистка не нужна.
- Три вопроса до начала: будем ли перерабатывать данные? Как они приходят? Что из них строим?

## Jinja templating

- Шаблон это строка с `{{ ... }}`. Внутри любое выражение Python.
- Пример: `{{ logical_date.year }}`. Airflow подставляет значение перед запуском задачи.
- Даты в Airflow это объекты `pendulum`. Они ведут себя как обычный `datetime`.
- Нужен ноль в начале (`07`)? Форматируйте: `{{ '{:02}'.format(logical_date.hour) }}` или `logical_date.format('YYYYMMDDHH')`.

### Какие аргументы шаблонизируются

- Не все. Каждый оператор перечисляет их в атрибуте `template_fields`.
- Остальные поля Jinja не трогает, `{{ x }}` останется текстом.
- Список ищите в документации оператора.
- `template_ext` задаёт расширения файлов, которые оператор читает и шаблонизирует (например `.sql`).
- Папки для поиска файлов добавляйте в DAG через `template_searchpath`.

## PythonOperator работает иначе

| Оператор | Как получить значения |
|---|---|
| `BashOperator` и другие | Пишете `{{ ... }}` в строке аргумента |
| `PythonOperator` | Функция сама получает context через аргументы |

- Python-код внутри функции Jinja не обрабатывает.
- Airflow вызывает функцию со всеми переменными context как keyword-аргументами.
- Нужные переменные объявляйте явно: `def f(data_interval_start, **context)`. Остальные попадут в `context`.
- Так код понятнее. Линтеры и type hints тоже работают.
- Назовите словарь `**context`, а не `**kwargs`. Это сообщает читателю, что внутри.

Свои параметры передают двумя способами:

- `op_args` это список позиционных аргументов.
- `op_kwargs` это словарь именованных. Строки в нём шаблонизируются.

## Что лежит в context

| Переменная | Что это |
|---|---|
| `logical_date` | Условная дата запуска |
| `data_interval_start`, `data_interval_end` | Границы интервала |
| `ds`, `ds_nodash`, `ts` | Дата и время в виде строк |
| `run_id`, `dag_run` | Данные текущего запуска |
| `task`, `task_instance` (`ti`) | Текущая задача и её экземпляр |
| `params` | Параметры, заданные пользователем |
| `var`, `conn` | Доступ к Variables и Connections |
| `prev_data_interval_*_success` | Интервал прошлого успешного запуска |
| `triggering_asset_events` | События asset (глава 4) |

В Airflow 3 удалили часть старых устаревших переменных. Чтобы увидеть всё, напечатайте `context` в тестовой задаче.

## Отладка шаблонов

- UI: откройте задачу и нажмите **Rendered Template**. Работает только после того, как задача была запущена.
- CLI: `airflow tasks render <dag_id> <task_id> <дата>`. Задача не запускается и ничего не пишет в metastore. Можно задать любую дату.

## Данные между задачами

- Задачи могут идти на разных машинах. Память не общая.
- Два способа: XCom (глава 6) или внешнее хранилище, доступное всем.
- В примере первая задача пишет файл с `INSERT`, вторая выполняет его в Postgres.
- Повторный запуск создаст дубли. Для идемпотентности нужны primary key и `ON CONFLICT ... DO UPDATE` или `DO NOTHING`.

## Операторы и hooks

- `SQLExecuteQueryOperator` берёт `conn_id` и `sql`. SQL может быть строкой или путём к `.sql` файлу.
- Credentials лежат в `Connection`. Её создают в UI (Admin, Connections) или через CLI.
- Оператор отвечает за "что сделать". `hook` отвечает за "как": он открывает соединение, шлёт запрос, закрывает.
- Для внешних систем нужны пакеты providers, например `apache-airflow-providers-common-sql`.

## Пример кода

Проверено на Airflow 3.4: DAG проходит `airflow dags test`.

Функция берёт интервал из context и параметры из `op_kwargs`.

```python
import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


def _report(city, data_interval_start, data_interval_end, **context):
    print(f"{city}: {data_interval_start} -> {data_interval_end}")


with DAG(
    dag_id="weather_templating",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
):
    download = BashOperator(
        task_id="download",
        bash_command="echo load /tmp/weather-{{ ds_nodash }}.json",
    )
    report = PythonOperator(
        task_id="report",
        python_callable=_report,
        op_kwargs={"city": "Berlin"},
    )
    download >> report
```

Проверить шаблон без запуска:

```bash
airflow tasks render weather_templating download 2025-01-05
```

## Ключевые термины

| Термин | Значение |
|---|---|
| `context` | Словарь переменных запуска задачи |
| Jinja | Шаблонизатор. Синтаксис `{{ ... }}` |
| `template_fields` | Аргументы оператора, которые шаблонизируются |
| `template_ext` | Расширения файлов, которые оператор шаблонизирует |
| `template_searchpath` | Папки для поиска файлов-шаблонов |
| `op_args` / `op_kwargs` | Свои аргументы для функции PythonOperator |
| `pendulum` | Библиотека дат, замена `datetime` |
| `Connection` | Сохранённые credentials для внешней системы |
| `hook` | Объект, который общается с внешней системой |

## Что это значит на практике

- Не зашивайте даты в код. Берите их из context.
- Перед ревью смотрите `airflow tasks render`. Это быстрее, чем ждать запуск.
- Если шаблон не сработал, проверьте, что поле входит в `template_fields`.
- Делайте записи идемпотентными: primary key и upsert. Повторный запуск не должен давать дубли.
- Не передавайте большие данные через память. Пишите в хранилище и передавайте путь.
- Не храните пароли в коде. Используйте `Connection`.

## Вопросы для самопроверки

1. Почему `{{ ds }}` в аргументе, который не входит в `template_fields`, не работает?
2. Чем PythonOperator отличается от BashOperator в работе с context?
3. Как проверить значения шаблона, не запуская задачу?
4. Чем оператор отличается от `hook`?

Предыдущая: [Asset-aware scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/). Следующая: [Зависимости между задачами](/book-summaries/engineering/data-pipelines-with-apache-airflow/06-task-dependencies/).
