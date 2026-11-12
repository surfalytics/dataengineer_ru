---
title: "Data Pipelines with Apache Airflow, глава 10: Тестирование"
head:
  - tag: title
    content: "Как тестировать DAG в Airflow: pytest, mock, CI/CD | Инжиниринг Данных"
description: "Конспект главы 10 Data Pipelines with Apache Airflow на русском. DAG integrity test, pytest, mock, Docker в тестах, dag.test(), CI/CD и DTAP."
sidebar:
  order: 10
  label: "10. Тестирование"
tags:
  - books
  - airflow
  - testing
  - ci-cd
---

**Главная мысль:** pipeline зависит от внешних систем, поэтому его трудно тестировать. Это не повод пропускать тесты. Начните с простых проверок DAG, потом добавьте unit-тесты операторов, а внешние системы заменяйте mock или контейнерами. Запускайте всё в CI/CD.

![Пайплайн CI/CD для Airflow: проверки стиля, DAG integrity test, unit и integration тесты, затем merge](/assets/data-pipelines-with-apache-airflow/ch10-ci-pipeline.png)

## Уровни тестов

| Уровень | Что проверяет |
|---|---|
| Unit test | Одну функцию или один оператор |
| Integration test | Несколько компонентов вместе |
| Acceptance test | Соответствие требованиям бизнеса. В главе его нет |

В книге тесты написаны на `pytest`. Его главная сила: `fixtures`. Они готовят и убирают окружение теста.

## DAG integrity test

Это первый тест любого проекта Airflow. Он загружает все файлы DAG и ищет простые ошибки.

- цикл в графе (`t1 >> t2 >> t3 >> t1`);
- одинаковые `task_id`, например при генерации задач в цикле;
- у оператора нет обязательного аргумента;
- файл в папке `dags/` не содержит ни одного DAG.

Как это работает:

- Тест ищет `dags/**/*.py` и запускает проверку для каждого файла (`pytest.mark.parametrize`).
- Для загрузки он использует `DagBag`.
- `DagBag` сам ловит ошибки и пишет их в лог. Тест читает лог и повторно поднимает ошибку.
- Можно добавить свои правила. Например, имя DAG должно начинаться с `import` или `export`.

Структура проекта: папка `tests/` повторяет структуру кода. Файлы называются `test_*.py`. Файлов `__init__.py` в `tests/` нет.

## CI/CD

CI/CD запускает скрипты при каждом изменении репозитория. Конфиг лежит в YAML. В книге это GitHub Actions (`.github/workflows/`), но идея одна для всех систем.

- Шаги: checkout, установка Python, `flake8`, `pylint`, `black --check`, `pytest`.
- Каждый шаг должен пройти. Если один упал, pipeline красный.
- В Git можно запретить merge без зелёного pipeline.
- CD (автоматический deploy) обычно включают только для главной ветки.

## Unit-тесты операторов

Оператор можно запустить без Airflow. Создайте объект и вызовите `execute(context={})`. Это самая низкая функция, которую реализует каждый оператор. Перед ней Airflow делает render шаблонов и готовит context. В тесте этого нет. Если оператору нужен context, заполните словарь вручную.

Проблема: оператор часто хочет connection из metastore. В тесте metastore нет. Тесты должны быть изолированы, общая БД не подходит.

Решение: **mock**. Вы подменяете вызов и возвращаете готовое значение.

- Пакет `pytest-mock` даёт fixture `mocker`.
- `mocker.patch.object(Hook, "get_connection", return_value=Connection(...))` подменяет метод.
- Результат патча можно сохранить в переменную. Тогда видно, сколько раз метод вызвали (`call_count`) и с какими аргументами (`assert_called_once_with`).
- **Частая ошибка:** патчить там, где метод определён. Патчить нужно там, где его вызывают. Если hook наследует `get_connection` от `BaseHook`, патчите на классе вашего hook.

### Файлы на диске

Для оператора, который читает и пишет файлы, используйте `tmp_path`. Это fixture pytest. Она даёт временную папку, которая стирается после теста.

## Внешние системы и Docker

Если оператор пишет в PostgreSQL, лучше проверить его на настоящей БД. Mock там слабо помогает.

- Пакет `pytest-docker-tools` даёт fixtures `fetch` (скачать образ) и `container` (запустить его).
- Порт контейнера можно оставить `None`. Тогда Docker выберет свободный порт. Это защищает от конфликтов.
- Начальный SQL кладут в `/docker-entrypoint-initdb.d/` через volume.
- Тест делает три шага: проверяет, что таблица пуста, запускает оператор, проверяет, что строки появились.
- После теста fixture останавливает контейнер.
- Mock всё равно нужен для того, что в контейнер не положить: например, API источника.

![Что подставить вместо внешней системы: mock или контейнер](/assets/data-pipelines-with-apache-airflow/ch10-mock-or-docker.png)

## Тесты для разработки

Тест удобно запускать под отладчиком. Поставьте breakpoint в `execute()`, запустите тест в режиме debug и смотрите значения переменных.

На сервере, где нет IDE, помогают такие способы:

- `breakpoint()` или `pdb.set_trace()` прямо в коде;
- команда `airflow tasks test <dag_id> <task_id> <дата>`. Она запускает одну задачу и не пишет записи в metastore.

## Тест целого DAG

Один оператор может работать верно, а связка из нескольких может сломаться. Для целого DAG есть три подхода.

| Подход | Идея | Ограничение |
|---|---|---|
| `dag.test()` | Запустить весь DAG из кода или из pytest | В книге сказано: в Airflow 3.1 пример из-за известной ошибки не работает |
| Whirl | Копия production в Docker Compose | Не всё есть как образ, например Google Cloud Storage |
| DTAP | Отдельные окружения dev, test, acceptance, production | Тяжело вести. Малые команды берут два окружения |

Детали про `dag.test()`:

- В тесте DAG нужно импортировать. Поэтому объявляйте его как переменную `dag = DAG(...)`, а не через `with`.
- Передавайте `logical_date`, чтобы `data_interval` был верным.
- Тест всего DAG ловит и побочные эффекты соседних задач.

Для DTAP заведите ветку Git на каждое окружение: `development`, `main`. Меняйте код в ветке, смотрите результат в окружении, потом делайте merge дальше.

## Пример кода

Проверено на Airflow 3.4: оба теста проходят в pytest.

Мини-версия DAG integrity test. Имена здесь свои, это не код из книги.

```python
from pathlib import Path

import pytest
from airflow.models import DagBag

DAGS_DIR = Path(__file__).parent.parent / "dags"
DAG_FILES = sorted(DAGS_DIR.rglob("*.py"))


@pytest.mark.parametrize("dag_file", DAG_FILES, ids=str)
def test_dag_loads(dag_file):
    bag = DagBag(dag_folder=str(dag_file))
    assert not bag.import_errors, bag.import_errors
    assert bag.dags, f"В файле {dag_file} нет DAG"
```

Unit-тест оператора с mock. Hook и operator лежат в том же файле, чтобы пример запускался сам по себе. В проекте они будут в своих модулях.

```python
from unittest import mock

from airflow.sdk import BaseHook, BaseOperator


class ApiHook(BaseHook):
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id

    def fetch(self):
        raise RuntimeError("В тесте сюда ходить нельзя")


class ReportOperator(BaseOperator):
    def __init__(self, conn_id, **kwargs):
        super().__init__(**kwargs)
        self.conn_id = conn_id

    def execute(self, context):
        return len(ApiHook(self.conn_id).fetch())


def test_report_operator_calls_api_once():
    with mock.patch.object(ApiHook, "fetch", return_value=[1, 2, 3]) as fake:
        op = ReportOperator(task_id="report", conn_id="api")
        result = op.execute(context={})

    fake.assert_called_once()
    assert result == 3
```

## Ключевые термины

| Термин | Значение |
|---|---|
| DAG integrity test | Тест, который загружает все DAG и ищет ошибки |
| `DagBag` | Объект Airflow, который читает DAG из файлов |
| `fixture` | Подготовка и уборка окружения в pytest |
| `mock` | Подмена вызова готовым ответом |
| `tmp_path` | Временная папка для теста |
| `execute()` | Метод оператора, который делает работу |
| `dag.test()` | Запуск целого DAG из кода |
| DTAP | Dev, Test, Acceptance, Production |
| Whirl | Инструмент для копии production в Docker |

## Что это значит на практике

- Добавьте DAG integrity test в первый же день. Он дешёвый и ловит много ошибок.
- Запускайте `ruff` или `flake8`, `black --check` и `pytest` в CI на каждый push.
- Не лезьте в production-БД из тестов. Подмените connection mock или поднимите БД в контейнере.
- Перед тестом решите, что именно проверяете. От этого зависит тип теста.
- Держите папку `dags/` только для DAG. Утилиты вынесите в другое место.
- Для отладки на сервере используйте `airflow tasks test`.

## Вопросы для самопроверки

1. Какие ошибки ловит DAG integrity test? Почему его делают первым?
2. Почему `mocker.patch.object` нужно применять к месту вызова, а не к месту определения?
3. Когда лучше взять контейнер PostgreSQL, а когда mock?
4. Чем `dag.test()` отличается от `execute()` одного оператора?

Предыдущая: [Расширение Airflow: свои операторы и sensors](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/). Следующая: [Запуск задач в контейнерах](/book-summaries/engineering/data-pipelines-with-apache-airflow/11-tasks-in-containers/).
