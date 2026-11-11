---
title: "Свой образ: Dockerfile"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Dockerfile: как собрать образ для Python-скрипта | Инжиниринг Данных"
description: "Как написать Dockerfile, собрать образ командой docker build и запустить Python-скрипт в контейнере. FROM, COPY, RUN, CMD и ENTRYPOINT с примерами."
sidebar:
  order: 8
tags:
  - docker
  - practice
---

**Dockerfile** — это текстовый файл с рецептом образа. Каждая строка — один шаг. Командой `docker build` Docker читает рецепт и собирает образ.

Так вы упаковываете свой скрипт или пайплайн, чтобы он работал одинаково на любом компьютере.

## Инструкции

| Инструкция | Что делает |
|---|---|
| `FROM` | Берёт готовый образ за основу. Всегда первая строка |
| `WORKDIR` | Задаёт рабочую папку в образе. Если её нет, создаёт |
| `COPY` | Копирует файлы с вашего компьютера в образ |
| `RUN` | Выполняет команду **при сборке** (например, `pip install`) |
| `ENV` | Задаёт переменную окружения |
| `CMD` | Команда, которая запускается **при старте контейнера** |
| `ENTRYPOINT` | Программа, которая запускается при старте. `CMD` становится её аргументами |

`RUN` работает один раз, при сборке. `CMD` работает каждый раз, когда вы запускаете контейнер.

## Первый образ

Учебный скрипт `app/report.py` читает `orders.csv` и печатает выручку по каналам. Ему нужен только Python. Упакуем его.

Перейдите в папку курса и создайте файл `Dockerfile`:

```bash
cd ~/docker-practice
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY app/ .
CMD ["python", "report.py"]
```

Что здесь происходит:

1. Берём `python:3.12-slim`. В нём уже есть Python.
2. Рабочая папка в образе — `/app`.
3. Копируем всё из папки `app/` с вашего компьютера в `/app`.
4. При старте запускаем `python report.py`.

Соберите образ:

```bash
docker build -t orders-report:1.0 .
```

- `-t orders-report:1.0` — имя и тег образа.
- Точка `.` в конце — **контекст сборки**. Это папка, из которой `COPY` берёт файлы. Точка — текущая папка.

В конце вы увидите:

```
 => naming to docker.io/library/orders-report:1.0
```

Проверьте:

```bash
docker images orders-report
```

```
REPOSITORY       TAG   IMAGE ID       CREATED          SIZE
orders-report    1.0   57062938303c   ...              145MB
```

## Запуск и данные

Запустите образ и подключите данные через bind mount (урок про [тома](/practice/docker/volumes/)):

```bash
docker run --rm -v "$PWD/data:/data" orders-report:1.0
```

```
Файл: /data/orders.csv
Заказов: 500
Выручка по каналам (только completed):
  organic    23715.82
  ads        23082.74
  email      15459.67
```

Мы не положили `orders.csv` в образ. Данные меняются, а образ — это программа. Данные подключают снаружи.

### Что будет без данных

Запустите без `-v`:

```bash
docker run --rm orders-report:1.0
```

```
  File "/app/report.py", line 11, in <module>
    with open(path, newline="") as f:
         ^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/data/orders.csv'
```

Скрипт ищет `/data/orders.csv`, а в контейнере такой папки нет. Это ошибка в запуске, а не в образе.

Путь к файлу скрипт берёт из переменной `ORDERS_PATH`. Её можно поменять без пересборки:

```bash
docker run --rm -v "$PWD/data:/mnt" -e ORDERS_PATH=/mnt/orders.csv orders-report:1.0
```

Первая строка ответа теперь `Файл: /mnt/orders.csv`.

Хотите задать путь по умолчанию в образе? Добавьте в `Dockerfile` строку `ENV ORDERS_PATH=/data/orders.csv`. Флаг `-e` при запуске всё равно её перекроет.

## CMD и ENTRYPOINT

`CMD` — команда по умолчанию. Её легко заменить при запуске:

```bash
docker run --rm orders-report:1.0 python --version
```

```
Python 3.12.16
```

Всё, что вы пишете после имени образа, заменяет `CMD`. Версия Python у вас может быть другой.

```bash
docker run --rm orders-report:1.0 ls
```

```
load_orders.py
report.py
requirements.txt
```

Так видно, что `WORKDIR /app` работает: `ls` показывает файлы в `/app`. Здесь же лежит `load_orders.py`. Мы запустим его позже, в Compose.

`ENTRYPOINT` — программа, которая запускается всегда. То, что вы пишете после имени образа, превращается в её аргументы.

```dockerfile
ENTRYPOINT ["python"]
CMD ["report.py"]
```

| Команда | Что запустится |
|---|---|
| `docker run образ` | `python report.py` |
| `docker run образ --version` | `python --version` |
| `docker run образ other.py` | `python other.py` |

Так устроены образы-инструменты: `dbt`, `aws`, `terraform`. Образ — это сама программа, вы передаёте ей аргументы. Для обычного приложения хватает `CMD`.

## Форма exec и форма shell

Команду пишут двумя способами:

| Форма | Пример | Когда |
|---|---|---|
| exec | `CMD ["python", "report.py"]` | **Всегда по умолчанию.** Программа получает сигналы (`docker stop`) напрямую |
| shell | `CMD python report.py` | Docker запускает `/bin/sh -c`. Сигнал получает shell, а не ваша программа |

С формой shell `docker stop` может ждать 10 секунд и убить программу принудительно. Пишите форму exec: квадратные скобки и двойные кавычки.

## Слои и history

Каждая инструкция делает **слой** образа. Посмотрите их:

```bash
docker history orders-report:1.0
```

```
CREATED BY                                      SIZE
CMD ["python" "report.py"]                      0B
COPY app/ . # buildkit                          1.9kB
WORKDIR /app                                    0B
CMD ["python3"]                                 0B
...
```

Ваши три слоя — сверху. Ниже идут слои базового образа Python. Наш код весит 1.9 КБ. Остальные 145 МБ — это Python.

Слои кэшируются. Как этим пользоваться — в следующем уроке.

## Практика

Работайте в папке `~/docker-practice`.

### Задание 1

Создайте `Dockerfile` для `report.py`, как выше. Соберите образ `orders-report:1.0`. Запустите его с данными.

**Проверка:**

```
Файл: /data/orders.csv
Заказов: 500
Выручка по каналам (только completed):
  organic    23715.82
  ads        23082.74
  email      15459.67
```

<details>
<summary>Решение</summary>

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY app/ .
CMD ["python", "report.py"]
```

```bash
docker build -t orders-report:1.0 .
docker run --rm -v "$PWD/data:/data" orders-report:1.0
```

</details>

### Задание 2

Запустите образ без `-v`. Прочитайте ошибку. Исправьте запуск, не меняя образ.

**Проверка:** сначала `FileNotFoundError ... '/data/orders.csv'`. После исправления — отчёт.

<details>
<summary>Решение</summary>

Добавьте `-v "$PWD/data:/data"`. Образ менять не нужно: он не содержит данных.

</details>

### Задание 3

Запустите образ, но вместо отчёта выведите версию Python.

**Проверка:** `Python 3.12.x`.

<details>
<summary>Решение</summary>

```bash
docker run --rm orders-report:1.0 python --version
```

</details>

### Задание 4

Соберите образ с тегом `orders-report:2.0`, у которого `ORDERS_PATH` по умолчанию равен `/data/orders.csv`, добавив `ENV`. Проверьте, какие переменные заданы в образе.

**Проверка:** в списке `Env` есть `ORDERS_PATH=/data/orders.csv`.

<details>
<summary>Решение</summary>

Добавьте строку `ENV ORDERS_PATH=/data/orders.csv` после `FROM`. Затем:

```bash
docker build -t orders-report:2.0 .
docker image inspect orders-report:2.0 --format '{{.Config.Env}}'
```

В выводе будет и `PATH`, и другие переменные базового образа. Найдите нужную.

</details>

### Задание 5

Сколько строк в `docker history` создали вы сами, а сколько пришло из `python:3.12-slim`? Какие ваши слои весят 0B?

**Проверка:** ваших слоёв три: `WORKDIR`, `COPY`, `CMD`. `WORKDIR` и `CMD` весят 0B.

<details>
<summary>Решение</summary>

```bash
docker history orders-report:1.0
```

Строка `CMD ["python3"]` и всё ниже пришло из базового образа.

</details>

Дальше: [Хороший образ](/practice/docker/build-better/).
