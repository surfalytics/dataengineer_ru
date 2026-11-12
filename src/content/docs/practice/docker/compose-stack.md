---
title: Compose для пайплайна
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker Compose для пайплайна: Postgres и dbt | Инжиниринг Данных"
description: "Собираем пайплайн в Docker Compose: build, healthcheck и depends_on, файл .env с паролем, profiles для dbt, команды run и config. Пример с Postgres и dbt."
sidebar:
  order: 12
tags:
  - docker
  - practice
---

Теперь соберём настоящий пайплайн: Postgres, загрузчик CSV и dbt. Для этого нужны пять приёмов Compose: `build`, `command`, `healthcheck`, `.env` и `profiles`.

## Цель

```
orders.csv → loader (Python) → Postgres → dbt → analytics.revenue_by_channel
                                  ↑
                               Adminer
```

- `loader` — наш образ. Он читает CSV и пишет в базу. Работает один раз и завершается.
- `db` — Postgres. Работает постоянно.
- `dbt` — запускаем вручную, когда нужно.

## Файлы

Работайте в `~/docker-practice`. Понадобятся файлы:

```
docker-practice/
├── app/                  # из учебного набора
├── data/orders.csv       # из учебного набора
├── Dockerfile            # образ загрузчика
├── compose.yaml
├── .env                  # пароль (не в Git)
├── .env.example          # пример без секрета (в Git)
├── .gitignore
└── dbt/
    ├── Dockerfile
    ├── dbt_project.yml
    ├── profiles.yml
    └── models/revenue_by_channel.sql
```

### Dockerfile

Это `Dockerfile` из урока «Хороший образ». Он собирает образ с `psycopg` и скриптами из `app/`:

```dockerfile
FROM python:3.12-slim

# Пользователь без прав root. Создаём его рано: этот слой почти не меняется
RUN useradd --create-home appuser

WORKDIR /app

# Сначала зависимости: слой берётся из кэша, пока requirements.txt не изменился
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом код: он меняется чаще
COPY app/ .

USER appuser

CMD ["python", "report.py"]
```

По умолчанию образ запускает `report.py`. Для загрузки мы заменим команду в Compose.

### Пароль в .env

Compose сам читает файл `.env` рядом с `compose.yaml`. Создайте его:

```bash
echo "DB_PASSWORD=secret" > .env
echo "DB_PASSWORD=change-me" > .env.example
printf '.env\ndbt/target/\ndbt/logs/\ndbt/.user.yml\n' > .gitignore
```

В `compose.yaml` пароль берётся так: `${DB_PASSWORD}`.

:::danger
Никогда не добавляйте `.env` в Git. Там пароли и ключи. В Git кладут `.env.example` с пустыми или фальшивыми значениями. Так коллега поймёт, какие переменные нужны.
:::

Проверьте, что подстановка работает:

```bash
docker compose config | grep POSTGRES_PASSWORD
```

```
      POSTGRES_PASSWORD: secret
```

`docker compose config` печатает итоговый файл после подстановки. Если переменной нет, Compose предупредит: `The "DB_PASSWORD" variable is not set. Defaulting to a blank string.` Это значит, что вы не создали `.env` или запустили команду не из той папки.

### compose.yaml

```yaml
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: shop
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U postgres -d shop"]
      interval: 5s
      timeout: 3s
      retries: 10

  loader:
    build: .
    command: ["python", "load_orders.py"]
    environment:
      DB_HOST: db
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data:/data:ro
    depends_on:
      db:
        condition: service_healthy

  adminer:
    image: adminer:5
    ports:
      - "8080:8080"
    depends_on:
      - db

  dbt:
    build: ./dbt
    profiles: ["tools"]
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      DBT_PROFILES_DIR: /project
    volumes:
      - ./dbt:/project
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

## Разбор

### build и command

`build: .` говорит: не скачивай образ, а собери его из `Dockerfile` в этой папке. `./dbt` — собрать из папки `dbt`.

`command:` заменяет `CMD` из образа. Один образ — две задачи: `report.py` по умолчанию и `load_orders.py` для загрузчика.

`./data:/data:ro` — папка с данными подключена только для чтения (`ro`).

### healthcheck и depends_on

Контейнер «запущен» ещё не значит «готов». Postgres стартует несколько секунд. Если загрузчик подключится раньше, он упадёт с `Connection refused`.

- `healthcheck` — команда, которая проверяет готовность. `pg_isready` отвечает «ок», когда база принимает подключения.
- `condition: service_healthy` — запускай `loader`, только когда `db` в статусе `healthy`.

Простой `depends_on: [db]` ждёт только запуска контейнера, не готовности. Для Adminer этого хватает: он сам повторяет попытки.

### profiles

Служба с `profiles: ["tools"]` **не запускается** командой `docker compose up`. Её запускают явно. Так dbt не стартует вместе с базой.

### restart

`restart: unless-stopped` у базы: Docker поднимет её после сбоя или перезагрузки компьютера. Остановленную вручную не тронет.

| Политика | Что делает |
|---|---|
| `no` (по умолчанию) | Не перезапускает |
| `on-failure` | Перезапускает, если код выхода не 0 |
| `unless-stopped` | Всегда, кроме ручной остановки |
| `always` | Всегда. Даже контейнер, остановленный вручную, запустится после перезапуска Docker |

Загрузчику политика не нужна: он должен выполниться один раз.

## Файлы dbt

`dbt/Dockerfile`:

```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir dbt-core==1.12.6 dbt-postgres==1.11.0
WORKDIR /project
ENTRYPOINT ["dbt"]
```

Версии закреплены специально. Если поставить только `dbt-postgres`, `pip` может взять тестовую версию `dbt-core`. Закрепляйте обе версии.

`ENTRYPOINT ["dbt"]` значит: всё, что вы напишете после имени службы, станет аргументами `dbt`. Команда `run` превратится в `dbt run`.

`dbt/dbt_project.yml`:

```yaml
name: shop
version: "1.0"
profile: shop
model-paths: ["models"]
```

`dbt/profiles.yml`:

```yaml
shop:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db
      port: 5432
      user: postgres
      password: "{{ env_var('DB_PASSWORD') }}"
      dbname: shop
      schema: analytics
      threads: 2
```

`host: db` — имя службы. Пароль dbt берёт из переменной окружения, а не из файла.

`dbt/models/revenue_by_channel.sql`:

```sql
select
    channel,
    count(*)    as orders,
    sum(amount) as revenue
from public.orders
where status = 'completed'
group by channel
```

## Запуск

```bash
docker compose up -d --build
```

`--build` пересобирает образы, если файлы изменились. Compose запустит `db` и `adminer`. Потом дождётся, когда `db` станет `healthy`, и только тогда запустит `loader`.

Подождите 2–3 секунды. Загрузчику нужно время, чтобы закончить работу.

Статус:

```bash
docker compose ps
```

```
NAME                        IMAGE         SERVICE   STATUS                   PORTS
docker-practice-adminer-1   adminer:5     adminer   Up 8 seconds             0.0.0.0:8080->8080/tcp
docker-practice-db-1        postgres:17   db        Up 8 seconds (healthy)   127.0.0.1:5432->5432/tcp
```

Загрузчика в списке нет: он уже завершился. Покажите все службы:

```bash
docker compose ps -a --format 'table {{.Service}}\t{{.Status}}'
```

```
SERVICE   STATUS
adminer   Up 8 seconds
db        Up 8 seconds (healthy)
loader    Exited (0) 2 seconds ago
```

Лог загрузчика:

```bash
docker compose logs loader
```

```
loader-1  | Загружено строк: 500
```

Запустите dbt. Первая сборка образа dbt занимает около минуты:

```bash
docker compose run --rm dbt run
```

В конце вывода:

```
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=1
```

dbt пишет служебные файлы в папку `dbt/` на вашем компьютере: `target/`, `logs/`, `.user.yml`. Мы уже добавили их в `.gitignore`.

:::note[Linux]
Контейнер dbt работает от root. На Linux эти файлы будут принадлежать root. Удалить их можно так: `sudo rm -rf dbt/target dbt/logs dbt/.user.yml`. На macOS и Windows такой проблемы нет.
:::

Посмотрите результат:

```bash
docker compose exec db psql -U postgres -d shop -c \
  "select channel, orders, revenue from analytics.revenue_by_channel order by 3 desc"
```

```
 channel | orders | revenue  
---------+--------+----------
 organic |    164 | 23715.82
 ads     |    158 | 23082.74
 email   |     96 | 15459.67
(3 rows)
```

`docker compose run --rm` запускает **одноразовый** контейнер службы и удаляет его после выхода. Так запускают задачи: загрузку, dbt, миграции.

## Если порт занят

Если на компьютере уже что-то слушает порт `8080`, вы увидите:

```
Error response from daemon: ... Bind for 0.0.0.0:8080 failed: port is already allocated
```

`db` при этом работает и здоров. Контейнер `adminer` остаётся в состоянии `Created` и не запущен. Исправление: поменять левое число в `ports:`, например `"8081:8080"`, и выполнить `docker compose up -d` ещё раз.

## Практика

### Задание 1

Поднимите стек. Сколько строк загрузил `loader`?

**Проверка:** `Загружено строк: 500`.

<details>
<summary>Решение</summary>

```bash
docker compose up -d --build
docker compose logs loader
```

</details>

### Задание 2

Уберите `condition: service_healthy` у `loader`, оставив `depends_on: [db]`. Выполните `docker compose down -v`, потом `up -d`. Что случилось с загрузчиком?

**Проверка:** `loader` в статусе `Exited (1)`. В логе: `connection failed: ... port 5432 failed: Connection refused`. На очень быстром компьютере база может успеть стартовать. Но на это нельзя рассчитывать.

<details>
<summary>Решение</summary>

В `compose.yaml`:

```yaml
    depends_on:
      - db
```

```bash
docker compose down -v
docker compose up -d
docker compose ps -a --format 'table {{.Service}}\t{{.Status}}'
docker compose logs loader
```

Верните `condition: service_healthy`. Только `healthcheck` гарантирует, что база готова.

</details>

### Задание 3

Запустите dbt и найдите в базе таблицу (view) `analytics.revenue_by_channel`.

**Проверка:** три строки, у `organic` 164 заказа и выручка 23715.82.

<details>
<summary>Решение</summary>

```bash
docker compose run --rm dbt run
docker compose exec db psql -U postgres -d shop -c "select * from analytics.revenue_by_channel order by 3 desc"
```

</details>

### Задание 4

Смените пароль: поменяйте `DB_PASSWORD` в `.env` на `newpass`. Выполните `docker compose down -v`, затем `up -d`. Проверьте, что загрузчик работает с новым паролем.

**Проверка:** `Загружено строк: 500`.

<details>
<summary>Решение</summary>

```bash
echo "DB_PASSWORD=newpass" > .env
docker compose down -v
docker compose up -d
docker compose logs loader
```

В конце верните `DB_PASSWORD=secret` в `.env` и снова выполните `docker compose down -v` и `docker compose up -d`.

Нужен `-v`: Postgres задаёт пароль только при **первом** создании базы. Старый том хранит старый пароль. Без `-v` загрузчик упадёт с ошибкой `password authentication failed for user "postgres"`.

</details>

### Задание 5

Добавьте новую строку в конец `data/orders.csv` и запустите загрузчик снова, не пересоздавая стек. Сколько строк в таблице `orders`?

**Проверка:** 501.

:::note[macOS]
Docker Desktop на macOS видит изменения файла с задержкой в 1–2 секунды. Если загрузчик показал старое число, подождите пару секунд и запустите его ещё раз.
:::

<details>
<summary>Решение</summary>

```bash
echo "1501,2024-04-01,5,email,99.00,completed" >> data/orders.csv
docker compose run --rm loader
docker compose exec db psql -U postgres -d shop -tc "select count(*) from orders"
```

Скрипт делает `TRUNCATE` и грузит файл заново, поэтому повторный запуск безопасен.

Верните файл в исходный вид. Эта команда удаляет последнюю строку и работает на macOS и Linux:

```bash
sed -i.bak '$d' data/orders.csv && rm data/orders.csv.bak
```

</details>

Остановите стек, когда закончите: `docker compose down`.

Дальше: [Open source за минуты](/practice/docker/use-cases/).
