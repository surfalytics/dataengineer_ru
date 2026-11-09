---
title: "Скорость запросов"
description: "Как ускорять SQL-запросы: фильтровать данные раньше, уменьшать таблицы до JOIN и читать план запроса через EXPLAIN."
sidebar:
  order: 7
tags:
  - sql
  - practice
---

Быстрый запрос делает меньше работы. Цель настройки скорости: чтобы база обработала меньше строк и сделала меньше вычислений.

В уроке работаем с таблицей `benn.sample_event_table` (1 миллион событий пользователей за первое полугодие 2014) и таблицами `benn.college_football_players` и `benn.college_football_teams`.

## От чего зависит время запроса

Вы можете влиять на это:

- **Размер таблицы.** Чем больше строк, тем дольше.
- **JOIN.** Если JOIN сильно увеличивает число строк, запрос будет медленным.
- **Агрегации.** Свёртка строк требует больше вычислений, чем простое чтение.

Вы не можете влиять на это:

- другие пользователи, которые запускают запросы в то же время;
- настройки и версия базы.

:::note
DuckDB работает локально и очень быстро на таких объёмах. Разницу в секундах вы не увидите. Поэтому смотрите на план запроса и число обработанных строк. На больших данных в облачных базах разница будет заметна.
:::

## Сначала уменьшите таблицу

Фильтруйте данные как можно раньше. Для временных рядов хорошо работает ограничение по периоду:

```sql
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01';
```

`LIMIT` помогает при исследовании. Достаточно 100 строк, чтобы понять структуру данных:

```sql
SELECT *
FROM benn.sample_event_table
LIMIT 100;
```

### LIMIT и агрегации

`LIMIT` работает после агрегации. Поэтому он не ускорит такой запрос:

```sql
SELECT COUNT(*)
FROM benn.sample_event_table
LIMIT 100;
```

База всё равно посчитает все строки, а потом покажет одну строку. Чтобы посчитать только по 100 строкам, поставьте `LIMIT` в подзапрос:

```sql
SELECT COUNT(*)
FROM (
      SELECT *
      FROM benn.sample_event_table
      LIMIT 100
     ) sub;
```

:::caution
Так вы меняете результат. Используйте `LIMIT` только чтобы проверить логику. Итоговые цифры считайте на полных данных.
:::

Правило: ограничивайте данные там, где запрос выполняется первым. Это внутренний подзапрос, а не внешний.

## Сделайте JOIN проще

Тот же принцип: уменьшайте таблицы до `JOIN`, а не после. Вот запрос, который присоединяет команды к игрокам:

```sql
SELECT teams.conference AS conference,
       players.school_name,
       COUNT(1) AS players
FROM benn.college_football_players players
JOIN benn.college_football_teams teams
  ON teams.school_name = players.school_name
GROUP BY 1, 2;
```

В `benn.college_football_players` 6935 строк. Все они проверяются на совпадение. Сначала сожмите игроков до одной строки на школу. Таких школ 73:

```sql
SELECT players.school_name,
       COUNT(*) AS players
FROM benn.college_football_players players
GROUP BY 1;
```

Теперь `JOIN` обрабатывает 73 строки вместо 6935:

```sql
SELECT teams.conference,
       sub.*
FROM (
      SELECT players.school_name,
             COUNT(*) AS players
      FROM benn.college_football_players players
      GROUP BY 1
     ) sub
JOIN benn.college_football_teams teams
  ON teams.school_name = sub.school_name;
```

:::tip
Сначала добейтесь верного результата. Потом ускоряйте. Быстрый неверный запрос бесполезен.
:::

## EXPLAIN

`EXPLAIN` перед запросом показывает план: в каком порядке база выполнит шаги. Сам запрос не выполняется.

```sql
EXPLAIN
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
LIMIT 100;
```

План DuckDB — это дерево из блоков. Как его читать:

- Читайте снизу вверх. Нижний блок выполняется первым.
- `SEQ_SCAN` — чтение таблицы. Внутри блока строка `Filters` показывает фильтр по датам. Он применяется прямо при чтении.
- `STREAMING_LIMIT` — ограничение `LIMIT 100`. Оно останавливает чтение, когда набрано 100 строк.
- `PROJECTION` — выбор колонок.
- `~N rows` — оценка числа строк. Это только прикидка.
- `HASH_JOIN` и `HASH_GROUP_BY` встречаются в планах с `JOIN` и `GROUP BY`.

:::note
В Postgres `EXPLAIN` выглядит иначе. Это текст со строками `Seq Scan`, `Filter` и числами `cost=...`. Читают его тоже снизу вверх. В DuckDB `cost` нет, есть оценка числа строк.
:::

## EXPLAIN ANALYZE

`EXPLAIN ANALYZE` запускает запрос по-настоящему. Он показывает реальное число строк и время каждого шага:

```sql
EXPLAIN ANALYZE
SELECT *
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
LIMIT 100;
```

Вместо оценки `~N rows` вы увидите точные `N rows` и время в секундах. Обратите внимание на `SEQ_SCAN`. Он прочитал лишь несколько сотен строк, а не миллион. `LIMIT` остановил чтение.

Так работает практика: запустите `EXPLAIN ANALYZE`, найдите самый дорогой шаг, измените запрос, запустите снова и сравните.

## Практика

Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.

В этом уроке не было задач в оригинале. Ниже три задачи, которые проверяют тему.

### Задание 1

Посчитайте число событий в `benn.sample_event_table` за март 2014 по типам событий (`event_name`). Сначала самые частые. Потом добавьте `EXPLAIN` и найдите в плане строку `Filters`.

**Проверка:** 6 строк. Первая: `search_run` — 28937. Сумма по всем строкам — 171551.

<details>
<summary>Решение</summary>

```sql
SELECT event_name,
       COUNT(*) AS events
FROM benn.sample_event_table
WHERE event_date >= '2014-03-01'
  AND event_date < '2014-04-01'
GROUP BY 1
ORDER BY 2 DESC;
```

</details>

### Задание 2

Напишите запрос, который показывает конференцию, школу и число игроков. Сначала сожмите игроков по школам в подзапросе, потом присоедините `benn.college_football_teams`. Сначала школы с самым большим числом игроков, потом по алфавиту.

**Проверка:** 73 строки. Первая: `Auburn` (конференция `Southeastern`) — 110 игроков.

<details>
<summary>Решение</summary>

```sql
SELECT teams.conference,
       sub.school_name,
       sub.players
FROM (
      SELECT school_name,
             COUNT(*) AS players
      FROM benn.college_football_players
      GROUP BY 1
     ) sub
JOIN benn.college_football_teams teams
  ON teams.school_name = sub.school_name
ORDER BY sub.players DESC, sub.school_name;
```

</details>

### Задание 3

Запустите `EXPLAIN ANALYZE` для запроса `SELECT * FROM benn.sample_event_table LIMIT 100`. Посмотрите, сколько строк прочитал `TABLE_SCAN` и сколько строк прошло через `STREAMING_LIMIT`. Сравните с числом строк в таблице.

**Проверка:** через `STREAMING_LIMIT` проходит ровно 100 строк. `TABLE_SCAN` прочитал намного меньше миллиона строк.

<details>
<summary>Решение</summary>

```sql
EXPLAIN ANALYZE
SELECT *
FROM benn.sample_event_table
LIMIT 100;
```

</details>
