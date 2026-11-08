---
title: JOIN по нескольким ключам
description: Как соединять таблицы по нескольким условиям в ON и когда это полезно.
sidebar:
  order: 19
tags:
  - sql
  - practice
---

В `ON` можно связать таблицы сразу по нескольким столбцам. Условия соединяют через `AND`. Это нужно в двух случаях: когда одного ключа мало, чтобы однозначно найти строку, и когда нужно дополнительно проверить данные. Работаем с таблицами Crunchbase. Подробнее — в [описании данных](/practice/sql/datasets/).

## Два условия в ON

```sql
SELECT companies.permalink,
       companies.name,
       investments.company_name,
       investments.company_permalink
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND companies.name = investments.company_name;
```

Здесь строки соединяются, только если совпали и `permalink`, и название компании.

В наших данных результат такой же, как при соединении только по `permalink`: 128690 строк. Название везде совпадает с ключом, поэтому второе условие ничего не отсекает.

## Зачем нужен второй ключ

- **Составной ключ.** Если строку определяют два столбца (например, `год` и `страна`), нужны оба.
- **Проверка данных.** Второе условие убирает ложные совпадения, если ключ в одной из таблиц загрязнён.
- **Скорость.** Иногда лишнее условие помогает базе быстрее найти строки. На маленьких таблицах эффект почти не виден.

:::tip
Если после добавления второго условия число строк уменьшилось, значит, часть строк совпала по первому ключу, но не по второму. Это повод изучить данные.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Выполните `LEFT JOIN` таблицы `tutorial.crunchbase_companies` с `tutorial.crunchbase_investments_part1` по двум ключам: `permalink = company_permalink` и `name = company_name`. Посчитайте строки результата.

**Проверка:** 128690.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS rows_count
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink
 AND companies.name = investments.company_name;
```

</details>

### Задание 2

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` (`INNER JOIN`) по `permalink = company_permalink` и по категории: `category_code = company_category_code`. Посчитайте строки. Сравните с соединением только по `permalink`.

**Проверка:** с двумя ключами 5784, только по `permalink` 5941. Разница — 157 строк, где категория не совпала.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS two_keys
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND companies.category_code = acquisitions.company_category_code;

SELECT COUNT(*) AS one_key
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>
