---
title: Внешние соединения (OUTER JOIN)
description: Обзор внешних соединений LEFT, RIGHT и FULL OUTER JOIN и знакомство с данными Crunchbase.
sidebar:
  order: 12
tags:
  - sql
  - practice
---

`INNER JOIN` теряет строки без пары. Внешние соединения (`OUTER JOIN`) могут их сохранить. Для таких уроков нужны данные, где пары есть не у всех строк. Мы возьмём данные Crunchbase: каталог стартапов, покупок и инвестиций. Подробнее о таблицах — в [описании данных](/practice/sql/datasets/).

## Виды внешних соединений

| Соединение | Что вернёт |
|---|---|
| `LEFT JOIN` | Все строки левой таблицы. Для строк без пары справа будет `NULL` |
| `RIGHT JOIN` | Все строки правой таблицы. Для строк без пары слева будет `NULL` |
| `FULL OUTER JOIN` | Все строки обеих таблиц |
| `INNER JOIN` | Только строки с парой в обеих таблицах |

Слово `OUTER` можно не писать. `LEFT JOIN` — то же, что `LEFT OUTER JOIN`. `FULL JOIN` — то же, что `FULL OUTER JOIN`.

Уроки дальше разбирают каждый вид отдельно:

- [LEFT JOIN](/practice/sql/intermediate/left-join/)
- [RIGHT JOIN](/practice/sql/intermediate/right-join/)
- [FULL OUTER JOIN](/practice/sql/intermediate/full-outer-join/)

## Данные Crunchbase

Первая таблица — компании. Одна строка на компанию.

```sql
SELECT *
FROM tutorial.crunchbase_companies
LIMIT 5;
```

Столбец `permalink` — уникальный идентификатор компании.

Вторая таблица — покупки компаний. Одна строка на покупку.

```sql
SELECT *
FROM tutorial.crunchbase_acquisitions
LIMIT 5;
```

Связь таблиц:

- `crunchbase_acquisitions.company_permalink` ссылается на `crunchbase_companies.permalink`. Так мы получаем данные о купленной компании.
- `crunchbase_acquisitions.acquirer_permalink` тоже ссылается на `crunchbase_companies.permalink`. Так мы получаем данные о покупателе.

Какой ключ брать, зависит от вопроса: интересует купленная компания или покупатель.

Такая схема встречается часто. Например, в таблице писем есть `sender_email` и `recipient_email`. Оба ссылаются на одну таблицу людей.

:::caution
Данные Crunchbase реальные и неидеальные. В таблице покупок 13027 строк ссылаются на компании, которых нет в `crunchbase_companies`. Поэтому внутреннее соединение теряет много строк. Это нормально для учебных данных, но в работе стоит разбираться, почему так.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Посчитайте строки в таблицах `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions` двумя отдельными запросами или одним запросом с двумя подзапросами.

**Проверка:** компаний 66368, покупок 18968.

<details>
<summary>Решение</summary>

```sql
SELECT (SELECT COUNT(*) FROM tutorial.crunchbase_companies) AS companies_rows,
       (SELECT COUNT(*) FROM tutorial.crunchbase_acquisitions) AS acquisitions_rows;
```

</details>

### Задание 2

Покупатель в таблице покупок указан в `acquirer_permalink`. Соедините `tutorial.crunchbase_acquisitions` с `tutorial.crunchbase_companies` по покупателю (`INNER JOIN`) и посчитайте строки.

**Проверка:** 6935.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS acquisitions_with_known_acquirer
FROM tutorial.crunchbase_acquisitions acquisitions
JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.acquirer_permalink;
```

</details>

### Задание 3

Теперь повторите соединение из задания 2 как `LEFT JOIN` от таблицы покупок. Сколько строк получилось? Сколько из них без покупателя в таблице компаний?

**Проверка:** всего 18968 строк, из них без пары 12033.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(*) AS all_rows,
       COUNT(*) - COUNT(companies.permalink) AS no_acquirer_in_companies
FROM tutorial.crunchbase_acquisitions acquisitions
LEFT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.acquirer_permalink;
```

</details>
