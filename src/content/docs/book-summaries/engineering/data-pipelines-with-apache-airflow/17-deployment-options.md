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

**Главная мысль:** Docker Compose годится для разработки, но не для production. Есть два пути. Купить managed сервис и отдать ему работу. Или развернуть Airflow в Kubernetes самим и получить больше контроля.

![Выбор развёртывания: managed сервис или свой Kubernetes с Helm Chart](/assets/data-pipelines-with-apache-airflow/ch17-deploy-choice.png)

## Managed Airflow

Свой Airflow даёт гибкость, но требует много работы. Managed сервис берёт на себя инфраструктуру, патчи и мониторинг. В книге три примера.

| Сервис | Суть | Как деплоить DAG |
|---|---|---|
| Astronomer (Astro) | Платформа вокруг Airflow. Работает в Azure, AWS и Google Cloud. Команда Astronomer сильно участвует в разработке Airflow 3 | Через UI, Astro CLI, REST API или Terraform. Код синхронизируется с Git |
| Google Cloud Composer | Работает на GKE. Тесно связан с сервисами GCP, например BigQuery и Cloud Storage | Через GCP CLI или web-интерфейс |
| Amazon MWAA | Сервис AWS. Интеграция с S3, Redshift, SageMaker, CloudWatch, IAM. Использует `CeleryExecutor`, воркеры масштабируются по нагрузке | Загрузка DAG в S3 bucket |

Что даёт Astronomer кроме хостинга:

- Astro CLI для локальной разработки.
- Astro IDE: редактор в браузере.
- Cosmos: запуск проектов `dbt Core` как DAG.
- Astro Observe: наблюдаемость, lineage, SLA, стоимость.
- Обзор всех deployments в одном UI. Удобно для нескольких команд.

Про цену: Composer берёт плату за environment плюс за GKE и Cloud Storage. MWAA берёт базовую плату, плату за каждого worker и за хранение metastore.

## Airflow в Kubernetes

Для своего production нужен кластер Kubernetes. В книге его заменяет k3s внутри Docker Compose. Он поднимает кластер, PostgreSQL и Docker registry. Компоненты Airflow потом ставят внутрь кластера.

- `kubectl` смотрит ресурсы кластера.
- `helm` ставит приложения. Это package manager для Kubernetes. Пакет называется chart.

### Официальный Helm Chart

Сначала ставят chart с настройками по умолчанию. Единственная правка: `apiServer.service.type=LoadBalancer`, чтобы UI был виден снаружи кластера. В списке pods видно знакомую архитектуру из главы 1:

| Pod | Роль |
|---|---|
| api-server | UI и API |
| scheduler | Планирует task |
| dag-processor | Читает DAG-файлы |
| triggerer | Deferrable операторы |
| worker | Выполняет task |
| redis | Очередь для Celery |
| postgresql | Metastore |
| statsd | Метрики |

Настройки меняют так: пишут values-файл и запускают `helm upgrade --install ... -f values.yaml`. Значения по умолчанию видно командой `helm show values`. В книге каждый следующий values-файл содержит и прежние правки. Иначе они откатятся.

### Шаги настройки

1. **Свой начальный пользователь.** Блок `webserver.defaultUser` в values. Прежний пользователь остаётся, если базу не пересоздавали.
2. **Статичный secret key для api-server.** По умолчанию chart генерирует новый ключ при каждом обновлении, и компоненты лишний раз перезапускаются. Создайте Kubernetes secret и сошлитесь на него через `apiSecretKeySecretName`. Книга предупреждает: так хранить ключ всё ещё небезопасно. Для production берите внешний store (Key Vault, Vault, Secret Manager).
3. **Внешняя база для metadata.** Это лучший вариант для production. Вы сами настраиваете доступ, backup и восстановление. Параметры подключения кладут в Kubernetes secret. Затем отключают встроенный PostgreSQL (`postgresql.enabled: false`) и задают `data.metadataSecretName`. Совет: с PostgreSQL включите PgBouncer. Airflow открывает много соединений, а пул их сокращает.

## Как доставить DAG

![Три способа доставки DAG: image, persistent volume и git-sync](/assets/data-pipelines-with-apache-airflow/ch17-dag-delivery.png)

| Способ | Как работает | Плюсы | Минусы |
|---|---|---|---|
| DAG в image | `COPY dags` в Dockerfile, сборка и push в registry | Immutable. Всегда ясно, какая версия кода. Апгрейд Airflow меняет тег базового image. Так делает и Astronomer | Каждая правка требует сборки и деплоя image. Неудобно для многих команд |
| Persistent volume | Общий том Kubernetes, DAG копирует CI/CD | Подходит для нескольких команд | Нужен свой CI/CD для копирования. Зависит от типа тома |
| Git-sync | Sidecar-контейнер `git-sync` тянет код из репозитория | Просто и удобно. DAG обновляются при новом коммите | Нужен доступ к репозиторию. Задаются ветка, ревизия и подпапка |

С git-sync в pod dag-processor появляется контейнер `git-sync`. Настройка идёт в блоке `dags.gitSync`: адрес репозитория, ветка, глубина клона и `subPath` с DAG.

## Как доставить Python-библиотеки

- `_PIP_ADDITIONAL_REQUIREMENTS` ставит пакеты при старте. Удобно для разработки, но не для production.
- Для production установите пакеты в image: `FROM apache/airflow:<версия>` и `RUN pip install ...`. Потом соберите image и пропишите его в `images.airflow.repository` и `images.airflow.tag`.
- Минус: у всех worker один набор зависимостей. При нескольких командах зависимости начнут конфликтовать.
- Выход: несколько очередей `CeleryExecutor`. Каждая очередь получает свой worker и свой image с нужными библиотеками.
- Для изоляции есть и запуск task в контейнерах. Это тема главы 11.

## Пример кода

Проверено на Airflow 3.4: DAG проходит `airflow dags test`.

Книга показывает Dockerfile и YAML. Вот Python-часть: простой DAG, который проверяет, что библиотека есть в image. Имена в нём придуманы здесь.

```python
import pendulum
from airflow.sdk import DAG, task

with DAG(
    dag_id="check_image_libs",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
):

    @task
    def print_pandas_version():
        import pandas

        print(pandas.__version__)

    print_pandas_version()
```

## Ключевые термины

| Термин | Значение |
|---|---|
| Managed Airflow | Сервис, где провайдер ведёт инфраструктуру Airflow |
| Astro | Managed платформа Astronomer |
| Cloud Composer | Managed Airflow в Google Cloud |
| MWAA | Managed Airflow в AWS |
| Helm / chart | Package manager Kubernetes и пакет приложения |
| values-файл | YAML, который переопределяет настройки chart |
| Kubernetes secret | Объект для хранения секретов в кластере |
| Persistent volume | Общее хранилище, смонтированное в pods |
| git-sync | Sidecar, который тянет DAG из Git |
| PgBouncer | Пул соединений для PostgreSQL |

## Что это значит на практике

- Начните с вопроса: есть ли у команды люди, которые ведут Kubernetes? Если нет, возьмите managed сервис.
- Для Airflow в Kubernetes берите официальный Helm Chart. Все настройки держите в values-файлах в Git.
- Всегда выносите metastore во внешнюю базу с backup. Добавьте PgBouncer.
- Не используйте `_PIP_ADDITIONAL_REQUIREMENTS` в production. Собирайте image.
- Для одной команды подойдёт DAG в image. Для нескольких команд смотрите git-sync или volume.
- Не храните пароли в values-файлах. Берите их из secrets backend (глава 16).

## Вопросы для самопроверки

1. Какие три managed сервиса назвала книга? Чем они отличаются?
2. Какие pods появляются после установки Helm Chart? За что отвечает каждый?
3. Почему metastore лучше держать во внешней базе?
4. Какой способ доставки DAG вы выберете для трёх команд и почему?

Предыдущая: [Безопасность Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/16-securing-airflow/).
