---
title: "Образы и реестры"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker-образы: теги, Docker Hub, pull и версии | Инжиниринг Данных"
description: "Что такое образ Docker, как скачать его командой pull, почему нельзя брать тег latest, чем slim отличается от alpine и как безопасно чистить диск."
sidebar:
  order: 5
tags:
  - docker
  - practice
---

**Образ** — это шаблон, из которого запускают контейнер. Образ только читают. Контейнер — это запущенная копия образа.

Образы лежат в **реестре** (registry). Команда `docker run` сама скачивает образ из реестра, если его нет на вашем компьютере.

## Имя образа

Полное имя состоит из трёх частей:

```
реестр / репозиторий : тег
docker.io/library/postgres:17
```

| Часть | Пример | Что значит |
|---|---|---|
| Реестр | `docker.io` | Где лежит образ. По умолчанию Docker Hub |
| Репозиторий | `library/postgres` | Имя образа. `library` — официальные образы |
| Тег | `17` | Версия или вариант образа. По умолчанию `latest` |

Когда вы пишете `postgres:17`, Docker читает это как `docker.io/library/postgres:17`.

## Реестры

| Реестр | Адрес | Что там |
|---|---|---|
| Docker Hub | `docker.io` | Официальные образы: `postgres`, `python`, `nginx`, `alpine` |
| GitHub Container Registry | `ghcr.io` | Образы проектов на GitHub. Например `ghcr.io/dbt-labs/...` |
| Quay | `quay.io` | Образы Red Hat и Jupyter: `quay.io/jupyter/scipy-notebook` |
| Облачные реестры | AWS ECR, Google Artifact Registry, Azure ACR | Частные образы вашей команды. Об этом — в уроке [Контейнеры в продакшене](/practice/docker/production/) |

Для образа не из Docker Hub пишите адрес реестра целиком: `ghcr.io/owner/name:tag`.

## Скачать образ: pull

```bash
docker pull alpine:3.22
```

Посмотреть, какие образы уже есть:

```bash
docker images
```

```
REPOSITORY   TAG         IMAGE ID       CREATED      SIZE
alpine       3.22        49340b346798   ...          8.54MB
python       3.12-slim   5e2bdb1b0d54   ...          145MB
postgres     17          ...            ...          477MB
```

Список на вашем компьютере будет другим. Столбцы такие же. `IMAGE ID` — короткий отпечаток образа.

## Теги: всегда фиксируйте версию

Тег `latest` — ловушка. Он значит «последняя версия на сегодня». Завтра это будет другая версия.

Пример:

- Вы запускаете `postgres:latest` сегодня. Это Postgres 17.
- Через год коллега запускает ту же команду. Это уже другая мажорная версия.
- Данные в томе от старой версии могут не подойти к новой. Контейнер может не стартовать.

Правило: **всегда пишите версию**. Это `postgres:17`, `python:3.12-slim`, `nginx:1.29`.

| Тег | Насколько точный |
|---|---|
| `postgres:latest` | Плохо. Меняется без предупреждения |
| `postgres:17` | Хорошо. Мажорная версия фиксирована, обновляются только патчи |
| `postgres:17.11` | Строго. Меняется только по вашему решению |

## Варианты slim и alpine

Один и тот же Python есть в нескольких вариантах:

| Образ | Размер | Что внутри |
|---|---|---|
| `python:3.12` | около 1 ГБ | Полный Debian и компиляторы |
| `python:3.12-slim` | около 145 МБ | Debian без лишнего. **Наш выбор** |
| `python:3.12-alpine` | меньше всего | Alpine Linux. Часть пакетов Python ставится долго или не ставится |

Начинайте с `-slim`. Он маленький и работает с обычными пакетами Python (`pip install` без сюрпризов). Alpine берут, когда размер важнее всего, и вы знаете, зачем.

## Digest: самая точная ссылка

Тег можно перенести на другой образ. **Digest** перенести нельзя. Это отпечаток содержимого образа.

```bash
docker image inspect alpine:3.22 --format '{{index .RepoDigests 0}}'
```

```
alpine@sha256:49340b346798875b5592e5d420241f2f9cfba5f47e62ebb1446a1b34734e898f
```

Запуск по digest: `docker run alpine@sha256:49340b...`. В продакшене это даёт полную гарантию, что образ тот же. Для учёбы хватает тега с версией.

## Платформы: arm64 и amd64

У образа может быть несколько сборок для разных процессоров. Intel и AMD — это `linux/amd64`. Apple Silicon (M1–M4) и многие серверы AWS Graviton — это `linux/arm64`.

Если сборки для вашего процессора нет, получите ошибку. Вот настоящий пример на Mac с чипом M:

```bash
docker run --rm ghcr.io/dbt-labs/dbt-postgres:1.9.latest --version
```

```
docker: no matching manifest for linux/arm64/v8 in the manifest list entries
```

Образ dbt-postgres не собран для arm64. Что делать:

| Способ | Команда или шаг | Минус |
|---|---|---|
| Запустить как amd64 | `docker run --platform linux/amd64 ...` | Эмуляция. Медленно, иногда с ошибками |
| Собрать свой образ | `FROM python:3.12-slim` и `pip install dbt-postgres` | Нужно написать `Dockerfile` |

Второй способ лучше. Мы сделаем его в уроке [Open source за минуты](/practice/docker/use-cases/).

Узнать платформу образа:

```bash
docker image inspect alpine:3.22 --format '{{.Os}}/{{.Architecture}}'
```

## Диск и чистка

Образы, тома и кэш сборки занимают много места. Посмотреть, сколько:

```bash
docker system df
```

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          12        3         4.2GB     3.1GB (73%)
Containers      4         3         120MB     35MB (29%)
Local Volumes   6         2         1.1GB     900MB (81%)
Build Cache     40        0         200MB     200MB
```

Цифры у вас будут другими. На компьютере, где Docker работает давно, это бывают десятки гигабайт. Столбец `RECLAIMABLE` показывает, сколько места можно освободить.

Удалить один образ:

```bash
docker rmi alpine:3.22
```

Образ нельзя удалить, пока из него работает контейнер. Сначала остановите и удалите контейнер.

<details>
<summary>Чистка без риска</summary>

Команды `docker system prune` и `docker volume prune` удаляют сразу много. `volume prune` может удалить том с базой данных, если ни один контейнер сейчас его не использует.

Безопасный порядок:

1. Посмотрите, что есть: `docker system df`, `docker images`, `docker volume ls`.
2. Удаляйте по имени: `docker rmi <образ>`, `docker volume rm <том>`.
3. Если всё же нужен `prune`, начните с остановленных контейнеров: `docker container prune`. Он спросит подтверждение.
4. Тома не чистите массово. Сначала проверьте каждый.

</details>

## Практика

Работайте в любой папке. Файлы курса пока не нужны.

### Задание 1

Скачайте образ `alpine:3.22` командой `pull`. Потом выведите его размер из списка образов, только для `alpine`.

**Проверка:** в списке есть строка с `alpine` и тегом `3.22`. Размер около 8–9 МБ.

<details>
<summary>Решение</summary>

```bash
docker pull alpine:3.22
docker images alpine
```

</details>

### Задание 2

Найдите digest образа `alpine:3.22`.

**Проверка:** ответ начинается с `alpine@sha256:` и содержит 64 символа после двоеточия.

<details>
<summary>Решение</summary>

```bash
docker image inspect alpine:3.22 --format '{{index .RepoDigests 0}}'
```

</details>

### Задание 3

Сравните размеры `python:3.12-slim` и `python:3.12`. Скачайте оба и выведите размеры. Какой больше и во сколько раз?

**Проверка:** полный образ в несколько раз больше `slim`. Точные цифры зависят от версии.

<details>
<summary>Решение</summary>

```bash
docker pull python:3.12-slim
docker pull python:3.12
docker images python
```

Потом удалите полный образ, он вам не нужен: `docker rmi python:3.12`.

</details>

### Задание 4

Какая у образа `postgres:17` платформа (ОС и архитектура)?

**Проверка:** `linux/arm64` на Mac с чипом M. `linux/amd64` на Intel и AMD.

<details>
<summary>Решение</summary>

```bash
docker pull postgres:17
docker image inspect postgres:17 --format '{{.Os}}/{{.Architecture}}'
```

</details>

Дальше: [Порты и переменные окружения](/practice/docker/ports-env/).
