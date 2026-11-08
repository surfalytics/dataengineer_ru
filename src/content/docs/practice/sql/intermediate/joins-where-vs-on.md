---
title: Фильтр в WHERE или в ON
description: Чем отличается условие в ON от условия в WHERE при внешних соединениях и как это влияет на результат.
sidebar:
  order: 15
tags:
  - sql
  - practice
---

В запросе с `JOIN` условие можно поставить в `ON` или в `WHERE`. Для `INNER JOIN` результат одинаковый. Для `LEFT JOIN` результат разный. В этом уроке разберём почему. Работаем с `tutorial.crunchbase_companies`, `tutorial.crunchbase_acquisitions` и `tutorial.crunchbase_investments`. Подробнее о них — в [описании данных](/practice/sql/datasets/).

## Фильтр в ON

Условие в `ON` применяется **до** соединения. Оно работает как `WHERE`, но только для одной таблицы.

Сначала запрос без фильтра:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
ORDER BY 1;
```

Теперь добавим условие в `ON`. Мы исключаем из правой таблицы покупку компании `1000memories`:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
 AND acquisitions.company_permalink != '/organization/1000memories'
ORDER BY 1;
```

Что видно в результате:

- Компания `1000memories` осталась в левом столбце.
- В столбцах из таблицы покупок для неё стоит `NULL`.
- Строка осталась, потому что `LEFT JOIN` сохраняет левую таблицу.

## Фильтр в WHERE

`WHERE` работает **после** соединения. Он убирает строки целиком, из обеих таблиц.

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink
WHERE acquisitions.company_permalink != '/organization/1000memories'
   OR acquisitions.company_permalink IS NULL
ORDER BY 1;
```

Теперь компании `1000memories` в результате нет совсем.

Мы добавили `OR ... IS NULL`. Без него `WHERE` убрал бы и все строки с `NULL` справа, то есть всех непроданных компаний. Сравнение с `NULL` никогда не бывает истинным.

| Вариант | Число строк | Что произошло |
|---|---|---|
| Без фильтра | 66562 | Все компании и все покупки |
| Фильтр в `ON` | 66562 | `1000memories` осталась, покупка обнулена |
| Фильтр в `WHERE` | 66561 | `1000memories` пропала |

:::caution
Условие в `WHERE` по столбцу правой таблицы превращает `LEFT JOIN` в `INNER JOIN`. Строки с `NULL` не пройдут фильтр. Если нужно сохранить левую таблицу, ставьте условие в `ON`.
:::

## Практика

Для этих задач мы берём новую таблицу `tutorial.crunchbase_investments`. В ней одна строка на инвестицию. У компании может быть несколько инвестиций. Один инвестор может вложиться в одну компанию несколько раз. Столбец `company_permalink` связан с `permalink` в `tutorial.crunchbase_companies`.

Перед решением изучите таблицу сами: посмотрите строки, посчитайте уникальные значения.

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Покажите название компании, её статус (`status`, из таблицы компаний) и число уникальных инвесторов. Отсортируйте по числу инвесторов от большего к меньшему. Оставьте только компании из штата New York (`NY`).

**Проверка:** 3947 строк. Первая строка: `Fab`, `acquired`, 34 (у `SeatGeek` тоже 34).

<details>
<summary>Решение</summary>

```sql
SELECT companies.name AS company_name,
       companies.status,
       COUNT(DISTINCT investments.investor_name) AS unique_investors
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
WHERE companies.state_code = 'NY'
GROUP BY 1, 2
ORDER BY 3 DESC;
```

</details>

### Задание 2

Составьте список инвесторов по числу компаний, в которые они вложились. Добавьте строку для компаний без инвесторов. Отсортируйте от большего числа к меньшему.

**Проверка:** 30189 строк. Первая строка: `No Investors`, 21642. Дальше: `Y Combinator` — 758.

<details>
<summary>Решение</summary>

```sql
SELECT CASE WHEN investments.investor_name IS NULL THEN 'No Investors'
            ELSE investments.investor_name END AS investor,
       COUNT(DISTINCT companies.permalink) AS companies_invested_in
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_investments investments
  ON companies.permalink = investments.company_permalink
GROUP BY 1
ORDER BY 2 DESC;
```

</details>
