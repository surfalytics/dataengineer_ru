---
title: "Порты и переменные окружения"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker: порты, -p, -e и запуск Postgres | Инжиниринг Данных"
description: "Как открыть порт контейнера командой -p, передать настройки через -e и --env-file, запустить Postgres в Docker и подключиться к нему через psql."
sidebar:
  order: 6
tags:
  - docker
  - practice
---

Контейнер изолирован. Снаружи его не видно, пока вы не откроете порт. Настройки в контейнер передают через переменные окружения.

## Порты: -p

Программа в контейнере слушает свой порт. Например, Postgres слушает `5432`. Чтобы подключиться с вашего компьютера, нужно связать порт компьютера с портом контейнера:

```
-p ПОРТ_КОМПЬЮТЕРА:ПОРТ_КОНТЕЙНЕРА
```

```bash
docker run -d --name web -p 8080:80 nginx:1.29
```

- `80` — порт nginx внутри контейнера.
- `8080` — порт на вашем компьютере.
- Откройте `http://localhost:8080` в браузере. Вы увидите страницу nginx.

Проверьте и в терминале:

```bash
curl -s localhost:8080 | head -4
```

```
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
```

Столбец `PORTS` в `docker ps` показывает связку:

```
IMAGE        STATUS         PORTS                                     NAMES
nginx:1.29   Up 2 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

Остановите и удалите контейнер:

```bash
docker rm -f web
```

### Только для своего компьютера

`-p 8080:80` открывает порт на всех сетевых интерфейсах. Любой в вашей Wi-Fi сети может зайти на ваш nginx или на вашу базу.

Чтобы открыть порт только для себя, добавьте адрес `127.0.0.1`:

```bash
-p 127.0.0.1:5432:5432
```

:::tip
Для баз данных на ноутбуке всегда пишите `127.0.0.1:`. Так базу не увидят другие.
:::

### Порт уже занят

Если порт на компьютере занят, Docker не запустит контейнер:

```
docker: Error response from daemon: failed to set up container networking: driver failed
programming external connectivity on endpoint web (...): Bind for 0.0.0.0:8088 failed: port is already allocated
```

Что делать:

- Выберите другой порт на компьютере: `-p 8089:80`. Порт контейнера (`80`) не меняйте.
- Или найдите, кто занял порт: `docker ps` покажет контейнеры, `lsof -i :8088` на macOS и Linux покажет процессы.

## Переменные окружения: -e

Многие образы настраиваются через переменные окружения. Их передают флагом `-e`:

```bash
docker run --rm -e GREETING=привет alpine:3.22 sh -c 'echo $GREETING'
```

```
привет
```

Кавычки вокруг `echo $GREETING` важны. Без них ваш shell подставит `$GREETING` сам, ещё до контейнера, и получится пустая строка.

### Много переменных: --env-file

Если переменных много, храните их в файле. Каждая строка — `ИМЯ=значение`:

```bash
printf 'POSTGRES_PASSWORD=secret\nPOSTGRES_DB=shop\n' > pg.env
docker run -d --name pg --env-file pg.env postgres:17
```

Файл `.env` с паролями **не добавляют в Git**. Положите его в `.gitignore`.

## Запускаем Postgres

Образ `postgres:17` настраивается переменными:

| Переменная | Зачем | Обязательна |
|---|---|---|
| `POSTGRES_PASSWORD` | Пароль пользователя `postgres` | **Да** |
| `POSTGRES_DB` | Имя базы, которую создать при первом старте | Нет. По умолчанию `postgres` |
| `POSTGRES_USER` | Имя пользователя | Нет. По умолчанию `postgres` |

Без пароля контейнер не стартует:

```bash
docker run --rm postgres:17
```

```
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".
```

Запустите правильно:

```bash
docker run -d --name pg \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=shop \
  -p 127.0.0.1:5432:5432 \
  postgres:17
```

Если у вас уже есть контейнер `pg` из примера с `--env-file`, сначала удалите его: `docker rm -f pg`.

Подождите пять секунд, пока база стартует. Проверьте:

```bash
docker ps --filter name=pg
```

```
IMAGE         STATUS         PORTS                      NAMES
postgres:17   Up 6 seconds   127.0.0.1:5432->5432/tcp   pg
```

## Подключиться: два способа

**Способ 1. Через `docker exec`.** Команда запускается внутри контейнера. Ничего ставить на компьютер не нужно.

```bash
docker exec -it pg psql -U postgres -d shop
```

Вы попадёте в консоль `psql`. Выйти: `\q`.

Разовый запрос без консоли:

```bash
docker exec pg psql -U postgres -d shop -c "SELECT version();"
```

Версия в ответе будет `PostgreSQL 17.x`.

**Способ 2. С вашего компьютера.** Нужен установленный клиент `psql` или DBeaver, DataGrip. Адрес — `localhost` и порт, который вы открыли:

```bash
PGPASSWORD=secret psql -h 127.0.0.1 -p 5432 -U postgres -d shop -c "SELECT 1"
```

```
 ?column? 
----------
        1
(1 row)
```

Для DBeaver и других клиентов: host `localhost`, port `5432`, database `shop`, user `postgres`, password `secret`.

Таблиц в базе пока нет. Данные мы загрузим в уроке про [Docker Compose](/practice/docker/compose-stack/).

## Практика

В конце удалите свои контейнеры: `docker rm -f pg`.

### Задание 1

Запустите nginx на порту `8080` компьютера. Если 8080 занят, возьмите 8090. Проверьте через `curl`, что страница открывается. Затем удалите контейнер.

**Проверка:** `curl` печатает HTML с `<title>Welcome to nginx!</title>`.

<details>
<summary>Решение</summary>

```bash
docker run -d --name web -p 8080:80 nginx:1.29
curl -s localhost:8080 | grep title
docker rm -f web
```

</details>

### Задание 2

Запустите Postgres так: имя контейнера `pg`, база `shop`, пароль `secret`, порт `5432` только для вашего компьютера. Проверьте, что контейнер работает и какой порт открыт.

**Проверка:** в `docker ps` в столбце `PORTS` стоит `127.0.0.1:5432->5432/tcp`.

<details>
<summary>Решение</summary>

```bash
docker run -d --name pg \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=shop \
  -p 127.0.0.1:5432:5432 \
  postgres:17
docker ps --filter name=pg
```

Если порт 5432 занят (например, у вас уже стоит Postgres), используйте `-p 127.0.0.1:5433:5432`.

</details>

### Задание 3

Не заходя в консоль, спросите у Postgres в контейнере, как называется текущая база.

**Проверка:** ответ `shop`.

<details>
<summary>Решение</summary>

```bash
docker exec pg psql -U postgres -d shop -tc "SELECT current_database();"
```

Флаг `-t` убирает заголовок таблицы. В ответе будет пробел перед `shop`. Это нормально.

</details>

### Задание 4

Посмотрите, какие переменные `POSTGRES_*` видит контейнер `pg`.

**Проверка:**

```
POSTGRES_PASSWORD=secret
POSTGRES_DB=shop
```

<details>
<summary>Решение</summary>

```bash
docker exec pg env | grep POSTGRES
```

Так видно, что `-e` кладёт переменную прямо в окружение контейнера. Заметьте: пароль виден любому, кто может сделать `docker exec`.

</details>

### Задание 5

Запустите второй контейнер на том же порту компьютера (`-p 127.0.0.1:5432:5432`) и прочитайте ошибку.

**Проверка:** в ошибке есть `Bind for 127.0.0.1:5432 failed: port is already allocated`.

<details>
<summary>Решение</summary>

```bash
docker run -d --name pg2 -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=x postgres:17
```

Docker создаёт контейнер, но не может его запустить. Удалите его: `docker rm -f pg2`.

</details>

Дальше: [Тома](/practice/docker/volumes/).
