---
title: Практика на GitLab
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Проект на GitLab: Issue, Merge Request | Инжиниринг Данных"
description: "Пошаговая практика: создайте бесплатный проект на GitLab, заведите задачу Issue, сделайте ветку, Merge Request и merge. Сравнение с GitHub."
sidebar:
  order: 7
tags:
  - git
  - gitlab
  - practice
---

Повторим путь из прошлого урока на GitLab. Идея та же. Отличаются названия и кнопки.

**Задача:** добавить SQL-запрос «выручка по статусам заказов» и показать его команде через Merge Request.

Вам нужен аккаунт GitLab и SSH-ключ из урока [Установка](/practice/git/setup/).

## Словарь: GitHub и GitLab

| GitHub | GitLab |
|---|---|
| Repository | **Project** |
| Pull Request | **Merge Request** (MR) |
| Issues | Issues |
| Actions | CI/CD Pipelines |
| Squash and merge | Squash commits (галочка при merge) |
| Fork | Fork |

## Шаг 1. Создайте проект

1. Откройте [gitlab.com](https://gitlab.com/) и нажмите **New project** → **Create blank project**.
2. **Project name:** `sql-practice`.
3. **Visibility Level:** `Public` или `Private`. Оба бесплатные.
4. Включите **Initialize repository with a README**.
5. Нажмите **Create project**.

Так выглядит страница проекта. Здесь — публичный проект GitLab Runner:

![Страница проекта на GitLab: меню слева, кнопка Code, список файлов и последний коммит](/assets/practice/git/gitlab-project.jpg)

Главное отличие от GitHub — **меню слева**:

- **Code** — файлы, ветки, коммиты и Merge requests.
- **Plan** — задачи (Issues или Work items).
- **Build** — CI/CD: Pipelines и Jobs.
- **Settings** — настройки проекта. Видны только владельцу.

Над файлами — последний коммит и кнопка **History**. Это `git log` в браузере.

## Шаг 2. Клонируйте проект

Нажмите синюю кнопку **Code**, скопируйте адрес из блока **Clone with SSH**.

```bash
cd ..
git clone git@gitlab.com:YOUR_NAME/sql-practice.git sql-practice-gitlab
cd sql-practice-gitlab
```

Мы указали имя папки `sql-practice-gitlab`, чтобы не путать её с проектом на GitHub.

## Шаг 3. Заведите Issue

Слева откройте **Plan** → **Issues** → **New issue**. В новых версиях GitLab этот пункт называется **Work items**, а кнопка — **New item**. Выберите тип **Issue**.

- **Title:** `Add revenue by status query`
- **Description:** `Нужен запрос: выручка по статусам заказов.`

Нажмите **Create issue**. Запомните номер, например `#1`.

## Шаг 4. Ветка и код

```bash
git switch -c add-revenue-by-status

cat > orders.csv <<'CSV'
order_id,customer,amount,status
1,anna,100,completed
2,boris,50,cancelled
3,anna,70,completed
4,clara,300,completed
5,boris,40,completed
6,dima,20,completed
CSV

cat > revenue_by_status.sql <<'SQL'
select
    status,
    sum(amount) as revenue
from 'orders.csv'
group by status
order by status
SQL

duckdb -c ".read revenue_by_status.sql"
```

Ожидаемый результат:

| status | revenue |
|---|---|
| cancelled | 50 |
| completed | 530 |

## Шаг 5. Коммит и push

```bash
git add orders.csv revenue_by_status.sql
git commit -m "Add revenue by status query"
git push -u origin add-revenue-by-status
```

GitLab напечатает ссылку для создания Merge Request.

## Шаг 6. Откройте Merge Request

1. Перейдите по ссылке из терминала. Или откройте **Code** → **Merge requests** → **New merge request**.
2. **Title:** `Add revenue by status query`.
3. В описании напишите:

```
Closes #1

- Добавил запрос revenue_by_status.sql
- Добавил тестовые данные orders.csv

Как проверить: duckdb -c ".read revenue_by_status.sql"
```

4. Включите **Squash commits** и **Delete source branch**.
5. Нажмите **Create merge request**.

Так выглядит Merge Request после merge:

![Merge Request на GitLab: статус Merged, вкладки Overview, Commits, Pipelines, Changes, пройденный pipeline и блок Approved by](/assets/practice/git/gitlab-merge-request.jpg)

Что на нём искать:

- **Статус** под названием: `Open` или `Merged`. Рядом — из какой ветки в какую.
- **Описание** со словами `Closes #40238`. После merge задача закрылась сама.
- **Pipeline** — результат CI. Кружки — это этапы (stages). Зелёные — пройдены.
- **Approved by** — кто одобрил.
- **Вкладки:** `Overview` — обсуждение, `Commits` — коммиты, `Pipelines` — запуски CI, `Changes` — diff.

## Шаг 7. Ревью

1. Откройте вкладку **Changes**. Тут тот же diff, что на GitHub:

![Вкладка Changes в Merge Request на GitLab: три удалённые строки красным и три добавленные строки зелёным, исправлена опечатка ppc64el на ppc64le](/assets/practice/git/gitlab-mr-changes.jpg)

В этом MR исправили опечатку: `ppc64el` → `ppc64le`. Маленький и понятный MR легко проверить.

2. Наведите мышь на строку и нажмите значок комментария.
3. Напишите: `Добавь в запрос количество заказов по статусам`.
4. Нажмите **Start review** → **Submit review**.

В GitLab у комментария есть **thread**. Автор отвечает в нём и нажимает **Resolve thread**, когда исправил.

Исправьте запрос:

```bash
# добавьте в select: count(*) as orders
git commit -am "Add orders count"
git push
```

Новый коммит появится в Merge Request.

## Шаг 8. Merge

1. Нажмите **Approve**, если кнопка есть. Если вы работаете один, этот шаг можно пропустить.
2. Нажмите **Merge**.
3. Проверьте: Issue `#1` закрыта, ветка удалена.

```bash
git switch main
git pull
git log --oneline
```

## Шаг 9. Защита main

В GitLab ветка `main` по умолчанию **защищена**: в неё нельзя делать `force push`. Прямой push доступен владельцу. Чтобы закрыть и его:

1. **Settings** → **Repository** → **Protected branches**.
2. У ветки `main` в **Allowed to push and merge** выберите `No one`. Или роль `Maintainers` для merge.
3. В **Settings** → **Merge requests** включите **Pipelines must succeed**, когда подключите CI (урок [CI/CD](/practice/git/ci-cd/)).

## Проверьте себя

- [ ] Проект `sql-practice` есть на GitLab.
- [ ] Issue `#1` закрыта после merge.
- [ ] В `main` есть `revenue_by_status.sql`.
- [ ] В Merge Request виден thread ревью и коммит с исправлением.

## Дополнительные задания

### Задание 1. Одна история, два сервера

В локальном репозитории `sql-practice` (из GitHub) добавьте GitLab как второй remote. Отправьте `main` на оба сервера.

**Проверка:** на GitHub и GitLab одинаковая история коммитов.

<details>
<summary>Решение</summary>

```bash
cd ../sql-practice
git remote add gitlab git@gitlab.com:YOUR_NAME/sql-practice-copy.git
git remote -v
git push gitlab main
```

Сначала создайте на GitLab пустой проект без README. Назовите его `sql-practice-copy`.

</details>

### Задание 2. Шаблон Merge Request

Создайте файл `.gitlab/merge_request_templates/Default.md`:

```
## Что изменилось

## Как проверить
```

**Проверка:** при создании нового MR описание заполнено шаблоном.

### Задание 3. Сравнение

Заполните таблицу для себя: где вам было удобнее и почему.

| | GitHub | GitLab |
|---|---|---|
| Создание репозитория | | |
| Ревью кода | | |
| Закрытие Issue из PR/MR | | |

Нет правильных ответов. Важно увидеть, что обе платформы делают одно и то же.
