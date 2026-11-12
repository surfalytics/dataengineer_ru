---
title: "Data Pipelines with Apache Airflow, глава 2: Анатомия DAG"
head:
  - tag: title
    content: "Первый DAG в Airflow: операторы, зависимости, сбои | Инжиниринг Данных"
description: "Конспект главы 2 Data Pipelines with Apache Airflow на русском. Первый DAG, BashOperator и PythonOperator, запуск, clear упавших tasks, DAG versioning."
sidebar:
  order: 2
  label: "2. Анатомия DAG"
tags:
  - books
  - airflow
  - dag
---

**Главная мысль:** DAG состоит из tasks. Каждая task запускает один operator. Порядок задают оператором `>>`. Airflow показывает статусы и логи, а упавшие tasks можно перезапустить через `clear`.

![Пример DAG: скачать запуски ракет, скачать картинки, отправить уведомление](/assets/data-pipelines-with-apache-airflow/ch02-rocket-dag.png)

## Пример из главы

Джон любит ракеты. Он хочет собирать картинки ближайших запусков в одну папку. Источник: бесплатный API Launch Library 2. Он отдаёт JSON со списком запусков, и у каждого есть ссылка на картинку.

План разбит на три tasks:

| Task | Operator | Что делает |
|---|---|---|
| `download_launches` | `BashOperator` | Скачивает JSON через `curl` |
| `get_pictures` | `PythonOperator` | Читает JSON и скачивает картинки |
| `notify` | `BashOperator` | Печатает, сколько картинок скачано |

Правильных границ между tasks нет. Книга обещает вернуться к этому вопросу в других главах.

## Из чего состоит DAG-файл

- Импорты. В Airflow 3 класс `DAG` берут из `airflow.sdk`.
- Объект `DAG` с `dag_id`, `start_date` и `schedule`.
- Tasks: объекты operators с уникальным `task_id`.
- Зависимости между tasks.

Три способа определить DAG:

| Способ | Плюс | Минус |
|---|---|---|
| Explicit: DAG передаётся в каждую task | Прямо видно, к какому DAG относится task | Много кода. Можно забыть аргумент |
| Context manager (`with DAG(...)`) | Короче, меньше ошибок | Один DAG на блок. Новичкам синтаксис `with` может быть незнаком |
| Taskflow API | Современный стиль на декораторах | Разбирается в главе 6 |

Книга использует context manager.

## Зависимости

Порядок задают оператором `>>` (или `<<`):

```text
download_launches >> get_pictures >> notify
```

- Это Python-операторы побитового сдвига. Airflow переопределил их ради читаемости.
- Стрелка значит: следующая task стартует только после успеха предыдущей.

## Task и operator

- Operator делает одну единицу работы. Это шаблон: `BashOperator` запускает команду, `PythonOperator` вызывает функцию, `EmailOperator` шлёт письмо.
- Task это обёртка над operator. Она управляет запуском: состоянием, ошибками, зависимостями.
- В разговорах слова часто взаимозаменяют. Для пользователя это одно и то же.
- Все operators наследуются от `BaseOperator`.

### Как работает PythonOperator

- Вы пишете функцию. Книга называет её с подчёркиванием: `_get_pictures`.
- Передаёте её в `python_callable`.
- Всё, что функция печатает через `print`, попадает в логи Airflow.
- `task_id` это главный идентификатор task в логах, API и UI. Удобно называть переменную так же, как `task_id`.

## Запуск Airflow

Минимальный Airflow это пять компонентов: DAG processor, scheduler, API server, triggerer и база.

| Способ | Как | Когда |
|---|---|---|
| Python-окружение | `pip install apache-airflow`, затем `airflow standalone` | Быстрый старт. Команда создаёт базу и пользователя и запускает компоненты |
| Docker Compose | `docker compose up` в папке главы | Книга советует его. Окружение воспроизводимое |

- Ставьте `apache-airflow`, а не `airflow`. Пакет `airflow` на PyPI это заглушка.
- UI открывается на `localhost:8080`.
- В Docker файлы из `/tmp` лежат внутри контейнера worker. Чтобы их увидеть, зайдите туда через `docker exec`.

## Работа в UI

1. Откройте список DAG. Включите DAG переключателем и нажмите `Trigger`.
2. В `graph view` видна структура DAG и цвета состояний. Этот вид удобен при разработке.
3. Нажмите на task и откройте `Logs`. Там весь вывод.
4. В `grid view` каждая колонка это один run. Каждая строка это одна task во времени.

## Регулярный запуск

Чтобы не запускать вручную, задают `schedule`. Для примера: `schedule="@daily"`, плюс `start_date` 14 дней назад и `catchup=True`. Тогда Airflow создаст 14 дневных runs за прошлое.

Подробно расписания разбираются в [главе 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/).

## Сбои

![Task упала, следующая получила upstream_failed, после clear обе запускаются снова](/assets/data-pipelines-with-apache-airflow/ch02-failure-clear.png)

Причин много: сервис недоступен, ошибка в коде, нет сети, сломался диск.

- Упавшая task получает статус `failed`.
- Следующие tasks не запускаются. Их статус `upstream_failed`, цвет оранжевый.
- Причину ищут в логах. Там виден stack trace.
- Починили причину? Нажмите `Clear Task Instance`. Можно очистить только эту task, а можно и `Upstream` или `Downstream`.
- Перезапускать весь DAG не нужно. Успешные tasks остаются как есть.
- Автоматически сбои смягчают через `retries`. Их разбирают в главе 6.

## DAG versioning

Новая возможность Airflow 3.

- DAG processor замечает изменения кода и создаёт новую версию.
- В UI есть меню `Versions`. Там видно старые версии кода и tasks.
- В релизе 3.0.0 запуск всегда идёт по последней версии. Пока это скорее удобство для просмотра.
- Версии нужны как основа для более безопасных backfills и лучшей наблюдаемости.
- Работает через `DAG bundles`. Локальная папка dags это `LocalDagBundle`. Есть и `GitDagBundle`. Подробности в главе 17.

## Пример кода

Проверено на Airflow 3.4: DAG проходит `airflow dags test`.

Своя маленькая версия DAG с функцией на Python. Имена придуманы для примера.

```python
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def _count_words():
    with open("/tmp/news.txt") as f:
        print(len(f.read().split()))


with DAG(
    dag_id="demo_news_words",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,
):
    download = BashOperator(
        task_id="download",
        bash_command="curl -o /tmp/news.txt -L https://example.com",
    )
    count = PythonOperator(task_id="count", python_callable=_count_words)

    download >> count
```

## Ключевые термины

| Термин | Значение |
|---|---|
| `dag_id` | Имя DAG в UI |
| `task_id` | Имя task внутри DAG |
| `BashOperator` | Запускает команду shell |
| `PythonOperator` | Вызывает Python-функцию (`python_callable`) |
| `>>` | Задаёт порядок: левая task раньше правой |
| `Context manager` | Блок `with DAG(...)`, внутри которого tasks привязаны к DAG |
| `upstream_failed` | Статус task, чья предыдущая task упала |
| `Clear` | Сброс состояния task. Airflow запускает её заново |
| `DAG versioning` | История версий структуры DAG (Airflow 3) |
| `DAG bundle` | Источник DAG-кода: локальная папка или git |

## Что это значит на практике

- Начинайте DAG с одного `dag_id`, понятных `task_id` и явных зависимостей.
- Не кладите тяжёлую логику внутрь DAG-файла. Держите функции короткими и выносите их в модули.
- При сбое сначала читайте логи task. Потом чините причину и делайте `clear`, а не запускайте DAG целиком.
- Помните про `upstream_failed`: это не ошибка самой task, а следствие.
- Для локальной разработки берите Docker Compose. Окружение будет одинаковым у всей команды.
- Ставьте `apache-airflow`, не `airflow`.

## Вопросы для самопроверки

1. В чём разница между task и operator?
2. Какие три способа определить DAG? Какой выбрала книга и почему?
3. Что значит статус `upstream_failed` и что делать после починки причины?
4. Что даёт DAG versioning в Airflow 3 и чего он пока не делает?

Предыдущая: [Знакомство с Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/). Следующая: [Расписания по времени](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/).
