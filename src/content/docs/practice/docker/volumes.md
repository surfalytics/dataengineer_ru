---
title: "Тома и bind mount"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker volumes: как сохранить данные Postgres | Инжиниринг Данных"
description: "Почему данные пропадают вместе с контейнером Docker, чем том отличается от bind mount, как сохранить базу Postgres и подключить папку с файлами."
sidebar:
  order: 7
tags:
  - docker
  - practice
---

**Файлы внутри контейнера временные.** Удалили контейнер — исчезли и файлы. Для баз данных и для файлов с данными нужны **тома**.

## Потеря данных: смотрим сами

Запустим Postgres без тома, создадим таблицу и удалим контейнер.

```bash
docker run -d --name pg1 -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=shop postgres:17
sleep 5
docker exec pg1 psql -U postgres -d shop -c "CREATE TABLE t(x int); INSERT INTO t VALUES (1),(2),(3);"
```

```
CREATE TABLE
INSERT 0 3
```

Запишите имя тома первого контейнера. Оно понадобится для уборки в конце:

```bash
docker inspect pg1 --format '{{range .Mounts}}{{.Name}}{{end}}'
```

Ответ — длинная строка из букв и цифр. Это имя тома.

Удалим контейнер и запустим новый с теми же настройками:

```bash
docker rm -f pg1
docker run -d --name pg2 -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=shop postgres:17
sleep 5
docker exec pg2 psql -U postgres -d shop -c "SELECT count(*) FROM t;"
```

```
ERROR:  relation "t" does not exist
LINE 1: SELECT count(*) FROM t;
                             ^
```

Таблицы нет. База новая и пустая.

Почему так? Образ `postgres` сам создаёт анонимный том для папки `/var/lib/postgresql/data`. Это видно в `docker inspect`:

```bash
docker inspect pg2 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}'
```

```
volume 60339739465d7ecb35d3abd... -> /var/lib/postgresql/data
```

Старые данные остались в первом анонимном томе. Но у нового контейнера свой новый том. Вернуться к старому без имени сложно. Для работы нужен **том с именем**.

Уберите за собой:

```bash
docker rm -fv pg2
```

Флаг `-v` удаляет вместе с контейнером его анонимный том. Том первого контейнера `pg1` остался. Его имя вы записали в начале урока. Удалите его по имени: `docker volume rm <имя>`. Не трогайте другие тома: на вашем компьютере могут быть данные других проектов.

## Два вида монтирования

| | Именованный том (volume) | Bind mount |
|---|---|---|
| Что это | Папка, которой управляет Docker | Папка с вашего компьютера |
| Запись | `-v pgdata:/var/lib/postgresql/data` | `-v "$PWD/data:/data"` |
| Где лежит | Внутри Docker. Путь вам не нужен | В вашей папке. Вы видите файлы |
| Для чего | Данные баз, состояние программ | Исходные файлы, код, конфиги |

Простое правило:

- **База данных** — именованный том.
- **Ваши файлы, которые вы открываете и правите** — bind mount.

Формат всегда один: `-v ОТКУДА:КУДА`. Если слева имя без слэша, это том. Если слева путь, это bind mount.

## Именованный том для Postgres

```bash
docker volume create pgdata
```

Запустите Postgres с этим томом:

```bash
docker run -d --name pg \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data \
  postgres:17
```

Создайте таблицу, удалите контейнер и запустите новый с тем же томом:

```bash
sleep 5
docker exec pg psql -U postgres -d shop -c "CREATE TABLE t(x int); INSERT INTO t VALUES (1),(2),(3);"
docker rm -f pg
docker run -d --name pg \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data \
  postgres:17
sleep 5
docker exec pg psql -U postgres -d shop -c "SELECT count(*) FROM t;"
```

```
 count 
-------
     3
(1 row)
```

Данные пережили удаление контейнера. Логи нового контейнера скажут: `Database directory appears to contain a database; Skipping initialization`. Значит, Postgres нашёл старую базу.

Переменные `POSTGRES_PASSWORD` и `POSTGRES_DB` работают **только при первом старте** с пустым томом. Если том уже с базой, они игнорируются.

:::caution
Путь `/var/lib/postgresql/data` верен для `postgres:17`. В более новых мажорных версиях образа путь к данным менялся. Когда переходите на новую мажорную версию, читайте описание образа на Docker Hub. И не запускайте новую версию на старом томе: данные версий несовместимы.
:::

## Команды для томов

```bash
docker volume ls                   # список томов
docker volume inspect pgdata       # подробности
docker volume rm pgdata            # удалить том (после удаления контейнера)
```

```bash
docker volume ls --filter name=pgdata
```

```
DRIVER    VOLUME NAME
local     pgdata
```

Том нельзя удалить, пока его использует контейнер. **Удаление тома стирает данные навсегда.**

## Bind mount: папка с вашего компьютера

Покажем на nginx. Создайте папку с одной страницей:

```bash
mkdir -p site
echo "<h1>Привет, Docker</h1>" > site/index.html
```

Подключите её в контейнер:

```bash
docker run -d --name web -p 8080:80 -v "$PWD/site:/usr/share/nginx/html:ro" nginx:1.29
curl -s localhost:8080
```

```
<h1>Привет, Docker</h1>
```

Теперь измените файл на своём компьютере. Контейнер перезапускать не надо:

```bash
echo "<h1>Версия 2</h1>" > site/index.html
curl -s localhost:8080
```

```
<h1>Версия 2</h1>
```

Контейнер видит те же файлы, что и вы. Так удобно разрабатывать: правите код в редакторе, контейнер сразу работает с новой версией.

Если порт 8080 занят, возьмите другой, например `-p 8090:80`.

### Только чтение: :ro

Суффикс `:ro` значит read-only. Контейнер может читать, но не может писать:

```bash
docker exec web sh -c 'echo x > /usr/share/nginx/html/new.html'
```

```
sh: 1: cannot create /usr/share/nginx/html/new.html: Read-only file system
```

Подключайте исходные данные с `:ro`. Так ошибка в программе не испортит ваш CSV.

Путь слева в bind mount должен быть **абсолютным**. Поэтому пишем `"$PWD/site"`, а не `./site`. Кавычки нужны, если в пути есть пробелы.

Удалите контейнер: `docker rm -f web`.

## Резервная копия тома

Том можно сохранить в архив с помощью временного контейнера. Он читает том и пишет архив в вашу папку:

```bash
docker stop pg
docker run --rm -v pgdata:/src:ro -v "$PWD:/backup" alpine:3.22 \
  tar czf /backup/pgdata.tar.gz -C /src .
docker start pg
```

Это копия файлов базы. Делайте её, только когда Postgres **остановлен**. Поэтому первая команда — `docker stop`. Для работающей базы лучше `pg_dump`: `docker exec pg pg_dump -U postgres shop > shop.sql`.

## Практика

Работайте в папке `~/docker-practice`. Если файлов ещё нет, скачайте их в уроке [Установка](/practice/docker/setup/).

### Задание 1

Сначала удалите контейнер и том из примеров выше: `docker rm -f pg && docker volume rm pgdata`.

Запустите Postgres `pg` с томом `pgdata`. Создайте таблицу `t` с тремя строками. Удалите контейнер. Запустите новый с тем же томом и посчитайте строки.

**Проверка:** `count` равен `3`.

<details>
<summary>Решение</summary>

Команды — в разделе «Именованный том для Postgres» выше. Главное: оба раза один и тот же флаг `-v pgdata:/var/lib/postgresql/data`.

</details>

### Задание 2

Не запуская новый контейнер, покажите, что том `pgdata` существует. Потом попробуйте удалить его, пока контейнер `pg` ещё жив. Что ответит Docker?

**Проверка:** ошибка вида `volume is in use`.

<details>
<summary>Решение</summary>

```bash
docker volume ls --filter name=pgdata
docker volume rm pgdata
```

Том занят контейнером `pg`. Сначала `docker rm -f pg`, потом `docker volume rm pgdata`.

</details>

### Задание 3

Запустите `app/report.py` без своего образа. Возьмите `python:3.12-slim` и подключите папку курса через bind mount. Данные — `data/orders.csv`.

**Проверка:** в ответе `Заказов: 500` и выручка: organic 23715.82, ads 23082.74, email 15459.67.

<details>
<summary>Решение</summary>

```bash
docker run --rm -v "$PWD:/work" -w /work \
  -e ORDERS_PATH=/work/data/orders.csv \
  python:3.12-slim python app/report.py
```

- `-v "$PWD:/work"` подключает всю папку курса.
- `-w /work` делает её рабочей папкой в контейнере.
- `-e ORDERS_PATH=...` говорит скрипту, где искать CSV.

Так запускают скрипт без своего образа. Это удобно для проверки на скорую руку.

</details>

### Задание 4

Подключите `data` с флагом `:ro` и попробуйте записать в неё файл из контейнера.

**Проверка:** ошибка `Read-only file system`.

<details>
<summary>Решение</summary>

```bash
docker run --rm -v "$PWD/data:/data:ro" alpine:3.22 sh -c 'echo x > /data/test.txt'
```

</details>

### Задание 5

Удалите всё, что создали: контейнеры `pg`, `web` и том `pgdata`.

**Проверка:** `docker volume ls --filter name=pgdata` не показывает строк, кроме заголовка.

<details>
<summary>Решение</summary>

```bash
docker rm -f pg web
docker volume rm pgdata
```

Если контейнера `web` уже нет, Docker просто скажет об этом. Это не страшно.

</details>

Дальше: [Свой образ: Dockerfile](/practice/docker/dockerfile/).
