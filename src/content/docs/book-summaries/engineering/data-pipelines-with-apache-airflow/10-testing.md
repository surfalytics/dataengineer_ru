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

## О чём глава

Как убедиться, что код верен до выкладки в production? Нужно проверить и обычный сценарий (`happy flow`), и крайние случаи. Прошлая тема: [свои операторы и sensors](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/).

![Пайплайн CI/CD для Airflow: проверки стиля, DAG integrity test, unit и integration тесты, затем merge](/assets/data-pipelines-with-apache-airflow/ch10-ci-pipeline.png)

## Уровни тестов

| Уровень | Что проверяет |
|---|---|
| Unit test | Одну функцию или один оператор |
| Integration test | Несколько компонентов вместе |
| Acceptance test | Соответствие требованиям бизнеса. В главе его нет |

Unit-тест не покажет, как ведёт себя система из нескольких частей. Для этого нужен integration test. В книге тесты написаны на `pytest`. Его главная сила: `fixtures`. Они готовят и убирают окружение теста.

## DAG integrity test

Это первый тест любого проекта Airflow. Идея пришла из статьи «Data's Inferno: 7 Circles of Data Testing Hell with Airflow». Тест загружает все DAG и ищет простые ошибки.

- цикл в графе (`t1 >> t2 >> t3 >> t1`);
- одинаковые `task_id`. Частый случай: задачи в цикле `for` с фиксированным id;
- у оператора нет обязательного аргумента, например `bash_command` у `BashOperator`;
- файл в папке `dags/` не содержит ни одного DAG.

Airflow проверяет это сам и показывает ошибку в интерфейсе. Но лучше узнать об ошибке до deploy.

### Структура проекта

Папка `tests/` повторяет структуру кода. Тест для `movielens_operator.py` лежит в `test_movielens_operator.py`. Префикс `test_` обязателен: pytest ищет файлы по нему. Файлов `__init__.py` в `tests/` нет: тесты запускаются независимо.

### Как работает тест

- Он ищет `dags/**/*.py`, в том числе во вложенных папках.
- `@pytest.mark.parametrize` запускает проверку для каждого найденного файла.
- Загружает файл `DagBag`. Это объект Airflow, который читает DAG из файлов.
- `DagBag` сам ловит ошибки и пишет их в лог. Тест читает лог (fixture `caplog`) и повторно поднимает исходную ошибку. Если лог говорит, что в файле нет DAG, тест падает.
- Из-за последней проверки в `dags/` нельзя держать утилиты без DAG. Зато папка только для DAG даёт чёткое разделение.
- Можно добавить свои правила. Например, имя DAG должно начинаться с `import` или `export`.

Тесты запускают командой `pytest tests/`. В выводе смотрите начало (какой тест упал) и конец (почему).

<details>
<summary>Код: ch10_integrity_test.py</summary>

```python
"""DAG integrity test: проверяет каждый файл в папке dags/.
Это тест для pytest. Запуск как скрипта показывает работу на трёх тестовых DAG."""
import contextlib
import os
import sys
import tempfile
from pathlib import Path

from airflow.models import DagBag


def check_file(dag_file):
    """Возвращает текст ошибки или None, если файл в порядке."""
    bag = DagBag(dag_folder=str(dag_file))
    if bag.import_errors:
        return "; ".join(msg.strip().splitlines()[-1] for msg in bag.import_errors.values())
    if not bag.dags:
        return "в файле нет DAG"
    return None


# pytest берёт файлы из папки dags/ рядом с tests/
try:
    import pytest
    DAG_FILES = sorted((Path(__file__).parent.parent / "dags").rglob("*.py"))

    @pytest.mark.parametrize("dag_file", DAG_FILES, ids=str)
    def test_dag_loads(dag_file):
        assert check_file(dag_file) is None
except ImportError:
    pass

@contextlib.contextmanager
def quiet():
    """Прячет вывод логов Airflow (на уровне файловых дескрипторов)."""
    sys.stdout.flush()
    saved = os.dup(1), os.dup(2)
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, 1), os.dup2(null, 2)
    try:
        yield
    finally:
        os.dup2(saved[0], 1), os.dup2(saved[1], 2)
        for fd in (*saved, null):
            os.close(fd)


GOOD = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
with DAG("good", schedule=None):
    EmptyOperator(task_id="a") >> EmptyOperator(task_id="b")
'''
CYCLE = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
with DAG("cycle", schedule=None):
    t1, t2, t3 = (EmptyOperator(task_id=f"t{i}") for i in (1, 2, 3))
    t1 >> t2 >> t3 >> t1
'''
NO_COMMAND = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
with DAG("no_command", schedule=None):
    BashOperator(task_id="this_should_fail")
'''
HELPER = "def util():\n    return 1\n"

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        for name, code in [("good.py", GOOD), ("cycle.py", CYCLE),
                           ("no_command.py", NO_COMMAND), ("helper.py", HELPER)]:
            path = Path(tmp) / name
            path.write_text(code)
            with quiet():
                result = check_file(path)  # DagBag пишет трассировки в лог, прячем их
            print(f"{name:14} -> {result or 'ok'}")
    sys.exit(0)
```

</details>

Скрипт проверяет четыре файла. Вот его настоящий вывод.

```text
good.py        -> ok
cycle.py       -> AirflowDagCycleException: Cycle detected in Dag: cycle. Faulty task: t3
no_command.py  -> TypeError: missing keyword argument 'bash_command'
helper.py      -> в файле нет DAG
```

Ошибки те же, что в книге: цикл на `t3` и пропущенный `bash_command`.

## CI/CD

CI/CD запускает скрипты при каждом изменении репозитория. `CI` проверяет, что код соответствует стандартам и проходит тесты (Flake8, Pylint, Black, потом pytest). `CD` выкладывает код в production автоматически.

Все популярные системы (GitHub Actions, GitLab, Bitbucket, Azure DevOps) работают одинаково: pipeline описан в YAML в корне проекта. У GitHub Actions файлы лежат в `.github/workflows/`.

- Каждый шаг должен пройти. Если один упал, pipeline красный.
- Строка `on: [push]` запускает pipeline при каждом push.
- В Git можно запретить merge в главную ветку без зелёного pipeline.
- CD обычно включают только для главной ветки: шаги deploy идут, если pipeline на ней успешен.

```yaml
# .github/workflows/ci.yaml (не запускали: нужен репозиторий на GitHub)
name: Python static checks and tests
on: [push]
jobs:
  testing:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: "3.12" }
      - run: pip install flake8 black apache-airflow pytest
      - run: flake8
      - run: black --check .
      - run: pytest tests/
```

## Unit-тесты операторов

Книга берёт `MovielensPopularityOperator`: он получает рейтинги из MovieLens API и возвращает top N фильмов за период. Проверять надо и верные, и неверные данные. Например, что будет при отрицательном `batch_size`?

Оператор можно запустить без Airflow. Создайте объект и вызовите `execute(context={})`. Это самая низкая функция, которую реализует каждый оператор. Перед ней Airflow делает render шаблонов и готовит context. В тесте этого нет. Если оператору нужен context, заполните словарь вручную.

### Mock

Первый запуск падает: нужен аргумент `conn_id`, ссылка на connection в metastore. В тесте metastore нет. Тесты должны быть изолированы, общая БД не подходит.

Решение: **mock**. Вы подменяете вызов и возвращаете готовое значение. Цена: нужно знать внутренности того, что тестируете.

- Пакет `pytest-mock` даёт fixture `mocker`.
- `mocker.patch.object(Hook, "get_connection", return_value=Connection(...))` подменяет метод на время теста. Это monkey patch.
- Результат патча можно сохранить в переменную. Тогда видно, сколько раз метод вызвали (`call_count`) и с какими аргументами (`assert_called_with`). Для обеих проверок есть `assert_called_once_with()`.
- **Частая ошибка:** патчить там, где метод определён. Патчить нужно там, где его вызывают. `get_connection` определён в `BaseHook`, но оператор вызывает его на своём hook. Значит, патчите класс вашего hook.

![Где ставить mock: на классе hook, который вызывает оператор, а не на BaseHook](/assets/data-pipelines-with-apache-airflow/ch10-where-to-patch.png)

<details>
<summary>Код: ch10_operator_test.py</summary>

```python
"""Unit-тест оператора с mock. Hook и operator в одном файле, чтобы пример запускался сам."""
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


if __name__ == "__main__":
    import os
    import sys

    sys.stdout.flush()
    saved = os.dup(1)
    os.dup2(os.open(os.devnull, os.O_WRONLY), 1)  # прячем предупреждения Airflow про вызов вне Task Runner
    try:
        test_report_operator_calls_api_once()
        try:
            ReportOperator(task_id="r2", conn_id="api").execute(context={})
            error = None
        except RuntimeError as e:
            error = e
    finally:
        os.dup2(saved, 1)
    print("test_report_operator_calls_api_once: passed")
    print("без mock оператор упал:", error)
```

</details>

```text
test_report_operator_calls_api_once: passed
без mock оператор упал: В тесте сюда ходить нельзя
```

### Файлы на диске

Для оператора, который читает и пишет файлы, нужна временная папка. Pytest даёт её через fixtures `tmp_path` (объект `pathlib`) и `tmp_dir` (объект `os.path`). После теста папка стирается.

В книге оператор `JsonToCsvOperator` читает JSON и пишет CSV. Тест кладёт входной JSON в `tmp_path`, запускает оператор, читает CSV и сравнивает с входом. Fixture похожа на `setUp()` и `tearDown()` из `unittest`, но гибче. По умолчанию её область (`scope`) это одна функция: в каждом тесте новая папка.

## Внешние системы и Docker

Теперь оператор `MovielensToPostgresOperator`. Источник отдаёт данные «как сейчас» и не хранит историю. Поэтому раз в день Airflow забирает все данные и сохраняет их со временем записи. Оператор превращает рейтинги в `INSERT`-запросы для PostgreSQL.

Продовую БД с ноутбука не трогаем, но легко поднять PostgreSQL в Docker. Контейнер даёт настоящие методы hooks, без mock.

- Пакет `pytest-docker-tools` даёт fixtures `fetch` (скачать образ, это `docker pull`) и `container` (запустить его). Нужен Docker.
- Порт в `ports={"5432/tcp": None}` оставляют `None`. Docker выберет свободный порт, как `docker run -P`. Номер лежит в `container.ports`.
- Начальный SQL кладут через `volumes` в `/docker-entrypoint-initdb.d/`. Образ PostgreSQL выполнит его при старте.
- Тест делает три шага: проверяет, что таблица пуста, запускает оператор, проверяет, что строки появились.
- Контейнер стартует за пару секунд, после теста его останавливают.
- Mock всё равно нужен для того, что в контейнер не положить: например, для MovieLens API. Для `PostgresHook` подменяют `get_connection`, чтобы он вёл на контейнер.

![Что подставить вместо внешней системы: mock или контейнер](/assets/data-pipelines-with-apache-airflow/ch10-mock-or-docker.png)

## Тесты для разработки

Тесты помогают и при разработке. Поставьте breakpoint в `execute()`, запустите тест в режиме debug и смотрите значения переменных. Подойдёт любая IDE.

Если код падает только на сервере, а IDE нет, помогают такие способы:

- `breakpoint()` (с Python 3.7) или `import pdb; pdb.set_trace()` прямо в коде. В `pdb` команда `n` выполняет строку, `l` показывает соседние строки;
- команда `airflow tasks test <dag_id> <task_id> <дата>`. Она запускает одну задачу и не пишет записи в metastore. Её удобно использовать на production.

## Тест целого DAG

Один оператор может работать верно, а связка сломаться: первый преобразует данные так, что второй падает. Production не всегда можно повторить: мешают приватность и размер данных. Нельзя держать петабайт в четырёх окружениях. В книге три подхода.

![Три способа проверить весь DAG: dag.test(), Whirl и DTAP](/assets/data-pipelines-with-apache-airflow/ch10-whole-dag.png)

| Подход | Идея | Ограничение |
|---|---|---|
| `dag.test()` | Запустить весь DAG из кода или из pytest (с Airflow 2.5.0) | В книге: в Airflow 3.1 пример из-за известной ошибки не работает |
| Whirl | Копия production в Docker Compose с утилитой CLI | Не всё есть как образ, например Google Cloud Storage |
| DTAP | Отдельные окружения dev, test, acceptance, production | Тяжело вести. Малые команды берут два окружения |

### dag.test()

Простой вариант: добавить в конец файла DAG `if __name__ == "__main__": dag.test()`. Тогда `python` выполнит tasks, а не только разберёт файл. Минус: логика DAG смешивается с тестовой. Лучше вызвать `dag.test()` из теста.

- DAG нужно импортировать в тест. Поэтому объявляйте его как переменную `dag = DAG(...)`, а не через `with`.
- Передавайте `logical_date`, чтобы `data_interval` был верным.
- Тест целого DAG ловит и побочные эффекты соседних tasks.
- Главная трудность та же: внешние системы. Путь первый: заменить их mock. Нужно знать, что вернёт каждая, зато ничего внешнего не требуется. Путь второй: эмулировать их, как PostgreSQL выше. Настройка сложнее.

> **Пояснение:** по замечанию автора, на момент книги `dag.test()` в Airflow 3.1 не создавал DAG run из-за открытой ошибки ([issue 56657](https://github.com/apache/airflow/issues/56657)). Мы этот случай не проверяли.

### Whirl и DTAP

Whirl имитирует компоненты production в контейнерах через Docker Compose.

Иногда нельзя повторить production даже локально. Например, FTP-сервер пускает только известные IP. Службе безопасности легче согласовать изолированные окружения DTAP. В них можно держать фиктивные данные.

Заведите ветку Git на каждое окружение: `development`, `main`. Меняйте код в ветке, сливайте в `development` и смотрите DAG в dev. Когда всё хорошо, делайте merge в следующую ветку.

## Итоги главы

- DAG integrity test отсеивает простые ошибки DAG.
- Unit-тест проверяет один оператор. Его запускают через `execute()`.
- pytest и плагины дают временные папки (`tmp_path`), mock (`pytest-mock`) и контейнеры (`pytest-docker-tools`).
- `dag.test()` имитирует запуск целого DAG.
- Для integration-тестов имитируйте production как можно ближе.
- Разные тесты ловят разные ошибки. Перед тестом решите, что именно проверяете.
- Запускайте тесты в CI/CD, чтобы ловить сбои рано.

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
| CI/CD | Автоматические проверки и deploy при изменении репозитория |
| DTAP | Dev, Test, Acceptance, Production |
| Whirl | Инструмент для копии production в Docker |

## Что это значит на практике

- Добавьте DAG integrity test в первый же день. Он дешёвый и ловит много ошибок.
- Запускайте `ruff` или `flake8`, `black --check` и `pytest` в CI на каждый push.
- Не лезьте в production-БД из тестов. Подмените connection mock или поднимите БД в контейнере.
- Перед тестом решите, что именно проверяете. От этого зависит тип теста.
- Держите папку `dags/` только для DAG. Утилиты вынесите в другое место.
- Для отладки на сервере используйте `airflow tasks test`.
- Патчите mock на классе вашего hook, а не на `BaseHook`. Иначе оператор вызовет настоящий метод.
- Не ждите от `dag.test()` полной замены production. Он проверяет связку tasks, но внешние системы всё равно нужны.

## Практика

Скрипты работают без запущенного Airflow (Airflow 3.4.0, pytest 9.2.0). Тест с контейнером PostgreSQL мы не запускали: нужен Docker. Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

Скрипты выше: [ch10_integrity_test.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch10_integrity_test.py) и [ch10_operator_test.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch10_operator_test.py). Решения заданий: [ch10_practice_test.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch10_practice_test.py). Тесты проходят в pytest.

### Задания

**1. Правило имён.** Как проверить в integrity test, что имя каждого DAG начинается с `import` или `export`?

<details>
<summary>Решение</summary>

Загрузите файл через `DagBag` и проверьте ключи `bag.dags`:

```python
bad = [d for d in bag.dags if not d.startswith(("import", "export"))]
assert not bad
```

Для DAG `report_daily` список `bad` равен `["report_daily"]`, тест падает. Проверено в pytest.

</details>

**2. Файлы в тесте.** Оператор читает JSON и пишет CSV. Куда сохранить выходной файл в тесте, чтобы после теста ничего не осталось?

<details>
<summary>Решение</summary>

Возьмите fixture `tmp_path`: `def test_json_to_csv(tmp_path): ...`. Положите в неё вход, запустите `execute(context={})` и прочитайте выход. Папка стирается после теста. Проверено в pytest.

</details>

**3. Какой класс патчить?** `MyHook` наследует `get_connection` от `BaseHook`. На каком классе вызвать `mocker.patch.object`?

<details>
<summary>Решение</summary>

На `MyHook`: оператор вызывает метод именно там. Тест `test_patch_on_subclass` в `ch10_practice_test.py` проходит, `assert_called_once_with` подтверждает один вызов.

</details>

## Вопросы для самопроверки

1. Какие ошибки ловит DAG integrity test? Почему его делают первым?
2. Почему `mocker.patch.object` нужно применять к месту вызова, а не к месту определения?
3. Когда лучше взять контейнер PostgreSQL, а когда mock?
4. Чем `dag.test()` отличается от `execute()` одного оператора?

Предыдущая: [Расширение Airflow: свои операторы и sensors](/book-summaries/engineering/data-pipelines-with-apache-airflow/09-custom-operators-sensors/). Следующая: [Запуск задач в контейнерах](/book-summaries/engineering/data-pipelines-with-apache-airflow/11-tasks-in-containers/).
