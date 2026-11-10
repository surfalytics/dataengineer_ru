---
title: "Итоговая практика"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Итоговая практика по CLI: разбор выгрузки данных | Инжиниринг Данных"
description: "Итоговое задание курса CLI: наведите порядок в выгрузке от поставщика. Папки, перенос и удаление файлов, шаблоны, grep, права и архив."
sidebar:
  order: 13
tags:
  - cli
  - practice
---

Ваш первый день в команде данных. Поставщик прислал папку `inbox`. В ней вперемешку файлы продаж, справочник товаров, временные файлы и скрытый файл с ключом API.

Перед загрузкой в хранилище папку нужно привести к такому виду:

```
inbox/
├── raw/
│   ├── sales/    ← месячные файлы продаж
│   └── ref/      ← справочник товаров
├── archive/      ← копия справочника с датой
├── README.txt
└── .env          ← ключ API, закрыт правами 600
```

Используйте только команды из курса. Решайте сами, без AI. Решения — под каждым заданием.

Хотите начать заново? Удалите `~/cli-practice` и распакуйте архив ещё раз (см. [Установка](/practice/cli/setup/)).

### Задание 1

Перейдите в папку `inbox` и напечатайте полный путь к ней.

**Проверка:** путь заканчивается на `/cli-practice/inbox`.

<details>
<summary>Решение</summary>

```bash
cd ~/cli-practice/inbox
pwd
```

</details>

### Задание 2

`ls` показывает 8 имён, но в папке есть ещё скрытый файл. Найдите его и выведите содержимое.

**Проверка:** `API_KEY=not-a-real-key`.

<details>
<summary>Решение</summary>

```bash
ls -a
cat .env
```

</details>

### Задание 3

Создайте папки `raw/sales`, `raw/ref` и `archive` одной командой.

**Проверка:** нет вывода. `ls` теперь показывает ещё `archive` и `raw`.

<details>
<summary>Решение</summary>

```bash
mkdir -p raw/sales raw/ref archive
```

</details>

### Задание 4

Перенесите оба файла продаж в `raw/sales` одним шаблоном, не печатая имена.

**Проверка:** `ls raw/sales` показывает `sales_2024-04.csv` и `sales_2024-05.csv`.

<details>
<summary>Решение</summary>

```bash
mv sales_*.csv raw/sales/
```

</details>

### Задание 5

Перенесите `products.csv` в `raw/ref`. Потом скопируйте его в `archive/products_2024-06-01.csv` как копию с датой. Проверьте, что файлы одинаковые.

**Проверка:** `diff` ничего не печатает. Значит, файлы одинаковые.

<details>
<summary>Решение</summary>

```bash
mv products.csv raw/ref/
cp raw/ref/products.csv archive/products_2024-06-01.csv
diff raw/ref/products.csv archive/products_2024-06-01.csv
```

</details>

### Задание 6

В `notes.txt` написано, что файлы `tmp` — мусор. Сначала посмотрите, что попадает под шаблон. Потом удалите эти файлы одной командой.

**Проверка:** шаблон находит три файла `tmp_export_01.bak`–`tmp_export_03.bak`. После удаления `ls` их не показывает.

<details>
<summary>Решение</summary>

```bash
cat notes.txt
ls tmp_*
rm tmp_*.bak
```

</details>

### Задание 7

Удалите пустую папку `old` командой, которая удаляет только пустые папки. Переименуйте `notes.txt` в `README.txt`.

**Проверка:** папки `old` нет. Есть `README.txt`, нет `notes.txt`.

<details>
<summary>Решение</summary>

```bash
rmdir old
mv notes.txt README.txt
```

</details>

### Задание 8

Посмотрите на апрельский файл продаж: заголовок и первый заказ.

**Проверка:**

```
order_id,order_date,customer_id,amount,status
1076,2024-04-01,5,453.02,completed
```

<details>
<summary>Решение</summary>

```bash
head -n 2 raw/sales/sales_2024-04.csv
```

</details>

### Задание 9

Сколько заказов в двух файлах вместе, без заголовков? И сколько из них выполнено (`completed`)?

**Проверка:** 44 заказа, из них 36 выполнено.

<details>
<summary>Решение</summary>

```bash
grep -hv order_id raw/sales/*.csv | wc -l
grep -h ",completed" raw/sales/*.csv | wc -l
```

`-v order_id` убирает строки заголовков: только в них есть слово `order_id`.

</details>

### Задание 10

Закройте `.env` так, чтобы его мог читать только владелец.

**Проверка:** `ls -l .env` показывает `-rw-------`. В Git Bash права могут не поменяться — это нормально.

<details>
<summary>Решение</summary>

```bash
chmod 600 .env
ls -l .env
```

</details>

### Задание 11

Проверьте результат: выведите все файлы в `inbox`, включая скрытые, по одному пути на строку, отсортированные.

**Проверка:**

```
./.env
./README.txt
./archive/products_2024-06-01.csv
./raw/ref/products.csv
./raw/sales/sales_2024-04.csv
./raw/sales/sales_2024-05.csv
```

<details>
<summary>Решение</summary>

```bash
find . -type f | sort
```

</details>

### Задание 12

Упакуйте готовую папку `inbox` в архив `inbox-clean.tar.gz` в папке `cli-practice`. Посмотрите, что в архиве.

**Проверка:** в архиве 11 записей: 5 папок (`inbox/` и 4 внутри) и 6 файлов, включая `inbox/.env`.

<details>
<summary>Решение</summary>

```bash
cd ..
tar czf inbox-clean.tar.gz inbox
tar tzf inbox-clean.tar.gz
tar tzf inbox-clean.tar.gz | wc -l
```

</details>

## Что дальше

Вы прошли базовый минимум CLI. Теперь терминал не страшен, а команды в инструкциях и у AI-агентов понятны.

- Продолжайте с [Базовым минимумом SQL](/practice/sql/), если ещё не прошли его.
- Дальше в практике: Python, Git и Docker. Все они работают через терминал.
