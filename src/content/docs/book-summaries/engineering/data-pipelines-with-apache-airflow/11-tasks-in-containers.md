---
title: "Data Pipelines with Apache Airflow, глава 11: Запуск задач в контейнерах"
head:
  - tag: title
    content: "Airflow, Docker и Kubernetes: задачи в контейнерах | Инжиниринг Данных"
description: "Конспект главы 11 Data Pipelines with Apache Airflow на русском. Зачем контейнеры, DockerOperator, образы, volumes, Kubernetes и KubernetesPodOperator."
sidebar:
  order: 11
  label: "11. Задачи в контейнерах"
tags:
  - books
  - airflow
  - docker
  - kubernetes
---

**Главная мысль:** много разных операторов значит много зависимостей и конфликтов. Контейнеры решают это. Каждая задача получает свой образ, а в Airflow для всех задач работает один оператор: `DockerOperator` или `KubernetesPodOperator`.

![Рабочий процесс: образ собирают и кладут в registry, worker запускает его как контейнер задачи](/assets/data-pipelines-with-apache-airflow/ch11-container-workflow.png)

## Проблемы разных операторов

Пример: DAG с рекомендациями фильмов. Он берёт данные из API, считает рейтинг и пишет в MySQL. Это три разных оператора.

- Нужно знать интерфейс каждого оператора. Баги в редких операторах искать долго.
- У каждого оператора свои зависимости. Все они ставятся на scheduler и на worker.
- Версии библиотек конфликтуют. В одном окружении Python нельзя поставить две версии одного пакета.
- Больше пакетов значит больше рисков для безопасности.

Идея: взять один универсальный оператор, который запускает контейнер.

## Краткое введение в контейнеры

- Виртуальная машина (VM) несёт целую гостевую ОС. Она тяжёлая.
- Контейнер использует ядро хост-ОС. Он лёгкий, но изолирует приложение и его зависимости.
- Контейнером управляет container engine: Docker или Podman.
- **Image** это шаблон. **Container** это запущенный image.
- Image собирают из `Dockerfile` командой `docker build`. Запускают командой `docker run`.
- Файлы внутри контейнера исчезают после его остановки. Чтобы сохранить данные, подключают **volume**.

## Зачем это в Airflow

| Плюс | Что значит |
|---|---|
| Зависимости | Каждый image содержит ровно то, что нужно задаче. Конфликтов нет. На worker ничего ставить не надо |
| Единый интерфейс | Все задачи это «запустить контейнер». Различаются только image и команда |
| Тестируемость | Образ живёт отдельно от DAG и имеет свои тесты на тестовых данных |
| Безопасность | Критичные задачи можно держать в образах с проверенными библиотеками |

Цена: нужно собирать и хранить образы.

## DockerOperator

Он живёт в пакете `apache-airflow-providers-docker`. По сути это `docker run` с ожиданием результата.

Что происходит при запуске:

1. Scheduler ставит задачу, worker её берёт.
2. Оператор запускает `docker run` на машине worker.
3. Если образа нет локально, Docker скачивает его из registry.
4. Docker создаёт контейнер.
5. Volume монтируется в контейнер. Когда команда завершилась, контейнер останавливается, а оператор забирает результат.

Основные параметры: `image`, `command`, `mounts` или `volumes`, `network_mode`. В `command` работают шаблоны Jinja, например `{{ data_interval_start | ds }}`.

## Как делают образ для задачи

1. Превратите код в CLI-скрипт. В книге для этого `click` (можно `argparse`). Скрипт принимает даты, пути, параметры подключения.
2. Напишите `Dockerfile`: базовый образ Python, установка зависимостей, копирование скрипта, скрипт доступен в `PATH`.
3. Соберите образ: `docker build -t <имя> .`
4. Проверьте: `docker run --rm <имя> <команда> --help`.

Образы можно переиспользовать для похожих задач. Как их разбить, решаете вы.

## DAG на DockerOperator

- Каждая задача это `DockerOperator` со своим image и командой.
- Файловая система контейнера живёт только до конца задачи. Поэтому данные между задачами идут через общий volume. Первая задача пишет в `/data/ratings/...`, вторая читает оттуда.
- Нужен `network_mode`, если контейнер должен видеть другой контейнер (например, API в той же Docker-сети). Для API в интернете сеть настраивать не надо.
- Логи контейнера попадают в лог задачи Airflow.

### Процесс работы

1. Разработчик пишет `Dockerfile`.
2. Docker (локально или в CI/CD) собирает image.
3. Image уходит в container registry.
4. Разработчик пишет DAG с `DockerOperator`.
5. Airflow ставит задачи, worker скачивает image и запускает контейнер.

Плюс: разработка образа отделена от разработки DAG.

## Kubernetes

Docker работает на одной машине. Для масштаба нужна оркестрация. Kubernetes управляет контейнерами на кластере.

- **Control plane** (master): API server, scheduler и другие сервисы.
- **Nodes**: машины, где работают pods.
- **Pod**: самая маленькая единица. В Airflow одна задача это один контейнер в одном pod.
- Kubernetes сам выбирает node по ресурсам: CPU, память, GPU.
- Он умеет хранить секреты и выдавать storage.

Подготовка:

- `namespace` для ресурсов Airflow;
- `PersistentVolume` и `PersistentVolumeClaim` для данных;
- `Deployment` и `Service`, если нужен сервис вроде API.

Всё описывается в YAML и применяется командой `kubectl apply -f`.

## KubernetesPodOperator

Он из пакета `apache-airflow-providers-cncf-kubernetes`. DAG почти тот же, что с Docker. Отличия в параметрах.

- `cmds` (что запустить) и `arguments` (аргументы) задают отдельно.
- Нужны `namespace`, `name`, `volumes` и `volume_mounts`.
- `in_cluster=False`, если сам Airflow не внутри Kubernetes.
- `image_pull_policy="IfNotPresent"` берёт локальные образы.
- `on_finish_action="delete_pod"` удаляет pod после работы. Это значение по умолчанию. Старый аргумент `is_delete_operator_pod` устарел.

![Docker запускает контейнер на хосте worker, Kubernetes запускает pod на отдельном node](/assets/data-pipelines-with-apache-airflow/ch11-docker-vs-k8s.png)

### Если задача зависла

Частая причина: pod в состоянии `Pending`, Kubernetes не может его запустить.

1. Сначала смотрите лог задачи в Airflow.
2. Если там «Pod not yet started», найдите pod: `kubectl get pods`.
3. Посмотрите события: `kubectl describe pod <имя>`.
4. В примере книги не хватало `PersistentVolumeClaim`. Его создали, и pod запустился.

Pods по сути временные. Они могут упасть по многим причинам.

## Docker и Kubernetes: разница

| | Docker | Kubernetes |
|---|---|---|
| Где работает контейнер | На машине worker | На отдельном node кластера |
| Ресурсы | Ресурсы worker | Можно выбрать node по CPU, памяти, GPU |
| Хранилище | Локальное или volume Docker | Должно быть доступно pod: volumes, облачное хранилище |
| Сложность | Низкая | Нужен кластер и его поддержка |
| Масштаб | Одна машина | Кластер |

## Пример кода

Проверено на Airflow 3.4: DAG загружается. Для запуска нужны Docker и кластер Kubernetes.

Два оператора с одной идеей. Имена образов и команд придуманы для примера.

```python
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.cncf.kubernetes.operators.pod import (
    KubernetesPodOperator,
)

with DAG(
    dag_id="containers_demo",
    start_date=datetime(2025, 1, 1),
    schedule=None,
):
    clean_in_docker = DockerOperator(
        task_id="clean_in_docker",
        image="my-team/cleaner:1.0",
        command=[
            "clean-data",
            "--input", "/data/raw/{{ ds }}.csv",
            "--output", "/data/clean/{{ ds }}.csv",
        ],
        mount_tmp_dir=False,
    )

    clean_in_k8s = KubernetesPodOperator(
        task_id="clean_in_k8s",
        name="clean-data",
        namespace="airflow",
        image="my-team/cleaner:1.0",
        cmds=["clean-data"],
        arguments=["--input", "/data/raw/{{ ds }}.csv"],
        in_cluster=False,
        on_finish_action="delete_pod",
    )

    clean_in_docker >> clean_in_k8s
```

## Ключевые термины

| Термин | Значение |
|---|---|
| Container | Изолированный процесс со своими зависимостями |
| Image | Шаблон, из которого запускают контейнер |
| `Dockerfile` | Рецепт сборки image |
| Registry | Хранилище образов, например Docker Hub |
| Volume | Хранилище, которое живёт дольше контейнера |
| `DockerOperator` | Запускает задачу как `docker run` |
| Kubernetes | Оркестратор контейнеров на кластере |
| Pod | Минимальная единица в Kubernetes. Для Airflow это одна задача |
| `KubernetesPodOperator` | Запускает задачу как pod |
| `PersistentVolumeClaim` | Заявка на хранилище для pod |

## Что это значит на практике

- Если зависимости задач конфликтуют, выносите их в образы. Worker остаётся чистым.
- Данные между контейнерами передавайте через общее хранилище: volume, bucket, база. Не через файловую систему контейнера.
- Версионируйте образы тегами. Не полагайтесь на `latest`.
- Тестируйте образ отдельно от DAG, на небольших тестовых данных.
- Берите Kubernetes, когда нужен масштаб и разные ресурсы для задач. Для малых нагрузок хватает Docker.
- При проблемах с pod идите по цепочке: лог Airflow, `kubectl get pods`, `kubectl describe pod`.

## Вопросы для самопроверки

1. Какие проблемы создают много разных операторов в одном Airflow?
2. Что происходит от запуска `DockerOperator` до остановки контейнера?
3. Почему между задачами в контейнерах нужен volume?
4. Чем `KubernetesPodOperator` отличается от `DockerOperator` по месту запуска и хранилищу?

Предыдущая: [Тестирование](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/). Следующая: [Best practices](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/).
