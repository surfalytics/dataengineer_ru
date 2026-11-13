---
title: "Data Pipelines with Apache Airflow, глава 17: Варианты развёртывания"
head:
  - tag: title
    content: "Развёртывание Airflow: managed и Kubernetes | Инжиниринг Данных"
description: "Конспект главы 17 Data Pipelines with Apache Airflow на русском. Managed Airflow, Helm Chart в Kubernetes, внешняя база и способы доставки DAG."
sidebar:
  order: 17
  label: "17. Развёртывание"
tags:
  - books
  - airflow
  - kubernetes
  - deployment
---

**Главная мысль:** Docker Compose годится для разработки, но не для production. Есть два пути. Купить managed сервис и отдать ему работу. Или развернуть Airflow в Kubernetes самим и получить больше контроля. Какой путь лучше, зависит от команды, облака и бюджета.

## О чём глава

До сих пор все примеры шли в Docker Compose. Для production он не подходит. Глава отвечает, где и как запускать Airflow дальше. Она идёт после [главы 16](/book-summaries/engineering/data-pipelines-with-apache-airflow/16-securing-airflow/) о безопасности. Темы: managed сервисы, Helm Chart в Kubernetes, доставка DAG и библиотек, несколько executors, выбор стратегии.

![Выбор развёртывания: managed сервис или свой Kubernetes с Helm Chart](/assets/data-pipelines-with-apache-airflow/ch17-deploy-choice.png)

## Managed Airflow

Свой Airflow даёт максимум гибкости, но требует много работы. Managed сервис отдаёт её провайдеру: он обновляет ОС и Airflow, ставит патчи и мониторит систему. Книга описывает три сервиса.

### Astronomer

Astronomer занимается только Airflow. Люди компании входят в Airflow PMC и сильно участвовали в разработке Airflow 3. Её сервис Astro работает в Azure, AWS и Google Cloud. Deployments создают через UI, Astro CLI, REST API или Terraform. Один UI показывает все deployments и их стоимость. Для нескольких команд это удобно.

Кроме хостинга есть Astro CLI для локальной разработки, Astro IDE (редактор в браузере), Cosmos (запуск проектов `dbt Core` как DAG) и Astro Observe: здоровье pipelines, lineage, SLA, качество данных и стоимость.

### Google Cloud Composer

Composer почти в один клик ставит Airflow в GCP. Он работает на Google Kubernetes Engine (GKE) и тесно связан с BigQuery, Cloud Storage и другими сервисами GCP. Плата идёт за сам environment и за GKE и Cloud Storage. Операторы Google для её сервисов работают и вне Composer.

### Amazon MWAA

MWAA похож на Composer, но живёт в AWS. Он интегрирован с S3, Redshift, SageMaker, CloudWatch и IAM. Он использует `CeleryExecutor` и сам масштабирует workers. DAG загружают в S3 bucket. Цена: базовая плата за environment, плата за каждый worker и плата за хранение metastore.

## Airflow в Kubernetes

Нужен кластер Kubernetes. Для примеров автор берёт k3s в Docker Compose: он поднимает кластер, внешний PostgreSQL и Docker registry. Airflow ставят внутрь кластера. `kubectl` смотрит ресурсы кластера. `helm` ставит приложения: это package manager для Kubernetes, а пакеты называются charts.

### Официальный Helm Chart

Сначала ставят официальный chart с настройками по умолчанию. Одна правка: `apiServer.service.type=LoadBalancer`, чтобы UI был виден снаружи. В списке pods видна архитектура из главы 1.

| Pod | Роль |
|---|---|
| api-server | UI и API |
| scheduler | Планирует tasks |
| dag-processor | Читает DAG-файлы |
| triggerer | Следит за deferrable операторами |
| worker | Выполняет tasks |
| redis | Очередь для Celery |
| postgresql | Metastore |

### Как менять настройки

Настройки меняют через values-файлы. Значения по умолчанию показывает `helm show values apache-airflow/airflow`. Вы пишете файл с правками и запускаете `helm upgrade --install ... -f values.yaml`.

Есть ловушка: helm не помнит прошлые файлы. Поэтому каждый следующий файл в книге содержит новую правку и все прежние. Иначе они откатятся к значениям по умолчанию.

![Четыре values-файла: каждый повторяет правки предыдущих](/assets/data-pipelines-with-apache-airflow/ch17-values-layers.png)

Скрипт показывает это на урезанных значениях, кластер не нужен.

```python
"""Глава 17: как helm собирает настройки. Чистый Python + PyYAML 6.0.3, кластер не нужен.
Helm берёт значения chart по умолчанию и накладывает на них values-файл.
Прежние values-файлы он не помнит, поэтому каждый новый файл повторяет старые правки."""
import yaml

# Урезанные значения chart по умолчанию (настоящие даёт `helm show values`)
DEFAULTS = yaml.safe_load("""
postgresql: {enabled: true}
webserver: {defaultUser: {username: admin}}
apiSecretKeySecretName: null
""")

FILE_01_USER = "webserver: {defaultUser: {username: airflow}}"
FILE_02_SECRET = "apiSecretKeySecretName: my-apiserver-secret"
FILE_03_DB = "postgresql: {enabled: false}"


def merge(base, over):
    """Глубокое слияние: значения из over заменяют значения из base."""
    out = dict(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], val)
        else:
            out[key] = val
    return out


def release(*files):
    """Итоговые настройки после `helm upgrade -f файл ...` (без --reuse-values)."""
    values = DEFAULTS
    for text in files:
        values = merge(values, yaml.safe_load(text))
    return values


def show(title, values):
    print(title)
    print("  встроенный PostgreSQL:", values["postgresql"]["enabled"])
    print("  пользователь:", values["webserver"]["defaultUser"]["username"])
    print("  secret key:", values["apiSecretKeySecretName"])


# Файл 03 накапливает правки 01 и 02, как в книге
cumulative = FILE_03_DB + "\n" + FILE_02_SECRET + "\n" + FILE_01_USER
show("Файл 03 повторяет прежние правки:", release(cumulative))
show("Файл 03 только с новой правкой:", release(FILE_03_DB))
```

```text
Файл 03 повторяет прежние правки:
  встроенный PostgreSQL: False
  пользователь: airflow
  secret key: my-apiserver-secret
Файл 03 только с новой правкой:
  встроенный PostgreSQL: False
  пользователь: admin
  secret key: None
```

Файл [ch17_values_layers.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch17_values_layers.py) лежит в репозитории, вывод одинаков при шести запусках. Сам `helm upgrade` не запускали.

### Шаги настройки

1. **Свой начальный пользователь.** Блок `webserver.defaultUser`. Старый остаётся, если базу не пересоздавали.
2. **Статичный secret key для api-server.** По умолчанию chart генерирует новый ключ при каждом обновлении, и компоненты лишний раз перезапускаются. Создайте Kubernetes secret и сошлитесь на него через `apiSecretKeySecretName`. Автор предупреждает: так хранить ключ всё ещё небезопасно. Для production берите внешний store: Key Vault, HashiCorp Vault или Secret Manager.
3. **Внешняя база для metadata.** Это лучший вариант для production: вы сами настраиваете доступ, backup и восстановление. Параметры подключения кладут в Kubernetes secret, потом отключают встроенный PostgreSQL (`postgresql.enabled: false`) и задают `data.metadataSecretName`. База новая, прежнего пользователя в ней нет. Совет автора: для PostgreSQL включите PgBouncer. Airflow открывает много соединений, а пул их сокращает.

## Как доставить DAG

Нужно доставить DAG во все компоненты Airflow. Есть три способа.

![Три способа доставки DAG: image, persistent volume и git-sync](/assets/data-pipelines-with-apache-airflow/ch17-dag-delivery.png)

**DAG в image.** Файлы запекают в image строкой `COPY dags` в Dockerfile. Любая правка требует нового image, поэтому версия кода всегда ясна. Так делает и Astronomer. Апгрейд Airflow сводится к смене тега базового image. Image кладут в registry и прописывают в `images.airflow.repository` и `images.airflow.tag`. Минус: неудобно, если DAG пишут несколько команд.

**Persistent volume.** Это абстракция Kubernetes над хранилищем: общий том монтируется в pods. Способ подходит для нескольких команд. Сложнее всего CI/CD: код надо копировать в том, а решение зависит от типа тома.

**Git-sync.** В pod dag-processor появляется sidecar-контейнер `git-sync`. Он тянет DAG из Git и обновляет их при новой версии. В values задают репозиторий, ветку, глубину клона и `subPath` с DAG.

```yaml
dags:
  persistence:
    enabled: false
  gitSync:
    enabled: true
    repo: https://github.com/example-org/airflow-dags.git
    branch: main
    ref: main
    depth: 1
    maxFailures: 0
    subPath: "dags"
```

Файл [ch17_git_sync_values.yaml](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch17_git_sync_values.yaml) разбирается как YAML без ошибок. На кластере его не запускали.

## Как доставить Python-библиотеки

Для DAG нужны ещё pandas или providers. Переменная `_PIP_ADDITIONAL_REQUIREMENTS` ставит пакеты при старте. Это удобно в разработке, но не для production. Для production пакеты ставят в image (`FROM apache/airflow:<версия>`, `RUN pip install ...`) и прописывают его в `images.airflow.*`.

Минус: у всех worker один набор зависимостей. Если Airflow делят несколько команд, зависимости конфликтуют. Выход: несколько очередей `CeleryExecutor`, у каждой свой worker и свой image. Другой путь изоляции описан в [главе 11](/book-summaries/engineering/data-pipelines-with-apache-airflow/11-tasks-in-containers/).

## Несколько executors

В Airflow 2 для этого был `CeleryKubernetesExecutor`. В Airflow 3 он устарел. Теперь можно включить несколько executors и выбирать нужный для каждой task. Функция ещё экспериментальная.

В values ставят `executor: "CeleryExecutor,KubernetesExecutor"`. Книга собирает три image: общий для Celery (без TensorFlow), по умолчанию для `KubernetesExecutor` (с TensorFlow) и ещё один со старой версией TensorFlow, который задаёт сама task. DAG печатает версию TensorFlow. Task на Celery падает: библиотеки нет. Две task на `KubernetesExecutor` проходят.

![Две tasks с разными executors: Celery падает без библиотеки, Kubernetes запускает pod со своим image](/assets/data-pipelines-with-apache-airflow/ch17-multi-executor.png)

Ниже наша версия без TensorFlow: у второй task свой image через `pod_override`.

```python
"""Глава 17: две task, два executor. Одна идёт в Celery worker, другая в отдельный pod
со своим image. Нужен values: executor: "CeleryExecutor,KubernetesExecutor"."""
import pendulum
from airflow.sdk import DAG, task
from kubernetes.client import models as k8s

# Свой image только для этой task: pod_override правит pod, который создаст executor
OLD_LIBS = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[k8s.V1Container(name="base", image="registry:5000/team-a/airflow-libs:1.0")]
        )
    )
}

with DAG(
    dag_id="executors_demo",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
):

    @task(executor="CeleryExecutor")
    def on_celery():
        print("работаю в общем worker")

    @task(executor="KubernetesExecutor", executor_config=OLD_LIBS)
    def on_k8s():
        print("работаю в своём pod со своим image")

    on_celery() >> on_k8s()
```

Проверка без кластера читает DAG через `DagBag`.

```text
ошибки импорта: нет
on_celery: executor=CeleryExecutor, image=по умолчанию
on_k8s: executor=KubernetesExecutor, image=registry:5000/team-a/airflow-libs:1.0
```

Проверено на Airflow 3.4.0 и `apache-airflow-providers-cncf-kubernetes==11.0.0`: DAG разбирается, вывод одинаков при шести запусках. Сами tasks и `airflow dags test` не запускали: нужны Celery worker и Kubernetes. Если executor нет в `[core] executor`, Airflow отклоняет DAG при разборе (`UnknownExecutorException`). Это мы проверили. Список проверок в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

## Как выбрать стратегию

Свой deployment гибче, но требует опыта, особенно для безопасности и стоимости. Managed решение снимает эти заботы, но может быть негибким. Пять вопросов автора:

- **Нужен ли Kubernetes?** Astronomer и GCP дают простой путь. Можно и поставить Airflow в свой кластер.
- **К каким сервисам идут DAG?** В GCP очевидный выбор Composer. Для on-premise или других облаков менее логичен.
- **Как доставлять DAG?** Astronomer даёт CLI, Composer даёт bucket. Подумайте о CI/CD.
- **Сколько платить?** Kubernetes бывает дорогим из-за кластера. SaaS вроде Astronomer бывает дешевле. Если кластер уже есть, запускайте Airflow в нём.
- **Нужен ли тонкий контроль?** Тогда свой deployment, но с затратами на поддержку.

## Итоги главы

- Managed сервисы снимают работу с инфраструктурой: Astronomer, Cloud Composer, MWAA.
- Airflow в Kubernetes через Helm Chart даёт полную гибкость, но требует опыта.
- Настройки chart меняют values-файлом и `helm upgrade`. Каждый файл повторяет прежние правки.
- Для production нужны статичный secret key, внешняя база metadata и PgBouncer.
- DAG доставляют тремя способами: в image, через persistent volume или через git-sync.
- Библиотеки для production ставят в image. Для разных зависимостей есть очереди Celery и несколько executors.
- Выбор зависит от Kubernetes, облака, доставки DAG, цены и нужного контроля.

## Ключевые термины

| Термин | Значение |
|---|---|
| Managed Airflow | Сервис, где провайдер ведёт инфраструктуру Airflow |
| Astro, Composer, MWAA | Managed Airflow: Astronomer, Google Cloud, AWS |
| Helm / chart | Package manager Kubernetes и пакет приложения |
| values-файл | YAML с правками настроек chart |
| git-sync | Sidecar, который тянет DAG из Git |
| PgBouncer | Пул соединений для PostgreSQL |

## Что это значит на практике

- Начните с вопроса: есть ли у команды люди, которые ведут Kubernetes? Если нет, возьмите managed сервис.
- Для Airflow в Kubernetes берите официальный Helm Chart. Все настройки держите в values-файлах в Git.
- Всегда выносите metastore во внешнюю базу с backup. Добавьте PgBouncer.
- Не используйте `_PIP_ADDITIONAL_REQUIREMENTS` в production. Собирайте image.
- Для одной команды подойдёт DAG в image. Для нескольких команд смотрите git-sync или volume.
- Не храните пароли в values-файлах. Берите их из secrets backend (глава 16).
- Не кладите в values-файл только новую правку. Проверяйте итог командой `helm get values`.
- Для задачи с особыми библиотеками дайте ей свой executor и image, а не ломайте общий image.

## Практика

Код выше работает без кластера.

1. Что напечатает `ch17_values_layers.py`, если убрать из накопленного файла `FILE_02_SECRET`?
2. Что случится с DAG `executors_demo`, если убрать `CeleryExecutor` из `[core] executor`?
3. Какой способ доставки DAG выбрать одной команде с жёстким аудитом версий? А трём командам?

<details>
<summary>Решение</summary>

1. Secret key вернётся к значению по умолчанию: `None`. Мы проверили запуском: пользователь `airflow`, встроенный PostgreSQL `False`, secret key `None`.
2. Airflow отклонит DAG при разборе: `UnknownExecutorException`. Мы получили эту ошибку в DagBag.
3. Одной команде подойдёт DAG в image: версия всегда ясна. Трём командам лучше git-sync или volume: не нужен общий image.

</details>

## Вопросы для самопроверки

1. Какие три managed сервиса назвала книга? Чем они отличаются?
2. Какие pods появляются после установки Helm Chart? За что отвечает каждый?
3. Почему metastore лучше держать во внешней базе?
4. Почему каждый values-файл должен повторять прежние правки?
5. Как дать одной task свою версию библиотеки, не меняя общий worker?

Предыдущая: [Безопасность Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/16-securing-airflow/).
