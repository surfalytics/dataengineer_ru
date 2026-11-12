---
title: Цикл работы
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Git для начинающих: commit, diff, log на SQL | Инжиниринг Данных"
description: "Базовый цикл работы с Git на примере SQL-проекта: git init, status, add, commit, diff, log, откат изменений и файл .gitignore."
sidebar:
  order: 4
tags:
  - git
  - practice
---

Здесь вы создадите свой первый репозиторий с SQL-запросом. Всё делаем локально, интернет не нужен.

## Цикл

Работа с Git — это повторение одного цикла:

```
изменить файл  →  git add  →  git commit  →  (повторить)
```

Три области, через которые проходит файл:

| Область | Что это |
|---|---|
| **Рабочая папка** | Файлы, которые вы правите |
| **Индекс** (staging) | Изменения, которые вы выбрали для следующего коммита (`git add`) |
| **История** | Сохранённые коммиты (`git commit`) |

Индекс нужен, чтобы вы сами решали, что попадёт в коммит. Правки в разных файлах можно разложить по разным коммитам.

## Создайте репозиторий

```bash
mkdir sql-reports
cd sql-reports
git init
```

`git init` создаёт скрытую папку `.git`. Теперь папка — репозиторий.

Создайте первый запрос:

```bash
mkdir models
cat > models/revenue.sql <<'SQL'
select
    order_id,
    amount
from orders
SQL
```

## status — что изменилось

```bash
git status
```

Git покажет `models/` в разделе `Untracked files`. Он видит файл, но не следит за ним.

## add и commit — сохранить версию

```bash
git add models/revenue.sql
git commit -m "Add revenue model"
```

- `git add` кладёт файл в индекс.
- `git commit -m` сохраняет снимок в историю. Сообщение в кавычках — это **что** вы сделали.

Пишите сообщения коротко и понятно: `Filter completed orders`, `Fix refund join`. Не пишите `fix`, `update`, `asdf`. Через месяц вы не поймёте, что это было.

## diff — что именно изменилось

Поправьте запрос: нужны только завершённые заказы.

```bash
cat > models/revenue.sql <<'SQL'
select
    order_id,
    amount
from orders
where status = 'completed'
SQL
git diff
```

Строки с `+` добавлены. Строки с `-` удалены. Так же выглядит изменение на GitHub и GitLab, только в цвете:

![Diff коммита на GitHub: сообщение коммита, автор, hash и строка, которая изменилась, красным и зелёным](/assets/practice/git/github-commit-diff.jpg)

Вверху — сообщение коммита, автор и hash. Ниже — diff каждого файла.

Сохраните:

```bash
git add models/revenue.sql
git commit -m "Filter completed orders"
```

Короткая запись для уже отслеживаемых файлов: `git commit -am "сообщение"`. Новые файлы она не берёт.

## log — история

```bash
git log --oneline
```

```
9d1f502 Filter completed orders
9a73738 Add revenue model
```

Это и есть замена `revenue_v2.sql` и `revenue_v2_final.sql`. Файл один. Версий две, и у каждой есть имя.

Посмотреть старую версию файла:

```bash
git show HEAD~1:models/revenue.sql
```

`HEAD` — последний коммит. `HEAD~1` — на один коммит раньше.

## Откат

| Ситуация | Команда |
|---|---|
| Испортил файл, ещё не сделал commit. Хочу вернуть как в последнем коммите | `git restore models/revenue.sql` |
| Убрать файл из индекса, но оставить правки | `git restore --staged models/revenue.sql` |
| Коммит уже сделан и отправлен коллегам. Хочу отменить его | `git revert <hash>` |

`git revert` не стирает историю. Он создаёт **новый коммит**, который отменяет старый. Это безопасный способ.

<br />

:::caution
`git restore` без `--staged` удаляет правки без возможности вернуть. Перед ним посмотрите `git diff`.
:::

## .gitignore — что не хранить

Создайте файл `.gitignore` в корне репозитория:

```
.env
*.duckdb
__pycache__/
.DS_Store
```

Теперь Git не будет предлагать эти файлы в `git status`. Сам `.gitignore` коммитят, чтобы он был у всей команды.

```bash
git add .gitignore
git commit -m "Add .gitignore"
```

## Шпаргалка

| Команда | Что делает |
|---|---|
| `git init` | Создаёт репозиторий |
| `git status` | Показывает, что изменилось |
| `git diff` | Показывает изменения построчно |
| `git add <файл>` | Выбирает изменения для коммита |
| `git commit -m "..."` | Сохраняет версию |
| `git log --oneline` | Показывает историю |
| `git restore <файл>` | Отменяет правки в файле |
| `git revert <hash>` | Отменяет коммит новым коммитом |

## Практика

### Задание 1

Создайте репозиторий `sql-reports` и сделайте два коммита: `Add revenue model` и `Filter completed orders`.

**Проверка:** `git log --oneline` показывает два коммита.

<details>
<summary>Решение</summary>

Команды из урока выше: `git init`, создать `models/revenue.sql`, `git add`, `git commit`, правка, снова `git add` и `git commit`.

</details>

### Задание 2

Добавьте второй запрос `models/refunds.sql`. Сделайте для него отдельный коммит.

```sql
select
    order_id,
    amount
from refunds
```

**Проверка:** в `git log --oneline` три коммита. Последний про `refunds`.

<details>
<summary>Решение</summary>

```bash
cat > models/refunds.sql <<'SQL'
select
    order_id,
    amount
from refunds
SQL
git add models/refunds.sql
git commit -m "Add refunds model"
```

</details>

### Задание 3

Испортите `models/revenue.sql`: удалите всё содержимое файла. Не делайте commit. Верните файл.

**Проверка:** `git status` пишет `nothing to commit, working tree clean`.

<details>
<summary>Решение</summary>

```bash
: > models/revenue.sql
git status
git restore models/revenue.sql
git status
```

</details>

### Задание 4

Оказалось, что запрос `refunds` не нужен. Отмените коммит `Add refunds model` безопасным способом, без потери истории.

**Проверка:** в `git log --oneline` появился коммит `Revert "Add refunds model"`. Файла `models/refunds.sql` больше нет.

<details>
<summary>Решение</summary>

```bash
git log --oneline          # найдите hash нужного коммита
git revert <hash>
```

Откроется редактор с сообщением. Сохраните и закройте. Для `vim`: `:wq`. Чтобы не открывать редактор: `git revert --no-edit <hash>`.

</details>

### Задание 5

Создайте файл `.env` с текстом `API_KEY=secret`. Сделайте так, чтобы Git его не видел.

**Проверка:** `git status` не показывает `.env`.

<details>
<summary>Решение</summary>

```bash
echo "API_KEY=secret" > .env
echo ".env" >> .gitignore
git status
```

</details>
