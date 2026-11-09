---
title: "Операторы сравнения"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Операторы сравнения в SQL: =, <>, >, < | Инжиниринг Данных"
description: "Как фильтровать строки в SQL операторами =, <>, >, <, >=, <= и как считать арифметику в SELECT."
sidebar:
  order: 4
tags:
  - sql
  - practice
---

Операторы сравнения — самый простой способ фильтровать данные в `WHERE`. Они сравнивают значение столбца с числом, текстом или другим столбцом.

В этом уроке работаем с таблицей `tutorial.us_housing_units`. Числа в таблице — тысячи домов.

## Операторы для чисел

| Оператор | Значение |
|---|---|
| `=` | равно |
| `<>` или `!=` | не равно |
| `>` | больше |
| `<` | меньше |
| `>=` | больше или равно |
| `<=` | меньше или равно |

Найдём месяцы, когда на западе построили больше 30 тысяч домов:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE west > 30;
```

Запрос вернёт 278 строк. Замените `>` на другие операторы. Попробуйте другие числа. Так вы быстро почувствуете, как они работают.

## Операторы для текста

Сравнивать можно и текст. Текстовое значение пишут в одинарных кавычках:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name = 'January';
```

Операторы `>` и `<` для текста сравнивают значения по алфавиту. Точнее, по коду символов:

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name < 'O';
```

:::caution
Регистр важен. В DuckDB все заглавные буквы идут раньше строчных. `'January' < 'o'` — верно, `'September' < 'o'` — тоже верно. Поэтому сравнивайте с заглавной буквой, если значения начинаются с заглавной. Результат зависит от базы и её настроек (collation).
:::

:::tip
Сравнение текста по алфавиту нужно редко. Обычно для текста хватает `=` и `<>`.
:::

## Арифметика в SELECT

В `SELECT` можно считать. Доступны `+`, `-`, `*`, `/` и скобки:

```sql
SELECT year,
       month,
       west + south AS west_south_total
FROM tutorial.us_housing_units;
```

Правила:

- арифметика работает по строкам: каждая строка считается отдельно;
- новому столбцу дайте имя через `AS`;
- порядок действий как в математике, скобки меняют его.

Арифметику можно использовать и в `WHERE`. Здесь сравниваем столбец с суммой двух других:

```sql
SELECT year,
       month,
       west,
       south
FROM tutorial.us_housing_units
WHERE west > south + 10;
```

:::note
В DuckDB `/` делит как дробное число: `5 / 2` даст `2.5`. В Postgres для целых чисел `5 / 2` даст `2`. Целочисленное деление в DuckDB — оператор `//`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Выпускал ли регион West больше 50 тысяч домов за один месяц?

**Проверка:** 19 строк. Максимум в столбце `west` — 55.7.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE west > 50;
```

</details>

### Задание 2

Выпускал ли регион South 20 тысяч домов или меньше за один месяц?

**Проверка:** 5 строк. Минимум в столбце `south` — 17.4.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE south <= 20;
```

</details>

### Задание 3

Напишите запрос, который покажет только строки, где название месяца — February.

**Проверка:** 47 строк.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name = 'February';
```

</details>

### Задание 4

Напишите запрос, который покажет только строки, где `month_name` начинается с буквы N или с буквы, которая в алфавите раньше.

**Проверка:** 470 строк, 10 разных месяцев. Нет September и October.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.us_housing_units
WHERE month_name < 'O';
```

</details>

### Задание 5

Напишите запрос, который считает сумму всех четырёх регионов в отдельном столбце.

**Проверка:** 564 строки. В первой строке (январь 1968) сумма равна 80.5.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west,
       south,
       midwest,
       northeast,
       west + south + midwest + northeast AS usa_total
FROM tutorial.us_housing_units;
```

</details>

### Задание 6

Напишите запрос, который вернёт все строки, где в регионе West построили больше домов, чем в Midwest и Northeast вместе.

**Проверка:** 104 строки.

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west,
       south,
       midwest,
       northeast
FROM tutorial.us_housing_units
WHERE west > (midwest + northeast);
```

</details>

### Задание 7

Напишите запрос, который считает, какой процент всех построенных домов США приходится на каждый регион. Верните только годы с 2000 и позже.

Подсказка: должно получиться четыре столбца с процентами.

**Проверка:** 180 строк. Для января 2000: `west_pct` = 24.45, `south_pct` = 52.36 (округление до сотых).

<details>
<summary>Решение</summary>

```sql
SELECT year,
       month,
       west / (west + south + midwest + northeast) * 100 AS west_pct,
       south / (west + south + midwest + northeast) * 100 AS south_pct,
       midwest / (west + south + midwest + northeast) * 100 AS midwest_pct,
       northeast / (west + south + midwest + northeast) * 100 AS northeast_pct
FROM tutorial.us_housing_units
WHERE year >= 2000;
```

</details>
