---
title: "INNER JOIN"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "INNER JOIN в SQL: примеры и задачи | Инжиниринг Данных"
description: "Как работает INNER JOIN, какие строки он оставляет и как не запутаться в одинаковых именах столбцов."
sidebar:
  order: 11
tags:
  - sql
  - practice
---

`INNER JOIN` оставляет только строки, у которых нашлась пара в обеих таблицах. Это тип соединения по умолчанию. В уроке работаем с `benn.college_football_players` и `benn.college_football_teams`.

## Как работает INNER JOIN

Запись `JOIN` и `INNER JOIN` — одно и то же.

```sql
SELECT players.player_name,
       teams.conference
FROM benn.college_football_players players
INNER JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name;
```

Правила:

- Игрок, чьей школы нет в таблице команд, не попадёт в результат.
- Команда, у которой нет игроков, тоже не попадёт.
- Это пересечение двух таблиц.

Если в таблице команд три строки с одним названием школы, каждый игрок этой школы появится три раза. Строки умножаются.

:::caution
Если число строк после `JOIN` стало больше, чем было, значит, ключ в одной из таблиц не уникален. Проверьте это сразу.
:::

В наших данных у каждого игрока есть команда. Поэтому `INNER JOIN` вернёт все 6935 строк.

## Одинаковые имена столбцов

В обеих таблицах есть столбец `school_name`. Если взять `players.*` и `teams.*`, в результате будет два столбца с одним именем. Это неудобно.

```sql
SELECT players.*,
       teams.*
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

Чтобы избежать путаницы, называйте столбцы через `AS`:

```sql
SELECT players.school_name AS players_school_name,
       teams.school_name AS teams_school_name
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
LIMIT 5;
```

:::note
Если сохранить такой результат в таблицу, DuckDB добавит к повтору суффикс: `school_name_1`. В других базах поведение другое. Лучше всегда задавать псевдонимы.
:::

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

### Задание 1

Напишите запрос, который покажет имена игроков, названия школ и конференции для школ из дивизиона `FBS (Division I-A Teams)`.

**Проверка:** 5089 строк. Среди строк есть: Jamal Sullivan, Alabama, Southeastern.

<details>
<summary>Решение</summary>

```sql
SELECT players.player_name,
       players.school_name,
       teams.conference
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
WHERE teams.division = 'FBS (Division I-A Teams)';
```

</details>

### Задание 2

Посчитайте игроков в каждом дивизионе.

**Проверка:** 2 строки: `FBS (Division I-A Teams)` — 5089, `FCS (Division I-AA Teams)` — 1846.

<details>
<summary>Решение</summary>

```sql
SELECT teams.division,
       COUNT(*) AS players
FROM benn.college_football_players players
INNER JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY teams.division
ORDER BY teams.division;
```

</details>
