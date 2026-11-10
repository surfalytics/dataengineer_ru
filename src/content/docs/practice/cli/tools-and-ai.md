---
title: "CLI-инструменты и AI-агенты"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "CLI-инструменты данных и AI-агенты в терминале | Инжиниринг Данных"
description: "У каждого инструмента данных есть CLI: dbt, aws, gcloud, snow, duckdb. Как разобраться в команде, поставить её и работать с AI-агентами."
sidebar:
  order: 12
tags:
  - cli
  - practice
  - ai
---

Всё, что вы выучили, нужно для одного: уверенно работать с инструментами данных. У каждого из них есть CLI. И AI-агенты для разработки тоже живут в терминале.

## У каждого инструмента есть CLI

| Инструмент | Команда | Пример |
|---|---|---|
| dbt | `dbt` | `dbt run --select marts` |
| AWS | `aws` | `aws s3 ls s3://my-bucket/raw/` |
| Google Cloud | `gcloud`, `bq` | `bq query "SELECT 1"` |
| Azure | `az` | `az storage blob list ...` |
| Snowflake | `snow` | `snow sql -q "SELECT current_role()"` |
| Yandex Cloud | `yc` | `yc compute instance list` |
| DuckDB | `duckdb` | `duckdb -c "SELECT ..."` |
| PostgreSQL | `psql` | `psql -h localhost -U analyst analytics` |
| Docker | `docker` | `docker compose up -d` |
| Airflow | `airflow` | `airflow dags list` |
| Terraform | `terraform` | `terraform plan` |
| GitHub | `gh` | `gh pr list` |

Через CLI работать быстрее, чем через веб-консоль. И команду можно положить в скрипт или в CI.

## Как разобраться в любой команде

```bash
duckdb --help      # короткая справка, есть почти у всех программ
man ls             # полное руководство (macOS, WSL, Linux). Выйти — q
dbt run --help     # справка по подкоманде
aws s3 help        # у aws справка устроена так
```

`--version` показывает версию. С неё начинают, когда что-то не работает: «у меня dbt 1.8, а в инструкции 1.10».

## Как ставить инструменты

| Система | Менеджер пакетов | Пример |
|---|---|---|
| macOS | [Homebrew](https://brew.sh/) | `brew install duckdb` |
| WSL, Ubuntu | `apt` | `sudo apt install -y postgresql-client` |
| Windows | `winget` | `winget install DuckDB.cli` |
| Python-инструменты | `pip` или `uv` | `uv tool install dbt-core` |

После установки откройте новое окно терминала. Если команда не находится — проверьте `PATH` (урок [Переменные и PATH](/practice/cli/variables/)).

## AI-агенты в терминале

Агенты для разработки работают прямо в терминале:

- **Claude Code** — команда `claude`. Курс: [Claude Code 101](/ai/claude-code-101/).
- **Codex** — команда `codex`. Курс: [Codex 101](/ai/codex-101/).
- **Gemini CLI**, **OpenCode** и другие открытые агенты. Курс: [Открытые агенты 101](/ai/open-agents-101/).

Агент читает файлы, запускает `grep`, `dbt run`, `git`, `docker` и сам чинит ошибки. Перед опасной командой он спрашивает разрешение:

```
Allow command: rm -rf data/raw ?
```

Чтобы ответить «да» или «нет», нужно понимать, что делает команда. Поэтому CLI нужен и тем, кто работает с агентами. Он нужен им даже больше.

## Запуск по расписанию: cron

На сервере скрипты запускают по расписанию через **cron**:

```bash
crontab -e    # открыть своё расписание
crontab -l    # показать его
```

Строка в расписании:

```
0 2 * * * cd ~/project && dbt run >> ~/dbt.log 2>&1
```

- `0 2 * * *` — минута, час, день месяца, месяц, день недели. Здесь: каждый день в 02:00.
- `>> ~/dbt.log` — дописать вывод в лог.
- `2>&1` — ошибки тоже в лог, а не в никуда.

В компаниях вместо cron обычно берут Airflow или Dagster. Но cron понимать нужно: он есть на любом сервере.

## Практика

Все задания — в папке `~/cli-practice`. Для заданий 2–5 нужен DuckDB. Не ставили? Инструкция в курсе SQL: [Установка DuckDB](/practice/sql/setup/).

### Задание 1

Посмотрите справку `curl`. Найдите в ней, что делает флаг `-o`.

**Проверка:** `-o, --output <file>` — записать вывод в файл, а не на экран.

<details>
<summary>Решение</summary>

```bash
curl --help | grep -- "-o,"
```

`--` говорит `grep`, что дальше идёт текст для поиска, а не его опции.

</details>

### Задание 2

Проверьте, что DuckDB установлен. Где лежит программа и какая у неё версия?

**Проверка:** путь к программе, например `/opt/homebrew/bin/duckdb`, и версия вида `v1.4.3`.

<details>
<summary>Решение</summary>

```bash
which duckdb
duckdb --version
```

</details>

### Задание 3

Посчитайте заказы марта по статусам SQL-запросом прямо к CSV. Используйте `duckdb -c "..."`. Сравните с ответом из урока [grep и конвейеры](/practice/cli/grep-pipes/).

**Проверка:** `completed` — 22, `cancelled` — 4, `refunded` — 2. Как и через `cut | sort | uniq -c`.

<details>
<summary>Решение</summary>

```bash
duckdb -c "SELECT status, count(*) AS orders FROM 'data/sales_2024-03.csv' GROUP BY status ORDER BY orders DESC"
```

DuckDB читает CSV сам: находит заголовок, разделитель и типы столбцов.

</details>

### Задание 4

Сколько выполненных (`completed`) заказов за все три месяца и на какую сумму? Прочитайте все файлы продаж одним шаблоном.

**Проверка:** 58 заказов на 14906.18.

<details>
<summary>Решение</summary>

```bash
duckdb -c "SELECT count(*) AS orders, round(sum(amount), 2) AS revenue FROM 'data/sales_*.csv' WHERE status = 'completed'"
```

</details>

### Задание 5

Посчитайте выручку выполненных заказов по странам: соедините продажи с `data/customers.csv`. Сохраните результат в файл `revenue_by_country.csv`. Используйте флаг `-csv` и `>`.

**Проверка:** `cat revenue_by_country.csv` показывает:

```
country,orders,revenue
Russia,30,8753.52
Serbia,12,2681.76
Kazakhstan,7,1508.94
Armenia,6,1101.52
Georgia,3,860.44
```

<details>
<summary>Решение</summary>

```bash
duckdb -csv -c "SELECT c.country, count(*) AS orders, round(sum(s.amount), 2) AS revenue FROM 'data/sales_*.csv' s JOIN 'data/customers.csv' c USING (customer_id) WHERE s.status = 'completed' GROUP BY c.country ORDER BY revenue DESC" > revenue_by_country.csv
cat revenue_by_country.csv
rm revenue_by_country.csv
```

Так собирают маленький отчёт одной командой. Её можно положить в скрипт и запускать через cron.

</details>

Дальше: [Итоговая практика](/practice/cli/final/).
