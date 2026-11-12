---
title: Сети
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Сети Docker: как контейнеры находят друг друга | Инжиниринг Данных"
description: "Как контейнеры Docker общаются между собой: сети bridge, имена контейнеров вместо IP, ловушка localhost и разница между портом хоста и портом контейнера."
sidebar:
  order: 10
tags:
  - docker
  - practice
---

Контейнеры общаются по сети. Чтобы пайплайн нашёл базу, нужна общая сеть и имя базы. Это самая частая причина ошибки «Connection refused».

## Главное правило

**Внутри контейнера `localhost` — это сам контейнер.** Не ваш ноутбук и не соседний контейнер.

Если скрипт в контейнере `loader` ходит на `localhost:5432`, он ищет Postgres внутри `loader`. Там его нет.

## Сеть с именами

Docker умеет создавать виртуальные сети. Контейнеры в одной сети видят друг друга **по имени**.

```bash
docker network create shop-net
docker network ls --filter name=shop-net
```

Ответ:

```
NETWORK ID     NAME       DRIVER    SCOPE
66a43eab964e   shop-net   bridge    local
```

Две сети — два разных поведения:

| Сеть | Имена контейнеров работают? |
|---|---|
| `bridge` (по умолчанию) | Нет |
| Своя сеть (`docker network create`) | Да. Docker сам отвечает на запрос имени |

Compose создаёт свою сеть автоматически. Поэтому в Compose имена работают без настройки. Об этом — в [следующем уроке](/practice/docker/compose/).

## Демо: база и загрузчик

Нужна папка `~/docker-practice` и `Dockerfile` из урока [Хороший образ](/practice/docker/build-better/) (раздел «Итоговый Dockerfile»). Если вы его пропустили, создайте файл по этому уроку.

Соберите образ:

```bash
cd ~/docker-practice
docker build -t orders-app:1.0 .
```

Запустите Postgres в сети `shop-net`. Имя контейнера — `db`:

```bash
docker run -d --name db --network shop-net \
  -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=shop \
  postgres:17
```

Подождите 5–6 секунд, пока база стартует. Проверьте, что имя `db` работает:

```bash
docker run --rm --network shop-net alpine:3.22 ping -c 1 db
```

Ответ:

```
PING db (172.25.0.2): 56 data bytes
64 bytes from 172.25.0.2: seq=0 ttl=64 time=0.064 ms
```

IP-адрес у вас будет другой. Он нам не нужен: мы пользуемся именем.

Для сравнения запустите тот же `ping` без `--network`:

```bash
docker run --rm alpine:3.22 ping -c 1 db
```

Ответ:

```
ping: bad address 'db'
```

В сети `bridge` по умолчанию имена не работают.

## Ловушка localhost

Запустите загрузчик без `DB_HOST`. Скрипт `load_orders.py` берёт `localhost` по умолчанию:

```bash
docker run --rm --network shop-net \
  -e DB_PASSWORD=secret \
  -v "$PWD/data:/data:ro" \
  orders-app:1.0 python load_orders.py
```

Ошибка:

```
connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
```

Postgres работает. Но скрипт ищет его в своём контейнере. Теперь укажите имя контейнера базы:

```bash
docker run --rm --network shop-net \
  -e DB_HOST=db -e DB_PASSWORD=secret \
  -v "$PWD/data:/data:ro" \
  orders-app:1.0 python load_orders.py
```

Ответ:

```
Загружено строк: 500
```

Здесь `python load_orders.py` после имени образа **заменяет** `CMD` из `Dockerfile`. Образ тот же, команда другая.

Проверьте данные в базе:

```bash
docker exec db psql -U postgres -d shop -c \
  "SELECT channel, sum(amount) AS revenue FROM orders WHERE status='completed' GROUP BY channel ORDER BY 2 DESC"
```

Ответ:

```
 channel | revenue  
---------+----------
 organic | 23715.82
 ads     | 23082.74
 email   | 15459.67
(3 rows)
```

## Два порта: хоста и контейнера

В уроке про [порты](/practice/docker/ports-env/) мы писали `-p 127.0.0.1:5432:5432`. Этот ключ нужен только для доступа **с вашего компьютера**: из DBeaver, `psql` на ноутбуке, браузера.

| Кто подключается | Куда | Нужен `-p`? |
|---|---|---|
| Ваш ноутбук | `localhost:5432` | Да |
| Другой контейнер в той же сети | `db:5432` | **Нет** |

Контейнеры общаются по **внутреннему** порту. Если вы запустили `-p 5433:5432`, снаружи база на `5433`, а контейнеры всё равно ходят на `db:5432`.

Контейнеру `db` в нашем демо мы не открывали ни одного порта. Загрузчик всё равно до него дошёл.

## Полезные команды

```bash
docker network ls                    # список сетей
docker network inspect shop-net      # кто подключён, какие адреса
docker network rm shop-net           # удалить сеть (контейнеры должны быть остановлены)
docker run --network shop-net ...    # запустить контейнер в сети
```

Покажем, кто сидит в сети:

```bash
docker network inspect shop-net --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```

Ответ:

```
db 172.25.0.2/16
```

:::caution
Не пишите IP-адрес контейнера в настройках. При перезапуске он может измениться. Используйте имя.
:::

## Практика

Если контейнер `db` и сеть `shop-net` ещё есть, используйте их. Иначе повторите команды выше.

### Задание 1

Подключитесь к базе из **второго контейнера** `postgres:17`. Используйте `psql` и имя `db`. Сколько строк в таблице `orders`?

Подсказка: пароль передаётся переменной `PGPASSWORD`.

**Проверка:** 500.

<details>
<summary>Решение</summary>

```bash
docker run --rm --network shop-net -e PGPASSWORD=secret \
  postgres:17 psql -h db -U postgres -d shop -tc "select count(*) from orders"
```

`-h db` — имя контейнера базы. Порт не нужен: по умолчанию `5432`.

</details>

### Задание 2

Покажите, что имя `db` не работает вне своей сети. Запустите `ping -c 1 db` в контейнере `alpine:3.22` без `--network`.

**Проверка:** ответ `ping: bad address 'db'`.

<details>
<summary>Решение</summary>

```bash
docker run --rm alpine:3.22 ping -c 1 db
```

Без `--network` контейнер попадает в сеть `bridge`. Там нет имён.

</details>

### Задание 3

Запустите загрузчик с неверным именем базы: `DB_HOST=database`. Что получилось?

**Проверка:** последняя строка ошибки: `failed to resolve host 'database': [Errno -2] Name or service not known`.

<details>
<summary>Решение</summary>

```bash
docker run --rm --network shop-net \
  -e DB_HOST=database -e DB_PASSWORD=secret \
  -v "$PWD/data:/data:ro" \
  orders-app:1.0 python load_orders.py
```

Это другая ошибка, чем «Connection refused». «Refused» — имя нашлось, но там никто не слушает. «Name not known» — имени нет в сети.

</details>

### Задание 4

Остановите и удалите контейнер `db` и сеть `shop-net`.

**Проверка:** `docker network ls` не показывает `shop-net`.

<details>
<summary>Решение</summary>

```bash
docker rm -f db
docker network rm shop-net
```

Сеть нельзя удалить, пока в ней есть контейнеры.

</details>

Дальше: [Docker Compose](/practice/docker/compose/).
