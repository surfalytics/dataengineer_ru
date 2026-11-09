---
title: Учебные данные
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Учебные данные для курса SQL на DuckDB | Инжиниринг Данных"
description: Какие таблицы есть в учебной базе DuckDB, что в них лежит и откуда эти данные.
sidebar:
  order: 3
tags:
  - sql
  - practice
  - duckdb
---

Все таблицы лежат в файле `sql-tutorial.duckdb` ([как скачать](/practice/sql/setup/)). Таблицы разложены по двум схемам: `tutorial` и `benn`. Имена такие же, как в оригинальном курсе ThoughtSpot (Mode). Поэтому запросы из уроков работают без изменений.

Посмотреть список таблиц и их описания прямо в DuckDB:

```sql
SELECT schema_name, table_name, estimated_size, comment
FROM duckdb_tables()
ORDER BY 1, 2;
```

Столбцы конкретной таблицы:

```sql
DESCRIBE tutorial.billboard_top_100_year_end;
```

## Список таблиц

| Таблица | Строк | Что в ней | Где используется |
|---|---|---|---|
| `tutorial.us_housing_units` | 564 | Новое жильё в США по месяцам и регионам, тыс. домов, 1968–2014 | Основы |
| `tutorial.billboard_top_100_year_end` | 6 445 | Итоговые годовые чарты Billboard, 1956–2013 | Основы |
| `tutorial.aapl_historical_stock_price` | 3 773 | Дневные цены акций Apple, 2000–2014 | Агрегаты |
| `tutorial.crunchbase_companies` | 66 368 | Стартапы и компании | Средний и продвинутый уровень |
| `tutorial.crunchbase_acquisitions` | 18 968 | Покупки компаний | JOIN |
| `tutorial.crunchbase_investments` | 168 647 | Инвестиции в компании | JOIN, UNION |
| `tutorial.crunchbase_investments_part1`, `_part2` | ~84 000 | Две половины инвестиций (представления) | UNION |
| `tutorial.crunchbase_companies_clean_date` | 66 368 | Компании с «грязной» и чистой датой основания (представление) | Даты |
| `tutorial.crunchbase_acquisitions_clean_date` | 18 968 | Покупки с «грязной» и чистой датой (представление) | Даты |
| `tutorial.sf_crime_incidents_2014_01` | 11 969 | Инциденты полиции Сан-Франциско, январь 2014. Дата — строкой | Чистка данных, строки |
| `tutorial.sf_crime_incidents_cleandate` | 11 969 | То же плюс чистая дата `cleaned_date` (представление) | Даты |
| `tutorial.dc_bikeshare_q1_2012` | 361 317 | Поездки на прокатных велосипедах в Вашингтоне, 1 квартал 2012 | Оконные функции |
| `tutorial.worldwide_earthquakes` | 6 | Число землетрясений в мире по магнитуде, 2000–2012 | Pivot |
| `tutorial.yammer_users` | 18 102 | Пользователи соцсети Yammer | Аналитические кейсы |
| `tutorial.yammer_events` | 380 006 | События в продукте | Аналитические кейсы |
| `tutorial.yammer_emails` | 99 508 | События email-рассылок | Аналитические кейсы |
| `tutorial.yammer_experiments` | 2 825 | Участники A/B-теста | Аналитические кейсы |
| `benn.dimension_rollup_periods` | 2 190 | Справочник скользящих периодов | Аналитические кейсы |
| `benn.college_football_teams` | 73 | Команды студенческого американского футбола | CASE, JOIN, Pivot |
| `benn.college_football_players` | 6 935 | Игроки этих команд | CASE, JOIN, Pivot |
| `benn.sample_event_table` | 1 000 000 | Большая таблица событий | Производительность |

## Столбцы

### tutorial.us_housing_units

| Столбец | Тип | Что значит |
|---|---|---|
| `year`, `month` | integer | Год и номер месяца |
| `month_name` | varchar | Название месяца по-английски: `January`, `February`... |
| `south`, `west`, `midwest`, `northeast` | double | Сколько домов начали строить в регионе за месяц, тыс. |

### tutorial.billboard_top_100_year_end

| Столбец | Тип | Что значит |
|---|---|---|
| `year` | integer | Год чарта |
| `year_rank` | integer | Место песни в чарте за год (до 1959 года — топ-50) |
| `group_name` | varchar | Полное имя исполнителя, как в чарте: `DJ Khaled featuring T-Pain, Ludacris...` |
| `artist` | varchar | Один исполнитель. Если исполнителей несколько, у песни несколько строк |
| `song_name` | varchar | Название песни |
| `id` | integer | Номер строки |

### tutorial.aapl_historical_stock_price

| Столбец | Тип | Что значит |
|---|---|---|
| `date` | date | День торгов |
| `year`, `month` | integer | Год и месяц |
| `open`, `high`, `low`, `close` | double | Цена открытия, максимум, минимум, цена закрытия, $ |
| `volume` | bigint | Число проданных акций за день |

### Crunchbase

**`tutorial.crunchbase_companies`** — одна строка на компанию.

| Столбец | Что значит |
|---|---|
| `permalink` | Уникальный идентификатор: `/organization/...` |
| `name`, `homepage_url` | Название и сайт |
| `category_code` | Категория: `software`, `biotechnology`, `e-commerce`... |
| `funding_total_usd` | Сколько всего инвестиций получила компания, $ |
| `status` | `operating`, `acquired`, `closed`, `ipo` |
| `country_code`, `state_code`, `region`, `city` | Где находится компания |
| `funding_rounds` | Число раундов инвестиций |
| `founded_at` | Дата основания, строка `YYYY-MM-DD` |
| `founded_month`, `founded_quarter`, `founded_year` | Месяц (`2012-05`), квартал (`2012-Q2`) и год основания |
| `first_funding_at`, `last_funding_at` | Даты первого и последнего раунда, строки |

**`tutorial.crunchbase_acquisitions`** — одна строка на покупку. Столбцы `company_*` описывают купленную компанию, `acquirer_*` — покупателя. Плюс `acquired_at` (строка), `acquired_month`, `acquired_quarter`, `acquired_year`, `price_amount`, `price_currency_code`.

**`tutorial.crunchbase_investments`** — одна строка на пару «компания — инвестор» в раунде. Столбцы `company_*` и `investor_*`, плюс `funding_round_type` (`venture`, `seed`, `angel`...), `funded_at`, `funded_month`, `funded_quarter`, `funded_year`, `raised_amount_usd`.

Как связаны таблицы: `crunchbase_companies.permalink` = `crunchbase_acquisitions.company_permalink` = `crunchbase_investments.company_permalink`.

### tutorial.sf_crime_incidents_2014_01

| Столбец | Что значит |
|---|---|
| `incidnt_num` | Номер инцидента |
| `category`, `descript` | Категория и описание |
| `day_of_week` | День недели |
| `date` | Дата **строкой**: `01/31/2014 08:00:00 AM +0000`. На ней учимся чистить данные |
| `time` | Время строкой: `HH:MM` |
| `pd_district`, `resolution`, `address` | Район полиции, решение, адрес |
| `lon`, `lat`, `location` | Координаты. `location` — строка вида `(37.78, -122.41)` |

### tutorial.dc_bikeshare_q1_2012

| Столбец | Что значит |
|---|---|
| `duration` | Длительность строкой: `0h 7min. 55sec.` |
| `duration_seconds` | Длительность в секундах |
| `start_time`, `end_time` | Начало и конец поездки |
| `start_station`, `start_terminal` | Станция начала: название и номер |
| `end_station`, `end_terminal` | Станция конца |
| `bike_number` | Номер велосипеда |
| `rider_type` | `Registered` (подписчик) или `Casual` (разовая поездка) |

### Yammer

Yammer — корпоративная соцсеть. Данные выдуманы для [аналитических кейсов](/practice/sql/analytics/). Подробное описание столбцов — в самих кейсах.

| Таблица | Столбцы |
|---|---|
| `tutorial.yammer_users` | `user_id`, `created_at`, `company_id`, `language`, `activated_at`, `state` |
| `tutorial.yammer_events` | `user_id`, `occurred_at`, `event_type`, `event_name`, `location`, `device`, `user_type` |
| `tutorial.yammer_emails` | `user_id`, `occurred_at`, `action`, `user_type` |
| `tutorial.yammer_experiments` | `user_id`, `occurred_at`, `experiment`, `experiment_group`, `location`, `device` |
| `benn.dimension_rollup_periods` | `period_id`, `time_id`, `pst_start`, `pst_end`, `utc_start`, `utc_end` |

### Студенческий футбол

**`benn.college_football_teams`**: `division` (`FBS (Division I-A Teams)` или `FCS (Division I-AA Teams)`), `conference`, `school_name`, `roster_url`, `id`.

**`benn.college_football_players`**: `full_school_name`, `school_name`, `player_name`, `position`, `height` (дюймы), `weight` (фунты), `year` (курс: `FR`, `SO`, `JR`, `SR`), `hometown`, `state`, `id`.

Связь: `players.school_name = teams.school_name`.

### Остальные

- **`tutorial.worldwide_earthquakes`**: `magnitude` (`8.0 to 9.9`, `7.0 to 7.9`...) и столбцы `year_2000` ... `year_2012` с числом землетрясений.
- **`benn.sample_event_table`**: `event_id`, `user_id`, `event_date`, `event_name`, `device`.

## Откуда данные

| Данные | Источник | Лицензия |
|---|---|---|
| Новое жильё | [US Census Bureau, New Residential Construction](https://www.census.gov/construction/nrc/) | Public domain |
| Чарты Billboard | Списки «Billboard Year-End Hot 100» в [Википедии](https://en.wikipedia.org/wiki/Billboard_Year-End) | Факты, CC BY-SA |
| Акции Apple | Yahoo Finance | Факты о ценах |
| Crunchbase | [Экспорт Crunchbase, декабрь 2015](https://github.com/notpeter/crunchbase-data) | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), только некоммерческое использование |
| Инциденты в Сан-Франциско | [DataSF](https://data.sfgov.org/) | PDDL (public domain) |
| Велопрокат | [Capital Bikeshare System Data](https://capitalbikeshare.com/system-data) | Capital Bikeshare Data License |
| Землетрясения | [Каталог USGS](https://earthquake.usgs.gov/fdsnws/event/1/) | Public domain |
| Yammer, футболисты, sample_event_table | Сгенерированы нами | — |

Данные отличаются от оригинального курса ThoughtSpot (Mode): там другие выгрузки. Поэтому ответы в наших заданиях другие. Все решения проверены на нашей базе.

Скрипты сборки базы лежат в репозитории: [`scripts/sql-tutorial-db`](https://github.com/surfalytics/dataengineer_ru/tree/main/scripts/sql-tutorial-db).
