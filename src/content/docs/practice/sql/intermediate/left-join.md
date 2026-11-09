---
title: "LEFT JOIN"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "LEFT JOIN в SQL: примеры и задачи | Инжиниринг Данных"
description: "Как работает LEFT JOIN, чем он отличается от INNER JOIN и как с его помощью найти строки без пары."
sidebar:
  order: 13
tags:
  - sql
  - practice
---

`LEFT JOIN` оставляет все строки левой таблицы, даже если справа нет пары. Для таких строк столбцы правой таблицы заполнены `NULL`. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`.

## Сначала INNER JOIN

Посмотрим на обычное соединение компаний и покупок:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1
LIMIT 10;
```

Одна компания может появиться в списке дважды. Так бывает, если у неё две записи о покупке. Обе записи присоединяются к строке компании.

## Тот же запрос как LEFT JOIN

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1
LIMIT 10;
```

Теперь в результате много строк с `NULL` в столбцах `acquisitions_permalink` и `acquired_date`. Это компании, которых никто не купил.

Правило: `LEFT JOIN` возвращает все строки таблицы из `FROM`, независимо от того, есть ли пара в таблице из `LEFT JOIN`.

## Строки без пары

Частый приём: найти строки левой таблицы, у которых нет пары. Для этого фильтруем `NULL` из правой таблицы:

```sql
SELECT companies.permalink,
       companies.name
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE acquisitions.company_permalink IS NULL
LIMIT 10;
```

:::tip
Для проверки пары берите столбец-ключ правой таблицы. Он не бывает `NULL`, если пара есть.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Выполните `INNER JOIN` таблиц `tutorial.crunchbase_acquisitions` и `tutorial.crunchbase_companies`. Вместо списка строк посчитайте непустые значения ключа в каждой таблице.

**Проверка:** обе колонки равны 5941.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(companies.permalink) AS companies_rowcount,
       COUNT(acquisitions.company_permalink) AS acquisitions_rowcount
FROM tutorial.crunchbase_companies companies
JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>

### Задание 2

Измените запрос выше на `LEFT JOIN`. Обратите внимание на разницу в результатах.

**Проверка:** `companies_rowcount` — 66562, `acquisitions_rowcount` — 5941.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(companies.permalink) AS companies_rowcount,
       COUNT(acquisitions.company_permalink) AS acquisitions_rowcount
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

</details>

### Задание 3

Посчитайте по штатам число уникальных компаний и число уникальных купленных компаний. Не включайте строки, где штата нет. Отсортируйте по числу купленных компаний от большего к меньшему.

**Проверка:** первая строка: `CA`, 12900, 1937. Вторая: `MA`, 2542, 396.

<details>
<summary>Решение</summary>

```sql
SELECT companies.state_code,
       COUNT(DISTINCT companies.permalink) AS unique_companies,
       COUNT(DISTINCT acquisitions.company_permalink) AS unique_companies_acquired
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE companies.state_code IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;
```

</details>
