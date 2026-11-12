---
title: "Хороший образ"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Dockerfile: кэш слоёв, .dockerignore, non-root | Инжиниринг Данных"
description: "Как написать хороший Dockerfile: порядок слоёв и кэш, .dockerignore, пользователь без root, фиксация версий пакетов, секреты и multi-stage сборка."
sidebar:
  order: 9
tags:
  - docker
  - practice
---

Простой `Dockerfile` из прошлого урока работает. Но в команде и в продакшене нужны ещё пять привычек. Они делают сборку быстрой, образ безопасным, а результат повторяемым.

## 1. Порядок слоёв и кэш

Docker кэширует слои. Если инструкция и её входные файлы не изменились, Docker берёт готовый слой. Если слой изменился, **все слои ниже** собираются заново.

Отсюда правило: **то, что меняется редко — выше. То, что меняется часто — ниже.**

Плохо: сначала весь код, потом зависимости.

```dockerfile
COPY app/ .
RUN pip install -r requirements.txt
```

Вы поменяли одну строку в `report.py`. Docker заново ставит все пакеты. Это минуты.

Хорошо: сначала список зависимостей, потом код.

```dockerfile
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
```

Теперь правка кода не трогает слой с пакетами.

### Смотрим кэш

Мы соберём образ с зависимостями. Скопируйте `Dockerfile` из раздела [«Итоговый Dockerfile»](#итоговый-dockerfile) ниже в папку `~/docker-practice` и соберите его:

```bash
docker build -t orders-app:1.0 .
```

Измените код и соберите снова:

```bash
echo "# правка" >> app/report.py
docker build --progress=plain -t orders-app:1.0 .
```

В выводе найдите слова `CACHED`. Для слоёв `RUN useradd`, `WORKDIR`, `COPY app/requirements.txt` и `RUN pip install` вы увидите `CACHED`. Заново собирается только `COPY app/ .`. Сборка занимает меньше секунды.

Теперь измените `requirements.txt`:

```bash
echo "# правка" >> app/requirements.txt
docker build --progress=plain -t orders-app:1.0 .
```

Слой `COPY app/requirements.txt` и все слои ниже собираются заново, включая `pip install`. Слои выше остаются в кэше.

Уберите ваши правки из файлов `app/report.py` и `app/requirements.txt` (удалите последнюю строку-комментарий).

## 2. .dockerignore

При сборке Docker отправляет в сборку всю папку (контекст). Файл `.dockerignore` говорит, что отправлять не нужно. Формат такой же, как у `.gitignore`.

Создайте `.dockerignore` в папке `~/docker-practice`:

```
.git
__pycache__
*.pyc
.env
data
```

Зачем:

- Меньше контекст и быстрее сборка.
- Секреты (`.env`) не попадут в образ даже по ошибке.
- `data` не нужна в образе: мы подключаем её через `-v`.

Проверим защиту. Создайте `.env` и попробуйте скопировать его:

```bash
echo "SECRET=1" > .env
printf 'FROM alpine:3.22\nCOPY .env /app/.env\n' > Dockerfile.bad
docker build -f Dockerfile.bad -t orders-bad .
```

```
ERROR: failed to build: failed to solve: failed to compute cache key: ... "/.env": not found
```

Docker не нашёл `.env`, потому что `.dockerignore` его скрыл. Удалите пробные файлы: `rm .env Dockerfile.bad`.

## 3. Не запускайте от root

По умолчанию процесс в контейнере работает как `root`. Если в программе есть уязвимость, у атакующего больше прав. Создайте обычного пользователя:

```dockerfile
RUN useradd --create-home appuser
...
USER appuser
```

Проверьте:

```bash
docker run --rm orders-app:1.0 id
```

```
uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

Пользователя создаём **рано**, сразу после `FROM`. Его слой почти не меняется и всегда берётся из кэша. Инструкцию `USER` ставим после установки пакетов: `pip install` ещё должен работать от root.

## 4. Фиксируйте версии

Всё, что может измениться, закрепляйте:

| Что | Плохо | Хорошо |
|---|---|---|
| Базовый образ | `python:latest` | `python:3.12-slim` |
| Пакет Python | `psycopg` | `psycopg[binary]==3.3.8` |
| Инструмент | `pip install dbt-postgres` | `pip install dbt-core==1.12.6 dbt-postgres==1.11.0` |

Настоящий пример с dbt. Мы поставили `pip install dbt-postgres==1.11.0` и проверили версию:

```
Core:
  - installed: 1.13.0-b1
  - latest:    1.12.6    - Ahead of latest version!
```

Версия `1.13.0-b1` — это **бета**. Пакет `dbt-postgres` требует `dbt-core>=1.8.0rc1`, и pip взял самую новую версию, даже пре-релиз. Мы закрепили адаптер, но не ядро. Поэтому в образ попала бета.

Вывод: закрепляйте **все** версии, а не только главный пакет. Для Python — файл `requirements.txt` с `==`.

## 5. Секреты не кладут в образ

В образе всё читается: `docker history` и `docker run образ cat файл`. Кто получит образ, получит и всё, что в нём лежит.

Никогда:

- `COPY .env ...` — не копируйте файлы с паролями.
- `ENV DB_PASSWORD=secret` — переменная останется в образе навсегда.
- `RUN ... --password secret` — пароль виден в истории слоёв.

Передавайте секреты **при запуске**: `-e DB_PASSWORD=...` или `--env-file`. В Compose — через файл `.env` и секреты оркестратора. Образ хранит программу. Настройки и пароли приходят снаружи.

## Multi-stage: когда нужно

**Multi-stage** — это сборка в несколько этапов. На первом этапе ставят всё нужное для сборки. На втором берут только результат.

```dockerfile
FROM python:3.12-slim AS build
RUN python -m venv /opt/venv
COPY app/requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN useradd --create-home appuser
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY app/ .
USER appuser
CMD ["python", "report.py"]
```

Мы проверили, и честный результат такой:

| Образ | Размер |
|---|---|
| Обычный `Dockerfile` | 180 МБ |
| Multi-stage | 183 МБ |

Для нашего приложения выигрыша нет. Здесь пакет `psycopg[binary]` приходит уже собранным.

Multi-stage окупается, когда для сборки нужны **компиляторы** (`gcc`, заголовки C), а в готовом образе они не нужны. Тогда образ может стать на сотни мегабайт меньше. Не усложняйте `Dockerfile`, пока у вас нет такой задачи.

## Теги и публикация (только объяснение)

Чтобы поделиться образом, ему дают имя с адресом реестра и отправляют:

```bash
docker tag orders-app:1.0 ghcr.io/<user>/orders-app:1.0
docker push ghcr.io/<user>/orders-app:1.0
```

Здесь `<user>` — ваш логин на GitHub. Перед `push` нужен вход: `docker login ghcr.io`. Мы этого не делаем в курсе. Как это работает в команде — в уроке [Контейнеры в продакшене](/practice/docker/production/).

Теги образов тоже фиксируют. Не перезаписывайте `1.0`. Выпустили исправление — это `1.1`.

В учебных сборках мы перезаписываем `1.0` для простоты. В команде так не делают.

## Итоговый Dockerfile

Это образ `orders-app:1.0`. Он нужен нам в следующих уроках. Сохраните его в `~/docker-practice/Dockerfile` (замените старый):

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

В образе два скрипта: `report.py` и `load_orders.py`. По умолчанию запускается `report.py`. Второй мы запустим позже, заменив команду в Compose.

Запуск:

```bash
docker build -t orders-app:1.0 .
docker run --rm -v "$PWD/data:/data:ro" orders-app:1.0
```

```
Файл: /data/orders.csv
Заказов: 500
Выручка по каналам (только completed):
  organic    23715.82
  ads        23082.74
  email      15459.67
```

Проверьте, что `psycopg` есть в образе:

```bash
docker run --rm orders-app:1.0 python -c "import psycopg; print(psycopg.__version__)"
```

```
3.3.8
```

## Практика

Работайте в папке `~/docker-practice`.

### Задание 1

Создайте `.dockerignore` и итоговый `Dockerfile`. Соберите `orders-app:1.0` и запустите отчёт.

**Проверка:** `Заказов: 500`, organic 23715.82, ads 23082.74, email 15459.67.

<details>
<summary>Решение</summary>

Файлы — выше. Сборка и запуск:

```bash
docker build -t orders-app:1.0 .
docker run --rm -v "$PWD/data:/data:ro" orders-app:1.0
```

</details>

### Задание 2

От какого пользователя работает контейнер? Какой у него `uid`?

**Проверка:** `uid=1000(appuser)`.

<details>
<summary>Решение</summary>

```bash
docker run --rm orders-app:1.0 id
```

</details>

### Задание 3

Проверьте кэш. Добавьте в конец `app/report.py` строку-комментарий и соберите образ с `--progress=plain`. Какие слои были `CACHED`? Какой слой пересобрался?

**Проверка:** `CACHED` у слоя `pip install`. Пересобрался только `COPY app/ .`.

<details>
<summary>Решение</summary>

```bash
echo "# правка" >> app/report.py
docker build --progress=plain -t orders-app:1.0 . 2>&1 | grep -E "CACHED|COPY|RUN"
```

Потом удалите комментарий из `report.py`.

</details>

### Задание 4

Поменяйте порядок в `Dockerfile` на плохой: сначала `COPY app/ .`, потом `pip install`. Измените `report.py` и соберите. Что изменилось в кэше? Верните правильный порядок.

**Проверка:** слой `pip install` больше не `CACHED`: пакеты ставятся заново при каждой правке кода.

<details>
<summary>Решение</summary>

Плохой порядок:

```dockerfile
COPY app/ .
RUN pip install --no-cache-dir -r requirements.txt
```

`requirements.txt` уже внутри `app/`, поэтому отдельный `COPY` не нужен. Любая правка кода меняет `COPY app/ .`, а значит, и всё ниже.

</details>

### Задание 5

Докажите, что секрет в `ENV` виден всем. Соберите образ с `ENV DB_PASSWORD=secret` и найдите пароль без запуска программы.

**Проверка:** пароль виден в выводе `docker image inspect`.

<details>
<summary>Решение</summary>

```bash
printf 'FROM alpine:3.22\nENV DB_PASSWORD=secret\n' > Dockerfile.bad
docker build -f Dockerfile.bad -t orders-bad .
docker image inspect orders-bad --format '{{.Config.Env}}'
docker history orders-bad
rm Dockerfile.bad
docker rmi orders-bad
```

В `Env` есть `DB_PASSWORD=secret`. Пароль в образе навсегда. Передавайте его через `-e` при запуске.

</details>

Дальше: [Сети](/practice/docker/networks/).
