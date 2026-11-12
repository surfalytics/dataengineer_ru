---
title: Docker Compose
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker Compose: Postgres и Adminer одной командой | Инжиниринг Данных"
description: "Что такое Docker Compose и зачем он нужен. Файл compose.yaml, команды up, down, logs, exec. Запускаем Postgres и Adminer и сохраняем данные в томе."
sidebar:
  order: 11
tags:
  - docker
  - practice
---

**Docker Compose** запускает несколько контейнеров по одному файлу. Вместо длинных `docker run` вы пишете `compose.yaml` и запускаете всё командой `docker compose up`.

## Зачем Compose

Вспомните запуск Postgres из прошлых уроков:

```bash
docker run -d --name db --network shop-net \
  -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data -p 127.0.0.1:5432:5432 \
  postgres:17
```

Это одна служба. В реальной работе их три-пять: база, загрузчик, BI. Команды длинные, их легко забыть или ошибиться.

Compose решает три задачи:

- **Всё в одном файле.** Его можно хранить в Git и показать коллеге.
- **Сеть создаётся сама.** Службы видят друг друга по имени.
- **Одна команда на всё:** `up` запускает, `down` останавливает.

:::note
Команда называется `docker compose` (через пробел). Старая `docker-compose` (через дефис) — прошлая версия. Файл называйте `compose.yaml`. Ключ `version:` в начале больше не нужен.
:::

## Первый compose.yaml

В папке `~/docker-practice` создайте файл `compose.yaml`:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: shop
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  adminer:
    image: adminer:5
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  pgdata:
```

**Adminer** — лёгкий веб-интерфейс для баз данных. Он нужен, чтобы посмотреть таблицы в браузере.

Как читать файл:

| Ключ | Что значит | Аналог в `docker run` |
|---|---|---|
| `services:` | Список контейнеров. `db` и `adminer` — имена служб | — |
| `image:` | Какой образ взять | имя образа |
| `environment:` | Переменные окружения | `-e` |
| `ports:` | Порты: `хост:контейнер` | `-p` |
| `volumes:` (внутри службы) | Куда подключить том | `-v` |
| `depends_on:` | Какую службу запустить раньше | — |
| `volumes:` (в конце файла) | Объявление именованных томов | `docker volume create` |

Имя службы — это и имя в сети. Adminer найдёт базу по имени `db`.

Порты в кавычках: `"127.0.0.1:5432:5432"`. `127.0.0.1` открывает базу только для вашего компьютера, как в уроке [Порты](/practice/docker/ports-env/). YAML может неверно прочитать число с двоеточием.

:::caution
Порт `8080` часто занят другими программами. Если Docker пишет `port is already allocated`, замените левое число: `"8081:8080"`. То же для `5432`, если у вас уже стоит Postgres: `"127.0.0.1:5433:5432"`.
:::

## Запуск

```bash
docker compose up -d
```

`-d` запускает в фоне. Compose создаст сеть, том и два контейнера:

```
 Container docker-practice-db-1 Started
 Container docker-practice-adminer-1 Started
```

Имя контейнера складывается так: **папка проекта** + служба + номер. Папка у нас `docker-practice`, поэтому `docker-practice-db-1`. Если папка называется иначе, имена будут другими.

Посмотрите состояние:

```bash
docker compose ps
```

```
NAME                        IMAGE         SERVICE   STATUS         PORTS
docker-practice-adminer-1   adminer:5     adminer   Up 4 seconds   0.0.0.0:8080->8080/tcp
docker-practice-db-1        postgres:17   db        Up 4 seconds   127.0.0.1:5432->5432/tcp
```

Колонки `CREATED` и `COMMAND` мы убрали, чтобы строки были короче.

Откройте в браузере <http://localhost:8080>. Войдите так:

| Поле | Значение |
|---|---|
| System | PostgreSQL |
| Server | `db` |
| Username | `postgres` |
| Password | `secret` |
| Database | `shop` |

В поле Server пишем `db`, а не `localhost`. Adminer работает в контейнере и ходит к базе по имени службы. Подробно — в уроке про [сети](/practice/docker/networks/).

## Главные команды

```bash
docker compose up -d          # создать и запустить всё
docker compose ps             # запущенные службы
docker compose ps -a          # все службы, в том числе завершённые
docker compose logs -f db     # логи службы db (Ctrl+C — выйти)
docker compose exec db psql -U postgres -d shop   # команда внутри работающей службы
docker compose stop           # остановить, ничего не удаляя
docker compose start          # запустить остановленное
docker compose restart db     # перезапустить одну службу
docker compose down           # остановить и удалить контейнеры и сеть
docker compose down -v        # то же + удалить тома (данные!)
```

Команды `docker compose` читают `compose.yaml` в **текущей папке**. Запускайте их из `~/docker-practice`.

Почему `ps` и `ps -a`: `ps` показывает только работающие. Служба, которая выполнила задачу и вышла (например, загрузчик данных), в `ps` не видна. В `ps -a` она есть со статусом `Exited (0)`. Ноль значит «без ошибок».

## down и данные

Создайте таблицу в базе:

```bash
docker compose exec db psql -U postgres -d shop -c "CREATE TABLE t(x int); INSERT INTO t VALUES (1);"
```

Остановите и удалите контейнеры:

```bash
docker compose down
docker volume ls | grep pgdata
```

```
local     docker-practice_pgdata
```

Контейнеров нет, а том остался. Запустите снова и проверьте таблицу:

```bash
docker compose up -d
docker compose exec db psql -U postgres -d shop -tc "select count(*) from t"
```

```
     1
```

Данные на месте. Теперь удалите всё вместе с томом:

```bash
docker compose down -v
docker volume ls | grep pgdata
```

Вывода нет: том удалён, вместе с ним все данные.

:::danger
`docker compose down -v` удаляет данные базы без вопросов. Перед `-v` убедитесь, что данные не нужны.
:::

## Практика

Работайте в `~/docker-practice` с файлом `compose.yaml` из урока.

### Задание 1

Запустите стек. Откройте Adminer и войдите в базу `shop`. Сколько в ней таблиц?

**Проверка:** 0. База пустая: загрузчик мы ещё не запускали.

<details>
<summary>Решение</summary>

```bash
docker compose up -d
```

Откройте <http://localhost:8080> и войдите с данными из таблицы выше. Если порт занят, поменяйте его в `compose.yaml` и снова выполните `docker compose up -d`.

</details>

### Задание 2

Посмотрите последние 5 строк лога базы. Какая строка говорит, что база готова?

**Проверка:** в логе есть `database system is ready to accept connections`.

<details>
<summary>Решение</summary>

```bash
docker compose logs --tail 5 db
```

</details>

### Задание 3

Остановите стек командой `stop`. Покажите все службы со статусом. Потом запустите командой `start`.

**Проверка:** после `stop` команда `ps -a` показывает `Exited (0)` у обеих служб.

<details>
<summary>Решение</summary>

```bash
docker compose stop
docker compose ps -a
docker compose start
```

`stop` не удаляет контейнеры. Они остаются в списке `ps -a`.

</details>

### Задание 4

Докажите, что данные переживают `down`, но не `down -v`. Создайте таблицу `t`, выполните `down`, `up -d`, посчитайте строки. Потом выполните `down -v`, `up -d` и снова посмотрите таблицы.

**Проверка:** после `down` и `up` в таблице `t` одна строка. После `down -v` и `up` таблицы `t` нет: `relation "t" does not exist`.

<details>
<summary>Решение</summary>

```bash
docker compose exec db psql -U postgres -d shop -c "CREATE TABLE t(x int); INSERT INTO t VALUES (1);"
docker compose down
docker compose up -d
docker compose exec db psql -U postgres -d shop -tc "select count(*) from t"

docker compose down -v
docker compose up -d
docker compose exec db psql -U postgres -d shop -tc "select count(*) from t"
```

После `up` подождите 3–5 секунд, пока база стартует. В конце выполните `docker compose down`.

</details>

Дальше: [Compose для пайплайна](/practice/docker/compose-stack/).
