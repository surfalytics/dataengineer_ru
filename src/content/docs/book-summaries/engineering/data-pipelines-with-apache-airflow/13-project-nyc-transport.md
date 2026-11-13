---
title: "Data Pipelines with Apache Airflow, глава 13: Проект про транспорт Нью-Йорка"
head:
  - tag: title
    content: "Проект на Airflow: pandas, MinIO и идемпотентность | Инжиниринг Данных"
description: "Конспект главы 13 Data Pipelines with Apache Airflow на русском. Мини-проект: raw и processed слои, PandasOperator, идемпотентная запись в базу."
sidebar:
  order: 13
  label: "13. Проект: транспорт NYC"
tags:
  - books
  - airflow
  - orchestration
  - etl
---

**Главная мысль:** в реальном проекте нет готового оператора на каждый случай. Вы пишете свою логику на hooks и connections, храните сырые данные и делаете каждый шаг идемпотентным. Тогда любой запуск можно безопасно повторить.

## О чём глава

Первая глава-проект: pipeline с нуля из всего, что было в книге. Темы: промежуточные данные, идемпотентные tasks, один оператор для похожих преобразований. Общую картину смотрите в [обзоре](/book-summaries/engineering/data-pipelines-with-apache-airflow/).

![Схема проекта: два источника, скачивание в MinIO raw, обработка pandas, processed, PostgreSQL и веб-страница](/assets/data-pipelines-with-apache-airflow/ch13-nyc-pipeline.png)

## Задача проекта

Вопрос: что быстрее добраться из точки A в точку B по Нью-Йорку, такси или Citi Bike? Ответ зависит от района и времени суток. Город публикует данные о поездках раз в месяц. Это долго. Поэтому авторы сделали `Docker Compose` с двумя своими API, где интервал доходит до минуты. Там же MinIO (хранилище с протоколом S3), PostgreSQL и Flask-страница. Docker Compose мы не запускали.

Станции Citi Bike есть только в центре города. Поэтому сравнивать можно только зоны, где есть и такси, и Citi Bike.

## Данные в источниках

- **Yellow Cab.** Файл-индекс со списком CSV. Один файл на 15 минут, авторизации нет. В строке: время начала и конца поездки, ID зон. Хранится только последний час.
- **Citi Bike.** REST API с basic authentication. Адрес `/recent/<period>/<amount>`, период это минута, час или день. В JSON: время, координаты и названия станций, длительность.

## План подхода

- У такси есть ID зон, у Citi Bike координаты. Координаты станций привязывают к зонам такси. Это грубо: поездки внутри зоны разной длины. Книга принимает такую потерю точности.
- Такси хранит данные час, поэтому их сохраняют у себя.
- Оба источника режут данные по 15 минут. DAG тоже идёт каждые 15 минут. Так оба потока обрабатываются параллельно в одном DAG.

## Извлечение данных

Готовый `SimpleHttpOperator` не подходит: он делает запрос, но не сохраняет ответ. Нужна своя функция в `PythonOperator`. Для Citi Bike она берёт логин и пароль из connection и пишет JSON в MinIO через `S3Hook`. Имя файла содержит `data_interval_start`. Для такси сначала запрашивают индекс, потом скачивают каждый CSV: имена неизвестны заранее.

Connection задают переменной `AIRFLOW_CONN_<ID>` в формате URI. Есть ловушка: `S3Hook` по умолчанию ходит в AWS. Адрес MinIO надо дать в extras, ключ `endpoint_url`, а не в host. 

**Ловушка идемпотентности.** `S3Hook.load_string` не перезаписывает объект. Если ключ есть, он падает с `ValueError`. Для такси это сразу: файлы последнего часа повторяются при каждом запуске. Книга ловит `ValueError` и пишет в лог (стиль EAFP). Проще передать `replace=True`:

```python
s3_hook.load_string(string_data=text, key=f"raw/taxi/{name}", bucket_name="datalake", replace=True)
```

<details>
<summary>Код: ch13_nyc_dag.py</summary>

```python
"""Глава 13: каркас DAG проекта. Скачивание идёт в MinIO через S3Hook (нужны Docker Compose книги).
Здесь проверяется только разбор DAG. Импорты провайдеров лежат внутри функций."""
import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def _download_citi_bike_data(data_interval_start, **_):
    import json

    import requests
    from airflow.hooks.base import BaseHook
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
    from requests.auth import HTTPBasicAuth

    conn = BaseHook.get_connection("citibike")
    url = f"http://{conn.host}:{conn.port}/recent/minute/15"
    data = requests.get(url, auth=HTTPBasicAuth(conn.login, conn.password)).json()
    S3Hook(aws_conn_id="s3").load_string(
        string_data=json.dumps(data),
        key=f"raw/citibike/{data_interval_start.strftime('%Y%m%dT%H%M%S')}.json",
        bucket_name="datalake",
        replace=True,  # повтор не падает
    )


def _download_taxi_data():
    import requests
    from airflow.hooks.base import BaseHook
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    url = f"http://{BaseHook.get_connection('taxi').host}"
    s3_hook = S3Hook(aws_conn_id="s3")
    for name in [f["name"] for f in requests.get(url).json()]:
        text = requests.get(f"{url}/{name}").text
        s3_hook.load_string(string_data=text, key=f"raw/taxi/{name}", bucket_name="datalake", replace=True)


with DAG(
    dag_id="nyc_dag",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
):
    PythonOperator(task_id="download_citi_bike_data", python_callable=_download_citi_bike_data)
    PythonOperator(task_id="download_taxi_data", python_callable=_download_taxi_data)
```

</details>

DAG только разобрали через `DagBag`. Скачивание не запускали: нужны MinIO и API.

## Один оператор для похожих преобразований

Обработка Citi Bike и такси почти одинакова. Общее у них pandas `DataFrame`. Где считать, зависит от объёма:

- **Большие данные:** Spark (`SparkSubmitOperator`). Airflow только запускает и следит.
- **Малые данные:** pandas в `PythonOperator`. Он работает на машине Airflow и при нехватке памяти может уронить и Airflow.
- **Вынос тяжёлого:** `KubernetesPodOperator` или `ECSOperator`.

Книга берёт pandas и пишет свой `PandasOperator` из трёх функций:

| Функция | Что делает |
|---|---|
| `input_callable` | Читает данные, возвращает `DataFrame` |
| `transform_callable` | Необязательная. `DataFrame` на входе и на выходе |
| `output_callable` | Записывает `DataFrame`, например в Parquet |

![PandasOperator: input, transform и output вокруг DataFrame](/assets/data-pipelines-with-apache-airflow/ch13-pandas-operator.png)

Аргументы функций лежат в `template_fields`, поэтому в них работают шаблоны, например `data_interval_start | ts_nodash` в пути файла. Формат входа меняют одним аргументом: `pd.read_csv` на `pd.read_parquet`. Код не дублируется.

> **Пояснение:** в нашем примере MinIO заменён строкой и буфером в памяти, чтобы идти без Docker. Ядро оператора то же. Оператор берём из `airflow.sdk` (Airflow 3).

<details>
<summary>Код: ch13_pandas_operator.py</summary>

```python
"""Глава 13: PandasOperator из книги (read -> transform -> write вокруг DataFrame).
MinIO заменён строкой и буфером в памяти, чтобы пример шёл без Docker.
Запуск: $VENV/bin/python -I ch13_pandas_operator.py  (apache-airflow==3.4.0, pandas==2.3.3)"""
import io
import pandas as pd
from airflow.sdk import BaseOperator

CSV = """pickup_datetime,dropoff_datetime,pickup_locationid,dropoff_locationid,trip_distance
2024-09-19 18:55:06,2024-09-19 19:05:38,230,68,1.00
2024-09-19 18:50:29,2024-09-19 19:02:07,48,239,1.86
"""


class PandasOperator(BaseOperator):
    template_fields = ("_input_callable_kwargs", "_transform_callable_kwargs", "_output_callable_kwargs")

    def __init__(self, input_callable, output_callable, transform_callable=None,
                 input_callable_kwargs=None, transform_callable_kwargs=None,
                 output_callable_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self._input_callable = input_callable
        self._input_callable_kwargs = input_callable_kwargs or {}
        self._transform_callable = transform_callable
        self._transform_callable_kwargs = transform_callable_kwargs or {}
        self._output_callable = output_callable
        self._output_callable_kwargs = output_callable_kwargs or {}

    def execute(self, context):
        df = self._input_callable(**self._input_callable_kwargs)
        print("Read DataFrame with shape:", df.shape)
        if self._transform_callable:
            df = self._transform_callable(df, **self._transform_callable_kwargs)
            print("DataFrame shape after transform:", df.shape)
        self._output_callable(df, **self._output_callable_kwargs)


def read_text(pandas_read_callable, text):
    return pandas_read_callable(io.StringIO(text))


def transform_taxi_data(df):
    return (
        df.assign(
            starttime=lambda d: pd.to_datetime(d.pickup_datetime),
            stoptime=lambda d: pd.to_datetime(d.dropoff_datetime),
            tripduration=lambda d: (d.stoptime - d.starttime).dt.total_seconds().astype(int),
        )
        .rename(columns={"pickup_locationid": "start_location_id", "dropoff_locationid": "end_location_id"})
        .drop(columns=["trip_distance", "pickup_datetime", "dropoff_datetime"])
    )


def write_text(df, sink):
    sink.append(df.to_csv(index=False))


sink = []
op = PandasOperator(
    task_id="process_taxi_data",
    input_callable=read_text,
    input_callable_kwargs={"pandas_read_callable": pd.read_csv, "text": CSV},
    transform_callable=transform_taxi_data,
    output_callable=write_text,
    output_callable_kwargs={"sink": sink},
)
print("template_fields:", op.template_fields)
# execute() вызывают task runner; здесь берём исходную функцию без обёртки
type(op).execute.__wrapped__(op, {})
print(sink[0], end="")
```

</details>

```text
template_fields: ('_input_callable_kwargs', '_transform_callable_kwargs', '_output_callable_kwargs')
Read DataFrame with shape: (2, 5)
DataFrame shape after transform: (2, 5)
start_location_id,end_location_id,starttime,stoptime,tripduration
230,68,2024-09-19 18:55:06,2024-09-19 19:05:38,632
48,239,2024-09-19 18:50:29,2024-09-19 19:02:07,698
```

## Как структурировать pipeline

Можно писать одну функцию без файлов: извлечь, посчитать и записать в базу из памяти. Это быстрее. Но книга сохраняет промежуточные файлы:

- Данные нужны и другим людям и pipeline.
- Нужна воспроизводимость. REST API не вернёт состояние двухмесячной давности. Поэтому хранят копию входа почти без правок.

В своих системах данные раскладывают по жизненному циклу:

| Слой | Что хранит |
|---|---|
| `raw` | Исходные данные без изменений |
| `processed` | Очищенные данные. Расчёт дорогой, поэтому результат сохраняют |
| `export` | Наборы для передачи наружу |

Слоёв бывает больше (raw, preprocessed, enriched, processed, export). Единой схемы нет, её задаёт проект.

## Идемпотентные pipeline

Идемпотентность нужна в двух местах:

1. **Файлы в `processed`.** Включите перезапись. Тогда повтор не падает.
2. **Запись в базу.** Повтор не падает, но даёт дубли строк. Они портят результат.

![Сравнение записи без защиты и записи через DELETE и INSERT в транзакции](/assets/data-pipelines-with-apache-airflow/ch13-idempotent-write.png)

Решение: добавьте колонку с признаком запуска (в книге `airflow_execution_date`, туда `data_interval_start`). Потом в одной транзакции удалите строки этого запуска и вставьте новые. Транзакция атомарна: оба шага или ни одного, остатков при сбое нет. Мы повторили идею на SQLite с придуманной таблицей `rides`:

<details>
<summary>Код: ch13_idempotent_write.py</summary>

```python
"""Глава 13: запись в базу. append даёт дубли при повторе, DELETE + INSERT в транзакции не даёт.
SQLite в памяти вместо PostgreSQL. Запуск: python3 -I ch13_idempotent_write.py (нужны pandas, sqlalchemy)"""
import pandas as pd
import sqlalchemy as sa

df = pd.DataFrame({"start_location_id": [230, 48], "end_location_id": [68, 239], "tripduration": [632, 698]})
run_ts = pd.Timestamp("2024-09-19 19:15:00")


def count(engine, table):
    with engine.connect() as conn:
        return conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()


def save_rides(df, engine, run_ts):
    """Replace all rows of one run, then insert fresh rows."""
    df = df.assign(run_ts=run_ts)
    with engine.begin() as conn:  # one transaction
        if sa.inspect(conn).has_table("rides"):
            delete = sa.text("DELETE FROM rides WHERE run_ts = :ts").bindparams(
                sa.bindparam("ts", type_=sa.DateTime)
            )
            conn.execute(delete, {"ts": run_ts.to_pydatetime()})
        df.to_sql("rides", con=conn, index=False, if_exists="append")


naive = sa.create_engine("sqlite://")
for _ in range(2):
    df.to_sql("rides_append", con=naive, index=False, if_exists="append")
print("append, 2 запуска:", count(naive, "rides_append"), "строк")

safe = sa.create_engine("sqlite://")
for _ in range(2):
    save_rides(df, safe, run_ts)
print("DELETE + INSERT, 2 запуска:", count(safe, "rides"), "строк")
```

</details>

```text
append, 2 запуска: 4 строк
DELETE + INSERT, 2 запуска: 2 строк
```

Два `append` дали 4 строки, это дубли. Два `DELETE` + `INSERT` дали 2.

Веб-страница показывает результат. Пример книги: в четверг вечером из Astoria в Old Astoria такси быстрее: 996 секунд против 1465 у Citi Bike.

## Итоги главы

- Свои данные храните по слоям: `raw`, `processed`, `export`.
- Когда оператора не хватает, вызывайте функцию через `PythonOperator` или пишите свой оператор.
- `PandasOperator` обобщает pandas: функции чтения и записи меняются.
- Идемпотентность нужна для файлов и для базы.

## Ключевые термины

| Термин | Значение |
|---|---|
| MinIO | Хранилище с интерфейсом S3. Подходит для локальной работы |
| `raw` / `processed` / `export` | Слои данных по жизненному циклу |
| `PandasOperator` | Свой оператор: input, transform, output вокруг `DataFrame` |
| Idempotency | Повторный запуск даёт тот же результат без ручного сброса |

## Что это значит на практике

- Если готового оператора нет, пишите функцию на hook и connection. Если логика повторяется, делайте свой оператор.
- Храните сырые данные в `raw` без правок. Тогда можно пересчитать результат после исправления кода.
- Ключ запуска (`data_interval_start`) кладите в имя файла и в колонку таблицы. Он делает запись идемпотентной.
- Для базы используйте `DELETE` + `INSERT` в одной транзакции. В хранилище подойдёт `MERGE` или перезапись партиции. Вспомните `incremental` модели в `dbt`.
- Тяжёлую обработку не держите на машине Airflow. Выносите в Spark, Kubernetes или контейнер.
- Проверьте, как инструмент ведёт себя при повторе: падает, пропускает или дублирует.

## Практика

Скрипты: [ch13_idempotent_write.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch13_idempotent_write.py), [ch13_pandas_operator.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch13_pandas_operator.py). Проверка: [README](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

**Задание 1.** Вызовите `save_rides` для запусков 19:15, 19:30 и снова 19:15. Сколько строк будет после каждого вызова?

<details>
<summary>Решение</summary>

2, 4, 4. Повтор 19:15 удаляет свои строки и вставляет их снова. Мы запустили это на SQLite.

</details>

**Задание 2.** Как заставить `PandasOperator` читать JSON Citi Bike вместо CSV?

<details>
<summary>Решение</summary>

Заменить `pandas_read_callable` с `pd.read_csv` на `pd.read_json`. Оператор не меняется. Мы проверили `pd.read_json(io.StringIO(...))` на записи Citi Bike: получился `DataFrame` из 1 строки и 3 колонок.

</details>

## Вопросы для самопроверки

1. Почему для скачивания в MinIO нельзя взять готовый HTTP-оператор?
2. Зачем хранить `raw` и `processed` отдельно, если можно всё сделать в памяти?
3. Как `df.to_sql(..., if_exists="append")` ломает идемпотентность? Как это исправить?
4. Что общего у входов Citi Bike и такси позволило сделать один `PandasOperator`?

Предыдущая: [Best practices](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/). Следующая: [Проект: семейные традиции и GenAI](/book-summaries/engineering/data-pipelines-with-apache-airflow/14-project-genai-family-traditions/).
