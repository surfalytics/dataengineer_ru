---
title: Шпаргалка и частые ошибки
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker: шпаргалка команд и частые ошибки | Инжиниринг Данных"
description: Шпаргалка по командам Docker и Compose, таблица частых ошибок с причинами и решениями, порядок отладки контейнера.
sidebar:
  order: 17
  label: Шпаргалка и ошибки
tags:
  - docker
  - practice
---

Эта страница — справочник. Держите её открытой, пока работаете.

:::danger
Команды с пометкой ⚠️ удаляют данные. Читайте, что именно они удалят, до нажатия Enter.
:::

## Контейнеры

| Команда | Что делает |
|---|---|
| `docker run IMAGE` | Создаёт и запускает контейнер |
| `docker run -d --name NAME -p 8080:80 IMAGE` | В фоне, с именем, с портом |
| `docker run --rm IMAGE` | Удаляет контейнер после выхода |
| `docker run -it IMAGE sh` | Интерактивная оболочка |
| `docker run -e KEY=value IMAGE` | Переменная окружения |
| `docker run -v "$PWD/data:/data" IMAGE` | Подключить папку |
| `docker ps` | Работающие контейнеры |
| `docker ps -a` | Все контейнеры, и остановленные тоже |
| `docker logs NAME` | Логи. С `-f` — следить за ними |
| `docker exec -it NAME sh` | Зайти в работающий контейнер |
| `docker stop NAME` | Остановить |
| `docker start NAME` | Запустить остановленный |
| `docker rm NAME` | Удалить остановленный контейнер |
| ⚠️ `docker rm -f NAME` | Остановить и удалить |
| `docker stats --no-stream` | Память и процессор |
| `docker inspect NAME` | Все детали контейнера |

## Образы

| Команда | Что делает |
|---|---|
| `docker pull IMAGE:TAG` | Скачать образ |
| `docker images` | Список образов |
| `docker build -t NAME:TAG .` | Собрать образ из `Dockerfile` |
| `docker tag SRC NAME:TAG` | Добавить тег |
| `docker push NAME:TAG` | Отправить в реестр |
| `docker history NAME:TAG` | Слои образа |
| `docker rmi NAME:TAG` | Удалить образ |

## Тома и сети

| Команда | Что делает |
|---|---|
| `docker volume ls` | Список томов |
| `docker volume create NAME` | Создать том |
| ⚠️ `docker volume rm NAME` | Удалить том и данные в нём |
| `docker network ls` | Список сетей |
| `docker network create NAME` | Создать сеть |
| `docker network inspect NAME` | Кто подключён к сети |

## Compose

| Команда | Что делает |
|---|---|
| `docker compose up -d` | Запустить всё в фоне |
| `docker compose up --build` | Пересобрать образы и запустить |
| `docker compose ps` | Сервисы. Остановленные видны с `-a` |
| `docker compose logs -f SERVICE` | Логи сервиса |
| `docker compose exec SERVICE sh` | Зайти в сервис |
| `docker compose run --rm SERVICE CMD` | Разовый запуск сервиса |
| `docker compose restart SERVICE` | Перезапуск |
| `docker compose down` | Удалить контейнеры и сеть. Тома остаются |
| ⚠️ `docker compose down -v` | Удалить ещё и тома. Данные базы пропадут |
| `docker compose config -q` | Проверить файл |
| `docker compose config --services` | Список сервисов |

## Очистка

| Команда | Что делает |
|---|---|
| `docker system df` | Сколько места занимает Docker |
| ⚠️ `docker system prune` | Удаляет остановленные контейнеры, неиспользуемые сети и висячие образы |
| ⚠️ `docker volume prune` | Удаляет тома, которые не использует ни один контейнер |

Перед `prune` посмотрите `docker ps -a` и `docker volume ls`. Остановленный контейнер может хранить нужные данные. Том без контейнера может быть вашей базой.

## Частые ошибки

| Сообщение | Причина | Что делать |
|---|---|---|
| `Bind for 0.0.0.0:8088 failed: port is already allocated` | Порт на вашем компьютере занят | Выберите другой порт слева: `-p 8089:80`. Или найдите владельца: `docker ps` |
| `no matching manifest for linux/arm64/v8 in the manifest list entries` | У образа нет сборки для вашего процессора (Mac с Apple) | Возьмите другой образ. Или `--platform linux/amd64` (медленнее). Или соберите образ сами |
| `connection to server at "127.0.0.1", port 5432 failed: Connection refused` | Приложение в контейнере ищет базу в `localhost`. Это он сам | Используйте имя сервиса: `DB_HOST=db`. Контейнеры должны быть в одной сети |
| `FileNotFoundError: [Errno 2] No such file or directory: '/data/orders.csv'` | Папку с данными не подключили | Добавьте `-v "$PWD/data:/data"` |
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` | Docker не запущен | Запустите Docker Desktop. На Linux: `sudo systemctl start docker` |
| `pull access denied for postgress, repository does not exist or may require 'docker login'` | Опечатка в имени образа. Или образ приватный | Проверьте имя на Docker Hub. Для приватного образа сделайте `docker login` |
| `no space left on device` | Диск Docker заполнен | `docker system df`. Удалите ненужные образы и тома. Осторожно с `prune` |
| Контейнер сразу завершился (`Exited (3)`) | Главная команда вышла с ошибкой | `docker logs NAME`, затем `docker inspect NAME --format '{{.State.ExitCode}}'` |
| `Database directory appears to contain a database; Skipping initialization` | Это не ошибка. В томе уже есть база | Читайте ниже: пароль не изменится |

### Postgres и смена пароля

Postgres читает `POSTGRES_PASSWORD` только при **первом** запуске с пустым томом. Мы запустили контейнер с паролем `one`, удалили его и запустили снова с паролем `two` на том же томе. В логе:

```
PostgreSQL Database directory appears to contain a database; Skipping initialization
```

Пароль остался `one`. Чтобы получить новый, удалите том (⚠️ данные пропадут) или смените пароль командой `ALTER USER` в SQL.

### Коды выхода

- `0` — программа завершилась успешно.
- `1` и другие числа — ошибка в программе. Мы запустили `exit 3` и получили `Exited (3)`.
- `137` — процесс убит. Часто из-за нехватки памяти.

## Как отлаживать

Идите по лестнице сверху вниз:

1. **Что с контейнером?** `docker ps -a`. Работает он, или завершился, и с каким кодом.
2. **Что он написал?** `docker logs NAME`. Чаще всего ответ уже здесь.
3. **Как он настроен?** `docker inspect NAME`. Проверьте переменные, порты, тома.
4. **Что внутри?** `docker exec -it NAME sh`. Посмотрите файлы и сеть.
5. **Контейнер не стартует?** Запустите образ с оболочкой вместо главной команды:

```bash
docker run --rm -it --entrypoint sh IMAGE
```

Пример: образ `alpine:3.22` с оболочкой вместо обычной команды:

```bash
docker run --rm --entrypoint sh alpine:3.22 -c 'echo in-shell'
```

Ответ: `in-shell`.

В Compose то же самое: `docker compose run --rm --entrypoint sh SERVICE`.

## Практика

### Задание 1

Запустите два контейнера `nginx:1.29` на одном порту `8120`. Прочитайте ошибку второго.

**Проверка:** в ошибке есть `port is already allocated`.

<details>
<summary>Решение</summary>

```bash
docker run -d --name web-a -p 8120:80 nginx:1.29
docker run -d --name web-b -p 8120:80 nginx:1.29
```

Второй контейнер не стартует: порт занят первым. Исправьте: `-p 8121:80`. Уберите за собой:

```bash
docker rm -f web-a web-b
```

</details>

### Задание 2

Запустите `alpine:3.22` с командой `sh -c 'echo boom; exit 3'` и именем `crash`. Найдите код выхода двумя способами.

**Проверка:** в статусе `Exited (3)`, а `docker inspect` печатает `3`.

<details>
<summary>Решение</summary>

```bash
docker run --name crash alpine:3.22 sh -c 'echo boom; exit 3'
docker ps -a --filter name=crash --format '{{.Status}}'
docker inspect crash --format '{{.State.ExitCode}}'
docker rm crash
```

</details>

### Задание 3

Опечатайтесь в имени образа: `docker pull postgress:17`. Прочитайте сообщение.

**Проверка:** сообщение начинается с `pull access denied for postgress`.

<details>
<summary>Решение</summary>

```bash
docker pull postgress:17
```

Правильное имя — `postgres` с одной `s`. Docker не отличает опечатку от приватного образа. Поэтому в сообщении есть слова про `docker login`.

</details>

### Задание 4

Запустите отчёт без `-v` и прочитайте ошибку. Потом исправьте команду. Нужен образ `orders-report:1.0` из урока про `Dockerfile`.

**Проверка:** сначала `FileNotFoundError: ... '/data/orders.csv'`, потом вывод `Заказов: 500`.

<details>
<summary>Решение</summary>

```bash
cd ~/docker-practice
docker run --rm orders-report:1.0
docker run --rm -v "$PWD/data:/data" orders-report:1.0
```

</details>

Вы прошли курс. Вернитесь к [описанию курса](/practice/docker/), если хотите повторить тему.
