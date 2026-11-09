---
title: "Логические операторы"
description: "Обзор логических операторов SQL: LIKE, IN, BETWEEN, IS NULL, AND, OR, NOT, и знакомство с таблицей Billboard."
sidebar:
  order: 5
tags:
  - sql
  - practice
---

Чаще всего одного условия мало. Логические операторы помогают собрать из нескольких условий один фильтр. Этот урок — обзор. Каждый оператор разберём отдельно в следующих уроках.

## Операторы

| Оператор | Что делает | Урок |
|---|---|---|
| `LIKE` | ищет значения по шаблону | [LIKE](/practice/sql/basic/like/) |
| `IN` | оставляет значения из списка | [IN](/practice/sql/basic/in/) |
| `BETWEEN` | оставляет значения из диапазона | [BETWEEN](/practice/sql/basic/between/) |
| `IS NULL` | находит пустые значения | [IS NULL](/practice/sql/basic/is-null/) |
| `AND` | оба условия верны | [AND](/practice/sql/basic/and/) |
| `OR` | верно хотя бы одно условие | [OR](/practice/sql/basic/or/) |
| `NOT` | условие неверно | [NOT](/practice/sql/basic/not/) |

## Таблица Billboard

Для этих уроков нужна таблица `tutorial.billboard_top_100_year_end`. В ней итоговые годовые чарты Billboard: 100 лучших песен каждого года, с 1956 по 2013.

Столбцы:

| Столбец | Что в нём |
|---|---|
| `year` | год чарта |
| `year_rank` | место песни в конце года |
| `group_name` | полное имя исполнителя, как в чарте. Для совместных песен — несколько имён |
| `artist` | один исполнитель. У песни с гостями несколько строк |
| `song_name` | название песни |

Посмотрим на таблицу. Пока не думайте об `ORDER BY`, он будет в одном из следующих уроков:

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
ORDER BY year DESC, year_rank;
```

Обратите внимание на 2013 год. У песни Macklemore несколько строк, по одной на каждого исполнителя. Поэтому строк в таблице больше, чем 100 на год.

:::tip
Столбец `group_name` — это полное имя, например `Katy Perry featuring Snoop Dogg`. Столбец `artist` — один человек или группа: `Katy Perry`, `Snoop Dogg`. Для поиска по составу чаще берут `group_name` с `LIKE`.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет все строки таблицы `tutorial.billboard_top_100_year_end` за 2013 год.

**Проверка:** 144 строки в 2013 году. Первое место — Thrift Shop.

<details>
<summary>Решение</summary>

```sql
SELECT *
FROM tutorial.billboard_top_100_year_end
WHERE year = 2013;
```

</details>

### Задание 2

Напишите запрос, который покажет только столбцы `year`, `year_rank` и `song_name` для песен, занявших первое место в 2005 году.

**Проверка:** 1 уникальная песня, год 2005, `year_rank` = 1.

<details>
<summary>Решение</summary>

```sql
SELECT DISTINCT year,
       year_rank,
       song_name
FROM tutorial.billboard_top_100_year_end
WHERE year = 2005
  AND year_rank = 1;
```

</details>
