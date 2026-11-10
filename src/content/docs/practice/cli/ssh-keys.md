---
title: "SSH и ключи"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "SSH-ключи и вход в базу по ключу: ssh-keygen | Инжиниринг Данных"
description: "Что такое SSH и пара ключей, как создать ключ через ssh-keygen, подключиться к серверу и настроить вход сервисного аккаунта в базу по ключу вместо пароля."
sidebar:
  order: 11
tags:
  - cli
  - practice
  - ssh
---

Инженер данных подключается к серверам, облачным машинам, Git и базам данных. Почти везде для этого нужны **ключи**, а не пароли. В этом уроке создадим ключи и научимся ими пользоваться.

## Что такое SSH

**SSH** (Secure Shell) — защищённое подключение к другому компьютеру через терминал. Вы пишете команды у себя, а выполняются они на сервере.

```bash
ssh ubuntu@203.0.113.10
```

- `ubuntu` — пользователь на сервере.
- `203.0.113.10` — адрес сервера (IP или имя, например `vm.example.com`).

При первом подключении SSH спросит, доверяете ли вы серверу (`Are you sure you want to continue connecting?`). Ответьте `yes`. SSH запомнит сервер в файле `~/.ssh/known_hosts`.

## Пара ключей

Ключ — это два файла:

| Файл | Что это | Кому показывать |
|---|---|---|
| `id_ed25519` | **Приватный ключ** | Никому. Он остаётся только на вашем компьютере |
| `id_ed25519.pub` | **Публичный ключ** | Можно отдать: серверу, GitHub, базе данных |

Сервер хранит ваш публичный ключ. При подключении он проверяет, что у вас есть подходящий приватный ключ. Сам приватный ключ по сети не передаётся.

## Почему ключи, а не пароль

- **Пароль можно подобрать или украсть.** Ключ — длинное случайное число. Подобрать его нельзя.
- **Роботы не умеют вводить пароль и MFA.** Пайплайн, dbt в CI или Airflow не нажмут кнопку в приложении на телефоне. Ключ работает без человека.
- **Базы запрещают вход только по паролю.** Например, Snowflake отказывается от входа по одному паролю. Для сервисных аккаунтов он рекомендует пару ключей.
- **Ключ легко отозвать.** Удалили один публичный ключ — доступ закрыт только для него. Остальные работают.

## Где это нужно в работе с данными

- Подключиться к виртуальной машине в облаке (AWS EC2, Yandex Cloud, VK Cloud) или к серверу компании.
- Работать с GitHub и GitLab по SSH. Это разберём в практике по Git.
- Открыть **SSH-туннель** к базе данных, которая закрыта от интернета.
- Забрать файлы с SFTP-сервера поставщика.
- Дать **сервисному аккаунту** доступ к базе: dbt, Airflow, Airbyte ходят в Snowflake по ключу.

## Создать ключ: ssh-keygen

```bash
ssh-keygen -t ed25519 -C "maria@example.com"
```

- `-t ed25519` — тип ключа. Современный и короткий. Берите его по умолчанию.
- `-C` — комментарий, обычно ваш email. Помогает понять, чей это ключ.
- `-f` — имя файла. Без него ключ запишется в `~/.ssh/id_ed25519`.

`ssh-keygen` спросит **passphrase** — пароль на сам ключ. Если ноутбук украдут, без passphrase ключом сможет воспользоваться кто угодно. Для личного ключа задайте passphrase. Для учебного ключа можно оставить пустой: нажмите Enter два раза.

## Отдать публичный ключ серверу

На сервере публичные ключи лежат в файле `~/.ssh/authorized_keys`. Добавить свой ключ туда можно так:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub ubuntu@203.0.113.10
```

В облаке обычно проще: публичный ключ вставляют в форму при создании машины. После этого подключаемся:

```bash
ssh -i ~/.ssh/id_ed25519 ubuntu@203.0.113.10
```

`-i` — какой приватный ключ использовать.

## ~/.ssh/config — короткие имена для серверов

Чтобы не писать каждый раз адрес, пользователя и ключ, их записывают в `~/.ssh/config`:

```
Host analytics-vm
    HostName 203.0.113.10
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
```

Теперь хватает короткой команды:

```bash
ssh analytics-vm
```

Это имя понимают и другие команды:

```bash
scp report.csv analytics-vm:/tmp/        # скопировать файл на сервер
scp analytics-vm:/var/log/app.log .      # скопировать файл с сервера
ssh -L 5433:db.internal:5432 analytics-vm   # туннель к базе
```

Туннель из последней строки работает так. База `db.internal` закрыта от интернета, но сервер `analytics-vm` её видит. Пока туннель открыт, ваш DBeaver или `psql` подключается к `localhost:5433`, а попадает в базу.

## Частые ошибки

| Ошибка | Что значит | Что делать |
|---|---|---|
| `Permission denied (publickey)` | Сервер не нашёл ваш публичный ключ | Проверьте пользователя, ключ в `-i` и `authorized_keys` на сервере |
| `UNPROTECTED PRIVATE KEY FILE!` | Приватный ключ могут читать другие | `chmod 600 ~/.ssh/ваш_ключ` |
| `REMOTE HOST IDENTIFICATION HAS CHANGED!` | Сервер пересоздали, или кто-то подменил адрес | Уточните у админа. Если сервер пересоздали: `ssh-keygen -R 203.0.113.10` |
| `Connection timed out` | Сервер недоступен | Проверьте адрес, VPN и правила сети (security group) |

## Ключ сервисного аккаунта для базы данных

**Сервисный аккаунт** — пользователь базы не для человека, а для программы: dbt, Airflow, Airbyte, BI-инструмента. Ему дают ключ вместо пароля. Разберём на примере Snowflake.

Snowflake использует ключи RSA в формате PKCS#8. Создаём их через `openssl`:

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
chmod 600 rsa_key.p8
```

- `rsa_key.p8` — приватный ключ. Его получит программа (dbt).
- `rsa_key.pub` — публичный ключ. Его получит Snowflake.
- `-nocrypt` — ключ без пароля. В рабочих проектах ключ шифруют паролем и хранят в менеджере секретов.

Администратор Snowflake создаёт пользователя и вставляет публичный ключ. Строки `-----BEGIN PUBLIC KEY-----` и `-----END PUBLIC KEY-----` не нужны, только текст между ними:

```sql
CREATE USER svc_dbt
  TYPE = SERVICE
  DEFAULT_ROLE = transformer
  RSA_PUBLIC_KEY = 'MIIBIjANBgkq...';
```

`TYPE = SERVICE` значит, что пользователь — программа. Войти по паролю он не может.

dbt подключается по ключу. Пароля в `profiles.yml` нет:

```yaml
analytics:
  target: prod
  outputs:
    prod:
      type: snowflake
      account: abc12345
      user: svc_dbt
      private_key_path: /secrets/rsa_key.p8
      role: transformer
      warehouse: transform_wh
      database: analytics
      schema: marts
```

Так же работают и другие системы. В Google Cloud сервисный аккаунт получает JSON-файл с ключом. Путь к нему кладут в переменную окружения `GOOGLE_APPLICATION_CREDENTIALS`.

## Правила безопасности

- Приватный ключ никому не отправляйте. Ни в чат, ни в почту, ни в задачу в трекере.
- Приватный ключ не попадает в Git. Добавьте `*.p8`, `*.pem` и папку с ключами в `.gitignore`.
- Права на приватный ключ — `600`, на папку `~/.ssh` — `700`.
- Один ключ на одну задачу. Отдельный ключ для каждого сервисного аккаунта.
- Ключи меняют по расписанию. В Snowflake для этого есть второй слот `RSA_PUBLIC_KEY_2`: новый ключ добавляют до того, как удалить старый.

## Практика

Задания безопасные: мы создаём учебный ключ с отдельным именем и не трогаем ваши настоящие ключи.

:::note[Git Bash]
`ssh-keygen`, `ssh` и `openssl` в Git Bash есть. Папка `~/.ssh` — это `C:\Users\<имя>\.ssh`. Права файлов `ls -l` в Git Bash показывает неточно. Это нормально.
:::

### Задание 1

Создайте папку `~/.ssh`, если её нет, и закройте её для других пользователей. Потом создайте ключ `ed25519` с именем файла `~/.ssh/cli_practice` и комментарием `cli-practice`. Passphrase оставьте пустой.

**Проверка:** `ls -l ~/.ssh` показывает два новых файла: `cli_practice` с правами `-rw-------` и `cli_practice.pub` с правами `-rw-r--r--`.

<details>
<summary>Решение</summary>

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "cli-practice" -f ~/.ssh/cli_practice
ls -l ~/.ssh
```

На вопросы про passphrase нажмите Enter два раза.

</details>

### Задание 2

Посмотрите начало обоих файлов. Потом выведите **отпечаток** (fingerprint) публичного ключа. По отпечатку сравнивают ключи, не показывая сам ключ.

**Проверка:** приватный ключ начинается с `-----BEGIN OPENSSH PRIVATE KEY-----`, публичный — с `ssh-ed25519 AAAA`. Отпечаток выглядит так: `256 SHA256:<случайные символы> cli-practice (ED25519)`.

<details>
<summary>Решение</summary>

```bash
head -n 1 ~/.ssh/cli_practice
cat ~/.ssh/cli_practice.pub
ssh-keygen -lf ~/.ssh/cli_practice.pub
```

</details>

### Задание 3

Добавьте в `~/.ssh/config` сервер `analytics-vm`: адрес `203.0.113.10`, пользователь `ubuntu`, ключ `~/.ssh/cli_practice`. Подключаться не нужно: это учебный адрес, сервера там нет. Проверьте настройки командой `ssh -G analytics-vm` — она печатает, с какими параметрами SSH подключился бы.

**Проверка:** в выводе есть строки:

```
user ubuntu
hostname 203.0.113.10
identityfile ~/.ssh/cli_practice
```

<details>
<summary>Решение</summary>

Откройте файл в редакторе `nano`:

```bash
nano ~/.ssh/config
```

Допишите в конец:

```
Host analytics-vm
    HostName 203.0.113.10
    User ubuntu
    IdentityFile ~/.ssh/cli_practice
```

Сохраните: `Ctrl + O`, Enter. Выйдите: `Ctrl + X`. Проверьте:

```bash
ssh -G analytics-vm | grep -E "^(hostname|user|identityfile) "
```

`grep -E` позволяет искать несколько слов через `|`.

</details>

### Задание 4

Создайте пару ключей для сервисного аккаунта Snowflake в папке `~/cli-practice/keys`. Закройте приватный ключ правами `600`.

**Проверка:** в папке два файла. `rsa_key.p8` начинается с `-----BEGIN PRIVATE KEY-----`, `rsa_key.pub` — с `-----BEGIN PUBLIC KEY-----`.

<details>
<summary>Решение</summary>

```bash
mkdir -p ~/cli-practice/keys
cd ~/cli-practice/keys
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
chmod 600 rsa_key.p8
head -n 1 rsa_key.p8 rsa_key.pub
```

</details>

### Задание 5

Подготовьте значение для `RSA_PUBLIC_KEY` в Snowflake: текст публичного ключа без строк `BEGIN` и `END`, одной строкой. Используйте `grep -v` и `tr -d '\n'` (удалить переводы строк).

**Проверка:** одна длинная строка, которая начинается с `MIIBIjANBgkq`. В ней 392 символа: проверьте через `| wc -c`.

<details>
<summary>Решение</summary>

```bash
grep -v "PUBLIC KEY" rsa_key.pub | tr -d '\n'
grep -v "PUBLIC KEY" rsa_key.pub | tr -d '\n' | wc -c
```

</details>

### Задание 6

Защитите ключи от случайного коммита: создайте в `~/cli-practice` файл `.gitignore`, в котором есть папка `keys/` и все файлы `*.p8`. Потом уберите учебные ключи.

**Проверка:** `cat ~/cli-practice/.gitignore` показывает две строки: `keys/` и `*.p8`. Папки `keys` больше нет. Файлов `cli_practice` в `~/.ssh` тоже.

<details>
<summary>Решение</summary>

```bash
cd ~/cli-practice
echo "keys/" > .gitignore
echo "*.p8" >> .gitignore
cat .gitignore
rm -r keys
rm ~/.ssh/cli_practice ~/.ssh/cli_practice.pub
```

Блок `analytics-vm` из `~/.ssh/config` удалите в `nano`.

</details>

Дальше: [CLI-инструменты и AI-агенты](/practice/cli/tools-and-ai/).
