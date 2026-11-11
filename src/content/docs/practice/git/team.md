---
title: Ветки и Pull Request
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Git-ветки, Pull Request и Merge Request | Инжиниринг Данных"
description: "Как работать в команде с Git: ветки, push, Pull Request на GitHub и Merge Request на GitLab, код-ревью, merge и разрешение конфликтов."
sidebar:
  order: 5
tags:
  - git
  - github
  - gitlab
  - practice
---

Один в репозитории вы работаете быстро. В команде нужны правила. Основное правило такое: **в `main` код попадает только после ревью**. `main` — это продакшен. Его нельзя ломать.

## Ветки

**Ветка** — отдельная линия изменений. Вы делаете её от `main`, правите код, а `main` остаётся нетронутым.

```
main:      A ── B ── C ───────────── G   ← merge
                      \             /
fix-revenue:           D ── E ── F
```

```bash
git switch -c fix-revenue      # создать ветку и перейти в неё
git branch                     # список веток
git switch main                # вернуться в main
```

Имя ветки — коротко, что делаете: `fix-revenue`, `add-refunds`. В компаниях часто добавляют номер задачи: `DE-123-add-refunds`.

## Рабочий цикл в команде

```
1. git switch -c add-refunds     ← ветка от main
2. правим код, git add, git commit
3. git push -u origin add-refunds ← отправляем ветку на GitHub/GitLab
4. открываем Pull Request (Merge Request)
5. коллеги смотрят код, пишут замечания
6. правим, делаем новые коммиты, git push
7. CI зелёный и есть approve → merge в main
8. удаляем ветку
```

## Подключите удалённый репозиторий

1. На GitHub нажмите **New repository**. Назовите его `sql-reports`. Не добавляйте README: репозиторий должен быть пустым.
2. Подключите его к локальному репозиторию:

```bash
git remote add origin git@github.com:YOUR_NAME/sql-reports.git
git push -u origin main
```

- `origin` — имя удалённого репозитория по умолчанию.
- `-u` запоминает связь, дальше хватит `git push`.

Обновите страницу на GitHub: там ваши файлы и история коммитов.

Чужой репозиторий копируют командой `git clone`:

```bash
git clone git@github.com:company/analytics.git
```

## Pull Request и Merge Request

После `git push` ветки GitHub показывает кнопку **Compare & pull request**. На GitLab кнопка называется **Create merge request**.

Это **одно и то же**. Вы просите команду: «Посмотрите мои изменения и добавьте их в `main`».

| | GitHub | GitLab |
|---|---|---|
| Название | Pull Request (PR) | Merge Request (MR) |
| Автоматические проверки | GitHub Actions (`.github/workflows/*.yml`) | GitLab CI/CD (`.gitlab-ci.yml`) |
| Защита `main` | Branch protection rules / Rulesets | Protected branches |
| Одобрение | Approve в Review | Approve в Merge Request |
| Где работает | github.com, GitHub Enterprise | gitlab.com, self-hosted GitLab |

Идея одинаковая. Названия и кнопки разные. Выучите один раз. Второй освоите за час.

### Хороший Pull Request

- **Маленький.** Одна задача. Читать 20 строк легко. Читать 2000 — никто не будет внимательно.
- **С понятным названием и описанием.** Что изменилось и зачем. Как проверить.
- **С зелёным CI.** Не просите ревью, пока проверки красные.

### Ревью

Ревьюер смотрит diff и пишет замечания к конкретным строкам. Затем выбирает одно из трёх:

- **Approve** — всё хорошо.
- **Request changes** — нужно исправить.
- **Comment** — вопрос или совет.

Что искать в SQL-ревью:

- Совпадает ли гранулярность (`grain`) с ожидаемой?
- Нет ли дублей после `JOIN`?
- Обрабатываются ли `NULL`?
- Нет ли секретов в коде?

Ревью — не проверка человека. Это способ найти ошибку до продакшена и поделиться знанием.

## merge — объединить

Когда PR одобрен и CI зелёный, нажмите **Merge**. Ветка вливается в `main`. После этого локально обновите `main`:

```bash
git switch main
git pull
git branch -d add-refunds      # удалить локальную ветку
```

Кнопки merge на платформах бывают в трёх вариантах: merge commit, squash и rebase. На старте берите **Squash and merge**. Все коммиты ветки склеятся в один чистый коммит в `main`.

## Конфликты

Конфликт возникает, когда два человека поменяли **одни и те же строки**. Git не знает, чья версия правильная, и просит решить вас.

В файле появляются маркеры:

```
<<<<<<< HEAD
where status = 'completed'
=======
where status in ('completed', 'shipped')
>>>>>>> add-refunds
```

Что делать:

1. Откройте файл. Оставьте нужный вариант. Удалите маркеры `<<<<<<<`, `=======`, `>>>>>>>`.
2. `git add <файл>`
3. `git commit`

Конфликтов меньше, если ветки короткие и вы чаще делаете `git pull`.

## Практика

### Задание 1

Создайте репозиторий `sql-reports` на GitHub. Отправьте в него свой локальный репозиторий из прошлого урока.

**Проверка:** на GitHub видны файлы и история коммитов.

<details>
<summary>Решение</summary>

```bash
git remote add origin git@github.com:YOUR_NAME/sql-reports.git
git push -u origin main
```

</details>

### Задание 2

Создайте ветку `add-revenue-by-day`. Добавьте файл `models/revenue_by_day.sql`:

```sql
select
    order_date,
    sum(amount) as revenue
from orders
where status = 'completed'
group by order_date
```

Сделайте коммит и отправьте ветку на GitHub.

**Проверка:** на GitHub появилась ветка `add-revenue-by-day`.

<details>
<summary>Решение</summary>

```bash
git switch -c add-revenue-by-day
git add models/revenue_by_day.sql
git commit -m "Add revenue by day model"
git push -u origin add-revenue-by-day
```

</details>

### Задание 3

Откройте Pull Request из этой ветки в `main`. Напишите описание: что изменилось и как проверить. Попросите коллегу или друга сделать ревью. Если коллеги нет, оставьте комментарий к строке самому себе.

**Проверка:** PR открыт. В нём есть описание и хотя бы один комментарий.

### Задание 4

Сделайте merge через **Squash and merge**. Обновите локальный `main`.

**Проверка:** `git log --oneline` в `main` показывает новый коммит. Файл `revenue_by_day.sql` есть в `main`.

<details>
<summary>Решение</summary>

```bash
git switch main
git pull
git log --oneline
```

</details>

### Задание 5. Конфликт

1. Создайте ветку `a` от `main`. Поменяйте в `models/revenue.sql` строку `where` на `where status = 'completed' and amount > 0`. Сделайте коммит.
2. Вернитесь в `main`. Поменяйте ту же строку на `where status in ('completed', 'shipped')`. Сделайте коммит.
3. В `main` выполните `git merge a`.

**Проверка:** Git пишет `CONFLICT`. Решите конфликт: оставьте условие `status in ('completed', 'shipped') and amount > 0`. Завершите merge.

<details>
<summary>Решение</summary>

```bash
git switch -c a
# правим файл
git commit -am "Filter amount > 0"
git switch main
# правим ту же строку
git commit -am "Include shipped orders"
git merge a
# открываем файл, убираем маркеры, оставляем нужное условие
git add models/revenue.sql
git commit -m "Merge branch a"
```

</details>

### Задание 6. GitLab

Повторьте путь на GitLab: создайте проект, отправьте код, откройте Merge Request, сделайте merge.

**Проверка:** на GitLab виден смёрженный Merge Request.

<details>
<summary>Подсказка</summary>

Добавьте второй remote: `git remote add gitlab git@gitlab.com:YOUR_NAME/sql-reports.git`. Затем `git push gitlab main`. Ветки и коммиты работают одинаково.

</details>
