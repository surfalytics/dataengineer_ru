---
title: "Data Pipelines with Apache Airflow, глава 8: Связь с внешними системами"
head:
  - tag: title
    content: "Airflow providers, hooks и A-to-B operators | Инжиниринг Данных"
description: "Конспект главы 8 Data Pipelines with Apache Airflow на русском. Provider packages, SageMaker, hooks, A-to-B operators, airflow tasks test, DockerOperator."
sidebar:
  order: 8
  label: "8. Внешние системы"
tags:
  - books
  - airflow
  - operators
  - hooks
---

**Главная мысль:** сила Airflow в том, что он соединяет другие системы. `Operator` - это тонкий слой над клиентом сервиса. Сложность обычно не в Airflow, а в настройке самой внешней системы. Тяжёлую работу выносите из Airflow.

## О чём глава

До сих пор книга брала `BashOperator` и `PythonOperator`. Автор считает, что это не лучшее применение Airflow. Глава учит ставить operators для внешних систем и строит два pipeline: обучение ML-модели в AWS и перенос данных из PostgreSQL в S3. Предыдущая глава: [Запуск workflow внешними событиями](/book-summaries/engineering/data-pipelines-with-apache-airflow/07-triggering-external-input/). Свои operators разбирает [глава 9](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/).

![Pipeline обучения ML-модели: Airflow готовит данные, обучает и деплоит модель, а API живёт отдельно](/assets/data-pipelines-with-apache-airflow/ch08-ml-pipeline.png)

## Установка дополнительных operators

У облачных API есть Python-клиент: `boto3` для AWS, Cloud SDK для GCP, Azure SDK. Operator это тонкий слой над ним: вы заполняете аргументы, а он вызывает клиент. Пакет `apache-airflow` содержит только базовые operators. Остальные идут в `provider package` для каждой системы, его ставят через `pip`.

| Система | Пакет |
|---|---|
| AWS | `apache-airflow-providers-amazon` |
| GCP | `apache-airflow-providers-google` |
| Azure | `apache-airflow-providers-microsoft-azure` |
| PostgreSQL | `apache-airflow-providers-postgres` |

Пример: `S3CopyObjectOperator` копирует объект между bucket. Вы задаёте имена и ключи, а внутри он вызывает `copy_object()` из `boto3`. Operators быстро развиваются, готовый вариант мог уже появиться.

## Use case 1: обучение ML-модели

Книга строит классификатор рукописных цифр на датасете MNIST (около 70 000 картинок) в AWS. Данные лежат в S3, модель обучается в SageMaker (сервис AWS для разработки и деплоя ML-моделей).

У модели две части. Offline-часть обучает модель и сохраняет параметры. Online-часть загружает модель и классифицирует новую картинку мгновенно. Airflow подходит для offline-части: периодическое переобучение ложится на batch-подход. Online-часть это обычно API. Его выкатывают один раз или через CI/CD: перевыкатывать API каждую неделю незачем.

### Pipeline в DAG

В DAG шесть tasks.

1. `S3CreateBucketOperator` создаёт bucket.
2. `PythonOperator` ставит bucket policy для чтения из SageMaker.
3. `S3CopyObjectOperator` копирует датасет в свой bucket.
4. `PythonOperator` с `S3Hook` переводит данные в формат recordIO.
5. `SageMakerTrainingOperator` обучает модель.
6. `SageMakerEndpointOperator` деплоит модель за HTTP endpoint.

Сила Airflow в расписании: при новых данных или правке модели DAG сам перезапустит pipeline и задеплоит новую версию. Код DAG длинный из-за настроек SageMaker. Автор делает вывод: сложность не в Airflow, а в стыковке частей.

> **Пояснение:** `hook` это класс, который подключается к системе по `connection ID`. Operator использует hook внутри, а в своём коде hook можно взять самому, как `S3Hook` в шаге 4.

Для шага 4 готового operator нет, поэтому функцию пишут сами. Она читает объект в `io.BytesIO`, пишет recordIO и грузит результат в S3. Файлов не остаётся, но датасет маленький (15 МБ). Для больших данных пишите на диск и читайте частями.

### Локальная разработка: airflow tasks test

Как проверить task, не запуская весь pipeline? Если есть доступ к облаку, запустите одну task: `airflow tasks test <dag_id> <task_id> <date>`.

1. Положите ключи в `~/.aws/credentials` и задайте `AWS_PROFILE`. `boto3` сам найдёт их.
2. Задайте `AIRFLOW_HOME`. Папку `dags` Airflow ищет внутри. Другую задают через `AIRFLOW__CORE__DAGS_FOLDER`.
3. Выполните `airflow db init`. Без `AIRFLOW__CORE__SQL_ALCHEMY_CONN` создаётся локальный SQLite.
4. Запустите `airflow tasks test`.

Команда не пишет состояние в базу, но база нужна для логов. Если в task есть `{{ ds }}`, подумайте, какую дату передать. В production автор советует secret manager (Vault, Key Vault, AWS SSM, глава 16). Ещё есть экспериментальный Object Storage (с Airflow 2.8): единый код для S3, GCS и Azure Blob.

### Два урока для любой внешней системы

**Уникальные имена.** AWS требует уникальное `TrainingJobName` в аккаунте и регионе, иначе второй запуск упадёт. `config` поддерживает templates, поэтому в имя добавляют `logical_date`. Тогда task идемпотентна.

**Ожидание завершения.** Клиент `boto3` работает как `fire and forget`: запустил job и забыл. SageMaker operators по умолчанию ждут (`wait_for_completion=True`) и опрашивают AWS каждые `check_interval` секунд. Task успешна, только когда job в AWS закончилась. Если ниже по графу есть tasks, ждать нужно.

![Fire and forget против wait_for_completion: во втором случае task зависит от результата job](/assets/data-pipelines-with-apache-airflow/ch08-wait-completion.png)

### API для пользователей

Endpoint SageMaker не виден из интернета. Нужны Lambda и API Gateway. Их ставят один раз, это online-стадия, то есть CI/CD, а не DAG. Для примера автор пишет API на Chalice (фреймворк, похожий на Flask): он принимает JPEG, вызывает endpoint и возвращает ближайший кластер.

## Use case 2: перенос данных между системами

Классическая задача Airflow это периодический ETL. Продакшн-базы обычно не хранят историю, поэтому данные выгружают регулярно.

Пример автора: объявления Airbnb в Амстердаме. Раз в день данные из PostgreSQL выгружаются в S3. Потом контейнер с `pandas` считает изменение цен и пишет результат обратно в S3. В `docker compose` три сервиса: PostgreSQL, MinIO (хранилище с S3 API) и Airflow. В большой системе контейнер заменил бы Spark job.

### A-to-B operators

Запрос в MySQL с записью в GCS, копия с SFTP в S3, вызов REST API: везде две системы, вход и выход. Для этого есть `A-to-B operators`: `MySqlToGoogleCloudStorageOperator`, `SFTPToS3Operator`, `SimpleHttpOperator`. Готового `PostgresToS3Operator` нет. Автор советует посмотреть на похожие operators и написать свой (глава 9).

![Как устроен A-to-B operator: два hooks и промежуточное хранение между ними](/assets/data-pipelines-with-apache-airflow/ch08-a-to-b.png)

В обоих примерах из книги `execute()` создаёт два hooks, для системы A и для B. Различается место промежуточного результата.

| Operator | Где результат | На что смотреть |
|---|---|---|
| `MongoToS3Operator` | В памяти | Хватит ли RAM |
| `S3ToSFTPOperator` | Во временном файле | Хватит ли места на диске |

Для PostgreSQL можно читать порциями через курсоры. Автор считает, что результат помещается в ресурсы Airflow.

### Первая версия и её ошибка

Минимальный `PostgresToS3Operator` создаёт два hooks, вызывает `get_records()` и `load_string()`. Две тонкости.

- `S3Hook` принимает `aws_conn_id`, а не `s3_conn_id`, потому что наследует `AwsBaseHook`. Такое ищут в исходниках.
- `get_records()` возвращает список кортежей (PEP 249). Если превратить его в строку через `str()`, `pandas` и Spark такой текст не прочтут.

Решение: записать результат в CSV через `csv.writer` в буфер и загрузить через `load_file_obj()`. Результат должен помещаться в память. Идемпотентность даёт `replace=True`: после правки кода повторный запуск не упадёт на существующем файле. В запросе и ключе используют templates: `data_interval_start` и `{{ ds }}`.

### Тяжёлую работу выносим

В сообществе спорят: Airflow только запускает работу (orchestration) или ещё и выполняет её (execution). `BashOperator` и `PythonOperator` работают в том же Python, что и Airflow. Противники считают, что работу должен делать Spark. Если job займёт все ресурсы машины, пусть Airflow стартует её и ждёт. Spark job запускают тремя способами.

| Способ | Что нужно |
|---|---|
| `SparkSubmitOperator` | `spark-submit` и конфиг YARN на машине Airflow |
| `SSHOperator` | SSH-доступ к Spark |
| `SimpleHttpOperator` | Запущенный Livy (REST API для Spark) |

![Orchestration и execution: Airflow запускает job, а работу делает Spark или контейнер](/assets/data-pipelines-with-apache-airflow/ch08-orchestration-execution.png)

В примере книги работу делает `DockerOperator`: контейнер читает данные из S3, считает изменение цены за день и пишет JSON обратно. Airflow запускает контейнер, забирает логи и удаляет его. Состояние не остаётся, поэтому task идемпотентна (глава 11).

## Итоги главы

- Operators вызывают клиент внешней системы. Иногда они добавляют логику, как опрос в SageMaker operators.
- Каждая система имеет свой provider package.
- Одну task можно проверить через `airflow tasks test`.
- Разовую инфраструктуру деплойте через CI/CD, а не через DAG.
- A-to-B operators переносят данные между системами. Нужного нет, напишите свой.
- Ждите завершения внешней работы и давайте ей уникальные имена.
- Разделяйте orchestration и execution.

## Ключевые термины

| Термин | Значение |
|---|---|
| Provider package | Пакет с operators и hooks для одной системы |
| `Hook` | Класс для подключения к системе по `connection ID` |
| A-to-B operator | Operator, который переносит данные из одной системы в другую |
| `airflow tasks test` | Команда, которая запускает одну task без записи состояния |
| `wait_for_completion` | Operator ждёт конца внешней работы |
| Fire and forget | Запустить работу и не проверять результат |
| `DockerOperator` | Запускает контейнер как task |
| Orchestration vs execution | Airflow управляет, другая система считает |
| `replace=True` | Перезапись объекта в S3. Нужна для идемпотентности |

## Что это значит на практике

- Сначала ищите готовый operator в provider package. Свой пишите, только если его нет.
- Читайте документацию внешней системы. Большая часть проблем будет там, а не в Airflow.
- Давайте внешним ресурсам уникальные имена с `logical_date`. Так перезапуск и backfill безопасны.
- Всегда ждите завершения внешней работы или используйте deferrable-версию (глава 7).
- Не загружайте большие данные в память worker. Читайте частями или передавайте через диск и хранилище.
- Тяжёлые трансформации отдавайте в Spark, dbt, warehouse или контейнер. Airflow только запускает их.
- Разовую инфраструктуру (API, Lambda) выкатывайте через CI/CD, а не через DAG.
- Проверяйте одну task локально через `airflow tasks test`. Не ждите полного запуска.
- Следите за версией provider: у `SageMakerTrainingOperator` в новых версиях есть `action_if_job_exists`, и имя job можно не менять вручную. Читайте changelog provider.

## Практика

Запускали на Airflow 3.4.0 (providers amazon 9.40.0, postgres 7.1.2) без AWS и PostgreSQL: hooks заменены `mock`. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

DAG обучения в сокращённом виде. Имя job содержит `logical_date`, а `wait_for_completion=True` ждёт конца job.

```python
"""Глава 8: DAG обучения модели в SageMaker (сокращённая версия). Только описание, в AWS не ходит.
Имя training job содержит logical_date, wait_for_completion=True ждёт конца job."""
import pendulum
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator
from airflow.providers.amazon.aws.operators.sagemaker import SageMakerTrainingOperator
from airflow.sdk import DAG

BUCKET = "my-mnist-bucket"

with DAG(
    dag_id="mnist_train",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
):
    copy_data = S3CopyObjectOperator(
        task_id="download_mnist_data",
        source_bucket_name="sagemaker-sample-data-eu-west-1",
        source_bucket_key="algorithms/kmeans/mnist/mnist.pkl.gz",
        dest_bucket_name=BUCKET,
        dest_bucket_key="mnist.pkl.gz",
    )
    train = SageMakerTrainingOperator(
        task_id="sagemaker_train_model",
        config={
            "TrainingJobName": "mnistclassifier-{{ logical_date | ts_nodash }}",
            # ... остальной config: образ, гиперпараметры, S3-пути, роль ...
        },
        wait_for_completion=True,  # task успешна, только когда job в AWS закончилась
        print_log=True,
        check_interval=10,  # опрос AWS каждые 10 секунд
    )
    copy_data >> train
```

Проверка через `DagBag` ([ch08_check_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch08_check_dag.py)):

```text
ошибки импорта: нет
tasks: ['download_mnist_data', 'sagemaker_train_model']
тип train: SageMakerTrainingOperator
wait_for_completion: True | check_interval: 10
config в template_fields: True
logical_date 2025-01-01 -> mnistclassifier-20250101T000000
logical_date 2025-01-08 -> mnistclassifier-20250108T000000
```

Две даты дают два имени. Теперь свой A-to-B operator (имена выдуманы).

```python
"""Глава 8: свой A-to-B operator. Читает заказы из PostgreSQL и кладёт CSV в S3.
Имена выдуманы. Здесь только сам operator, проверка в ch08_check_operator.py."""
import csv
import io

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import BaseOperator


class OrdersToS3Operator(BaseOperator):
    template_fields = ("query", "s3_key")

    def __init__(self, query, s3_bucket, s3_key, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

    def execute(self, context):
        rows = PostgresHook(postgres_conn_id="shop_db").get_records(self.query)
        text = io.StringIO()
        csv.writer(text, lineterminator="\n").writerows(rows)  # список кортежей -> CSV
        S3Hook(aws_conn_id="lake").load_file_obj(
            io.BytesIO(text.getvalue().encode()),
            bucket_name=self.s3_bucket,
            key=self.s3_key,
            replace=True,  # повторный запуск перезапишет файл, а не упадёт
        )
```

Проверка без PostgreSQL и S3 ([ch08_check_operator.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch08_check_operator.py)):

```text
str(records): [(1, 'Ann', 10.5), (2, 'Bob, Jr.', 7.0)]
template_fields: ('query', 's3_key')
CSV для S3: '1,Ann,10.5\n2,"Bob, Jr.",7.0\n'
bucket: lake | key: orders-{{ ds }}.csv | replace: True
conn ids: {'postgres_conn_id': 'shop_db'} {'aws_conn_id': 'lake'}
```

Запятая попала в кавычки, `replace=True` передан. Шаблон `{{ ds }}` Airflow подставит при запуске. Полный DAG с SageMaker и Docker не запускали: нужны AWS и Docker.

### Задания

**1. Запятая в данных.** Что будет с `Bob, Jr.`, если записать кортежи через `str()` вместо `csv.writer`?

<details>
<summary>Решение</summary>

`str()` вернёт одну строку вида `[(1, 'Ann', 10.5), ...]`. Её не прочтёт ни `pandas`, ни Spark. `csv.writer` берёт `Bob, Jr.` в кавычки (`"Bob, Jr."`), и запятая внутри не ломает столбцы. Видно в выводе выше.

</details>

**2. Имя job.** Что будет, если `TrainingJobName` без `logical_date` и DAG запущен дважды?

<details>
<summary>Решение</summary>

AWS требует уникальное имя в аккаунте и регионе, и второй запуск упадёт с ошибкой. С `logical_date` имена разные: `mnistclassifier-20250101T000000` и `mnistclassifier-20250108T000000`. Это видно в выводе выше.

</details>

**3. Где что живёт.** Куда отнести: (а) обучение модели раз в неделю; (б) Lambda и API Gateway для пользователей; (в) расчёт на 500 ГБ данных?

<details>
<summary>Решение</summary>

(а) В DAG: это offline-часть, повторяется по расписанию. (б) В CI/CD: разовый деплой online-части. (в) В Spark или контейнер: Airflow только запускает job и ждёт.

</details>

## Вопросы для самопроверки

1. Зачем нужны provider packages? Что делает operator внутри?
2. Почему в имя training job добавляют `logical_date`?
3. Чем `MongoToS3Operator` отличается от `S3ToSFTPOperator` по хранению промежуточных данных?
4. Почему лучше не выполнять тяжёлую обработку внутри Airflow?

Предыдущая: [Запуск workflow внешними событиями](/book-summaries/engineering/data-pipelines-with-apache-airflow/07-triggering-external-input/). Следующая: [Свои operators и sensors](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/).
