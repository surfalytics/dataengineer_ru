---
title: Self JOIN
description: Как соединять таблицу саму с собой с помощью псевдонимов и зачем это нужно.
sidebar:
  order: 20
tags:
  - sql
  - practice
---

Self JOIN соединяет таблицу саму с собой. Он нужен, когда надо сравнить строки одной таблицы между собой. Например: «компании, которые получили инвестицию из Великобритании после инвестиции из Японии». Работаем с `tutorial.crunchbase_investments_part1`. Подробнее о ней — в [описании данных](/practice/sql/datasets/).

## Как это пишется

Особого синтаксиса нет. Одну и ту же таблицу пишем дважды и даём разные псевдонимы:

```sql
SELECT DISTINCT japan_investments.company_name,
       japan_investments.company_permalink
FROM tutorial.crunchbase_investments_part1 japan_investments
JOIN tutorial.crunchbase_investments_part1 gb_investments
  ON japan_investments.company_name = gb_investments.company_name
 AND gb_investments.investor_country_code = 'GBR'
 AND gb_investments.funded_at > japan_investments.funded_at
WHERE japan_investments.investor_country_code = 'JPN'
ORDER BY 1;
```

Как читать запрос:

- `japan_investments` — инвестиции японских инвесторов (фильтр в `WHERE`).
- `gb_investments` — инвестиции британских инвесторов (фильтр в `ON`).
- Строки соединяются по одной и той же компании.
- Условие `gb_investments.funded_at > japan_investments.funded_at` оставляет случаи, когда британская инвестиция была позже японской.

Запрос вернёт 13 компаний. Первая в списке: `Aperto Networks`.

:::note
Мы используем только первую половину таблицы инвестиций. Остальные данные лежат в `tutorial.crunchbase_investments_part2`. Поэтому в результате лишь часть компаний.
:::

:::tip
Даты здесь хранятся строками `YYYY-MM-DD`. Для таких строк сравнение `>` работает правильно: формат сортируется по алфавиту так же, как по времени.
:::

## Другие примеры

Self JOIN нужен не только для дат. Типичные случаи:

- Сотрудники и руководители в одной таблице.
- Пары товаров, которые покупают вместе.
- Цепочки: компания, которую купили, а потом она сама купила другую.

## Что дальше

Вы прошли средний уровень SQL. Дальше идёт продвинутый уровень: типы данных, подзапросы, оконные функции и другое.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Найдите компании, которые получили инвестицию от инвестора из Великобритании (`GBR`) позже, чем от инвестора из США (`USA`). Используйте `tutorial.crunchbase_investments_part1` и соедините компании по `company_permalink`. Посчитайте уникальные компании.

**Проверка:** 372.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT usa_investments.company_permalink) AS companies
FROM tutorial.crunchbase_investments_part1 usa_investments
JOIN tutorial.crunchbase_investments_part1 gb_investments
  ON usa_investments.company_permalink = gb_investments.company_permalink
 AND gb_investments.investor_country_code = 'GBR'
 AND gb_investments.funded_at > usa_investments.funded_at
WHERE usa_investments.investor_country_code = 'USA';
```

</details>

### Задание 2

Найдите компании, у которых был раунд типа `seed`, а позже раунд типа `venture`. Используйте `tutorial.crunchbase_investments_part1`. Посчитайте уникальные компании.

**Проверка:** 1518.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT seed.company_permalink) AS companies
FROM tutorial.crunchbase_investments_part1 seed
JOIN tutorial.crunchbase_investments_part1 venture
  ON seed.company_permalink = venture.company_permalink
 AND venture.funding_round_type = 'venture'
 AND venture.funded_at > seed.funded_at
WHERE seed.funding_round_type = 'seed';
```

</details>

### Задание 3

В `tutorial.crunchbase_acquisitions` найдите компании, которых купили, а потом они сами стали покупателями. Для этого соедините таблицу саму с собой: `company_permalink` одной копии должен совпасть с `acquirer_permalink` другой. Посчитайте уникальные такие компании.

**Проверка:** 1345.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(DISTINCT bought.company_permalink) AS companies
FROM tutorial.crunchbase_acquisitions bought
JOIN tutorial.crunchbase_acquisitions bought_others
  ON bought.company_permalink = bought_others.acquirer_permalink;
```

</details>
