---
title: "Data Pipelines with Apache Airflow, глава 5: Templating и контекст задачи"
head:
  - tag: title
    content: "Airflow templating: Jinja и context | Инжиниринг Данных"
description: "Конспект главы 5 Data Pipelines with Apache Airflow на русском. Jinja templating, task context, template_fields, op_kwargs, tasks render, hooks."
sidebar:
  order: 5
  label: "5. Templating и контекст"
tags:
  - books
  - airflow
  - templating
  - jinja
---

**Главная мысль:** Airflow подставляет значения в задачу во время запуска. Значения берутся из `context`: даты интервала, `run_id` и другое. Так один DAG работает для любого интервала. Операторы и `PythonOperator` получают context по-разному.

## О чём глава

Глава отвечает на вопрос: как сделать задачу динамичной, чтобы она знала свой интервал? Мы уже видели `logical_date` в [главах 3 и 4](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/). Здесь разбираем, как значения попадают в код: Jinja, `PythonOperator`, `op_kwargs`, отладка шаблонов, оператор и `hook`.

![Как значения из context попадают в шаблон оператора и в функцию PythonOperator](/assets/data-pipelines-with-apache-airflow/ch05-context-flow.png)

## Пример книги: StockSense

Автор строит учебный пайплайн StockSense. Идея: рост просмотров Wikipedia-страницы компании значит рост интереса, а значит акция, скорее всего, дорожает.

Wikimedia отдаёт почасовые файлы `.gz` с 2015 года: около 50 MB в архиве и 200-250 MB после распаковки. В имени файла стоит конец периода: `210000` значит интервал 20:00-21:00. Строка файла это четыре поля: код домена, название страницы, число просмотров, размер ответа.

Автор советует сначала посмотреть данные руками (`wget`, `gunzip`, `head`, `awk`). Самые частые домены `en` и `en.m` (мобильная версия): данные ожидаемые, чистка не нужна. Обычно чистка занимает большую часть работы. Ещё до кода ответьте на три вопроса: будем ли перерабатывать данные, как они приходят, что мы из них строим.

## Task context и Jinja

Первая версия DAG качает файл, распаковывает его и берёт просмотры пяти компаний. URL зависит от даты и часа, поэтому его собирают в момент запуска.

### Шаблоны в аргументах оператора

В `BashOperator` место подстановки обводят в `{{ ... }}`. Это string interpolation: строку собирают, когда значение стало известно. Airflow делает это через Jinja, шаблонизатор с синтаксисом `{{ переменная }}`. Внутри любое выражение Python.

Значения берутся из `context`. Одна из переменных, `logical_date`, это объект библиотеки `pendulum`: он ведёт себя как `datetime`. URL требует нули в начале (`07` вместо `7`), поэтому используют форматирование: `{{ '{:02}'.format(logical_date.hour) }}`.

Не все аргументы шаблонизируются. Каждый оператор хранит список таких полей в атрибуте `template_fields`. Для остальных Jinja не срабатывает, и `{{ name }}` остаётся обычным текстом. Список смотрите в документации оператора.

### PythonOperator работает иначе

`PythonOperator` берёт не строку, а функцию (`python_callable`). Код внутри функции Jinja не обрабатывает. Вместо этого Airflow вызывает функцию и передаёт ей переменные context как keyword-аргументы.

Есть два способа принять их. Можно собрать всё в словарь: `def f(**context)`. Автор советует имя `context` вместо привычного `kwargs`: оно говорит читателю, что внутри. Можно объявить нужные переменные явно: `def f(data_interval_start, **context)`. Python сверяет имена: совпавшие идут в свои аргументы, остальные падают в `**context`.

![Как Python раздаёт переменные context: явный аргумент и остальное в **context](/assets/data-pipelines-with-apache-airflow/ch05-kwargs-routing.png)

Явный вариант лучше: код понятнее, а линтеры и type hints работают. Но если переменной нет в context, функция упадёт.

### Свои аргументы: op_args и op_kwargs

Чтобы не копировать функцию ради другого пути, ей передают свои значения. `op_args` это список позиционных аргументов. `op_kwargs` это словарь именованных. Строки в них шаблонизируются, поэтому дату можно разобрать на части до вызова функции.

### Как проверить шаблон

В UI откройте задачу и нажмите **Rendered Template**. Минус: он работает только для задачи, которую Airflow уже запускал. Проще CLI: `airflow tasks render <dag_id> <task_id> <дата>`. Команда рисует шаблоны для любой даты, не запускает задачу и ничего не пишет в metastore.

## Что доступно в шаблонах

Полный context проще всего увидеть, если напечатать его в `PythonOperator`. Вот самые полезные переменные.

| Переменная | Что это |
|---|---|
| `logical_date` | Условная дата запуска |
| `data_interval_start`, `data_interval_end` | Границы интервала |
| `ds`, `ds_nodash`, `ts` | Дата и время строкой |
| `run_id`, `dag_run` | Данные текущего запуска |
| `task`, `task_instance` (`ti`) | Текущая задача и её экземпляр |
| `params` | Параметры, заданные пользователем |
| `var`, `conn` | Доступ к Variables и Connections |
| `prev_data_interval_*_success` | Интервал прошлого успешного запуска |
| `triggering_asset_events` | События asset, которые запустили DAG (глава 4) |

В Airflow 3 удалили часть устаревших (deprecated) переменных. 

## Собираем StockSense целиком

Следующие две задачи распаковывают архив и читают файл: функция берёт домен `en` и нужные страницы, результат идёт в лог. Затем счётчики пишут в PostgreSQL, чтобы отвечать на вопросы вроде "каково среднее число просмотров Google в час?". Таблица `pageview_counts` хранит страницу, число просмотров и время (это `data_interval_start`).

![Четыре шага StockSense и работа SQLExecuteQueryOperator с hook](/assets/data-pipelines-with-apache-airflow/ch05-stocksense-hook.png)

### Данные между задачами

Задачи могут идти на разных машинах, общей памяти нет. Данные отдают туда, где они переживут задачу: в XCom (запись в metastore, глава 6) или во внешнее хранилище, доступное всем машинам. В примере первая задача пишет файл с запросами `INSERT`, вторая выполняет его в базе. Повторный запуск создаст дубли. Автор советует идемпотентную запись: поле-ключ как `primary key` и `ON CONFLICT ... DO UPDATE` или `DO NOTHING`.

### SQLExecuteQueryOperator и connection

Оператору нужны `task_id`, `conn_id` и `sql`. Параметр `sql` принимает строку или путь к `.sql` файлу: файл читают, шаблонизируют и выполняют. Какие расширения оператор шаблонизирует, говорит `template_ext`. Jinja ищет файлы в папке DAG, другие папки добавляют через `template_searchpath`.

`conn_id` указывает на `Connection`: хранилище credentials. Airflow держит его в metastore в зашифрованном виде. Connection создают в UI (Admin, Connections) или командой `airflow connections add`. Для PostgreSQL нужен пакет `apache-airflow-providers-common-sql`: для каждой внешней системы ставят свои зависимости.

### Operator и hook

Внутри оператор создаёт `hook`. Hook открывает соединение, отправляет запрос и закрывает соединение. Оператор лишь передаёт ему запрос. Оператор определяет, что делать, а hook определяет, как. Обычно вы работаете только с операторами.

Airflow отвечает за время и порядок шагов, а context даёт каждому запуску значения его интервала.

## Итоги главы

- Templating задаёт значения задачи во время запуска: даты и пути не зашиты в код.
- Jinja работает только в полях из `template_fields`.
- В `PythonOperator` Jinja не трогает код функции. Airflow передаёт context как keyword-аргументы, нужные лучше объявлять явно.
- `op_args` и `op_kwargs` передают свои параметры. Строки в них шаблонизируются.
- `airflow tasks render` показывает шаблоны без запуска задачи.
- Задачи не делят память: данные идут через XCom или хранилище. Запись должна быть идемпотентной.
- Оператор отвечает за "что", `hook` за "как". Credentials лежат в `Connection`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `context` | Словарь переменных запуска задачи |
| `Jinja` | Шаблонизатор. Синтаксис `{{ ... }}` |
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
- В `PythonOperator` объявляйте нужные переменные context в сигнатуре и называйте остаток `**context`.

## Практика

Скрипты работают без сервера и без сети. DAG проверен на Airflow 3.4.0: `airflow dags test stocksense_templating 2025-04-24T22:00:00` завершился успешно. Скачивание не запускали: DAG только печатает URL. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

Главное из DAG: два оператора, оба берут дату из context. Файл: [ch05_stocksense_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch05_stocksense_dag.py).

```python
# BashOperator: bash_command входит в template_fields, Jinja подставляет {{ ... }}
show_name = BashOperator(
    task_id="show_name",
    bash_command=(
        "echo pageviews-{{ logical_date.format('YYYYMMDD') }}-"
        "{{ '{:02}'.format(logical_date.hour) }}0000.gz"
    ),
)
# PythonOperator: строки в op_kwargs шаблонизируются, функция получает уже готовые значения
get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ logical_date.year }}",
        "month": "{{ logical_date.month }}",
        "day": "{{ logical_date.day }}",
        "hour": "{{ logical_date.hour }}",
        "output_path": "/tmp/wikipageviews-{{ logical_date.format('YYYYMMDDHH') }}.gz",
    },
)
show_name >> get_data
```

Проверим шаблоны для даты, которой ещё не было. Скрипт [ch05_check_render.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch05_check_render.py) разбирает DAG и вызывает `airflow tasks render`.

```text
ошибки импорта: нет
tasks: show_name >> get_data
template_fields у show_name: ['bash_command', 'env', 'cwd']
template_fields у get_data: ['templates_dict', 'op_args', 'op_kwargs']
render show_name: echo pageviews-20250424-220000.gz
render get_data: {'year': '2025', 'month': '4', 'day': '24', 'hour': '22', 'output_path': '/tmp/wikipageviews-2025042422.gz'}
```

Теперь повторный запуск того же интервала: таблица `plain` без ключа и таблица `safe` с `primary key` и upsert. Скрипт: [ch05_idempotent_insert.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch05_idempotent_insert.py).

```text
после run 1: plain=3 строк, safe=3 строк
после run 2: plain=6 строк, safe=3 строк
```

Без ключа второй запуск удвоил строки, с upsert нет. В примере `sqlite3`, в PostgreSQL запрос такой же.

### Задания

**1. Добавьте переменную.** Добавьте в `op_kwargs` ключ `"ds": "{{ ds }}"`, а в функцию аргумент `ds`. Что покажет `airflow tasks render` для даты 2025-04-24T22:00:00?

<details>
<summary>Решение</summary>

В `op_kwargs` появится `'ds': '2025-04-24'`. `ds` это дата как строка `YYYY-MM-DD`. Проверено запуском.

</details>

**2. Сломайте upsert.** В скрипте с идемпотентной записью уберите `PRIMARY KEY`, а `ON CONFLICT` оставьте. Что случится?

<details>
<summary>Решение</summary>

`sqlite3` выдаст ошибку `ON CONFLICT clause does not match any PRIMARY KEY or UNIQUE constraint`. Без ключа базе не с чем сравнивать строки. Проверено запуском.

</details>

## Вопросы для самопроверки

1. Почему `{{ ds }}` в аргументе, который не входит в `template_fields`, не работает?
2. Чем `PythonOperator` отличается от `BashOperator` в работе с context? Почему удобнее объявлять переменные явно?
3. Как проверить значения шаблона, не запуская задачу? Чем CLI лучше UI на этапе разработки?
4. Почему данные между задачами нельзя передать через память?
5. Чем оператор отличается от `hook`?

Предыдущая: [Asset-aware scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/). Следующая: [Зависимости между задачами](/book-summaries/engineering/data-pipelines-with-apache-airflow/06-task-dependencies/).
