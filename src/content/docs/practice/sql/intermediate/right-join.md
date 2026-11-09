---
title: "RIGHT JOIN"
description: "Как работает RIGHT JOIN и почему его почти всегда можно заменить на LEFT JOIN."
sidebar:
  order: 14
tags:
  - sql
  - practice
---

`RIGHT JOIN` — зеркало `LEFT JOIN`. Он оставляет все строки правой таблицы. Из левой таблицы берутся только строки с парой. В уроке работаем с `tutorial.crunchbase_companies` и `tutorial.crunchbase_acquisitions`.

## RIGHT JOIN и LEFT JOIN дают одно и то же

Этот запрос оставляет все компании:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_companies companies
LEFT JOIN tutorial.crunchbase_acquisitions acquisitions
  ON companies.permalink = acquisitions.company_permalink;
```

Поменяйте таблицы местами и замените `LEFT` на `RIGHT`. Результат тот же:

```sql
SELECT companies.permalink AS companies_permalink,
       companies.name AS companies_name,
       acquisitions.company_permalink AS acquisitions_permalink,
       acquisitions.acquired_at AS acquired_date
FROM tutorial.crunchbase_acquisitions acquisitions
RIGHT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.company_permalink;
```

В обоих запросах все компании сохранены. Меняется только порядок таблиц.

## Какой выбрать

- `RIGHT JOIN` используют редко. Любой запрос можно переписать через `LEFT JOIN`, поменяв таблицы местами.
- Принято всегда писать `LEFT JOIN`. Так запрос легче читать и проверять: главная таблица всегда в `FROM`.
- Технического запрета на `RIGHT JOIN` нет.

Записи `LEFT OUTER JOIN` и `RIGHT OUTER JOIN` — то же самое, что `LEFT JOIN` и `RIGHT JOIN`.

:::tip
Если видите в чужом запросе `RIGHT JOIN`, мысленно поменяйте таблицы местами. Станет проще понять, какие строки сохраняются.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Перепишите запрос из урока про [LEFT JOIN](/practice/sql/intermediate/left-join/), где вы считали все и купленные компании по штатам. Используйте `RIGHT JOIN` вместо `LEFT JOIN`. Результат должен быть таким же.

**Проверка:** первая строка: `CA`, 12900, 1937. Вторая: `MA`, 2542, 396.

<details>
<summary>Решение</summary>

```sql
SELECT companies.state_code,
       COUNT(DISTINCT companies.permalink) AS unique_companies,
       COUNT(DISTINCT acquisitions.company_permalink) AS acquired_companies
FROM tutorial.crunchbase_acquisitions acquisitions
RIGHT JOIN tutorial.crunchbase_companies companies
  ON companies.permalink = acquisitions.company_permalink
WHERE companies.state_code IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;
```

</details>
