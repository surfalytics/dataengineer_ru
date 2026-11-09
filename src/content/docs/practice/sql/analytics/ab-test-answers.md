---
title: "Кейс 3: разбор"
description: "Разбор кейса о проверке A/B-теста Yammer. Дополнительные метрики, ошибка в распределении по группам и честное сравнение."
sidebar:
  order: 7
next:
  label: "Продвинутый SQL"
tags:
  - sql
  - practice
---

:::caution
Открывайте после того, как попробовали сами. Сначала запишите свои гипотезы и проверки. Потом сравните с нашими.
:::

Вернитесь к [условию кейса](/practice/sql/analytics/ab-test/), если нужно вспомнить задачу.

## Гипотезы

Сначала гипотезы, потом данные. Иначе вы всегда подтвердите первое объяснение, которое нашли.

| Гипотеза | Как проверить |
|---|---|
| Метрика неверная или неполная. Публикации растут, но польза для клиентов может не расти. | Посмотреть другие метрики: входы, дни активности. |
| Тест посчитан неверно. | Пересчитать средние и значимость, проверить формулы. |
| Пользователей неправильно распределили по группам. Группы не случайные. | Сравнить состав групп: новые и старые пользователи, устройства, страны. |
| Есть скрытый фактор или взаимодействие. Функция меняет что-то ещё. | Разбить по когортам: устройства, тип пользователя, новые и старые. |

:::note
Пример неверной метрики: огромная кнопка «Написать сообщение» точно увеличит число публикаций. Но Yammer она, скорее всего, не поможет.
:::

## Шаг 0. Воспроизведите результат

Нужен расчёт по пользователям. Для каждого пользователя из эксперимента считаем сообщения, входы и дни активности с момента попадания в группу до 1 июля. Пользователь, который не написал ни одного сообщения, остаётся в данных с нулём (`LEFT JOIN`).

Мы также помечаем пользователя как нового (`new`), если он активирован в июне, и существующего (`existing`) в остальных случаях. Пригодится на шаге 3.

```sql
CREATE TEMP TABLE ab_users AS
SELECT ex.user_id,
       ex.experiment_group,
       CASE WHEN u.activated_at >= '2014-06-01' THEN 'new' ELSE 'existing' END AS user_kind,
       COUNT(e.user_id) FILTER (WHERE e.event_name = 'send_message') AS messages,
       COUNT(e.user_id) FILTER (WHERE e.event_name = 'login') AS logins,
       COUNT(DISTINCT e.occurred_at::DATE) AS days_engaged
FROM tutorial.yammer_experiments ex
JOIN tutorial.yammer_users u ON u.user_id = ex.user_id
LEFT JOIN tutorial.yammer_events e
  ON e.user_id = ex.user_id
 AND e.event_type = 'engagement'
 AND e.occurred_at >= ex.occurred_at
 AND e.occurred_at < '2014-07-01'
WHERE ex.experiment = 'publisher_update'
GROUP BY ex.user_id, ex.experiment_group, user_kind;
```

Теперь итоговая таблица теста. Для t-статистики используем средние и стандартные отклонения двух групп:

```sql
-- не запускать отдельно: нужна таблица ab_users
WITH g AS (
  SELECT experiment_group,
         COUNT(*) AS users,
         AVG(messages) AS average,
         STDDEV_SAMP(messages) AS stdev
  FROM ab_users
  GROUP BY 1
), c AS (
  SELECT * FROM g WHERE experiment_group = 'control_group'
)
SELECT g.experiment_group,
       g.users,
       ROUND(g.average, 3) AS average,
       ROUND(g.average - c.average, 3) AS rate_difference,
       ROUND(g.average / c.average - 1, 3) AS rate_lift,
       ROUND((g.average - c.average)
             / SQRT(g.stdev ^ 2 / g.users + c.stdev ^ 2 / c.users), 2) AS t_stat
FROM g CROSS JOIN c
ORDER BY 1;
```

| Группа | Пользователей | Среднее | Разница | Рост | t_stat |
|---|---:|---:|---:|---:|---:|
| control_group | 1783 | 2.189 | 0 | 0% | 0 |
| test_group | 1042 | 3.385 | 1.196 | +54.6% | 10.42 |

Это исходный результат: +55% и очень большая значимость (`t_stat` намного больше 2).

## Шаг 1. Другие метрики

Одних сообщений мало. Нужны метрики, которые показывают пользу. В Yammer главная такая метрика — частота входов. Добавим дни активности: в сколько разных дней пользователь заходил.

```sql
-- не запускать отдельно: нужна таблица ab_users
SELECT experiment_group,
       ROUND(AVG(messages), 2) AS avg_messages,
       ROUND(AVG(logins), 2) AS avg_logins,
       ROUND(AVG(days_engaged), 2) AS avg_days_engaged
FROM ab_users
GROUP BY 1
ORDER BY 1;
```

| Группа | Сообщений | Входов | Дней активности |
|---|---:|---:|---:|
| control_group | 2.19 | 3.83 | 3.90 |
| test_group | 3.38 | 4.37 | 4.37 |

Вывод: входов больше, дней активности тоже больше. Если бы входы росли, а дни были бы без изменений, это могло значить, что пользователи заходят и сразу выходят. Возможно, ошибка входа. Здесь такого нет. По метрикам всё хорошо.

Значит, проблема не в выборе метрики.

## Шаг 2. Метод расчёта

Спорить о математике можно: односторонний или двусторонний тест, размер выборки, форма распределения. Но на этот результат такие выборы не повлияют.

Зато в тесте есть ошибка метода. Он смешивает новых и существующих пользователей и считает все сообщения до конца июня.

- Пользователь, зарегистрированный в январе, мог писать весь месяц.
- Пользователь, зарегистрированный за день до конца теста, почти не имел времени писать.

Нужно считать новых и существующих отдельно. Так величины сравнимы. Так же можно проверить эффект новизны: опытные пользователи могут пробовать функцию просто потому, что она новая. Для новых пользователей публикатор не «новый», они не знают старого.

## Шаг 3. Как распределили пользователей

Посмотрим на группы с учётом возраста пользователя:

```sql
-- не запускать отдельно: нужна таблица ab_users
SELECT user_kind,
       experiment_group,
       COUNT(*) AS users,
       ROUND(AVG(messages), 2) AS avg_messages
FROM ab_users
GROUP BY 1, 2
ORDER BY 1, 2;
```

| Тип | Группа | Пользователей | Сообщений в среднем |
|---|---|---:|---:|
| existing | control_group | 1076 | 2.65 |
| existing | test_group | 1042 | 3.38 |
| new | control_group | 707 | 1.49 |

Это и есть ошибка. В тестовой группе нет ни одного нового пользователя. Все 707 новых пользователей попали в контрольную группу.

Чем это плохо:

- Новые пользователи пишут меньше, потому что у них мало времени. Это не связано с версией публикатора.
- Все они в контроле, поэтому среднее контроля занижено.
- Часть «роста» создана ошибкой в распределении, а не новой функцией.

:::caution
Это типичная ошибка A/B-тестов. Если группы не случайные, вывод теста нельзя принимать. Всегда проверяйте состав групп до анализа результата.
:::

## Шаг 4. Честное сравнение

Сравним только существующих пользователей. У них у обоих групп сопоставимое время для публикаций:

```sql
-- не запускать отдельно: нужна таблица ab_users
WITH g AS (
  SELECT experiment_group,
         COUNT(*) AS users,
         AVG(messages) AS average,
         STDDEV_SAMP(messages) AS stdev
  FROM ab_users
  WHERE user_kind = 'existing'
  GROUP BY 1
), c AS (
  SELECT * FROM g WHERE experiment_group = 'control_group'
)
SELECT g.experiment_group,
       g.users,
       ROUND(g.average, 3) AS average,
       ROUND(g.average - c.average, 3) AS rate_difference,
       ROUND(g.average / c.average - 1, 3) AS rate_lift,
       ROUND((g.average - c.average)
             / SQRT(g.stdev ^ 2 / g.users + c.stdev ^ 2 / c.users), 2) AS t_stat
FROM g CROSS JOIN c
ORDER BY 1;
```

| Группа | Пользователей | Среднее | Разница | Рост | t_stat |
|---|---:|---:|---:|---:|---:|
| control_group | 1076 | 2.650 | 0 | 0% | 0 |
| test_group | 1042 | 3.385 | 0.735 | +27.7% | 5.88 |

Вывод: рост упал с +55% до +28%. Но он остаётся значимым (`t_stat` 5.88).

Другие метрики на тех же существующих пользователях:

```sql
-- не запускать отдельно: нужна таблица ab_users
SELECT experiment_group,
       ROUND(AVG(messages), 2) AS avg_messages,
       ROUND(AVG(logins), 2) AS avg_logins,
       ROUND(AVG(days_engaged), 2) AS avg_days_engaged
FROM ab_users
WHERE user_kind = 'existing'
GROUP BY 1
ORDER BY 1;
```

| Группа | Сообщений | Входов | Дней активности |
|---|---:|---:|---:|
| control_group | 2.65 | 3.59 | 3.70 |
| test_group | 3.38 | 4.37 | 4.37 |

Тестовая группа впереди по всем трём метрикам, но разрыв меньше.

## Шаг 5. Другие когорты

Исправили одну проблему. Это не значит, что других нет. Проблем может быть несколько, и они часто связаны. Типовые когорты для проверки: устройство и тип пользователя (пишет контент или читает).

Среднее число сообщений у существующих пользователей по устройствам:

```sql
-- не запускать отдельно: нужна таблица ab_users
SELECT CASE WHEN ex.device IN ('iphone 5', 'iphone 5s', 'iphone 4s',
              'samsung galaxy s4', 'nexus 5', 'htc one', 'nokia lumia 635',
              'samsung galaxy note', 'amazon fire phone') THEN 'phone'
            WHEN ex.device IN ('ipad air', 'ipad mini', 'nexus 7', 'nexus 10',
              'kindle fire', 'samsung galaxy tablet') THEN 'tablet'
            ELSE 'computer' END AS device_class,
       a.experiment_group,
       COUNT(*) AS users,
       ROUND(AVG(a.messages), 2) AS avg_messages
FROM ab_users a
JOIN tutorial.yammer_experiments ex
  ON ex.user_id = a.user_id AND ex.experiment = 'publisher_update'
WHERE a.user_kind = 'existing'
GROUP BY 1, 2
ORDER BY 1, 2;
```

| Устройство | Группа | Пользователей | Сообщений |
|---|---|---:|---:|
| computer | control_group | 767 | 2.70 |
| computer | test_group | 780 | 3.48 |
| phone | control_group | 242 | 2.37 |
| phone | test_group | 206 | 3.15 |
| tablet | control_group | 67 | 3.12 |
| tablet | test_group | 56 | 2.95 |

По типу пользователя (`user_type` берём из событий):

```sql
-- не запускать отдельно: нужна таблица ab_users
SELECT t.user_type,
       a.experiment_group,
       COUNT(*) AS users,
       ROUND(AVG(a.messages), 2) AS avg_messages
FROM ab_users a
JOIN (SELECT DISTINCT user_id, user_type FROM tutorial.yammer_events) t
  ON t.user_id = a.user_id
WHERE a.user_kind = 'existing'
GROUP BY 1, 2
ORDER BY 1, 2;
```

| Тип | Группа | Пользователей | Сообщений |
|---:|---|---:|---:|
| 1 | control_group | 300 | 4.46 |
| 1 | test_group | 295 | 6.05 |
| 2 | control_group | 511 | 2.19 |
| 2 | test_group | 490 | 2.74 |
| 3 | control_group | 265 | 1.49 |
| 3 | test_group | 257 | 1.54 |

Вывод:

- На компьютерах и телефонах тестовая группа впереди примерно на 0.8 сообщения.
- У планшетов тестовая группа чуть ниже контрольной. Но там всего 56 и 67 пользователей, это может быть шум.
- Больше всего выигрывают пользователи типа 1 (те, кто пишет много). У типа 3 почти нет разницы.

Ни одна когорта не объясняет весь эффект. Но эффект неравномерный. Это стоит проверить в следующем тесте.

## Рекомендация

Что сказать команде продукта:

- Исходные +55% завышены. Ошибка в распределении: все новые пользователи попали в контроль.
- На честном сравнении (только существующие) рост +28%. Он всё ещё значимый. Входы и дни активности тоже выше.
- Новую функцию стоит развивать, а не отменять.

Что делать:

1. Найти и исправить ошибку, из-за которой все новые пользователи попадают в контрольную группу.
2. Повторить тест с правильным распределением. Или хотя бы проверить результат отдельно для новых пользователей.
3. Проверить результат по когортам: устройство, тип пользователя. Особенно планшеты и пользователи типа 3.
4. До переделанного теста не говорить о «+50%». Говорить о «примерно +28% среди существующих пользователей».

:::note
Для новых пользователей ответа пока нет. В тестовой группе их нет вообще. Значит, как функция работает для них, мы не знаем.
:::
