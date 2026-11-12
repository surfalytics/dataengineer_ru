---
title: Итоговая практика
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Docker на практике: Postgres, загрузчик и Metabase | Инжиниринг Данных"
description: "Итог курса Docker: собираем мини-стек для аналитики в Docker Compose. Postgres, загрузчик CSV и BI-инструмент Metabase. Проверяем, что данные не теряются."
sidebar:
  order: 16
tags:
  - docker
  - practice
---

Соберём мини-стек для аналитики с нуля: база, загрузчик и BI-инструмент. Всё запускается одной командой и работает на вашем компьютере.

```
orders.csv → loader → Postgres → Metabase (дашборды в браузере)
                              ↘ Adminer (просмотр таблиц)
```

:::caution
Образ Metabase большой: скачивание около 1 ГБ. Первый запуск займёт несколько минут. Начните с хорошего интернета.
:::

На схеме — то, что мы построим. Одна сеть, четыре сервиса, два вида хранения данных.

![Схема стека: loader пишет заказы в Postgres, Metabase и Adminer читают из него, данные Postgres лежат в томе pgdata](/assets/practice/docker/compose-stack.png)

## Шаг 1. Папка проекта

Создайте новую папку и скопируйте в неё данные и скрипты из учебного набора:

```bash
mkdir ~/shop-stack
cd ~/shop-stack
cp -r ~/docker-practice/app ~/docker-practice/data .
ls
```

**Проверка:** `app  data`.

## Шаг 2. Файлы

`Dockerfile` (образ загрузчика):

```dockerfile
FROM python:3.12-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

USER appuser

CMD ["python", "report.py"]
```

`.env`:

```bash
echo "DB_PASSWORD=secret" > .env
echo "DB_PASSWORD=change-me" > .env.example
echo ".env" > .gitignore
```

`compose.yaml`:

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

  metabase:
    image: metabase/metabase:v0.65.4
    restart: unless-stopped
    environment:
      MB_DB_FILE: /metabase-data/metabase.db
    ports:
      - "3000:3000"
    volumes:
      - metabase-data:/metabase-data
    depends_on:
      db:
        condition: service_healthy

  adminer:
    image: adminer:5
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  pgdata:
  metabase-data:
```

Что здесь нового:

- `metabase` хранит свои настройки (пользователь, дашборды) в файле. `MB_DB_FILE` задаёт путь к файлу, а том `metabase-data` сохраняет его.
- Два тома: один для данных, второй для настроек BI.
- `adminer` — тот же веб-клиент базы, что в уроке [Docker Compose](/practice/docker/compose/). Удобно смотреть таблицы без Metabase.

Проверьте файл:

```bash
docker compose config -q && echo ok
```

**Проверка:** `ok`.

## Шаг 3. Запуск

Сначала остановите стек из прошлых уроков. Иначе порты `5432` и `8080` будут заняты:

```bash
cd ~/docker-practice && docker compose down
cd ~/shop-stack
```

Запустите новый стек:

```bash
docker compose up -d --build
```

Metabase стартует медленно. Следите за логом:

```bash
docker compose logs -f metabase
```

Выйти из лога: `Ctrl+C`. Проверьте готовность:

```bash
curl localhost:3000/api/health
```

**Проверка:** `{"status":"ok"}`. Пока Metabase запускается, ответ другой: `{"status":"initializing", ...}` или ошибка `curl: (52)` или `curl: (56)`. Подождите 1–2 минуты и повторите.

Проверьте, что загрузчик отработал:

```bash
docker compose logs loader
```

**Проверка:** `Загружено строк: 500`.

## Шаг 4. Metabase

Откройте <http://localhost:3000>.

1. Выберите язык **English**: так названия кнопок совпадут с уроком. Создайте администратора. Почта может быть любой. Пароль запомните.
2. Metabase предложит добавить данные. Выберите **PostgreSQL**. Если пропустили шаг, откройте Admin → Databases → Add database.
3. Заполните поля:

| Поле | Значение |
|---|---|
| Display name | `shop` |
| Host | `db` |
| Port | `5432` |
| Database name | `shop` |
| Username | `postgres` |
| Password | пароль из `.env` (`secret`) |

:::danger
В поле Host пишите `db`, **не** `localhost`. Metabase работает в контейнере. С `localhost` он ищет базу у себя и отвечает: `Hmm, we couldn't connect to the database. Make sure your Host and Port settings are correct.` Подробно: урок про [сети](/practice/docker/networks/).
:::

Нажмите Save. Metabase проверит подключение и прочитает таблицы.

## Шаг 5. Первый вопрос

1. Нажмите **New → SQL query** и выберите базу `shop`.
2. Вставьте запрос и запустите:

```sql
SELECT channel, round(sum(amount), 2) AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY channel
ORDER BY revenue DESC;
```

**Проверка:**

| channel | revenue |
|---|---|
| organic | 23715.82 |
| ads | 23082.74 |
| email | 15459.67 |

Эти цифры совпадают с `report.py` и dbt из прошлых уроков. Сохраните вопрос и выберите вид «Bar» (столбцы).

## Практика

### Задание 1

Остановите стек командой `down` и запустите снова. Войдите в Metabase. Остались ли ваш пользователь, подключение и сохранённый вопрос?

**Проверка:** да. Данные в Postgres тоже на месте: 500 строк.

<details>
<summary>Решение</summary>

Запускаем только `db` и `metabase`, без загрузчика. Иначе загрузчик заново зальёт 500 строк, и проверка ничего не докажет.

```bash
docker compose down
docker compose up -d --wait db metabase
curl localhost:3000/api/health
docker compose exec db psql -U postgres -d shop -tc "select count(*) from orders"
```

`down` удаляет контейнеры, но не тома. Всё состояние лежит в томах `pgdata` и `metabase-data`.

</details>

### Задание 2

Докажите, что `down -v` стирает данные. Выполните `docker compose down -v`. Запустите **только базу**: `docker compose up -d --wait db`. Посчитайте строки в `orders`.

**Проверка:** ошибка `relation "orders" does not exist`. Таблицы нет: том удалён.

<details>
<summary>Решение</summary>

```bash
docker compose down -v
docker compose up -d --wait db
docker compose exec db psql -U postgres -d shop -tc "select count(*) from orders"
```

`--wait` ждёт, пока база станет `healthy`. Без него `psql` может запуститься раньше базы и выдать другую ошибку.

Важно запустить только `db`. Если выполнить `up -d` без имени службы, загрузчик создаст таблицу заново, и вы не увидите потери. Metabase тоже начнёт с чистого листа: придётся снова создать администратора.

</details>

### Задание 3

Верните данные одной командой. Не запускайте `up` для всех служб: запустите только загрузчик.

**Проверка:** в `orders` снова 500 строк.

<details>
<summary>Решение</summary>

```bash
docker compose run --rm loader
docker compose exec db psql -U postgres -d shop -tc "select count(*) from orders"
```

`run` ждёт, пока загрузчик закончит. Compose сам запустит `db`, если она не работает (она нужна по `depends_on`), и дождётся `healthy`.

</details>

### Задание 4

Порт `3000` у вас занят? Или просто смените его: пусть Metabase открывается на порту `3001`. Что нужно изменить?

**Проверка:** Metabase отвечает на `localhost:3001`. Внутри сети ничего не меняется: подключение к базе остаётся `db:5432`.

<details>
<summary>Решение</summary>

В `compose.yaml` поменяйте левое число:

```yaml
    ports:
      - "3001:3000"
```

```bash
docker compose up -d metabase
curl localhost:3001/api/health
```

Левое число — порт на вашем компьютере. Правое — порт внутри контейнера. Его менять не надо.

</details>

### Задание 5

Добавьте в конец `data/orders.csv` новый заказ и загрузите файл ещё раз, не пересоздавая стек:

```
1501,2024-04-01,5,email,99.00,completed
```

Сколько строк теперь в `orders`? Какая выручка у `email`?

**Проверка:** 501 строка. Выручка `email`: 15558.67 (было 15459.67, плюс 99.00).

:::note[macOS]
Docker Desktop на macOS видит изменения файла с задержкой в 1–2 секунды. Если загрузчик показал старое число, подождите пару секунд и запустите его ещё раз.
:::

<details>
<summary>Решение</summary>

```bash
echo "1501,2024-04-01,5,email,99.00,completed" >> data/orders.csv
docker compose run --rm loader
docker compose exec db psql -U postgres -d shop -tc "select count(*) from orders"
docker compose exec db psql -U postgres -d shop -tc "select sum(amount) from orders where channel='email' and status='completed'"
```

В Metabase обновите вопрос: цифра изменилась. Затем удалите последнюю строку из файла и загрузите снова:

```bash
sed -i.bak '$d' data/orders.csv && rm data/orders.csv.bak
docker compose run --rm loader
```

</details>

### Задание 6 (по желанию)

Добавьте в стек службу `dbt` из урока [«Compose для пайплайна»](/practice/docker/compose-stack/). Запустите `docker compose run --rm dbt run`. В Metabase обновите список таблиц базы `shop` (Admin → Databases → Sync database schema). Появилась ли схема `analytics`?

**Проверка:** dbt пишет `PASS=1 WARN=0 ERROR=0`. В Metabase в схеме **Analytics** есть таблица **Revenue By Channel**. Metabase показывает имена так: с большой буквы и без `_`.

<details>
<summary>Решение</summary>

Скопируйте папку `dbt/` из прошлого урока:

```bash
cp -r ~/docker-practice/dbt .
printf 'dbt/target/\ndbt/logs/\ndbt/.user.yml\n' >> .gitignore
```

Вставьте службу в блок `services:` файла `compose.yaml`, перед строкой `volumes:`:

```yaml
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
```

```bash
docker compose run --rm dbt run
```

</details>

## Уборка

Остановить стек и **сохранить** данные:

```bash
docker compose down
```

Удалить всё, в том числе тома:

```bash
docker compose down -v
```

Удалить образы загрузчика и dbt, если они больше не нужны:

```bash
docker image ls
docker rmi shop-stack-loader shop-stack-dbt
```

Имя образа — `<папка>-<служба>`. Проверьте его в списке `docker image ls`.

:::caution
Не используйте `docker system prune`, пока не поняли, что он удалит. Он стирает все остановленные контейнеры, неиспользуемые сети, висячие образы и кэш сборки. В том числе чужих проектов.
:::

## Что вы умеете теперь

- [ ] Объяснить, чем контейнер отличается от виртуальной машины.
- [ ] Запускать готовые образы: `docker run`, `ps`, `logs`, `exec`, `stop`, `rm`.
- [ ] Открывать порты и передавать переменные окружения.
- [ ] Хранить данные в томах и не терять их.
- [ ] Писать `Dockerfile` и собирать образ для своего скрипта.
- [ ] Объединять контейнеры в сеть и ходить по имени службы, а не `localhost`.
- [ ] Описывать стек в `compose.yaml`: `build`, `healthcheck`, `depends_on`, `.env`, `profiles`.
- [ ] Поднимать у себя Postgres, BI и dbt одной командой.

Дальше:

- [Open source за минуты](/practice/docker/use-cases/): Airflow, Jupyter, Kafka и другие инструменты данных.
- [Нужен ли Kubernetes](/practice/docker/kubernetes/): когда хватит контейнеров, а когда нужен оркестратор.
- [Шпаргалка](/practice/docker/cheatsheet/): все команды на одной странице.
