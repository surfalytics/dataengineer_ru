---
title: CI/CD
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "CI/CD для инженера данных: Actions и GitLab CI | Инжиниринг Данных"
description: "Что такое CI и CD, зачем они инженеру данных и как настроить автоматическую проверку SQL в GitHub Actions и GitLab CI, чтобы не сломать продакшен."
sidebar:
  order: 6
tags:
  - git
  - ci-cd
  - github
  - gitlab
  - practice
---

## Что такое CI/CD

- **CI** (Continuous Integration) — автоматические проверки. При каждом изменении сервер сам запускает тесты и линтер.
- **CD** (Continuous Delivery / Deployment) — автоматическая выкладка. После проверок и merge код сам попадает в продакшен.

Без CI проверка зависит от человека. Кто-то забыл запустить тест. Кто-то не заметил дубли. С CI проверка работает каждый раз, одинаково.

## Зачем это инженеру данных

- **Не сломать продакшен.** Битый SQL не дойдёт до `main`. Красный CI блокирует merge.
- **Каждая версия хранится в Git.** Любое изменение можно найти и откатить.
- **Коллеги смотрят код.** Они видят diff, результаты проверок и пишут замечания.
- **Проверки делает машина.** Человек в ревью думает о логике, а не о запятых и стиле.

Путь изменения выглядит так:

```
push в ветку → CI: линтер + тесты → ревью коллег → merge в main → CD: выкладка
                  │ красный? merge закрыт
```

## Что проверять в проекте с SQL

Начните с малого. Две проверки закрывают большую часть проблем:

| Проверка | Инструмент | Что ловит |
|---|---|---|
| **Линтер** | `sqlfluff` | Ошибки синтаксиса и разный стиль SQL |
| **Тесты** | Python + DuckDB (или `dbt test`) | Запрос ничего не вернул, в данных дубли или отрицательные суммы |

Для dbt-проектов обычно запускают `dbt build` на тестовых данных. Глубже в это не идём. С опытом вы добавите свои проверки.

### Пример теста

Файл `tests/test_revenue.py` запускает запрос на маленьком CSV и проверяет результат:

```python
import duckdb

con = duckdb.connect()
con.execute("create table orders as select * from 'data/orders.csv'")
rows = con.execute(open("models/revenue.sql").read()).fetchall()

assert len(rows) > 0, "revenue model returns no rows"
assert all(amount >= 0 for _, amount in rows), "negative amount"
print("OK:", len(rows), "rows")
```

Файл `data/orders.csv` — маленький тестовый набор:

```csv
order_id,amount,status
1,100,completed
2,50,cancelled
3,70,completed
```

Этот файл маленький, поэтому его хранят в Git. CI берёт данные из репозитория.

Локально проверка запускается так:

```bash
pip install duckdb sqlfluff
sqlfluff lint models --dialect duckdb
python tests/test_revenue.py
```

## GitHub Actions

Создайте файл `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install duckdb sqlfluff
      - name: Lint SQL
        run: sqlfluff lint models --dialect duckdb
      - name: Test models
        run: python tests/test_revenue.py
```

Как читать файл:

- `on` — когда запускать: при каждом Pull Request и при push в `main`.
- `jobs` — что делать. Здесь одна задача `checks`.
- `steps` — шаги по порядку: забрать код, поставить Python, поставить пакеты, линтер, тест.

Если любой шаг падает, проверка красная. В Pull Request появляется красный крестик.

## GitLab CI

То же самое для GitLab. Файл `.gitlab-ci.yml` в корне репозитория:

```yaml
image: python:3.12

stages:
  - check

checks:
  stage: check
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - pip install duckdb sqlfluff
    - sqlfluff lint models --dialect duckdb
    - python tests/test_revenue.py
```

Идея та же. Меняется только формат файла.

| | GitHub Actions | GitLab CI |
|---|---|---|
| Файл | `.github/workflows/ci.yml` | `.gitlab-ci.yml` |
| Запуск | `on:` | `rules:` |
| Шаги | `steps:` | `script:` |
| Где смотреть результат | Вкладка Actions и статус в PR | Раздел Pipelines и статус в MR |

## Защитите main

CI бесполезен, если его можно обойти. Включите защиту ветки `main`:

- **GitHub:** Settings → Branches → Add branch ruleset. Включите **Require a pull request before merging** и **Require status checks to pass**.
- **GitLab:** Settings → Repository → Protected branches. В Settings → Merge requests включите **Pipelines must succeed**.

После этого напрямую в `main` писать нельзя. Только через PR или MR с зелёным CI и approve.

## CD: выкладка

CD — следующий шаг. После merge в `main` пайплайн сам выкладывает изменения. Что именно выкладывается, зависит от проекта:

| Проект | Что делает CD |
|---|---|
| Airflow | Копирует DAG на сервер или в облако |
| dbt | Запускает `dbt build` на продакшен-схеме |
| Terraform | Применяет изменения инфраструктуры |
| Docker | Собирает образ и выкладывает его |

На старте CD не нужен. Сначала настройте хороший CI. Для CD понадобятся секреты (пароли и ключи). Их хранят в **Secrets** платформы (`Settings → Secrets`), а не в коде.

<br />

:::caution
Не пишите пароли и ключи прямо в `ci.yml`. Файл виден всем, у кого есть доступ к репозиторию, и остаётся в истории.
:::

## Практика

### Задание 1

Добавьте в `sql-reports` файлы `data/orders.csv` и `tests/test_revenue.py` из урока. Запустите проверки локально.

**Проверка:** `python tests/test_revenue.py` печатает `OK: 2 rows`. `sqlfluff lint` не показывает ошибок.

Если `sqlfluff` ругается на стиль, поправьте `models/revenue.sql` или запустите `sqlfluff fix models --dialect duckdb`.

<details>
<summary>Подсказка</summary>

Хороший вид запроса для `sqlfluff`:

```sql
select
    order_id,
    amount
from orders
where status = 'completed'
```

</details>

### Задание 2

Добавьте `.github/workflows/ci.yml`. Сделайте новую ветку, коммит и Pull Request.

**Проверка:** на странице Pull Request есть проверка `checks`, и она зелёная.

<details>
<summary>Решение</summary>

```bash
git switch -c add-ci
mkdir -p .github/workflows
# создайте ci.yml с текстом из урока
git add .github tests data
git commit -m "Add CI with sqlfluff and tests"
git push -u origin add-ci
```

Затем откройте Pull Request на GitHub.

</details>

### Задание 3. Сломайте проверку

В ветке сделайте ошибку: измените запрос так, чтобы в нём не осталось строк, например `where status = 'unknown'`. Сделайте коммит и `git push`.

**Проверка:** проверка в Pull Request стала красной. В логе видно `revenue model returns no rows`.

Верните правильный запрос, сделайте коммит и push. Проверка снова зелёная.

<details>
<summary>Решение</summary>

```bash
# правим models/revenue.sql
git commit -am "Break filter on purpose"
git push
# смотрим красный CI, затем возвращаем:
git revert HEAD --no-edit
git push
```

</details>

### Задание 4. Защита main

Включите правило защиты `main`: только через Pull Request и только с зелёной проверкой.

**Проверка:** `git push origin main` напрямую отклоняется.

### Задание 5. GitLab

Скопируйте тот же проект в GitLab. Добавьте `.gitlab-ci.yml` из урока. Откройте Merge Request.

**Проверка:** в Merge Request виден зелёный pipeline.
