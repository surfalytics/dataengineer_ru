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

**Главная мысль:** много разных операторов значит много зависимостей и конфликтов между ними. Контейнеры решают это. Каждая задача получает свой image, а в Airflow все задачи запускает один оператор: `DockerOperator` или `KubernetesPodOperator`.

## О чём глава

В [главе 10](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/) мы тестировали DAG. Теперь вопрос другой: как не утонуть в зависимостях, когда в Airflow десятки DAG и операторов. Авторы предлагают запускать каждую задачу как контейнер. В главе: проблемы разных операторов, основы Docker, зачем контейнеры в Airflow, `DockerOperator`, Kubernetes и `KubernetesPodOperator`.

![Рабочий процесс: образ собирают и кладут в registry, worker запускает его как контейнер задачи](/assets/data-pipelines-with-apache-airflow/ch11-container-workflow.png)

## Проблемы разных операторов

Авторы берут DAG с рекомендациями фильмов из главы 9. В нём три задачи: взять данные из API, посчитать рейтинг и записать итог в MySQL. Это три оператора: `HttpOperator`, `PythonOperator` и оператор для MySQL.

### Интерфейсы и реализации

Чтобы пользоваться оператором, надо знать его интерфейс и устройство. Если в нём баг, вы тратите время на поиск. Редкие операторы ошибаются чаще. В одном маленьком DAG это терпимо, в большом развёртывании тяжело.

### Конфликты зависимостей

У каждого оператора свои зависимости: `requests`, библиотеки для MySQL, `pandas` или `scikit-learn` для кода рекомендаций. Airflow ставит их все и в scheduler, и в каждый worker. Пакетов много, поэтому растут сложность и риск для безопасности.

Главная беда в Python: в одно окружение нельзя поставить две версии одного пакета. Если DAG 1 нужна библиотека A версии 1, а DAG 2 нужна A версии 2, придётся переписывать DAG или зависимости.

![Слева DAG с разными версиями библиотеки в одном окружении дают конфликт, справа у каждой задачи свой image](/assets/data-pipelines-with-apache-airflow/ch11-dependencies.png)

### Идея: один универсальный оператор

Если все задачи запускает один оператор, вы знаете только его, DAG проще читать, баги в общем операторе находят быстрее, а зависимостей Airflow нужен один набор. Такому оператору нужен способ запускать любую работу без установки её зависимостей. Это контейнеры.

## Контейнеры

Авторы коротко вводят Docker. Кто его знает, может пропустить раздел.

### Что такое контейнер

Приложение трудно развернуть: у машин разные ОС, библиотеки и железо. Первый ответ был виртуальная машина (VM). Она несёт целую гостевую ОС, поэтому тяжёлая. Контейнер использует ядро хост-ОС и изолирует приложение с его зависимостями, без отдельной ОС. Контейнерами управляет container engine: Docker или Podman.

### Первый контейнер в Docker

Команда `docker run debian:buster-slim echo Hello, world!` делает пять шагов. Клиент Docker обращается к Docker daemon на вашей машине. Daemon скачивает image из registry (по умолчанию Docker Hub) и создаёт из него контейнер. Контейнер выполняет `echo`. Daemon возвращает вывод в терминал. Тег, например `python:3.12`, выбирает версию image.

### Свой image

**Image** (образ) это шаблон. **Container** это запущенный image. Свой image описывают в `Dockerfile`. Начинается он с `FROM`: базовый image. Дальше идут инструкции `COPY`, `RUN`, `ENV` и другие: каждая добавляет слой с вашим кодом и зависимостями. `ENTRYPOINT` задаёт команду при старте, а `CMD` задаёт аргументы по умолчанию.

В примере книги скрипт `fetch_weather.py` берёт прогноз из API wttr.in. Ему нужны Python, `click` и `requests`. Image собирают командой `docker build --tag <имя> .`. Точка это build context: папка, где Docker ищет `Dockerfile` и файлы для `COPY`.

### Volumes

Если запустить скрипт с `--output_path amsterdam.out`, файла на вашей машине не будет. У контейнера своя изолированная файловая система, и она исчезает после остановки. Обменяться файлами можно двумя путями:

- хранилище по сети, например S3;
- смонтировать папку хоста: `--volume $(pwd)/data:/data` (слева путь на хосте, справа в контейнере).

Для уборки есть `docker ps` (работающие контейнеры), `docker stop <id>` и `docker rm <id>`. Остановленные контейнеры остаются в системе: их видно по `docker ps -a`.

## Контейнеры и Airflow

В Airflow задачу запускают как контейнер через `DockerOperator` или `KubernetesPodOperator`. Оператор стартует контейнер и ждёт его конца, как `docker run`. Рекомендательный DAG превращается в три `DockerOperator` с тремя образами. Образы надо собирать и хранить. Зачем это нужно:

| Плюс | Что значит |
|---|---|
| Зависимости | Каждый image содержит ровно то, что нужно задаче. Конфликтов нет. На worker ставить ничего не надо |
| Единый интерфейс | Все задачи это «запустить контейнер». Различаются image, настройки и команда |
| Тестируемость | Image живёт отдельно от DAG и имеет свои тесты на тестовых данных. С `PythonOperator` это труднее: функции тесно связаны с DAG |
| Безопасность | Критичные задачи держат в образах с проверенными библиотеками. Рискованные библиотеки остаются в других образах |

## Задачи в Docker

### DockerOperator

Он живёт в пакете `apache-airflow-providers-docker`. Параметры: `image`, `command`, `mounts` (или `volumes`, формат `хост:контейнер`), `network_mode`. В `command` работают шаблоны Jinja. При запуске:

1. Scheduler ставит задачу, worker берёт её.
2. Оператор запускает `docker run` на машине worker.
3. Если нужно, Docker скачивает image из registry.
4. Docker создаёт контейнер.
5. Docker монтирует volume. Когда команда закончилась, контейнер останавливается, а оператор забирает результат на worker.

### Image для задачи

Сначала надо понять, какие программы и зависимости нужны задаче. Дальше четыре шага:

1. Превратить код в CLI-скрипт. В книге это `click` (можно `argparse`): он сам разбирает и проверяет аргументы.
2. Написать `Dockerfile`: базовый image, зависимости (в файле или через `requirements.txt`), скрипт в `PATH`.
3. Собрать image: `docker build -t <имя> .`
4. Проверить: `docker run --rm <имя> <команда> --help`.

Если у задач много общего кода, у них может быть один image с разными командами. Как разбить образы, решаете вы. Вот CLI-скрипт для задачи `rank_movies`, с нашими данными.

```python
#!/usr/bin/env python
"""CLI-скрипт для задачи в контейнере: считает рейтинг фильмов из JSON с оценками.
Так выглядит код, который кладут в image (глава 11). click==8.5.1."""
import csv
import json
from collections import defaultdict
from pathlib import Path

import click


@click.command()
@click.option("--input_path", type=click.Path(exists=True), required=True, help="JSON с оценками.")
@click.option("--output_path", type=click.Path(), required=True, help="CSV с рейтингом.")
@click.option("--top", type=int, default=3, show_default=True, help="Сколько фильмов оставить.")
def main(input_path, output_path, top):
    """Считает средний рейтинг фильмов."""
    ratings = json.loads(Path(input_path).read_text())
    by_movie = defaultdict(list)
    for r in ratings:
        by_movie[r["movieId"]].append(r["rating"])
    rows = [(m, round(sum(v) / len(v), 2), len(v)) for m, v in by_movie.items()]
    rows.sort(key=lambda x: (-x[1], -x[2], x[0]))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)  # папка может быть новым volume
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["movieId", "avg_rating", "num_ratings"])
        w.writerows(rows[:top])
    click.echo(f"Фильмов в рейтинге: {min(top, len(rows))}. Файл: {out.name}")


if __name__ == "__main__":
    main()
```

### DAG на DockerOperator

Каждая задача это `DockerOperator` со своим image и командой. Файловая система контейнера живёт до конца задачи, поэтому данные между задачами идут через общий volume: первая пишет в `/data/ratings/...`, вторая читает оттуда. `network_mode` нужен, чтобы контейнер видел другой контейнер, например API в той же Docker-сети. Для API в интернете сеть не нужна. Логи контейнера попадают в лог задачи. Третью задачу, запись в базу, авторы оставляют читателю.

```python
"""DAG главы 11 на DockerOperator. Docker здесь не запускаем, файл только разбираем (ch11_check.py).
Нужны apache-airflow==3.4.0 и apache-airflow-providers-docker==4.6.1."""
import os
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

USER = os.environ.get("MOVIELENS_USER", "demo")
HOST = os.environ.get("MOVIELENS_HOST", "http://movielens:8081")
PASSWORD = os.environ.get("MOVIELENS_PASSWORD", "demo")

# Данные между задачами идут через общий volume.
with DAG(
    dag_id="11_docker_ratings",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule="@daily",
):
    fetch_ratings = DockerOperator(
        task_id="fetch_ratings",
        image="manning-airflow/movielens-fetch:1.0",
        command=[
            "fetch-ratings",
            "--start_date", "{{ data_interval_start | ds }}",
            "--end_date", "{{ data_interval_end | ds }}",
            "--output_path", "/data/ratings/{{ logical_date | ds }}.json",
            "--user", USER, "--password", PASSWORD, "--host", HOST,
        ],
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        network_mode="docker_default",
    )
    rank_movies = DockerOperator(
        task_id="rank_movies",
        image="manning-airflow/movielens-rank:1.0",
        command=[
            "rank-movies",
            "--input_path", "/data/ratings/{{ data_interval_start | ds }}.json",
            "--output_path", "/data/rankings/{{ data_interval_start | ds }}.csv",
        ],
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        network_mode="docker_default",
    )
    fetch_ratings >> rank_movies
```

Мы запустили CLI-скрипт без Docker, через `CliRunner`, на сгенерированных оценках (seed 11). Затем разобрали оба файла с DAG через `DagBag`.

```text
exit code: 0
Фильмов в рейтинге: 3. Файл: 2023-01-01.csv
movieId,avg_rating,num_ratings
30,4.4,5
40,4.09,11
20,4.0,11
без --input_path: exit code 2 | Error: Missing option '--input_path'.
DagBag: ошибки импорта: нет
11_docker_ratings {'fetch_ratings': 'DockerOperator', 'rank_movies': 'DockerOperator'} | rank_movies после ['fetch_ratings']
11_kubernetes_ratings {'fetch_ratings': 'KubernetesPodOperator', 'rank_movies': 'KubernetesPodOperator'} | rank_movies после ['fetch_ratings']
docker: image = manning-airflow/movielens-rank:1.0 | command[0] = rank-movies | network = docker_default
k8s: image = manning-airflow/movielens-rank:1.0 | cmds = ['rank-movies'] | on_finish_action = delete_pod
```

> **Пояснение:** DAG не запускали в Docker, его здесь нет. Образы не собирали. Проверен только разбор (Airflow 3.4.0, provider docker 4.6.1).

### Процесс работы

![Docker запускает контейнер на хосте worker, Kubernetes запускает pod на отдельном node](/assets/data-pipelines-with-apache-airflow/ch11-docker-vs-k8s.png)

Работа идёт в семь шагов:

1. Разработчик пишет `Dockerfile`. Он или CI/CD просит Docker собрать image.
2. Docker daemon собирает image.
3. Daemon отправляет image в container registry.
4. Разработчик пишет DAG с `DockerOperator`, который ссылается на image.
5. После включения DAG Airflow ставит задачи.
6. Worker берёт задачу и скачивает image.
7. Worker запускает контейнер через Docker daemon на своей машине.

Плюс: разработка образов отделена от разработки DAG. У образов свой жизненный цикл и свои тесты.

## Задачи в Kubernetes

Docker работает на одной машине и не распределяет работу. Для масштаба нужна оркестрация. `Kubernetes` это open source платформа для развёртывания и масштабирования контейнеров на кластере. Она учитывает CPU, память, хранилище и особое железо, например GPU.

### Как устроен Kubernetes

- **Master** (control plane): API server, scheduler и другие сервисы. Клиенты, например `kubectl` или Python SDK, говорят с API server.
- **Nodes**: машины, где работают приложения. Приложение живёт в **pod**: в нём один или несколько контейнеров на одной машине. В Airflow одна задача это один контейнер в одном pod.
- Kubernetes сам хранит секреты и выдаёт storage. Вы просите volume у master и монтируете его в контейнер.

### Подготовка

Нужны кластер (локально через Docker Desktop, minikube, K3s или в облаке) и `kubectl`. Проверка: `kubectl cluster-info`. Ресурсы описывают в YAML и применяют командой `kubectl apply -f`:

- `namespace` для ресурсов Airflow и pods задач;
- `PersistentVolume` (диск для pods) и `PersistentVolumeClaim` (заявка на часть диска): pods Airflow хранят данные через заявку;
- `Deployment` и `Service` для API: они говорят, как запустить сервис.

### KubernetesPodOperator

Он из пакета `apache-airflow-providers-cncf-kubernetes`. DAG почти тот же. Отличия в параметрах:

- `cmds` (что запустить) и `arguments` (аргументы) задают отдельно. В `DockerOperator` обе части лежат в `command`.
- Нужны `namespace` и `name` pod.
- Volumes описывают объектами Kubernetes SDK: `V1Volume` ссылается на заявку, `V1VolumeMount` задаёт путь в контейнере. Их передают в `volumes` и `volume_mounts`.
- `in_cluster=False`, если сам Airflow не внутри Kubernetes.
- `image_pull_policy="IfNotPresent"` берёт локальные образы.
- Pod после работы удаляется.

> **Пояснение:** в книге для удаления pod стоит `is_delete_operator_pod=True`. Этот аргумент устарел. Теперь пишут `on_finish_action="delete_pod"`. Это значение по умолчанию. Мы так и сделали в коде.

Полный пример: [ch11_k8s_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch11_k8s_dag.py). Кластера у нас нет: DAG только разобран через `DagBag`, pods не запускали. Статус проверок в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

### Если задача зависла

Частая причина: pod в состоянии `Pending`, Kubernetes не может его запустить. В логе Airflow идут предупреждения «Pod not yet started». Что делать:

1. Начните с лога задачи в Airflow.
2. Найдите pod: `kubectl --namespace airflow get pods`.
3. Посмотрите события: `kubectl describe pod <имя>`.
4. В примере книги было событие `FailedScheduling`: заявка `data-volume` не найдена. Забыли применить YAML с хранилищем. После `kubectl apply` pod запустился.

Pods по сути временные. Они могут упасть по многим причинам.

### Docker и Kubernetes: разница

Процесс в Kubernetes почти такой же, как в Docker. Кроме кластера, который надо поддерживать, отличий два: место запуска и хранилище.

| | Docker | Kubernetes |
|---|---|---|
| Где работает контейнер | На машине worker | На отдельном node. Нагрузка на worker минимальна |
| Ресурсы | Ресурсы worker | Node с нужными CPU, памятью, GPU |
| Хранилище | Локальное или volume Docker | Должно быть доступно pod: storage Kubernetes или облачное хранилище |
| Сложность | Низкая | Нужен кластер |

Авторы считают, что Kubernetes сильнее по масштабу, гибкости (разные ресурсы для разных задач) и управлению storage и секретами. Сам Airflow тоже можно запустить в Kubernetes.

## Итоги главы

- Много разных операторов усложняют развёртывание: разные API, баги в каждом и много зависимостей.
- Зависимости ставят на scheduler и worker. В одном окружении Python нельзя держать две версии пакета, поэтому возникают конфликты.
- Контейнер упаковывает задачу с зависимостями и изолирует её. В отличие от VM, он использует ядро хоста и поэтому лёгкий.
- Файлы внутри контейнера исчезают. Данные сохраняют через volume или сетевое хранилище.
- Контейнеры дают простые зависимости, единый интерфейс, тестируемость и безопасность.
- `DockerOperator` работает как `docker run` на worker. Сначала собирают и публикуют image, потом пишут DAG.
- `KubernetesPodOperator` запускает задачи как pods на кластере: это масштаб и выбор ресурсов, но нужен кластер.

## Ключевые термины

| Термин | Значение |
|---|---|
| Container | Изолированный процесс со своими зависимостями |
| Image | Шаблон, из которого запускают контейнер |
| `Dockerfile` | Рецепт сборки image |
| Container engine | Сервис, который управляет контейнерами: Docker, Podman |
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

## Практика

Docker и Kubernetes у нас не запускали. Задания проверяют понимание.

1. Напишите `Dockerfile` для `ch11_rank_movies.py`.
2. Pod висит в `Pending`, в событиях `persistentvolumeclaim "data-volume" not found`. Что делать?
3. DAG ссылается на `my-team/cleaner:latest`. Что может пойти не так?

<details>
<summary>Решения</summary>

1. Пример (не запускали, нужен Docker):

```dockerfile
FROM python:3.12-slim
RUN pip install click==8.5.1
COPY ch11_rank_movies.py /usr/local/bin/rank-movies
RUN chmod +x /usr/local/bin/rank-movies
```

   Скрипт начинается с `#!/usr/bin/env python`, поэтому его можно запускать как команду.

2. Заявки на хранилище нет. Примените YAML: `kubectl --namespace airflow apply -f data-volume.yml`. Потом снова посмотрите события pod.
3. Тег `latest` меняется. Завтра задача может запуститься с другим кодом. Используйте версию, например `my-team/cleaner:1.0`.

</details>

## Вопросы для самопроверки

1. Какие проблемы создают много разных операторов в одном Airflow?
2. Что происходит от запуска `DockerOperator` до остановки контейнера?
3. Почему между задачами в контейнерах нужен volume?
4. Чем `KubernetesPodOperator` отличается от `DockerOperator` по месту запуска и хранилищу?

Предыдущая: [Тестирование](/book-summaries/engineering/data-pipelines-with-apache-airflow/10-testing/). Следующая: [Best practices](/book-summaries/engineering/data-pipelines-with-apache-airflow/12-best-practices/).
