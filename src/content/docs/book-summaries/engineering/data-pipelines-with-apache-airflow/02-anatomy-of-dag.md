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

**Главная мысль:** большую работу Airflow режет на небольшие tasks, которые вместе образуют DAG. Порядок tasks задают зависимости. Статусы и логи видны в UI, а упавшие tasks можно перезапустить без перезапуска всего DAG.

## О чём глава

[Глава 1](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/) объяснила, зачем нужен Airflow. Эта глава собирает первый рабочий DAG: пример, три способа определить DAG, task и operator, запуск и UI, расписание, сбои и DAG versioning.

![Пример DAG: скачать запуски ракет, скачать картинки, отправить уведомление](/assets/data-pipelines-with-apache-airflow/ch02-rocket-dag.png)

## Пример: картинки ракет

Джон следит за запусками ракет и хочет собирать их картинки в одну папку. Данные даёт бесплатный API Launch Library 2: JSON со списком ближайших запусков. У каждого есть название, окно старта и ссылка на картинку (`image`).

План Джона состоит из пяти шагов. В Airflow он делится на три tasks.

| Task | Operator | Что делает |
|---|---|---|
| `download_launches` | `BashOperator` | Скачивает JSON через `curl` |
| `get_pictures` | `PythonOperator` | Читает JSON и скачивает картинки |
| `notify` | `BashOperator` | Сообщает, сколько картинок скачано |

Почему три, а не одна или пять? Правильного ответа нет. Автор вернётся к границам между tasks позже. Зачем тут Airflow, если хватит одной команды Bash? Tasks можно запускать параллельно и на разных технологиях, и у каждой свой статус и лог.

## Первый DAG

Всё начинается с объекта `DAG`. Каждая task ссылается на него, так Airflow знает, что они в одном workflow. Три способа определить DAG:

| Способ | Плюс | Минус |
|---|---|---|
| Explicit: DAG передаётся в каждую task | Прямо видно, к какому DAG относится task | Много кода. Можно забыть `dag` |
| Context manager (`with DAG(...)`) | Короче, меньше ошибок | Один DAG на блок. Синтаксис `with` может быть незнаком |
| Taskflow API | Современный стиль на декораторах | Разбирается в главе 6 |

Книга берёт context manager. Обязательные аргументы `DAG`: `dag_id` (имя в UI) и `start_date`. `schedule=None` значит ручной запуск.

Первая task это `BashOperator` с командой `curl`. Вторая это `PythonOperator`: он вызывает функцию из аргумента `python_callable`. Функцию называют с подчёркиванием, `_get_pictures`, чтобы имя не совпало с переменной `get_pictures`. Всё, что она печатает через `print`, попадёт в логи Airflow. `task_id` это главный идентификатор task в логах, API и UI. Переменную удобно называть так же.

Ниже наша версия DAG. Она работает без сети: первая task пишет маленький JSON, вторая пишет файлы вместо скачивания. Полный файл: [ch02_rocket_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch02_rocket_dag.py).

```python
with DAG(
    dag_id="rocket_launches",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # запуск только вручную
):
    download_launches = BashOperator(
        task_id="download_launches",
        bash_command=(
            f"mkdir -p {WORK} && echo "
            "'{\"results\": [{\"image\": \"https://x.org/falcon9.jpg\"},"
            " {\"image\": \"https://x.org/electron.jpg\"}]}' "
            f"> {WORK}/launches.json"
        ),
    )
    get_pictures = PythonOperator(task_id="get_pictures", python_callable=_get_pictures)
    notify = BashOperator(
        task_id="notify",
        bash_command=f'echo "There are $(ls {WORK}/images | wc -l) images."',
    )

    download_launches >> get_pictures >> notify
```

### Зависимости

Порядок задаёт последняя строка: `download_launches >> get_pictures >> notify`. Это побитовый сдвиг вправо из Python. Airflow переопределил его, потому что сдвиг битов в DAG не нужен, а запись читается как стрелка. Работает и `<<`. Task справа стартует только после успеха task слева.

### Task и operator

Operator делает одну единицу работы. Есть общие (`BashOperator`, `PythonOperator`) и узкие (`EmailOperator`, `HTTPOperator`). Все наследуются от `BaseOperator`. Task это обёртка над operator: она управляет запуском, ошибками и зависимостями. Пользователь выбирает operator, Airflow ведёт task. В разговорах слова часто взаимозаменяют.

![DAG состоит из tasks, каждая task оборачивает один operator](/assets/data-pipelines-with-apache-airflow/ch02-dag-task-operator.png)

## Запуск Airflow

Минимальный Airflow это пять компонентов: DAG processor, scheduler, API server, triggerer и база. Поднять их можно двумя путями.

**Python-окружение.** Создайте виртуальное окружение (`venv`, `uv`, `Poetry`, `Conda`), чтобы зависимости проектов не мешали друг другу. Дальше:

```text
pip install apache-airflow
airflow standalone
```

Ставьте `apache-airflow`, а не `airflow`: старое имя на PyPI осталось как заглушка. Команда `airflow standalone` создаёт metastore (базу состояний) и пользователя `admin`, затем запускает api-server, scheduler, dag-processor и triggerer. Пароль печатается в логе.

**Docker.** Автор советует Docker: контейнер даёт воспроизводимое окружение вместе с драйверами и другими зависимостями. Docker Compose описывает несколько контейнеров в YAML-файле. В репозитории книги есть compose-файл для каждой главы. В папке главы выполните `docker compose up`. Через пару минут `docker ps` покажет worker, apiserver, dag-processor, scheduler, triggerer, postgres и redis. UI: `localhost:8080`, логин и пароль `airflow`.

## Работа в UI

1. В списке DAG найдите свой DAG из папки `dags` и откройте `graph view`. Он показывает tasks и их порядок. Во время разработки этот вид нужен чаще всего.
2. Включите DAG переключателем и нажмите `Trigger`. Цвета показывают состояние.
3. Нажмите на task и откройте `Logs`. Там весь вывод, включая `print`.
4. В Docker папка `/tmp/images` лежит только внутри контейнера worker. Зайдите туда через `docker exec -it <worker> /bin/bash`.

Проверим наш DAG без сервера: разберём его в `DagBag` и выполним через `dag.test()`. Скрипт [ch02_check_rocket.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch02_check_rocket.py).

```text
ошибки импорта: нет
порядок: download_launches >> get_pictures >> notify
download_launches: success
get_pictures: success
notify: success
файлов в images: 2
```

Ошибок нет, порядок совпал со строкой `>>`, все tasks в `success`.

## Регулярный запуск

Чтобы не нажимать `Trigger` каждый раз, задают `schedule`. Для примера: `schedule="@daily"` (это `0 0 * * *`, полночь), `start_date` 14 дней назад и `catchup=True`. Airflow делит время на 14 интервалов по дню. Все они уже в прошлом, поэтому DAG запустит 14 runs. В `grid view` каждая колонка это один run, а каждая строка это одна task. Остальные способы расписания разобраны в [главе 3](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/).

## Сбои

![Task упала, следующая получила upstream_failed, после clear обе запускаются снова](/assets/data-pipelines-with-apache-airflow/ch02-failure-clear.png)

Причин сбоя много: сервис недоступен, ошибка в коде, сеть, диск. Допустим, пропала сеть.

- Упавшая task получает статус `failed`.
- Следующая task не запускается. Её статус `upstream_failed`, цвет оранжевый. По умолчанию все upstream tasks должны завершиться успехом.
- Причину ищут в логах. В stack trace будет, например, `ConnectionError: Could not connect to ...`.
- Починили причину? Нажмите `Clear Task Instance`. Можно очистить только эту task, а можно и `Upstream` или `Downstream` в том же run, или ту же task в другом run. Clear сбрасывает состояние, и Airflow сам запускает tasks заново.
- Весь DAG перезапускать не нужно: успешные tasks остаются как есть.

В [ch02_failure_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch02_failure_dag.py) функция `get_pictures` всегда падает.

```python
def _get_pictures():
    raise ConnectionError("Could not connect to https://x.org/falcon9.jpg")
```

```text
download_launches: success
get_pictures: failed
notify: upstream_failed
```

Это картина из UI: упала одна task, следующая получила `upstream_failed`. Когда сбой допустим, настраивают на любом уровне workflow (глава 6). Дату run в код вносят позже, в главе 5.

## DAG versioning

Это новая возможность Airflow 3. Изменения структуры DAG (переименовали task, поменяли зависимости) записываются в metadata database, и их видно в UI и API. DAG processor сам замечает правку кода и создаёт новую версию. Старые версии кода и tasks видны в меню `Versions`. В выпуске 3.0.0 эффект ограничен: DAG всегда запускается по последней версии. Это основа для безопасных backfills и наблюдаемости в следующих релизах.

![Версия v1 и версия v2 с добавленной task](/assets/data-pipelines-with-apache-airflow/ch02-dag-versions.png)

Чтобы увидеть версию, запустите DAG, затем добавьте в конец новую task. После обработки файла появится `v2`, а вкладка `Code` покажет код любой версии. Версии работают через `DAG bundles`: локальная папка `dags` это `LocalDagBundle`, есть и `GitDagBundle` (глава 17).

## Итоги главы

- Airflow режет большую работу на tasks. Вместе они образуют DAG, он следит за зависимостями.
- DAG определяют тремя способами: explicit, context manager или Taskflow API.
- Operator делает одну единицу работы. Task оборачивает его и управляет состоянием.
- Порядок tasks задают операторами `>>` и `<<`.
- В UI видны список DAG, запуск, статусы tasks и логи для поиска причин.
- Упавшую task чинят и перезапускают через `clear`. Остальные tasks заново не идут.
- DAG versioning в Airflow 3 хранит версии структуры DAG. Пока он в основном информационный.

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
- Границы между tasks выбирайте так, чтобы упавшую часть можно было перезапустить отдельно.
- Печатайте в функциях через `print` или logging: так видно, что было внутри task.

## Практика

Скрипты работают без запущенного Airflow. DAG проверены на Airflow 3.4.0. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

**1. Добавьте task.** В `ch02_rocket_dag.py` добавьте task `archive` (`BashOperator`, `echo archived`), которая идёт после `notify`.

<details>
<summary>Решение</summary>

Создайте `archive = BashOperator(task_id="archive", bash_command="echo archived")` и замените последнюю строку на `download_launches >> get_pictures >> notify >> archive`. Проверка показывает четыре tasks со статусом `success`. Проверено запуском.

</details>

**2. Сбой в начале.** В `ch02_failure_dag.py` замените команду `download_launches` на `exit 1`. Какие статусы получат tasks?

<details>
<summary>Решение</summary>

`download_launches` получит `failed`, а `get_pictures` и `notify` получат `upstream_failed`. Ни одна из них не запускалась. Проверено запуском.

</details>

## Вопросы для самопроверки

1. В чём разница между task и operator?
2. Какие три способа определить DAG? Какой выбрала книга и почему?
3. Что значит статус `upstream_failed` и что делать после починки причины?
4. Почему при `clear` не нужно запускать весь DAG заново?
5. Что даёт DAG versioning в Airflow 3 и чего он пока не делает?

Предыдущая: [Знакомство с Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/01-meet-airflow/). Следующая: [Расписания по времени](/book-summaries/engineering/data-pipelines-with-apache-airflow/03-time-based-scheduling/).
