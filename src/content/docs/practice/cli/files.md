---
title: "Файлы и папки: mkdir, cp, mv, rm"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Файлы и папки в терминале: mkdir, cp, mv, rm | Инжиниринг Данных"
description: "Как создавать, копировать, переносить, переименовывать и удалять файлы и папки в терминале. Команды mkdir, touch, cp, mv, rm и задания."
sidebar:
  order: 5
tags:
  - cli
  - practice
---

Эти команды заменяют проводник Windows и Finder на macOS.

## Создать

```bash
mkdir reports              # создать папку
mkdir -p raw/sales/2024    # создать папку вместе со всеми папками выше
touch notes.txt            # создать пустой файл
echo "привет" > hello.txt  # создать файл с текстом
```

`echo` печатает текст. Знак `>` отправляет этот текст не на экран, а в файл. Подробнее о `>` — в уроке [grep и конвейеры](/practice/cli/grep-pipes/).

## Копировать

```bash
cp data/customers.csv backup.csv     # скопировать файл с новым именем
cp data/customers.csv reports/       # скопировать в папку
cp -r data data_backup               # скопировать папку целиком
```

Для папок нужен флаг `-r` (recursive). Без него `cp` откажется копировать папку.

## Переместить и переименовать

```bash
mv backup.csv old_backup.csv   # переименовать
mv old_backup.csv reports/     # переместить в папку
```

Отдельной команды «переименовать» нет. Переименование — это перенос файла под новым именем в ту же папку.

## Удалить

```bash
rm notes.txt          # удалить файл
rmdir reports         # удалить пустую папку
rm -r data_backup     # удалить папку со всем содержимым
```

:::danger
В терминале нет корзины. `rm` удаляет файл сразу и навсегда. Перед `rm -r` прочитайте путь два раза. Никогда не запускайте `rm -rf /` и `rm -rf ~`.
:::

`rmdir` удаляет только пустую папку. Поэтому он безопасный: если внутри что-то есть, он откажется.

## Практика

Все задания — в папке `~/cli-practice`.

### Задание 1

Создайте папку `work/reports` одной командой. Папки `work` ещё нет.

**Проверка:** `ls work` показывает `reports`.

<details>
<summary>Решение</summary>

```bash
cd ~/cli-practice
mkdir -p work/reports
ls work
```

</details>

### Задание 2

Скопируйте `data/customers.csv` в папку `work`. Потом переименуйте копию в `clients.csv`.

**Проверка:** `ls work` показывает `clients.csv  reports`. Файл `data/customers.csv` остался на месте.

<details>
<summary>Решение</summary>

```bash
cp data/customers.csv work/
mv work/customers.csv work/clients.csv
ls work
```

</details>

### Задание 3

Создайте файл `work/reports/todo.txt` с текстом `проверить продажи за март`. Выведите его содержимое на экран.

**Проверка:** на экране строка `проверить продажи за март`.

<details>
<summary>Решение</summary>

```bash
echo "проверить продажи за март" > work/reports/todo.txt
cat work/reports/todo.txt
```

`cat` печатает файл целиком. Подробнее — в следующем уроке.

</details>

### Задание 4

Попробуйте удалить папку `work` командой `rmdir`. Что произошло? Потом удалите её так, чтобы удалилось всё содержимое.

**Проверка:** `rmdir` пишет ошибку `Directory not empty`. После второй команды `ls` больше не показывает `work`.

<details>
<summary>Решение</summary>

```bash
rmdir work
rm -r work
ls
```

</details>

Дальше: [Чтение файлов](/practice/cli/read-files/).
