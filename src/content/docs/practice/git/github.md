---
title: Практика на GitHub
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Репозиторий на GitHub: Issue, Pull Request | Инжиниринг Данных"
description: "Пошаговая практика: создайте бесплатный репозиторий на GitHub, заведите задачу Issue, сделайте ветку, Pull Request, ревью и merge на SQL-примере."
sidebar:
  order: 6
tags:
  - git
  - github
  - practice
---

Теперь всё вместе, на настоящем сайте. Создадим бесплатный репозиторий на GitHub и выполним в нём маленькую задачу. Весь путь занимает 20–30 минут.

**Задача:** добавить SQL-запрос «топ-3 клиента по выручке» и показать его команде через Pull Request.

Вам нужен аккаунт и SSH-ключ из урока [Установка](/practice/git/setup/).

## Шаг 1. Создайте репозиторий

1. Откройте [github.com/new](https://github.com/new).
2. **Repository name:** `sql-practice`.
3. **Visibility:** `Public`. Приватный тоже бесплатный. Для учебы выберите любой. Не кладите в него ничего личного.
4. Включите **Add a README file**.
5. **Add .gitignore:** оставьте `None`. Свой файл добавим позже.
6. Нажмите **Create repository**.

GitHub создал репозиторий с одним файлом `README.md` и веткой `main`. Платить не нужно.

Так выглядит страница репозитория. Здесь — публичный репозиторий этого сайта:

![Страница репозитория на GitHub: вкладки Code, Issues, Pull requests, Actions, список файлов и кнопка Code](/assets/practice/git/github-repo.jpg)

Что на ней искать:

- **Вкладки сверху.** `Code` — файлы. `Issues` — задачи. `Pull requests` — изменения на ревью. `Actions` — CI/CD.
- **Ветка `main`** слева над файлами. Здесь можно переключить ветку.
- **Последний коммит** над списком файлов: автор, сообщение, hash. Ссылка `Commits` справа открывает всю историю. Это `git log` в браузере.
- **Колонка справа от каждого файла** — последний коммит, который его менял.

## Шаг 2. Клонируйте его на компьютер

На странице репозитория нажмите зелёную кнопку **Code**, вкладка **SSH**, скопируйте адрес.

![Окно Clone на GitHub после нажатия кнопки Code: адрес репозитория и кнопка копирования](/assets/practice/git/github-clone.jpg)

На скриншоте нет вкладки **SSH**: он сделан без входа в аккаунт. Когда вы вошли и добавили SSH-ключ, вкладка появится рядом с **HTTPS**. Адрес SSH начинается с `git@github.com:`.

```bash
git clone git@github.com:YOUR_NAME/sql-practice.git
cd sql-practice
ls
```

Вы увидели `README.md`. Команда `git clone` скачала репозиторий вместе с историей и сама настроила `origin`.

## Шаг 3. Заведите задачу (Issue)

В командах работа начинается с задачи. На GitHub откройте вкладку **Issues** → **New issue**.

- **Title:** `Add top 3 customers by revenue query`
- **Description:** `Нужен запрос: топ-3 клиента по сумме завершённых заказов.`

Нажмите **Submit new issue**. У задачи есть номер, например `#1`. Он нужен для связи с Pull Request.

## Шаг 4. Ветка и код

Не работайте в `main`. Создайте ветку под задачу:

```bash
git switch -c add-top-customers
```

Добавьте тестовые данные и запрос:

```bash
cat > orders.csv <<'CSV'
order_id,customer,amount,status
1,anna,100,completed
2,boris,50,cancelled
3,anna,70,completed
4,clara,300,completed
5,boris,40,completed
6,dima,20,completed
CSV

cat > top_customers.sql <<'SQL'
select
    customer,
    sum(amount) as revenue
from 'orders.csv'
where status = 'completed'
group by customer
order by revenue desc
limit 3
SQL
```

Проверьте запрос (нужен [DuckDB](/practice/sql/setup/)):

```bash
duckdb -c ".read top_customers.sql"
```

Ожидаемый результат:

| customer | revenue |
|---|---|
| clara | 300 |
| anna | 170 |
| boris | 40 |

## Шаг 5. Коммит и push

Сделайте два отдельных коммита: данные и запрос.

```bash
git add orders.csv
git commit -m "Add sample orders"
git add top_customers.sql
git commit -m "Add top 3 customers query"
git push -u origin add-top-customers
```

В ответ Git напечатает ссылку для создания Pull Request.

## Шаг 6. Откройте Pull Request

1. Обновите страницу репозитория. Нажмите **Compare & pull request**.
2. **Title:** `Add top 3 customers query`.
3. В описании напишите:

```
Closes #1

- Добавил запрос top_customers.sql
- Добавил тестовые данные orders.csv

Как проверить: duckdb -c ".read top_customers.sql"
```

Слова `Closes #1` свяжут PR с задачей. После merge задача закроется сама.

4. Нажмите **Create pull request**.

Так выглядит открытый Pull Request. Здесь — PR, в котором добавили этот курс:

![Страница Pull Request на GitHub: название, статус, вкладки Conversation, Commits, Checks, Files changed и описание](/assets/practice/git/github-pull-request.jpg)

Что на ней искать:

- **Статус** под названием: `Open`, `Merged` или `Closed`. Рядом — из какой ветки в какую: `main` ← `ваша-ветка`.
- **Conversation** — описание и обсуждение.
- **Commits** — все коммиты ветки.
- **Checks** — результат CI. Зелёная галочка или красный крестик.
- **Files changed** — diff. Здесь делают ревью.
- **Справа** — ревьюеры (`Reviewers`) и связанные задачи (`Development`).

## Шаг 7. Ревью

Попросите коллегу или друга открыть вкладку **Files changed** и оставить комментарий к строке. Если никого нет, сделайте это сами.

Так выглядит diff на GitHub. Красное — удалено, зелёное — добавлено:

![Diff на GitHub: строка order 7 удалена и выделена красным, строка order 9 добавлена и выделена зелёным](/assets/practice/git/github-commit-diff.jpg)

- Слева два столбца номеров: строка в старой версии и в новой.
- Сверху имя файла и счётчик `+1 -1`.
- Значок `+` появляется, когда вы наводите мышь на номер строки. Им добавляют комментарий.

1. Наведите мышь на строку `limit 3` и нажмите `+`.
2. Напишите: `Что будет, если у двух клиентов одинаковая выручка?`
3. Нажмите **Start a review** → **Finish your review** → **Request changes**.

Ответьте на замечание новым коммитом. Например, добавьте `, customer` в `order by`, чтобы порядок был всегда одинаковым:

```bash
# правим top_customers.sql: order by revenue desc, customer
git commit -am "Make order stable for equal revenue"
git push
```

Новый коммит сам появится в Pull Request. Ревьюер нажимает **Approve**.

## Шаг 8. Merge

1. Нажмите **Squash and merge** → **Confirm**.
2. Нажмите **Delete branch**.
3. Откройте Issue `#1`. Она закрыта автоматически.

Обновите локальный репозиторий:

```bash
git switch main
git pull
git branch -d add-top-customers
git log --oneline
```

В `main` один новый коммит с вашим запросом.

## Шаг 9. Добавьте защиту main

Сделайте так, чтобы в `main` нельзя было писать напрямую.

1. **Settings** → **Rules** → **Rulesets** → **New ruleset** → **New branch ruleset**.
2. Название: `protect-main`. **Enforcement status:** `Active`.
3. **Target branches:** `Include default branch`.
4. Включите **Require a pull request before merging**.
5. Нажмите **Create**.

Проверьте:

```bash
echo "test" >> README.md
git commit -am "Direct push"
git push origin main
```

**Проверка:** `git push` отклонён с ошибкой. Значит, защита работает.

Уберите тестовый коммит из локального `main`:

```bash
git reset --hard origin/main
```

`git reset --hard` стирает локальные коммиты и правки без возврата. Здесь это нужно: тестовый коммит нам не нужен.

<br />

:::note
Rulesets для **приватных** репозиториев есть только на платных тарифах. Если репозиторий приватный, пропустите этот шаг. На публичном он бесплатный.
:::

## Проверьте себя

- [ ] Репозиторий `sql-practice` есть на GitHub.
- [ ] Issue `#1` закрыта автоматически после merge.
- [ ] В `main` есть `top_customers.sql` и `orders.csv`.
- [ ] В истории PR виден комментарий ревью и коммит с исправлением.
- [ ] Ветка `add-top-customers` удалена.

## Дополнительные задания

### Задание 1. Вторая задача

Заведите Issue `Add revenue by customer status`. Сделайте для неё ветку, запрос `revenue_by_status.sql` и Pull Request. Свяжите его с Issue словом `Closes`.

**Проверка:** merge закрыл вторую Issue.

<details>
<summary>Подсказка</summary>

```sql
select
    status,
    sum(amount) as revenue
from 'orders.csv'
group by status
```

</details>

### Задание 2. Шаблон Pull Request

Добавьте файл `.github/pull_request_template.md`:

```
## Что изменилось

## Как проверить
```

**Проверка:** при создании нового PR описание заполнено шаблоном.

### Задание 3. Форк

Зайдите в чужой публичный репозиторий. Нажмите **Fork**. Исправьте опечатку в `README.md` и откройте Pull Request в оригинал. Так работают в open source.

**Проверка:** PR открыт. Мержить его не нужно.
