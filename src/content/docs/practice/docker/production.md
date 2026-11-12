---
title: Контейнеры в продакшене и облаке
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker в продакшене: ECS, Cloud Run, CI/CD | Инжиниринг Данных"
description: Как контейнеры работают в продакшене и в облаке. Реестры образов, ECS, Cloud Run, Azure, Airflow, правила для продакшена и сборка образа в GitHub Actions.
sidebar:
  order: 14
  label: Продакшен и облако
tags:
  - docker
  - practice
---

Образ, который работает на ноутбуке, работает и в облаке. Это главная причина, почему контейнеры любят в продакшене. Образ собирают один раз. Запускают где угодно.

## Путь от кода до продакшена

```
код в Git → CI собирает образ → образ в реестре → облако запускает контейнер
```

1. Вы пушите код в Git.
2. CI (например, GitHub Actions) выполняет `docker build`.
3. CI отправляет образ в **реестр** (`docker push`).
4. Облачный сервис берёт образ из реестра и запускает контейнер.

Сам образ на пути не меняется. Меняются только переменные окружения: адрес базы, пароль, имя бакета.

## Реестры образов

**Реестр** — хранилище образов. `docker pull` берёт образ оттуда.

| Реестр | Где |
|---|---|
| Docker Hub | Общий публичный реестр |
| GHCR (`ghcr.io`) | GitHub. Удобен, если код уже на GitHub |
| ECR | AWS |
| Artifact Registry | Google Cloud |
| ACR | Azure |

Обычно берут реестр того облака, где работает контейнер. Так быстрее и проще с правами.

## Где запускают контейнеры

| Облако | Сервис | Для чего |
|---|---|---|
| AWS | ECS на Fargate | Сервисы и задачи без управления серверами |
| AWS | AWS Batch | Большие пакетные задачи с очередью |
| AWS | Lambda (образ контейнера) | Короткие задачи по событию, до 15 минут. Образ должен быть на базе `public.ecr.aws/lambda/python` или содержать runtime interface client. Обычный `python:3.12-slim` не подойдёт |
| AWS | ECS Express Mode | Простой веб-сервис из образа. App Runner с 30.04.2026 закрыт для новых клиентов |
| Google Cloud | Cloud Run (services) | HTTP-сервис, масштабируется до нуля |
| Google Cloud | Cloud Run (jobs) | Пакетная задача: запустилась, отработала, остановилась |
| Azure | Container Apps (apps) | Сервисы и API |
| Azure | Container Apps (jobs) | Задачи по расписанию или по событию |

Для данных чаще всего нужна **пакетная задача**. Это контейнер, который запускается по расписанию, грузит данные и завершается. Именно так работает наш `load_orders.py`.

Кто запускает задачу по расписанию:

| Сервис | Расписание |
|---|---|
| ECS на Fargate | Amazon EventBridge Scheduler |
| Cloud Run jobs | Cloud Scheduler |
| Container Apps jobs | Встроенный cron в настройках задачи |
| Любой из них | Airflow, если между задачами есть зависимости |

## Контейнеры и Airflow

- **DockerOperator.** Задача DAG запускает контейнер на хосте. Окружение задачи не зависит от окружения Airflow.
- **KubernetesPodOperator.** То же самое, но контейнер запускается в Kubernetes.
- **Управляемый Airflow.** MWAA (AWS), Cloud Composer (Google Cloud), Astronomer. Облако само поддерживает Airflow. Вам не нужно запускать Kubernetes.

Про Kubernetes — в [следующем уроке](/practice/docker/kubernetes/).

## Правила для продакшена

| Правило | Что значит |
|---|---|
| Конфиг через переменные окружения | Один образ для dev и prod. Меняются только переменные |
| Секреты не в образе | Пароли и ключи берите из менеджера секретов (Secrets Manager, Secret Manager, Key Vault). Не пишите их в `Dockerfile` и не коммитьте `.env` |
| Логи в stdout и stderr | Пишите через `print` или `logging` в консоль. Облако соберёт их само |
| Неизменяемые теги | Тегируйте образ хешем коммита: `orders:9554b77`. Не используйте `latest` |
| Не root | `USER appuser` в `Dockerfile` |
| Лимиты ресурсов | `--memory` и `--cpus`. Один плохой контейнер не должен занять весь сервер |
| Health check | Оркестратор проверяет, что контейнер жив, и перезапускает его |
| Сканирование образов | Реестр или CI ищет известные уязвимости |
| Маленькие образы | `-slim`. Быстрее скачать, меньше уязвимостей. `alpine` хорош для утилит, но не для Python: многие пакеты под него не собраны |
| Один процесс на контейнер | База, приложение и планировщик — разные контейнеры |
| Контейнер без состояния | Для приложений и задач: данные живут в базе или S3, не в файлах контейнера. Саму базу держите в управляемом сервисе или в томе с бэкапами |

:::caution
Контейнер можно в любой момент удалить и создать заново. Всё, что вы сохранили внутри, пропадёт. Состояние держите снаружи.
:::

### Лимиты ресурсов

Ограничьте память и процессор:

```bash
docker run -d --name orders-limited --memory 256m --cpus 1 alpine:3.22 sleep 300
docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' orders-limited
```

Ответ:

```
orders-limited 1.344MiB / 256MiB 0.00%
```

После `/` стоит лимит: `256MiB`. Если контейнер превысит память, Docker остановит его (OOM kill). Лучше узнать об этом сейчас, чем в продакшене.

Удалите контейнер: `docker rm -f orders-limited`.

### Тег с хешем коммита

```bash
git rev-parse --short HEAD
```

Ответ — короткий хеш, например `9554b77`. Тег показывает, из какого коммита собран образ. Откат — это запуск старого тега.

```bash
docker build -t orders:9554b77 .
```

## GitHub Actions: сборка и отправка в GHCR

Файл `.github/workflows/docker.yml`. Мы его не запускали. Версии действий мы проверили на день написания (ноябрь 2026). Проверьте актуальные версии на страницах действий.

```yaml
name: docker

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: docker/setup-buildx-action@v4

      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

Что здесь важно:

- `permissions: packages: write` разрешает токену `GITHUB_TOKEN` писать образы в GHCR. Без него `push` вернёт ошибку доступа.
- Тег — полный хеш коммита `github.sha`. Это неизменяемый тег.
- Пароль не написан в файле. Токен выдаёт GitHub.
- Имя образа должно быть в нижнем регистре. Если в имени репозитория есть заглавные буквы, добавьте шаг `docker/metadata-action@v6`. Он сам делает имя маленькими буквами и готовит теги.

## Практика

### Задание 1

Создайте Git-репозиторий в `~/docker-practice` и сделайте коммит. Возьмите короткий хеш и поставьте его тегом на образ `alpine:3.22` с именем `orders-demo`.

**Проверка:** `docker images orders-demo` показывает тег, равный `git rev-parse --short HEAD`. У вас хеш будет другой.

<details>
<summary>Решение</summary>

```bash
cd ~/docker-practice
git init -q
git config user.email you@example.com
git config user.name you
git add .
git commit -qm "init"
SHA=$(git rev-parse --short HEAD)
docker tag alpine:3.22 orders-demo:$SHA
docker images orders-demo
```

Уберите за собой: `docker rmi orders-demo:$SHA`. Это удалит только тег. Образ `alpine:3.22` останется.

</details>

### Задание 2

Запустите `alpine:3.22` с командой `sleep 300`, лимитом памяти 128 МБ и одним процессором. Покажите использование памяти.

**Проверка:** в колонке памяти после `/` стоит `128MiB`.

<details>
<summary>Решение</summary>

```bash
docker run -d --name limit-test --memory 128m --cpus 1 alpine:3.22 sleep 300
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' limit-test
docker rm -f limit-test
```

</details>

### Задание 3

В `Dockerfile` есть шесть строк. Какие из них плохие для продакшена и почему?

```dockerfile
FROM python:latest
COPY . /app
ENV DB_PASSWORD=secret123
RUN pip install psycopg
USER root
CMD ["python", "/app/load_orders.py"]
```

**Проверка:** найдите пять проблем.

<details>
<summary>Решение</summary>

| Строка | Проблема | Как исправить |
|---|---|---|
| `FROM python:latest` | `latest` меняется. Образ тяжёлый | `FROM python:3.12-slim` |
| `COPY . /app` | Копирует всё, даже `.env` и `.git`. Ломает кэш | Сначала `requirements.txt`, потом код. Добавьте `.dockerignore` |
| `ENV DB_PASSWORD=secret123` | Пароль остаётся в образе и в истории слоёв | Передавайте пароль при запуске из менеджера секретов |
| `RUN pip install psycopg` | Нет версии. Нет `--no-cache-dir`. Нет `requirements.txt` | `pip install --no-cache-dir -r requirements.txt` |
| `USER root` | Запуск от root | `USER appuser` |

Строка `CMD` в порядке. Это шестая строка, и к ней нет замечаний.

</details>

Дальше: [Нужен ли Kubernetes](/practice/docker/kubernetes/).
