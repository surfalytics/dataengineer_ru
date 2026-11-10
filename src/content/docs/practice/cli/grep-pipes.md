---
title: "grep и конвейеры"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "grep, конвейеры, sort и uniq в терминале | Инжиниринг Данных"
description: "Как искать строки в логах и CSV командой grep, соединять команды конвейером, считать значения через cut, sort, uniq и сохранять результат в файл."
sidebar:
  order: 8
tags:
  - cli
  - practice
---

Это самый полезный урок курса. `grep` и конвейеры каждый день используют, чтобы разобраться в логах и быстро посчитать что-то в CSV.

## grep — найти строки

`grep` печатает строки, в которых есть текст:

```bash
grep ERROR logs/pipeline.log         # строки с ERROR
grep -i error logs/pipeline.log      # без учёта регистра: error, Error, ERROR
grep -v INFO logs/pipeline.log       # строки БЕЗ INFO
grep -c ERROR logs/pipeline.log      # не строки, а их количество
grep -n ERROR logs/pipeline.log      # с номерами строк
grep ERROR logs/*.log                # во многих файлах; перед строкой будет имя файла
grep -h ERROR logs/*.log             # во многих файлах, без имени файла
grep -o "table=[a-z]*" logs/pipeline.log   # только совпавший кусок, а не всю строку
```

Текст для поиска — это **регулярное выражение**. Пара правил:

- `.` — один любой символ, `*` — повтор предыдущего символа сколько угодно раз.
- `[a-z]*` — сколько угодно маленьких латинских букв.

Если в тексте есть пробел, берите его в кавычки: `grep "run failed" logs/pipeline.log`.

## Конвейер |

Знак `|` (pipe) передаёт вывод одной команды на вход другой:

```bash
grep ERROR logs/pipeline.log | wc -l
```

`grep` нашёл строки с ошибками, `wc -l` их посчитал. Команд в конвейере может быть сколько угодно. Это главная идея Unix: маленькие программы, которые соединяют вместе.

## cut, sort, uniq — посчитать значения

```bash
cut -d, -f5 data/sales_2024-03.csv   # 5-й столбец CSV (разделитель — запятая)
sort                                 # отсортировать строки
sort -rn                             # по числу, по убыванию
uniq -c                              # склеить одинаковые соседние строки и посчитать их
```

Вместе они работают как `GROUP BY` в SQL:

```bash
cut -d, -f5 data/sales_2024-03.csv | tail -n +2 | sort | uniq -c
```

1. `cut` берёт столбец `status`.
2. `tail -n +2` убирает заголовок.
3. `sort` ставит одинаковые значения рядом. Без этого `uniq` не сработает.
4. `uniq -c` считает каждое значение.

:::note
`cut` не понимает кавычки в CSV. Если в значениях есть запятые (`"Petrov, Ivan"`), он разрежет строку неправильно. Для таких файлов берите DuckDB. Как — в уроке [CLI-инструменты и AI-агенты](/practice/cli/tools-and-ai/).
:::

## > и >> — сохранить в файл

```bash
grep ERROR logs/pipeline.log > errors.txt    # записать в файл (старое содержимое пропадёт)
grep WARN logs/pipeline.log >> errors.txt    # дописать в конец файла
```

`>` перезаписывает файл без вопросов. `>>` добавляет в конец.

## Практика

Все задания — в папке `~/cli-practice`.

### Задание 1

Сколько строк с `ERROR` в логе за март (`logs/pipeline.log`)?

**Проверка:** 20.

<details>
<summary>Решение</summary>

```bash
grep -c ERROR logs/pipeline.log
```

</details>

### Задание 2

В какие дни марта пайплайн упал? Найдите строки `run failed` и выведите из них только дату — первый столбец, разделитель пробел.

**Проверка:** 10 дат, от `2024-03-02` до `2024-03-30`.

<details>
<summary>Решение</summary>

```bash
grep "run failed" logs/pipeline.log | cut -d" " -f1
```

</details>

### Задание 3

Сколько в мартовском логе строк, где нет `INFO`? Это все ошибки и предупреждения.

**Проверка:** 31.

<details>
<summary>Решение</summary>

```bash
grep -v INFO logs/pipeline.log | wc -l
```

</details>

### Задание 4

Посчитайте заказы марта по статусам.

**Проверка:**

```
   4 cancelled
  22 completed
   2 refunded
```

Число пробелов перед числами может быть другим.

<details>
<summary>Решение</summary>

```bash
cut -d, -f5 data/sales_2024-03.csv | tail -n +2 | sort | uniq -c
```

</details>

### Задание 5

Какие типы событий самые частые? Посчитайте события в `data/events.csv` по типу (3-й столбец) и отсортируйте от большего к меньшему.

**Проверка:**

```
5344 page_view
2756 click
 953 purchase
 947 signup
```

<details>
<summary>Решение</summary>

```bash
cut -d, -f3 data/events.csv | tail -n +2 | sort | uniq -c | sort -rn
```

</details>

### Задание 6

Какая таблица чаще всего ломает загрузку? Найдите строки `load failed` во всех логах за три месяца: `logs/pipeline.log` и `logs/archive/*.log`. Вытащите из них `table=...` и посчитайте.

**Проверка:**

```
   9 table=customers
   6 table=orders
   5 table=events
```

<details>
<summary>Решение</summary>

```bash
grep -h "load failed" logs/pipeline.log logs/archive/*.log | grep -o "table=[a-z]*" | sort | uniq -c | sort -rn
```

Без `-h` перед каждой строкой будет имя файла, и `uniq` посчитает неправильно.

</details>

### Задание 7

Сохраните все строки с `ERROR` из трёх логов в файл `errors.txt`. Потом допишите в конец строку `проверено`. Сколько строк в файле?

**Проверка:** 41 строка: 40 ошибок и строка `проверено`.

<details>
<summary>Решение</summary>

```bash
grep -h ERROR logs/pipeline.log logs/archive/*.log > errors.txt
echo "проверено" >> errors.txt
wc -l errors.txt
rm errors.txt
```

</details>

Дальше: [Переменные и PATH](/practice/cli/variables/).
