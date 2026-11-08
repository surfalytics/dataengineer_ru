---
title: "JOIN"
description: "Как объединять данные из нескольких таблиц с помощью JOIN и ON, и зачем нужны псевдонимы таблиц."
sidebar:
  order: 10
tags:
  - sql
  - practice
---

До сих пор мы работали с одной таблицей. Но данные обычно лежат в нескольких таблицах, и `JOIN` соединяет их. Это главная сила SQL. В этом уроке работаем с таблицами `benn.college_football_players` и `benn.college_football_teams`.

## Зачем нужны JOIN

Реляционная база хранит разные сущности в разных таблицах. Так данные не повторяются.

- В таблице игроков есть школа игрока, но нет конференции школы.
- В таблице команд есть конференция, но нет игроков.
- Школа (`school_name`) есть в обеих таблицах. Это ключ для связи.

Чтобы узнать, в какой конференции игроки тяжелее всех, нужны обе таблицы.

## Устройство JOIN

```sql
SELECT teams.conference AS conference,
       AVG(players.weight) AS average_weight
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.conference
ORDER BY AVG(players.weight) DESC;
```

Разберём запрос по частям:

| Часть | Что делает |
|---|---|
| `FROM ... players` | Первая (левая) таблица |
| `JOIN ... teams` | Вторая таблица |
| `ON teams.school_name = players.school_name` | Условие: какие строки соединять |
| `GROUP BY`, `ORDER BY` | Как обычно: группируют и сортируют результат |

## Псевдонимы таблиц

Имя `benn.college_football_players` длинное. Дайте таблице короткое имя: напишите его через пробел после имени таблицы.

```sql
SELECT players.player_name,
       players.school_name
FROM benn.college_football_players players
LIMIT 5;
```

После этого столбцы указывают через псевдоним: `players.player_name`. Это то же самое, что `benn.college_football_players.player_name`.

:::tip
Всегда пишите столбцы с псевдонимом таблицы, даже если имя не повторяется. Запрос легче читать. И он не сломается, когда в другой таблице появится столбец с таким же именем.
:::

## JOIN и ON

`ON` говорит базе, как сопоставить строки двух таблиц. Обычно это равенство ключей. Каждая строка слева ищет подходящие строки справа.

```sql
SELECT players.player_name,
       players.school_name,
       teams.conference
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

:::caution
Если забыть `ON`, DuckDB вернёт ошибку. А если условие неверное, получится много лишних строк. Всегда проверяйте число строк после `JOIN`.
:::

Какой именно тип соединения выбрать, расскажут следующие уроки: [INNER JOIN](/practice/sql/intermediate/inner-join/), [LEFT JOIN](/practice/sql/intermediate/left-join/) и другие.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который вернёт школу, имя игрока, позицию и вес каждого игрока из штата Georgia (`GA`). Отсортируйте по весу от самого тяжёлого к самому лёгкому. Дайте таблице псевдоним и указывайте все столбцы через него.

**Проверка:** 335 строк. Первая строка: Auburn, Brian Barnes, DL, 331.

<details>
<summary>Решение</summary>

```sql
SELECT players.school_name,
       players.player_name,
       players.position,
       players.weight
FROM benn.college_football_players players
WHERE players.state = 'GA'
ORDER BY players.weight DESC;
```

</details>

### Задание 2

Посчитайте число игроков в каждой конференции. Для этого соедините игроков с командами. Сначала конференция с наибольшим числом игроков.

**Проверка:** первая строка: `Southeastern`, 799.

<details>
<summary>Решение</summary>

```sql
SELECT teams.conference,
       COUNT(*) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.conference
ORDER BY players DESC;
```

</details>
