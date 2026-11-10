---
title: "Права, скрипты и архивы"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Права файлов, chmod, sudo, tar и curl | Инжиниринг Данных"
description: "Как читать права файлов, менять их через chmod, запускать bash-скрипты, работать через sudo, упаковывать файлы в tar.gz и скачивать их через curl."
sidebar:
  order: 10
tags:
  - cli
  - practice
---

Последний набор основ: кто может читать и запускать файл, как запустить скрипт, как упаковать и скачать файлы.

## Права файлов

`ls -l` показывает права в начале строки:

```bash
ls -l scripts/report.sh
```

```
-rw-r--r--  1 maria  staff  198 Apr  1  2024 scripts/report.sh
```

Разберём `-rw-r--r--`:

- Первый символ — тип: `-` файл, `d` папка, `l` ссылка.
- Дальше три тройки: права **владельца**, **группы** и **всех остальных**.
- `r` — читать, `w` — менять, `x` — запускать. `-` — права нет.

Здесь владелец может читать и менять файл. Остальные — только читать. Запускать не может никто.

## chmod — поменять права

Права удобно задавать тремя цифрами: владелец, группа, остальные. `r` = 4, `w` = 2, `x` = 1, складываем.

| Режим | Права | Для чего |
|---|---|---|
| `644` | `rw-r--r--` | Обычные файлы |
| `600` | `rw-------` | Секреты: `.env`, SSH-ключи. Только владелец |
| `755` | `rwxr-xr-x` | Скрипты и папки |
| `700` | `rwx------` | Личные папки, например `~/.ssh` |

```bash
chmod 600 config/app.env      # только я могу читать пароли
chmod +x scripts/report.sh    # разрешить запуск
```

С правами вы встретитесь, когда SSH откажется брать ключ: `UNPROTECTED PRIVATE KEY FILE`. Лечится так: `chmod 600 ~/.ssh/ваш_ключ`. Подробнее — в уроке [SSH и ключи](/practice/cli/ssh-keys/).

:::note[Git Bash]
В Git Bash `chmod` почти ничего не меняет: Windows хранит права по-своему. Скрипты с первой строкой `#!` Git Bash и так считает запускаемыми. В WSL, macOS и Linux всё работает как в уроке.
:::

## Скрипты

Скрипт — файл с командами. Первая строка говорит, какой программой его выполнять:

```bash
cat scripts/report.sh
```

```bash
#!/usr/bin/env bash
# Считает число заказов в каждом файле продаж.
for f in data/sales_*.csv; do
  echo "$f: $(tail -n +2 "$f" | wc -l | tr -d ' ') orders"
done
```

Строка `#!/usr/bin/env bash` называется **shebang**. Запустить скрипт можно двумя способами:

```bash
bash scripts/report.sh    # работает всегда
./scripts/report.sh       # нужно право x
```

`./` в начале значит «файл в текущей папке». Без него shell будет искать `scripts/report.sh` как команду.

## sudo — от имени администратора

`sudo` запускает одну команду от имени **root**. Нужен, чтобы ставить программы и менять системные файлы:

```bash
sudo apt install -y htop       # WSL, Ubuntu
```

Shell попросит ваш пароль. Символы при вводе не видны. Это нормально.

- В WSL и Linux `sudo` есть.
- На macOS программы обычно ставят через [Homebrew](https://brew.sh/) без `sudo`: `brew install htop`.
- В Git Bash `sudo` нет.

:::danger
`sudo rm -r` по ошибке может удалить систему. Перечитайте команду перед Enter.
:::

## Архивы: tar и gzip

```bash
tar czf logs.tar.gz logs     # упаковать папку logs в архив
tar tzf logs.tar.gz          # посмотреть, что внутри, не распаковывая
tar xzf logs.tar.gz          # распаковать
gzip big.csv                 # сжать один файл → big.csv.gz
gunzip big.csv.gz            # распаковать
```

Буквы в `tar`: `c` — create, `x` — extract, `t` — list, `z` — сжать через gzip, `f` — имя файла архива. Выгрузки данных и релизы программ часто приходят в `.tar.gz` или `.csv.gz`.

## curl — скачать файл

```bash
curl -L -o file.csv https://example.com/file.csv   # скачать в файл
curl -I https://dataengineer.ru                   # только заголовки ответа
curl https://api.github.com/repos/duckdb/duckdb    # ответ API прямо на экран
```

- `-L` — идти по редиректам.
- `-o` — имя файла, куда сохранить.

`curl` — первый инструмент, чтобы проверить API. Вы уже скачали им учебные файлы.

## Практика

Все задания — в папке `~/cli-practice`.

### Задание 1

Посмотрите права на `scripts/report.sh`. Попробуйте запустить его через `./`.

**Проверка:** права `-rw-r--r--`. Запуск даёт ошибку `Permission denied`. В Git Bash скрипт может запуститься сразу: там `chmod` не нужен.

<details>
<summary>Решение</summary>

```bash
ls -l scripts/report.sh
./scripts/report.sh
```

</details>

### Задание 2

Разрешите запуск скрипта и запустите его.

**Проверка:**

```
data/sales_2024-01.csv: 25 orders
data/sales_2024-02.csv: 22 orders
data/sales_2024-03.csv: 28 orders
```

<details>
<summary>Решение</summary>

```bash
chmod +x scripts/report.sh
ls -l scripts/report.sh
./scripts/report.sh
```

Права стали `-rwxr-xr-x`.

</details>

### Задание 3

В `config/app.env` лежит пароль. Сделайте так, чтобы файл мог читать только владелец.

**Проверка:** `ls -l config/app.env` показывает `-rw-------`.

<details>
<summary>Решение</summary>

```bash
chmod 600 config/app.env
ls -l config/app.env
```

</details>

### Задание 4

Упакуйте папку `logs` в `logs-backup.tar.gz`. Посмотрите, что внутри архива, не распаковывая его. Потом удалите архив.

**Проверка:** в архиве папки `logs/`, `logs/archive/` и три файла `.log`.

<details>
<summary>Решение</summary>

```bash
tar czf logs-backup.tar.gz logs
tar tzf logs-backup.tar.gz
rm logs-backup.tar.gz
```

</details>

### Задание 5

Проверьте, что сайт `dataengineer.ru` отвечает. Запросите только заголовки ответа.

**Проверка:** первая строка `HTTP/2 200`.

<details>
<summary>Решение</summary>

```bash
curl -I https://dataengineer.ru
```

</details>

Дальше: [SSH и ключи](/practice/cli/ssh-keys/).
