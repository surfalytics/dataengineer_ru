---
title: Итоговая практика
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Практика по Git: SQL-проект, Pull Request и CI | Инжиниринг Данных"
description: "Итоговое задание по Git: создайте SQL-проект, пройдите путь от коммита до Pull Request с CI на GitHub и GitLab, исправьте ошибку и сделайте откат."
sidebar:
  order: 10
tags:
  - git
  - practice
---

Вы пришли в команду данных. Нужно завести репозиторий для отчётов и пройти весь путь изменения, как в настоящей команде.

Используйте только то, что было в курсе. Решайте сами, без AI. Решения — под заданиями.

### Задание 1. Репозиторий

Создайте репозиторий `sales-reports` на своём компьютере и на GitHub. В нём:

- `README.md` с описанием проекта в одну строку;
- `.gitignore` с `.env`, `*.duckdb`, `.DS_Store`;
- `models/revenue.sql`.

**Проверка:** на GitHub видны три файла. В `git log --oneline` есть минимум три коммита, и у каждого понятное сообщение.

<details>
<summary>Решение</summary>

```bash
mkdir sales-reports && cd sales-reports
git init
echo "# Sales reports" > README.md
git add README.md && git commit -m "Add README"
printf ".env\n*.duckdb\n.DS_Store\n" > .gitignore
git add .gitignore && git commit -m "Add .gitignore"
mkdir models
printf "select\n    order_id,\n    amount\nfrom orders\n" > models/revenue.sql
git add models && git commit -m "Add revenue model"
git remote add origin git@github.com:YOUR_NAME/sales-reports.git
git push -u origin main
```

</details>

### Задание 2. CI

Добавьте тест и `.github/workflows/ci.yml` из урока [CI/CD](/practice/git/ci-cd/). Сделайте это в ветке `add-ci` и через Pull Request.

**Проверка:** Pull Request с зелёной проверкой смёржен в `main`.

### Задание 3. Защита main

Включите защиту `main`: только через Pull Request и с зелёным CI.

**Проверка:** прямой `git push origin main` отклоняется.

### Задание 4. Новая метрика

В ветке `add-refunds` добавьте `models/refunds.sql`. Пишите каждый столбец на новой строке, иначе `sqlfluff` в CI упадёт с ошибкой `LT09`. Откройте Pull Request. Попросите коллегу сделать ревью. Учтите хотя бы одно замечание отдельным коммитом.

**Проверка:** в PR виден комментарий ревьюера и два коммита: основной и после замечания. Merge через Squash.

### Задание 5. Сломали и починили

В новой ветке намеренно сломайте запрос так, чтобы тест упал. Отправьте ветку и откройте Pull Request.

**Проверка:** CI красный, merge заблокирован. Исправьте запрос, сделайте `push`. CI стал зелёным.

### Задание 6. Откат в продакшене

Допустим, `main` уже содержит плохой коммит. Отмените его безопасно.

**Проверка:** в `main` появился коммит `Revert ...`. История не переписана.

<details>
<summary>Решение</summary>

```bash
git switch -c revert-bad-change
git revert <hash плохого коммита>
git push -u origin revert-bad-change
```

Откройте Pull Request. Так откат тоже проходит ревью и CI.

</details>

### Задание 7. GitLab

Загрузите проект в GitLab. Добавьте `.gitlab-ci.yml` и откройте Merge Request.

**Проверка:** в Merge Request виден зелёный pipeline.

### Задание 8. Агент

Попросите AI-агента добавить новую модель `models/orders_by_status.sql` в отдельной ветке. Проверьте `git diff`. Откройте Pull Request.

**Проверка:** вы нашли минимум одну вещь, которую поправили вручную. CI зелёный.

## Что дальше

- Попробуйте `git rebase` и `git stash`. Они нужны реже, но часто встречаются.
- Освойте `dbt` и запустите `dbt build` в CI.
- Изучите [Docker](/practice/docker/). В CI часто запускают контейнеры.
- Подробнее про платформы: [Git](/tools/git/) и [DevOps](/tools/devops/).
