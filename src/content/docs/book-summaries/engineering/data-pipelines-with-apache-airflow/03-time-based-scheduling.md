---
title: "Data Pipelines with Apache Airflow, глава 3: Расписания по времени"
head:
  - tag: title
    content: "Расписания Airflow: cron, data interval, backfill | Инжиниринг Данных"
description: "Конспект главы 3 Data Pipelines with Apache Airflow на русском. Trigger и data interval timetables, catchup, backfilling, atomicity и idempotency."
sidebar:
  order: 3
  label: "3. Расписания по времени"
tags:
  - books
  - airflow
  - scheduling
---

**Главная мысль:** расписание Airflow задают через `start_date`, `schedule`, `end_date` и `catchup`. Для инкрементальной загрузки нужны `data interval`. А чтобы повторные запуски были безопасны, task должна быть атомарной и идемпотентной.

## О чём глава

Главы 1 и 2 запускали DAG раз в день. Здесь разберём, когда стартует run, как брать данные только за свой интервал и как безопасно перезапускать прошлое. Предыдущая тема: [анатомия DAG](/book-summaries/engineering/data-pipelines-with-apache-airflow/02-anatomy-of-dag/).

![Сравнение: trigger timetable запускает run в момент времени, data interval timetable запускает его в конце интервала](/assets/data-pipelines-with-apache-airflow/ch03-trigger-vs-interval.png)

## Обработка событий пользователей

Сервис пишет, какие страницы сайта открывали пользователи. Маркетингу нужна дневная статистика. Внешний сервис хранит события 30 дней, а API отдаёт последние 7. Историю копим сами.

DAG из двух tasks: `fetch_events` скачивает события через `BashOperator` и `curl`, `calculate_stats` считает их через pandas в `PythonOperator`. Первая версия без расписания: `schedule=None`.

## Четыре параметра расписания

| Параметр | Что значит |
|---|---|
| `start_date` | Начало окна, в котором DAG может запускаться. Обязателен |
| `end_date` | Конец окна. Не обязателен. Без него DAG работает бесконечно |
| `schedule` | Как часто запускать. Обязателен. `None` значит только ручной запуск |
| `catchup` | Запускать ли пропущенные точки из прошлого |

Расписание бывает time-based (эта глава) и asset-based (глава 4).

При `catchup=False` Airflow смотрит только вперёд, с момента включения DAG. При `catchup=True` он создаёт runs и за прошлое, начиная со `start_date`.

> **Предупреждение автора: Airflow 2 и 3 ведут себя по-разному.** Строка `"@daily"` или cron в `schedule` в Airflow 3 даёт trigger-расписание, в Airflow 2 давала interval-расписание. `catchup` по умолчанию был `True`, стал `False`. Поэтому автор называет класс timetable явно и советует задавать `catchup` явно. Дефолт меняет настройка `scheduler.catchup_by_default`.

## Trigger-расписания

`Trigger timetable` задаёт точки времени. Когда точка прошла, Airflow сразу создаёт run. Это работает как cron.

### Ежедневный запуск

Берём `CronTriggerTimetable` с выражением `"0 0 * * *"` (каждый день в полночь) и поясом UTC, это пояс Airflow по умолчанию. Если убрать `end_date`, DAG работает бесконечно.

Ловушка: включим DAG с `start_date` в прошлом, и в Airflow 3 не будет ни одного run, ведь `catchup=False`. Для прошлых runs ставим `catchup=True`.

Вторая проблема: каждый run пишет в один файл и затирает прошлый результат. Решение: имя файла с датой, например `/data/events/2025-01-01.json`. Дату даёт `logical_date` из контекста task. Её вставляет Jinja-шаблон `{{ logical_date | ds }}` (подробно в главе 5).

Минусы остаются: мы не управляем диапазоном событий от `latest`, и статистика не строго дневная. Это решают интервалы.

### Cron-выражения

Cron записывают пятью полями: минута, час, день месяца, месяц, день недели. Звёздочка значит «любое значение», запятая даёт список, дефис диапазон.

| Выражение | Что значит |
|---|---|
| `0 * * * *` | каждый час |
| `0 0 * * MON-FRI` | по будням в полночь |
| `0 0,12 * * *` | каждый день в 00:00 и 12:00 |

Совет автора: проверяйте cron на crontab.guru и комментируйте сложные выражения.

### Сокращения

Для частых расписаний есть preset: `@hourly`, `@daily` (равно `0 0 * * *`), `@weekly`, `@monthly`, `@quarterly`, `@yearly`. Автор предпочитает передавать его в явный класс.

### Расписание по частоте

Cron не умеет «раз в два дня». Выражение «1, 3, 5... числа» ломается на границе месяца: DAG пойдёт 31-го и 1-го подряд. Причина: cron stateless. Он сверяет шаблон с текущим временем и не помнит прошлый запуск.

Здесь помогает `DeltaTriggerTimetable` с `pendulum.duration`. Например, `duration(days=2)` и `start_date` 1 января дают runs 1, 3 и 5 января (книга называет 3 и 5, но в Airflow 3.4.0 первый run идёт в сам `start_date`). Так же задают «каждые 10 минут».

## Data interval: инкрементальная обработка

Сейчас DAG каждый день скачивает и считает весь каталог событий. Это неэффективно, а файлы по дням полны дублей.

### Инкрементальная обработка

Выход: грузить только события за свой день и считать статистику только по ним. Файлы пишем по дням (`partitions`). Так мы не затираем старое и копим историю дольше 7 дней API.

![Три дневных интервала: у каждого свой файл событий и свой файл статистики](/assets/data-pipelines-with-apache-airflow/ch03-incremental-partitions.png)

### Data interval timetable

Для интервала у сервиса есть endpoint `/events/range` с началом (включено) и концом (не включён). Даты в команде надо менять под каждый run. Это умеет `data interval timetable`: он задаёт отрезки времени, а не точки. Класс для cron: `CronDataIntervalTimetable`. Что меняется:

- Run стартует в конце интервала. Это логично: данные из будущего обработать нельзя.
- В контексте появляются `data_interval_start` и `data_interval_end`.

Даты вставляем шаблонами `{{ data_interval_start | ds }}` и `{{ data_interval_end | ds }}`. Теперь каждый файл содержит события только своего дня. Для `@hourly` схема та же.

![Три дневных интервала: run стартует в конце каждого интервала, logical_date указывает на его начало](/assets/data-pipelines-with-apache-airflow/ch03-interval-timeline.png)

По частоте интервалы задаёт `DeltaDataIntervalTimetable`: тоже run в конце интервала и те же `data_interval_start/end`.

> **Пояснение:** в книге этот класс назван `DeltaIntervalTimetable`. В Airflow 3.4.0 такого имени нет, класс называется `DeltaDataIntervalTimetable`. Мы проверили это импортом.

### Итог по интервалам

Airflow делит время на интервалы от `start_date`. Run первого интервала стартует сразу после его конца: для дня 2024-01-01 это начало 2024-01-02. Мы точно знаем отрезок данных, поэтому это идеально для инкремента. `logical_date` указывает на начало интервала.

Проверим на коде: скрипт печатает три первых run для трёх расписаний.

```text
CronTriggerTimetable:
  run в 2025-01-01 00:00; interval [2025-01-01 00:00, 2025-01-01 00:00)
  run в 2025-01-02 00:00; interval [2025-01-02 00:00, 2025-01-02 00:00)
  run в 2025-01-03 00:00; interval [2025-01-03 00:00, 2025-01-03 00:00)
CronDataIntervalTimetable:
  run в 2025-01-02 00:00; interval [2025-01-01 00:00, 2025-01-02 00:00)
  run в 2025-01-03 00:00; interval [2025-01-02 00:00, 2025-01-03 00:00)
  run в 2025-01-04 00:00; interval [2025-01-03 00:00, 2025-01-04 00:00)
DeltaTriggerTimetable (раз в 2 дня):
  run в 2025-01-01 00:00; interval [2025-01-01 00:00, 2025-01-01 00:00)
  run в 2025-01-03 00:00; interval [2025-01-03 00:00, 2025-01-03 00:00)
  run в 2025-01-05 00:00; interval [2025-01-05 00:00, 2025-01-05 00:00)
```

Trigger-расписание запускает run в точке, интервал пустой: начало равно концу. Раз в два дня идёт с самого `start_date`. Interval-расписание запускает run в конце отрезка и даёт его границы. Скрипт: [ch03_timetables.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch03_timetables.py).

## Нерегулярные события

Не всё идёт по ритму: праздники, матчи, выборы. Для этого есть `EventsTimetable`: вы даёте список дат, и DAG запускается ровно в них.

- Список конечный и небольшой: чем он длиннее, тем дольше грузится DAG.
- Ведёт себя как trigger: есть `logical_date`, нет data interval. Для инкремента смещения считайте сами.
- Ручной запуск из интерфейса возможен всегда. Флаг `restrict_to_events=True` ограничивает его: ручной run берёт последнюю дату из списка (или первую, если ни одна не наступила).

## Backfilling

Backfilling это запуск DAG за прошлые интервалы. Лучше всего он работает с data interval. Им управляет `catchup`, и автор настойчиво советует задавать его явно. Нужен он в двух случаях:

- Загрузить историю для нового набора данных. Но источник должен её хранить: с API на 7 дней глубже недели не загрузить.
- Пересчитать данные после изменения кода или ошибки. Делают `clear` старых task. Лимит API здесь не мешает: старые partitions уже лежат у нас.

Риск: нагрузка. Airflow догоняет быстро и создаёт сотни параллельных runs. Они вытесняют другие DAG и перегружают внешние системы. Ограничить можно так:

| Параметр | Что делает |
|---|---|
| `max_active_runs` | Максимум одновременных runs одного DAG. По умолчанию `core.max_active_runs_per_dag`, это 16 |
| `max_active_tasks` | Максимум одновременных tasks одного DAG. По умолчанию 16. В Airflow 2 назывался `concurrency` |
| `pools` | Лимит по ресурсу, глава 12 |

## Хорошие tasks: атомарность и идемпотентность

Airflow делает почти всю работу для backfill и перезапуска. Но результат верный, только если task атомарна и идемпотентна.

### Атомарность

Атомарность пришла из баз данных: транзакция выполняется целиком или никак. В Airflow task должна либо дать результат, либо упасть, не меняя состояние системы.

Пример: добавим в `calculate_stats` письмо топ-10 пользователей. Если письмо не ушло, task упадёт, но CSV уже записан. Статус `failed` скрывает, что данные записаны частично. Решение: вынести письмо в отдельную task `send_stats`. Тогда упадёт только она.

![Неатомарная task с двумя работами и две атомарные tasks](/assets/data-pipelines-with-apache-airflow/ch03-atomicity.png)

Но «одна операция, одна task» верно не всегда. Если API требует логин, отдельная task на токен создаёт сильную связь: вторая упадёт, если токен устарел. Такие шаги держите в одной task. Готовые операторы обычно атомарны, а с `PythonOperator` и `BashOperator` об этом думаете вы.

### Идемпотентность

Task идемпотентна, если повторный запуск с теми же входами не меняет результат. Простой повтор: кнопка `Clear` на task. Airflow запускает её с теми же значениями интервала.

Наш `fetch_events` идемпотентен: он перезаписывает файл с датой теми же событиями. Неидемпотентный вариант: дописывать события в общий `events.json`, каждый повтор создаст дубли. Проверим: три попытки одной task, два способа записи.

```python
import tempfile
from pathlib import Path

events = ["event1", "event2", "event3"]  # события одного дня
folder = Path(tempfile.mkdtemp())
shared = folder / "events.json"
partition = folder / "events-2025-01-01.json"

for attempt in range(1, 4):
    with shared.open("a") as f:  # плохо: каждый повтор дописывает те же события
        f.write("\n".join(events) + "\n")
    partition.write_text("\n".join(events) + "\n")  # хорошо: повтор перезаписывает файл
    print(f"попытка {attempt}: общий файл {len(shared.read_text().splitlines())} строк, partition {len(partition.read_text().splitlines())} строк")
```

```text
попытка 1: общий файл 3 строк, partition 3 строк
попытка 2: общий файл 6 строк, partition 3 строк
попытка 3: общий файл 9 строк, partition 3 строк
```

Общий файл растёт, partition не меняется. Скрипт: [ch03_idempotent.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch03_idempotent.py).

Правило: перезаписывайте свою partition, в базах используйте upsert, а побочные эффекты task проверяйте отдельно.

## Итоги главы

- Расписание задают `start_date`, `schedule`, `end_date` и `catchup`.
- Trigger запускает run в точке времени и даёт `logical_date`. Data interval режет время на интервалы и даёт `data_interval_start/end`.
- Run по интервалу идёт в конце интервала, поэтому он подходит для инкрементальной загрузки в partitions.
- Расписание задают cron, preset или частотой. Нерегулярные даты берёт `EventsTimetable`.
- Backfilling ограничен данными источника. Нагрузку держат `max_active_runs`, `max_active_tasks` и pools.
- Атомарная task либо дала результат, либо не изменила систему. Идемпотентная при повторе не меняет результат.
- Airflow 3 сменил дефолты: cron и preset стали trigger, `catchup` стал `False`. Будьте явными.

## Ключевые термины

| Термин | Значение |
|---|---|
| `start_date` / `end_date` | Границы окна, где DAG может запускаться |
| `schedule` | Правило запуска: timetable, cron, preset или `None` |
| `catchup` | Запускать ли пропущенные точки из прошлого |
| `CronTriggerTimetable` | Trigger-расписание по cron |
| `DeltaTriggerTimetable` | Trigger-расписание по частоте |
| `CronDataIntervalTimetable` | Data interval по cron |
| `DeltaDataIntervalTimetable` | Data interval по частоте (в книге `DeltaIntervalTimetable`) |
| `EventsTimetable` | Запуск по списку дат |
| `logical_date` | Время, за которое запущен run |
| `data_interval_start/end` | Границы интервала данных run |
| `Partition` | Кусок набора данных, обычно по дате |
| `Atomicity` | Всё или ничего |
| `Idempotency` | Повтор с теми же входами не меняет результат |

## Что это значит на практике

- Задавайте `catchup` явно в каждом DAG. Не полагайтесь на дефолт Airflow 2 или 3.
- Для загрузки в `warehouse` по дням берите data interval и пишите в партицию своего интервала.
- Делайте `INSERT` через перезапись партиции или `MERGE`. Тогда `clear` и backfill не создают дубли.
- Перед backfill на большой период проверьте `max_active_runs` и pools. Иначе вы перегрузите источник.
- Для миграции с Airflow 2 на 3 проверьте все строки `schedule` и значение `catchup`.
- Не складывайте запись и уведомление в одну task. Письмо или вызов API лучше вынести в отдельную.
- Задавайте расписание явным классом timetable. Так DAG ведёт себя одинаково в Airflow 2 и 3.

## Практика

Скрипты проверены на Airflow 3.4.0 без сервера. DAG [ch03_events_dag.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch03_events_dag.py) собирается в `DagBag` и проходит `airflow dags test`. API событий заменён функцией, которая генерирует события из даты. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md). Главная часть DAG:

```python
with DAG(
    dag_id="events_daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    end_date=pendulum.datetime(2025, 1, 5, tz="UTC"),
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="UTC"),
    catchup=True,
    max_active_runs=2,
):
```

### Задания

**1. Первый run.** Дневное interval-расписание, `start_date` 2025-01-01. Когда стартует первый run и чему равен его `data_interval_end`?

<details>
<summary>Решение</summary>

Первый run стартует 2025-01-02 00:00 и обрабатывает интервал от 2025-01-01 до 2025-01-02. `data_interval_end` равен 2025-01-02 00:00. Проверено скриптом `ch03_timetables.py`.

</details>

**2. Раз в два дня.** `DeltaTriggerTimetable(pendulum.duration(days=2))`, `start_date` 2025-01-01. В какие даты пойдут runs?

<details>
<summary>Решение</summary>

Runs пойдут 1, 3 и 5 января: первый в сам `start_date`, дальше каждые два дня. Проверено скриптом `ch03_timetables.py`.

</details>

**3. Дубли.** Task дописывает события в общий `events.json`, и после `clear` там дубли. Как исправить?

<details>
<summary>Решение</summary>

Писать в файл своего интервала, например `events/{{ data_interval_start | ds }}.json`, и перезаписывать его. Тогда повтор даёт тот же файл. Для базы используйте upsert. Так ведёт себя `partition` в скрипте `ch03_idempotent.py`.

</details>

## Вопросы для самопроверки

1. Чем trigger timetable отличается от data interval timetable? Когда стартует run в каждом случае?
2. Что изменилось в Airflow 3 для `schedule="@daily"` и для `catchup`?
3. Почему cron не умеет «каждые два дня» и что использовать вместо него?
4. Чем опасен backfill на год без `max_active_runs`?
5. Приведите пример неатомарной и неидемпотентной task. Как исправить обе?

Предыдущая: [Анатомия DAG](/book-summaries/engineering/data-pipelines-with-apache-airflow/02-anatomy-of-dag/). Следующая: [Asset-aware scheduling](/book-summaries/engineering/data-pipelines-with-apache-airflow/04-asset-aware-scheduling/).
