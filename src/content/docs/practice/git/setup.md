---
title: Установка
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Установка Git, аккаунт GitHub и GitLab, SSH-ключ | Инжиниринг Данных"
description: "Как установить Git на macOS, Windows и Linux, настроить имя и email, создать аккаунты GitHub и GitLab и подключить SSH-ключ."
sidebar:
  order: 2
tags:
  - git
  - practice
---

Для курса нужны три вещи: Git на компьютере, аккаунт на GitHub и аккаунт на GitLab. GitLab нужен, чтобы увидеть разницу между платформами. Основную практику можно делать только на GitHub.

## Шаг 1. Установите Git

| Система | Команда |
|---|---|
| macOS | `brew install git` (или `xcode-select --install`) |
| Windows | Установите [Git for Windows](https://git-scm.com/downloads/win). Вместе с ним ставится Git Bash |
| Linux (Ubuntu) | `sudo apt install git` |

Проверьте:

```bash
git --version
```

Должна быть версия, например `git version 2.45.0`.

## Шаг 2. Скажите Git, кто вы

Git подписывает каждое изменение вашим именем и email. Это нужно сделать один раз:

```bash
git config --global user.name "Maria Petrova"
git config --global user.email "maria@example.com"
git config --global init.defaultBranch main
```

- Email должен совпадать с email в аккаунте GitHub или GitLab. Тогда платформа покажет вас как автора.
- Последняя команда делает `main` главной веткой по умолчанию.

Проверьте настройки:

```bash
git config --global --list
```

## Шаг 3. Создайте аккаунты

- [github.com](https://github.com/) — основная платформа для курса.
- [gitlab.com](https://gitlab.com/) — вторая платформа. Бесплатного аккаунта достаточно.

Включите двухфакторную защиту (2FA) в обоих аккаунтах. В компаниях без неё часто нельзя получить доступ к коду.

## Шаг 4. Подключите SSH-ключ

Ключ нужен, чтобы `git push` и `git pull` работали без пароля. Как создать ключ — в уроке [SSH и ключи](/practice/cli/ssh-keys/).

Коротко:

```bash
ssh-keygen -t ed25519 -C "maria@example.com"
cat ~/.ssh/id_ed25519.pub
```

Скопируйте **публичный** ключ (файл `.pub`). Приватный ключ никому не показывайте.

- GitHub: Settings → SSH and GPG keys → New SSH key.
- GitLab: Preferences → SSH Keys → Add new key.

Проверьте подключение:

```bash
ssh -T git@github.com
ssh -T git@gitlab.com
```

В ответ будет приветствие с вашим именем. Если ключа нет, можно работать и по HTTPS, но придётся вводить токен.

## Проверка

- [ ] `git --version` показывает версию.
- [ ] `git config --global user.email` показывает ваш email.
- [ ] `ssh -T git@github.com` приветствует вас по имени.
