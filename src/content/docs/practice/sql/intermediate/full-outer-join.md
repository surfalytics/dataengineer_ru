---
title: "FULL OUTER JOIN"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "FULL OUTER JOIN в SQL: примеры и задачи | Инжиниринг Данных"
description: "Как работает FULL OUTER JOIN и как с его помощью измерить пересечение двух таблиц."
sidebar:
  order: 16
tags:
  - sql
  - practice
---

`FULL OUTER JOIN` возвращает все строки обеих таблиц. Совпавшие строки соединяются. Несовпавшие остаются с `NULL` на месте другой таблицы. Он нужен реже других соединений. Чаще всего его используют вместе с агрегатами, чтобы понять, насколько таблицы пересекаются. Работаем с таблицами Crunchbase.

## Как работает

Запись `FULL JOIN` и `FULL OUTER JOIN` — одно и то же.

| Строка | Есть слева | Есть справа |
|---|---|---|
| Только слева | да | `NULL` |
| Совпала | да | да |
| Только справа | `NULL` | да |

## Измеряем пересечение

Сколько компаний есть только в таблице компаний, сколько в обеих таблицах и сколько только в таблице покупок:

```sql
SELECT COUNT(CASE WHEN companies.permalink IS NOT NULL AND acquisitions.company_permalink IS NULL
                  THEN companies.permalink ELSE NULL END) AS companies_only,
       COUNT(CASE WHEN companies.permalink IS NOT NULL AND acquisitions.company_permalink IS NOT NULL
                  THEN companies.permalink ELSE NULL END) AS both_tables,
       COUNT(CASE WHEN companies.permalink IS NULL AND acquisitions.company_permalink IS NOT NULL
                  THEN acquisitions.company_permalink ELSE NULL END) AS acquisitions_only
FROM tutorial.crunchbase_companies companies
FULL JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

| companies_only | both_tables | acquisitions_only |
|---|---|---|
| 60621 | 5941 | 13027 |

Обратите внимание: третий столбец считает ключ из таблицы покупок. Если считать `companies.permalink`, получится 0, потому что в таких строках он `NULL`.

В таблице покупок совпала лишь часть строк. В реальной работе стоит посмотреть на несовпавшие строки и понять причину. Возможно, нужны другие данные.

:::tip
Хотите узнать, какие строки есть только в одной таблице? Используйте `FULL JOIN` с условием `WHERE левый_ключ IS NULL OR правый_ключ IS NULL`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

Для задачи используется таблица инвестиций Crunchbase. Мы разделили её на две части: `tutorial.crunchbase_investments_part1` и `tutorial.crunchbase_investments_part2`.

### Задание 1

Соедините `tutorial.crunchbase_companies` и `tutorial.crunchbase_investments_part1` через `FULL JOIN`. Посчитайте, сколько строк есть только в компаниях, в обеих таблицах и только в инвестициях. Используйте подход из примера выше.

**Проверка:** `companies_only` — 43618, `both_tables` — 85072, `investments_only` — 1.

<details>
<summary>Решение</summary>

```sql
SELECT COUNT(CASE WHEN companies.permalink IS NOT NULL AND investments.company_permalink IS NULL
                  THEN companies.permalink ELSE NULL END) AS companies_only,
       COUNT(CASE WHEN companies.permalink IS NOT NULL AND investments.company_permalink IS NOT NULL
                  THEN companies.permalink ELSE NULL END) AS both_tables,
       COUNT(CASE WHEN companies.permalink IS NULL AND investments.company_permalink IS NOT NULL
                  THEN investments.company_permalink ELSE NULL END) AS investments_only
FROM tutorial.crunchbase_companies companies
FULL JOIN tutorial.crunchbase_investments_part1 investments
  ON companies.permalink = investments.company_permalink;
```

</details>
