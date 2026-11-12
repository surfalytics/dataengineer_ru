---
title: Первые контейнеры
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "docker run, ps, logs, exec, stop: первые команды | Инжиниринг Данных"
description: Первые команды Docker с примерами. Как запустить контейнер командой docker run, посмотреть список, логи, зайти внутрь, остановить и удалить.
sidebar:
  order: 4
tags:
  - docker
  - practice
---

В этом уроке вы запустите первые контейнеры и научитесь ими управлять. Шесть команд покрывают почти всю ежедневную работу: `run`, `ps`, `logs`, `exec`, `stop` и `rm`.

## docker run

Главная команда. Она создаёт контейнер из образа и запускает его:

```bash
docker run [опции] ОБРАЗ [команда]
```

Начнём с самого простого:

```bash
docker run --rm alpine:3.22 echo "Привет из контейнера"
```

```
Привет из контейнера
```

Что сделал Docker:

1. Проверил, есть ли образ `alpine:3.22` на вашем компьютере. Если нет, скачал его из Docker Hub. Это видно по строкам `Pulling from library/alpine`. В следующий раз скачивания не будет.
2. Создал контейнер из образа.
3. Запустил в нём команду `echo "Привет из контейнера"`.
4. Команда закончилась, и контейнер остановился.
5. Из-за `--rm` Docker удалил остановленный контейнер.

**Alpine** — очень маленький образ Linux (около 8 МБ). Его удобно брать для проверок.

Контейнер живёт, пока работает его главная команда. Закончилась команда — остановился контейнер. Это главное правило, и оно будет нужно дальше.

### Полезные опции

| Опция | Что делает |
|---|---|
| `--rm` | Удалить контейнер после остановки. Для одноразовых команд |
| `-d` | Запустить в фоне (detached). Терминал остаётся свободным |
| `--name web` | Дать контейнеру имя. Иначе Docker придумает случайное, например `quirky_turing` |
| `-p 8080:80` | Открыть порт. Разберём в уроке [Порты и переменные](/practice/docker/ports-env/) |
| `-it` | Интерактивный режим: можно вводить команды в контейнере |
| `-e NAME=value` | Передать переменную окружения |
| `-v ...` | Подключить папку или том. Разберём в уроке [Тома](/practice/docker/volumes/) |

## Сервис в фоне

Одноразовые команды удобны, но чаще контейнер — это сервис: база данных, веб-сервер. Он должен работать долго. Запустим веб-сервер Nginx:

```bash
docker run -d --name web -p 8080:80 nginx:1.29
```

Docker напечатает длинный идентификатор контейнера и вернёт вам терминал. Контейнер работает в фоне. Проверьте:

```bash
curl -s localhost:8080 | head -5
```

```
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
```

Вы получили страницу от Nginx, который работает внутри контейнера. Можно открыть <http://localhost:8080> в браузере.

<details>
<summary>Порт 8080 занят?</summary>

Тогда Docker ответит `port is already allocated`. Возьмите другой порт слева: `-p 8081:80`, и открывайте <http://localhost:8081>. Подробности — в уроке [Порты и переменные](/practice/docker/ports-env/).

</details>

## docker ps

Список контейнеров:

```bash
docker ps
```

```
CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS                                     NAMES
ee879a5aca06   nginx:1.29   "/docker-entrypoint.…"   10 seconds ago   Up 9 seconds    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
```

| Столбец | Что значит |
|---|---|
| `CONTAINER ID` | Короткий идентификатор |
| `IMAGE` | Из какого образа запущен |
| `STATUS` | `Up` — работает. `Exited (0)` — закончил без ошибки. `Exited (1)` и больше — ошибка |
| `PORTS` | Какие порты открыты |
| `NAMES` | Имя контейнера |

`docker ps` показывает **только работающие** контейнеры. Все, включая остановленные:

```bash
docker ps -a
```

Остановленные контейнеры остаются на диске, пока вы их не удалите. Это частая причина странных ошибок: имя `web` уже занято остановленным контейнером.

Удобные варианты:

```bash
docker ps -q                          # только идентификаторы
docker ps --filter 'name=^web$'        # точное имя. Без ^ и $ найдёт и web-2, и airflow-webserver
docker ps --format 'table {{.Names}}\t{{.Status}}'   # только нужные столбцы
```

## docker logs

Всё, что программа пишет в stdout и stderr, Docker сохраняет как логи:

```bash
docker logs web
```

```
...
2026/11/11 17:50:15 [notice] 1#1: start worker process 35
192.168.65.1 - - [11/Nov/2026:17:50:17 +0000] "GET / HTTP/1.1" 200 896 "-" "curl/8.7.1" "-"
```

Последняя строка — ваш запрос `curl`. Часто используют два варианта:

```bash
docker logs -f web          # следить за логом в реальном времени (выход: Ctrl+C)
docker logs --tail 20 web   # только последние 20 строк
```

Логи — первое, что смотрят, когда контейнер не работает.

## docker exec

Выполнить команду **внутри уже запущенного** контейнера:

```bash
docker exec web nginx -v
```

```
nginx version: nginx/1.29.8
```

Чтобы зайти внутрь и работать как в терминале, нужны опции `-it`:

```bash
docker exec -it web sh
```

Вы увидите приглашение `#`. Это терминал внутри контейнера. Выполните `ls /usr/share/nginx/html`, посмотрите файлы. Выход: `exit`.

| | `docker run` | `docker exec` |
|---|---|---|
| Что делает | Создаёт **новый** контейнер | Работает в **существующем** |
| Образ нужен | Да | Нет |

`docker exec` — главный способ посмотреть, что внутри. Например, зайти в контейнер с базой и выполнить `psql`.

## Остановить и удалить

```bash
docker stop web      # остановить
docker start web     # запустить снова
docker restart web   # перезапустить
docker rm web        # удалить остановленный контейнер
```

Проверьте статус после остановки:

```bash
docker stop web
docker ps -a --filter 'name=^web$' --format '{{.Names}} | {{.Status}}'
```

```
web | Exited (0) Less than a second ago
```

Контейнер остановлен, но существует. Его можно запустить командой `docker start web`. Удалите его:

```bash
docker rm web
```

Две частые ошибки:

```
Error response from daemon: cannot remove container "web": container is running: stop the container before removing or force remove
```

Сначала остановите (`docker stop web`) или удалите принудительно: `docker rm -f web`.

```
docker: Error response from daemon: Conflict. The container name "/web" is already in use by container "c206c14b6d09...". You have to remove (or rename) that container to be able to reuse that name.
```

Имя занято старым контейнером. Удалите его: `docker rm web`.

<details>
<summary>Чем stop отличается от kill?</summary>

`docker stop` просит программу завершиться (сигнал SIGTERM) и ждёт 10 секунд. Если она не завершилась, Docker убивает её. Так программа успевает сохранить данные. `docker kill` убивает сразу. Используйте `stop`.

</details>

## Интерактивный контейнер

Можно запустить контейнер и сразу работать в нём:

```bash
docker run -it --rm alpine:3.22 sh
```

Опции:

- `-i` оставляет ввод открытым.
- `-t` включает терминал.
- `--rm` удалит контейнер после выхода.

Вы внутри Alpine. Попробуйте `cat /etc/os-release`, `ls /`, `whoami`. Выход: `exit`. Контейнер остановится и удалится.

Так же запускают Python без установки на компьютер:

```bash
docker run -it --rm python:3.12-slim python
```

## Практика

Выполняйте задания по порядку. Задания 2–5 используют один контейнер `web`.

### Задание 1

Запустите одноразовый контейнер Alpine и покажите первые две строки файла `/etc/os-release`. Контейнер должен удалиться сам.

**Проверка:**

```
NAME="Alpine Linux"
ID=alpine
```

<details>
<summary>Решение</summary>

```bash
docker run --rm alpine:3.22 head -2 /etc/os-release
```

Проверка удаления: `docker ps -a` не показывает этот контейнер.

</details>

### Задание 2

Запустите Nginx в фоне с именем `web` на порту 8080. Проверьте командой `curl`, что он отвечает. Выведите только строку с заголовком страницы.

**Проверка:** `<title>Welcome to nginx!</title>`

<details>
<summary>Решение</summary>

```bash
docker run -d --name web -p 8080:80 nginx:1.29
curl -s localhost:8080 | grep title
```

Если порт занят, используйте `-p 8081:80` и `localhost:8081`.

</details>

### Задание 3

Найдите в логах контейнера `web` строку с вашим запросом `curl`.

**Проверка:** строка содержит `"GET / HTTP/1.1" 200`.

<details>
<summary>Решение</summary>

```bash
docker logs web | grep GET
```

Nginx пишет запросы в stdout, а ошибки в stderr. Чтобы искать сразу по всем логам, добавьте `2>&1`: `docker logs web 2>&1 | grep error`.

</details>

### Задание 4

Не заходя в контейнер, узнайте версию Nginx внутри `web`. Затем зайдите в контейнер и посмотрите список файлов в папке `/usr/share/nginx/html`.

**Проверка:** версия `nginx/1.29.<число>`. Файлы: `50x.html` и `index.html`.

<details>
<summary>Решение</summary>

```bash
docker exec web nginx -v
docker exec -it web sh
ls /usr/share/nginx/html
exit
```

Или одной командой, без входа внутрь: `docker exec web ls /usr/share/nginx/html`.

</details>

### Задание 5

Остановите `web`. Проверьте, что он остановлен, но не удалён. Запустите его снова. Остановите и удалите совсем.

**Проверка:** после `stop` статус `Exited (0)`. После `start` статус `Up`. После `rm` команда `docker ps -a --filter 'name=^web$'` показывает только строку заголовка.

<details>
<summary>Решение</summary>

```bash
docker stop web
docker ps -a --filter 'name=^web$'
docker start web
docker ps --filter 'name=^web$'
docker stop web
docker rm web
docker ps -a --filter 'name=^web$'
```

Короткий вариант для последних двух шагов: `docker rm -f web`. Флаг `-f` останавливает и удаляет.

</details>

### Задание 6

Запустите интерактивный Python в контейнере. Посчитайте `2 ** 10`. Выйдите.

**Проверка:** `1024`. После выхода контейнер удалён (`docker ps -a` его не показывает).

<details>
<summary>Решение</summary>

```bash
docker run -it --rm python:3.12-slim python
```

В Python:

```python
2 ** 10
exit()
```

</details>

Дальше: [Образы и реестры](/practice/docker/images/).
